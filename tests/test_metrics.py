import builtins
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import metrics as m  # noqa: E402

CANONICAL_RANKED = {
    "q1": ["A", "B", "C"],
    "q2": ["A", "B", "C"],
    "q3": ["A", "B", "C"],
    "q4": ["B", "A", "C"],
}
CANONICAL_GOLD = {"q1": "A", "q2": "B", "q3": "C", "q4": "A"}


def test_exemplo_calculado_a_mao():
    report = m.evaluate(CANONICAL_RANKED, CANONICAL_GOLD)
    assert report["recall"]["@1"]["macro"] == pytest.approx(0.166667, abs=1e-6)
    assert report["recall"]["@1"]["micro"] == pytest.approx(0.25)
    assert report["recall"]["@5"]["macro"] == 1.0
    assert report["mrr"] == pytest.approx(0.583333, abs=1e-6)
    assert report["map"] == pytest.approx(0.583333, abs=1e-6)
    assert report["top_k_accuracy"]["@1"] == pytest.approx(0.25)
    assert report["top_k_accuracy"]["@5"] == 1.0
    assert report["macro_f1"] == pytest.approx(0.133333, abs=1e-6)
    assert report["balanced_accuracy"] == pytest.approx(0.166667, abs=1e-6)
    assert report["counts"] == {"queries_scored": 4, "queries_unmatched": 0, "classes": 3}
    assert report["recall"]["@1"]["per_class"] == {"A": 0.5, "B": 0.0, "C": 0.0}


def test_empates_desfeitos_por_rotulo_e_orientacao():
    scores = {"q1": {"A": 0.5, "B": 0.5, "C": 0.1}}
    ranked = m.rank_from_scores(scores, higher_is_better=True)
    assert ranked["q1"] == ["A", "B", "C"]
    assert m.recall_at_k(ranked, {"q1": "A"}, 1)["micro"] == 1.0
    as_distances = m.rank_from_scores(scores, higher_is_better=False)
    assert as_distances["q1"] == ["C", "A", "B"]
    assert m.recall_at_k(as_distances, {"q1": "A"}, 1)["micro"] == 0.0


def test_classes_ausentes_entram_no_denominador_macro():
    ranked = {"q1": ["A"], "q2": ["A"]}
    gold = {"q1": "A", "q2": "Z"}
    report = m.recall_at_k(ranked, gold, 1)
    assert report["micro"] == pytest.approx(0.5)
    assert report["macro"] == pytest.approx(0.5)  # A=1,0 e Z=0
    assert report["per_class"] == {"A": 1.0, "Z": 0.0}


def test_multi_instance():
    ranked = {"q1": ["C", "A", "B"]}
    gold = {"q1": ["A", "B"]}
    assert m.recall_at_k(ranked, gold, 1)["micro"] == 0.0
    assert m.recall_at_k(ranked, gold, 5)["micro"] == 1.0
    assert m.mean_reciprocal_rank(ranked, gold) == pytest.approx(0.5)
    assert m.average_precision(ranked, gold) == pytest.approx(0.583333, abs=1e-6)


def test_query_sem_match_e_contada_a_parte():
    ranked = {"q1": ["A", "B"], "q2": ["A"]}
    gold = {"q1": None, "q2": "A"}
    report = m.recall_at_k(ranked, gold, 1)
    assert report["queries_unmatched"] == 1
    assert report["queries_scored"] == 1
    assert report["macro"] == 1.0


def test_implementacao_nao_le_arquivos(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("métricas não podem abrir arquivos")

    monkeypatch.setattr(builtins, "open", forbidden)
    report = m.evaluate(CANONICAL_RANKED, CANONICAL_GOLD, k_values=(1, 5))
    assert report["counts"]["queries_scored"] == 4


def test_gold_invalido_falha():
    with pytest.raises(m.MetricsError):
        m.recall_at_k({"q1": ["A"]}, {"q1": 123}, 1)
