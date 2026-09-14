import json
import sys
import time
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.feather as feather
import pyarrow.parquet as pq
import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import artisanal_features as af  # noqa: E402
import baselines_source as bs  # noqa: E402
import metrics  # noqa: E402
import mlp_control as mc  # noqa: E402
import opaque_ids  # noqa: E402


def blobs(n_per_class=20, seed=7):
    rng = np.random.RandomState(seed)
    centers = np.asarray([[-4.0] * 4, [0.0] * 4, [4.0] * 4])
    parts = [center + 0.5 * rng.randn(n_per_class, 4) for center in centers]
    matrix = np.vstack(parts)
    labels = np.asarray([0] * n_per_class + [1] * n_per_class + [2] * n_per_class)
    names = [["A", "B", "C"][i] for i in labels]
    return matrix, labels, names


def test_contagem_exata_de_parametros():
    for name, cfg in mc.CONFIGS.items():
        hidden = tuple(cfg["hidden"])
        model = mc.MLP(11, hidden, 519)
        assert mc.count_params(model) == mc.expected_params(11, hidden, 519), name
    tiny = mc.MLP(4, (8, 8), 3)
    assert mc.count_params(tiny) == (4 * 8 + 8) + (8 * 8 + 8) + (8 * 3 + 3)


def test_budgets_aproximados_e_pareado_no_intervalo():
    in_dim, classes = 11, 519
    small = mc.expected_params(in_dim, tuple(mc.CONFIGS["s"]["hidden"]), classes)
    medium = mc.expected_params(in_dim, tuple(mc.CONFIGS["m"]["hidden"]), classes)
    large = mc.expected_params(in_dim, tuple(mc.CONFIGS["l"]["hidden"]), classes)
    assert 80_000 <= small <= 130_000
    assert 400_000 <= medium <= 600_000
    assert 1_000_000 <= large <= 3_000_000


def test_smoke_em_fixture(tmp_path):
    matrix, labels, names = blobs()
    stats = mc.fit_stats(matrix[:45])
    train = mc.apply_stats(matrix[:45], stats)
    val = mc.apply_stats(matrix[45:], stats)
    started = time.perf_counter()
    model, n_params = mc.train_mlp(train, labels[:45], 3, (16, 16), int(bs.SELECTION_SEEDS[0]), epochs=5, batch=16)
    elapsed = time.perf_counter() - started
    assert n_params == mc.expected_params(4, (16, 16), 3)
    preds = mc.predict_mlp(model, val)
    assert len(preds) == 15
    ranked = {f"q{i}": [["A", "B", "C"][p]] for i, p in enumerate(preds)}
    truth = {f"q{i}": names[45 + i] for i in range(15)}
    evaluation = metrics.evaluate(ranked, truth, k_values=(1,))
    assert 0.0 <= evaluation["recall"]["@1"]["macro"] <= 1.0
    assert elapsed < 120


def test_overfit_em_fixture_separavel():
    matrix, labels, names = blobs()
    stats = mc.fit_stats(matrix)
    scaled = mc.apply_stats(matrix, stats)
    model, _ = mc.train_mlp(scaled, labels, 3, (64, 32), int(bs.SELECTION_SEEDS[1]), epochs=200, batch=16, lr=5e-3)
    preds = mc.predict_mlp(model, scaled)
    ranked = {f"q{i}": [["A", "B", "C"][p]] for i, p in enumerate(preds)}
    truth = {f"q{i}": name for i, name in enumerate(names)}
    evaluation = metrics.evaluate(ranked, truth, k_values=(1,))
    assert evaluation["recall"]["@1"]["macro"] >= 0.95


def test_determinismo_mesma_seed():
    matrix, labels, _ = blobs()
    stats = mc.fit_stats(matrix)
    scaled = mc.apply_stats(matrix, stats)
    first, _ = mc.train_mlp(scaled, labels, 3, (16, 16), 12345, epochs=10, batch=16)
    second, _ = mc.train_mlp(scaled, labels, 3, (16, 16), 12345, epochs=10, batch=16)
    assert mc.predict_mlp(first, scaled) == mc.predict_mlp(second, scaled)


def test_mesmas_features_e_source_fit():
    assert list(af.FEATURE_ORDER) == [
        "in_degree",
        "out_degree",
        "weighted_in",
        "weighted_out",
        "reciprocal_weight_ratio",
        "reciprocal_count_ratio",
        "clustering_undirected",
        "feedforward_paths",
        "bottleneck_ratio",
        "successor_out_degree_mean",
        "predecessor_in_degree_mean",
    ]
    source = (ROOT / "tools" / "mlp_control.py").read_text(encoding="utf-8")
    for token in ("data/sealed", "target_labels", "crosswalk"):
        assert token not in source
    assert "male-cns" not in source
    matrix, _, _ = blobs()
    stats = mc.fit_stats(matrix[:45])
    assert np.asarray(stats["mean"]).shape == (4,)
    assert all(v > 0 for v in stats["std"])


def write_source_fixture(directory: Path):
    bodies = [f"n{i}" for i in range(30)]
    ids = [opaque_ids.opaque_node_id("MANC", "manc:v1.2.1", b) for b in bodies]
    directory.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.table({"id": pa.array(ids)}), directory / "nodes.parquet")
    pre = [ids[i] for i in range(29)] + [ids[i] for i in range(1, 30)]
    post = [ids[i] for i in range(1, 30)] + [ids[i] for i in range(29)]
    pq.write_table(
        pa.table({"source": pa.array(pre), "target": pa.array(post), "weight": pa.array([2] * len(pre), type=pa.int64())}),
        directory / "edges.parquet",
    )
    return bodies


def test_run_minimo_ponta_a_ponta(tmp_path):
    bodies = write_source_fixture(tmp_path / "snap")
    properties = tmp_path / "properties.feather"
    feather.write_feather(
        pa.table(
            {
                "bodyId": pa.array(bodies, type=pa.string()),
                "type": pa.array(["X"] * 15 + ["Y"] * 15),
            }
        ),
        properties,
    )
    report = mc.run(
        tmp_path / "snap",
        properties,
        tmp_path / "out",
        tmp_path / "report.json",
        configs=("s",),
        seeds=(bs.SELECTION_SEEDS[0],),
        epochs=3,
        batch=16,
    )
    assert report["features"] == list(af.FEATURE_ORDER)
    assert report["seeds"] == [bs.SELECTION_SEEDS[0]]
    assert set(report["results"]) == {"s"}
    value = report["results"]["s"]["per_seed"][0]["macro_recall@1"]
    assert 0.0 <= value <= 1.0
    assert len(report["predictions"]) == 1
    assert len(report["predictions"][0]["sha256"]) == 64
    assert int(report["predictions"][0]["sha256"], 16) >= 0
    assert (tmp_path / "out" / "predictions-mlp-s-seed0.json").exists()
    assert torch.device(mc.DEVICE).type == "cpu"
    assert json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))["schema"] == "b05-mlp-control"
