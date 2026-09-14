import json
import random
import sys
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.feather as feather
import pyarrow.parquet as pq
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import artisanal_features as af  # noqa: E402
import opaque_ids  # noqa: E402

EDGES = [
    ("a", "b", 5),
    ("b", "a", 2),
    ("a", "c", 3),
    ("c", "a", 1),
    ("b", "c", 4),
    ("c", "b", 1),
    ("d", "e", 7),
    ("e", "d", 9),
]


def write_snapshot(directory: Path, edges, shuffle=False):
    labels = sorted({value for edge in edges for value in edge[:2]})
    ids = [opaque_ids.opaque_node_id("MANC", "manc:v1.2.1", label) for label in labels]
    order = list(range(len(ids)))
    if shuffle:
        random.Random(3).shuffle(order)
    directory.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.table({"id": pa.array([ids[index] for index in order])}), directory / "nodes.parquet")
    index_of = {label: position for position, label in enumerate(labels)}
    rows = list(edges)
    if shuffle:
        random.Random(5).shuffle(rows)
    pq.write_table(
        pa.table(
            {
                "source": pa.array([ids[index_of[pre]] for pre, _, _ in rows]),
                "target": pa.array([ids[index_of[post]] for _, post, _ in rows]),
                "weight": pa.array([weight for _, _, weight in rows], type=pa.int64()),
            }
        ),
        directory / "edges.parquet",
    )
    return {label: ids[index] for index, label in enumerate(labels)}


def test_features_em_grafo_conhecido(tmp_path):
    mapping = write_snapshot(tmp_path, EDGES)
    ids, features = af.extract_features(tmp_path)
    index = {node: position for position, node in enumerate(ids)}
    node = mapping["a"]
    position = index[node]
    assert features["in_degree"][position] == 2
    assert features["out_degree"][position] == 2
    assert features["weighted_in"][position] == 3
    assert features["weighted_out"][position] == 8
    assert features["reciprocal_weight_ratio"][position] == pytest.approx(3 / 8)
    assert features["reciprocal_count_ratio"][position] == 1.0
    assert features["clustering_undirected"][position] == pytest.approx(1.0)
    assert features["feedforward_paths"][position] == 4
    assert features["bottleneck_ratio"][position] == pytest.approx(0.5)
    assert features["successor_out_degree_mean"][position] == pytest.approx(2.0)
    assert features["predecessor_in_degree_mean"][position] == pytest.approx(2.0)
    d_position = index[mapping["d"]]
    assert features["reciprocal_weight_ratio"][d_position] == pytest.approx(7 / 7)
    assert features["clustering_undirected"][d_position] == 0.0


def test_invariancia_a_ids_e_ordem(tmp_path):
    first_dir = tmp_path / "a"
    second_dir = tmp_path / "b"
    mapping = write_snapshot(first_dir, EDGES)
    write_snapshot(second_dir, EDGES, shuffle=True)
    ids_a, features_a = af.extract_features(first_dir)
    ids_b, features_b = af.extract_features(second_dir)
    index_a = {node: position for position, node in enumerate(ids_a)}
    index_b = {node: position for position, node in enumerate(ids_b)}
    assert set(ids_a) == set(ids_b)
    for node in ids_a:
        for name, values in features_a.items():
            assert values[index_a[node]] == pytest.approx(features_b[name][index_b[node]])


def test_probe_deterministico():
    train = np.asarray([[0.0, 0.0], [0.1, 0.1], [5.0, 5.0], [5.1, 4.9]])
    labels = ["A", "A", "B", "B"]
    val = np.asarray([[0.2, 0.2], [4.8, 5.0]])
    first = af.probe(train, labels, val, ["A", "B"])
    second = af.probe(train, labels, val, ["A", "B"])
    assert first == second == ["A", "B"]


def test_familias_sem_features_proibidas():
    for family, names in af.FAMILIES.items():
        for name in names:
            lowered = name.lower()
            assert not any(token in lowered for token in af.FORBIDDEN), (family, name)
    source = (ROOT / "tools" / "artisanal_features.py").read_text(encoding="utf-8")
    for token in ("male-cns", "data/sealed", "target_labels", "crosswalk"):
        assert token not in source


def test_run_com_ablation(tmp_path):
    mapping = write_snapshot(tmp_path / "snap", EDGES)
    bodies = []
    labels = []
    for label in ("a", "b", "c", "d", "e"):
        bodies.extend([label] * 12)
        labels.extend(["X"] * 12)
    properties = tmp_path / "properties.feather"
    feather.write_feather(
        pa.table(
            {
                "bodyId": pa.array(bodies, type=pa.string()),
                "type": pa.array(labels),
            }
        ),
        properties,
    )
    report = af.run(tmp_path / "snap", properties, tmp_path / "out", tmp_path / "report.json")
    assert set(report["results"]) == set(af.FAMILIES) | {"all"}
    assert report["interrupted_features"]
    assert report["predictions"]["sha256"]
