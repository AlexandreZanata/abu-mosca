#!/usr/bin/env python3
"""Controles nulos e congelamento do pacote de baselines (B09).

Somente fonte: permutação de rótulos (nulo), rewiring preservando grau
(dirigido, sem self-loops novos nem multiedges), permutação de IDs (invariância
do pipeline), negativos pareados por grau e o manifesto congelado dos
comparadores de B03–B08. Nenhuma métrica, rótulo ou arquivo do alvo é aberto;
o relatório é restrito ao diagnóstico within-source e o melhor baseline é
escolhido por regra source-only declarada antes de qualquer uso do alvo.
"""

import argparse
import hashlib
import json
import random
import resource
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.feather as feather
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import artisanal_features as af  # noqa: E402
import baselines_source as bs  # noqa: E402
import metrics  # noqa: E402
import opaque_ids  # noqa: E402
import seeds as seedlib  # noqa: E402

MASTER_SEED = 20260914
SOURCE_SNAPSHOT = ROOT / "runs" / "h08" / "source"
SOURCE_PROPERTIES = ROOT / "data" / "raw" / "spikes" / "manc_neuron_properties.feather"
LABEL_DRAWS = 20
NEGATIVE_COUNT = 10
REWIRE_MULTIPLIER = 10
CHANCE_TOLERANCE = 0.02
DEGREE_COLUMNS = ("in_degree", "out_degree", "weighted_in", "weighted_out")
BASELINE_SOURCES = {
    "majority": ("artifacts/reports/B03-BASELINES-FONTE.json", ["results", "baselines", "majority", "recall", "@1", "macro"]),
    "random estratificado": ("artifacts/reports/B03-BASELINES-FONTE.json", ["results", "baselines", "stratified_random", "median_accuracy"]),
    "degree-only": ("artifacts/reports/B03-BASELINES-FONTE.json", ["results", "baselines", "degree_only", "recall", "@1", "macro"]),
    "artesanal (todas)": ("artifacts/reports/B04-ARTESANAL.json", ["results", "all", "macro_recall@1"]),
    "MLP 100k": ("artifacts/reports/B05-MLP.json", ["results", "s", "median_macro_recall@1"]),
    "MLP 500k": ("artifacts/reports/B05-MLP.json", ["results", "m", "median_macro_recall@1"]),
    "MLP pareado 1-3M": ("artifacts/reports/B05-MLP.json", ["results", "l", "median_macro_recall@1"]),
    "deepwalk": ("artifacts/reports/B06-NODE2VEC.json", ["results", "deepwalk", "median_macro_recall@1"]),
    "node2vec": ("artifacts/reports/B06-NODE2VEC.json", ["results", "node2vec", "median_macro_recall@1"]),
    "svd dirigido": ("artifacts/reports/B07-ESPECTRAL.json", ["results", "svd_dirigido", "median_macro_recall@1"]),
    "ase simetrizado": ("artifacts/reports/B07-ESPECTRAL.json", ["results", "ase_simetrizado", "median_macro_recall@1"]),
}
CLASSICAL = ("majority", "random estratificado", "degree-only", "artesanal (todas)")
NEURAL = ("MLP 100k", "MLP 500k", "MLP pareado 1-3M")
TRANSDUTIVE = ("deepwalk", "node2vec", "svd dirigido", "ase simetrizado")


class ControlError(RuntimeError):
    pass


def _lookup(document: dict, keys: list[str]):
    current = document
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            raise ControlError(f"campo ausente: {'/'.join(keys)}")
        current = current[key]
    return current


def permute_labels_within_split(train: dict[str, str], val: dict[str, str], seed: int) -> tuple[dict[str, str], dict[str, str]]:
    rng = random.Random(int(seed) % (2**63))
    permuted = []
    for split in (train, val):
        by_class: dict[str, list[str]] = defaultdict(list)
        for node, name in split.items():
            by_class[name].append(node)
        names = sorted(by_class)
        pool = [name for name in names for _ in by_class[name]]
        rng.shuffle(pool)
        rebuilt = {}
        cursor = 0
        for name in names:
            for node in by_class[name]:
                rebuilt[node] = pool[cursor]
                cursor += 1
        permuted.append(rebuilt)
    return permuted[0], permuted[1]


def probe_macro(matrix: np.ndarray, order: dict[str, int], train: dict[str, str], val: dict[str, str], classes: list[str], columns: list[int]) -> float:
    train_nodes, val_nodes = list(train), list(val)
    train_matrix = matrix[[order[node] for node in train_nodes]][:, columns]
    val_matrix = matrix[[order[node] for node in val_nodes]][:, columns]
    predictions = af.probe(train_matrix, [train[node] for node in train_nodes], val_matrix, classes)
    ranked = {node: [predictions[index]] for index, node in enumerate(val_nodes)}
    return float(metrics.evaluate(ranked, val, k_values=(1,))["recall"]["@1"]["macro"])


def label_permutation_control(matrix: np.ndarray, order: dict[str, int], train: dict[str, str], val: dict[str, str], classes: list[str], columns: list[int], draws: int, seed: int) -> dict:
    real = probe_macro(matrix, order, train, val, classes, columns)
    nulls = []
    for draw in range(draws):
        draw_seed = seedlib.derive_seed(seed, "b09", "label-permutation", str(draw))
        train_p, val_p = permute_labels_within_split(train, val, draw_seed)
        nulls.append(probe_macro(matrix, order, train_p, val_p, classes, columns))
    exceed = sum(1 for value in nulls if value >= real)
    return {
        "real_macro_recall@1": round(real, 6),
        "draws": draws,
        "null_mean": round(float(np.mean(nulls)), 6),
        "null_sd": round(float(np.std(nulls)), 6),
        "null_max": round(float(np.max(nulls)), 6),
        "null_values": [round(value, 6) for value in nulls],
        "exceedances": exceed,
        "p_value": round((1 + exceed) / (draws + 1), 6),
    }


def _edge_keys(src: np.ndarray, dst: np.ndarray, n_nodes: int) -> set[int]:
    return set((src.astype(np.int64) * n_nodes + dst).tolist())


def rewire_directed(src: np.ndarray, dst: np.ndarray, n_nodes: int, accepted_target: int, seed: int) -> tuple[np.ndarray, np.ndarray, dict]:
    """Trocas dirigidas de alvo (a→b, c→d) ⇒ (a→d, c→b), preservando in/out graus."""
    src = src.astype(np.int64).copy()
    dst = dst.astype(np.int64).copy()
    n_edges = len(src)
    keys = _edge_keys(src, dst, n_nodes)
    protected = {int(src[i]) * n_nodes + int(dst[i]) for i in range(n_edges) if src[i] == dst[i]}
    rng = np.random.RandomState(int(seed) % (2**32))
    stats = {"attempts": 0, "accepted": 0, "rejected_self_loop": 0, "rejected_duplicate": 0, "kept_self_loops": len(protected)}
    started = time.perf_counter()
    batch = 1 << 20
    while stats["accepted"] < accepted_target:
        draws = rng.randint(0, n_edges, size=(batch, 2))
        for i_raw, j_raw in draws:
            if stats["accepted"] >= accepted_target:
                break
            i, j = int(i_raw), int(j_raw)
            stats["attempts"] += 1
            if i == j:
                continue
            a, b, c, d = int(src[i]), int(dst[i]), int(src[j]), int(dst[j])
            if a == b or c == d:
                continue
            if a == c or b == d:
                continue
            if a == d or c == b:
                stats["rejected_self_loop"] += 1
                continue
            key_ad, key_cb = a * n_nodes + d, c * n_nodes + b
            key_ab, key_cd = a * n_nodes + b, c * n_nodes + d
            if key_ad == key_cb:
                stats["rejected_duplicate"] += 1
                continue
            if (key_ad in keys and key_ad != key_ab and key_ad != key_cd) or (key_cb in keys and key_cb != key_ab and key_cb != key_cd):
                stats["rejected_duplicate"] += 1
                continue
            keys.discard(key_ab)
            keys.discard(key_cd)
            keys.add(key_ad)
            keys.add(key_cb)
            src[i], dst[i] = a, d
            src[j], dst[j] = c, b
            stats["accepted"] += 1
    stats["seconds"] = round(time.perf_counter() - started, 3)
    stats["rate_per_second"] = round(stats["attempts"] / max(stats["seconds"], 1e-9))
    return src, dst, stats


def degree_profile(degree_sum: np.ndarray) -> np.ndarray:
    return np.floor(np.log2(np.asarray(degree_sum, dtype=np.float64) + 1.0)).astype(np.int64)


def degree_matched_negatives(matrix: np.ndarray, order: dict[str, int], train: dict[str, str], val: dict[str, str], classes: list[str], columns: list[int], n_negatives: int, seed: int, matching: str) -> dict:
    if matching not in ("fine", "coarse", "none"):
        raise ControlError(f"modo de pareamento desconhecido: {matching}")
    train_nodes, val_nodes = list(train), list(val)
    train_matrix = matrix[[order[node] for node in train_nodes]][:, columns]
    val_matrix = matrix[[order[node] for node in val_nodes]][:, columns]
    stats = bs.fit_stats(train_matrix)
    train_scaled = bs.transform(train_matrix, stats)
    val_scaled = bs.transform(val_matrix, stats)
    centroids = {}
    for name in classes:
        rows = [train_scaled[index] for index, node in enumerate(train_nodes) if train[node] == name]
        if rows:
            centroids[name] = np.mean(rows, axis=0)
    degree_sum = matrix[:, af.FEATURE_ORDER.index("weighted_in")] + matrix[:, af.FEATURE_ORDER.index("weighted_out")]
    log_degree = np.log2(degree_sum + 1.0)
    class_median = {
        name: float(np.median([log_degree[order[node]] for node, label in train.items() if label == name]))
        for name in classes
    }
    rng = np.random.RandomState(int(seed) % (2**32))
    hits = 0
    fallbacks = 0
    for index, node in enumerate(val_nodes):
        true_name = val[node]
        candidates_pool = [name for name in classes if name != true_name]
        if matching == "fine":
            # negativos pareados ao perfil da classe verdadeira (não à consulta):
            # teste mais duro, onde o grau do positivo não o favorece por construção
            target_profile = class_median[true_name]
            candidates = sorted(candidates_pool, key=lambda name: (abs(class_median[name] - target_profile), name))
        elif matching == "coarse":
            query_profile = int(np.floor(log_degree[order[node]]))
            candidates = [name for name in candidates_pool if int(np.floor(class_median[name])) == query_profile]
            if len(candidates) < n_negatives:
                fallbacks += 1
                candidates = sorted(candidates_pool, key=lambda name: (abs(class_median[name] - log_degree[order[node]]), name))
        else:
            candidates = candidates_pool
        if matching in ("coarse", "none") and len(candidates) > n_negatives:
            picks = rng.choice(len(candidates), size=n_negatives, replace=False)
            sampled = [candidates[int(pick)] for pick in picks]
        else:
            sampled = candidates[:n_negatives]
        considered = [true_name] + sampled
        distances = {name: float(np.linalg.norm(val_scaled[index] - centroids[name])) for name in considered if name in centroids}
        if true_name not in distances:
            continue
        best = min(distances, key=lambda name: (distances[name], name))
        hits += int(best == true_name)
    queries = len(val_nodes)
    expected = 1.0 / (n_negatives + 1)
    return {
        "matching": matching,
        "negatives_per_query": n_negatives,
        "queries": queries,
        "hits": hits,
        "hit_rate": round(hits / queries, 6),
        "chance": round(expected, 6),
        "fallback_queries": fallbacks,
    }


def write_snapshot(directory: Path, ids: np.ndarray, src: np.ndarray, dst: np.ndarray, weights: np.ndarray) -> dict:
    directory.mkdir(parents=True, exist_ok=True)
    degree_in = np.bincount(dst, minlength=len(ids)).astype(np.int64)
    degree_out = np.bincount(src, minlength=len(ids)).astype(np.int64)
    id_array = pa.array(ids.tolist(), type=pa.string())
    pq.write_table(
        pa.table({"id": id_array, "degree_in": pa.array(degree_in), "degree_out": pa.array(degree_out)}),
        directory / "nodes.parquet",
    )
    pq.write_table(
        pa.table(
            {
                "source": pa.array(ids[src].tolist(), type=pa.string()),
                "target": pa.array(ids[dst].tolist(), type=pa.string()),
                "weight": pa.array(weights.tolist(), type=pa.int64()),
            }
        ),
        directory / "edges.parquet",
    )
    return {
        "nodes": int(len(ids)),
        "edges": int(len(src)),
        "edges_sha256": bs.sha256_file(directory / "edges.parquet"),
        "nodes_sha256": bs.sha256_file(directory / "nodes.parquet"),
    }


def permute_node_ids(snapshot: Path, properties: Path, out_dir: Path, out_properties: Path, seed: int, permutation_out: Path | None = None) -> dict:
    nodes = pq.read_table(snapshot / "nodes.parquet")
    edges = pq.read_table(snapshot / "edges.parquet", columns=["source", "target", "weight"])
    ids = sorted(nodes["id"].combine_chunks().to_pylist())
    table = feather.read_table(properties)
    bodies = table["bodyId"].to_pylist()
    node_set = set(ids)
    body_of = {}
    for body in bodies:
        opaque = opaque_ids.opaque_node_id(bs.DATASET, bs.RELEASE, body)
        if opaque in node_set and opaque not in body_of:
            body_of[opaque] = body
    rng = np.random.RandomState(int(seed) % (2**32))
    permutation = rng.permutation(len(ids))
    if permutation_out is not None:
        permutation_out.parent.mkdir(parents=True, exist_ok=True)
        np.save(permutation_out, permutation)
    new_ids = [ids[index] for index in permutation]
    old_index = {node: position for position, node in enumerate(ids)}
    new_id_of_old = {node: new_ids[old_index[node]] for node in ids}
    id_array = pa.array(ids, type=pa.string())
    src = pc.index_in(edges["source"].combine_chunks(), value_set=id_array).to_numpy(zero_copy_only=False)
    dst = pc.index_in(edges["target"].combine_chunks(), value_set=id_array).to_numpy(zero_copy_only=False)
    if np.any(src < 0) or np.any(dst < 0):
        raise ControlError("aresta com endpoint fora dos nodes")
    weights = np.asarray(edges["weight"].combine_chunks().to_pylist(), dtype=np.int64)
    permuted_ids = np.asarray(new_ids, dtype=object)
    src_permuted = np.asarray([new_id_of_old[ids[int(value)]] for value in src], dtype=object)
    dst_permuted = np.asarray([new_id_of_old[ids[int(value)]] for value in dst], dtype=object)
    index_of_new = {node: position for position, node in enumerate(new_ids)}
    src_pos = np.asarray([index_of_new[node] for node in src_permuted], dtype=np.int64)
    dst_pos = np.asarray([index_of_new[node] for node in dst_permuted], dtype=np.int64)
    snapshot_info = write_snapshot(out_dir, permuted_ids, src_pos, dst_pos, weights)
    new_bodies = []
    for body in bodies:
        opaque = opaque_ids.opaque_node_id(bs.DATASET, bs.RELEASE, body)
        if opaque in new_id_of_old:
            target = body_of[new_id_of_old[opaque]]
            new_bodies.append(target)
        else:
            new_bodies.append(body)
    out_properties.parent.mkdir(parents=True, exist_ok=True)
    permuted_table = table.set_column(table.schema.get_field_index("bodyId"), "bodyId", pa.array(new_bodies, type=table.schema.field("bodyId").type))
    feather.write_feather(permuted_table, out_properties)
    if len(set(new_bodies)) != len(new_bodies):
        raise ControlError("permutação de IDs gerou bodyId duplicado")
    original_labels, _ = bs.load_source_labels(properties)
    permuted_labels, _ = bs.load_source_labels(out_properties)
    checked = 0
    mismatches = 0
    for node, label in original_labels.items():
        if node not in new_id_of_old:
            continue
        checked += 1
        if permuted_labels.get(new_id_of_old[node]) != label:
            mismatches += 1
    if checked == 0:
        raise ControlError("nenhum rótulo verificado na permutação de IDs")
    if mismatches:
        raise ControlError(f"rótulos não seguiram a permutação em {mismatches}/{checked}")
    return {
        "seed": int(seed) % (2**32),
        "nodes": snapshot_info["nodes"],
        "edges": snapshot_info["edges"],
        "snapshot": snapshot_info,
        "properties_sha256": bs.sha256_file(out_properties),
        "labels_checked": checked,
        "labels_follow_permutation": True,
        "permutation_sha256": bs.sha256_file(permutation_out) if permutation_out is not None else None,
    }


def run_artisanal(snapshot: Path, properties: Path, out_dir: Path, report_path: Path) -> dict:
    command = [sys.executable, str(ROOT / "tools" / "artisanal_features.py"), "--snapshot", str(snapshot), "--properties", str(properties), "--out-dir", str(out_dir), "--report", str(report_path)]
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0:
        raise ControlError(f"artisanal_features falhou: {completed.stderr[-300:]}")
    return json.loads(report_path.read_text(encoding="utf-8"))


def frozen_package() -> dict:
    ranking = []
    for name, (relative, keys) in BASELINE_SOURCES.items():
        report_path = ROOT / relative
        document = json.loads(report_path.read_text(encoding="utf-8"))
        value = _lookup(document, keys)
        ranking.append({"method": name, "macro_recall@1": round(float(value), 6), "report": relative, "report_sha256": bs.sha256_file(report_path)})
    ranking.sort(key=lambda item: (-item["macro_recall@1"], item["method"]))
    best_overall = ranking[0]
    best_classical = next(item for item in ranking if item["method"] in CLASSICAL)
    best_others = [item for item in ranking if item["method"] not in CLASSICAL]
    predictions = []
    for relative in sorted({source[0] for source in BASELINE_SOURCES.values()}):
        document = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        entries = document.get("predictions", [])
        if isinstance(entries, dict):
            entries = [entries]
        for entry in entries:
            path = ROOT / entry.get("path", "")
            if not path.exists():
                predictions.append({"path": entry.get("path"), "status": "ausente"})
                continue
            digest = bs.sha256_file(path)
            predictions.append(
                {
                    "path": entry.get("path"),
                    "status": "ok" if digest == entry.get("sha256") else "divergente",
                    "sha256": digest,
                }
            )
    tools = {}
    for name in ("baselines_source.py", "artisanal_features.py", "mlp_control.py", "node2vec_baseline.py", "spectral_baseline.py", "regal_repro.py"):
        tool = ROOT / "tools" / name
        if tool.exists():
            tools[name] = bs.sha256_file(tool)
    config = ROOT / "configs" / "edge-primary.json"
    return {
        "schema": "b09-baseline-package",
        "status": "frozen-within-source (schema próprio; sem dados do alvo)",
        "rule": "maior mediana de Macro Recall@1 na validação da fonte (source-only); empate → método mais simples",
        "target_data_used": False,
        "ranking": ranking,
        "best_comparator": best_overall["method"],
        "best_classical": best_classical["method"],
        "top_non_classical": best_others[0]["method"] if best_others else None,
        "predictions": predictions,
        "tools_sha256": tools,
        "edge_primary_sha256": bs.sha256_file(config) if config.exists() else None,
    }


def derive_interpretations(report: dict) -> dict:
    controls = report["controls"]
    real_macro = float(controls["label_permutation"]["all_features"]["real_macro_recall@1"])
    out = {}
    for subset in ("all_features", "degree_features"):
        entry = controls["label_permutation"][subset]
        out[f"label_permutation_{subset}"] = (
            "degradou como esperado" if float(entry["null_max"]) < float(entry["real_macro_recall@1"]) else "investigar"
        )
    rewire = controls["degree_preserving_rewiring"]
    out["degree_preserving_rewiring"] = (
        "degradou como esperado" if float(rewire["artisanal_all_macro_recall@1"]) < real_macro else "investigar"
    )
    identity = controls["id_permutation"]
    identity_ok = (
        bool(identity.get("features_equivariant"))
        and int(identity.get("label_mismatches", 1)) == 0
        and abs(float(identity.get("carried_split_macro_recall@1", -1)) - real_macro) <= 1e-9
    )
    out["id_permutation"] = "invariante como esperado" if identity_ok else "investigar"
    for subset in ("degree_features", "all_features"):
        fine = controls["degree_matched_negatives"][subset]["fine"]
        matched = float(fine["hit_rate"])
        chance = float(fine["chance"])
        out[f"degree_matched_{subset}"] = (
            "caiu ao nível do acaso (|Δ| <= tolerância)"
            if abs(matched - chance) <= CHANCE_TOLERANCE
            else f"manteve vantagem ({matched:.6f} vs acaso {chance:.6f}) — investigar"
        )
    return out


def derive_pending(interpretation: dict) -> list[str]:
    return sorted(key for key, value in interpretation.items() if value == "investigar" or value.startswith("manteve vantagem"))


def run(workdir: Path, report_path: Path, manifest_path: Path, draws: int = LABEL_DRAWS, negative_count: int = NEGATIVE_COUNT, rewire_multiplier: int = REWIRE_MULTIPLIER) -> dict:
    started = time.perf_counter()
    workdir = Path(workdir).resolve()
    report_path = Path(report_path).resolve()
    manifest_path = Path(manifest_path).resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    ids, features = af.extract_features(SOURCE_SNAPSHOT)
    order = {node: position for position, node in enumerate(ids)}
    matrix = np.column_stack([features[name] for name in af.FEATURE_ORDER])
    degree_columns = [af.FEATURE_ORDER.index(name) for name in DEGREE_COLUMNS]
    all_columns = list(range(len(af.FEATURE_ORDER)))
    labels, label_meta = bs.load_source_labels(SOURCE_PROPERTIES)
    labels = {node: name for node, name in labels.items() if node in order}
    counts = Counter(labels.values())
    labels = {node: name for node, name in labels.items() if counts[name] >= bs.K_MIN}
    train, val = bs.split_deterministic(labels)
    classes = sorted(set(train.values()))
    report: dict = {
        "schema": "b09-null-controls",
        "scope": "diagnóstico within-source; nenhum dado do alvo usado",
        "label_meta": label_meta,
        "split": {"train": len(train), "val": len(val), "classes": len(classes)},
        "declared": {
            "label_draws": draws,
            "negatives": negative_count,
            "rewire_multiplier": rewire_multiplier,
            "chance_tolerance": CHANCE_TOLERANCE,
            "best_baseline_rule": "maior mediana de Macro Recall@1 na fonte; empate → mais simples",
        },
        "controls": {},
    }
    seed_labels = seedlib.derive_seed(MASTER_SEED, "b09", "label-permutation")
    seed_rewire = seedlib.derive_seed(MASTER_SEED, "b09", "rewire")
    seed_ids = seedlib.derive_seed(MASTER_SEED, "b09", "id-permutation")
    seed_negatives = seedlib.derive_seed(MASTER_SEED, "b09", "negatives")
    report["seeds"] = {
        "label_permutation": seed_labels,
        "rewire": seed_rewire,
        "id_permutation": seed_ids,
        "negatives": seed_negatives,
    }
    report["controls"]["label_permutation"] = {
        "all_features": label_permutation_control(matrix, order, train, val, classes, all_columns, draws, seed_labels),
        "degree_features": label_permutation_control(matrix, order, train, val, classes, degree_columns, draws, seed_labels),
    }
    report["interpretation"] = {}
    report["controls"]["label_permutation"]["all_features"]["comment"] = "nulo destrói a associação rótulo-estrutura; esperado cair ao acaso"
    nodes = pq.read_table(SOURCE_SNAPSHOT / "nodes.parquet")
    edges = pq.read_table(SOURCE_SNAPSHOT / "edges.parquet", columns=["source", "target", "weight"])
    id_array = pa.array(ids, type=pa.string())
    src = pc.index_in(edges["source"].combine_chunks(), value_set=id_array).to_numpy(zero_copy_only=False)
    dst = pc.index_in(edges["target"].combine_chunks(), value_set=id_array).to_numpy(zero_copy_only=False)
    weights = np.asarray(edges["weight"].combine_chunks().to_pylist(), dtype=np.int64)
    degree_in_before = np.bincount(dst, minlength=len(ids))
    degree_out_before = np.bincount(src, minlength=len(ids))
    weight_counts_before = Counter(weights.tolist())
    accepted_target = rewire_multiplier * len(src)
    rewired_src, rewired_dst, rewire_stats = rewire_directed(src, dst, len(ids), accepted_target, seed_rewire)
    degree_in_after = np.bincount(rewired_dst, minlength=len(ids))
    degree_out_after = np.bincount(rewired_src, minlength=len(ids))
    weight_counts_after = Counter(np.asarray(weights).tolist())
    weighted_in_before = np.bincount(dst, weights=weights.astype(np.float64), minlength=len(ids))
    weighted_out_before = np.bincount(src, weights=weights.astype(np.float64), minlength=len(ids))
    weighted_in_after = np.bincount(rewired_dst, weights=weights.astype(np.float64), minlength=len(ids))
    weighted_out_after = np.bincount(rewired_src, weights=weights.astype(np.float64), minlength=len(ids))
    weighted_preserved = bool(
        np.array_equal(weighted_in_before, weighted_in_after) and np.array_equal(weighted_out_before, weighted_out_after)
    )
    rewired_snapshot = workdir / "rewired"
    snapshot_info = write_snapshot(rewired_snapshot, np.asarray(ids, dtype=object), rewired_src, rewired_dst, weights)
    rewired_report = run_artisanal(rewired_snapshot, SOURCE_PROPERTIES, workdir / "rewired-out", workdir / "rewired-report.json")
    report["controls"]["degree_preserving_rewiring"] = {
        "accepted_target": int(accepted_target),
        "stats": rewire_stats,
        "edge_count_preserved": int(len(rewired_src)) == int(len(src)),
        "in_degree_preserved": bool(np.array_equal(degree_in_before, degree_in_after)),
        "out_degree_preserved": bool(np.array_equal(degree_out_before, degree_out_after)),
        "weight_multiset_preserved": weight_counts_before == weight_counts_after,
        "weighted_degrees_preserved": weighted_preserved,
        "comment_pesos": "trocas preservam graus de contagem e o multiconjunto de pesos; os pesos ficam nos slots e os graus ponderados podem mudar (não são invariantes deste controle)",
        "new_self_loops": int(np.sum(rewired_src == rewired_dst)) - rewire_stats["kept_self_loops"],
        "unique_pairs_before": int(len(set(zip(src.tolist(), dst.tolist())))),
        "unique_pairs_after": int(len(set(zip(rewired_src.tolist(), rewired_dst.tolist())))),
        "snapshot": snapshot_info,
        "artisanal_all_macro_recall@1": rewired_report["results"]["all"]["macro_recall@1"],
        "artisanal_degree_macro_recall@1": rewired_report["results"]["degree"]["macro_recall@1"],
        "artisanal_report_sha256": bs.sha256_file(workdir / "rewired-report.json"),
        "comment": "degree-only é invariante por construção; o alvo do controle é o ganho estrutural além do grau",
    }
    original_macro_for_rewire = float(report["controls"]["label_permutation"]["all_features"]["real_macro_recall@1"])
    permuted_properties = workdir / "id-permuted-properties.feather"
    permutation_path = workdir / "id-permutation.npy"
    report["controls"]["id_permutation"] = permute_node_ids(
        SOURCE_SNAPSHOT, SOURCE_PROPERTIES, workdir / "id-permuted", permuted_properties, seed_ids, permutation_path
    )
    permutation = np.load(permutation_path)
    sorted_ids = sorted(ids)
    new_ids_sorted = [sorted_ids[index] for index in permutation]
    new_id_of_old = dict(zip(sorted_ids, new_ids_sorted))
    permuted_ids_list, permuted_features = af.extract_features(workdir / "id-permuted")
    permuted_order = {node: position for position, node in enumerate(permuted_ids_list)}
    permuted_matrix = np.column_stack([permuted_features[name] for name in af.FEATURE_ORDER])
    original_features_by_node = {node: {name: features[name][order[node]] for name in af.FEATURE_ORDER} for node in ids}
    max_abs_diff = 0.0
    for node in ids:
        target = new_id_of_old[node]
        for name in af.FEATURE_ORDER:
            delta = abs(float(original_features_by_node[node][name]) - float(permuted_features[name][permuted_order[target]]))
            max_abs_diff = max(max_abs_diff, delta)
    train_carried = {new_id_of_old[node]: label for node, label in train.items()}
    val_carried = {new_id_of_old[node]: label for node, label in val.items()}
    permuted_labels, _ = bs.load_source_labels(permuted_properties)
    label_mismatches = sum(
        1 for node, label in {**train, **val}.items() if permuted_labels.get(new_id_of_old[node]) != label
    )
    carried_macro = probe_macro(permuted_matrix, permuted_order, train_carried, val_carried, classes, all_columns)
    permuted_report = run_artisanal(workdir / "id-permuted", permuted_properties, workdir / "id-permuted-out", workdir / "id-permuted-report.json")
    report["controls"]["id_permutation"].update(
        {
            "features_equivariant": max_abs_diff <= 1e-9,
            "features_max_abs_diff": max_abs_diff,
            "label_mismatches": label_mismatches,
            "carried_split_macro_recall@1": round(carried_macro, 6),
            "resplit_macro_recall@1": permuted_report["results"]["all"]["macro_recall@1"],
            "resplit_delta": round(float(permuted_report["results"]["all"]["macro_recall@1"]) - original_macro_for_rewire, 6),
            "artisanal_degree_macro_recall@1": permuted_report["results"]["degree"]["macro_recall@1"],
            "artisanal_report_sha256": bs.sha256_file(workdir / "id-permuted-report.json"),
            "comment": "features são equívocas à permutação; o split por hash de ID muda e é registrado como sensibilidade técnica",
        }
    )
    identity_ok = max_abs_diff <= 1e-9 and label_mismatches == 0 and abs(carried_macro - original_macro_for_rewire) <= 1e-9
    report["interpretation"]["id_permutation"] = "invariante como esperado" if identity_ok else "investigar"
    report["controls"]["degree_matched_negatives"] = {
        "degree_features": {
            "fine": degree_matched_negatives(matrix, order, train, val, classes, degree_columns, negative_count, seed_negatives, "fine"),
            "coarse": degree_matched_negatives(matrix, order, train, val, classes, degree_columns, negative_count, seed_negatives, "coarse"),
            "none": degree_matched_negatives(matrix, order, train, val, classes, degree_columns, negative_count, seed_negatives, "none"),
        },
        "all_features": {
            "fine": degree_matched_negatives(matrix, order, train, val, classes, all_columns, negative_count, seed_negatives, "fine"),
            "coarse": degree_matched_negatives(matrix, order, train, val, classes, all_columns, negative_count, seed_negatives, "coarse"),
            "none": degree_matched_negatives(matrix, order, train, val, classes, all_columns, negative_count, seed_negatives, "none"),
        },
        "comment": "acaso = 1/(negativos+1); fine = B classes de mediana de log-grau mais próxima da classe verdadeira (pareamento duro); coarse = bin de piso do log-grau da consulta; none = sorteio sem pareamento",
    }
    report["interpretation"] = derive_interpretations(report)
    report["pending_investigation"] = derive_pending(report["interpretation"])
    package = frozen_package()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(package, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report["frozen_package"] = {
        "schema": package["schema"],
        "path": str(manifest_path.relative_to(ROOT)),
        "sha256": bs.sha256_file(manifest_path),
        "best_comparator": package["best_comparator"],
        "best_classical": package["best_classical"],
        "predictions_ok": sum(1 for entry in package["predictions"] if entry["status"] == "ok"),
        "predictions_total": len(package["predictions"]),
    }
    report["seconds"] = round(time.perf_counter() - started, 3)
    report["peak_rss_mib"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def check_report(path: Path, manifest: Path | None = None) -> list[str]:
    failures: list[str] = []
    path = Path(path).resolve()
    if not path.exists():
        return [f"relatório ausente: {path}"]
    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("schema") != "b09-null-controls":
        failures.append("schema divergente")
    if "within-source" not in str(report.get("scope", "")):
        failures.append("escopo deve declarar diagnóstico within-source")
    controls = report.get("controls", {})
    for name in ("label_permutation", "degree_preserving_rewiring", "id_permutation", "degree_matched_negatives"):
        if name not in controls:
            failures.append(f"controle ausente: {name}")
    if failures:
        return failures
    for subset in ("all_features", "degree_features"):
        entry = controls["label_permutation"].get(subset, {})
        real = float(entry.get("real_macro_recall@1", -1))
        null_max = float(entry.get("null_max", 1.0))
        null_mean = float(entry.get("null_mean", 1.0))
        if not 0.0 <= real <= 1.0 or not 0.0 <= null_mean <= 1.0 or not 0.0 <= null_max <= 1.0:
            failures.append(f"nulo de rótulos com valores fora de [0,1]: {subset}")
        if null_max >= real:
            failures.append(f"nulo de rótulos não degradou como esperado: {subset}")
        if int(entry.get("draws", 0)) < 10:
            failures.append(f"poucas permutações de rótulo: {subset}")
        if not 0.0 <= float(entry.get("p_value", -1)) <= 1.0:
            failures.append(f"p-valor inválido: {subset}")
    rewire = controls["degree_preserving_rewiring"]
    for key in ("edge_count_preserved", "in_degree_preserved", "out_degree_preserved", "weight_multiset_preserved"):
        if not rewire.get(key):
            failures.append(f"rewiring não preservou invariante: {key}")
    if int(rewire.get("new_self_loops", 1)) != 0:
        failures.append("rewiring criou self-loops novos")
    if int(rewire.get("unique_pairs_after", -1)) != int(rewire.get("unique_pairs_before", -2)):
        failures.append("rewiring criou multiedges")
    accepted = int(rewire.get("stats", {}).get("accepted", 0))
    target = int(rewire.get("accepted_target", 1))
    if accepted < target:
        failures.append("rewiring não atingiu as trocas declaradas")
    if accepted < 1000:
        failures.append("rewiring trivial (poucas trocas)")
    rewired_macro = float(rewire.get("artisanal_all_macro_recall@1", -1))
    original_macro = float(controls["label_permutation"]["all_features"]["real_macro_recall@1"])
    if not 0.0 <= rewired_macro <= 1.0:
        failures.append("macro pós-rewiring fora de [0,1]")
    if not rewired_macro < original_macro:
        failures.append("rewiring não degradou o comparador artesanal")
    if "weighted_degrees_preserved" not in rewire:
        failures.append("rewiring deve registrar se graus ponderados foram preservados")
    if "comment_pesos" not in rewire:
        failures.append("rewiring deve documentar o tratamento dos pesos")
    identity = controls["id_permutation"]
    for key in ("nodes", "edges"):
        if int(identity.get(key, 0)) <= 0:
            failures.append(f"permutação de IDs sem contagem de {key}")
    if not identity.get("snapshot", {}).get("edges_sha256"):
        failures.append("permutação de IDs sem hash do snapshot")
    if not identity.get("labels_follow_permutation"):
        failures.append("rótulos não seguiram a permutação de IDs")
    if not identity.get("features_equivariant") or float(identity.get("features_max_abs_diff", 1.0)) > 1e-9:
        failures.append("features deveriam ser equívocas à permutação de IDs")
    if int(identity.get("label_mismatches", 1)) != 0:
        failures.append("rótulos divergentes após permutação de IDs")
    carried = float(identity.get("carried_split_macro_recall@1", -1))
    if abs(carried - original_macro) > 1e-9:
        failures.append("partição carregada deveria preservar a métrica sob permutação de IDs")
    negatives = controls["degree_matched_negatives"]
    for subset in ("degree_features", "all_features"):
        for mode in ("fine", "coarse", "none"):
            entry = negatives.get(subset, {}).get(mode, {})
            rate = float(entry.get("hit_rate", -1))
            if not 0.0 <= rate <= 1.0:
                failures.append(f"taxa de acerto inválida em {subset}/{mode}")
            if int(entry.get("queries", 0)) <= 0:
                failures.append(f"sem consultas em {subset}/{mode}")
            if str(entry.get("matching", "")) != mode:
                failures.append(f"modo de pareamento divergente em {subset}/{mode}")
    interpretation = report.get("interpretation", {})
    try:
        expected = derive_interpretations(report)
    except (KeyError, TypeError, ValueError) as error:
        failures.append(f"não foi possível derivar interpretações: {error}")
        expected = {}
    for key, value in expected.items():
        recorded = str(interpretation.get(key, ""))
        if recorded != value:
            failures.append(f"interpretação divergente da regra em {key}")
    recorded_pending = sorted(report.get("pending_investigation", []))
    if recorded_pending != derive_pending(expected):
        failures.append("pending_investigation divergente das regras declaradas")
    package = report.get("frozen_package", {})
    if package.get("schema") != "b09-baseline-package":
        failures.append("pacote congelado sem schema esperado")
    manifest_path = Path(manifest).resolve() if manifest else (ROOT / str(package.get("path", "")))
    if not manifest_path.exists():
        failures.append("manifesto congelado ausente")
    else:
        manifest_doc = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest_doc.get("target_data_used") is not False:
            failures.append("manifesto congelado deve declarar que não usou dados do alvo")
        ranking = manifest_doc.get("ranking", [])
        if len(ranking) < 8:
            failures.append("ranking congelado insuficiente")
        for entry in ranking:
            if not 0.0 <= float(entry.get("macro_recall@1", -1)) <= 1.0:
                failures.append(f"métrica fora de [0,1] no ranking: {entry.get('method')}")
            digest = str(entry.get("report_sha256", ""))
            if len(digest) != 64:
                failures.append(f"relatório sem sha256 no ranking: {entry.get('method')}")
            report_file = ROOT / str(entry.get("report", ""))
            if not report_file.exists() or bs.sha256_file(report_file) != digest:
                failures.append(f"hash do relatório divergente: {entry.get('method')}")
        best = max(ranking, key=lambda item: (float(item.get("macro_recall@1", -1)), [-ord(c) for c in item.get("method", "")]))
        if manifest_doc.get("best_comparator") != best["method"]:
            failures.append("melhor comparador do manifesto diverge da regra declarada")
        if manifest_doc.get("best_comparator") != package.get("best_comparator"):
            failures.append("melhor comparador do relatório diverge do manifesto")
        for entry in manifest_doc.get("predictions", []):
            if entry.get("status") != "ok":
                failures.append(f"artefato congelado indisponível/divergente: {entry.get('path')}")
        if len(str(package.get("sha256", ""))) != 64:
            failures.append("pacote congelado sem sha256")
        if bs.sha256_file(manifest_path) != package.get("sha256"):
            failures.append("sha256 do manifesto congelado divergente")
    return failures


def refresh(path: Path) -> dict:
    """Recalcula apenas os campos derivados (interpretação e pendências) de um relatório existente."""
    path = Path(path).resolve()
    report = json.loads(path.read_text(encoding="utf-8"))
    report["interpretation"] = derive_interpretations(report)
    report["pending_investigation"] = derive_pending(report["interpretation"])
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def write_package(report_path: Path, manifest_path: Path) -> dict:
    """Regera o manifesto congelado e atualiza o bloco correspondente no relatório."""
    report_path = Path(report_path).resolve()
    manifest_path = Path(manifest_path).resolve()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    package = frozen_package()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(package, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report["frozen_package"] = {
        "schema": package["schema"],
        "path": str(manifest_path.relative_to(ROOT)),
        "sha256": bs.sha256_file(manifest_path),
        "best_comparator": package["best_comparator"],
        "best_classical": package["best_classical"],
        "predictions_ok": sum(1 for entry in package["predictions"] if entry["status"] == "ok"),
        "predictions_total": len(package["predictions"]),
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("run", "check", "refresh", "package"))
    parser.add_argument("--workdir", type=Path, default=ROOT / "runs" / "b09")
    parser.add_argument("--report", type=Path, default=ROOT / "artifacts" / "reports" / "B09-CONTROLES.json")
    parser.add_argument("--manifest", type=Path, default=ROOT / "data" / "manifests" / "baselines-b09.json")
    parser.add_argument("--draws", type=int, default=LABEL_DRAWS)
    parser.add_argument("--negatives", type=int, default=NEGATIVE_COUNT)
    parser.add_argument("--rewire-multiplier", type=int, default=REWIRE_MULTIPLIER)
    args = parser.parse_args()
    try:
        if args.command == "run":
            report = run(args.workdir, args.report, args.manifest, args.draws, args.negatives, args.rewire_multiplier)
            summary = {
                "label_permutation_all": report["controls"]["label_permutation"]["all_features"]["null_max"],
                "rewire_macro": report["controls"]["degree_preserving_rewiring"]["artisanal_all_macro_recall@1"],
                "rewire_accepted": report["controls"]["degree_preserving_rewiring"]["stats"]["accepted"],
                "id_permutation_carried": report["controls"]["id_permutation"]["carried_split_macro_recall@1"],
                "id_permutation_resplit": report["controls"]["id_permutation"]["resplit_macro_recall@1"],
                "degree_matched_degree": report["controls"]["degree_matched_negatives"]["degree_features"]["fine"]["hit_rate"],
                "degree_matched_all": report["controls"]["degree_matched_negatives"]["all_features"]["fine"]["hit_rate"],
                "best_comparator": report["frozen_package"]["best_comparator"],
                "seconds": report["seconds"],
                "peak_rss_mib": report["peak_rss_mib"],
            }
            print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        elif args.command == "refresh":
            report = refresh(args.report)
            print(json.dumps({"interpretation": report["interpretation"], "pending_investigation": report["pending_investigation"]}, ensure_ascii=False, sort_keys=True))
        elif args.command == "package":
            report = write_package(args.report, args.manifest)
            print(json.dumps(report["frozen_package"], ensure_ascii=False, sort_keys=True))
        else:
            failures = check_report(args.report, args.manifest)
            if failures:
                for failure in failures:
                    print(f"FALHA: {failure}")
                return 1
            print("OK: controles B09 validados (nulos, invariantes e pacote congelado)")
    except (ControlError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FALHA: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
