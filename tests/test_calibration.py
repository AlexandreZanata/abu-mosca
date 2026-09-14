import builtins
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import calibration as c  # noqa: E402


def test_brier_perfeito_e_ruim():
    perfect = {"q1": {"A": 1.0, "B": 0.0}, "q2": {"A": 0.0, "B": 1.0}}
    gold = {"q1": "A", "q2": "B"}
    assert c.brier_multiclass(perfect, gold) == 0.0
    mixed = {"q1": {"A": 0.8, "B": 0.2}, "q2": {"A": 0.1, "B": 0.9}}
    assert c.brier_multiclass(mixed, gold) == pytest.approx(0.05, abs=1e-6)


def test_ece_bins_fixos_e_tabela():
    confidences = [0.9, 0.9, 0.6]
    correct = [True, True, False]
    table = c.reliability_table(confidences, correct, bins=2)
    assert table[0]["count"] == 0
    assert table[1]["count"] == 3
    assert table[1]["mean_confidence"] == pytest.approx(0.8)
    assert table[1]["accuracy"] == pytest.approx(0.666667, abs=1e-6)
    assert c.expected_calibration_error(confidences, correct, bins=2) == pytest.approx(0.133333, abs=1e-6)


def test_auroc_aupr_e_degenerado():
    assert c.auroc([0.9, 0.8], [0.4, 0.3]) == 1.0
    assert c.aupr([0.9, 0.8], [0.4]) == 1.0
    assert c.auroc([0.5, 0.5], [0.5, 0.5]) == 0.5
    assert c.aupr([], [0.5]) == 0.0


def test_fpr_em_tpr_fixada():
    positives = [index / 20 for index in range(1, 21)]  # 0,05..1,00
    result = c.fpr_at_tpr(positives, [0.02, 0.03], tpr=0.95)
    assert result["tpr_achieved"] >= 0.95
    assert result["fpr"] == 0.0
    with_high_negative = c.fpr_at_tpr(positives, [0.2], tpr=0.95)
    assert with_high_negative["fpr"] == 1.0


def test_open_set_perfeito():
    result = c.open_set_metrics(known_scores=[0.9, 0.85], unknown_scores=[0.1, 0.2])
    assert result["auroc"] == 1.0
    assert result["fpr_at_tpr"]["fpr"] == 0.0


def test_bootstrap_agrupado_estavel_e_com_seed():
    groups = {"A": [1, 1, 1], "B": [0, 0, 0], "C": [1, 0, 1]}
    first = c.bootstrap_ci_grouped(groups, iterations=200, seed=7)
    second = c.bootstrap_ci_grouped(groups, iterations=200, seed=7)
    assert first == second
    assert first["seed"] == 7
    assert first["point"] == pytest.approx((1 + 0 + 2 / 3) / 3, abs=1e-6)
    assert first["ci95"][0] <= first["point"] <= first["ci95"][1]


def test_permutacao_por_troca_de_sinal():
    assert c.permutation_p_sign_flip([0, 0, 0], iterations=50, seed=1) == 1.0
    strong = c.permutation_p_sign_flip([1, 1, 1, 1, 1], iterations=200, seed=1)
    assert 0.0 < strong < 0.2


def test_limiar_aprendido_so_na_fonte():
    fitted = c.fit_threshold_source([0.9, 0.8, 0.7, 0.6], [0.2, 0.1], tpr=1.0)
    assert fitted["fitted_on"] == "source"
    assert fitted["threshold"] == 0.6
    assert c.apply_threshold([0.65, 0.55], fitted["threshold"]) == [False, True]


def test_fixture_desbalanceada():
    probabilities = {"q1": {"A": 0.9, "B": 0.1}, "q2": {"A": 0.9, "B": 0.1}, "q3": {"A": 0.7, "B": 0.3}}
    gold = {"q1": "A", "q2": "A", "q3": "B"}
    assert c.brier_multiclass(probabilities, gold) == pytest.approx(0.34, abs=1e-6)
    known = [0.9] * 100
    unknown = [0.1, 0.2]
    metrics = c.open_set_metrics(known, unknown)
    assert metrics["auroc"] == 1.0
    assert metrics["aupr"] == 1.0


def test_sem_io(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("calibração não pode abrir arquivos")

    monkeypatch.setattr(builtins, "open", forbidden)
    assert c.brier_multiclass({"q": {"A": 1.0}}, {"q": "A"}) == 0.0
