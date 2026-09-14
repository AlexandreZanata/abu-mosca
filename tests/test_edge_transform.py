import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import edge_transform as et  # noqa: E402
import graph_contract as gc  # noqa: E402
import opaque_ids  # noqa: E402

PRIMARY = json.loads((ROOT / "configs" / "edge-primary.json").read_text(encoding="utf-8"))
VARIANTS = json.loads((ROOT / "configs" / "edge-variants.json").read_text(encoding="utf-8"))


def nid(label: str) -> str:
    return opaque_ids.opaque_node_id("FIXTURE", "v1", label)


def graph(edges):
    labels = sorted({value for edge in edges for value in edge[:2]} | {"e"})
    return {
        "schema_version": "1.0",
        "provenance": {
            "dataset": "FIXTURE",
            "release": "v1",
            "license": "CC0-1.0",
            "source_files": [{"path": "x.csv", "sha256": "0" * 64}],
            "adapter": {"name": "adapter-teste", "version": "1.0", "config_sha256": "1" * 64},
            "created_at": "2026-09-14",
        },
        "graph": {
            "directed": True,
            "weighted": True,
            "weight_units": "synapse_count",
            "allow_self_loops": True,
            "aggregation": "sum",
            "threshold": {"weight_min": 0, "rule": "keep"},
        },
        "nodes": [{"id": nid(label), "attributes": {}, "missing": []} for label in labels],
        "edges": [
            {"source": nid(pre), "target": nid(post), "weight": weight, "attributes": {}, "missing": []}
            for pre, post, weight in edges
        ],
    }


EDGES = [("a", "b", 5), ("b", "a", 2), ("a", "c", 0), ("c", "c", 3), ("c", "d", 4)]


def test_primaria_conserva_peso_e_preserva_zero_self_loop_isolado():
    out, metrics = et.apply(graph(EDGES), PRIMARY)
    assert gc.validate_graph(out) == []
    assert metrics["edges_out"] == 5
    assert metrics["weight_in"] == metrics["weight_out"] == 14
    assert metrics["zero_weight_edges"] == 1
    assert metrics["self_loops_kept"] == 1
    assert metrics["isolated_nodes"] == 1
    assert nid("e") in {node["id"] for node in out["nodes"]}


@pytest.mark.parametrize("variant", [item["variant"] for item in VARIANTS["variants"]])
def test_variantes_validam_e_nao_perdem_nodes(variant):
    config = next(item for item in VARIANTS["variants"] if item["variant"] == variant)
    out, metrics = et.apply(graph(EDGES), config)
    assert gc.validate_graph(out) == []
    assert {node["id"] for node in out["nodes"]} == {node["id"] for node in graph(EDGES)["nodes"]}
    assert metrics["edges_out"] <= metrics["edges_in"]


def test_binaria_e_log1p():
    binary, binary_metrics = et.apply(graph(EDGES), {**PRIMARY, "variant": "binary", "weight": "binary"})
    assert binary_metrics["weight_out"] == 4  # a->c tem peso zero e continua zero
    assert all(edge["weight"] in (0, 1) for edge in binary["edges"])
    logged, log_metrics = et.apply(graph(EDGES), {**PRIMARY, "variant": "log1p", "weight": "log1p"})
    expected = sum(math.log1p(weight) for _, _, weight in EDGES)
    assert log_metrics["weight_out"] == pytest.approx(expected, rel=1e-6)
    assert log_metrics["edges_out"] == 5


def test_threshold_conta_peso_descartado():
    out, metrics = et.apply(
        graph(EDGES), {**PRIMARY, "variant": "threshold_5", "threshold": {"weight_min": 5, "rule": "drop_below"}}
    )
    assert metrics["edges_out"] == 1  # apenas a->b (5); c->d (4) fica abaixo
    assert metrics["weight_dropped"] == 9  # b->a (2) + a->c (0) + c->c (3) + c->d (4)
    assert metrics["weight_out"] == 5


def test_simetrizada_conserva_peso_total():
    out, metrics = et.apply(graph(EDGES), {**PRIMARY, "variant": "symmetrized", "direction": "symmetrized"})
    assert metrics["weight_out"] == 14
    assert metrics["edges_out"] == 4  # (a,b)=7, (a,c)=0, (c,c)=3, (c,d)=4
    assert out["graph"]["directed"] is False


def test_drop_self_loops_registra_peso():
    out, metrics = et.apply(graph(EDGES), {**PRIMARY, "variant": "drop_self_loops", "self_loops": "drop"})
    assert metrics["self_loops_dropped"] == 1
    assert metrics["weight_dropped"] == 3
    assert metrics["weight_out"] == 11


def test_config_invalida_falha():
    for bad in (
        {**PRIMARY, "extra": 1},
        {**PRIMARY, "threshold": {"weight_min": -1, "rule": "keep"}},
        {**PRIMARY, "threshold": {"weight_min": 0, "rule": "escolher"}},
        {**PRIMARY, "direction": "aleatoria"},
    ):
        with pytest.raises(et.TransformError):
            et.apply(graph(EDGES), bad)


def test_aplicacao_igual_sem_estatistica_do_alvo():
    first, _ = et.apply(graph(EDGES), PRIMARY)
    second, _ = et.apply(graph(EDGES), PRIMARY)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["provenance"]["adapter"]["config_sha256"] == et.config_sha256(PRIMARY)
    assert "target" not in et.config_sha256(PRIMARY)
