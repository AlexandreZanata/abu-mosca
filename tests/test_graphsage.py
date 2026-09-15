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
import gnn_graphsage as gg  # noqa: E402
import opaque_ids  # noqa: E402
import ssl_decoder as sd  # noqa: E402
import topology_features as tf  # noqa: E402

REPORT = ROOT / "artifacts" / "reports" / "M02-GRAPHSAGE.json"


def ring_graph(n: int = 24, seed: int = 3):
    rng = np.random.RandomState(seed)
    edges = []
    for node in range(n):
        edges.append((node, (node + 1) % n, 1.0 + rng.rand()))
        edges.append(((node + 1) % n, node, 1.0 + rng.rand()))
    for _ in range(n):
        a, b = rng.randint(0, n, size=2)
        if a != b:
            edges.append((int(a), int(b), 1.0))
    src = np.asarray([edge[0] for edge in edges], dtype=np.int64)
    dst = np.asarray([edge[1] for edge in edges], dtype=np.int64)
    weight = np.asarray([edge[2] for edge in edges], dtype=np.float64)
    features = rng.randn(n, len(gg.FEATURE_NAMES)).astype(np.float32)
    return src, dst, weight, features


def test_contagem_exata_e_independente_do_grafo():
    for dim, layers in ((16, 1), (64, 2), (128, 3)):
        config = gg.EncoderConfig(dim=dim, layers=layers, fanout=(5,) * layers)
        encoder = gg.build_encoder(config)
        assert gg.encoder_parameter_count(encoder) == gg.parameter_count_formula(config)
        extra = (config.input_dim * dim + dim) + (layers - 1) * (dim * dim + dim)
        assert gg.parameter_count_formula(config) == gg.parameter_count_two_projections(config) + extra
    assert gg.parameter_count_formula(gg.EncoderConfig(dim=576, layers=2, fanout=(10, 10))) == 1009152


def test_sem_parametros_por_node():
    encoder = gg.build_encoder(gg.EncoderConfig(dim=32, layers=2, fanout=(5, 5)))
    keys = " ".join(encoder.state_dict().keys())
    assert "nodes" not in keys and "embedding" not in keys.lower()
    source = (ROOT / "tools" / "gnn_graphsage.py").read_text(encoding="utf-8")
    assert "nn.Embedding" not in source
    assert "toarray(" not in source and "todense" not in source


def test_shapes_e_gradientes():
    src, dst, weight, features = ring_graph()
    n_nodes = features.shape[0]
    config = gg.EncoderConfig(dim=16, layers=2, fanout=(n_nodes, n_nodes))
    encoder = gg.build_encoder(config)
    decoder = sd.BilinearDecoder(config.dim)
    in_edges = gg.csr_edges(gg.build_direction_csr(src, dst, weight, n_nodes, "in"))
    out_edges = gg.csr_edges(gg.build_direction_csr(src, dst, weight, n_nodes, "out"))
    embeddings = gg.forward_full(encoder, features, in_edges, out_edges, training=True)
    assert embeddings.shape == (n_nodes, config.dim)
    positive_weight = torch.from_numpy(weight[:8].astype(np.float32))
    parts = sd.masked_edge_weight_loss(decoder, embeddings[src[:8]], embeddings[dst[:8]], positive_weight, embeddings[src[:8]], embeddings[dst[8:16]])
    parts["loss"].backward()
    for parameter in list(encoder.parameters()) + list(decoder.parameters()):
        assert parameter.grad is not None and torch.isfinite(parameter.grad).all()


def test_forward_sampled_igual_ao_full_com_fanout_completo():
    src, dst, weight, features = ring_graph()
    n_nodes = features.shape[0]
    config = gg.EncoderConfig(dim=16, layers=2, fanout=(n_nodes, n_nodes), dropout=0.0)
    encoder = gg.build_encoder(config)
    encoder.eval()
    in_csr = gg.build_direction_csr(src, dst, weight, n_nodes, "in")
    out_csr = gg.build_direction_csr(src, dst, weight, n_nodes, "out")
    targets = np.asarray([0, 3, 7, 11], dtype=np.int64)
    subgraph = gg.sample_subgraph(targets, in_csr, out_csr, config.fanout, 11)
    sampled = gg.forward_sampled(encoder, features, subgraph)
    full = gg.forward_full(encoder, features, gg.csr_edges(in_csr), gg.csr_edges(out_csr))
    np.testing.assert_allclose(sampled.detach().numpy(), full[targets].detach().numpy(), atol=1e-5)
    assert subgraph["sampled_nodes"] >= len(targets)


def test_sampler_respeita_fanout():
    src, dst, weight, features = ring_graph(n=30)
    n_nodes = features.shape[0]
    fanout = (2, 3)
    in_csr = gg.build_direction_csr(src, dst, weight, n_nodes, "in")
    out_csr = gg.build_direction_csr(src, dst, weight, n_nodes, "out")
    targets = np.asarray([1, 5, 9], dtype=np.int64)
    subgraph = gg.sample_subgraph(targets, in_csr, out_csr, fanout, 5)
    for depth, (edges, frontier_size) in enumerate(zip(subgraph["edges_per_layer"], subgraph["frontier_sizes"])):
        assert edges <= 2 * fanout[depth] * frontier_size
    assert len(subgraph["targets_local"]) == len(set(targets.tolist())) == len(targets)
    assert sorted(subgraph["nodes"][subgraph["targets_local"]].tolist()) == sorted(targets.tolist())
    assert np.all(np.asarray(subgraph["in_edges"][2]) > 0)


def test_determinismo_e_serializacao(tmp_path):
    src, dst, weight, features = ring_graph()
    n_nodes = features.shape[0]
    config = gg.EncoderConfig(dim=16, layers=2, fanout=(n_nodes, n_nodes))
    in_edges = gg.csr_edges(gg.build_direction_csr(src, dst, weight, n_nodes, "in"))
    out_edges = gg.csr_edges(gg.build_direction_csr(src, dst, weight, n_nodes, "out"))
    torch.manual_seed(7)
    first = gg.build_encoder(config)
    torch.manual_seed(7)
    second = gg.build_encoder(config)
    first_embeddings = gg.forward_full(first, features, in_edges, out_edges)
    second_embeddings = gg.forward_full(second, features, in_edges, out_edges)
    assert np.array_equal(first_embeddings.detach().numpy(), second_embeddings.detach().numpy())
    path = tmp_path / "encoder.pt"
    gg.save_encoder(path, first, config)
    reloaded, reloaded_config = gg.load_encoder(path)
    assert reloaded_config == config
    restored = gg.forward_full(reloaded, features, in_edges, out_edges)
    assert float((first_embeddings - restored).abs().max()) <= 1e-6


def test_inferencia_em_grafo_novo_e_permutacao():
    src_a, dst_a, weight_a, features_a = ring_graph(n=20, seed=1)
    src_b, dst_b, weight_b, features_b = ring_graph(n=37, seed=2)
    config = gg.EncoderConfig(dim=12, layers=2, fanout=(37, 37))
    encoder = gg.build_encoder(config)
    edges_a = (gg.csr_edges(gg.build_direction_csr(src_a, dst_a, weight_a, 20, "in")), gg.csr_edges(gg.build_direction_csr(src_a, dst_a, weight_a, 20, "out")))
    edges_b = (gg.csr_edges(gg.build_direction_csr(src_b, dst_b, weight_b, 37, "in")), gg.csr_edges(gg.build_direction_csr(src_b, dst_b, weight_b, 37, "out")))
    torch.manual_seed(4)
    trained = gg.build_encoder(config)
    gg.forward_full(trained, features_a, edges_a[0], edges_a[1])
    embeddings_b = gg.forward_full(trained, features_b, edges_b[0], edges_b[1])
    assert embeddings_b.shape == (37, config.dim)
    assert np.isfinite(embeddings_b.detach().numpy()).all()
    permutation = np.random.RandomState(9).permutation(37)
    inverse = np.argsort(permutation)
    src_p = permutation[src_b]
    dst_p = permutation[dst_b]
    features_p = features_b[inverse]
    edges_p = (gg.csr_edges(gg.build_direction_csr(src_p, dst_p, weight_b, 37, "in")), gg.csr_edges(gg.build_direction_csr(src_p, dst_p, weight_b, 37, "out")))
    permuted_embeddings = gg.forward_full(trained, features_p, edges_p[0], edges_p[1])
    np.testing.assert_allclose(permuted_embeddings.detach().numpy(), embeddings_b.detach().numpy()[inverse], atol=1e-4)


def test_overfit_controlado_de_tiny_graph():
    result = gg._train_fixture(seed=gg.MASTER_SEED)
    assert result["auc_train"] >= 0.95
    assert result["loss_last"] < 0.5 * result["loss_first"]
    assert result["gradients_finite"]
    assert result["encoder_parameters"] == result["parameters_formula"]


def _graph_dict_from_snapshot(directory: Path, edges):
    labels = sorted({value for edge in edges for value in edge[:2]})
    ids = [opaque_ids.opaque_node_id("MANC", "manc:v1.2.1", label) for label in labels]
    directory.mkdir(parents=True, exist_ok=True)
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
    graph = {
        "provenance": {"created_at": "2026-09-15"},
        "nodes": [{"id": node_id, "attributes": {}} for node_id in ids],
        "edges": [
            {"source": ids[index[pre]], "target": ids[index[post]], "weight": float(weight)}
            for pre, post, weight in edges
        ],
    }
    return graph


def test_snapshot_features_equivalentes_h05(tmp_path):
    edges = [(0, 1, 3), (1, 2, 2), (2, 0, 5), (0, 0, 4), (3, 1, 1)]
    graph = _graph_dict_from_snapshot(tmp_path / "snap", edges)
    _, matrix = gg.snapshot_features(tmp_path / "snap")
    _, reference = tf.raw_features(graph)
    np.testing.assert_allclose(np.asarray(matrix, dtype=float), np.asarray(reference, dtype=float), atol=1e-9)


def test_orcamento_emendado_dentro_do_intervalo():
    grid = gg.grid_parameter_counts()
    values = [row["parameters"] for row in grid]
    assert len(grid) == 12
    assert gg.MVP_RANGE[0] <= min(values) and max(values) <= gg.MVP_RANGE[1]
    assert all(row["dim"] in (408, 576) for row in grid)
    assert "R07" in gg.GRID_AMENDMENT and "2026-" in gg.GRID_AMENDMENT
    capacity = gg.capacity_table()
    assert any(row["meets_mvp_range"] for row in capacity)
    smallest = gg.smallest_dims_for_range()
    assert smallest and all(row["parameters"] >= gg.MVP_RANGE[0] for row in smallest)
    assert gg.parameter_count_formula(gg.EncoderConfig(dim=smallest[0]["dim"], layers=smallest[0]["layers"], fanout=(10,) * smallest[0]["layers"])) == smallest[0]["parameters"]


@pytest.mark.skipif(not REPORT.exists(), reason="smoke M02 ainda não executado")
def test_check_report_real_passa():
    assert gg.check_report(REPORT) == []


@pytest.mark.skipif(not REPORT.exists(), reason="smoke M02 ainda não executado")
def test_check_report_detecta_desonestidade(tmp_path):
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    wrong_params = copy.deepcopy(report)
    wrong_params["parameter_budget"]["grid_rows"][0]["parameters"] += 1
    path = tmp_path / "params.json"
    path.write_text(json.dumps(wrong_params), encoding="utf-8")
    assert any("contagem" in failure for failure in gg.check_report(path))
    node_table = copy.deepcopy(report)
    node_table["config"]["per_node_parameters"] = 10
    path = tmp_path / "node.json"
    path.write_text(json.dumps(node_table), encoding="utf-8")
    assert any("parâmetros por node" in failure for failure in gg.check_report(path))
    weak = copy.deepcopy(report)
    weak["fixture_smoke"]["overfit_train_auc"] = 0.5
    path = tmp_path / "overfit.json"
    path.write_text(json.dumps(weak), encoding="utf-8")
    assert any("overfit" in failure for failure in gg.check_report(path))
    dense = copy.deepcopy(report)
    dense["real_graph_smoke"]["sparse_bytes"] = dense["real_graph_smoke"]["dense_equivalent_bytes"]
    path = tmp_path / "dense.json"
    path.write_text(json.dumps(dense), encoding="utf-8")
    assert any("esparsa" in failure for failure in gg.check_report(path))
    no_amendment = copy.deepcopy(report)
    no_amendment["resolution"]["amendment"] = "sem emenda registrada"
    path = tmp_path / "amendment.json"
    path.write_text(json.dumps(no_amendment), encoding="utf-8")
    assert any("emenda do grid" in failure for failure in gg.check_report(path))
    blocked = copy.deepcopy(report)
    blocked["blocking_issue"] = {"present": True, "summary": "grid antigo", "options": [], "decision_required_from": "x"}
    path = tmp_path / "blocked.json"
    path.write_text(json.dumps(blocked), encoding="utf-8")
    assert any("bloqueio" in failure for failure in gg.check_report(path))


def test_sem_referencias_proibidas():
    source = (ROOT / "tools" / "gnn_graphsage.py").read_text(encoding="utf-8")
    for token in ("male-cns", "data/sealed", "target_labels", "crosswalk"):
        assert token not in source
    assert gg.MVP_RANGE == (1_000_000, 3_000_000)
    assert "repete o" in gg.FANOUT_CONVENTION
