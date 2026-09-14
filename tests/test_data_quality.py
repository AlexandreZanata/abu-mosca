import json
import sys
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import data_quality as dq  # noqa: E402


def write_snapshot(directory: Path, nodes, edges, node_columns=("id", "degree_in", "degree_out")):
    directory.mkdir(parents=True, exist_ok=True)
    node_ids = [f"n{index:016x}" for index in range(nodes)]
    pre = [source for source, _, _ in edges]
    post = [target for _, target, _ in edges]
    weights = [weight for _, _, weight in edges]
    degree_in = np.bincount(post, weights=weights, minlength=nodes).astype("int64")
    degree_out = np.bincount(pre, weights=weights, minlength=nodes).astype("int64")
    node_table = pa.table(
        {
            "id": pa.array(node_ids, type=pa.string()),
            "degree_in": pa.array(degree_in.tolist(), type=pa.int64()),
            "degree_out": pa.array(degree_out.tolist(), type=pa.int64()),
        }
    ).select(node_columns)
    pq.write_table(node_table, directory / "nodes.parquet")
    pq.write_table(
        pa.table(
            {
                "source": pa.array([node_ids[source] for source in pre], type=pa.string()),
                "target": pa.array([node_ids[target] for target in post], type=pa.string()),
                "weight": pa.array(weights, type=pa.int64()),
            }
        ),
        directory / "edges.parquet",
    )


def test_auditoria_detecta_qualidade(tmp_path):
    write_snapshot(tmp_path, 4, [(0, 1, 5), (1, 0, 2), (2, 2, 1), (3, 3, 7)])
    report = dq.audit_snapshot(tmp_path, "teste")
    assert report["nodes"] == 4
    assert report["edges"] == 4
    assert report["duplicate_pairs"] == 0
    assert report["self_loops"] == 2
    assert report["reciprocal_edges"] == 2
    assert report["weight_sum"] == 15
    assert report["degree_mismatch_in"] == 0
    assert report["components"] == 3
    assert report["isolated_nodes"] == 0
    assert report["schema"]["edges"]["drift"] == {}


def test_duplicatas_e_drift_detectados(tmp_path):
    write_snapshot(tmp_path, 3, [(0, 1, 2), (0, 1, 3), (1, 2, 1)])
    report = dq.audit_snapshot(tmp_path, "dup")
    assert report["duplicate_pairs"] == 1
    write_snapshot(tmp_path, 3, [(0, 1, 1)])
    nodes_path = tmp_path / "nodes.parquet"
    table = pq.read_table(nodes_path).append_column("extra", pa.array([1, 2, 3], type=pa.int64()))
    pq.write_table(table, nodes_path)
    report = dq.audit_snapshot(tmp_path, "drift")
    assert report["schema"]["nodes"]["drift"]


def test_manifesto_congela_exploratorio(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    write_snapshot(source, 2, [(0, 1, 4)])
    write_snapshot(target, 2, [(0, 1, 9)])
    manifest_path = tmp_path / "manifests" / "analitico.json"
    manifest = dq.freeze_manifest(source, target, manifest_path)
    assert manifest["status"] == "exploratory-only"
    assert manifest["labels_used"] is False
    assert "inconclusiva" in manifest["confirmatory_outcome"]
    assert len(manifest["analytic_sha256"]) == 64
    assert manifest == json.loads(manifest_path.read_text(encoding="utf-8"))
