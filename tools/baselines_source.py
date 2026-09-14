#!/usr/bin/env python3
"""Baselines internos da fonte: random estratificado, maioria e degree-only (B03).

Executa apenas **dentro da fonte MANC** (rótulos públicos da fonte), com split
determinístico por hash de ID, transformações z-score ajustadas somente no
treino (source-fit) e seeds do pré-registro. Não lê nada do alvo e não consulta
scores do alvo. Saídas: predições congeláveis por baseline/seed, métricas
internas e conferência entre chance analítica e simulada.
"""

import argparse
import hashlib
import json
import random
import resource
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pyarrow.compute as pc
import pyarrow.feather as feather
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import metrics  # noqa: E402
import opaque_ids  # noqa: E402

DATASET, RELEASE = "MANC", "manc:v1.2.1"
K_MIN = 10
SPLIT_FRACTION = 0.8
SELECTION_SEEDS = (297979363399525401, 1699981902186354598, 3729859090210297070)
RANDOM_DRAWS = 200
DEGREE_FEATURES = ("in_degree", "out_degree", "weighted_in", "weighted_out")


class BaselineError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def load_source_labels(properties: Path) -> tuple[dict[str, str], dict[str, int]]:
    """Rótulos públicos da fonte por ID opaco, filtrando classes com n ≥ K."""
    table = feather.read_table(properties, memory_map=True)
    for column in ("bodyId", "type"):
        if column not in table.column_names:
            raise BaselineError(f"coluna ausente em propriedades: {column}")
    counts = Counter(value for value in table["type"].to_pylist() if value)
    kept_classes = {name for name, total in counts.items() if total >= K_MIN}
    labels = {}
    for body, name in zip(table["bodyId"].to_pylist(), table["type"].to_pylist()):
        if name in kept_classes:
            labels[opaque_ids.opaque_node_id(DATASET, RELEASE, body)] = name
    if not labels:
        raise BaselineError("nenhum rótulo de fonte com K mínimo")
    return labels, {"types_total": len(counts), "classes_k_min": len(kept_classes), "nodes_labeled": len(labels)}


def split_deterministic(labels: dict[str, str], fraction: float = SPLIT_FRACTION) -> tuple[dict[str, str], dict[str, str]]:
    by_class: dict[str, list[str]] = defaultdict(list)
    for node, name in labels.items():
        by_class[name].append(node)
    train, val = {}, {}
    for name, nodes in by_class.items():
        ordered = sorted(nodes, key=lambda node: hashlib.sha256(f"{node}|split".encode()).hexdigest())
        cut = max(1, int(len(ordered) * fraction))
        for node in ordered[:cut]:
            train[node] = name
        for node in ordered[cut:]:
            val[node] = name
    return train, val


def degree_features(snapshot: Path) -> dict[str, list[float]]:
    nodes = pq.read_table(snapshot / "nodes.parquet")
    edges = pq.read_table(snapshot / "edges.parquet", columns=["source", "target", "weight"])
    node_ids = nodes["id"].combine_chunks()
    pre = pc.index_in(edges["source"].combine_chunks(), value_set=node_ids).to_numpy(zero_copy_only=False)
    post = pc.index_in(edges["target"].combine_chunks(), value_set=node_ids).to_numpy(zero_copy_only=False)
    weights = edges["weight"].to_numpy(zero_copy_only=False)
    n = len(node_ids)
    weighted_in = np.bincount(post, weights=weights, minlength=n).astype("float64")
    weighted_out = np.bincount(pre, weights=weights, minlength=n).astype("float64")
    count_in = np.bincount(post, minlength=n).astype("float64")
    count_out = np.bincount(pre, minlength=n).astype("float64")
    ids = node_ids.to_pylist()
    return {
        node_id: [count_in[index], count_out[index], weighted_in[index], weighted_out[index]]
        for index, node_id in enumerate(ids)
    }


def fit_stats(matrix: np.ndarray) -> dict:
    mean = matrix.mean(axis=0)
    std = matrix.std(axis=0)
    std[std < 1e-6] = 1e-6
    return {"mean": mean.tolist(), "std": std.tolist()}


def transform(matrix: np.ndarray, stats: dict) -> np.ndarray:
    return (matrix - np.asarray(stats["mean"])) / np.asarray(stats["std"])


def evaluate_predictions(val_labels: dict[str, str], predictions: dict[str, str]) -> dict:
    ranked = {node: [predictions[node]] for node in val_labels}
    return metrics.evaluate(ranked, val_labels, k_values=(1, 5))


def run(properties: Path, snapshot: Path, out_dir: Path, report_path: Path, seeds=SELECTION_SEEDS) -> dict:
    started = time.perf_counter()
    labels, label_meta = load_source_labels(properties)
    features = degree_features(snapshot)
    dropped = [node for node in labels if node not in features]
    labels = {node: name for node, name in labels.items() if node in features}
    if dropped:
        kept = Counter(labels.values())
        labels = {node: name for node, name in labels.items() if kept[name] >= K_MIN}
        label_meta["nodes_dropped_without_features"] = len(dropped)
    label_meta["nodes_used"] = len(labels)
    label_meta["classes_used"] = len(set(labels.values()))
    if not labels:
        raise BaselineError("nenhum rótulo utilizável após mapear para o snapshot")
    train, val = split_deterministic(labels)
    train_classes = Counter(train.values())
    val_classes = Counter(val.values())
    classes = sorted(set(train_classes) | set(val_classes))
    p_train = np.array([train_classes.get(name, 0) / len(train) for name in classes])
    p_val = np.array([val_classes.get(name, 0) / len(val) for name in classes])
    majority_class = max(classes, key=lambda name: (train_classes.get(name, 0), name))
    analytical = {
        "uniform": 1.0 / len(classes),
        "stratified_random": float((p_train * p_val).sum()),
        "majority": float(p_val[classes.index(majority_class)]),
    }
    results: dict = {"baselines": {}, "analytical": analytical}
    out_dir.mkdir(parents=True, exist_ok=True)
    predictions_paths = []
    majority_predictions = {node: majority_class for node in val}
    results["baselines"]["majority"] = evaluate_predictions(val, majority_predictions)
    results["baselines"]["majority"]["analytical_accuracy"] = analytical["majority"]
    results["baselines"]["majority"]["simulated_accuracy"] = results["baselines"]["majority"]["recall"]["@1"]["micro"]

    simulated = []
    random_predictions_by_seed = {}
    for seed in seeds:
        rng = random.Random(int(seed))
        predictions = {node: rng.choices(classes, weights=p_train, k=1)[0] for node in val}
        random_predictions_by_seed[seed] = predictions
        simulated.append(evaluate_predictions(val, predictions)["recall"]["@1"]["micro"])
    draws = []
    for _ in range(RANDOM_DRAWS):
        rng = random.Random(int(seeds[0]) + len(draws))
        predictions = {node: rng.choices(classes, weights=p_train, k=1)[0] for node in val}
        draws.append(evaluate_predictions(val, predictions)["recall"]["@1"]["micro"])
    results["baselines"]["stratified_random"] = {
        "seeds": list(seeds),
        "per_seed_accuracy": [round(value, 6) for value in simulated],
        "median_accuracy": round(sorted(simulated)[len(simulated) // 2], 6),
        "analytical_accuracy": round(analytical["stratified_random"], 6),
        "simulated_draws_mean": round(sum(draws) / len(draws), 6),
        "draws": RANDOM_DRAWS,
    }
    for index, seed in enumerate(seeds):
        path = out_dir / f"predictions-random-seed{index}.json"
        path.write_text(json.dumps(random_predictions_by_seed[seed], sort_keys=True) + "\n", encoding="utf-8")
        predictions_paths.append({"baseline": "stratified_random", "seed_index": index, "path": path.as_posix(), "sha256": sha256_file(path)})

    stats = fit_stats(np.asarray([features[node][: len(DEGREE_FEATURES)] for node in train]))
    train_matrix = transform(np.asarray([features[node][: len(DEGREE_FEATURES)] for node in train]), stats)
    val_matrix = transform(np.asarray([features[node][: len(DEGREE_FEATURES)] for node in val]), stats)
    centroids = {}
    for name in classes:
        rows = [train_matrix[index] for index, node in enumerate(train) if train[node] == name]
        if rows:
            centroids[name] = np.mean(rows, axis=0)
    degree_predictions = {}
    for index, node in enumerate(val):
        distances = {name: float(np.linalg.norm(val_matrix[index] - centroid)) for name, centroid in centroids.items()}
        degree_predictions[node] = min(distances, key=lambda name: (distances[name], name))
    results["baselines"]["degree_only"] = evaluate_predictions(val, degree_predictions)
    results["baselines"]["degree_only"]["analytical_accuracy"] = None
    path = out_dir / "predictions-degree-only.json"
    path.write_text(json.dumps(degree_predictions, sort_keys=True) + "\n", encoding="utf-8")
    predictions_paths.append({"baseline": "degree_only", "path": path.as_posix(), "sha256": sha256_file(path)})
    path = out_dir / "predictions-majority.json"
    path.write_text(json.dumps(majority_predictions, sort_keys=True) + "\n", encoding="utf-8")
    predictions_paths.append({"baseline": "majority", "path": path.as_posix(), "sha256": sha256_file(path)})

    report = {
        "schema": "b03-source-baselines",
        "dataset": DATASET,
        "release": RELEASE,
        "labels": label_meta,
        "split": {"train": len(train), "val": len(val), "classes": len(classes), "fraction": SPLIT_FRACTION},
        "degree_features": list(DEGREE_FEATURES),
        "stats_source_fit": stats,
        "predictions": predictions_paths,
        "results": results,
        "seconds": round(time.perf_counter() - started, 3),
        "peak_rss_mib": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--properties", type=Path, required=True)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = run(args.properties, args.snapshot, args.out_dir, args.report)
    except (BaselineError, FileNotFoundError) as error:
        print(f"FALHA: {error}", file=sys.stderr)
        return 1
    summary = {
        "labels": report["labels"],
        "split": report["split"],
        "analytical": report["results"]["analytical"],
        "majority": report["results"]["baselines"]["majority"]["simulated_accuracy"],
        "random_median": report["results"]["baselines"]["stratified_random"]["median_accuracy"],
        "random_analytical": report["results"]["baselines"]["stratified_random"]["analytical_accuracy"],
        "random_simulated_mean": report["results"]["baselines"]["stratified_random"]["simulated_draws_mean"],
        "degree_only_macro@1": report["results"]["baselines"]["degree_only"]["recall"]["@1"]["macro"],
        "seconds": report["seconds"],
        "peak_rss_mib": report["peak_rss_mib"],
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
