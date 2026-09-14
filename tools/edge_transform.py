#!/usr/bin/env python3
"""Transformador de arestas, configuração primária e variantes (H06).

Aplica uma configuração de semântica de arestas ao grafo canônico (H01):
direção, peso (bruto, binário, log1p), threshold, reciprocidade e self-loops.
A configuração primária vem do pré-registro assinado; todas as variantes são
pré-registradas em `configs/edge-variants.json` e aplicadas igualmente à fonte e
ao alvo, sem usar estatística do alvo. Regras explícitas para peso zero,
self-loops e componentes isolados são registradas nas métricas.
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

TRANSFORMER_NAME = "edge-transform"
TRANSFORMER_VERSION = "1.0"
DIRECTIONS = ("directed", "symmetrized")
WEIGHTS = ("raw", "binary", "log1p")
THRESHOLD_RULES = ("keep", "drop_below")
SELF_LOOPS = ("keep", "drop")
REQUIRED_FIELDS = ("variant", "direction", "weight", "threshold", "self_loops")
ALLOWED_FIELDS = REQUIRED_FIELDS


class TransformError(RuntimeError):
    pass


def config_sha256(config: dict) -> str:
    return hashlib.sha256(json.dumps(config, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate_config(config: dict, label: str = "config") -> list[str]:
    failures = []
    if not isinstance(config, dict):
        return [f"{label}: deve ser objeto JSON"]
    for field in REQUIRED_FIELDS:
        if field not in config:
            failures.append(f"{label}: campo obrigatório ausente '{field}'")
    for field in config:
        if field not in ALLOWED_FIELDS:
            failures.append(f"{label}: campo inesperado '{field}'")
    if not isinstance(config.get("variant"), str) or not config.get("variant"):
        failures.append(f"{label}: 'variant' deve ser string não vazia")
    if config.get("direction") not in DIRECTIONS:
        failures.append(f"{label}: 'direction' deve ser {DIRECTIONS}")
    if config.get("weight") not in WEIGHTS:
        failures.append(f"{label}: 'weight' deve ser {WEIGHTS}")
    if config.get("self_loops") not in SELF_LOOPS:
        failures.append(f"{label}: 'self_loops' deve ser {SELF_LOOPS}")
    threshold = config.get("threshold")
    if not isinstance(threshold, dict):
        failures.append(f"{label}: 'threshold' deve ser objeto")
    else:
        if threshold.get("rule") not in THRESHOLD_RULES:
            failures.append(f"{label}: 'threshold.rule' deve ser {THRESHOLD_RULES}")
        if not isinstance(threshold.get("weight_min"), int) or threshold.get("weight_min", -1) < 0:
            failures.append(f"{label}: 'threshold.weight_min' deve ser inteiro ≥ 0")
    return failures


def apply(graph: dict, config: dict) -> tuple[dict, dict]:
    failures = validate_config(config)
    if failures:
        raise TransformError("; ".join(failures))
    nodes = [node["id"] for node in graph["nodes"]]
    node_set = set(nodes)
    edges = []
    weight_in = 0
    weight_dropped = 0
    loops_kept = 0
    loops_dropped = 0
    zero_weight_edges = 0
    isolated_nodes = 0
    touched: set[str] = set()
    for edge in graph["edges"]:
        source, target = edge["source"], edge["target"]
        weight = int(edge.get("weight") or 0)
        if weight == 0:
            zero_weight_edges += 1
        if source == target:
            if config["self_loops"] == "drop":
                loops_dropped += 1
                weight_dropped += weight
                continue
            loops_kept += 1
        weight_in += weight
        if weight < config["threshold"]["weight_min"]:
            weight_dropped += weight
            continue
        touched.add(source)
        touched.add(target)
        edges.append(
            {
                "source": source,
                "target": target,
                "weight": weight,
                "attributes": dict(edge.get("attributes") or {}),
                "missing": list(edge.get("missing") or []),
            }
        )

    if config["direction"] == "symmetrized":
        pair: dict[tuple[str, str], int] = {}
        order: list[tuple[str, str]] = []
        for edge in edges:
            key = tuple(sorted((edge["source"], edge["target"])))
            if key not in pair:
                pair[key] = 0
                order.append(key)
            pair[key] += edge["weight"]
        edges = [
            {"source": key[0], "target": key[1], "weight": pair[key], "attributes": {}, "missing": []}
            for key in order
        ]

    weight_out = 0
    for edge in edges:
        weight = edge["weight"]
        if config["weight"] == "binary":
            weight = 1 if weight > 0 else 0
        elif config["weight"] == "log1p":
            weight = math.log1p(weight)
        weight_out += weight
        edge["weight"] = int(weight) if float(weight).is_integer() else round(float(weight), 9)
    isolated_nodes = sum(1 for node_id in nodes if node_id not in touched)
    out = json.loads(json.dumps(graph))
    out["edges"] = edges
    if config["direction"] == "symmetrized" and out["graph"]["weight_units"] == "synapse_count":
        out["graph"] = {**out["graph"], "directed": False}
    out["provenance"]["adapter"] = {
        "name": f"{graph['provenance']['adapter']['name']}+{config['variant']}",
        "version": TRANSFORMER_VERSION,
        "config_sha256": config_sha256(config),
    }
    metrics = {
        "variant": config["variant"],
        "edges_in": len(graph["edges"]),
        "edges_out": len(edges),
        "weight_in": weight_in,
        "weight_out": weight_out,
        "weight_dropped": weight_dropped,
        "self_loops_kept": loops_kept,
        "self_loops_dropped": loops_dropped,
        "zero_weight_edges": zero_weight_edges,
        "isolated_nodes": isolated_nodes,
        "config_sha256": config_sha256(config),
    }
    if config["weight"] == "raw" and config["direction"] == "directed" and config["self_loops"] == "keep":
        if weight_in - weight_dropped != weight_out:
            raise TransformError("conservação de peso violada no pipeline primário")
    return out, metrics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--metrics", type=Path, default=None)
    args = parser.parse_args()
    started = time.perf_counter()
    try:
        graph = json.loads(args.graph.read_text(encoding="utf-8"))
        failures = graph_contract.validate_graph(graph, args.graph.name)
        if failures:
            raise TransformError("; ".join(failures))
        config = json.loads(args.config.read_text(encoding="utf-8"))
        out, metrics = apply(graph, config)
        out_failures = graph_contract.validate_graph(out, args.out.name)
        if out_failures:
            raise TransformError("; ".join(out_failures))
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        metrics["seconds"] = round(time.perf_counter() - started, 3)
        metrics["peak_rss_mib"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
        if args.metrics is not None:
            args.metrics.parent.mkdir(parents=True, exist_ok=True)
            args.metrics.write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(metrics, ensure_ascii=False, sort_keys=True))
        return 0
    except (TransformError, json.JSONDecodeError) as error:
        print(f"FALHA: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
