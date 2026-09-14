#!/usr/bin/env python3
"""Valida os registros de C01 e o documento de estimando de C02.

C01: GLOSSARIO.md, CLAIMS.md e RISCOS.md — IDs estáveis e únicos, campos
obrigatórios, vocabulário de status, exigência de artefato para itens marcados
como mitigados/confirmados e caminhos citados em backticks.
C02: PERGUNTA-E-ESTIMANDO.md — seções obrigatórias, declaração de independência
de seeds/neurônios, separação entre datasets observados e população de moscas,
diagrama do fluxo, termos restritos confinados à seção de vocabulário e
referências de fase contra o plano.
Sem dependências externas além de `tools/validate_plan.py`.
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
ESTIMAND = RESEARCH / "PERGUNTA-E-ESTIMANDO.md"
EQUIVALENCE = RESEARCH / "EQUIVALENCIA.md"
OUTCOMES = RESEARCH / "DESFECHOS-E-FALSIFICACAO.md"

OUTCOMES_SECTIONS = (
    "## 1. Estado e escopo",
    "## 2. Métrica primária",
    "## 3. Métricas secundárias",
    "## 4. SESOI provisório",
    "## 5. Controles nulos e robustez",
    "## 6. Gap within-vs-cross",
    "## 7. Árvore de decisão",
    "## 8. Regras de reporte e proibições",
    "## 9. Rastreabilidade e limitações",
)
OUTCOMES_TOKENS = (
    "Macro Recall@1",
    "Recall@5",
    "Recall@10",
    "MRR",
    "MAP",
    "macro-F1",
    "balanced accuracy",
    "Brier",
    "ECE",
    "AUROC",
    "AUPR",
    "FPR",
    "degree-matched",
    "gap within-vs-cross",
    "bootstrap agrupado por tipo",
    "IC 95%",
    "SESOI",
)
OUTCOMES_STATES = ("sucesso", "parcial", "refutado", "inconclusivo")
OUTCOMES_RULES = (
    "não contam como evidência",
    "não conta como estimativa",
    "após o unseal",
)

ESTIMAND_SECTIONS = (
    "Estimando",
    "Hipótese primária",
    "Hipótese nula",
    "Diagrama do fluxo",
    "Unidade de consulta e galeria",
    "Limites de generalização",
    "Vocabulário restrito",
)
RESTRICTED_TERMS = ("universal", "função", "cross-individual")

EQUIVALENCE_SECTIONS = (
    "## 1. Alvo primário",
    "## 2. Hierarquia avaliativa",
    "## 3. Relações e classificação epistêmica",
    "## 4. Cardinalidade e correspondências",
    "## 5. Regras para casos-limite",
    "## 6. Regras de crosswalk",
    "## 7. Decisões pendentes",
    "## 8. Limites deste documento",
    "## 9. Aprovação humana",
)
APPROVAL_FIELDS = ("Data", "Aprovador", "Escopo")
EQUIVALENCE_RELATIONS = ("EQ-01", "EQ-02", "EQ-03", "EQ-04", "EQ-05")
RELATION_CLASSIFICATIONS = ("gold label", "proxy", "hipótese", "fora do escopo")
PENDING_DECISION = "AGUARDANDO DECISÃO HUMANA"
APPROVED_STATUS = "APROVADO"
ALLOWED_EQUIVALENCE_STATUSES = (PENDING_DECISION, APPROVED_STATUS)
EQUIVALENCE_CASES = (
    "one-to-one",
    "multi-instance",
    "unknown",
    "tipos ausentes",
    "tipos ambíguos",
    "singleton",
    "rótulos conflitantes",
)
PHASE_REF_RE = re.compile(r"\b(?:[CLDRHBMS]\d{2}|G\d)\b")

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
FIELD_RE = r"^\s*- {field}: (.+)$"
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


def parse_heading_blocks(text: str, pattern: str) -> list[tuple[str, list[str]]]:
    regex = re.compile(pattern)
    blocks: list[tuple[str, list[str]]] = []
    current: tuple[str, list[str]] | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = None
            continue
        match = regex.match(line)
        if match:
            current = (match.group(1), [])
            blocks.append(current)
        elif current is not None:
            current[1].append(line)
    return blocks


def phase_refs(text: str) -> set[str]:
    refs = {ref for ref in expand_ranges(text) if PHASE_REF_RE.fullmatch(ref)}
    refs.update(PHASE_REF_RE.findall(text))
    return refs


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


def check_estimand() -> tuple[list[str], int]:
    label = ESTIMAND.name
    if not ESTIMAND.exists():
        return [f"{label}: arquivo ausente"], 0
    text = ESTIMAND.read_text(encoding="utf-8")
    flat = " ".join(text.split())
    failures: list[str] = []
    for section in ESTIMAND_SECTIONS:
        if section not in text:
            failures.append(f"{label}: seção obrigatória ausente '{section}'")
    if "não são indivíduos biológicos independentes" not in flat:
        failures.append(f"{label}: falta a declaração de que seeds e neurônios não são indivíduos")
    for phrase in ("datasets observados", "população de moscas"):
        if phrase not in flat:
            failures.append(f"{label}: falta separar generalização; esperado '{phrase}'")
    fenced = re.findall(r"```[a-z]*\n(.*?)```", text, re.S)
    if not any(
        all(word in block.lower() for word in ("fonte", "alvo", "avaliador")) for block in fenced
    ):
        failures.append(f"{label}: diagrama do fluxo ausente ou sem FONTE/ALVO/AVALIADOR")

    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if "Vocabulário restrito" in line), None)
    if start is None:
        outside = text
    else:
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
        outside = "\n".join(lines[:start] + lines[end:])
    for term in RESTRICTED_TERMS:
        if term in outside.lower():
            failures.append(f"{label}: termo restrito '{term}' fora da seção de vocabulário restrito")

    known = {item_id for _, item_id in parse_items(PLAN.read_text(encoding="utf-8").splitlines())}
    refs = phase_refs(text)
    for ref in sorted(ref for ref in refs if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(refs)


def check_equivalence() -> tuple[list[str], int, int]:
    label = EQUIVALENCE.name
    if not EQUIVALENCE.exists():
        return [f"{label}: arquivo ausente"], 0, 0
    text = EQUIVALENCE.read_text(encoding="utf-8")
    flat = " ".join(text.split())
    failures: list[str] = []
    for section in EQUIVALENCE_SECTIONS:
        if section not in text:
            failures.append(f"{label}: seção obrigatória ausente '{section}'")
    for phrase in (
        "não é equivalência confirmada",
        "nunca é usado como feature de entrada",
    ):
        if phrase not in flat:
            failures.append(f"{label}: regra obrigatória ausente ('{phrase}')")
    for case in EQUIVALENCE_CASES:
        if case not in flat:
            failures.append(f"{label}: caso obrigatório ausente ('{case}')")

    statuses: set[str] = set()
    relations = parse_heading_blocks(text, r"^### (EQ-\d{2}) — (.+)$")
    seen_rel = set()
    for rel_id, block in relations:
        seen_rel.add(rel_id)
        if rel_id not in EQUIVALENCE_RELATIONS:
            failures.append(f"{label}: relação inesperada {rel_id}")
        for field in ("Definição operacional", "Classificação proposta", "Condição de validade", "Status"):
            if field_value(block, field) is None:
                failures.append(f"{label}: {rel_id} sem campo '{field}'")
        classification = field_value(block, "Classificação proposta")
        if classification is not None and not classification.startswith(RELATION_CLASSIFICATIONS):
            failures.append(f"{label}: {rel_id} classificação inválida '{classification}'")
        status = field_value(block, "Status")
        if status is not None:
            statuses.add(status)
            if status not in ALLOWED_EQUIVALENCE_STATUSES:
                failures.append(f"{label}: {rel_id} status inválido '{status}'")
    for rel_id in EQUIVALENCE_RELATIONS:
        if rel_id not in seen_rel:
            failures.append(f"{label}: relação obrigatória ausente {rel_id}")

    decisions = parse_heading_blocks(text, r"^### (DEC-EQ-\d{2}) — (.+)$")
    seen_dec = {dec_id for dec_id, _ in decisions}
    for number in range(1, 10):
        dec_id = f"DEC-EQ-{number:02d}"
        if dec_id not in seen_dec:
            failures.append(f"{label}: decisão obrigatória ausente {dec_id}")
    approved = 0
    for dec_id, block in decisions:
        status = field_value(block, "Status")
        if status is not None:
            statuses.add(status)
            if status not in ALLOWED_EQUIVALENCE_STATUSES:
                failures.append(f"{label}: {dec_id} status inválido '{status}'")
            if status == APPROVED_STATUS:
                approved += 1
        if field_value(block, "Decisão") is None:
            failures.append(f"{label}: {dec_id} sem campo 'Decisão'")
        if field_value(block, "Recomendação") is None:
            failures.append(f"{label}: {dec_id} sem campo 'Recomendação'")

    for line in text.splitlines():
        match = re.match(r"^\s*- Status: (.+?)\s*$", line)
        if match:
            status = match.group(1).strip().rstrip(".")
            if status not in ALLOWED_EQUIVALENCE_STATUSES:
                failures.append(f"{label}: status '{status}' não permitido")

    if APPROVED_STATUS in statuses:
        section = re.search(r"## 9\. Aprovação humana\n(.*?)(?=\n## |\Z)", text, re.S)
        if section is None:
            failures.append(f"{label}: status APROVADO sem seção de aprovação humana")
        else:
            approval_lines = section.group(1).splitlines()
            for field in APPROVAL_FIELDS:
                if field_value(approval_lines, field) is None:
                    failures.append(f"{label}: aprovação humana sem campo '{field}'")
            approver = field_value(approval_lines, "Aprovador")
            if approver is not None and not any(
                word in approver.lower() for word in ("humano", "revisor")
            ):
                failures.append(f"{label}: aprovador não identificado como humano/revisor: '{approver}'")

    known = {item_id for _, item_id in parse_items(PLAN.read_text(encoding="utf-8").splitlines())}
    refs = phase_refs(text)
    for ref in sorted(ref for ref in refs if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(decisions), approved


def check_outcomes() -> tuple[list[str], int]:
    label = OUTCOMES.name
    if not OUTCOMES.exists():
        return [f"{label}: arquivo ausente"], 0
    text = OUTCOMES.read_text(encoding="utf-8")
    flat = " ".join(text.split()).lower()
    failures: list[str] = []
    for section in OUTCOMES_SECTIONS:
        if section not in text:
            failures.append(f"{label}: seção obrigatória ausente '{section}'")
    for token in OUTCOMES_TOKENS:
        if token.lower() not in flat:
            failures.append(f"{label}: métrica/controle obrigatório ausente ('{token}')")
    for state in OUTCOMES_STATES:
        if not re.search(rf"^- \*\*{state}:\*\*", text, re.M):
            failures.append(f"{label}: estado obrigatório ausente ou fora do formato: {state}")
    for rule in OUTCOMES_RULES:
        if rule not in flat:
            failures.append(f"{label}: proibição obrigatória ausente ('{rule}')")

    known = {item_id for _, item_id in parse_items(PLAN.read_text(encoding="utf-8").splitlines())}
    refs = phase_refs(text)
    for ref in sorted(ref for ref in refs if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(OUTCOMES_TOKENS)


def check_paths() -> tuple[list[str], int]:
    failures: list[str] = []
    total = 0
    for path in (GLOSSARY, CLAIMS, RISKS, ESTIMAND, EQUIVALENCE, OUTCOMES):
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
    estimand_failures, estimand_refs = check_estimand()
    equivalence_failures, equivalence_decisions, equivalence_approved = check_equivalence()
    outcomes_failures, outcomes_tokens = check_outcomes()
    failures += (
        ref_failures + path_failures + estimand_failures + equivalence_failures + outcomes_failures
    )

    if failures:
        for failure in failures:
            print(f"FALHA: {failure}")
        print(f"RESULTADO: {len(failures)} falha(s)")
        return 1
    print(f"OK: GLOSSARIO.md com {glossary_count} termos e os {len(REQUIRED_GLOSSARY_TERMS)} obrigatórios")
    print(f"OK: CLAIMS.md com {claim_count} claims, todos com status e evidência")
    print(f"OK: RISCOS.md com {risk_count} riscos, todos com campos completos")
    print(f"OK: PERGUNTA-E-ESTIMANDO.md com seções obrigatórias e {estimand_refs} referências de fase")
    print(
        f"OK: EQUIVALENCIA.md com 5 relações e {equivalence_decisions} decisões "
        f"({equivalence_approved} aprovadas por humano)"
    )
    print(
        f"OK: DESFECHOS-E-FALSIFICACAO.md com {len(OUTCOMES_STATES)} estados e "
        f"{outcomes_tokens} marcadores obrigatórios"
    )
    print(f"OK: {refs} referências de fase resolvidas contra o plano")
    print(f"OK: {paths} caminhos de arquivo citados e existentes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
