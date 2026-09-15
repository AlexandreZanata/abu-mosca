import json
import random
import sys
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.feather as feather
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import baselines_source as bs  # noqa: E402
import opaque_ids  # noqa: E402
import spectral_baseline as sb  # noqa: E402


def test_matriz_esparsa_exata():
    src = np.asarray([0, 0, 2, 1], dtype=np.int64)
    dst = np.asarray([1, 1, 2, 2], dtype=np.int64)
    wgt = np.asarray([2.0, 3.0, 1.0, 0.0], dtype=np.float64)
    matrix = sb.build_directed_matrix(3, src, dst, wgt)
    assert matrix.shape == (3, 3)
    assert matrix.nnz == 3
    assert matrix[0, 1] == 5.0
    assert matrix[2, 2] == 1.0
    assert matrix[1, 2] == 0.0
    assert (matrix.data == 0).sum() == 1
    sparse_bytes = matrix.data.nbytes + matrix.indices.nbytes + matrix.indptr.nbytes
    assert sparse_bytes < 3 * 3 * 8


def test_esparsidade_em_grafo_maior():
    n = 200
    src = np.asarray([0, 1, 2, 3], dtype=np.int64)
    dst = np.asarray([1, 2, 3, 4], dtype=np.int64)
    wgt = np.asarray([1.0, 1.0, 1.0, 1.0], dtype=np.float64)
    matrix = sb.build_directed_matrix(n, src, dst, wgt)
    sparse_bytes = matrix.data.nbytes + matrix.indices.nbytes + matrix.indptr.nbytes
    dense_bytes = n * n * 8
    assert sparse_bytes < dense_bytes / 10


def test_svd_dirigido_espectro_conhecido():
    src = np.asarray([0, 1, 2], dtype=np.int64)
    dst = np.asarray([1, 2, 3], dtype=np.int64)
    wgt = np.asarray([3.0, 5.0, 7.0], dtype=np.float64)
    matrix = sb.build_directed_matrix(4, src, dst, wgt)
    embeddings, spectrum, seconds = sb.fit_directed_svd(matrix, 2, 12345)
    assert seconds >= 0.0
    assert list(np.round(spectrum, 8)) == [7.0, 5.0]
    expected = np.asarray(
        [
            [0.0, 0.0, 0.0, 0.0],
            [0.0, np.sqrt(5.0), 0.0, 0.0],
            [np.sqrt(7.0), 0.0, 0.0, np.sqrt(5.0)],
            [0.0, 0.0, np.sqrt(7.0), 0.0],
        ]
    )
    np.testing.assert_allclose(embeddings, expected, atol=1e-6)
    for column in range(embeddings.shape[1]):
        values = embeddings[:, column]
        pivot = int(np.argmax(np.abs(values)))
        assert values[pivot] >= 0


def test_ase_simetrizado_autovetor_conhecido():
    n = 8
    rows = []
    for i in range(n - 1):
        rows.append((i, i + 1, 1.0))
        rows.append((i + 1, i, 1.0))
    src = np.asarray([row[0] for row in rows], dtype=np.int64)
    dst = np.asarray([row[1] for row in rows], dtype=np.int64)
    wgt = np.asarray([row[2] for row in rows], dtype=np.float64)
    matrix = sb.build_directed_matrix(n, src, dst, wgt)
    embeddings, spectrum, _ = sb.fit_symmetric_ase(matrix, 2, 777)
    expected_lambda = 2.0 * np.cos(np.pi / (n + 1))
    second_lambda = 2.0 * np.cos(2.0 * np.pi / (n + 1))
    np.testing.assert_allclose(spectrum[0], expected_lambda, atol=1e-8)
    np.testing.assert_allclose(spectrum[1], second_lambda, atol=1e-8)
    expected_vector = np.sin(np.arange(1, n + 1) * np.pi / (n + 1))
    expected_vector /= np.linalg.norm(expected_vector)
    column = embeddings[:, 0] / np.sqrt(abs(expected_lambda))
    np.testing.assert_allclose(column, expected_vector, atol=1e-6)


def write_graph_fixture(directory: Path, edges, shuffle=False):
    names = sorted({value for edge in edges for value in edge[:2]})
    ids = [opaque_ids.opaque_node_id("MANC", "manc:v1.2.1", name) for name in names]
    positions = list(range(len(ids)))
    if shuffle:
        random.Random(3).shuffle(positions)
    directory.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.table({"id": pa.array([ids[index] for index in positions])}), directory / "nodes.parquet")
    rows = list(edges)
    if shuffle:
        random.Random(5).shuffle(rows)
    index_of = {name: position for position, name in enumerate(names)}
    pq.write_table(
        pa.table(
            {
                "source": pa.array([ids[index_of[pre]] for pre, _, _ in rows]),
                "target": pa.array([ids[index_of[post]] for _, post, _ in rows]),
                "weight": pa.array([weight for _, _, weight in rows], type=pa.int64()),
            }
        ),
        directory / "edges.parquet",
    )
    return {name: ids[index] for index, name in enumerate(names)}


def two_cliques():
    edges = []
    for clique in (range(10), range(10, 20)):
        for a in clique:
            for b in clique:
                if a != b:
                    edges.append((f"c{a}", f"c{b}", 1))
    return edges


def write_clique_inputs(tmp_path: Path, shuffle: bool = False):
    bodies = [f"c{i}" for i in range(20)]
    mapping = write_graph_fixture(tmp_path / "snap", two_cliques(), shuffle=shuffle)
    properties = tmp_path / "properties.feather"
    feather.write_feather(
        pa.table({"bodyId": pa.array(bodies, type=pa.string()), "type": pa.array(["X"] * 10 + ["Y"] * 10)}),
        properties,
    )
    return mapping, properties


def test_ambiguidade_controlada(tmp_path):
    _, properties = write_clique_inputs(tmp_path)
    report = sb.run(
        tmp_path / "snap",
        properties,
        tmp_path / "out",
        tmp_path / "report.json",
        configs=("svd_dirigido", "ase_simetrizado"),
        seeds=(bs.SELECTION_SEEDS[0],),
        n_components=2,
    )
    for name, data in report["results"].items():
        assert data["rotation_agreement_equivariant_probe"] == 1.0, name
        assert data["sign_agreement"] == 1.0, name
        assert 0.0 <= data["rotation_agreement_standard_probe"] <= 1.0, name
        for pair in data["subspace_cosines"].values():
            assert pair["min_cos"] >= 0.999 and pair["mean_cos"] >= 0.999, name
        assert data["median_macro_recall@1"] >= 0.95, name


def test_sem_densificacao_estatica():
    source = (ROOT / "tools" / "spectral_baseline.py").read_text(encoding="utf-8")
    for token in (".toarray(", ".todense(", "todense()", "asmatrix("):
        assert token not in source
    assert "spla.svds(" in source
    assert "spla.eigsh(" in source


def test_determinismo_mesma_seed(tmp_path):
    _, properties = write_clique_inputs(tmp_path)
    kwargs = dict(configs=("svd_dirigido",), seeds=(bs.SELECTION_SEEDS[1],), n_components=3)
    sb.run(tmp_path / "snap", properties, tmp_path / "outa", tmp_path / "ra.json", **kwargs)
    sb.run(tmp_path / "snap", properties, tmp_path / "outb", tmp_path / "rb.json", **kwargs)
    assert np.array_equal(
        np.load(tmp_path / "outa" / "embeddings-svd_dirigido-seed0.npy"),
        np.load(tmp_path / "outb" / "embeddings-svd_dirigido-seed0.npy"),
    )
    first = json.loads((tmp_path / "outa" / "predictions-svd_dirigido-seed0.json").read_text(encoding="utf-8"))
    second = json.loads((tmp_path / "outb" / "predictions-svd_dirigido-seed0.json").read_text(encoding="utf-8"))
    assert first == second


def test_invariancia_a_ordem_da_tabela(tmp_path):
    mapping_a, _ = write_clique_inputs(tmp_path / "a")
    write_clique_inputs(tmp_path / "b", shuffle=True)
    ids_a, src_a, dst_a, wgt_a = sb.load_directed_edges(tmp_path / "a" / "snap")
    ids_b, src_b, dst_b, wgt_b = sb.load_directed_edges(tmp_path / "b" / "snap")
    assert ids_a == ids_b
    assert np.array_equal(np.sort(src_a), np.sort(src_b))
    matrix_a = sb.build_directed_matrix(len(ids_a), src_a, dst_a, wgt_a)
    matrix_b = sb.build_directed_matrix(len(ids_b), src_b, dst_b, wgt_b)
    assert (matrix_a != matrix_b).nnz == 0
    first, _, _ = sb.fit_symmetric_ase(matrix_a, 2, bs.SELECTION_SEEDS[0])
    second, _, _ = sb.fit_symmetric_ase(matrix_b, 2, bs.SELECTION_SEEDS[0])
    assert np.array_equal(first, second)
    assert mapping_a["c0"] != mapping_a["c10"]


def test_smoke_ponta_a_ponta(tmp_path):
    _, properties = write_clique_inputs(tmp_path)
    report = sb.run(
        tmp_path / "snap",
        properties,
        tmp_path / "out",
        tmp_path / "report.json",
        configs=("svd_dirigido", "ase_simetrizado"),
        seeds=(bs.SELECTION_SEEDS[0],),
        n_components=2,
    )
    assert report["schema"] == "b07-spectral"
    assert report["verdict"] == sb.VERDICT
    assert set(report["results"]) == {"svd_dirigido", "ase_simetrizado"}
    assert report["resources"]["directed_nnz"] == 180
    assert report["resources"]["directed_matrix_bytes"] < report["resources"]["directed_dense_equivalent_bytes"]
    assert report["resources"]["directed_dense_equivalent_bytes"] == 20 * 20 * 8
    assert report["split"] == {"train": 16, "val": 4, "classes": 2}
    assert len(report["predictions"]) == 2
    assert len(report["embeddings"]) == 2
    for entry in report["predictions"] + report["embeddings"]:
        assert len(entry["sha256"]) == 64
    assert (tmp_path / "out" / "predictions-ase_simetrizado-seed0.json").exists()
    assert (tmp_path / "out" / "embeddings-ase_simetrizado-seed0.npy").exists()
    stored = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    assert stored["verdict"] == sb.VERDICT
    assert stored["results"]["svd_dirigido"]["dims"] == 4
    assert stored["results"]["ase_simetrizado"]["dims"] == 2


def test_sem_referencias_proibidas_e_configs_fixas():
    source = (ROOT / "tools" / "spectral_baseline.py").read_text(encoding="utf-8")
    for token in ("data/sealed", "target_labels", "crosswalk"):
        assert token not in source
    assert "male-cns" not in source
    assert set(sb.CONFIGS) == {"svd_dirigido", "ase_simetrizado"}
    assert sb.CONFIGS["svd_dirigido"]["k"] == 32
    assert sb.CONFIGS["svd_dirigido"]["dims"] == 64
    assert sb.CONFIGS["ase_simetrizado"]["k"] == 32
    assert sb.CONFIGS["ase_simetrizado"]["dims"] == 32
