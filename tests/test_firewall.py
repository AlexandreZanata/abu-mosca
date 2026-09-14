import json
import logging
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import firewall as fw  # noqa: E402


@pytest.fixture()
def zonas(tmp_path, monkeypatch):
    sealed = tmp_path / "sealed"
    public = tmp_path / "public"
    sealed.mkdir()
    public.mkdir()
    (sealed / "labels.csv").write_text("ROTULO_SECRETO\n", encoding="utf-8")
    (public / "grafo.csv").write_text("id\n1\n", encoding="utf-8")
    monkeypatch.setattr(fw, "_ROOTS", (sealed,))
    return sealed, public


def test_guarded_open_bloqueia_selado_e_libera_publico(zonas):
    sealed, public = zonas
    with pytest.raises(fw.FirewallError):
        fw.guarded_open(sealed / "labels.csv")
    assert fw.guarded_open(public / "grafo.csv", "r").read().startswith("id")


def test_log_filter_bloqueia_caminho_e_coluna():
    logger = logging.getLogger("teste-firewall")
    logger.addFilter(fw.FirewallLogFilter(columns=("target_type",)))
    with pytest.raises(fw.FirewallError, match="caminho proibido"):
        logger.warning("abri data/sealed/x.csv")
    with pytest.raises(fw.FirewallError, match="coluna proibida"):
        logger.warning("coluna target_type lida")
    assert logger.info("mensagem limpa") is None


def test_inventario_expoe_apenas_hashes(zonas):
    sealed, _ = zonas
    inventory = fw.sealed_zone_inventory(sealed)
    assert inventory["count"] == 1
    assert len(inventory["files"][0]["sha256"]) == 64
    assert "ROTULO_SECRETO" not in json.dumps(inventory)


def test_scanner_detecta_e_respeita_marca(tmp_path):
    tools = tmp_path / "tools"
    tools.mkdir()
    bad = tools / "treino.py"
    bad.write_text("caminho = 'data/sealed/labels.csv'\n", encoding="utf-8")
    violations = fw.scan_forbidden_references(roots=(tools,), exempt=set())
    assert violations and "treino.py:1" in violations[0]
    bad.write_text("caminho = 'data/sealed/labels.csv'  # firewall-allow\n", encoding="utf-8")
    assert fw.scan_forbidden_references(roots=(tools,), exempt=set()) == []


def test_repo_limpo_no_scanner():
    assert fw.scan_forbidden_references() == []


def _run_script(tmp_path: Path, body: str) -> subprocess.CompletedProcess:
    script = tmp_path / "script.py"
    script.write_text(body, encoding="utf-8")
    return subprocess.run([sys.executable, str(script)], capture_output=True, text=True, timeout=120)


def test_auditoria_bloqueia_abertura_em_subprocesso(tmp_path, zonas):
    sealed, public = zonas
    body = f"""
import sys
from pathlib import Path
sys.path.insert(0, {str(ROOT / 'tools')!r})
from firewall import FirewallError, install_audit_firewall
install_audit_firewall(roots=(Path({str(sealed)!r}),))
try:
    open({str(sealed / 'labels.csv')!r}, "rb").read()
except FirewallError:
    pass
else:
    raise SystemExit("abertura selada permitida")
print("OK", open({str(public / 'grafo.csv')!r}, "rb").read().strip())
"""
    result = _run_script(tmp_path, body)
    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("OK")


def test_pipeline_publico_roda_com_firewall_armado(tmp_path):
    runs_dir = tmp_path / "runs"
    body = f"""
import sys
from pathlib import Path
sys.path.insert(0, {str(ROOT / 'tools')!r})
from firewall import install_audit_firewall
install_audit_firewall()
import run
result = run.execute(Path({str(ROOT / 'configs' / 'fixture.json')!r}), Path({str(runs_dir)!r}))
print(result["status"], result["run_id"])
"""
    result = _run_script(tmp_path, body)
    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("completed")
