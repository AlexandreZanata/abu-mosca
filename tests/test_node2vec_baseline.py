import json
import sys
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.feather as feather
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import baselines_source as bs  # noqa: E402
import metrics  # noqa: E402
import node2vec_baseline as nv  # noqa: E402
import opaque_ids  # noqa: E402


def tiny_graph():
    # 6 nós dirigidos com ramificação: 0 -> {1, 2}, 1 -> {3}, 2 -> {3}, 3 -> {4, 5}, 4 -> {5}
    pre = [0, 0, 1, 2, 3, 3, 4]
    post = [1, 2, 3, 3, 4, 5, 5]
    n = 6
    bounds = np.zeros(n + 1, dtype=np.int64)
    for s in pre:
        bounds[s + 1] += 1
    bounds = np.cumsum(bounds)
    nbr = np.asarray(post, dtype=np.int32)
    wgt = np.asarray([3.0, 1.0, 2.0, 2.0, 1.0, 4.0, 5.0], dtype=np.float64)
    cum = np.empty_like(wgt)
    total = np.zeros(n)
    for node in range(n):
        lo, hi = int(bounds[node]), int(bounds[node + 1])
        if hi > lo:
            cum[lo:hi] = np.cumsum(wgt[lo:hi])
            total[node] = cum[hi - 1]
    return bounds, nbr, wgt, cum, total, n


def test_pesos_enviesados_exatos():
    cand = np.asarray([0, 1, 2], dtype=np.int32)
    wgt = np.asarray([2.0, 2.0, 2.0], dtype=np.float32)
    prev_nbr = np.asarray([1, 4], dtype=np.int32)
    out = nv.biased_weights(cand, wgt, 0, prev_nbr, 2.0, 0.5)
    assert list(out) == [2.0 / 2.0, 2.0, 2.0 / 0.5]
    plain = nv.biased_weights(cand, wgt, 0, prev_nbr, 1.0, 1.0)
    assert list(plain) == [2.0, 2.0, 2.0]


def test_caminhadas_deterministicas_mesma_seed():
    bounds, nbr, wgt, cum, total, n = tiny_graph()
    first = nv.random_walks(bounds, nbr, wgt, cum, total, n, 3, 8, 1.0, 0.5, np.random.RandomState(11))
    second = nv.random_walks(bounds, nbr, wgt, cum, total, n, 3, 8, 1.0, 0.5, np.random.RandomState(11))
    assert len(first) == len(second) == n * 3
    for a, b in zip(first, second):
        assert np.array_equal(a, b)
    third = nv.random_walks(bounds, nbr, wgt, cum, total, n, 3, 8, 1.0, 0.5, np.random.RandomState(12))
    assert any(not np.array_equal(a, b) for a, b in zip(first, third))


def test_pares_cobrem_janela():
    walks = [np.asarray([0, 1, 2, 3], dtype=np.int32)]
    centers, contexts, tokens = nv.build_pairs(walks, 2)
    assert len(centers) == len(contexts) == 2 * (3 + 2)
    assert set(zip(centers.tolist(), contexts.tolist())) >= {(0, 1), (1, 0), (2, 3), (3, 2)}
    assert list(tokens) == [0, 1, 2, 3]


def test_probe_invariante_a_rotacao():
    rng = np.random.RandomState(3)
    train = np.vstack([rng.randn(10, 6) + 5.0, rng.randn(10, 6) - 5.0])
    val = np.vstack([rng.randn(4, 6) + 5.0, rng.randn(4, 6) - 5.0])
    train_labels = {f"t{i}": ("A" if i < 10 else "B") for i in range(20)}
    val_labels = {f"v{i}": ("A" if i < 4 else "B") for i in range(8)}
    order = {node: i for i, node in enumerate(list(train_labels) + list(val_labels))}
    full = np.vstack([train, val])
    classes = ["A", "B"]
    base = nv.probe_embeddings(full, order, train_labels, val_labels, classes)
    rot = nv.random_orthogonal(6, 99)
    turned = nv.probe_embeddings(full @ rot, order, train_labels, val_labels, classes)
    assert base == turned
    ranked = {node: [base[node]] for node in val_labels}
    assert metrics.evaluate(ranked, val_labels, k_values=(1,))["recall"]["@1"]["macro"] == 1.0


def write_cluster_fixture(directory: Path, shuffle: bool = False):
    import random as pyrandom

    bodies = [f"c{i}" for i in range(20)]
    ids = [opaque_ids.opaque_node_id("MANC", "manc:v1.2.1", b) for b in bodies]
    pairs = []
    for i in range(9):
        pairs.append((i, i + 1))
        pairs.append((10 + i, 10 + i + 1))
    pairs += [(9, 0), (19, 10), (4, 14), (14, 4)]
    rows = list(range(len(ids)))
    if shuffle:
        pyrandom.Random(5).shuffle(rows)
    directory.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.table({"id": pa.array([ids[i] for i in rows])}), directory / "nodes.parquet")
    pq.write_table(
        pa.table(
            {
                "source": pa.array([ids[a] for a, _ in pairs]),
                "target": pa.array([ids[b] for _, b in pairs]),
                "weight": pa.array([2] * len(pairs), type=pa.int64()),
            }
        ),
        directory / "edges.parquet",
    )
    return bodies


def test_invariancia_a_ordem_da_tabela(tmp_path):
    first = write_cluster_fixture(tmp_path / "a")
    write_cluster_fixture(tmp_path / "b", shuffle=True)
    assert first is not None
    ids_a, ba, na, wa, ca, ta = nv.load_directed_graph(tmp_path / "a")
    ids_b, bb, nb, wb, cb, tb = nv.load_directed_graph(tmp_path / "b")
    assert ids_a == ids_b
    assert np.array_equal(ba, bb) and np.array_equal(na, nb) and np.array_equal(wa, wb)
    assert np.array_equal(ca, cb) and np.array_equal(ta, tb)


def test_seed_muda_coordenadas_mas_nao_o_protocolo(tmp_path):
    bodies = write_cluster_fixture(tmp_path / "snap")
    properties = tmp_path / "properties.feather"
    feather.write_feather(
        pa.table({"bodyId": pa.array(bodies, type=pa.string()), "type": pa.array(["X"] * 10 + ["Y"] * 10)}),
        properties,
    )
    kwargs = dict(configs=("deepwalk",), walks_per_node=2, walk_length=8, window=2, dim=8, epochs=2, batch=8)
    rep_a = nv.run(tmp_path / "snap", properties, tmp_path / "outa", tmp_path / "ra.json", seeds=(11,), **kwargs)
    rep_b = nv.run(tmp_path / "snap", properties, tmp_path / "outb", tmp_path / "rb.json", seeds=(12,), **kwargs)
    emb_a = np.load(tmp_path / "outa" / "embeddings-deepwalk-seed0.npy")
    emb_b = np.load(tmp_path / "outb" / "embeddings-deepwalk-seed0.npy")
    assert emb_a.shape == emb_b.shape == (20, 8)
    assert abs(nv.mean_cosine(emb_a, emb_b)) < 0.5
    for rep in (rep_a, rep_b):
        value = rep["results"]["deepwalk"]["per_seed"][0]["macro_recall@1"]
        assert 0.0 <= value <= 1.0


def test_run_deterministico_mesma_seed(tmp_path):
    bodies = write_cluster_fixture(tmp_path / "snap")
    properties = tmp_path / "properties.feather"
    feather.write_feather(
        pa.table({"bodyId": pa.array(bodies, type=pa.string()), "type": pa.array(["X"] * 10 + ["Y"] * 10)}),
        properties,
    )
    kwargs = dict(configs=("node2vec",), walks_per_node=2, walk_length=8, window=2, dim=8, epochs=2, batch=8)
    nv.run(tmp_path / "snap", properties, tmp_path / "outa", tmp_path / "ra.json", seeds=(21,), **kwargs)
    nv.run(tmp_path / "snap", properties, tmp_path / "outb", tmp_path / "rb.json", seeds=(21,), **kwargs)
    a = json.loads((tmp_path / "outa" / "predictions-node2vec-seed0.json").read_text(encoding="utf-8"))
    b = json.loads((tmp_path / "outb" / "predictions-node2vec-seed0.json").read_text(encoding="utf-8"))
    assert a == b
    assert np.array_equal(
        np.load(tmp_path / "outa" / "embeddings-node2vec-seed0.npy"),
        np.load(tmp_path / "outb" / "embeddings-node2vec-seed0.npy"),
    )


def test_smoke_ponta_a_ponta(tmp_path):
    bodies = write_cluster_fixture(tmp_path / "snap")
    properties = tmp_path / "properties.feather"
    feather.write_feather(
        pa.table({"bodyId": pa.array(bodies, type=pa.string()), "type": pa.array(["X"] * 10 + ["Y"] * 10)}),
        properties,
    )
    report = nv.run(
        tmp_path / "snap", properties, tmp_path / "out", tmp_path / "report.json",
        configs=("deepwalk",), seeds=(bs.SELECTION_SEEDS[0],),
        walks_per_node=2, walk_length=8, window=2, dim=8, epochs=1, batch=8,
    )
    assert report["schema"] == "b06-node2vec"
    assert report["verdict"] == "não comparável zero-shot"
    assert set(report["results"]) == {"deepwalk"}
    value = report["results"]["deepwalk"]["per_seed"][0]["macro_recall@1"]
    assert 0.0 <= value <= 1.0
    # Rotação preserva distâncias em aritmética exata; em ponto flutuante,
    # empates próximos em 4 nós de validação podem virar (granularidade 0,25).
    # A invariância exata está coberta em test_probe_invariante_a_rotacao.
    assert report["results"]["deepwalk"]["rotation_agreement"] >= 0.75
    assert len(report["predictions"]) == 1
    assert len(report["predictions"][0]["sha256"]) == 64
    assert (tmp_path / "out" / "embeddings-deepwalk-seed0.npy").exists()
    assert json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))["schema"] == "b06-node2vec"


def test_sem_referencias_proibidas_e_configs_fixas():
    source = (ROOT / "tools" / "node2vec_baseline.py").read_text(encoding="utf-8")
    for token in ("data/sealed", "target_labels", "crosswalk"):
        assert token not in source
    assert "male-cns" not in source
    assert set(nv.CONFIGS) == {"deepwalk", "node2vec"}
    assert nv.CONFIGS["deepwalk"] == {"p": 1.0, "q": 1.0}
