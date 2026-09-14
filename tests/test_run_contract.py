import json
import re
import sys
import time as real_time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import run as r  # noqa: E402
import seeds as s  # noqa: E402

CONFIG = {"experiment": "teste", "seed": 7, "params": {"n_bytes": 256, "repeats": 2}}


def write_config(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "config.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_config_valida_e_resolve_defaults():
    assert r.validate_config(CONFIG) == []
    resolved = r.resolve_config({"experiment": "teste", "seed": 1, "params": {}})
    assert resolved["params"] == r.PARAM_DEFAULTS
    assert set(resolved["params"]) == set(r.PARAM_LIMITS)


@pytest.mark.parametrize(
    "mutacao, esperado",
    [
        (lambda c: c.pop("seed"), "seed"),
        (lambda c: c.update(experiment="MAIUSCULO"), "experiment"),
        (lambda c: c["params"].update(desconhecido=1), "inesperado"),
        (lambda c: c["params"].update(n_bytes=0), "entre"),
        (lambda c: c.update(extra=1), "inesperado"),
        (lambda c: c.update(seed=-1), "seed"),
        (lambda c: c.update(params="x"), "params"),
    ],
)
def test_config_invalida(mutacao, esperado):
    payload = json.loads(json.dumps(CONFIG))
    mutacao(payload)
    failures = r.validate_config(payload)
    assert failures and any(esperado in f for f in failures), failures


def test_schema_config_declara_os_mesmos_campos():
    schema = json.loads((ROOT / "schemas" / "run-config.schema.json").read_text(encoding="utf-8"))
    assert tuple(schema["required"]) == r.CONFIG_REQUIRED
    assert set(schema["properties"]["params"]["properties"]) == set(r.PARAM_LIMITS)
    assert "notes" in schema["properties"] and "notes" in r.CONFIG_OPTIONAL


def test_schema_manifest_declara_campos_obrigatorios():
    schema = json.loads((ROOT / "schemas" / "run-manifest.schema.json").read_text(encoding="utf-8"))
    for field in ("run_id", "created_at", "config", "code", "environment", "seeds", "resources", "outputs"):
        assert field in schema["required"], field
    assert "manifest" in r.TOOL_VERSION or "manifest" in (ROOT / "schemas" / "run-manifest.schema.json").name


def test_run_id_deterministico_e_sensivel_ao_commit():
    code = {"git_commit": "a" * 40, "git_dirty": False, "dirty_diff_sha256": None}
    first = r.compute_run_id(CONFIG, code)
    assert first == r.compute_run_id(CONFIG, code)
    other = r.compute_run_id(CONFIG, {**code, "git_commit": "b" * 40})
    assert first != other and re.fullmatch(r"[0-9a-f]{16}", first)


def test_duas_execucoes_geram_as_mesmas_saidas(tmp_path):
    config = write_config(tmp_path, CONFIG)
    first = r.execute(config, tmp_path / "runs-1")
    second = r.execute(config, tmp_path / "runs-2")
    assert first["status"] == second["status"] == "completed"
    assert first["run_id"] == second["run_id"]
    assert first["manifest_data"]["outputs"] == second["manifest_data"]["outputs"]


def test_segunda_execucao_usa_cache_sem_reescrever(tmp_path):
    config = write_config(tmp_path, CONFIG)
    runs = tmp_path / "runs"
    first = r.execute(config, runs)
    manifest_path = first["manifest"]
    before = manifest_path.read_bytes()
    second = r.execute(config, runs)
    assert second["status"] == "cached"
    assert manifest_path.read_bytes() == before


def test_saida_divergente_bloqueia_sem_sobrescrever(tmp_path):
    config = write_config(tmp_path, CONFIG)
    runs = tmp_path / "runs"
    first = r.execute(config, runs)
    summary = first["manifest"].parent / "outputs" / "summary.json"
    summary.write_bytes(b"adulterado")
    with pytest.raises(r.RunError, match="divergente"):
        r.execute(config, runs)
    assert summary.read_bytes() == b"adulterado"


def test_diretorio_sem_manifesto_bloqueia(tmp_path):
    config = write_config(tmp_path, CONFIG)
    runs = tmp_path / "runs"
    result = r.execute(config, runs)
    (result["manifest"]).unlink()
    with pytest.raises(r.RunError, match="sem manifesto"):
        r.execute(config, runs)


def test_timestamp_nao_entra_nas_saidas(tmp_path, monkeypatch):
    config = write_config(tmp_path, CONFIG)

    class FakeTime:
        def __init__(self, stamp):
            self.stamp = stamp

        def __getattr__(self, name):
            return getattr(real_time, name)

        def strftime(self, *args, **kwargs):
            return self.stamp

    monkeypatch.setattr(r, "time", FakeTime("2000-01-01T00:00:00Z"))
    first = r.execute(config, tmp_path / "runs-a")
    monkeypatch.setattr(r, "time", FakeTime("2030-12-31T23:59:59Z"))
    second = r.execute(config, tmp_path / "runs-b")
    assert first["manifest_data"]["outputs"] == second["manifest_data"]["outputs"]
    assert first["manifest_data"]["created_at"] != second["manifest_data"]["created_at"]


def test_manifesto_completo(tmp_path):
    config = write_config(tmp_path, CONFIG)
    result = r.execute(config, tmp_path / "runs")
    manifest = result["manifest_data"]
    assert manifest["status"] == "completed"
    assert manifest["config"]["params"] == CONFIG["params"]
    assert manifest["config_sha256"] == r.sha256_bytes(r.canonical_json(manifest["config"]).encode())
    assert manifest["seeds"]["master"] == CONFIG["seed"]
    assert set(manifest["seeds"]["derived"]) == set(r.SEED_NAMES)
    assert manifest["environment"]["python"]
    assert manifest["resources"]["wall_s"] >= 0
    assert manifest["outputs"] and all(re.fullmatch(r"[0-9a-f]{64}", o["sha256"]) for o in manifest["outputs"])


def test_seeds_centralizadas_deterministicas():
    assert s.derive_seed(1, "run", "stream") == s.derive_seed(1, "run", "stream")
    assert s.derive_seed(1, "run", "stream") != s.derive_seed(1, "run", "outro")
    assert s.derive_seed(1, "run", "stream") != s.derive_seed(2, "run", "stream")
    with pytest.raises(ValueError):
        s.derive_seed(-1, "run")
