import csv
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import adapter_manc as adapter  # noqa: E402
import graph_contract as gc  # noqa: E402

REAL_CSV = ROOT / "data" / "raw" / "spikes" / "manc_traced_connections.csv"
GOLDEN = ROOT / "tests" / "fixtures" / "manc-sample-graph.json"
METRICS = ROOT / "artifacts" / "reports" / "H02-ADAPTER-FONTE.json"


def write_csv(tmp_path: Path, rows: list[tuple[str, str, str]]) -> Path:
    path = tmp_path / "connections.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["bodyId_pre", "bodyId_post", "weight"])
        writer.writerows(rows)
    return path


def test_agrega_multiedges_e_conserva_peso(tmp_path):
    path = write_csv(tmp_path, [("10", "20", "3"), ("10", "20", "4"), ("20", "30", "1")])
    graph, metrics = adapter.build_graph(path)
    assert metrics["rows_in"] == 3
    assert metrics["edges_after_aggregation"] == 2
    assert metrics["multiedge_groups"] == 1
    assert metrics["weight_sum_in"] == metrics["weight_sum_out"] == 8
    assert gc.validate_graph(graph) == []
    pair = [edge for edge in graph["edges"] if edge["weight"] == 7]
    assert len(pair) == 1


def test_ids_opacos_unicos_e_sem_atributos_proibidos(tmp_path):
    path = write_csv(tmp_path, [("10", "20", "1"), ("20", "10", "2")])
    graph, metrics = adapter.build_graph(path)
    ids = [node["id"] for node in graph["nodes"]]
    assert len(ids) == len(set(ids)) == 2
    assert all(node_id.startswith("n") and len(node_id) == 17 for node_id in ids)
    for node in graph["nodes"]:
        assert not set(node["attributes"]) & set(adapter.FORBIDDEN_NODE_ATTRIBUTES)
    assert metrics["self_loops"] == 0
    assert graph["graph"]["allow_self_loops"] is False


def test_peso_negativo_e_cabecalho_errado_falham(tmp_path):
    bad = write_csv(tmp_path, [("10", "20", "-1")])
    with pytest.raises(adapter.AdapterError):
        adapter.build_graph(bad)
    wrong = tmp_path / "wrong.csv"
    wrong.write_text("a,b,c\n1,2,3\n", encoding="utf-8")
    with pytest.raises(adapter.AdapterError):
        adapter.build_graph(wrong)


def test_amostra_dourada_e_valida_e_limitada():
    sample = json.loads(GOLDEN.read_text(encoding="utf-8"))
    assert gc.validate_graph(sample) == []
    assert len(sample["nodes"]) == 40
    assert len(sample["edges"]) == 60
    assert sample["provenance"]["adapter"]["name"].endswith("-golden")
    recorded = json.loads(METRICS.read_text(encoding="utf-8"))
    digest = hashlib.sha256(GOLDEN.read_bytes()).hexdigest()
    assert digest == recorded["golden_sha256"]


@pytest.mark.skipif(not REAL_CSV.exists(), reason="amostra real de D09 ausente")
def test_amostra_real_reconcilia_com_manifesto():
    manifest = json.loads((ROOT / "data" / "manifests" / "manc-v1.0.json").read_text(encoding="utf-8"))
    entry = next(item for item in manifest["files"] if item["path"].endswith("manc_traced_connections.csv"))
    graph, metrics = adapter.build_graph(REAL_CSV)
    assert metrics["input_sha256"] == entry["sha256"]
    assert metrics["rows_in"] == 5243574
    assert metrics["nodes"] == 23188
    assert metrics["weight_conserved"] is True
    assert metrics["multiedge_groups"] == 0
    assert gc.validate_graph(graph) == []
