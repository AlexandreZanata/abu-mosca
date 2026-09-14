import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.feather as feather
import pyarrow.parquet as pq
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import baselines_source as b  # noqa: E402
import opaque_ids  # noqa: E402


def make_fixture(tmp_path: Path):
    bodies = list(range(1, 41))
    labels = ["A"] * 20 + ["B"] * 20
    properties = tmp_path / "properties.feather"
    feather.write_feather(
        pa.table({"bodyId": pa.array(bodies, type=pa.int64()), "type": pa.array(labels)}), properties
    )
    node_ids = [opaque_ids.opaque_node_id(b.DATASET, b.RELEASE, body) for body in bodies]
    edges = []
    for index in range(39):
        edges.append((index, index + 1, 1 if index % 2 == 0 else 9))
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    pq.write_table(
        pa.table({"id": pa.array(node_ids)}), snapshot / "nodes.parquet"
    )
    pq.write_table(
        pa.table(
            {
                "source": pa.array([node_ids[pre] for pre, _, _ in edges]),
                "target": pa.array([node_ids[post] for _, post, _ in edges]),
                "weight": pa.array([weight for _, _, weight in edges], type=pa.int64()),
            }
        ),
        snapshot / "edges.parquet",
    )
    return properties, snapshot


def test_split_deterministico_e_cobertura(tmp_path):
    properties, _ = make_fixture(tmp_path)
    labels, meta = b.load_source_labels(properties)
    assert meta["classes_k_min"] == 2
    train, val = b.split_deterministic(labels)
    assert len(train) + len(val) == len(labels)
    assert set(train.values()) == set(val.values()) == {"A", "B"}
    train_again, val_again = b.split_deterministic(labels)
    assert train == train_again and val == val_again


def test_run_executa_baselines_e_concorda_chance(tmp_path):
    properties, snapshot = make_fixture(tmp_path)
    report = b.run(properties, snapshot, tmp_path / "out", tmp_path / "report.json", seeds=(1, 2, 3))
    analytical = report["results"]["analytical"]
    majority = report["results"]["baselines"]["majority"]
    assert majority["simulated_accuracy"] == pytest.approx(majority["analytical_accuracy"])
    random_result = report["results"]["baselines"]["stratified_random"]
    assert abs(random_result["simulated_draws_mean"] - random_result["analytical_accuracy"]) < 0.05
    assert random_result["seeds"] == [1, 2, 3]
    degree = report["results"]["baselines"]["degree_only"]
    assert 0.0 <= degree["recall"]["@1"]["macro"] <= 1.0
    assert report["degree_features"] == list(b.DEGREE_FEATURES)
    assert len(report["stats_source_fit"]["mean"]) == len(b.DEGREE_FEATURES)
    for entry in report["predictions"]:
        assert len(entry["sha256"]) == 64
        assert Path(entry["path"]).exists()


def test_stats_e_source_fit(tmp_path):
    properties, snapshot = make_fixture(tmp_path)
    labels, _ = b.load_source_labels(properties)
    train, val = b.split_deterministic(labels)
    features = b.degree_features(snapshot)
    stats = b.fit_stats(np.asarray([features[node][: len(b.DEGREE_FEATURES)] for node in train]))
    first = b.transform(np.asarray([features[node][: len(b.DEGREE_FEATURES)] for node in val]), stats)
    second = b.transform(np.asarray([features[node][: len(b.DEGREE_FEATURES)] for node in val]), stats)
    assert np.allclose(first, second)
    assert any(abs(value) > 1e-9 for value in stats["std"])


def test_nao_le_nada_do_alvo():
    source = (ROOT / "tools" / "baselines_source.py").read_text(encoding="utf-8")
    for token in ("male-cns", "data/sealed", "target_labels", "crosswalk"):
        assert token not in source
