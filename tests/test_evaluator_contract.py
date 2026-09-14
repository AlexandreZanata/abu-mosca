import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import evaluator_contract as ec  # noqa: E402


def predictions() -> dict:
    return {
        "schema_version": "1.0",
        "run_id": "a" * 16,
        "seed": 1,
        "gallery": {"nodes": 100, "types": 5},
        "queries": [
            {
                "id": "q" + "b" * 16,
                "ranked": [{"id": "g" + "c" * 16, "score": 0.9}],
                "rejected": False,
            }
        ],
    }


def metrics() -> dict:
    return {
        "schema_version": "1.0",
        "run_id": "a" * 16,
        "evaluated_at": "2026-09-14T12:00:00Z",
        "inputs": {"predictions_sha256": "d" * 64, "label_set_sha256": "e" * 64},
        "counts": {
            "queries_total": 10, "known": 8, "unknown": 2,
            "excluded_missing": 0, "excluded_ambiguous": 0, "excluded_conflicting": 0,
            "classes_known": 5, "classes_small": 1,
        },
        "primary": {
            "name": "macro-recall@1-t0", "value": 0.4, "ci95": [0.3, 0.5],
            "n_classes": 5, "denominator": 8, "median_across_seeds": 0.41, "seed_range": [0.38, 0.44],
        },
        "comparisons": {
            "best_baseline": "degree-only", "delta": 0.07, "delta_ci95": [0.01, 0.13],
            "sesoi_pp": 5, "sesoi_met": True,
            "degree_matched": {"delta": 0.05, "ci95": [0.0, 0.1]},
            "balanced_sensitivity": {"delta": 0.06, "ci95": [0.01, 0.11], "k_min": 10},
            "holm_family_size": 3,
        },
        "open_set": {"auroc": 0.8, "aupr": 0.7, "fpr_at_tpr95": 0.1, "tpr_target": 0.95},
        "calibration": {"brier": 0.2, "ece": 0.05, "bins": 15, "temperature_source_fit": 1.1},
        "within_cross": {"within": 0.5, "cross": 0.4, "gap": 0.1},
        "secondary": {
            "recall@5": 0.6, "recall@10": 0.7, "mrr": 0.5, "map": 0.45,
            "macro_f1": 0.4, "balanced_accuracy": 0.42,
        },
        "nulls": {"label_permutation_p": 0.5, "degree_matched_p": 0.4, "permutations": 10000},
    }


def test_pacotes_validos_passam():
    assert ec.validate_predictions(predictions()) == []
    assert ec.validate_metrics(metrics()) == []


@pytest.mark.parametrize(
    "mutacao, esperado",
    [
        (lambda p: p.update(labels=["x"]), "proibida"),
        (lambda p: p["queries"][0].update(cell_type="X"), "proibida"),
        (lambda p: p["queries"][0].update(id="123456789012345"), "id opaco"),
        (lambda p: p["queries"][0]["ranked"][0].update(score="alto"), "score"),
        (lambda p: p["queries"][0]["ranked"][0].update(id="1234567890123"), "galeria"),
        (lambda p: p["queries"][0].update(ranked=[]), "ranked"),
        (lambda p: p.update(gallery={"nodes": 0, "types": 5}), "gallery"),
        (lambda p: p.update(schema_version="2.0"), "schema_version"),
    ],
)
def test_predicoes_invalidas(mutacao, esperado):
    payload = predictions()
    mutacao(payload)
    failures = ec.validate_predictions(payload)
    assert failures and any(esperado in f for f in failures), failures


@pytest.mark.parametrize(
    "mutacao, esperado",
    [
        (lambda m: m["primary"].pop("ci95"), "ci95"),
        (lambda m: m["primary"].update(name="accuracy"), "macro-recall@1-t0"),
        (lambda m: m["comparisons"].update(sesoi_pp=10), "SESOI"),
        (lambda m: m["comparisons"].update(holm_family_size=99), "Holm"),
        (lambda m: m["open_set"].update(tpr_target=0.9), "TPR"),
        (lambda m: m["calibration"].update(bins=5), "15 bins"),
        (lambda m: m.update(per_query=[{"ok": True}]), "inesperado"),
        (lambda m: m["inputs"].update(predictions_sha256="abc"), "inputs"),
        (lambda m: m["counts"].update(known=-1), "counts"),
    ],
)
def test_metricas_invalidas(mutacao, esperado):
    payload = metrics()
    mutacao(payload)
    failures = ec.validate_metrics(payload)
    assert failures and any(esperado in f for f in failures), failures


def test_id_cru_em_valor_falha():
    payload = metrics()
    payload["notes"] = "neurônio 1234567890"
    failures = ec.validate_metrics(payload)
    assert any("ID cru" in f for f in failures), failures


def test_schemas_e_validador_em_sincronia():
    pred = json.loads((ROOT / "schemas" / "predictions.schema.json").read_text(encoding="utf-8"))
    metr = json.loads((ROOT / "schemas" / "metrics.schema.json").read_text(encoding="utf-8"))
    assert tuple(pred["required"]) == ec.PREDICTIONS_REQUIRED
    assert tuple(metr["required"]) == ec.METRICS_REQUIRED
    assert pred["properties"]["run_id"]["pattern"] == ec.RUN_ID_RE.pattern
    assert metr["properties"]["primary"]["properties"]["name"]["const"] == "macro-recall@1-t0"
    assert metr["properties"]["comparisons"]["properties"]["sesoi_pp"]["const"] == 5
    assert metr["properties"]["calibration"]["properties"]["bins"]["const"] == 15


def test_cli_valida_arquivo(tmp_path):
    path = tmp_path / "pred.json"
    path.write_text(json.dumps(predictions()), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "evaluator_contract.py"), "validate", "predictions", str(path)],
        capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert "OK" in result.stdout
