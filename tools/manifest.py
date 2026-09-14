#!/usr/bin/env python3
"""Validação de manifestos de proveniência (schema manual, sem dependências).

O contrato legível está em `schemas/manifest.schema.json`; este módulo implementa
as mesmas regras em Python e é usado pelos testes e pelo validador da fase R03.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schemas" / "manifest.schema.json"
MANIFESTS_DIR = ROOT / "data" / "manifests"

SCHEMA_VERSION = "1.0"
LICENSES = ("CC-BY-4.0", "CC-BY-4.0-restricted", "CC-BY-4.0-annotations-unclear")
TOP_LEVEL_REQUIRED = ("schema_version", "dataset", "release", "source_page", "license", "files")
FILE_REQUIRED = ("path", "url", "bytes", "sha256", "accessed_at")
PATH_RE = re.compile(r"^data/raw/[A-Za-z0-9._/-]+$")
URL_RE = re.compile(r"^https://[^@\s]+$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
MD5_RE = re.compile(r"^[0-9a-f]{32}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SOURCE_PAGE_RE = re.compile(r"^(https://|10\.)")
FORBIDDEN_QUERY_KEYS = {
    "token", "access_token", "api_key", "apikey", "key", "sig", "signature",
    "expires", "st", "se", "sp", "sv", "sr", "spr", "sig", "partnumber",
}
FORBIDDEN_QUERY_PREFIXES = ("x-amz-", "x-goog-", "x-ms-")


def _check_url(url: str, label: str, failures: list[str]) -> None:
    if not URL_RE.match(url):
        failures.append(f"{label}: URL deve ser https sem credenciais embutidas")
        return
    query = url.split("?", 1)[1] if "?" in url else ""
    for pair in filter(None, query.split("&")):
        key = pair.split("=", 1)[0].strip().lower()
        if key in FORBIDDEN_QUERY_KEYS or key.startswith(FORBIDDEN_QUERY_PREFIXES):
            failures.append(f"{label}: URL contém parâmetro de credencial/assinatura '{key}'")


def validate_manifest(payload: dict, label: str = "manifesto") -> list[str]:
    failures: list[str] = []
    if not isinstance(payload, dict):
        return [f"{label}: raiz deve ser um objeto JSON"]
    for field in TOP_LEVEL_REQUIRED:
        if field not in payload:
            failures.append(f"{label}: campo obrigatório ausente '{field}'")
    for field in payload:
        if field not in TOP_LEVEL_REQUIRED + ("notes",):
            failures.append(f"{label}: campo inesperado '{field}'")
    if payload.get("schema_version") != SCHEMA_VERSION:
        failures.append(f"{label}: schema_version deve ser '{SCHEMA_VERSION}'")
    for field in ("dataset", "release"):
        if not isinstance(payload.get(field), str) or not payload.get(field, "").strip():
            failures.append(f"{label}: '{field}' deve ser string não vazia")
    source_page = payload.get("source_page")
    if not isinstance(source_page, str) or not SOURCE_PAGE_RE.match(source_page):
        failures.append(f"{label}: 'source_page' deve ser URL https ou DOI")
    if payload.get("license") not in LICENSES:
        failures.append(f"{label}: licença fora da lista permitida: {payload.get('license')!r}")
    files = payload.get("files")
    if not isinstance(files, list) or not files:
        failures.append(f"{label}: 'files' deve ser lista não vazia")
        return failures
    seen_paths: set[str] = set()
    for index, entry in enumerate(files):
        item = f"{label}:files[{index}]"
        if not isinstance(entry, dict):
            failures.append(f"{item}: entrada deve ser objeto")
            continue
        for field in FILE_REQUIRED:
            if field not in entry:
                failures.append(f"{item}: campo obrigatório ausente '{field}'")
        for field in entry:
            if field not in FILE_REQUIRED + ("md5_official", "notes"):
                failures.append(f"{item}: campo inesperado '{field}'")
        path = entry.get("path")
        if not isinstance(path, str) or not PATH_RE.match(path):
            failures.append(f"{item}: 'path' deve começar em data/raw/ e usar caminho relativo")
        elif path in seen_paths:
            failures.append(f"{item}: caminho duplicado '{path}'")
        else:
            seen_paths.add(path)
        _check_url(str(entry.get("url", "")), item, failures)
        if not isinstance(entry.get("bytes"), int) or entry.get("bytes", 0) < 1:
            failures.append(f"{item}: 'bytes' deve ser inteiro positivo")
        sha = entry.get("sha256")
        if not isinstance(sha, str) or not SHA256_RE.match(sha):
            failures.append(f"{item}: 'sha256' deve ter 64 hexadecimais minúsculos")
        md5 = entry.get("md5_official")
        if md5 is not None and (not isinstance(md5, str) or not MD5_RE.match(md5)):
            failures.append(f"{item}: 'md5_official' deve ser null ou 32 hexadecimais")
        if not isinstance(entry.get("accessed_at"), str) or not DATE_RE.match(entry["accessed_at"]):
            failures.append(f"{item}: 'accessed_at' deve ser AAAA-MM-DD")
    return failures


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def file_digest(path: Path, algorithm: str = "sha256", chunk: int = 1 << 20) -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        while block := handle.read(chunk):
            digest.update(block)
    return digest.hexdigest()


def check_files(payload: dict, label: str) -> list[str]:
    failures: list[str] = []
    for index, entry in enumerate(payload.get("files", [])):
        item = f"{label}:files[{index}]"
        path = ROOT / str(entry.get("path", ""))
        if not path.exists():
            failures.append(f"{item}: arquivo ausente '{path.relative_to(ROOT)}'")
            continue
        size = path.stat().st_size
        if size != entry.get("bytes"):
            failures.append(f"{item}: bytes divergentes ({size} != {entry.get('bytes')})")
        digest = file_digest(path)
        if digest != entry.get("sha256"):
            failures.append(f"{item}: sha256 divergente para '{path.relative_to(ROOT)}'")
        md5 = entry.get("md5_official")
        if md5 and file_digest(path, "md5") != md5:
            failures.append(f"{item}: md5 oficial divergente para '{path.relative_to(ROOT)}'")
    return failures


def validate_paths(paths: list[Path], with_files: bool) -> tuple[list[str], int]:
    failures: list[str] = []
    checked = 0
    for path in paths:
        label = path.name
        try:
            payload = load(path)
        except json.JSONDecodeError as error:
            failures.append(f"{label}: JSON inválido ({error})")
            continue
        failures += validate_manifest(payload, label)
        if with_files:
            failures += check_files(payload, label)
        checked += 1
    return failures, checked


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate",), nargs="?", default="validate")
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--check-files", action="store_true")
    parser.add_argument("--schema-only", action="store_true")
    args = parser.parse_args()
    if args.schema_only:
        payload = load(SCHEMA)
        required = ("schema_version", "dataset", "release", "source_page", "license", "files")
        if payload.get("required") != list(required):
            print("FALHA: schema não declara os campos obrigatórios esperados")
            return 1
        print("OK: schema de manifest presente e com campos obrigatórios")
        return 0
    paths = args.paths or sorted(MANIFESTS_DIR.glob("*.json"))
    if not paths:
        print("FALHA: nenhum manifesto encontrado")
        return 1
    failures, checked = validate_paths(paths, with_files=args.check_files)
    if failures:
        for failure in failures:
            print(f"FALHA: {failure}")
        return 1
    suffix = " e arquivos conferidos" if args.check_files else ""
    print(f"OK: {checked} manifesto(s) válidos{suffix}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
