#!/usr/bin/env python3
"""Estatísticas artesanais interpretáveis com probe comum (B04).

Extrai famílias de features somente-topologia de um grafo canônico (graus
ponderados, reciprocidade, clustering não dirigido, motivos dirigidos simples e
resumos de vizinhança), ajusta um probe comum (z-score source-fit + centroide
mais próximo) e mede cada família isoladamente e combinada, com ablação. Nada
de alvo, rótulos avaliativos, região, posição ou morfologia entra nas features.
"""

import argparse
import hashlib
import json
import resource
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pyarrow.compute as pc
import pyarrow.parquet as pq
import scipy.sparse as sp

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import baselines_source as bs  # noqa: E402
import metrics  # noqa: E402

FEATURE_VERSION = "1.0"
FAMILIES = {
    "degree": ("in_degree", "out_degree", "weighted_in", "weighted_out"),
    "reciprocity": ("reciprocal_weight_ratio", "reciprocal_count_ratio"),
    "clustering": ("clustering_undirected",),
    "motifs": ("feedforward_paths", "bottleneck_ratio"),
    "neighborhood": ("successor_out_degree_mean", "predecessor_in_degree_mean"),
}
FEATURE_ORDER = tuple(name for family in FAMILIES.values() for name in family)
INTERRUPTED_FEATURES = (
    {
        "feature": "directed_triangle_ratio",
        "reason": "contagem de triângulos dirigidos exigia produto esparso potencialmente denso; interrompida nesta fase",
    },
)
FORBIDDEN = ("type", "region", "position", "neuropil", "morphology", "label")


class ArtisanalError(RuntimeError):
    pass


def _load_graph(snapshot: Path):
    nodes = pq.read_table(snapshot / "nodes.parquet")
    edges = pq.read_table(snapshot / "edges.parquet", columns=["source", "target", "weight"])
    node_ids = nodes["id"].combine_chunks()
    pre = pc.index_in(edges["source"].combine_chunks(), value_set=node_ids).to_numpy(zero_copy_only=False)
    post = pc.index_in(edges["target"].combine_chunks(), value_set=node_ids).to_numpy(zero_copy_only=False)
    weights = edges["weight"].to_numpy(zero_copy_only=False).astype("float64")
    if np.any(pre < 0) or np.any(post < 0):
        raise ArtisanalError("aresta com endpoint fora dos nodes")
    return node_ids.to_pylist(), pre, post, weights


def extract_features(snapshot: Path) -> tuple[list[str], dict[str, np.ndarray]]:
    ids, pre, post, weights = _load_graph(snapshot)
    n = len(ids)
    weighted_in = np.bincount(post, weights=weights, minlength=n)
    weighted_out = np.bincount(pre, weights=weights, minlength=n)
    count_in = np.bincount(post, minlength=n).astype("float64")
    count_out = np.bincount(pre, minlength=n).astype("float64")
    pair_weight: dict[tuple[int, int], float] = {}
    for source, target, weight in zip(pre, post, weights):
        pair_weight[(int(source), int(target))] = pair_weight.get((int(source), int(target)), 0.0) + float(weight)
    reciprocal_weight = np.zeros(n)
    reciprocal_count = np.zeros(n)
    for (source, target), weight in pair_weight.items():
        reverse = pair_weight.get((target, source))
        if reverse is not None:
            reciprocal_weight[source] += min(weight, reverse)
            reciprocal_count[source] += 1
    reciprocal_weight_ratio = np.divide(reciprocal_weight, weighted_out, out=np.zeros(n), where=weighted_out > 0)
    reciprocal_count_ratio = np.divide(reciprocal_count, count_out, out=np.zeros(n), where=count_out > 0)
    del pair_weight, reciprocal_weight, reciprocal_count

    adjacency = sp.coo_matrix(
        (np.ones(len(pre)), (pre, post)), shape=(n, n)
    ).tocsr()
    adjacency.data[:] = 1.0
    undirected = (adjacency + adjacency.T).tocsr()
    undirected.data[:] = 1.0
    undirected.setdiag(0)
    undirected.eliminate_zeros()
    triangles = (undirected @ undirected).multiply(undirected).sum(axis=1).A1 / 2.0
    degree_undirected = np.asarray(undirected.sum(axis=1)).ravel()
    possible = degree_undirected * (degree_undirected - 1) / 2.0
    clustering = np.divide(triangles, np.maximum(possible, 1.0), out=np.zeros(n), where=possible > 0)

    feedforward_paths = count_in * count_out
    bottleneck_ratio = np.divide(
        np.minimum(count_in, count_out), np.maximum(count_in + count_out, 1.0)
    )
    successor_out_degree = np.divide(
        adjacency @ count_out, np.maximum(count_out, 1.0), out=np.zeros(n), where=count_out > 0
    )
    predecessor_in_degree = np.divide(
        adjacency.T @ count_in, np.maximum(count_in, 1.0), out=np.zeros(n), where=count_in > 0
    )
    features = {
        "in_degree": count_in,
        "out_degree": count_out,
        "weighted_in": weighted_in,
        "weighted_out": weighted_out,
        "reciprocal_weight_ratio": reciprocal_weight_ratio,
        "reciprocal_count_ratio": reciprocal_count_ratio,
        "clustering_undirected": clustering,
        "feedforward_paths": feedforward_paths,
        "bottleneck_ratio": bottleneck_ratio,
        "successor_out_degree_mean": successor_out_degree,
        "predecessor_in_degree_mean": predecessor_in_degree,
    }
    for name in FEATURE_ORDER:
        if not np.all(np.isfinite(features[name])):
            raise ArtisanalError(f"feature '{name}' contém valor não finito")
    return ids, features


def probe(train_matrix: np.ndarray, train_labels: list[str], val_matrix: np.ndarray, classes: list[str]) -> list[str]:
    mean = train_matrix.mean(axis=0)
    std = train_matrix.std(axis=0)
    std[std < 1e-6] = 1e-6
    train_scaled = (train_matrix - mean) / std
    val_scaled = (val_matrix - mean) / std
    centroids = {}
    for name in classes:
        rows = [train_scaled[index] for index, label in enumerate(train_labels) if label == name]
        if rows:
            centroids[name] = np.mean(rows, axis=0)
    predictions = []
    for row in val_scaled:
        distances = {name: float(np.linalg.norm(row - centroid)) for name, centroid in centroids.items()}
        predictions.append(min(distances, key=lambda name: (distances[name], name)))
    return predictions


def run(snapshot: Path, properties: Path, out_dir: Path, report_path: Path) -> dict:
    started = time.perf_counter()
    ids, features = extract_features(snapshot)
    labels, label_meta = bs.load_source_labels(properties)
    labels = {node: name for node, name in labels.items() if node in set(ids)}
    counts = Counter(labels.values())
    labels = {node: name for node, name in labels.items() if counts[name] >= bs.K_MIN}
    train, val = bs.split_deterministic(labels)
    order = {node: index for index, node in enumerate(ids)}
    train_nodes, val_nodes = list(train), list(val)
    classes = sorted(set(train.values()))
    results = {}
    for family, names in list(FAMILIES.items()) + [("all", FEATURE_ORDER)]:
        columns = [FEATURE_ORDER.index(name) for name in names]
        full = np.column_stack([features[name] for name in FEATURE_ORDER])
        train_matrix = full[[order[node] for node in train_nodes]][:, columns]
        val_matrix = full[[order[node] for node in val_nodes]][:, columns]
        predictions = probe(train_matrix, [train[node] for node in train_nodes], val_matrix, classes)
        ranked = {node: [predictions[index]] for index, node in enumerate(val_nodes)}
        evaluation = metrics.evaluate(ranked, val, k_values=(1, 5))
        results[family] = {
            "features": list(names),
            "macro_recall@1": evaluation["recall"]["@1"]["macro"],
            "micro_recall@1": evaluation["recall"]["@1"]["micro"],
        }
    out_dir.mkdir(parents=True, exist_ok=True)
    predictions_path = out_dir / "predictions-artesanal-all.json"
    full = np.column_stack([features[name] for name in FEATURE_ORDER])
    all_columns = list(range(len(FEATURE_ORDER)))
    predictions = probe(
        full[[order[node] for node in train_nodes]][:, all_columns],
        [train[node] for node in train_nodes],
        full[[order[node] for node in val_nodes]][:, all_columns],
        classes,
    )
    predictions_path.write_text(
        json.dumps({node: predictions[index] for index, node in enumerate(val_nodes)}, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report = {
        "schema": "b04-artisanal-features",
        "feature_version": FEATURE_VERSION,
        "families": {family: list(names) for family, names in FAMILIES.items()},
        "interrupted_features": list(INTERRUPTED_FEATURES),
        "label_meta": label_meta,
        "nodes_used": len(labels),
        "split": {"train": len(train), "val": len(val), "classes": len(classes)},
        "results": results,
        "baseline_degree_only_macro@1": None,
        "predictions": {"path": predictions_path.as_posix(), "sha256": bs.sha256_file(predictions_path)},
        "seconds": round(time.perf_counter() - started, 3),
        "peak_rss_mib": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1),
    }
    try:
        b03 = json.loads((ROOT / "artifacts" / "reports" / "B03-BASELINES-FONTE.json").read_text(encoding="utf-8"))
        report["baseline_degree_only_macro@1"] = b03["results"]["baselines"]["degree_only"]["recall"]["@1"]["macro"]
    except (FileNotFoundError, KeyError):
        pass
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--properties", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = run(args.snapshot, args.properties, args.out_dir, args.report)
    except (ArtisanalError, FileNotFoundError) as error:
        print(f"FALHA: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"results": report["results"], "baseline_degree_only": report["baseline_degree_only_macro@1"], "seconds": report["seconds"], "peak_rss_mib": report["peak_rss_mib"]}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
