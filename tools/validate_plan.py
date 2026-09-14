#!/usr/bin/env python3
"""Valida estrutura do plano de microfases para o baseline C00.

Verifica: contagem de microfases/gates, presença dos seis campos obrigatórios,
resolução de IDs referenciados em Dependências e resolução de links Markdown
relativos. Sem dependências externas; o diretório-raiz é o pai deste arquivo.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "docs" / "PLANO-MICROFASES.md"
FIELDS = ("Objetivo", "Entregas", "Aceite", "Proibições", "Dependências", "Orçamento")
ITEM_RE = re.compile(r"^- \[[ x]\] \*\*([A-Z]\d{1,2}) — (.+?)\*\*$")
ID_RE = re.compile(r"\b([A-Z])(\d{1,2})\b")
RANGE_RE = re.compile(r"\b([A-Z])(\d{1,2})\s*[–-]\s*([A-Z])?(\d{1,2})\b")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def canonical_id(prefix: str, number: str | int) -> str:
    value = int(number)
    return f"G{value}" if prefix == "G" else f"{prefix}{value:02d}"


def parse_items(lines: list[str]) -> list[tuple[int, str]]:
    items: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        m = ITEM_RE.match(line)
        if m:
            items.append((i, canonical_id(m.group(1)[0], m.group(1)[1:])))
    return items


def block_lines(lines: list[str], items: list[tuple[int, str]], idx: int) -> list[str]:
    start = items[idx][0]
    end = items[idx + 1][0] if idx + 1 < len(items) else len(lines)
    return lines[start:end]


def expand_ranges(token: str) -> list[str]:
    expanded: list[str] = []
    for m in RANGE_RE.finditer(token):
        prefix, first, second_prefix, last = m.group(1), int(m.group(2)), m.group(3) or m.group(1), int(m.group(4))
        if prefix == second_prefix:
            expanded.extend(canonical_id(prefix, n) for n in range(first, last + 1))
    return expanded


def check_fields(items: list[tuple[int, str]], lines: list[str]) -> list[str]:
    failures: list[str] = []
    for idx, (_, item_id) in enumerate(items):
        block = "\n".join(block_lines(lines, items, idx))
        for field in FIELDS:
            if not re.search(rf"^\s*- {re.escape(field)}:", block, re.M):
                failures.append(f"{item_id}: campo ausente '{field}'")
    return failures


def check_dependencies(items: list[tuple[int, str]], lines: list[str]) -> tuple[list[str], int]:
    known = {item_id for _, item_id in items}
    failures: list[str] = []
    resolved = 0
    for idx, (_, item_id) in enumerate(items):
        block = "\n".join(block_lines(lines, items, idx))
        m = re.search(r"^\s*- Dependências: (.+)$", block, re.M)
        if not m:
            continue
        value = m.group(1).strip()
        if value.rstrip(".").lower() in {"plano atual", "—", "-", "nenhuma"}:
            continue
        expanded = set(expand_ranges(value))
        for prefix, number in ID_RE.findall(value):
            expanded.add(canonical_id(prefix, number))
        if not expanded:
            failures.append(f"{item_id}: Dependências sem IDs reconhecíveis: {value!r}")
            continue
        for ref in sorted(expanded):
            if ref not in known:
                failures.append(f"{item_id}: dependência '{ref}' não existe no plano")
            else:
                resolved += 1
    return failures, resolved


def check_links() -> tuple[list[str], int, int]:
    failures: list[str] = []
    total = 0
    files = 0
    for md in sorted(ROOT.rglob("*.md")):
        if ".git" in md.parts:
            continue
        files += 1
        text = md.read_text(encoding="utf-8")
        for number, line in enumerate(text.splitlines(), 1):
            for target in LINK_RE.findall(line):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                path = target.split("#", 1)[0]
                if not path:
                    continue
                total += 1
                if not (md.parent / path).resolve().exists():
                    failures.append(f"{md.relative_to(ROOT)}:{number}: link quebrado '{target}'")
    return failures, total, files


def main() -> int:
    if not PLAN.exists():
        print(f"FALHA: {PLAN} não encontrado")
        return 1
    lines = PLAN.read_text(encoding="utf-8").splitlines()
    items = parse_items(lines)
    phases = [i for _, i in items if not i.startswith("G")]
    gates = [i for _, i in items if i.startswith("G")]
    failures: list[str] = []

    if len(phases) != 81:
        failures.append(f"esperadas 81 microfases, encontradas {len(phases)}")
    if len(gates) != 9:
        failures.append(f"esperados 9 gates, encontrados {len(gates)}")
    if gates and sorted(gates, key=lambda g: int(g[1:])) != [f"G{n}" for n in range(9)]:
        failures.append(f"gates inesperados: {', '.join(sorted(gates, key=lambda g: int(g[1:])))}")
    if len(set(phases + gates)) != len(items):
        failures.append("IDs duplicados no plano")

    failures += check_fields(items, lines)
    dep_failures, resolved = check_dependencies(items, lines)
    failures += dep_failures
    link_failures, links, link_files = check_links()
    failures += link_failures

    if failures:
        for failure in failures:
            print(f"FALHA: {failure}")
        print(f"RESULTADO: {len(failures)} falha(s)")
        return 1
    print(f"OK: {len(phases)} microfases e {len(gates)} gates (G0–G8)")
    print(f"OK: {len(FIELDS)} campos obrigatórios presentes nos {len(items)} itens")
    print(f"OK: {resolved} referências de dependência resolvidas")
    print(f"OK: {links} links relativos resolvidos em {link_files} arquivos Markdown")
    return 0


if __name__ == "__main__":
    sys.exit(main())
