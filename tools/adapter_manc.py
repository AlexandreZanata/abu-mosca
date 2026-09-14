#!/usr/bin/env python3
"""Adapter da fonte MANC → grafo canônico (H02).

Converte apenas a tabela de adjacências traçadas (`bodyId_pre`, `bodyId_post`,
`weight`) para o contrato H01. Nunca lê nem inclui tipo, região, posição ou
qualquer atributo do trilho A: os nodes carregam apenas graus derivados da
topologia. Multiedges são agregadas por soma com conservação de peso registrada.
"""

import argparse
import csv
import hashlib
import json
import resource
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import graph_contract  # noqa: E402

ADAPTER_NAME = "manc-adapter"
ADAPTER_VERSION = "1.0"
DATASET = "MANC"
RELEASE = "manc:v1.2.1"
LICENSE = "CC-BY-4.0"
EXPECTED_HEADER = ("bodyId_pre", "bodyId_post", "weight")
CONFIG = {
    "aggregation": "sum",
    "direction": "pre_to_post",
    "weight_units": "synapse_count",
    "threshold_min": 0,
}
FORBIDDEN_NODE_ATTRIBUTES = ("type", "cell_type", "region", "neuropil", "position", "x", "y", "z")


class AdapterError(RuntimeError):
    pass


def config_sha256() -> str:
    return hashlib.sha256(json.dumps(CONFIG, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def file_sha256(path: Path, chunk: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(chunk):
            digest.update(block)
    return digest.hexdigest()


def opaque_id(dataset: str, release: str, body: str) -> str:
    digest = hashlib.sha256(f"{dataset}|{release}|{body}".encode()).hexdigest()
    return "n" + digest[:16]


def read_connections(path: Path) -> dict:
    index: dict[str, int] = {}
    edges: dict[tuple[int, int], int] = {}
    rows = 0
    self_loops = 0
    weight_sum_in = 0
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header = tuple(next(reader))
        if header != EXPECTED_HEADER:
            raise AdapterError(f"cabeçalho inesperado: {header!r}")
        for row in reader:
            if len(row) != 3:
                raise AdapterError(f"linha com {len(row)} colunas na entrada {rows + 2}")
            pre, post, weight = row[0].strip(), row[1].strip(), row[2].strip()
            value = int(weight)
            if value < 0:
                raise AdapterError(f"peso negativo '{weight}' na linha {rows + 2}")
            rows += 1
            weight_sum_in += value
            if pre == post:
                self_loops += 1
            key = (index.setdefault(pre, len(index)), index.setdefault(post, len(index)))
            edges[key] = edges.get(key, 0) + value
    weight_sum_out = sum(edges.values())
    return {
        "index": index,
        "edges": edges,
        "rows": rows,
        "self_loops": self_loops,
        "weight_sum_in": weight_sum_in,
        "weight_sum_out": weight_sum_out,
        "multiedge_groups": rows - len(edges),
    }


def build_graph(path: Path) -> tuple[dict, dict]:
    started = time.perf_counter()
    data = read_connections(path)
    index, edges = data["index"], data["edges"]
    order = {position: body for body, position in index.items()}
    node_ids = {position: opaque_id(DATASET, RELEASE, order[position]) for position in order}
    if len(set(node_ids.values())) != len(node_ids):
        raise AdapterError("colisão de IDs opacos")
    degree_in: dict[int, int] = {}
    degree_out: dict[int, int] = {}
    for (pre, post), weight in edges.items():
        degree_out[pre] = degree_out.get(pre, 0) + weight
        degree_in[post] = degree_in.get(post, 0) + weight
    nodes = []
    for position in range(len(order)):
        nodes.append(
            {
                "id": node_ids[position],
                "attributes": {
                    "degree_in": degree_in.get(position, 0),
                    "degree_out": degree_out.get(position, 0),
                },
                "missing": [],
            }
        )
    edge_list = [
        {
            "source": node_ids[pre],
            "target": node_ids[post],
            "weight": weight,
            "attributes": {},
            "missing": [],
        }
        for (pre, post), weight in sorted(edges.items())
    ]
    digest = file_sha256(path)
    graph = {
        "schema_version": "1.0",
        "provenance": {
            "dataset": DATASET,
            "release": RELEASE,
            "license": LICENSE,
            "source_files": [{"path": path.as_posix(), "sha256": digest}],
            "adapter": {
                "name": ADAPTER_NAME,
                "version": ADAPTER_VERSION,
                "config_sha256": config_sha256(),
            },
            "created_at": time.strftime("%Y-%m-%d", time.gmtime()),
        },
        "graph": {
            "directed": True,
            "weighted": True,
            "weight_units": "synapse_count",
            "allow_self_loops": data["self_loops"] > 0,
            "aggregation": CONFIG["aggregation"],
            "threshold": {"weight_min": CONFIG["threshold_min"], "rule": "keep"},
        },
        "nodes": nodes,
        "edges": edge_list,
    }
    metrics = {
        "rows_in": data["rows"],
        "nodes": len(nodes),
        "edges_after_aggregation": len(edge_list),
        "multiedge_groups": data["multiedge_groups"],
        "self_loops": data["self_loops"],
        "weight_sum_in": data["weight_sum_in"],
        "weight_sum_out": data["weight_sum_out"],
        "weight_conserved": data["weight_sum_in"] == data["weight_sum_out"],
        "input_sha256": digest,
        "config_sha256": config_sha256(),
        "seconds": round(time.perf_counter() - started, 3),
        "peak_rss_mib": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1),
    }
    return graph, metrics


def golden_sample(graph: dict, max_nodes: int, max_edges: int) -> dict:
    nodes = graph["nodes"][:max_nodes]
    keep = {node["id"] for node in nodes}
    edges = [
        edge for edge in graph["edges"]
        if edge["source"] in keep and edge["target"] in keep
    ][:max_edges]
    sample = json.loads(json.dumps(graph))
    sample["nodes"] = nodes
    sample["edges"] = edges
    sample["provenance"]["adapter"] = {
        **graph["provenance"]["adapter"],
        "name": ADAPTER_NAME + "-golden",
    }
    return sample


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--connections", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--golden", type=Path, default=None)
    parser.add_argument("--max-nodes", type=int, default=40)
    parser.add_argument("--max-edges", type=int, default=60)
    parser.add_argument("--metrics", type=Path, default=None)
    args = parser.parse_args()
    try:
        graph, metrics = build_graph(args.connections)
    except AdapterError as error:
        print(f"FALHA: {error}", file=sys.stderr)
        return 1
    failures = graph_contract.validate_graph(graph, args.connections.name)
    if failures:
        for failure in failures:
            print(f"FALHA: {failure}")
        return 1
    if any(
        key in node["attributes"]
        for node in graph["nodes"]
        for key in FORBIDDEN_NODE_ATTRIBUTES
    ):
        print("FALHA: atributo proibido no trilho A", file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(graph, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    metrics["output_sha256"] = file_sha256(args.out)
    if args.golden is not None:
        sample = golden_sample(graph, args.max_nodes, args.max_edges)
        sample_failures = graph_contract.validate_graph(sample, args.golden.name)
        if sample_failures:
            for failure in sample_failures:
                print(f"FALHA: {failure}")
            return 1
        args.golden.parent.mkdir(parents=True, exist_ok=True)
        args.golden.write_text(
            json.dumps(sample, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        metrics["golden_nodes"] = len(sample["nodes"])
        metrics["golden_edges"] = len(sample["edges"])
        metrics["golden_sha256"] = file_sha256(args.golden)
    metrics["peak_rss_mib"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    if args.metrics is not None:
        args.metrics.parent.mkdir(parents=True, exist_ok=True)
        args.metrics.write_text(
            json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(json.dumps(metrics, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
