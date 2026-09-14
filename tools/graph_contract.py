#!/usr/bin/env python3
"""Contrato canônico do grafo: validação e round-trip (H01).

Sem dependências externas; implementa as mesmas regras de
`schemas/graph.schema.json` e garante que serializar → recarregar preserva
nodes, edges, multiedges, peso zero, self-loops, missingness e proveniência.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schemas" / "graph.schema.json"
FIXTURE = ROOT / "tests" / "fixtures" / "graph-fixture.json"

TOP_REQUIRED = ("schema_version", "provenance", "graph", "nodes", "edges")
PROVENANCE_REQUIRED = ("dataset", "release", "license", "source_files", "adapter", "created_at")
GRAPH_REQUIRED = ("directed", "weighted", "allow_self_loops", "aggregation", "threshold")
NODE_REQUIRED = ("id", "attributes", "missing")
EDGE_REQUIRED = ("source", "target", "weight", "attributes", "missing")
NODE_RE = re.compile(r"^n[0-9a-f]{16}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
AGGREGATIONS = ("none", "sum")
THRESHOLD_RULES = ("keep", "drop_below")


def _unknown(payload: dict, allowed: tuple, label: str, failures: list[str]) -> None:
    for field in payload:
        if field not in allowed:
            failures.append(f"{label}: campo inesperado '{field}'")


def validate_graph(payload: dict, label: str = "grafo") -> list[str]:
    failures: list[str] = []
    if not isinstance(payload, dict):
        return [f"{label}: raiz deve ser objeto JSON"]
    for field in TOP_REQUIRED:
        if field not in payload:
            failures.append(f"{label}: campo obrigatório ausente '{field}'")
    _unknown(payload, TOP_REQUIRED, label, failures)
    if payload.get("schema_version") != "1.0":
        failures.append(f"{label}: schema_version deve ser '1.0'")

    provenance = payload.get("provenance")
    if not isinstance(provenance, dict):
        failures.append(f"{label}: 'provenance' deve ser objeto")
    else:
        for field in PROVENANCE_REQUIRED:
            if field not in provenance:
                failures.append(f"{label}.provenance: campo obrigatório ausente '{field}'")
        _unknown(provenance, PROVENANCE_REQUIRED, f"{label}.provenance", failures)
        for field in ("dataset", "release", "license"):
            if not isinstance(provenance.get(field), str) or not provenance.get(field, "").strip():
                failures.append(f"{label}.provenance: '{field}' deve ser string não vazia")
        files = provenance.get("source_files")
        if not isinstance(files, list) or not files:
            failures.append(f"{label}.provenance: 'source_files' deve ser lista não vazia")
        else:
            for index, item in enumerate(files):
                if not isinstance(item, dict) or not SHA256_RE.match(str(item.get("sha256", ""))):
                    failures.append(f"{label}.provenance.source_files[{index}]: sha256 inválido")
        adapter = provenance.get("adapter")
        if not isinstance(adapter, dict) or not SHA256_RE.match(str(adapter.get("config_sha256", ""))):
            failures.append(f"{label}.provenance.adapter: config_sha256 inválido")
        if not isinstance(provenance.get("created_at"), str) or not DATE_RE.match(provenance["created_at"]):
            failures.append(f"{label}.provenance: created_at deve ser AAAA-MM-DD")

    graph = payload.get("graph")
    allow_self_loops = False
    if not isinstance(graph, dict):
        failures.append(f"{label}: 'graph' deve ser objeto")
    else:
        for field in GRAPH_REQUIRED:
            if field not in graph:
                failures.append(f"{label}.graph: campo obrigatório ausente '{field}'")
        _unknown(graph, GRAPH_REQUIRED + ("weight_units",), f"{label}.graph", failures)
        if not isinstance(graph.get("directed"), bool):
            failures.append(f"{label}.graph: 'directed' deve ser booleano")
        if not isinstance(graph.get("weighted"), bool):
            failures.append(f"{label}.graph: 'weighted' deve ser booleano")
        if not isinstance(graph.get("allow_self_loops"), bool):
            failures.append(f"{label}.graph: 'allow_self_loops' deve ser booleano")
        else:
            allow_self_loops = graph["allow_self_loops"]
        if graph.get("aggregation") not in AGGREGATIONS:
            failures.append(f"{label}.graph: 'aggregation' deve ser 'none' ou 'sum'")
        threshold = graph.get("threshold")
        if not isinstance(threshold, dict) or threshold.get("rule") not in THRESHOLD_RULES:
            failures.append(f"{label}.graph: 'threshold' deve ter rule 'keep' ou 'drop_below'")
        elif threshold.get("weight_min") is not None and (
            not isinstance(threshold["weight_min"], int) or threshold["weight_min"] < 0
        ):
            failures.append(f"{label}.graph: 'weight_min' deve ser inteiro ≥ 0 ou null")

    nodes = payload.get("nodes")
    edge_list = payload.get("edges")
    node_ids: set[str] = set()
    if not isinstance(nodes, list) or not nodes:
        failures.append(f"{label}: 'nodes' deve ser lista não vazia")
    else:
        for index, node in enumerate(nodes):
            item = f"{label}.nodes[{index}]"
            if not isinstance(node, dict):
                failures.append(f"{item}: node deve ser objeto")
                continue
            for field in NODE_REQUIRED:
                if field not in node:
                    failures.append(f"{item}: campo obrigatório ausente '{field}'")
            _unknown(node, NODE_REQUIRED, item, failures)
            node_id = node.get("id")
            if not isinstance(node_id, str) or not NODE_RE.match(node_id):
                failures.append(f"{item}: id opaco deve casar n<16 hex>")
            elif node_id in node_ids:
                failures.append(f"{item}: id duplicado '{node_id}'")
            else:
                node_ids.add(node_id)
            attributes = node.get("attributes")
            missing = node.get("missing")
            if not isinstance(attributes, dict):
                failures.append(f"{item}: 'attributes' deve ser objeto")
            if not isinstance(missing, list) or not all(isinstance(key, str) for key in missing):
                failures.append(f"{item}: 'missing' deve ser lista de strings")
            elif isinstance(attributes, dict):
                for key, value in attributes.items():
                    if value is None and key not in missing:
                        failures.append(f"{item}: null exige chave em 'missing' ('{key}')")
                    if key in missing:
                        failures.append(f"{item}: '{key}' está em attributes e em missing")
    if not isinstance(edge_list, list):
        failures.append(f"{label}: 'edges' deve ser lista")
        return failures
    for index, edge in enumerate(edge_list):
        item = f"{label}.edges[{index}]"
        if not isinstance(edge, dict):
            failures.append(f"{item}: aresta deve ser objeto")
            continue
        for field in EDGE_REQUIRED:
            if field not in edge:
                failures.append(f"{item}: campo obrigatório ausente '{field}'")
        _unknown(edge, EDGE_REQUIRED, item, failures)
        for endpoint in ("source", "target"):
            value = edge.get(endpoint)
            if not isinstance(value, str) or not NODE_RE.match(value):
                failures.append(f"{item}: '{endpoint}' deve casar n<16 hex>")
            elif value not in node_ids:
                failures.append(f"{item}: '{endpoint}' referencia node inexistente")
        source, target = edge.get("source"), edge.get("target")
        if source == target and not allow_self_loops:
            failures.append(f"{item}: self-loop não permitido por 'allow_self_loops'")
        weight = edge.get("weight")
        weighted = graph.get("weighted") if isinstance(graph, dict) else None
        if weight is not None and (
            not isinstance(weight, int)
            or isinstance(weight, bool)
            or weight < 0
        ):
            failures.append(f"{item}: 'weight' deve ser inteiro ≥ 0 ou null")
        if weighted is True and weight is None:
            failures.append(f"{item}: grafo ponderado exige 'weight' inteiro")
        if weighted is False and weight is not None:
            failures.append(f"{item}: grafo não ponderado exige 'weight' null")
        attributes = edge.get("attributes")
        missing = edge.get("missing")
        if not isinstance(attributes, dict):
            failures.append(f"{item}: 'attributes' deve ser objeto")
        if not isinstance(missing, list) or not all(isinstance(key, str) for key in missing):
            failures.append(f"{item}: 'missing' deve ser lista de strings")
        elif isinstance(attributes, dict):
            for key in missing:
                if key in attributes:
                    failures.append(f"{item}: '{key}' está em attributes e em missing")
    return failures


def canonical_json(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def roundtrip(path: Path) -> tuple[list[str], bool]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    failures = validate_graph(payload, path.name)
    if failures:
        return failures, False
    first = canonical_json(payload)
    reloaded = json.loads(first)
    second = canonical_json(reloaded)
    return [], first == second


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "roundtrip"))
    parser.add_argument("path", nargs="?", type=Path, default=FIXTURE)
    args = parser.parse_args()
    if args.command == "validate":
        failures = validate_graph(json.loads(args.path.read_text(encoding="utf-8")), args.path.name)
        if failures:
            for failure in failures:
                print(f"FALHA: {failure}")
            return 1
        print(f"OK: grafo canônico válido ({args.path})")
        return 0
    failures, ok = roundtrip(args.path)
    if failures:
        for failure in failures:
            print(f"FALHA: {failure}")
        return 1
    if not ok:
        print("FALHA: round-trip não preserva os dados")
        return 1
    print(f"OK: round-trip preserva nodes, edges, multiedges, missingness e proveniência ({args.path})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
