import copy
import json
import sys
from pathlib import Path

import numpy as np
import pytest
import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import gnn_gin as m3  # noqa: E402
import gnn_graphsage as gg  # noqa: E402
import ssl_decoder as sd  # noqa: E402

REPORT = ROOT / "artifacts" / "reports" / "M03-GIN.json"


def test_pareamento_dentro_da_tolerancia():
    rows = m3.pairing_table()
    assert {row["layers"] for row in rows} == {2, 3}
    for row in rows:
        assert row["within_tolerance"] and row["both_in_mvp_range"], row
        assert row["relative_delta"] <= m3.PARAMETER_TOLERANCE
        layers = row["layers"]
        gin_config = m3.GINConfig(dim=row["gin"]["dim"], layers=layers, fanout=tuple(row["gin"]["fanout"]), dropout=row["gin"]["dropout"])
        assert m3.gin_parameter_formula(gin_config) == row["gin"]["parameters"]
        graphsage_config = gg.EncoderConfig(dim=row["graphsage"]["dim"], layers=layers, fanout=gg.pad_fanout(layers, row["graphsage"]["fanout"]))
        assert gg.parameter_count_formula(graphsage_config) == row["graphsage"]["parameters"]
        assert list(gg.pad_fanout(layers, row["graphsage"]["fanout"])) == list(row["gin"]["fanout"])
        assert gg.MVP_RANGE[0] <= row["gin"]["parameters"] <= gg.MVP_RANGE[1]


def test_contagem_exata_do_modelo():
    for dim, layers in ((16, 1), (64, 2), (128, 3)):
        config = m3.GINConfig(dim=dim, layers=layers, fanout=(5,) * layers)
        encoder = m3.build_gin(config)
        assert m3.gin_parameter_count(encoder) == m3.gin_parameter_formula(config)


def test_sem_parametros_por_node_e_soma():
    encoder = m3.build_gin(m3.GINConfig(dim=32, layers=2, fanout=(5, 5)))
    keys = " ".join(encoder.state_dict().keys())
    assert "nodes" not in keys and "embedding" not in keys.lower()
    source = (ROOT / "tools" / "gnn_gin.py").read_text(encoding="utf-8")
    assert "nn.Embedding" not in source
    assert 'aggregation="sum"' in source or "aggregation=\"sum\"" in source


def test_soma_difere_da_media():
    src, dst, weight, features, adjacency = gg._fixture_graph(seed=5)
    n_nodes = features.shape[0]
    binary = np.ones_like(weight)
    in_edges = gg.csr_edges(gg.build_direction_csr(src, dst, binary, n_nodes, "in"))
    out_edges = gg.csr_edges(gg.build_direction_csr(src, dst, binary, n_nodes, "out"))
    gin = m3.build_gin(m3.GINConfig(dim=16, layers=2, fanout=(n_nodes, n_nodes)))
    sage = gg.build_encoder(gg.EncoderConfig(dim=16, layers=2, fanout=(n_nodes, n_nodes)))
    gin_embeddings = gg.forward_full(gin, features, in_edges, out_edges, aggregation="sum").detach().numpy()
    sage_embeddings = gg.forward_full(sage, features, in_edges, out_edges, aggregation="mean").detach().numpy()
    assert gin_embeddings.shape == sage_embeddings.shape
    assert not np.allclose(gin_embeddings, sage_embeddings)
    assert adjacency is not None


def test_overfit_controlado_e_determinismo():
    smoke = m3.fixture_smoke(seed=gg.MASTER_SEED)
    assert smoke["overfit_train_auc"] >= 0.95
    assert smoke["loss_last"] < 0.5 * smoke["loss_first"]
    assert smoke["gradients_finite"]
    assert smoke["deterministic_same_seed"]
    assert smoke["serialization_max_abs_diff"] <= 1e-6
    assert smoke["reloaded_config_matches"]
    assert smoke["encoder_parameters"] == smoke["parameters_formula"]


def test_incompatibilidade_registrada_no_relatorio_real():
    if not REPORT.exists():
        pytest.skip("smoke M03 ainda não executado")
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    smoke = report["real_graph_smoke"]
    if smoke.get("diverged"):
        assert report["candidate_status"]["usable_in_m05_as_implemented"] is False
        assert "R07" in report["candidate_status"]["summary"]
        assert report["discarded_runs"] and report["discarded_runs"][0]["diverged"]
    assert smoke["edge_weight_mode"] == "binary"


@pytest.mark.skipif(not REPORT.exists(), reason="smoke M03 ainda não executado")
def test_check_report_real_passa():
    assert m3.check_report(REPORT) == []


@pytest.mark.skipif(not REPORT.exists(), reason="smoke M03 ainda não executado")
def test_check_report_detecta_desonestidade(tmp_path):
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    wrong = copy.deepcopy(report)
    wrong["pairing"]["rows"][0]["gin"]["parameters"] += 1
    path = tmp_path / "pairing.json"
    path.write_text(json.dumps(wrong), encoding="utf-8")
    assert any("contagem" in failure for failure in m3.check_report(path))
    hidden = copy.deepcopy(report)
    hidden["candidate_status"]["usable_in_m05_as_implemented"] = True
    path = tmp_path / "hidden.json"
    path.write_text(json.dumps(hidden), encoding="utf-8")
    assert any("incompatível" in failure for failure in m3.check_report(path))
    node_table = copy.deepcopy(report)
    node_table["config"]["per_node_parameters"] = 3
    path = tmp_path / "node.json"
    path.write_text(json.dumps(node_table), encoding="utf-8")
    assert any("parâmetros por node" in failure for failure in m3.check_report(path))
    weak = copy.deepcopy(report)
    weak["fixture_smoke"]["overfit_train_auc"] = 0.5
    path = tmp_path / "overfit.json"
    path.write_text(json.dumps(weak), encoding="utf-8")
    assert any("overfit" in failure for failure in m3.check_report(path))


def test_sem_referencias_proibidas():
    source = (ROOT / "tools" / "gnn_gin.py").read_text(encoding="utf-8")
    for token in ("male-cns", "data/sealed", "target_labels", "crosswalk"):
        assert token not in source
    assert "binári" in json.dumps(m3.GIN_DIFFERENCES, ensure_ascii=False).lower()
    assert m3.FIXTURE_TRAINING["lr"] == 1e-3
