import copy
import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import regal_repro as rr  # noqa: E402

REPORT = ROOT / "artifacts" / "reports" / "B08-REGAL.json"


def test_parser_de_scores():
    stdout = "learning representations...\nscore top1: 0.905727\nscore top5: 0.990000\n"
    assert rr.parse_scores(stdout) == {"top1": 0.905727, "top5": 0.99}
    with pytest.raises(rr.RegalError):
        rr.parse_scores("sem score")


def test_criterio_paridade_declarado():
    same = rr.artifact_parity(0.9, 0.9, "a" * 64, "b" * 64, 0.01, 1e-5)
    assert same["status"] == "reproduzido" and same["delta_accuracy"] == 0.0
    within = rr.artifact_parity(0.9, 0.899, "a" * 64, "b" * 64, 0.01, 1e-5)
    assert within["status"] == "reproduzido"
    outside = rr.artifact_parity(0.9, 0.8, "a" * 64, "b" * 64, 0.01, 1e-5)
    assert outside["status"] == "divergente"
    noisy_embedding = rr.artifact_parity(0.9, 0.9, "a" * 64, "b" * 64, 0.5, 0.1)
    assert noisy_embedding["status"] == "divergente"
    identical = rr.artifact_parity(0.9, 0.5, "c" * 64, "c" * 64, 9.0, 9.0)
    assert identical["status"] == "reproduzido" and identical["hash_identical"]
    assert rr.ACCURACY_TOLERANCE == 0.002 and rr.EMBEDDING_MEAN_ABS_TOLERANCE == 1e-4


def test_paridade_publicada_sem_numero():
    published = rr.published_parity()
    assert published["status"] == "não verificável numericamente"
    assert published["numeric_reference"] is None
    assert len(published["checked_sources"]) >= 2
    for source in published["checked_sources"]:
        assert len(source["sha256"]) == 64
    assert any("Figura 4" in source["location"] for source in published["checked_sources"])


def test_check_report_real_passa():
    assert rr.check_report(REPORT) == []


def test_check_report_detecta_desonestidade(tmp_path):
    report = json.loads(REPORT.read_text(encoding="utf-8"))

    dishonest = copy.deepcopy(report)
    dishonest["artifact_parity"]["status"] = "reproduzido"
    dishonest["artifact_parity"]["delta_accuracy"] = 0.5
    dishonest["artifact_parity"]["mean_abs_diff"] = 0.5
    dishonest["artifact_parity"]["hash_identical"] = False
    path = tmp_path / "dishonest.json"
    path.write_text(json.dumps(dishonest), encoding="utf-8")
    assert any("sem satisfazer o critério" in failure for failure in rr.check_report(path))

    overclaimed = copy.deepcopy(report)
    overclaimed["published_parity"]["numeric_reference"] = 0.905727
    path = tmp_path / "overclaimed.json"
    path.write_text(json.dumps(overclaimed), encoding="utf-8")
    assert any("não pode declarar valor" in failure for failure in rr.check_report(path))

    hidden = copy.deepcopy(report)
    hidden["reference_pickle_artifact"]["status"] = "ok"
    path = tmp_path / "hidden.json"
    path.write_text(json.dumps(hidden), encoding="utf-8")
    assert any("pickle" in failure for failure in rr.check_report(path))

    broken_counts = copy.deepcopy(report)
    broken_counts["recomputed"]["run"]["correct"] = 0
    path = tmp_path / "counts.json"
    path.write_text(json.dumps(broken_counts), encoding="utf-8")
    assert any("incoerentes" in failure for failure in rr.check_report(path))

    missing_files = copy.deepcopy(report)
    missing_files["vendor"]["files"] = {}
    path = tmp_path / "files.json"
    path.write_text(json.dumps(missing_files), encoding="utf-8")
    assert any("incompleta" in failure for failure in rr.check_report(path))


def test_sem_referencias_proibidas_e_config_fixa():
    source = (ROOT / "tools" / "regal_repro.py").read_text(encoding="utf-8")
    for token in ("male-cns", "data/sealed", "target_labels", "crosswalk"):
        assert token not in source
    assert rr.REGAL_COMMIT == "42ed9083f51ad481dc7d7acfb488b390e2013050"
    assert rr.REGAL_LICENSE == "MIT"
    assert "license.txt" in rr.VENDOR_FILES


def _fixture_combined(tmp_path: Path, n: int = 30, seed: int = 7) -> Path:
    rng = np.random.RandomState(seed)
    adjacency = (rng.rand(n, n) < 0.15).astype(int)
    adjacency = np.triu(adjacency, 1)
    adjacency = adjacency + adjacency.T
    for index in range(n):
        if adjacency[index].sum() == 0:
            adjacency[index, (index + 1) % n] = 1
            adjacency[(index + 1) % n, index] = 1
    permutation = rng.permutation(n)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if adjacency[i, j]:
                edges.append((i, j))
                edges.append((n + permutation[i], n + permutation[j]))
    # Convenção oficial: os valores do mapa são índices locais no grafo 2
    # (ver score_alignment_matrix em alignments.py), não IDs globais.
    mapping = {i: int(permutation[i]) for i in range(n)}
    with (tmp_path / "fixture_combined_edges.txt").open("w", encoding="utf-8") as handle:
        for start, end in edges:
            handle.write(f"{start} {end}\n")
    with (tmp_path / "fixture_edges-mapping-permutation.txt").open("wb") as handle:
        pickle.dump(mapping, handle)
    return tmp_path


@pytest.mark.skipif(not rr.VENDOR.exists() or not rr.VENV_PY.exists(), reason="reprodução oficial ausente (vendor/venv ignorados)")
def test_integracao_com_codigo_oficial_em_fixture(tmp_path_factory, tmp_path):
    # O oficial localiza o mapa por split("_") no caminho de entrada; o diretório
    # do fixture precisa ficar sem underscores (tmp_path usa o nome do teste).
    fixture = tmp_path_factory.mktemp("b08")
    _fixture_combined(fixture)
    output = tmp_path / "fixture-run.npy"
    stdout, _, _ = rr._run(
        [str(rr.VENV_PY), "regal.py", "--input", str(fixture / "fixture_combined_edges.txt"), "--output", str(output)],
        cwd=rr.VENDOR,
    )
    assert str(fixture / "fixture_edges-mapping-permutation.txt") in stdout
    scores = rr.parse_scores(stdout)
    mapped = rr._score_embeddings(output, mapping=str(fixture / "fixture_edges-mapping-permutation.txt"))
    assert 0.0 <= scores["top1"] <= 1.0
    assert round(scores["top1"], 6) == round(mapped["accuracy"], 6)
    assert mapped["pairs"] == 30
    assert mapped["accuracy"] >= 0.7
