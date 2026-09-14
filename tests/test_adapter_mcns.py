import json
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.feather as feather
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import adapter_mcns as adapter  # noqa: E402
import graph_contract as gc  # noqa: E402

REAL_WEIGHTS = ROOT / "data" / "raw" / "target-public" / "mcns_connectome_weights.feather"
GOLDEN = ROOT / "tests" / "fixtures" / "mcns-sample-graph.json"
METRICS = ROOT / "artifacts" / "reports" / "H03-ADAPTER-ALVO.json"


def write_feather(tmp_path: Path, columns: dict) -> Path:
    path = tmp_path / "weights.feather"
    feather.write_feather(pa.table(columns), path, compression="zstd")
    return path


def test_converte_amostra_e_conserva_peso(tmp_path):
    path = write_feather(
        tmp_path,
        {
            "body_pre": pa.array([10, 10, 20, 30], type=pa.int64()),
            "body_post": pa.array([20, 20, 30, 10], type=pa.int64()),
            "weight": pa.array([3, 4, 1, 2], type=pa.int64()),
        },
    )
    table = adapter.read_weights(path)
    graph, metrics = adapter.sample_graph(
        table, sample_rows=10,
        source={"path": "sintetico.feather", "sha256": "0" * 64},
    )
    assert metrics["sample_rows"] == 4
    assert metrics["sample_multiedge_groups"] == 1
    assert metrics["sample_weight_sum_in"] == metrics["sample_weight_sum_out"] == 10
    assert gc.validate_graph(graph) == []
    ids = [node["id"] for node in graph["nodes"]]
    assert len(ids) == len(set(ids)) == 3
    assert all(node_id.startswith("n") and len(node_id) == 17 for node_id in ids)
    for node in graph["nodes"]:
        assert not set(node["attributes"]) & set(adapter.FORBIDDEN_NODE_ATTRIBUTES)


def test_colunas_extras_ou_pesos_negativos_falham(tmp_path):
    extra = write_feather(
        tmp_path,
        {
            "body_pre": pa.array([1], type=pa.int64()),
            "body_post": pa.array([2], type=pa.int64()),
            "weight": pa.array([1], type=pa.int64()),
            "type": pa.array(["x"]),
        },
    )
    with pytest.raises(adapter.AdapterError):
        adapter.read_weights(extra)
    negative = write_feather(
        tmp_path,
        {
            "body_pre": pa.array([1], type=pa.int64()),
            "body_post": pa.array([2], type=pa.int64()),
            "weight": pa.array([-1], type=pa.int64()),
        },
    )
    with pytest.raises(adapter.AdapterError):
        adapter.full_file_metrics(adapter.read_weights(negative), negative)


def test_golden_valida_sem_labels():
    sample = json.loads(GOLDEN.read_text(encoding="utf-8"))
    assert gc.validate_graph(sample) == []
    assert len(sample["nodes"]) == 40
    assert 40 <= len(sample["edges"]) <= 60
    for node in sample["nodes"]:
        assert not set(node["attributes"]) & set(adapter.FORBIDDEN_NODE_ATTRIBUTES)
    metrics = json.loads(METRICS.read_text(encoding="utf-8"))
    import hashlib

    assert hashlib.sha256(GOLDEN.read_bytes()).hexdigest() == metrics["golden_sha256"]


def test_adapter_nao_menciona_anotacoes():
    source = (ROOT / "tools" / "adapter_mcns.py").read_text(encoding="utf-8")
    for token in ("body-annotations", "flywireType", "hemibrainType", "annotations"):
        assert token not in source


@pytest.mark.skipif(not REAL_WEIGHTS.exists(), reason="grafo público do alvo ausente")
def test_arquivo_publico_conta_e_reconcilia():
    table = adapter.read_weights(REAL_WEIGHTS)
    metrics = adapter.full_file_metrics(table, REAL_WEIGHTS)
    assert metrics["rows_full"] == 151856684
    assert metrics["weight_sum_full"] == 311833243
    assert metrics["weight_min_full"] == 1
    assert metrics["self_loops_full"] == 123
    manifest = json.loads((ROOT / "data" / "manifests" / "mcns-v1.0.json").read_text(encoding="utf-8"))
    entry = next(item for item in manifest["files"] if item["path"].endswith("mcns_connectome_weights.feather"))
    assert metrics["input_sha256"] == entry["sha256"]
    assert metrics["input_sha256"] == "e35da783d1c686b2b58b3b87cd6a403ae43bfcfba8bff28e08ef752c1a56afc1"
