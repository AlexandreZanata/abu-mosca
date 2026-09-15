import copy
import json
import sys
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pytest
import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import opaque_ids  # noqa: E402
import ssl_decoder as sd  # noqa: E402
import ssl_task as st  # noqa: E402

REPORT = ROOT / "artifacts" / "reports" / "M01-SSL-TASK.json"


def write_snapshot(directory: Path, edges):
    directory.mkdir(parents=True, exist_ok=True)
    labels = sorted({value for edge in edges for value in edge[:2]})
    ids = [opaque_ids.opaque_node_id("MANC", "manc:v1.2.1", label) for label in labels]
    pq.write_table(pa.table({"id": pa.array(ids)}), directory / "nodes.parquet")
    index = {label: position for position, label in enumerate(labels)}
    pq.write_table(
        pa.table(
            {
                "source": pa.array([ids[index[pre]] for pre, _, _ in edges]),
                "target": pa.array([ids[index[post]] for _, post, _ in edges]),
                "weight": pa.array([weight for _, _, weight in edges], type=pa.int64()),
            }
        ),
        directory / "edges.parquet",
    )
    return ids


def fixture_edges():
    # 12 nós: cadeia 0→1→...→9, reversos em pares, atalho 0→5 e self-loop 3→3
    edges = [(i, i + 1, i + 1) for i in range(9)]
    edges += [(i + 1, i, i + 1) for i in range(9)]
    edges += [(0, 5, 4), (3, 3, 2), (9, 0, 3)]
    return edges


def test_hash_mask_deterministico():
    src = np.asarray([0, 1, 2, 3, 4], dtype=np.int64)
    dst = np.asarray([1, 2, 3, 4, 0], dtype=np.int64)
    first = st.hash_mask(src, dst, 5, 42, 0.4)
    second = st.hash_mask(src, dst, 5, 42, 0.4)
    third = st.hash_mask(src, dst, 5, 43, 0.4)
    assert np.array_equal(first, second)
    assert not np.array_equal(first, third)
    with pytest.raises(st.SslTaskError):
        st.hash_mask(src, dst, 5, 42, 1.5)


def test_mascara_com_reverso_e_self_loop():
    edges = [(0, 1, 1), (1, 0, 2), (2, 3, 3), (3, 3, 4)]
    src = np.asarray([edge[0] for edge in edges], dtype=np.int64)
    dst = np.asarray([edge[1] for edge in edges], dtype=np.int64)
    mask = st.hash_mask(src, dst, 4, 7, 0.5)
    info = st.build_mask(src, dst, 4, 7, 0.5)
    full = info.pop("mask")
    assert set(np.nonzero(full)[0].tolist()) >= set(np.nonzero(mask)[0].tolist())
    for index in np.nonzero(full)[0]:
        reverse = np.nonzero((src == dst[index]) & (dst == src[index]))[0]
        assert set(reverse.tolist()).issubset(set(np.nonzero(full)[0].tolist()))
    assert info["validation_edges"] == int(full.sum())
    assert info["train_edges"] + info["validation_edges"] == len(src)


def test_separacao_detecta_vazamento(tmp_path):
    ids = write_snapshot(tmp_path / "snap", fixture_edges())
    _, src, dst, wgt = st.load_source_edges(tmp_path / "snap")
    mask = st.build_mask(src, dst, len(ids), 11, 0.3)["mask"]
    train_idx = np.nonzero(~mask)[0]
    val_idx = np.nonzero(mask)[0]
    assert st.separation_checks(src, dst, train_idx, val_idx, len(ids))["leaks"] == 0
    leaked = np.concatenate([train_idx, val_idx[:1]])
    with pytest.raises(st.SslTaskError):
        st.separation_checks(src, dst, leaked, val_idx, len(ids))
    view_src, view_dst, _ = st.training_view(src, dst, wgt, mask)
    assert len(view_src) == len(src) - int(mask.sum())


def test_negativos_pareados_e_deterministicos(tmp_path):
    ids = write_snapshot(tmp_path / "snap", fixture_edges())
    _, src, dst, wgt = st.load_source_edges(tmp_path / "snap")
    n_nodes = len(ids)
    mask_info = st.build_mask(src, dst, n_nodes, 5, 0.25)
    mask = mask_info["mask"]
    train_src, train_dst, train_wgt = st.training_view(src, dst, wgt, mask)
    train_csr = st.build_csr(train_src, train_dst, n_nodes)
    full_csr = st.build_csr(src, dst, n_nodes)
    degrees = st.degree_tables(train_src, train_dst, train_wgt, n_nodes)
    positives_u = src[mask]
    positives_v = dst[mask]
    first = st.sample_negatives(positives_u, positives_v, train_csr, full_csr, degrees["log_total"], n_nodes, k=3)
    second = st.sample_negatives(positives_u, positives_v, train_csr, full_csr, degrees["log_total"], n_nodes, k=3)
    assert np.array_equal(first["u"], second["u"]) and np.array_equal(first["v"], second["v"])
    assert first["negatives_total"] == 3 * len(positives_u)
    true_edges = set(zip(src.tolist(), dst.tolist()))
    for u, v in zip(first["u"].tolist(), first["v"].tolist()):
        assert (u, v) not in true_edges
        assert v != u
    assert first["degree_abs_log_diff_max"] >= 0
    assert 0.0 <= first["class_match_rate"] <= 1.0
    assert first["class_two"] + first["class_far"] == first["negatives_total"]


def test_auc_ap_conferidos():
    perfect = st.auc_ap(np.asarray([0.9, 0.8, 0.3, 0.2]), np.asarray([1, 1, 0, 0]))
    assert perfect["auc"] == 1.0 and perfect["ap"] == 1.0
    inverted = st.auc_ap(np.asarray([0.1, 0.2, 0.8, 0.9]), np.asarray([1, 1, 0, 0]))
    assert inverted["auc"] == 0.0 and inverted["ap"] == pytest.approx(0.416667, abs=1e-5)
    tied = st.auc_ap(np.asarray([0.5, 0.5, 0.5, 0.5]), np.asarray([1, 0, 1, 0]))
    assert tied["auc"] == 0.5 and tied["ap"] == pytest.approx(0.5)
    with pytest.raises(st.SslTaskError):
        st.auc_ap(np.asarray([0.1, 0.2]), np.asarray([1, 1]))


def test_logistica_separa_exemplo_simples():
    rng = np.random.RandomState(0)
    positive = rng.randn(60, 3) + 2.0
    negative = rng.randn(60, 3) - 2.0
    features = np.vstack([positive, negative])
    labels = np.concatenate([np.ones(60, dtype=np.int64), np.zeros(60, dtype=np.int64)])
    weights, bias, mean, std = st.logistic_fit(features, labels)
    scores = st.logistic_predict(features, weights, bias, mean, std)
    assert st.auc_ap(scores, labels)["auc"] >= 0.99


def test_decoder_sem_parametros_por_node():
    decoder = sd.BilinearDecoder(8)
    assert int(sum(p.numel() for p in decoder.parameters())) == 2 * 8 * 8 + 2
    module_source = (ROOT / "tools" / "ssl_task.py").read_text(encoding="utf-8")
    assert "nn.Embedding" not in module_source
    assert "per_node_parameters" in module_source


def test_loss_de_peso_conferida_a_mao():
    decoder = sd.BilinearDecoder(3)
    with torch.no_grad():
        decoder.existence.zero_()
        decoder.weight.zero_()
        decoder.bias_existence.zero_()
        decoder.bias_weight.zero_()
    left = torch.zeros(2, 3)
    right = torch.zeros(2, 3)
    positive_weight = torch.tensor([0.0, np.expm1(1.0)])
    negative_left = torch.zeros(1, 3)
    negative_right = torch.zeros(1, 3)
    parts = sd.masked_edge_weight_loss(decoder, left, right, positive_weight, negative_left, negative_right)
    assert float(parts["existence"].detach()) == pytest.approx(float(np.log(2.0)), abs=1e-6)
    expected_weight = ((0.0 - 0.0) ** 2 + (0.0 - 1.0) ** 2) / 2
    assert float(parts["weight"].detach()) == pytest.approx(expected_weight, abs=1e-6)
    assert float(parts["loss"].detach()) == pytest.approx(float(parts["existence"].detach()) + expected_weight, abs=1e-6)


def test_smoke_do_decoder_converge():
    smoke = sd.decoder_smoke(dim=8, steps=40, seed=3)
    assert smoke["gradients_finite"] and smoke["loss_decreased"]
    assert smoke["per_node_parameters"] == 0
    assert smoke["parameters"] == 2 * 8 * 8 + 2


def test_run_em_fixture_e_check(tmp_path):
    write_snapshot(tmp_path / "snap", fixture_edges())
    report = st.run(
        tmp_path / "work",
        tmp_path / "report.json",
        audit_positives=6,
        k=2,
        train_pairs=6,
        snapshot=tmp_path / "snap",
    )
    assert report["schema"] == st.SCHEMA
    assert "sem nenhum dado do alvo" in report["status"]
    assert report["mask"]["validation_edges"] > 0
    assert report["separation"]["leaks"] == 0
    assert 0 < report["negatives"]["negatives_total"] <= 12
    assert report["negatives"]["shortfall_positives"] >= 0
    assert 0.0 <= report["shortcut_degree_baseline"]["validation_matched"]["auc"] <= 1.0
    assert report["decoder_smoke"]["loss_decreased"]
    assert st.check_report(tmp_path / "report.json") == []


@pytest.mark.skipif(not REPORT.exists(), reason="smoke M01 ainda não executado")
def test_check_report_real_passa():
    assert st.check_report(REPORT) == []


@pytest.mark.skipif(not REPORT.exists(), reason="smoke M01 ainda não executado")
def test_check_report_detecta_desonestidade(tmp_path):
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    broken = copy.deepcopy(report)
    broken["separation"]["held_out_absent_from_train_view"] = False
    path = tmp_path / "leak.json"
    path.write_text(json.dumps(broken), encoding="utf-8")
    assert any("holdout" in failure for failure in st.check_report(path))
    corrupted = copy.deepcopy(report)
    corrupted["mask"]["reverse_co_masking"] = False
    path = tmp_path / "noreverse.json"
    path.write_text(json.dumps(corrupted), encoding="utf-8")
    assert any("reverso" in failure for failure in st.check_report(path))
    wrong = copy.deepcopy(report)
    wrong["task"]["weight_transform"] = "raw"
    path = tmp_path / "weight.json"
    path.write_text(json.dumps(wrong), encoding="utf-8")
    assert any("peso" in failure for failure in st.check_report(path))
    node_table = copy.deepcopy(report)
    node_table["decoder_smoke"]["per_node_parameters"] = 10
    path = tmp_path / "node.json"
    path.write_text(json.dumps(node_table), encoding="utf-8")
    assert any("node" in failure for failure in st.check_report(path))


def test_sem_referencias_proibidas():
    source = (ROOT / "tools" / "ssl_task.py").read_text(encoding="utf-8")
    for token in ("male-cns", "data/sealed", "target_labels", "crosswalk"):
        assert token not in source
    assert st.WEIGHT_TRANSFORM == "log1p"
    assert "Macro Recall@1" in st.SELECTION_METRIC
