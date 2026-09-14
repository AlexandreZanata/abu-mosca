import hashlib
import json
import random
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import opaque_ids  # noqa: E402
import topology_features as tf  # noqa: E402


def node_id(label: str) -> str:
    return opaque_ids.opaque_node_id("FIXTURE", "v1", label)


def graph(edges: list[tuple[str, str, int]], nodes: list[str] | None = None) -> dict:
    labels = nodes or sorted({label for edge in edges for label in edge[:2]})
    return {
        "schema_version": "1.0",
        "provenance": {
            "dataset": "FIXTURE",
            "release": "v1",
            "license": "CC0-1.0",
            "source_files": [{"path": "sintetico.csv", "sha256": "0" * 64}],
            "adapter": {"name": "teste", "version": "1.0", "config_sha256": "1" * 64},
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
        "nodes": [
            {"id": node_id(label), "attributes": {"degree_in": 0}, "missing": []} for label in labels
        ],
        "edges": [
            {"source": node_id(pre), "target": node_id(post), "weight": weight, "attributes": {}, "missing": []}
            for pre, post, weight in edges
        ],
    }


def features_by_id(payload: dict) -> dict:
    ids, matrix = tf.raw_features(payload)
    return {node_id: row for node_id, row in zip(ids, matrix)}


def test_features_exatas_por_tipo():
    payload = graph([("a", "b", 5), ("b", "a", 2), ("a", "c", 3), ("a", "a", 4)])
    got = features_by_id(payload)
    # in/out degree do nó a: b->a conta 1; self-loop não conta grau
    assert got[node_id("a")] == [1.0, 2.0, 2.0, 8.0, 2.0 / 8.0, 4.0]
    assert got[node_id("b")] == [1.0, 1.0, 5.0, 2.0, 2.0 / 2.0, 0.0]
    assert got[node_id("c")] == [1.0, 0.0, 3.0, 0.0, 0.0, 0.0]


def test_permutar_ids_e_ordem_preserva_features():
    edges = [("a", "b", 5), ("b", "a", 2), ("a", "c", 3), ("c", "c", 1)]
    baseline = features_by_id(graph(edges))
    lookup = {"a": "x", "b": "y", "c": "z"}
    permuted_edges = [(lookup[pre], lookup[post], weight) for pre, post, weight in edges]
    permuted = features_by_id(graph(permuted_edges))
    inverse = {value: key for key, value in lookup.items()}
    for label, new_label in lookup.items():
        assert permuted[node_id(new_label)] == baseline[node_id(label)]
    assert sorted(map(tuple, permuted.values())) == sorted(map(tuple, baseline.values()))
    # ordem não importa: embaralhar nodes e arestas não muda o resultado
    shuffled = graph(edges)
    rng = random.Random(7)
    rng.shuffle(shuffled["nodes"])
    rng.shuffle(shuffled["edges"])
    assert features_by_id(shuffled) == baseline


def test_normalizador_ajustado_somente_na_fonte():
    source = graph([("a", "b", 10), ("b", "a", 10)])
    target = graph([("a", "b", 1000), ("b", "a", 1)])
    stats = tf.fit(source)
    _, _, report = tf.transform(target, stats)
    assert stats["features"]["weighted_out"]["mean"] == pytest.approx(10.0)
    # o alvo é clipado nos limites fixos porque os stats vêm da fonte
    assert report["clipped"] >= 2


def test_nao_finitos_e_clip_por_regra_fixa():
    source = graph([("a", "b", 1)])
    target = graph([("a", "b", 10**9), ("c", "c", 1)])
    stats = tf.fit(source)
    _, matrix, report = tf.transform(target, stats)
    assert report["nonfinite_replaced"] == 0
    assert report["clipped"] >= 1
    assert all(abs(value) <= tf.CLIP_Z for row in matrix for value in row)
    isolated = graph([("a", "b", 1)], nodes=["a", "b", "z"])
    ids, matrix = tf.raw_features(isolated)
    index = ids.index(node_id("z"))
    assert matrix[index] == [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]


def test_matriz_nao_contem_ids_nem_atributos_proibidos():
    payload = graph([("a", "b", 3)])
    ids, matrix = tf.raw_features(payload)
    assert len(matrix[0]) == len(tf.FEATURE_NAMES)
    assert all(isinstance(node_id_value, str) for node_id_value in ids)
    assert len(ids) == len(set(ids)) == len(matrix)


def test_atributo_proibido_falha():
    payload = graph([("a", "b", 1)])
    payload["nodes"][0]["attributes"]["region"] = "AL"
    payload["nodes"][0]["missing"] = ["region"]
    with pytest.raises(tf.FeatureError, match="proibido"):
        tf.raw_features(payload)
