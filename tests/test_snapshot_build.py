import csv
import json
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.feather as feather
import pyarrow.parquet as pq
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import snapshot_build as snap  # noqa: E402


def write_manc_csv(tmp_path: Path) -> Path:
    path = tmp_path / "connections.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["bodyId_pre", "bodyId_post", "weight"])
        writer.writerows([("10", "20", "3"), ("10", "20", "4"), ("20", "30", "1")])
    return path


def write_manifest(tmp_path: Path, files: dict, name: str) -> Path:
    path = tmp_path / name
    path.write_text(
        json.dumps({"schema_version": "1.0", "dataset": "x", "release": "v", "source_page": "https://x",
                    "license": "CC-BY-4.0",
                    "files": [{"path": key, "url": "https://x", "bytes": 1, "sha256": value, "accessed_at": "2026-09-14"}
                              for key, value in files.items()]}),
        encoding="utf-8",
    )
    return path


def test_manc_snapshot_conserva_e_e_idempotente(tmp_path):
    csv_path = write_manc_csv(tmp_path)
    manifest = write_manifest(tmp_path, {"manc_traced_connections.csv": snap.sha256_file(csv_path)}, "m.json")
    out = tmp_path / "out"
    first = snap.build_manc(csv_path, manifest, out)
    assert first["rows"] == 3 and first["nodes"] == 3 and first["weight_sum"] == 8
    edges = pq.read_table(out / "edges.parquet")
    assert edges.column_names == ["source", "target", "weight"]
    assert all(column.startswith("n") for column in edges["source"].to_pylist())
    second = snap.build_manc(csv_path, manifest, out)
    assert second.get("status") == "cached"
    assert second["snapshot_set_sha256"] == first["snapshot_set_sha256"]


def test_manc_manifest_divergente_falha(tmp_path):
    csv_path = write_manc_csv(tmp_path)
    manifest = write_manifest(tmp_path, {"manc_traced_connections.csv": "0" * 64}, "m.json")
    with pytest.raises(snap.SnapshotError, match="manifesto"):
        snap.build_manc(csv_path, manifest, tmp_path / "out")


def test_mcns_neuron_level_agrega_e_nao_usa_labels(tmp_path):
    weights = tmp_path / "weights.feather"
    feather.write_feather(
        pa.table(
            {
                "body_pre": pa.array([1, 1, 2, 9], type=pa.int64()),
                "body_post": pa.array([2, 2, 3, 1], type=pa.int64()),
                "weight": pa.array([5, 2, 1, 7], type=pa.int64()),
            }
        ),
        weights,
    )
    annotations = tmp_path / "annotations.feather"
    feather.write_feather(
        pa.table(
            {
                "bodyId": pa.array([1, 2, 3], type=pa.int64()),
                "type": pa.array(["T1", "T2", "T3"]),
                "region": pa.array(["r1", "r2", "r3"]),
            }
        ),
        annotations,
    )
    weights_sha = snap.sha256_file(weights)
    annotations_sha = snap.sha256_file(annotations)
    manifest = write_manifest(
        tmp_path,
        {
            "mcns_connectome_weights.feather": weights_sha,
            "body-annotations-male-cns-v1.0-minconf-0.5.feather": annotations_sha,
        },
        "m.json",
    )
    out = tmp_path / "out"
    result = snap.build_mcns(weights, manifest, out, annotations=annotations)
    assert result["rows"] == 2  # (1,2) agregado com peso 7; (2,3) com 1
    assert result["segment_edges_dropped"] == 1  # aresta 9->1 fora das anotações
    assert result["nodes"] == 3
    assert result["weight_sum"] == 8
    edges = pq.read_table(out / "edges.parquet")
    assert edges.column_names == ["source", "target", "weight"]
    assert "type" not in " ".join(edges.column_names)
    nodes = pq.read_table(out / "nodes.parquet")
    assert nodes.column_names == ["id", "degree_in", "degree_out"]
    assert "region" not in " ".join(nodes.column_names)
    assert result["annotations_columns_used"] == ["bodyId"]
