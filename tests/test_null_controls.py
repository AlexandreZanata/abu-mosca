import copy
import json
import random
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
import artisanal_features as af  # noqa: E402
import baselines_source as bs  # noqa: E402
import null_controls as nc  # noqa: E402
import opaque_ids  # noqa: E402

REPORT = ROOT / "artifacts" / "reports" / "B09-CONTROLES.json"
MANIFEST = ROOT / "data" / "manifests" / "baselines-b09.json"


def test_permutacao_de_rotulos_preserva_contagens_e_split():
    train = {f"t{i}": ("A" if i < 6 else "B" if i < 10 else "C") for i in range(12)}
    val = {f"v{i}": ("A" if i < 3 else "B" if i < 5 else "C") for i in range(6)}
    train_p, val_p = nc.permute_labels_within_split(train, val, 12345)
    assert set(train_p) == set(train) and set(val_p) == set(val)
    assert Counter(train_p.values()) == Counter(train.values())
    assert Counter(val_p.values()) == Counter(val.values())
    again = nc.permute_labels_within_split(train, val, 12345)
    assert again[0] == train_p and again[1] == val_p
    different = nc.permute_labels_within_split(train, val, 999)
    assert different[0] != train_p


def test_rewire_preserva_graus_e_invariantes():
    src = np.asarray([0, 1, 2, 3, 4, 0, 2], dtype=np.int64)
    dst = np.asarray([1, 2, 3, 4, 0, 0, 2], dtype=np.int64)
    n = 5
    degree_in = np.bincount(dst, minlength=n)
    degree_out = np.bincount(src, minlength=n)
    self_loops_before = int(np.sum(src == dst))
    rewired_src, rewired_dst, stats = nc.rewire_directed(src, dst, n, 40, 7)
    assert stats["accepted"] == 40
    assert np.array_equal(np.bincount(rewired_dst, minlength=n), degree_in)
    assert np.array_equal(np.bincount(rewired_src, minlength=n), degree_out)
    assert len(rewired_src) == len(src)
    assert int(np.sum(rewired_src == rewired_dst)) == self_loops_before
    assert len(set(zip(rewired_src.tolist(), rewired_dst.tolist()))) == len(set(zip(src.tolist(), dst.tolist())))
    again = nc.rewire_directed(src, dst, n, 40, 7)
    assert np.array_equal(again[0], rewired_src) and np.array_equal(again[1], rewired_dst)


def make_inputs(tmp_path: Path):
    bodies = [f"b{i}" for i in range(40)]
    ids = [opaque_ids.opaque_node_id(bs.DATASET, bs.RELEASE, body) for body in bodies]
    snapshot = tmp_path / "snap"
    snapshot.mkdir(parents=True, exist_ok=True)
    pq.write_table(
        pa.table({"id": pa.array(ids), "degree_in": pa.array([1] * 40), "degree_out": pa.array([1] * 40)}),
        snapshot / "nodes.parquet",
    )
    pre = [ids[i] for i in range(39)] + [ids[0]]
    post = [ids[i + 1] for i in range(39)] + [ids[0]]
    pq.write_table(
        pa.table({"source": pa.array(pre), "target": pa.array(post), "weight": pa.array([2] * 40, type=pa.int64())}),
        snapshot / "edges.parquet",
    )
    properties = tmp_path / "properties.feather"
    feather.write_feather(
        pa.table(
            {
                "bodyId": pa.array(bodies, type=pa.string()),
                "type": pa.array([f"T{i % 4}" for i in range(40)]),
            }
        ),
        properties,
    )
    return snapshot, properties


def test_permutacao_de_ids_preserva_rotulos(tmp_path):
    snapshot, properties = make_inputs(tmp_path)
    info = nc.permute_node_ids(snapshot, properties, tmp_path / "permuted", tmp_path / "permuted-properties.feather", 4242, tmp_path / "permutation.npy")
    assert info["labels_checked"] == 40
    assert info["labels_follow_permutation"] is True
    assert info["nodes"] == 40 and info["edges"] == 40
    assert len(str(info["permutation_sha256"])) == 64
    assert (tmp_path / "permutation.npy").exists()
    original = json.dumps(feather.read_table(properties)["type"].to_pylist())
    permuted = json.dumps(feather.read_table(tmp_path / "permuted-properties.feather")["type"].to_pylist())
    assert original == permuted  # tipos preservados linha a linha; só bodyId muda


def test_negativos_pareados_por_grau_sao_deterministicos():
    n_nodes = 60
    degree = np.tile(np.arange(0, 12), 5).astype(float)
    matrix = np.zeros((n_nodes, len(af.FEATURE_ORDER)))
    for column, name in enumerate(af.FEATURE_ORDER):
        if name == "in_degree":
            matrix[:, column] = np.arange(n_nodes) % 11
        elif name == "out_degree":
            matrix[:, column] = np.arange(n_nodes) // 11
        elif name == "weighted_in":
            matrix[:, column] = degree
        else:
            matrix[:, column] = degree / 2.0
    order = {f"n{i}": i for i in range(n_nodes)}
    train = {f"n{i}": f"C{i % 6}" for i in range(0, 40)}
    val = {f"n{i}": f"C{i % 6}" for i in range(40, 60)}
    classes = sorted(set(train.values()))
    columns = list(range(matrix.shape[1]))
    first = nc.degree_matched_negatives(matrix, order, train, val, classes, columns, 3, 11, "fine")
    second = nc.degree_matched_negatives(matrix, order, train, val, classes, columns, 3, 11, "fine")
    assert first == second
    assert first["matching"] == "fine"
    assert 0.0 <= first["hit_rate"] <= 1.0
    assert first["queries"] == 20
    assert first["negatives_per_query"] == 3
    assert first["chance"] == pytest.approx(0.25)
    coarse = nc.degree_matched_negatives(matrix, order, train, val, classes, columns, 3, 11, "coarse")
    none = nc.degree_matched_negatives(matrix, order, train, val, classes, columns, 3, 11, "none")
    for entry in (coarse, none):
        assert 0.0 <= entry["hit_rate"] <= 1.0
        assert entry["queries"] == 20


def test_pacote_congelado_respeita_regra():
    package = nc.frozen_package()
    assert package["schema"] == "b09-baseline-package"
    assert package["target_data_used"] is False
    assert len(package["ranking"]) >= 8
    assert package["best_comparator"] == "MLP pareado 1-3M"
    assert package["best_classical"] == "artesanal (todas)"
    assert package["predictions"]
    assert all(entry["status"] == "ok" for entry in package["predictions"])
    assert all(len(entry["report_sha256"]) == 64 for entry in package["ranking"])


@pytest.mark.skipif(not REPORT.exists() or not MANIFEST.exists(), reason="controles B09 ainda não executados")
def test_check_report_real_passa():
    assert nc.check_report(REPORT, MANIFEST) == []


@pytest.mark.skipif(not REPORT.exists() or not MANIFEST.exists(), reason="controles B09 ainda não executados")
def test_check_report_detecta_desonestidade(tmp_path):
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    corrupted = copy.deepcopy(report)
    corrupted["controls"]["label_permutation"]["all_features"]["null_max"] = 0.99
    path = tmp_path / "wrong-null.json"
    path.write_text(json.dumps(corrupted), encoding="utf-8")
    assert any("interpreta" in failure for failure in nc.check_report(path, MANIFEST))
    broken = copy.deepcopy(report)
    broken["pending_investigation"] = ["controle-inexistente"]
    path = tmp_path / "pending.json"
    path.write_text(json.dumps(broken), encoding="utf-8")
    assert any("pending" in failure for failure in nc.check_report(path, MANIFEST))
    rewired = copy.deepcopy(report)
    rewired["controls"]["degree_preserving_rewiring"]["stats"]["accepted"] = 1
    path = tmp_path / "trivial.json"
    path.write_text(json.dumps(rewired), encoding="utf-8")
    assert any("trocas declaradas" in failure for failure in nc.check_report(path, MANIFEST))
    identity = copy.deepcopy(report)
    identity["controls"]["id_permutation"]["carried_split_macro_recall@1"] = 0.99
    path = tmp_path / "identity.json"
    path.write_text(json.dumps(identity), encoding="utf-8")
    assert any("partição carregada" in failure for failure in nc.check_report(path, MANIFEST))
    altered = copy.deepcopy(manifest)
    altered["predictions"][0]["status"] = "divergente"
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(altered), encoding="utf-8")
    assert any("artefato congelado" in failure for failure in nc.check_report(REPORT, manifest_path))


def test_sem_referencias_proibidas_e_seeds():
    source = (ROOT / "tools" / "null_controls.py").read_text(encoding="utf-8")
    for token in ("male-cns", "data/sealed", "target_labels", "crosswalk"):
        assert token not in source
    assert nc.MASTER_SEED == 20260914
    assert random is not None
