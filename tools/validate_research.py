#!/usr/bin/env python3
"""Valida os registros abertos em C01: GLOSSARIO.md, CLAIMS.md e RISCOS.md.

Verifica IDs estáveis e únicos, campos obrigatórios, vocabulário de status,
exigência de artefato para itens marcados como mitigados/confirmados, referências
de fase contra o plano e caminhos de arquivo citados em backticks. Sem
dependências externas além de `tools/validate_plan.py`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from validate_plan import PLAN, canonical_id, expand_ranges, parse_items

ROOT = Path(__file__).resolve().parent.parent
RESEARCH = ROOT / "docs" / "research"

GLOSSARY = RESEARCH / "GLOSSARIO.md"
CLAIMS = RESEARCH / "CLAIMS.md"
RISKS = RESEARCH / "RISCOS.md"

REQUIRED_GLOSSARY_TERMS = (
    "fonte",
    "alvo",
    "zero-shot",
    "tipo",
    "supertype",
    "homologia",
    "função",
    "embedding",
    "leakage",
    "circularidade",
    "réplica técnica",
    "réplica biológica",
)

GLOSSARY_STATUS_PREFIXES = (
    "definido provisoriamente",
    "aberto até",
    "revisado por humano",
    "fora do escopo",
)
CLAIM_STATUSES = {"aberto", "confirmado", "ambíguo", "conflitante", "não encontrado", "refutado"}
RISK_STATUSES = {"aberto", "em detalhamento", "mitigado com artefato", "aceito com justificativa", "refutado"}
CLAIM_TYPES = {"hipótese", "capacidade de dado", "literatura", "método"}

ENTRY_RE = r"^- \*\*{prefix}-(\d{{{width}}}) — (.+?)\*\*$"
FIELD_RE = r"^\s+- {field}: (.+)$"
PATH_RE = re.compile(r"`((?:docs|tools)/[A-Za-z0-9_./-]+\.(?:md|py|yaml))`")
ID_RE = re.compile(r"\b([A-Z])(\d{1,2})\b")


def parse_entries(path: Path, prefix: str, width: int) -> list[tuple[str, str, list[str]]]:
    pattern = re.compile(ENTRY_RE.format(prefix=prefix, width=width))
    entries: list[tuple[str, str, list[str]]] = []
    current: tuple[str, str, list[str]] | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            current = (f"{prefix}-{match.group(1)}", match.group(2), [])
            entries.append(current)
        elif current is not None:
            current[2].append(line)
    return entries


def field_value(block: list[str], field: str) -> str | None:
    pattern = re.compile(FIELD_RE.format(field=re.escape(field)))
    for line in block:
        match = pattern.match(line)
        if match:
            return match.group(1).strip().rstrip(". ")
    return None


def check_entries(
    path: Path, prefix: str, width: int, fields: tuple[str, ...]
) -> tuple[list[str], list[tuple[str, str, list[str]]]]:
    filename = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
    if not path.exists():
        return [f"{filename}: arquivo ausente"], []
    entries = parse_entries(path, prefix, width)
    failures: list[str] = []
    seen: set[str] = set()
    for entry_id, _, block in entries:
        if entry_id in seen:
            failures.append(f"{filename}: ID duplicado {entry_id}")
        seen.add(entry_id)
        for field in fields:
            if field_value(block, field) is None:
                failures.append(f"{filename}: {entry_id} sem campo '{field}'")
    if not entries:
        failures.append(f"{filename}: nenhum registro {prefix}-* encontrado")
    return failures, entries


def check_glossary() -> tuple[list[str], int]:
    fields = ("Definição operacional", "Âncora", "Status", "Responsável")
    failures, entries = check_entries(GLOSSARY, "GLO", 2, fields)
    titles = {entry_id: title.lower() for entry_id, title, _ in entries}
    if entries:
        for term in REQUIRED_GLOSSARY_TERMS:
            if not any(term in title for title in titles.values()):
                failures.append(f"GLOSSARIO.md: termo obrigatório ausente ('{term}')")
        for entry_id, _, block in entries:
            status = field_value(block, "Status")
            if status is None:
                continue
            if not status.startswith(GLOSSARY_STATUS_PREFIXES):
                failures.append(f"GLOSSARIO.md: {entry_id} status inválido '{status}'")
    return failures, len(entries)


def check_claims() -> tuple[list[str], int]:
    fields = ("Claim", "Tipo", "Status", "Evidência", "Responsável", "Fase de resolução")
    failures, entries = check_entries(CLAIMS, "CLM", 3, fields)
    for entry_id, _, block in entries:
        status = field_value(block, "Status")
        claim_type = field_value(block, "Tipo")
        evidence = field_value(block, "Evidência")
        if status is not None and status not in CLAIM_STATUSES:
            failures.append(f"CLAIMS.md: {entry_id} status inválido '{status}'")
        if claim_type is not None and claim_type not in CLAIM_TYPES:
            failures.append(f"CLAIMS.md: {entry_id} tipo inválido '{claim_type}'")
        if status == "confirmado" and evidence is not None:
            if "pendente" in evidence.lower() or evidence in {"", "—", "-"}:
                failures.append(f"CLAIMS.md: {entry_id} confirmado sem evidência verificável")
    return failures, len(entries)


def check_risks() -> tuple[list[str], int]:
    fields = (
        "Risco",
        "Categoria",
        "Status",
        "Detecção planejada",
        "Mitigação planejada",
        "Fase de detalhamento",
        "Responsável",
    )
    failures, entries = check_entries(RISKS, "RSK", 3, fields)
    for entry_id, _, block in entries:
        status = field_value(block, "Status")
        artifact = field_value(block, "Artefato")
        if status is not None and status not in RISK_STATUSES:
            failures.append(f"RISCOS.md: {entry_id} status inválido '{status}'")
        if status == "mitigado com artefato" and (artifact is None or artifact in {"", "—", "-"}):
            failures.append(f"RISCOS.md: {entry_id} mitigado sem campo Artefato")
    return failures, len(entries)


def check_phase_refs(entries_by_file: list[tuple[Path, list[tuple[str, str, list[str]]]]]) -> tuple[list[str], int]:
    lines = PLAN.read_text(encoding="utf-8").splitlines()
    known = {item_id for _, item_id in parse_items(lines)}
    failures: list[str] = []
    resolved = 0
    for path, entries in entries_by_file:
        for entry_id, _, block in entries:
            for field in ("Fase de resolução", "Fase de detalhamento"):
                value = field_value(block, field)
                if value is None:
                    continue
                refs = set(expand_ranges(value))
                for prefix, number in ID_RE.findall(value):
                    refs.add(canonical_id(prefix, number))
                if not refs:
                    failures.append(f"{path.name}: {entry_id} sem fase reconhecível em '{field}'")
                for ref in sorted(refs):
                    if ref not in known:
                        failures.append(f"{path.name}: {entry_id} referencia fase inexistente '{ref}'")
                    else:
                        resolved += 1
    return failures, resolved


def check_paths() -> tuple[list[str], int]:
    failures: list[str] = []
    total = 0
    for path in (GLOSSARY, CLAIMS, RISKS):
        if not path.exists():
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for target in PATH_RE.findall(line):
                total += 1
                if not (ROOT / target).exists():
                    label = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
                    failures.append(f"{label}:{number}: caminho citado ausente '{target}'")
    return failures, total


def main() -> int:
    failures: list[str] = []
    glossary_failures, glossary_count = check_glossary()
    claim_failures, claim_count = check_claims()
    risk_failures, risk_count = check_risks()
    failures += glossary_failures + claim_failures + risk_failures
    entries_by_file = [
        (GLOSSARY, parse_entries(GLOSSARY, "GLO", 2) if GLOSSARY.exists() else []),
        (CLAIMS, parse_entries(CLAIMS, "CLM", 3) if CLAIMS.exists() else []),
        (RISKS, parse_entries(RISKS, "RSK", 3) if RISKS.exists() else []),
    ]
    ref_failures, refs = check_phase_refs(entries_by_file)
    path_failures, paths = check_paths()
    failures += ref_failures + path_failures

    if failures:
        for failure in failures:
            print(f"FALHA: {failure}")
        print(f"RESULTADO: {len(failures)} falha(s)")
        return 1
    print(f"OK: GLOSSARIO.md com {glossary_count} termos e os {len(REQUIRED_GLOSSARY_TERMS)} obrigatórios")
    print(f"OK: CLAIMS.md com {claim_count} claims, todos com status e evidência")
    print(f"OK: RISCOS.md com {risk_count} riscos, todos com campos completos")
    print(f"OK: {refs} referências de fase resolvidas contra o plano")
    print(f"OK: {paths} caminhos de arquivo citados e existentes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
