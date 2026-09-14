#!/usr/bin/env python3
"""Adapter público do alvo MCNS → grafo canônico (H03).

Lê **somente** a tabela pública de pesos de conectoma (`body_pre`, `body_post`,
`weight`) do MCNS `male-cns:v1.0`, sem abrir anotações, tipos ou crosswalk. O
schema de entrada é exigido com exatamente essas três colunas; qualquer coluna
extra falha. Produz um grafo canônico H01 de amostra (determinístico, primeiras
N linhas), uma amostra dourada sem labels e métricas de arquivo completo por
coluna (leitura em memória mapeada).
"""

import argparse
import hashlib
import json
import resource
import sys
import time
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.feather as feather

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import graph_contract  # noqa: E402

ADAPTER_NAME = "mcns-adapter"
ADAPTER_VERSION = "1.0"
DATASET = "MCNS"
RELEASE = "male-cns:v1.0"
LICENSE = "CC-BY-4.0"
ALLOWED_COLUMNS = ("body_pre", "body_post", "weight")
FORBIDDEN_NODE_ATTRIBUTES = ("type", "cell_type", "region", "neuropil", "position", "x", "y", "z")
CONFIG = {
    "aggregation": "sum",
    "direction": "pre_to_post",
    "weight_units": "synapse_count",
    "threshold_min": 0,
    "sample_rows": 100000,
}


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


def opaque_id(body: int) -> str:
    digest = hashlib.sha256(f"{DATASET}|{RELEASE}|{int(body)}".encode()).hexdigest()
    return "n" + digest[:16]


def read_weights(path: Path) -> pa.Table:
    table = feather.read_table(path, memory_map=True)
    if tuple(table.column_names) != ALLOWED_COLUMNS:
        raise AdapterError(
            f"colunas inesperadas: {tuple(table.column_names)}; esperado {ALLOWED_COLUMNS}"
        )
    return table


def full_file_metrics(table: pa.Table, path: Path) -> dict:
    weight = table["weight"]
    negative = int(pc.sum(pc.cast(pc.less(weight, 0), pa.int64())).as_py())
    if negative:
        raise AdapterError(f"pesos negativos encontrados: {negative}")
    self_loops = int(pc.sum(pc.cast(pc.equal(table["body_pre"], table["body_post"]), pa.int64())).as_py())
    return {
        "rows_full": table.num_rows,
        "weight_sum_full": int(pc.sum(weight).as_py()),
        "weight_min_full": int(pc.min(weight).as_py()),
        "self_loops_full": self_loops,
        "input_sha256": file_sha256(path),
        "input_bytes": path.stat().st_size,
    }


def sample_graph(table: pa.Table, sample_rows: int, source: dict | None = None) -> tuple[dict, dict]:
    sample = table.slice(0, sample_rows)
    index: dict[int, int] = {}
    edges: dict[tuple[int, int], int] = {}
    self_loops = 0
    weight_sum_in = 0
    pre_list = sample["body_pre"].to_pylist()
    post_list = sample["body_post"].to_pylist()
    weight_list = sample["weight"].to_pylist()
    for pre, post, weight in zip(pre_list, post_list, weight_list):
        value = int(weight)
        weight_sum_in += value
        if pre == post:
            self_loops += 1
        key = (index.setdefault(int(pre), len(index)), index.setdefault(int(post), len(index)))
        edges[key] = edges.get(key, 0) + value
    order = {position: body for body, position in index.items()}
    node_ids = {position: opaque_id(order[position]) for position in order}
    degree_in: dict[int, int] = {}
    degree_out: dict[int, int] = {}
    for (pre, post), weight in edges.items():
        degree_out[pre] = degree_out.get(pre, 0) + weight
        degree_in[post] = degree_in.get(post, 0) + weight
    nodes = [
        {
            "id": node_ids[position],
            "attributes": {
                "degree_in": degree_in.get(position, 0),
                "degree_out": degree_out.get(position, 0),
            },
            "missing": [],
        }
        for position in range(len(order))
    ]
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
    graph = {
        "schema_version": "1.0",
        "provenance": {
            "dataset": DATASET,
            "release": RELEASE,
            "license": LICENSE,
            "source_files": [source] if source else [],
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
            "allow_self_loops": self_loops > 0,
            "aggregation": CONFIG["aggregation"],
            "threshold": {"weight_min": CONFIG["threshold_min"], "rule": "keep"},
        },
        "nodes": nodes,
        "edges": edge_list,
    }
    metrics = {
        "sample_rows": sample.num_rows,
        "sample_nodes": len(nodes),
        "sample_edges_after_aggregation": len(edge_list),
        "sample_multiedge_groups": sample.num_rows - len(edges),
        "sample_self_loops": self_loops,
        "sample_weight_sum_in": weight_sum_in,
        "sample_weight_sum_out": sum(edges.values()),
        "sample_weight_conserved": weight_sum_in == sum(edges.values()),
    }
    return graph, metrics


def golden_sample(graph: dict, max_nodes: int, max_edges: int) -> dict:
    nodes = graph["nodes"][:max_nodes]
    keep = {node["id"] for node in nodes}
    edges = [edge for edge in graph["edges"] if edge["source"] in keep and edge["target"] in keep][:max_edges]
    sample = json.loads(json.dumps(graph))
    sample["nodes"] = nodes
    sample["edges"] = edges
    sample["provenance"]["adapter"] = {**graph["provenance"]["adapter"], "name": ADAPTER_NAME + "-golden"}
    return sample


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--golden", type=Path, default=None)
    parser.add_argument("--metrics", type=Path, default=None)
    parser.add_argument("--sample-rows", type=int, default=CONFIG["sample_rows"])
    parser.add_argument("--max-nodes", type=int, default=40)
    parser.add_argument("--max-edges", type=int, default=60)
    args = parser.parse_args()
    started = time.perf_counter()
    try:
        table = read_weights(args.weights)
        file_metrics = full_file_metrics(table, args.weights)
        graph, sample_metrics = sample_graph(
            table, args.sample_rows,
            source={"path": args.weights.as_posix(), "sha256": file_metrics["input_sha256"]},
        )
    except AdapterError as error:
        print(f"FALHA: {error}", file=sys.stderr)
        return 1
    failures = graph_contract.validate_graph(graph, args.weights.name)
    if failures:
        for failure in failures:
            print(f"FALHA: {failure}")
        return 1
    if any(key in node["attributes"] for node in graph["nodes"] for key in FORBIDDEN_NODE_ATTRIBUTES):
        print("FALHA: atributo proibido no trilho A", file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(graph, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    metrics = {
        **file_metrics,
        **sample_metrics,
        "columns": list(ALLOWED_COLUMNS),
        "config_sha256": config_sha256(),
        "sample_sha256": file_sha256(args.out),
        "seconds": round(time.perf_counter() - started, 3),
    }
    if args.golden is not None:
        sample = golden_sample(graph, args.max_nodes, args.max_edges)
        sample_failures = graph_contract.validate_graph(sample, args.golden.name)
        if sample_failures:
            for failure in sample_failures:
                print(f"FALHA: {failure}")
            return 1
        args.golden.parent.mkdir(parents=True, exist_ok=True)
        args.golden.write_text(json.dumps(sample, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        metrics["golden_nodes"] = len(sample["nodes"])
        metrics["golden_edges"] = len(sample["edges"])
        metrics["golden_sha256"] = file_sha256(args.golden)
    metrics["peak_rss_mib"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    if args.metrics is not None:
        args.metrics.parent.mkdir(parents=True, exist_ok=True)
        args.metrics.write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
