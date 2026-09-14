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

THREATS = RESEARCH / "AMEACAS-A-VALIDADE.md"
THREAT_SECTIONS = (
    "## 1. Estado e escopo",
    "## 2. Método de classificação",
    "## 3. Ameaças",
    "## 4. Controles transversais",
    "## 5. Mapa para o registro de riscos",
    "## 6. Limitações",
)
THREAT_TOPICS = (
    "IDs/ordem",
    "grau",
    "coordenadas/regiões",
    "rótulos derivados de conectividade/morfologia",
    "crosswalk circular",
    "normalização no alvo",
    "amostragem de negativos",
    "duplicação de neurônios",
    "sexo",
    "tecido",
    "cobertura",
    "reconstrução",
    "threshold",
    "tuning pós-unseal",
)
THREAT_FIELDS = (
    "Tema",
    "Categoria",
    "Severidade provisória",
    "Cenário",
    "Teste de detecção planejado",
    "Mitigação planejada",
    "Risco residual",
    "Status",
)
THREAT_SEVERITIES = ("alta", "média", "baixa")
THREAT_STATUSES = ("aberto", "em mitigação", "mitigado com artefato")
THREAT_PROHIBITION = "sem teste ou artefato"
RSK_ID_RE = re.compile(r"RSK-\d{3}")

LADDER = RESEARCH / "ESCADA-DE-CLAIMS.md"
INFEASIBLE = RESEARCH / "RELATORIO-INVIABILIDADE-ESQUELETO.md"
LADDER_SECTIONS = (
    "## 1. Regras gerais",
    "## 2. Níveis de evidência e linguagem",
    "## 3. Saídas negativas",
    "## 4. Proibições e limitações",
)
LADDER_LEVELS = ("NIV-01", "NIV-02", "NIV-03", "NIV-04", "NIV-05")
LADDER_TOKENS = (
    "sinal topológico",
    "transferência entre dois datasets",
    "cross-individual",
    "multi-connectome",
    "potencialmente novo",
    "resultado negativo",
    "benchmark inviável",
)
LADDER_RULES = (
    "não promete paper",
    "nem causalidade",
    "seeds não são indivíduos",
    "dois espécimes independentes",
)
LADDER_LEVEL_FIELDS = (
    "Alegação permitida",
    "Evidência mínima",
    "Fase de decisão",
    "Não autoriza",
    "Claims relacionados",
    "Status",
)
LADDER_STATUSES = ("bloqueado", "liberado com evidência")
INFEASIBLE_SECTIONS = (
    "## Decisão",
    "## Evidência que motivou",
    "## O que foi refutado",
    "## O que permanece aberto",
    "## Reformulação proposta",
    "## Publicação negativa",
    "## Limitações",
)
CLM_ID_RE = re.compile(r"CLM-\d{3}")

GATE_G0 = ROOT / "docs" / "gates" / "G0-CONTRATO.md"
GATE_SECTIONS = (
    "## Pacote de revisão",
    "## Critérios",
    "## Riscos e divergências",
    "## Escopo liberado",
    "## Assinaturas",
)
GATE_HEADER_FIELDS = ("Data/hora e fuso", "Commit e estado dirty", "Revisores", "Decisão")
GATE_SIGNATURE_FIELDS = (
    "Responsável científico",
    "Custodiante do alvo, quando aplicável",
    "Revisor de método/estatística",
)
CRITERION_RE = re.compile(r"^- .+: `(PASS|FAIL|NÃO VERIFICADO)` — .+$")

LIT_PROTOCOL = ROOT / "research" / "literature" / "PROTOCOL.md"
LIT_SECTIONS = (
    "## 1. Objetivo e perguntas",
    "## 2. Bases e ferramentas",
    "## 3. Strings de busca",
    "## 4. Período e idiomas",
    "## 5. Inclusão e exclusão",
    "## 6. Deduplicação",
    "## 7. Esquema do ledger",
    "## 8. Triagem e extração",
    "## 9. Reprodutibilidade e atualização",
    "## 10. Regras de evidência",
    "## 11. Versões do protocolo",
)
LIT_QUERIES = ("Q0", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7")
LIT_LEDGER = ROOT / "research" / "literature" / "LEDGER.tsv"
LIT_LEDGER_COLUMNS = (
    "lit_id",
    "run_date",
    "base",
    "query_id",
    "titulo",
    "autores",
    "ano",
    "venue",
    "tipo",
    "doi",
    "url",
    "versao",
    "status_triagem",
    "motivo_exclusao",
    "claims_relacionados",
    "dataset",
    "claim_atomico",
    "fase",
    "nota",
)
LIT_TRIAGE_STATUSES = ("triagem", "incluido", "excluido", "pendente_fulltext")
LIT_CANDIDATES = ("FlyWire/FAFB", "hemibrain", "BANC", "MANC", "MAOL", "MCNS")
LIT_DATASET_EXTRA = ("múltiplos", "geral", "—")
ALIGNMENT = ROOT / "research" / "literature" / "ALIGNMENT.md"
ALIGNMENT_SECTIONS = (
    "## 1. Estado e escopo",
    "## 2. Métodos",
    "## 3. Síntese para o zero-shot",
    "## 4. Limitações",
)
ALIGNMENT_FIELDS = (
    "Referência",
    "Input",
    "Âncoras/rótulos",
    "Supervisão",
    "Caráter",
    "Datasets",
    "Código/licença",
    "Métrica",
    "Inadequações ao zero-shot",
    "Status",
)
ALIGNMENT_SUPERVISIONS = (
    "não supervisionado",
    "supervisionado",
    "auto-supervisionado",
    "híbrido",
)
CELL_TYPE = ROOT / "research" / "literature" / "CELL-TYPE.md"
CELL_TYPE_SECTIONS = (
    "## 1. Estado e escopo",
    "## 2. Modalidades",
    "## 3. Proveniência dos rótulos",
    "## 4. Síntese e validade",
    "## 5. Limitações",
)
CELL_TYPE_MODALITIES = ("CT-M1", "CT-M2", "CT-M3", "CT-M4", "CT-M5", "CT-M6")
CELL_TYPE_MODALITY_TOPICS = (
    "Connectivity-only",
    "Morphology-only",
    "Posição",
    "Região",
    "Neurotransmissor",
    "Função",
)
CELL_TYPE_MODALITY_FIELDS = (
    "Referência",
    "Evidência a favor",
    "Evidência contra",
    "Condições de validade",
    "Status",
)
CELL_TYPE_PROVENANCE_FIELDS = ("Como o rótulo foi produzido", "Fonte", "Status")
CELL_TYPE_PROHIBITION = "correlação dentro de um indivíduo não prova transferência"
SSL_REVIEW = ROOT / "research" / "literature" / "SSL-GRAFOS.md"
SSL_SECTIONS = (
    "## 1. Estado e escopo",
    "## 2. Famílias de objetivos",
    "## 3. Embeddings de connectomas",
    "## 4. Alegações de graph foundation models",
    "## 5. Síntese e limitações",
)
SSL_FAMILIES = ("SSL-01", "SSL-02", "SSL-03", "SSL-04", "SSL-05")
SSL_FAMILY_TOPICS = (
    "Masked edge/weight",
    "Neighborhood reconstruction",
    "Contrastive",
    "Autoencoders",
    "Link prediction",
)
SSL_FAMILY_FIELDS = (
    "Referência",
    "Hipótese de sinal",
    "Atalhos prováveis",
    "Custo",
    "Grafo dirigido/ponderado",
    "Capacidade indutiva",
    "Status",
)
SSL_CEM_FIELDS = ("Referência", "Input", "Resultado relatado", "Limitação", "Status")
SSL_GFM_FIELDS = ("Referência", "Alegação", "Risco/limitação", "Status")
SSL_RULES = ("não assume transformer superior", "não são comparáveis sem alinhamento")
METHODS = ROOT / "research" / "literature" / "METHODS.md"
METHODS_SECTIONS = (
    "## 1. Estado e escopo",
    "## 2. Matriz de métodos",
    "## 3. Notas de execução e licenças",
    "## 4. Limitações",
)
METHODS_IDS = tuple(f"M-{number:02d}" for number in range(1, 16))
METHODS_TOPICS = (
    "Random",
    "Majority",
    "Degree-only",
    "Handcrafted",
    "Node2Vec",
    "DeepWalk",
    "Espectral",
    "MLP",
    "GraphSAGE",
    "GIN",
    "GAT",
    "Relacional",
    "Transformer",
    "NBLAST",
    "NeuronBridge",
)
METHODS_FIELDS = (
    "Referência",
    "Parâmetros",
    "Complexidade",
    "Dependências",
    "Licença",
    "Manutenção",
    "Suporte sparse/sampling",
    "Estimativa 8 GB",
    "Incompatibilidades",
    "Status",
)
METHODS_RULE = "nenhum pacote foi instalado"
LIT_ID_RE = re.compile(r"^LIT-\d{4}$")
LIT_QUERY_LOG = ROOT / "research" / "literature" / "QUERY-LOG.tsv"
LIT_QUERY_LOG_COLUMNS = (
    "run_date",
    "query_id",
    "base",
    "string_exata",
    "filtros",
    "periodo",
    "idioma",
    "n_resultados",
    "export_formato",
    "hash_export",
    "operador",
    "observacoes",
)
LIT_QUERY_FIELDS = ("Objetivo", "String", "Bases", "Janela")
LIT_TOPICS = (
    "neuron matching",
    "connectome alignment",
    "cell type",
    "graph representation learning",
    "cross-animal",
    "morfologia",
    "embeddings de connectomas",
)
LIT_BASES = (
    "Europe PMC",
    "PubMed",
    "arXiv",
    "bioRxiv",
    "Semantic Scholar",
    "OpenAlex",
    "Crossref",
    "DBLP",
)
LIT_LEDGER_FIELDS = (
    "lit_id",
    "query_id",
    "status_triagem",
    "motivo_exclusao",
    "claims_relacionados",
    "hash_export",
)
LIT_RULES = ("apenas para descoberta", "segundo executor", "não prova novidade")

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
PATH_RE = re.compile(r"`((?:docs|tools|research)/[A-Za-z0-9_./-]+\.(?:md|py|yaml))`")
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


def check_threats() -> tuple[list[str], int]:
    label = THREATS.name
    if not THREATS.exists():
        return [f"{label}: arquivo ausente"], 0
    text = THREATS.read_text(encoding="utf-8")
    failures: list[str] = []
    for section in THREAT_SECTIONS:
        if section not in text:
            failures.append(f"{label}: seção obrigatória ausente '{section}'")
    if THREAT_PROHIBITION not in text:
        failures.append(f"{label}: falta a proibição '{THREAT_PROHIBITION}'")

    known_risks = (
        {entry_id for entry_id, _, _ in parse_entries(RISKS, "RSK", 3)} if RISKS.exists() else set()
    )
    blocks = parse_heading_blocks(text, r"^### (AMA-\d{2}) — (.+)$")
    seen_topics: set[str] = set()
    for ama_id, block in blocks:
        for field in THREAT_FIELDS:
            if field_value(block, field) is None:
                failures.append(f"{label}: {ama_id} sem campo '{field}'")
        topic = field_value(block, "Tema")
        if topic is not None:
            seen_topics.add(topic)
            if topic not in THREAT_TOPICS:
                failures.append(f"{label}: {ama_id} tema inesperado '{topic}'")
        severity = field_value(block, "Severidade provisória")
        if severity is not None and severity not in THREAT_SEVERITIES:
            failures.append(f"{label}: {ama_id} severidade inválida '{severity}'")
        status = field_value(block, "Status")
        if status is not None and status not in THREAT_STATUSES:
            failures.append(f"{label}: {ama_id} status inválido '{status}'")
        if status == "mitigado com artefato" and field_value(block, "Artefato") is None:
            failures.append(f"{label}: {ama_id} mitigado sem campo Artefato")
        related = field_value(block, "Riscos relacionados")
        if related is not None:
            for rsk in RSK_ID_RE.findall(related):
                if known_risks and rsk not in known_risks:
                    failures.append(f"{label}: {ama_id} referencia risco inexistente '{rsk}'")
    for topic in THREAT_TOPICS:
        if topic not in seen_topics:
            failures.append(f"{label}: tema obrigatório ausente ('{topic}')")

    known = {item_id for _, item_id in parse_items(PLAN.read_text(encoding="utf-8").splitlines())}
    refs = phase_refs(text)
    for ref in sorted(ref for ref in refs if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(blocks)


def check_claim_ladder() -> tuple[list[str], int]:
    label = LADDER.name
    if not LADDER.exists():
        return [f"{label}: arquivo ausente"], 0
    text = LADDER.read_text(encoding="utf-8")
    flat = " ".join(text.split()).lower()
    failures: list[str] = []
    for section in LADDER_SECTIONS:
        if section not in text:
            failures.append(f"{label}: seção obrigatória ausente '{section}'")
    for token in LADDER_TOKENS:
        if token.lower() not in flat:
            failures.append(f"{label}: nível/token obrigatório ausente ('{token}')")
    for rule in LADDER_RULES:
        if rule not in flat:
            failures.append(f"{label}: regra obrigatória ausente ('{rule}')")

    blocks = parse_heading_blocks(text, r"^### (NIV-\d{2}) — (.+)$")
    seen: set[str] = set()
    for niv_id, block in blocks:
        seen.add(niv_id)
        if niv_id not in LADDER_LEVELS:
            failures.append(f"{label}: nível inesperado {niv_id}")
        for field in LADDER_LEVEL_FIELDS:
            if field_value(block, field) is None:
                failures.append(f"{label}: {niv_id} sem campo '{field}'")
        status = field_value(block, "Status")
        if status is not None and status not in LADDER_STATUSES:
            failures.append(f"{label}: {niv_id} status inválido '{status}'")
        if status == "liberado com evidência":
            evidence = field_value(block, "Evidência congelada")
            if evidence is None or "a preencher" in evidence.lower():
                failures.append(f"{label}: {niv_id} liberado sem campo 'Evidência congelada'")
    for niv_id in LADDER_LEVELS:
        if niv_id not in seen:
            failures.append(f"{label}: nível obrigatório ausente {niv_id}")

    if not INFEASIBLE.exists():
        failures.append(f"{INFEASIBLE.name}: arquivo ausente")
    else:
        skeleton = INFEASIBLE.read_text(encoding="utf-8")
        for section in INFEASIBLE_SECTIONS:
            if section not in skeleton:
                failures.append(f"{INFEASIBLE.name}: seção ausente '{section}'")
        if "A preencher" not in skeleton:
            failures.append(f"{INFEASIBLE.name}: esqueleto sem marcadores 'A preencher'")

    known_claims = (
        {entry_id for entry_id, _, _ in parse_entries(CLAIMS, "CLM", 3)} if CLAIMS.exists() else set()
    )
    for clm in sorted(set(CLM_ID_RE.findall(text))):
        if known_claims and clm not in known_claims:
            failures.append(f"{label}: referencia claim inexistente '{clm}'")

    known = {item_id for _, item_id in parse_items(PLAN.read_text(encoding="utf-8").splitlines())}
    refs = phase_refs(text)
    for ref in sorted(ref for ref in refs if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(blocks)


def check_gate_package() -> tuple[list[str], int, str]:
    label = GATE_G0.name
    if not GATE_G0.exists():
        return [f"{label}: arquivo ausente"], 0, "AUSENTE"
    text = GATE_G0.read_text(encoding="utf-8")
    lines = text.splitlines()
    failures: list[str] = []
    for section in GATE_SECTIONS:
        if section not in text:
            failures.append(f"{label}: seção obrigatória ausente '{section}'")
    for field in GATE_HEADER_FIELDS:
        if field_value(lines, field) is None:
            failures.append(f"{label}: cabeçalho sem campo '{field}'")
    decision = field_value(lines, "Decisão")
    if decision is None or not decision.startswith(("AGUARDAR", "GO")):
        failures.append(f"{label}: decisão deve começar com AGUARDAR ou GO")
    pending = decision is not None and decision.startswith("AGUARDAR")
    approved = decision is not None and decision.startswith("GO")
    criteria = [line for line in lines if CRITERION_RE.match(line)]
    if len(criteria) < 6:
        failures.append(f"{label}: esperados ao menos 6 critérios no formato do modelo (achados {len(criteria)})")
    if pending and not any("`NÃO VERIFICADO`" in line for line in criteria):
        failures.append(f"{label}: nenhum critério marcado 'NÃO VERIFICADO' com decisão pendente")
    if approved and any("`NÃO VERIFICADO`" in line for line in criteria):
        failures.append(f"{label}: decisão GO com critério ainda 'NÃO VERIFICADO'")
    if any("`FAIL`" in line for line in criteria):
        failures.append(f"{label}: critério FAIL exige decisão REFORMULAR/NO-GO, não GO/AGUARDAR")

    start = next((i for i, line in enumerate(lines) if line.startswith("## Assinaturas")), None)
    signature_lines = lines[start:] if start is not None else []
    signature_block = "\n".join(signature_lines)
    for field in GATE_SIGNATURE_FIELDS:
        value = field_value(signature_lines, field)
        if value is None:
            failures.append(f"{label}: assinatura sem campo '{field}'")
            continue
        if pending and "a preencher" not in value.lower():
            failures.append(f"{label}: assinatura '{field}' preenchida antes da revisão humana")
        if approved and "a preencher" in value.lower():
            failures.append(f"{label}: assinatura '{field}' ainda pendente com decisão GO")
    if approved and "2026-09-14" not in signature_block:
        failures.append(f"{label}: assinaturas sem data da revisão humana")

    plan_lines = PLAN.read_text(encoding="utf-8").splitlines()
    g0_line = next((line for line in plan_lines if "**G0 —" in line), None)
    if g0_line is None:
        failures.append(f"{label}: item G0 não encontrado no plano")
    elif pending and not g0_line.startswith("- [ ]"):
        failures.append(f"{label}: G0 marcado como concluído enquanto a decisão é AGUARDAR")
    elif approved and g0_line.startswith("- [ ]"):
        failures.append(f"{label}: decisão GO exige G0 marcado [x] no plano")

    known = {item_id for _, item_id in parse_items(plan_lines)}
    refs = phase_refs(text)
    for ref in sorted(ref for ref in refs if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    state = "GO" if approved else "AGUARDAR"
    return failures, len(criteria), state


def check_literature_protocol() -> tuple[list[str], int]:
    label = "PROTOCOL.md"
    if not LIT_PROTOCOL.exists():
        return [f"{label}: arquivo ausente em research/literature/"], 0
    text = LIT_PROTOCOL.read_text(encoding="utf-8")
    flat = " ".join(text.split()).lower()
    failures: list[str] = []
    for section in LIT_SECTIONS:
        if section not in text:
            failures.append(f"{label}: seção obrigatória ausente '{section}'")
    queries = parse_heading_blocks(text, r"^### (Q\d) — (.+)$")
    seen: set[str] = set()
    for query_id, block in queries:
        seen.add(query_id)
        if query_id not in LIT_QUERIES:
            failures.append(f"{label}: consulta inesperada {query_id}")
        for field in LIT_QUERY_FIELDS:
            if field_value(block, field) is None:
                failures.append(f"{label}: {query_id} sem campo '{field}'")
    for query_id in LIT_QUERIES:
        if query_id not in seen:
            failures.append(f"{label}: consulta obrigatória ausente {query_id}")
    for topic in LIT_TOPICS:
        if topic.lower() not in flat:
            failures.append(f"{label}: tema obrigatório ausente ('{topic}')")
    for base in LIT_BASES:
        if base.lower() not in flat:
            failures.append(f"{label}: base obrigatória ausente ('{base}')")
    for field in LIT_LEDGER_FIELDS:
        if field.lower() not in flat:
            failures.append(f"{label}: campo de ledger/log ausente ('{field}')")
    for rule in LIT_RULES:
        if rule not in flat:
            failures.append(f"{label}: regra obrigatória ausente ('{rule}')")
    known = {item_id for _, item_id in parse_items(PLAN.read_text(encoding="utf-8").splitlines())}
    refs = phase_refs(text)
    for ref in sorted(ref for ref in refs if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(queries)


def check_literature_ledger() -> tuple[list[str], int, int]:
    label = "LEDGER.tsv"
    if not LIT_LEDGER.exists():
        return [f"{label}: arquivo ausente em research/literature/"], 0, 0
    rows = [
        line.split("\t")
        for line in LIT_LEDGER.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(rows) < 2:
        return [f"{label}: sem registros"], 0, 0
    header = rows[0]
    failures: list[str] = []
    for column in LIT_LEDGER_COLUMNS:
        if column not in header:
            failures.append(f"{label}: coluna obrigatória ausente '{column}'")
    if failures:
        return failures, len(rows) - 1, 0
    index = {name: header.index(name) for name in header}
    seen: set[str] = set()
    per_candidate_included = {candidate: 0 for candidate in LIT_CANDIDATES}
    for number, row in enumerate(rows[1:], 2):
        if len(row) != len(header):
            failures.append(f"{label}:{number}: {len(row)} colunas para {len(header)} no cabeçalho")
            continue
        lit_id = row[index["lit_id"]]
        if not LIT_ID_RE.match(lit_id):
            failures.append(f"{label}:{number}: lit_id inválido '{lit_id}'")
        if lit_id in seen:
            failures.append(f"{label}:{number}: lit_id duplicado '{lit_id}'")
        seen.add(lit_id)
        status = row[index["status_triagem"]]
        if status not in LIT_TRIAGE_STATUSES:
            failures.append(f"{label}:{number}: status inválido '{status}'")
        query_id = row[index["query_id"]]
        if query_id not in LIT_QUERIES:
            failures.append(f"{label}:{number}: query_id inválido '{query_id}'")
        dataset = row[index["dataset"]]
        if dataset not in LIT_CANDIDATES and dataset not in LIT_DATASET_EXTRA:
            failures.append(f"{label}:{number}: dataset inesperado '{dataset}'")
        elif status == "incluido":
            if not row[index["doi"]].strip() and not row[index["url"]].strip():
                failures.append(f"{label}:{number}: incluído sem DOI nem URL")
            if row[index["claim_atomico"]].strip() in ("", "—"):
                failures.append(f"{label}:{number}: incluído sem claim_atomico")
            if dataset in LIT_CANDIDATES:
                per_candidate_included[dataset] += 1
    for candidate, count in per_candidate_included.items():
        if count == 0:
            failures.append(f"{label}: candidato sem fonte oficial incluída: {candidate}")

    log_label = "QUERY-LOG.tsv"
    log_rows: list[list[str]] = []
    if not LIT_QUERY_LOG.exists():
        failures.append(f"{log_label}: arquivo ausente em research/literature/")
    else:
        log_rows = [
            line.split("\t")
            for line in LIT_QUERY_LOG.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if len(log_rows) < 2:
            failures.append(f"{log_label}: sem consultas registradas")
        else:
            for column in LIT_QUERY_LOG_COLUMNS:
                if column not in log_rows[0]:
                    failures.append(f"{log_label}: coluna obrigatória ausente '{column}'")
    return failures, len(rows) - 1, max(len(log_rows) - 1, 0)


def _ledger_rows() -> list[list[str]]:
    if not LIT_LEDGER.exists():
        return []
    return [
        line.split("\t")
        for line in LIT_LEDGER.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def check_alignment_review() -> tuple[list[str], int]:
    label = "ALIGNMENT.md"
    if not ALIGNMENT.exists():
        return [f"{label}: arquivo ausente em research/literature/"], 0
    text = ALIGNMENT.read_text(encoding="utf-8")
    failures: list[str] = []
    for section in ALIGNMENT_SECTIONS:
        if section not in text:
            failures.append(f"{label}: seção obrigatória ausente '{section}'")

    rows = _ledger_rows()
    known_lit: set[str] = set()
    if len(rows) >= 2 and "lit_id" in rows[0]:
        index = rows[0].index("lit_id")
        known_lit = {row[index] for row in rows[1:] if len(row) > index}

    blocks = parse_heading_blocks(text, r"^### (ALN-\d{2}) — (.+)$")
    if len(blocks) < 5:
        failures.append(f"{label}: esperados ao menos 5 métodos (achados {len(blocks)})")
    for aln_id, block in blocks:
        for field in ALIGNMENT_FIELDS:
            if field_value(block, field) is None:
                failures.append(f"{label}: {aln_id} sem campo '{field}'")
        reference = field_value(block, "Referência") or ""
        ref_ids = sorted(set(re.findall(r"LIT-\d{4}", reference)))
        if not ref_ids:
            failures.append(f"{label}: {aln_id} sem referência LIT-*")
        for lit_id in ref_ids:
            if known_lit and lit_id not in known_lit:
                failures.append(f"{label}: {aln_id} referencia ledger inexistente '{lit_id}'")
        supervision = field_value(block, "Supervisão")
        anchors = (field_value(block, "Âncoras/rótulos") or "").lower()
        if supervision is not None:
            if not supervision.startswith(ALIGNMENT_SUPERVISIONS):
                failures.append(f"{label}: {aln_id} supervisão inválida '{supervision}'")
            if supervision.startswith("supervisionado") and anchors.startswith("nenhuma"):
                failures.append(f"{label}: {aln_id} supervisionado não pode declarar 'nenhuma' âncora")
            if (
                supervision.startswith("não supervisionado")
                and "semente" in anchors
                and "nenhuma" not in anchors
            ):
                failures.append(f"{label}: {aln_id} não supervisionado não pode depender de sementes")

    if len(rows) >= 2 and "query_id" in rows[0] and "fase" in rows[0]:
        qi, fi = rows[0].index("query_id"), rows[0].index("fase")
        queries = {
            row[qi] for row in rows[1:] if len(row) > max(qi, fi) and row[fi] == "L03"
        }
        for query in ("Q1", "Q2"):
            if query not in queries:
                failures.append(f"{label}: ledger sem consulta {query} em L03")

    known = {item_id for _, item_id in parse_items(PLAN.read_text(encoding="utf-8").splitlines())}
    refs = phase_refs(text)
    for ref in sorted(ref for ref in refs if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(blocks)


def check_cell_type_review() -> tuple[list[str], int]:
    label = "CELL-TYPE.md"
    if not CELL_TYPE.exists():
        return [f"{label}: arquivo ausente em research/literature/"], 0
    text = CELL_TYPE.read_text(encoding="utf-8")
    flat = " ".join(text.split()).lower()
    failures: list[str] = []
    for section in CELL_TYPE_SECTIONS:
        if section not in text:
            failures.append(f"{label}: seção obrigatória ausente '{section}'")
    if CELL_TYPE_PROHIBITION not in flat:
        failures.append(f"{label}: falta a proibição '{CELL_TYPE_PROHIBITION}'")
    for topic in CELL_TYPE_MODALITY_TOPICS:
        if topic.lower() not in flat:
            failures.append(f"{label}: modalidade obrigatória ausente ('{topic}')")

    rows = _ledger_rows()
    known_lit: set[str] = set()
    if len(rows) >= 2 and "lit_id" in rows[0]:
        index = rows[0].index("lit_id")
        known_lit = {row[index] for row in rows[1:] if len(row) > index}

    modalities = parse_heading_blocks(text, r"^### (CT-M\d) — (.+)$")
    seen_modalities: set[str] = set()
    for mod_id, block in modalities:
        seen_modalities.add(mod_id)
        if mod_id not in CELL_TYPE_MODALITIES:
            failures.append(f"{label}: modalidade inesperada {mod_id}")
        for field in CELL_TYPE_MODALITY_FIELDS:
            if field_value(block, field) is None:
                failures.append(f"{label}: {mod_id} sem campo '{field}'")
        reference = field_value(block, "Referência") or ""
        refs = sorted(set(re.findall(r"LIT-\d{4}", reference)))
        if not refs:
            failures.append(f"{label}: {mod_id} sem referência LIT-*")
        for lit_id in refs:
            if known_lit and lit_id not in known_lit:
                failures.append(f"{label}: {mod_id} referencia ledger inexistente '{lit_id}'")
    for mod_id in CELL_TYPE_MODALITIES:
        if mod_id not in seen_modalities:
            failures.append(f"{label}: modalidade obrigatória ausente {mod_id}")

    provenance = parse_heading_blocks(text, r"^### (CT-P\d) — (.+)$")
    if len(provenance) < 3:
        failures.append(f"{label}: esperados ao menos 3 registros de proveniência (achados {len(provenance)})")
    for prov_id, block in provenance:
        for field in CELL_TYPE_PROVENANCE_FIELDS:
            if field_value(block, field) is None:
                failures.append(f"{label}: {prov_id} sem campo '{field}'")
        source = field_value(block, "Fonte") or ""
        refs = sorted(set(re.findall(r"LIT-\d{4}", source)))
        if not refs:
            failures.append(f"{label}: {prov_id} sem fonte LIT-*")
        for lit_id in refs:
            if known_lit and lit_id not in known_lit:
                failures.append(f"{label}: {prov_id} referencia ledger inexistente '{lit_id}'")

    if len(rows) >= 2 and "query_id" in rows[0] and "fase" in rows[0]:
        qi, fi = rows[0].index("query_id"), rows[0].index("fase")
        queries = {
            row[qi] for row in rows[1:] if len(row) > max(qi, fi) and row[fi] == "L04"
        }
        for query in ("Q3", "Q6"):
            if query not in queries:
                failures.append(f"{label}: ledger sem consulta {query} em L04")

    known = {item_id for _, item_id in parse_items(PLAN.read_text(encoding="utf-8").splitlines())}
    refs = phase_refs(text)
    for ref in sorted(ref for ref in refs if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(modalities)


def _known_lit_ids(rows: list[list[str]]) -> set[str]:
    if len(rows) >= 2 and "lit_id" in rows[0]:
        index = rows[0].index("lit_id")
        return {row[index] for row in rows[1:] if len(row) > index}
    return set()


def check_ssl_review() -> tuple[list[str], int]:
    label = "SSL-GRAFOS.md"
    if not SSL_REVIEW.exists():
        return [f"{label}: arquivo ausente em research/literature/"], 0
    text = SSL_REVIEW.read_text(encoding="utf-8")
    flat = " ".join(text.split()).lower()
    failures: list[str] = []
    for section in SSL_SECTIONS:
        if section not in text:
            failures.append(f"{label}: seção obrigatória ausente '{section}'")
    for topic in SSL_FAMILY_TOPICS:
        if topic.lower() not in flat:
            failures.append(f"{label}: família obrigatória ausente ('{topic}')")
    for rule in SSL_RULES:
        if rule not in flat:
            failures.append(f"{label}: proibição obrigatória ausente ('{rule}')")

    rows = _ledger_rows()
    known_lit = _known_lit_ids(rows)

    families = parse_heading_blocks(text, r"^### (SSL-\d{2}) — (.+)$")
    seen: set[str] = set()
    for ssl_id, block in families:
        seen.add(ssl_id)
        if ssl_id not in SSL_FAMILIES:
            failures.append(f"{label}: família inesperada {ssl_id}")
        for field in SSL_FAMILY_FIELDS:
            if field_value(block, field) is None:
                failures.append(f"{label}: {ssl_id} sem campo '{field}'")
        reference = field_value(block, "Referência") or ""
        for lit_id in sorted(set(re.findall(r"LIT-\d{4}", reference))):
            if known_lit and lit_id not in known_lit:
                failures.append(f"{label}: {ssl_id} referencia ledger inexistente '{lit_id}'")
        if not re.search(r"LIT-\d{4}", reference):
            failures.append(f"{label}: {ssl_id} sem referência LIT-*")
    for ssl_id in SSL_FAMILIES:
        if ssl_id not in seen:
            failures.append(f"{label}: família obrigatória ausente {ssl_id}")

    cem_blocks = parse_heading_blocks(text, r"^### (CEM-\d{2}) — (.+)$")
    if len(cem_blocks) < 1:
        failures.append(f"{label}: nenhum registro de connectome embedding (CEM-*)")
    for cem_id, block in cem_blocks:
        for field in SSL_CEM_FIELDS:
            if field_value(block, field) is None:
                failures.append(f"{label}: {cem_id} sem campo '{field}'")
        reference = field_value(block, "Referência") or ""
        if not re.search(r"LIT-\d{4}", reference):
            failures.append(f"{label}: {cem_id} sem referência LIT-*")

    gfm_blocks = parse_heading_blocks(text, r"^### (GFM-\d{2}) — (.+)$")
    if len(gfm_blocks) < 2:
        failures.append(f"{label}: esperados ao menos 2 registros de GFM (achados {len(gfm_blocks)})")
    for gfm_id, block in gfm_blocks:
        for field in SSL_GFM_FIELDS:
            if field_value(block, field) is None:
                failures.append(f"{label}: {gfm_id} sem campo '{field}'")
        reference = field_value(block, "Referência") or ""
        if not re.search(r"LIT-\d{4}", reference):
            failures.append(f"{label}: {gfm_id} sem referência LIT-*")

    if len(rows) >= 2 and "query_id" in rows[0] and "fase" in rows[0]:
        qi, fi = rows[0].index("query_id"), rows[0].index("fase")
        queries = {
            row[qi] for row in rows[1:] if len(row) > max(qi, fi) and row[fi] == "L05"
        }
        for query in ("Q4", "Q7"):
            if query not in queries:
                failures.append(f"{label}: ledger sem consulta {query} em L05")

    known = {item_id for _, item_id in parse_items(PLAN.read_text(encoding="utf-8").splitlines())}
    refs = phase_refs(text)
    for ref in sorted(ref for ref in refs if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(families)


def check_methods_matrix() -> tuple[list[str], int]:
    label = "METHODS.md"
    if not METHODS.exists():
        return [f"{label}: arquivo ausente em research/literature/"], 0
    text = METHODS.read_text(encoding="utf-8")
    flat = " ".join(text.split()).lower()
    failures: list[str] = []
    for section in METHODS_SECTIONS:
        if section not in text:
            failures.append(f"{label}: seção obrigatória ausente '{section}'")
    for topic in METHODS_TOPICS:
        if topic.lower() not in flat:
            failures.append(f"{label}: método obrigatório ausente ('{topic}')")
    if METHODS_RULE not in flat:
        failures.append(f"{label}: falta a proibição '{METHODS_RULE}'")

    rows = _ledger_rows()
    known_lit = _known_lit_ids(rows)

    blocks = parse_heading_blocks(text, r"^### (M-\d{2}) — (.+)$")
    seen: set[str] = set()
    for method_id, block in blocks:
        seen.add(method_id)
        if method_id not in METHODS_IDS:
            failures.append(f"{label}: método inesperado {method_id}")
        for field in METHODS_FIELDS:
            if field_value(block, field) is None:
                failures.append(f"{label}: {method_id} sem campo '{field}'")
        reference = field_value(block, "Referência") or ""
        for lit_id in sorted(set(re.findall(r"LIT-\d{4}", reference))):
            if known_lit and lit_id not in known_lit:
                failures.append(f"{label}: {method_id} referencia ledger inexistente '{lit_id}'")
    for method_id in METHODS_IDS:
        if method_id not in seen:
            failures.append(f"{label}: método obrigatório ausente {method_id}")

    if len(rows) >= 2 and "query_id" in rows[0] and "fase" in rows[0]:
        qi, fi = rows[0].index("query_id"), rows[0].index("fase")
        queries = {
            row[qi] for row in rows[1:] if len(row) > max(qi, fi) and row[fi] == "L06"
        }
        if "Q4" not in queries:
            failures.append(f"{label}: ledger sem consulta Q4 em L06")

    known = {item_id for _, item_id in parse_items(PLAN.read_text(encoding="utf-8").splitlines())}
    refs = phase_refs(text)
    for ref in sorted(ref for ref in refs if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(blocks)


def check_paths() -> tuple[list[str], int]:
    failures: list[str] = []
    total = 0
    for path in (
        GLOSSARY,
        CLAIMS,
        RISKS,
        ESTIMAND,
        EQUIVALENCE,
        OUTCOMES,
        THREATS,
        LADDER,
        INFEASIBLE,
        GATE_G0,
        LIT_PROTOCOL,
        ALIGNMENT,
        CELL_TYPE,
        SSL_REVIEW,
        METHODS,
    ):
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
    threat_failures, threats = check_threats()
    ladder_failures, levels = check_claim_ladder()
    gate_failures, gate_criteria, gate_state = check_gate_package()
    lit_failures, lit_queries = check_literature_protocol()
    ledger_failures, ledger_rows, query_log_rows = check_literature_ledger()
    alignment_failures, alignment_methods = check_alignment_review()
    cell_type_failures, cell_type_modalities = check_cell_type_review()
    ssl_failures, ssl_families = check_ssl_review()
    methods_failures, methods_count = check_methods_matrix()
    failures += (
        ref_failures
        + path_failures
        + estimand_failures
        + equivalence_failures
        + outcomes_failures
        + threat_failures
        + ladder_failures
        + gate_failures
        + lit_failures
        + ledger_failures
        + alignment_failures
        + cell_type_failures
        + ssl_failures
        + methods_failures
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
    print(
        f"OK: AMEACAS-A-VALIDADE.md com {threats} ameaças cobrindo os "
        f"{len(THREAT_TOPICS)} temas exigidos"
    )
    print(
        f"OK: ESCADA-DE-CLAIMS.md com {levels} níveis e esqueleto de "
        f"inviabilidade com {len(INFEASIBLE_SECTIONS)} seções"
    )
    print(
        f"OK: G0-CONTRATO.md com decisão {gate_state}, {gate_criteria} critérios "
        f"e estado do plano coerente"
    )
    print(
        f"OK: research/literature/PROTOCOL.md com {lit_queries} consultas, "
        f"{len(LIT_TOPICS)} temas e {len(LIT_BASES)} bases"
    )
    print(
        f"OK: research/literature/LEDGER.tsv com {ledger_rows} registros, "
        f"{query_log_rows} consultas no QUERY-LOG e {len(LIT_CANDIDATES)} "
        f"candidatos com fonte incluída"
    )
    print(
        f"OK: research/literature/ALIGNMENT.md com {alignment_methods} métodos "
        f"e supervisão classificada"
    )
    print(
        f"OK: research/literature/CELL-TYPE.md com {cell_type_modalities} "
        f"modalidades e proveniência de rótulos"
    )
    print(
        f"OK: research/literature/SSL-GRAFOS.md com {ssl_families} famílias "
        f"SSL, connectome embedding e alegações de GFM"
    )
    print(
        f"OK: research/literature/METHODS.md com {methods_count} métodos e "
        f"estimativas para 8 GB"
    )
    print(f"OK: {refs} referências de fase resolvidas contra o plano")
    print(f"OK: {paths} caminhos de arquivo citados e existentes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
