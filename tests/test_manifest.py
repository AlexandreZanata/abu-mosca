import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import manifest as m  # noqa: E402


def base_manifest() -> dict:
    return {
        "schema_version": "1.0",
        "dataset": "Teste",
        "release": "v0",
        "source_page": "https://example.org/dataset",
        "license": "CC-BY-4.0",
        "files": [
            {
                "path": "data/raw/spikes/exemplo.bin",
                "url": "https://example.org/exemplo.bin",
                "bytes": 10,
                "sha256": "a" * 64,
                "md5_official": None,
                "accessed_at": "2026-09-14",
            }
        ],
    }


def test_manifest_valido_passa():
    assert m.validate_manifest(base_manifest()) == []


@pytest.mark.parametrize(
    "mutacao, esperado",
    [
        (lambda d: d.pop("files"), "obrigatório"),
        (lambda d: d["files"][0].pop("sha256"), "obrigatório"),
        (lambda d: d["files"][0].update(sha256="xyz"), "sha256"),
        (lambda d: d["files"][0].update(url="https://user:pass@example.org/x"), "credenciais"),
        (lambda d: d["files"][0].update(url="https://example.org/x?X-Amz-Signature=abc"), "credencial"),
        (lambda d: d["files"][0].update(url="http://example.org/x"), "https"),
        (lambda d: d.update(license="MIT"), "licença"),
        (lambda d: d["files"][0].update(path="tmp/x.bin"), "data/raw/"),
        (lambda d: d["files"][0].update(bytes=0), "bytes"),
        (lambda d: d["files"][0].update(accessed_at="14/09/2026"), "accessed_at"),
        (lambda d: d.update(schema_version="2.0"), "schema_version"),
        (lambda d: d["files"][0].update(extra="x"), "inesperado"),
    ],
)
def test_manifest_invalido_falha(mutacao, esperado):
    payload = base_manifest()
    mutacao(payload)
    failures = m.validate_manifest(payload)
    assert failures, "mutação deveria falhar"
    assert any(esperado in failure for failure in failures), failures


def test_schema_arquivo_declara_os_mesmos_obrigatorios():
    schema = json.loads((ROOT / "schemas" / "manifest.schema.json").read_text(encoding="utf-8"))
    assert tuple(schema["required"]) == m.TOP_LEVEL_REQUIRED
    assert schema["properties"]["license"]["enum"] == list(m.LICENSES)


def test_manifestos_reais_validam():
    paths = sorted((ROOT / "data" / "manifests").glob("*.json"))
    assert len(paths) >= 4, "esperados ao menos 4 manifestos versionados"
    failures, checked = m.validate_paths(paths, with_files=False)
    assert not failures, failures
    assert checked == len(paths)
