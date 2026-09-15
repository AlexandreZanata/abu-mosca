#!/usr/bin/env python3
"""Tarefa masked-edge/weight e auditoria de atalhos (M01).

Define o objetivo auto-supervisionado primário do MVP (R07 §4) sobre a fonte
MANC: máscara determinística por seed com co-mascaramento do reverso, negativos
pareados por grau e distância, decoder de duas cabeças por pares de embeddings
(sem tabela por node ID) e especificação de loss/transformação do peso. A fase é
exploratória (G5), apenas na fonte, sem nenhum dado do alvo.

Também audita o atalho: um baseline puramente de grau é ajustado e avaliado nas
mesmas partições, medindo quanto da tarefa é resolvível só por grau na
distribuição pareada e na distribuição aleatória.
"""

import argparse
import json
import resource
import sys
import time
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import scipy.sparse as sp
import scipy.stats as stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import baselines_source as bs  # noqa: E402
import seeds as seedlib  # noqa: E402

MASTER_SEED = 20260914
SOURCE_SNAPSHOT = ROOT / "runs" / "h08" / "source"
VALIDATION_FRACTION = 0.05
REVERSE_CO_MASKING = True
NEGATIVES_PER_POSITIVE = 5
AUDIT_POSITIVES = 5000
TRAIN_PAIRS = 100000
DEGREE_WINDOW = 400
WEIGHT_TRANSFORM = "log1p"
LAMBDA_WEIGHT = 1.0
SCHEMA = "m01-ssl-task"
DECODER_SPEC = "duas cabeças bilineares z_u^T W z_v + b (existência e peso); sem parâmetros por node ID"
DECODER_MODULE = "tools/ssl_decoder.py"
SSL_METRIC = "average precision de existência em arestas retiradas (monitoramento/early stop)"
SELECTION_METRIC = "Macro Recall@1 na fonte (R07 §5); métrica SSL apenas para monitoramento"


class SslTaskError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    return bs.sha256_file(path)


def load_source_edges(snapshot: Path) -> tuple[list[str], np.ndarray, np.ndarray, np.ndarray]:
    nodes = pq.read_table(snapshot / "nodes.parquet")
    edges = pq.read_table(snapshot / "edges.parquet", columns=["source", "target", "weight"])
    ids = sorted(nodes["id"].combine_chunks().to_pylist())
    value_set = pa.array(ids, type=pa.string())
    src = pc.index_in(edges["source"].combine_chunks(), value_set=value_set).fill_null(-1).to_numpy(zero_copy_only=False).astype(np.int64)
    dst = pc.index_in(edges["target"].combine_chunks(), value_set=value_set).fill_null(-1).to_numpy(zero_copy_only=False).astype(np.int64)
    wgt = np.asarray(edges["weight"].combine_chunks().to_pylist(), dtype=np.int64)
    if np.any(src < 0) or np.any(dst < 0):
        raise SslTaskError("aresta com endpoint fora dos nodes")
    if np.any(wgt < 0):
        raise SslTaskError("peso negativo no snapshot")
    return ids, src, dst, wgt


def ekey(u: np.ndarray, v: np.ndarray, n_nodes: int) -> np.ndarray:
    return u.astype(np.int64) * n_nodes + v.astype(np.int64)


def splitmix64(values: np.ndarray) -> np.ndarray:
    x = values.astype(np.uint64).copy()
    x ^= x >> np.uint64(30)
    x *= np.uint64(0xBF58476D1CE4E5B9)
    x ^= x >> np.uint64(27)
    x *= np.uint64(0x94D049BB133111EB)
    x ^= x >> np.uint64(31)
    return x


def hash_mask(src: np.ndarray, dst: np.ndarray, n_nodes: int, seed: int, fraction: float) -> np.ndarray:
    if not 0.0 < fraction < 1.0:
        raise SslTaskError("fração de validação deve ficar em (0,1)")
    keys = ekey(src, dst, n_nodes).astype(np.uint64)
    hashed = splitmix64(keys ^ np.uint64(seed & 0xFFFFFFFFFFFFFFFF))
    threshold = np.uint64(int(round(fraction * 10000)))
    return (hashed % np.uint64(10000)) < threshold


def build_mask(src: np.ndarray, dst: np.ndarray, n_nodes: int, seed: int, fraction: float = VALIDATION_FRACTION) -> dict:
    initial = hash_mask(src, dst, n_nodes, seed, fraction)
    extra = 0
    mask = initial
    if REVERSE_CO_MASKING:
        val_keys = ekey(src[initial], dst[initial], n_nodes)
        reverse_keys = ekey(dst, src, n_nodes)
        extra_mask = np.isin(reverse_keys, val_keys) & ~initial
        extra = int(extra_mask.sum())
        mask = initial | extra_mask
    return {
        "seed": int(seed),
        "fraction": fraction,
        "reverse_co_masking": REVERSE_CO_MASKING,
        "validation_edges": int(mask.sum()),
        "initial_hash_selected": int(initial.sum()),
        "reverse_comasked": extra,
        "train_edges": int((~mask).sum()),
        "self_loops_in_validation": int(((src == dst) & mask).sum()),
        "mask": mask,
    }


def training_view(src: np.ndarray, dst: np.ndarray, wgt: np.ndarray, mask: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    keep = ~mask
    return src[keep], dst[keep], wgt[keep]


def build_csr(src: np.ndarray, dst: np.ndarray, n_nodes: int) -> sp.csr_matrix:
    return sp.coo_matrix((np.ones(len(src), dtype=np.float64), (src, dst)), shape=(n_nodes, n_nodes)).tocsr()


def degree_tables(src: np.ndarray, dst: np.ndarray, wgt: np.ndarray, n_nodes: int) -> dict:
    tables = {
        "count_in": np.bincount(dst, minlength=n_nodes).astype(np.float64),
        "count_out": np.bincount(src, minlength=n_nodes).astype(np.float64),
        "weighted_in": np.bincount(dst, weights=wgt.astype(np.float64), minlength=n_nodes),
        "weighted_out": np.bincount(src, weights=wgt.astype(np.float64), minlength=n_nodes),
    }
    tables["log_total"] = np.log1p(tables["weighted_in"] + tables["weighted_out"])
    for name, values in tables.items():
        if not np.isfinite(values).all():
            raise SslTaskError(f"tabela de grau com valor não finito: {name}")
    return tables


def separation_checks(src: np.ndarray, dst: np.ndarray, train_idx: np.ndarray, val_idx: np.ndarray, n_nodes: int) -> dict:
    val_keys = set(ekey(src[val_idx], dst[val_idx], n_nodes).tolist())
    forward = sum(1 for key in ekey(src[train_idx], dst[train_idx], n_nodes).tolist() if key in val_keys)
    reverse = sum(1 for key in ekey(dst[train_idx], src[train_idx], n_nodes).tolist() if key in val_keys)
    if forward or reverse:
        raise SslTaskError(f"vazamento de holdout: forward={forward} reverse={reverse}")
    return {"held_out_absent_from_train_view": True, "reverse_absent_from_train_view": True, "leaks": 0}


def out_neighbors(csr: sp.csr_matrix, node: int) -> set[int]:
    return set(int(value) for value in csr.indices[csr.indptr[node] : csr.indptr[node + 1]])


def two_hop_membership(csr: sp.csr_matrix, node: int) -> set[int]:
    reachable = csr.getrow(node).dot(csr)
    return set(int(value) for value in reachable.indices if value != node)


def match_degree_window(
    u: int,
    v: int,
    forbidden: set[int],
    log_total: np.ndarray,
    order: np.ndarray,
    rank: np.ndarray,
    k: int,
    class_filter=None,
    window: int = DEGREE_WINDOW,
) -> list[int]:
    position = int(rank[v])
    for span in (window, window * 4, len(order)):
        low = max(0, position - span)
        high = min(len(order), position + span + 1)
        candidates = [int(w) for w in order[low:high] if int(w) != u and int(w) != v and int(w) not in forbidden]
        if class_filter is not None:
            candidates = [w for w in candidates if class_filter(w)]
        if candidates:
            candidates.sort(key=lambda w: (abs(float(log_total[w]) - float(log_total[v])), w))
            return candidates[:k]
    return []


def sample_negatives(
    positives_u: np.ndarray,
    positives_v: np.ndarray,
    train_csr: sp.csr_matrix,
    full_csr: sp.csr_matrix,
    log_total: np.ndarray,
    n_nodes: int,
    k: int = NEGATIVES_PER_POSITIVE,
) -> dict:
    order = np.argsort(log_total, kind="stable")
    rank = np.empty(n_nodes, dtype=np.int64)
    rank[order] = np.arange(n_nodes)
    neg_u: list[int] = []
    neg_v: list[int] = []
    degree_diffs: list[float] = []
    class_match: list[bool] = []
    class_positives: list[str] = []
    shortfalls = 0
    for index in range(len(positives_u)):
        u = int(positives_u[index])
        v = int(positives_v[index])
        one_hop = out_neighbors(full_csr, u)
        two_hop = two_hop_membership(train_csr, u)
        positive_class = "2" if v in two_hop else "far"
        if positive_class == "2":
            class_filter = lambda w, two=two_hop: w in two
        else:
            class_filter = lambda w, two=two_hop: w not in two
        selected = match_degree_window(u, v, one_hop, log_total, order, rank, k, class_filter)
        if len(selected) < k:
            shortfalls += 1
        for w in selected:
            neg_u.append(u)
            neg_v.append(w)
            degree_diffs.append(abs(float(log_total[w]) - float(log_total[v])))
            class_match.append((w in two_hop) == (positive_class == "2"))
            class_positives.append(positive_class)
    if not neg_u:
        raise SslTaskError("nenhum negativo amostrado")
    degree_diffs_array = np.asarray(degree_diffs, dtype=np.float64)
    class_positives_array = np.asarray(class_positives, dtype=object)
    return {
        "u": np.asarray(neg_u, dtype=np.int64),
        "v": np.asarray(neg_v, dtype=np.int64),
        "sample_positives": int(len(positives_u)),
        "negatives_total": int(len(neg_u)),
        "negatives_per_positive": k,
        "degree_abs_log_diff_median": round(float(np.median(degree_diffs_array)), 6),
        "degree_abs_log_diff_p90": round(float(np.percentile(degree_diffs_array, 90)), 6),
        "degree_abs_log_diff_max": round(float(degree_diffs_array.max()), 6),
        "class_match_rate": round(float(np.mean(class_match)), 6),
        "class_two": int(np.sum(class_positives_array == "2")),
        "class_far": int(np.sum(class_positives_array == "far")),
        "shortfall_positives": int(shortfalls),
    }


def auc_ap(scores: np.ndarray, labels: np.ndarray) -> dict:
    scores = np.asarray(scores, dtype=np.float64)
    labels = np.asarray(labels, dtype=np.int64)
    positives = int(labels.sum())
    negatives = int(len(labels) - positives)
    if positives == 0 or negatives == 0:
        raise SslTaskError("AUC/AP exigem positivos e negativos")
    ranks = stats.rankdata(scores, method="average")
    auc = float((ranks[labels == 1].sum() - positives * (positives + 1) / 2.0) / (positives * negatives))
    order = np.argsort(-scores, kind="stable")
    sorted_scores = scores[order]
    sorted_labels = labels[order]
    true_positives = np.cumsum(sorted_labels)
    false_positives = np.arange(1, len(sorted_labels) + 1) - true_positives
    group_end = np.empty(len(sorted_labels), dtype=bool)
    group_end[-1] = True
    group_end[:-1] = sorted_scores[:-1] != sorted_scores[1:]
    precision = true_positives[group_end] / (true_positives[group_end] + false_positives[group_end])
    recall = true_positives[group_end] / positives
    ap = float(np.sum(np.diff(np.concatenate([[0.0], recall])) * precision))
    return {"auc": round(auc, 6), "ap": round(ap, 6), "positives": positives, "negatives": negatives}


def logistic_fit(features: np.ndarray, labels: np.ndarray, iterations: int = 400, lr: float = 0.5, l2: float = 1e-3) -> tuple[np.ndarray, float, np.ndarray, np.ndarray]:
    mean = features.mean(axis=0)
    std = features.std(axis=0)
    std[std < 1e-9] = 1e-9
    scaled = (features - mean) / std
    weights = np.zeros(scaled.shape[1], dtype=np.float64)
    bias = 0.0
    for _ in range(iterations):
        logits = scaled @ weights + bias
        probs = 1.0 / (1.0 + np.exp(-logits))
        error = probs - labels
        weights -= lr * (scaled.T @ error / len(labels) + l2 * weights)
        bias -= lr * float(error.mean())
    return weights, bias, mean, std


def logistic_predict(features: np.ndarray, weights: np.ndarray, bias: float, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    scaled = (features - mean) / std
    return 1.0 / (1.0 + np.exp(-(scaled @ weights + bias)))


def _pair_features(degrees: dict, u: np.ndarray, v: np.ndarray) -> np.ndarray:
    return np.column_stack(
        [
            np.log1p(degrees["count_in"][u]),
            np.log1p(degrees["count_out"][u]),
            np.log1p(degrees["count_in"][v]),
            np.log1p(degrees["count_out"][v]),
            degrees["log_total"][u],
            degrees["log_total"][v],
        ]
    )


def _display_path(path: Path) -> str:
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def run(workdir: Path, report_path: Path, audit_positives: int = AUDIT_POSITIVES, k: int = NEGATIVES_PER_POSITIVE, train_pairs: int = TRAIN_PAIRS, snapshot: Path = SOURCE_SNAPSHOT) -> dict:
    started = time.perf_counter()
    workdir = Path(workdir).resolve()
    report_path = Path(report_path).resolve()
    snapshot = Path(snapshot)
    workdir.mkdir(parents=True, exist_ok=True)
    ids, src, dst, wgt = load_source_edges(snapshot)
    n_nodes = len(ids)
    seeds = {
        "mask": seedlib.derive_seed(MASTER_SEED, "m01", "mask"),
        "audit-positive-sample": seedlib.derive_seed(MASTER_SEED, "m01", "audit-positive-sample"),
        "degree-baseline": seedlib.derive_seed(MASTER_SEED, "m01", "degree-baseline"),
        "decoder-smoke": seedlib.derive_seed(MASTER_SEED, "m01", "decoder-smoke"),
    }
    mask_info = build_mask(src, dst, n_nodes, seeds["mask"])
    mask = mask_info.pop("mask")
    train_idx = np.nonzero(~mask)[0]
    val_idx = np.nonzero(mask)[0]
    separation = separation_checks(src, dst, train_idx, val_idx, n_nodes)
    train_src, train_dst, train_wgt = training_view(src, dst, wgt, mask)
    train_csr = build_csr(train_src, train_dst, n_nodes)
    full_csr = build_csr(src, dst, n_nodes)
    degrees = degree_tables(train_src, train_dst, train_wgt, n_nodes)
    rng = np.random.RandomState(seeds["audit-positive-sample"] % (2**32))
    sample_idx = rng.choice(len(val_idx), size=min(audit_positives, len(val_idx)), replace=False)
    positives_u = src[val_idx[sample_idx]]
    positives_v = dst[val_idx[sample_idx]]
    negatives = sample_negatives(positives_u, positives_v, train_csr, full_csr, degrees["log_total"], n_nodes, k=k)
    negative_labels = np.concatenate([np.ones(len(positives_u), dtype=np.int64), np.zeros(negatives["negatives_total"], dtype=np.int64)])
    # baseline de grau treinado na fonte (sem rótulo de tipo): negativos por faixa de grau
    rng_train = np.random.RandomState(seeds["degree-baseline"] % (2**32))
    train_pair_idx = rng_train.choice(len(train_idx), size=min(train_pairs, len(train_idx)), replace=False)
    train_pos_u = src[train_idx[train_pair_idx]]
    train_pos_v = dst[train_idx[train_pair_idx]]
    order = np.argsort(degrees["log_total"], kind="stable")
    rank = np.empty(n_nodes, dtype=np.int64)
    rank[order] = np.arange(n_nodes)
    train_neg_u: list[int] = []
    train_neg_v: list[int] = []
    for u, v in zip(train_pos_u.tolist(), train_pos_v.tolist()):
        one_hop = out_neighbors(full_csr, u)
        picked = match_degree_window(u, v, one_hop, degrees["log_total"], order, rank, 1)
        if picked:
            train_neg_u.append(u)
            train_neg_v.append(picked[0])
    train_neg_u_array = np.asarray(train_neg_u, dtype=np.int64)
    train_neg_v_array = np.asarray(train_neg_v, dtype=np.int64)
    train_features = np.vstack([_pair_features(degrees, train_neg_u_array, train_neg_v_array), _pair_features(degrees, train_pos_u, train_pos_v)])
    train_labels = np.concatenate([np.zeros(len(train_neg_u_array), dtype=np.int64), np.ones(len(train_pos_u), dtype=np.int64)])
    weights, bias, mean, std = logistic_fit(train_features, train_labels)
    matched_features = _pair_features(degrees, np.concatenate([positives_u, negatives["u"]]), np.concatenate([positives_v, negatives["v"]]))
    matched = auc_ap(logistic_predict(matched_features, weights, bias, mean, std), negative_labels)
    rng_unmatched = np.random.RandomState((seeds["degree-baseline"] + 1) % (2**32))
    candidate_unmatched = rng_unmatched.randint(0, n_nodes, size=len(positives_u))
    keep = candidate_unmatched != positives_v
    if not keep.all():
        candidate_unmatched[~keep] = (candidate_unmatched[~keep] + 1) % n_nodes
    unmatched_features = _pair_features(degrees, np.concatenate([positives_u, positives_u]), np.concatenate([candidate_unmatched, positives_v]))
    unmatched_labels = np.concatenate([np.zeros(len(positives_u), dtype=np.int64), np.ones(len(positives_u), dtype=np.int64)])
    unmatched = auc_ap(logistic_predict(unmatched_features, weights, bias, mean, std), unmatched_labels)
    import ssl_decoder  # dependência de torch apenas no smoke (M01)
    smoke = ssl_decoder.decoder_smoke(seed=seeds["decoder-smoke"] % (2**32))
    report = {
        "schema": SCHEMA,
        "status": "exploratory-only; sem nenhum dado do alvo",
        "source": {
            "snapshot": _display_path(snapshot),
            "dataset": bs.DATASET,
            "release": bs.RELEASE,
            "nodes": int(n_nodes),
            "edges": int(len(src)),
            "edges_sha256": sha256_file(snapshot / "edges.parquet"),
            "nodes_sha256": sha256_file(snapshot / "nodes.parquet"),
        },
        "seeds": seeds,
        "task": {
            "validation_fraction": VALIDATION_FRACTION,
            "reverse_co_masking": REVERSE_CO_MASKING,
            "negatives_per_positive": k,
            "weight_transform": WEIGHT_TRANSFORM,
            "lambda_weight": LAMBDA_WEIGHT,
            "loss": {"existence": "bce_with_logits", "weight": "mse sobre log1p(peso)"},
            "decoder": DECODER_SPEC,
            "decoder_module": DECODER_MODULE,
            "ssl_validation_metric": SSL_METRIC,
            "selection_metric": SELECTION_METRIC,
        },
        "mask": mask_info,
        "separation": separation,
        "negatives": {key: value for key, value in negatives.items() if key not in ("u", "v")},
        "shortcut_degree_baseline": {
            "training": {
                "positive_pairs": int(len(train_pos_u)),
                "negative_pairs": int(len(train_neg_u_array)),
                "negative_rule": "mesma faixa de grau total, sem aresta verdadeira (treino)",
                "features": ["log1p(grau_in/out de u)", "log1p(grau_in/out de v)", "log1p(grau total de u/v)"],
            },
            "validation_matched": matched,
            "validation_unmatched": unmatched,
        },
        "decoder_smoke": smoke,
        "resources": {"seconds": round(time.perf_counter() - started, 3), "peak_rss_mib": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1), "device": "cpu"},
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def check_report(path: Path) -> list[str]:
    failures: list[str] = []
    path = Path(path).resolve()
    if not path.exists():
        return [f"relatório ausente: {path}"]
    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("schema") != SCHEMA:
        failures.append("schema divergente")
    status = str(report.get("status", ""))
    if "exploratory-only" not in status or "sem nenhum dado do alvo" not in status:
        failures.append("status deve declarar modo exploratório e ausência de dados do alvo")
    source = report.get("source", {})
    if int(source.get("nodes", 0)) <= 0 or int(source.get("edges", 0)) <= 0:
        failures.append("fonte sem contagens")
    mask = report.get("mask", {})
    for key in ("validation_edges", "train_edges", "initial_hash_selected", "reverse_comasked"):
        if int(mask.get(key, -1)) < 0:
            failures.append(f"máscara sem contagem válida: {key}")
    edges = max(int(source.get("edges", 1)), 1)
    fraction = float(mask.get("validation_edges", 0)) / edges
    if not 0.03 <= fraction <= 0.20:
        failures.append("fração de validação fora do esperado")
    if not mask.get("reverse_co_masking"):
        failures.append("co-mascaramento do reverso desligado")
    separation = report.get("separation", {})
    if not separation.get("held_out_absent_from_train_view") or not separation.get("reverse_absent_from_train_view"):
        failures.append("holdout ou reverso presente na visão de treino")
    if int(separation.get("leaks", 1)) != 0:
        failures.append("vazamento de holdout detectado")
    negatives = report.get("negatives", {})
    if int(negatives.get("class_two", 0)) + int(negatives.get("class_far", 0)) <= 0:
        failures.append("distribuição de distância dos negativos ausente")
    if not 0.0 <= float(negatives.get("class_match_rate", -1)) <= 1.0:
        failures.append("taxa de pareamento de classe inválida")
    if float(negatives.get("degree_abs_log_diff_median", -1)) < 0:
        failures.append("diferença de grau dos negativos inválida")
    if int(negatives.get("negatives_total", 0)) <= 0:
        failures.append("nenhum negativo registrado")
    baseline = report.get("shortcut_degree_baseline", {})
    if not baseline.get("training", {}).get("features"):
        failures.append("baseline de grau sem features declaradas")
    for name in ("validation_matched", "validation_unmatched"):
        entry = baseline.get(name, {})
        for key in ("auc", "ap"):
            if not 0.0 <= float(entry.get(key, -1)) <= 1.0:
                failures.append(f"baseline de grau com {key} inválido em {name}")
    task = report.get("task", {})
    if task.get("weight_transform") != WEIGHT_TRANSFORM:
        failures.append("transformação de peso divergente")
    if float(task.get("lambda_weight", -1)) != LAMBDA_WEIGHT:
        failures.append("peso da loss de peso divergente")
    if "sem parâmetros por node ID" not in str(task.get("decoder", "")):
        failures.append("decoder deve declarar ausência de parâmetros por node ID")
    if not str(task.get("decoder_module", "")).endswith("ssl_decoder.py"):
        failures.append("módulo do decoder não declarado")
    if "Macro Recall@1" not in str(task.get("selection_metric", "")):
        failures.append("métrica de seleção deve seguir o pré-registro")
    smoke = report.get("decoder_smoke", {})
    if int(smoke.get("per_node_parameters", 1)) != 0:
        failures.append("decoder não pode ter parâmetros por node")
    if not smoke.get("gradients_finite") or not smoke.get("loss_decreased"):
        failures.append("smoke do decoder não convergiu com gradientes finitos")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("run", "check"))
    parser.add_argument("--workdir", type=Path, default=ROOT / "runs" / "m01")
    parser.add_argument("--report", type=Path, default=ROOT / "artifacts" / "reports" / "M01-SSL-TASK.json")
    parser.add_argument("--positives", type=int, default=AUDIT_POSITIVES)
    parser.add_argument("--negatives", type=int, default=NEGATIVES_PER_POSITIVE)
    parser.add_argument("--train-pairs", type=int, default=TRAIN_PAIRS)
    parser.add_argument("--snapshot", type=Path, default=SOURCE_SNAPSHOT)
    args = parser.parse_args()
    try:
        if args.command == "run":
            report = run(args.workdir, args.report, args.positives, args.negatives, args.train_pairs, args.snapshot)
            print(json.dumps({
                "mask": {key: value for key, value in report["mask"].items()},
                "negatives": report["negatives"],
                "shortcut_degree_baseline": report["shortcut_degree_baseline"],
                "decoder_smoke": report["decoder_smoke"],
                "resources": report["resources"],
            }, ensure_ascii=False, sort_keys=True))
        else:
            failures = check_report(args.report)
            if failures:
                for failure in failures:
                    print(f"FALHA: {failure}")
                return 1
            print("OK: tarefa M01 validada (máscara, separação, negativos, atalho e decoder)")
    except (SslTaskError, FileNotFoundError, json.JSONDecodeError) as error:
        print(f"FALHA: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
