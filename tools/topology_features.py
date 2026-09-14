#!/usr/bin/env python3
"""Features topology-only com fit/transform separado (H05).

Calcula apenas atributos derivados da topologia (graus, pesos, reciprocidade e
self-loops). Nenhum nome, tipo, região, coordenada ou ID entra na matriz: os
IDs ficam em array paralelo e nunca viram número, categoria ou índice. O
normalizador (z-score) é ajustado **somente na fonte** e aplicado ao alvo;
valores não finitos viram 0.0 por regra fixa e o clipping em ±8 é registrado.
"""

import argparse
import hashlib
import json
import math
import resource
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import graph_contract  # noqa: E402

FEATURE_NAMES = (
    "in_degree",
    "out_degree",
    "weighted_in",
    "weighted_out",
    "reciprocity",
    "self_loop_weight",
)
NONFINITE_VALUE = 0.0
CLIP_Z = 8.0
STATS_VERSION = "1.0"
FORBIDDEN_ATTRIBUTES = ("type", "cell_type", "region", "neuropil", "position", "x", "y", "z")


class FeatureError(RuntimeError):
    pass


def config_sha256() -> str:
    config = {"features": list(FEATURE_NAMES), "nonfinite": NONFINITE_VALUE, "clip_z": CLIP_Z}
    return hashlib.sha256(json.dumps(config, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def raw_features(graph: dict) -> tuple[list[str], list[list[float]]]:
    if graph.get("provenance", {}).get("created_at") is None:
        raise FeatureError("grafo sem proveniência")
    for node in graph["nodes"]:
        if set(node.get("attributes", {})) & set(FORBIDDEN_ATTRIBUTES):
            raise FeatureError("atributo proibido no trilha A")
    node_ids = sorted(node["id"] for node in graph["nodes"])
    position = {node_id: index for index, node_id in enumerate(node_ids)}
    in_degree = [0] * len(node_ids)
    out_degree = [0] * len(node_ids)
    weighted_in = [0.0] * len(node_ids)
    weighted_out = [0.0] * len(node_ids)
    self_loop_weight = [0.0] * len(node_ids)
    pair_weight: dict[tuple[int, int], float] = {}
    for edge in graph["edges"]:
        source, target = position[edge["source"]], position[edge["target"]]
        weight = float(edge.get("weight") or 0.0)
        if source == target:
            self_loop_weight[source] += weight
            continue
        out_degree[source] += 1
        in_degree[target] += 1
        weighted_out[source] += weight
        weighted_in[target] += weight
        pair_weight[(source, target)] = pair_weight.get((source, target), 0.0) + weight
    reciprocity = [0.0] * len(node_ids)
    for (source, target), weight in pair_weight.items():
        reverse = pair_weight.get((target, source), 0.0)
        reciprocity[source] += min(weight, reverse)
    matrix = []
    for index in range(len(node_ids)):
        reciprocal = reciprocity[index] / weighted_out[index] if weighted_out[index] > 0 else 0.0
        matrix.append(
            [
                float(in_degree[index]),
                float(out_degree[index]),
                weighted_in[index],
                weighted_out[index],
                min(1.0, reciprocal),
                self_loop_weight[index],
            ]
        )
    return node_ids, matrix


def fit(graph: dict) -> dict:
    _, matrix = raw_features(graph)
    stats = {"stats_version": STATS_VERSION, "features": {}, "config_sha256": config_sha256()}
    for column, name in enumerate(FEATURE_NAMES):
        values = [row[column] for row in matrix]
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        stats["features"][name] = {"mean": mean, "std": max(math.sqrt(variance), 1e-6)}
    return stats


def transform(graph: dict, stats: dict) -> tuple[list[str], list[list[float]], dict]:
    if stats.get("stats_version") != STATS_VERSION:
        raise FeatureError("stats incompatíveis")
    node_ids, matrix = raw_features(graph)
    transformed = []
    replaced = 0
    clipped = 0
    for row in matrix:
        values = []
        for column, name in enumerate(FEATURE_NAMES):
            mean = stats["features"][name]["mean"]
            std = stats["features"][name]["std"]
            value = (row[column] - mean) / std
            if not math.isfinite(value):
                value = NONFINITE_VALUE
                replaced += 1
            if value > CLIP_Z or value < -CLIP_Z:
                value = max(-CLIP_Z, min(CLIP_Z, value))
                clipped += 1
            values.append(value)
        transformed.append(values)
    column_means = [
        sum(row[column] for row in transformed) / len(transformed) for column in range(len(FEATURE_NAMES))
    ]
    column_stds = [
        math.sqrt(
            sum((row[column] - column_means[column]) ** 2 for row in transformed) / len(transformed)
        )
        for column in range(len(FEATURE_NAMES))
    ]
    report = {
        "nodes": len(node_ids),
        "features": len(FEATURE_NAMES),
        "nonfinite_replaced": replaced,
        "clipped": clipped,
        "mean": column_means,
        "std": column_stds,
    }
    return node_ids, transformed, report


def _save_npz(path: Path, node_ids: list[str], matrix: list[list[float]]) -> None:
    import numpy as np

    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        ids=np.array(node_ids),
        features=np.asarray(matrix, dtype="float32"),
        feature_names=np.array(FEATURE_NAMES),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    fit_parser = sub.add_parser("fit")
    fit_parser.add_argument("--graph", type=Path, required=True)
    fit_parser.add_argument("--stats", type=Path, required=True)
    fit_parser.add_argument("--npz", type=Path, default=None)
    fit_parser.add_argument("--metrics", type=Path, default=None)
    transform_parser = sub.add_parser("transform")
    transform_parser.add_argument("--graph", type=Path, required=True)
    transform_parser.add_argument("--stats", type=Path, required=True)
    transform_parser.add_argument("--npz", type=Path, required=True)
    transform_parser.add_argument("--metrics", type=Path, default=None)
    args = parser.parse_args()
    started = time.perf_counter()
    try:
        graph = json.loads(args.graph.read_text(encoding="utf-8"))
        failures = graph_contract.validate_graph(graph, args.graph.name)
        if failures:
            raise FeatureError("; ".join(failures))
        if args.command == "fit":
            stats = fit(graph)
            args.stats.parent.mkdir(parents=True, exist_ok=True)
            args.stats.write_text(json.dumps(stats, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            metrics = {"command": "fit", "graph": args.stats.name, "feature_names": list(FEATURE_NAMES)}
            if args.npz is not None:
                node_ids, matrix = raw_features(graph)
                _save_npz(args.npz, node_ids, matrix)
                metrics["nodes"] = len(node_ids)
        else:
            stats = json.loads(args.stats.read_text(encoding="utf-8"))
            node_ids, matrix, transform_report = transform(graph, stats)
            _save_npz(args.npz, node_ids, matrix)
            metrics = {"command": "transform", **transform_report, "stats_config_sha256": stats.get("config_sha256")}
        metrics["seconds"] = round(time.perf_counter() - started, 3)
        metrics["peak_rss_mib"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
        if args.metrics is not None:
            args.metrics.parent.mkdir(parents=True, exist_ok=True)
            args.metrics.write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(metrics, ensure_ascii=False, sort_keys=True))
        return 0
    except (FeatureError, json.JSONDecodeError) as error:
        print(f"FALHA: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
