import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import dry_run as dr  # noqa: E402
import evaluator_contract as ec  # noqa: E402
import firewall as fw  # noqa: E402


def test_dry_run_ponta_a_ponta(tmp_path):
    manifest = dr.run(tmp_path / "dryrun")
    assert manifest["schema_version"] == "1.0"
    assert manifest["dryrun_tag"].startswith("dryrun-1.0-")
    assert manifest["firewall_scanner_clean"] is True
    assert manifest["stages"]["download"]["download"] == "downloaded"
    assert manifest["stages"]["preprocess"]["rows"] == 60
    assert manifest["stages"]["inference"]["queries"] == 70
    assert manifest["stages"]["inference"]["rejected"] > 0
    assert manifest["unknown_queries"] == 10
    predictions = json.loads((tmp_path / "dryrun" / "predictions.json").read_text(encoding="utf-8"))
    metrics = json.loads((tmp_path / "dryrun" / "metrics.json").read_text(encoding="utf-8"))
    assert ec.validate_predictions(predictions) == []
    assert ec.validate_metrics(metrics) == []
    assert metrics["counts"]["unknown"] == 10
    assert 0.0 <= metrics["primary"]["value"] <= 1.0
    assert metrics["open_set"]["tpr_target"] == 0.95
    assert metrics["comparisons"]["sesoi_pp"] == 5


def test_dry_run_deterministico(tmp_path):
    first = dr.run(tmp_path / "a")
    second = dr.run(tmp_path / "b")
    assert first["dryrun_tag"] == second["dryrun_tag"]
    assert first["predictions_sha256"] == second["predictions_sha256"]
    assert first["stages"]["train"]["weights_sha256"] == second["stages"]["train"]["weights_sha256"]


def test_leakage_proposital_falha(tmp_path):
    sealed = tmp_path / "sealed"
    sealed.mkdir()
    (sealed / "labels.json").write_text(json.dumps({"q1": "alpha"}), encoding="utf-8")
    script = tmp_path / "leak.py"
    script.write_text(
        f"""
import sys
from pathlib import Path
sys.path.insert(0, {str(ROOT / 'tools')!r})
from firewall import FirewallError, install_audit_firewall, guarded_open
install_audit_firewall(roots=(Path({str(sealed)!r}),))
try:
    open({str(sealed / 'labels.json')!r}, "rb").read()
except FirewallError:
    first = "abertura bloqueada"
else:
    raise SystemExit("FALHA: sabotagem de leakage não foi detectada")
try:
    guarded_open({str(sealed / 'labels.json')!r})
except FirewallError:
    print(first, "e", "abertura guardada bloqueada")
""",
        encoding="utf-8",
    )
    result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stderr
    assert "abertura bloqueada" in result.stdout


def test_predicao_com_label_e_recusada(tmp_path):
    manifest = dr.run(tmp_path / "dryrun")
    predictions = json.loads((tmp_path / "dryrun" / "predictions.json").read_text(encoding="utf-8"))
    predictions["queries"][0]["type"] = "alpha"
    failures = ec.validate_predictions(predictions)
    assert any("proibida" in failure for failure in failures), failures


def test_manifesto_nao_referencia_dados_reais(tmp_path):
    manifest = dr.run(tmp_path / "dryrun")
    serialized = json.dumps(manifest)
    for token in ("target-public", "male-cns", "manc"):
        assert token not in serialized.lower()
    for path in (tmp_path / "dryrun").rglob("*"):
        if path.is_file() and path.suffix in (".json", ".csv"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            assert "target-public" not in text
