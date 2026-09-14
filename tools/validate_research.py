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

import hashlib
import importlib.util
import json
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
NOVELTY = ROOT / "research" / "literature" / "NOVIDADE.md"
NOVELTY_SECTIONS = (
    "## 1. Estado e escopo",
    "## 2. Mapa de lacunas",
    "## 3. Contribuições propostas",
    "## 4. Alternativa sem novidade suficiente",
    "## 5. Limitações",
)
NOVELTY_GAP_FIELDS = (
    "Claim",
    "Trabalhos mais próximos",
    "Diferença proposta",
    "Evidência conflitante",
    "Busca adversarial",
    "Status",
)
NOVELTY_CON_FIELDS = ("Contribuição", "Teste", "Versão mínima", "Risco", "Status")
NOVELTY_RULES = ("não há novidade suficiente", "ausência em uma busca não prova novidade")
GATE_G1 = ROOT / "docs" / "gates" / "G1-LITERATURA.md"
GATE_G1_SNAPSHOT = ROOT / "docs" / "gates" / "G1-LEDGER-SNAPSHOT.tsv"
GATE_G1_SECTIONS = (
    "## Pacote de revisão",
    "## Critérios",
    "## Riscos e divergências",
    "## Condições do G1",
    "## Escopo liberado",
    "## Assinaturas",
)
GATE_G1_SIGNATURE_FIELDS = (
    "Responsável científico",
    "Custodiante do alvo, quando aplicável",
    "Revisor de literatura/novidade",
)
GATE_G2 = ROOT / "docs" / "gates" / "G2-DADOS.md"
GATE_G2_SECTIONS = (
    "## Pacote de revisão",
    "## Cards congelados",
    "## Critérios",
    "## Riscos e divergências",
    "## Condições do G2",
    "## Escopo liberado",
    "## Assinaturas",
)
GATE_G2_SIGNATURE_FIELDS = (
    "Responsável científico",
    "Custodiante do alvo, quando aplicável",
    "Revisor de termos/licenças",
)
GATE_G2_RELEASES = ("manc:v1.2.1", "male-cns:v1.0", "v888", "v783", "v1.2.1")
GATE_G2_HASH_RE = re.compile(r"^- SHA-256 `([0-9a-f]{64})` — `([^`]+)`$")
DATASETS_INVENTORY = ROOT / "research" / "datasets" / "INVENTARIO.md"
DATASET_CARDS_DIR = ROOT / "research" / "datasets" / "cards"
INVENTORY_SECTIONS = (
    "## 1. Estado e escopo",
    "## 2. Esquema congelado",
    "## 3. Inventário dos candidatos",
    "## 4. Regras de preenchimento",
    "## 5. Limitações",
)
INVENTORY_FIELDS = (
    "Release",
    "Indivíduo/sexo/estágio/tecido",
    "Cobertura",
    "IDs",
    "Tipos",
    "Proveniência dos rótulos",
    "Neurotransmissores",
    "Regiões",
    "Edges",
    "Skeletons",
    "Crosswalks",
    "Licença",
    "API/dump",
    "Formato",
    "Tamanho",
    "Checksum",
)
INVENTORY_CANDIDATES = tuple(f"CAND-{number:02d}" for number in range(1, 7))
CROSSWALK = ROOT / "research" / "datasets" / "CROSSWALK-AUDIT.md"
RESOURCES = ROOT / "research" / "datasets" / "RECURSOS.md"
RESOURCES_SECTIONS = (
    "## 1. Amostras baixadas, checksums e custo de carga (medido)",
    "## 2. Tamanhos de release completos (publicado/listado, não baixado)",
    "## 3. Custo por linha/aresta e compressão (medido)",
    "## 4. Projeções com intervalo e margem (inferido)",
    "## 5. Consequências para 32 GB de RAM e 8 GB de VRAM (inferido)",
    "## 6. Falhas, descartes e limitações",
    "## 7. Reprodução",
)
DRY_RUN_TOOL = ROOT / "tools" / "dry_run.py"
DRY_RUN_REPORT = ROOT / "artifacts" / "reports" / "DRY-RUN-R08.md"
DRY_RUN_JSON = ROOT / "artifacts" / "reports" / "DRY-RUN-R08.json"
HANDOFF_DOC = ROOT / "docs" / "research" / "HANDOFF-CUSTODIAN.md"
DRY_RUN_TOKENS = (
    "download",
    "preprocessamento",
    "treino trivial",
    "congelamento",
    "inferência",
    "avaliação selada",
    "leakage",
    "schemas",
    "idempotente",
    "limitações",
    "dryrun-1.0-",
)
HANDOFF_TOKENS = (
    "custodiante",
    "predições",
    "metrics.json",
    "unseal",
    "firewall",
    "hashes",
    "ids opacos",
    "crosswalk",
)
PREREG_DIR = ROOT / "preregistration"
PREREG_PROTOCOL = PREREG_DIR / "PROTOCOL.md"
PREREG_REGISTRY = PREREG_DIR / "REGISTRY.md"
PREREG_CHANGELOG = PREREG_DIR / "CHANGELOG.md"
PREREG_CARDS = (
    PREREG_DIR / "cards" / "E1-selecao-fonte.md",
    PREREG_DIR / "cards" / "E2-mvp-zero-shot.md",
    PREREG_DIR / "cards" / "E3-nivel2-condicional.md",
)
PREREG_SECTIONS = (
    "## 1. Fonte, alvo e versões fixados",
    "## 2. População, unidade e independência",
    "## 3. Features permitidas (trilho A — topologia)",
    "## 4. Modelo, baselines e capacidade",
    "## 5. Espaço de hiperparâmetros e budget de trials",
    "## 6. Seeds finais",
    "## 7. Stopping e early stop",
    "## 8. Métricas, SESOI e exclusões",
    "## 9. Análise confirmatória",
    "## 10. Decisões condicionais do Nível 2",
    "## 11. Exploratório versus confirmatório",
    "## 12. Avaliação selada e unseal",
    "## 13. Alterações",
    "## 14. Assinatura",
    "## 15. Rastreabilidade e limitações",
)
PREREG_TOKENS = (
    "manc:v1.2.1",
    "male-cns:v1.0",
    "v888",
    "v783",
    "população",
    "features",
    "graphsage",
    "gin",
    "mlp",
    "degree-only",
    "hiperparâmetros",
    "12 trials",
    "seeds",
    "early stop",
    "sesoi",
    "5 pontos percentuais",
    "k = 10",
    "holm",
    "exclusões",
    "exploratório",
    "confirmatório",
    "unseal",
    "changelog",
)
PREREG_CARD_SECTIONS = (
    "## Pergunta e status",
    "## Dados",
    "## Informação permitida",
    "## Método",
    "## Avaliação",
    "## Orçamento e parada",
    "## Artefatos esperados",
)
PREREG_SIGNATURE_FIELDS = (
    "Responsável científico",
    "Revisor de estatística",
    "Custodiante designado",
)
PREREG_HASH_RE = re.compile(r"^- SHA-256 `([0-9a-f]{64})` — `([^`]+)`$")
SAP_DOC = ROOT / "docs" / "research" / "STATISTICAL-ANALYSIS-PLAN.md"
PREDICTIONS_SCHEMA = ROOT / "schemas" / "predictions.schema.json"
METRICS_SCHEMA = ROOT / "schemas" / "metrics.schema.json"
EVALUATOR_TOOL = ROOT / "tools" / "evaluator_contract.py"
SAP_SECTIONS = (
    "## 1. Estado e escopo",
    "## 2. Métrica primária e cálculo exato",
    "## 3. SESOI, Δ e regra de decisão",
    "## 4. Denominadores, missing labels e classes pequenas",
    "## 5. Dependência, agrupamento e nulos",
    "## 6. Open-set, calibração e incerteza",
    "## 7. Métricas secundárias",
    "## 8. Sensibilidade e circularidade",
    "## 9. Formato de predições (schema)",
    "## 10. Contrato do comando avaliador",
    "## 11. Ordem da análise confirmatória",
    "## 12. Rastreabilidade e limitações",
)
SAP_TOKENS = (
    "métrica primária",
    "sesoi",
    "denominador",
    "macro",
    "micro",
    "ic 95%",
    "bootstrap agrupado",
    "permuta",
    "múltiplas",
    "seeds",
    "missing",
    "classes pequenas",
    "open-set",
    "calibra",
    "não são réplicas biológicas independentes",
    "fpr@tpr95",
    "ece",
    "brier",
    "auroc",
    "aupr",
    "recall@5",
    "mrr",
    "macro-f1",
    "balanced accuracy",
    "temperatura",
    "unseal",
    "holm",
    "within-vs-cross",
)
SAP_METRICS_REQUIRED = (
    "schema_version", "run_id", "evaluated_at", "inputs", "counts", "primary",
    "comparisons", "open_set", "calibration", "within_cross", "secondary", "nulls",
)
FIREWALL_DOC = ROOT / "docs" / "research" / "FIREWALL.md"
FIREWALL_TOOL = ROOT / "tools" / "firewall.py"
FIREWALL_SECTIONS = (
    "## 1. Zonas e princípios",
    "## 2. Permissões e custódia",
    "## 3. Scanner de referências e dependências",
    "## 4. Barreiras de runtime",
    "## 5. Inventário selado: apenas hashes",
    "## 6. Testes antileakage",
    "## 7. Procedimento de unseal e invalidação",
    "## 8. Limitações",
)
FIREWALL_TOKENS = (
    "custodiante",
    "auditoria",
    "scanner",
    "firewall-allow",
    "hashes",
    "unseal",
    "invalidação",
    "logs",
    "colunas",
    "700",
    "subprocesso",
    "pipeline público",
)
RUN_CONTRACT_DOC = ROOT / "docs" / "research" / "RUN-CONTRACT.md"
RUN_CONFIG_SCHEMA = ROOT / "schemas" / "run-config.schema.json"
RUN_MANIFEST_SCHEMA = ROOT / "schemas" / "run-manifest.schema.json"
RUN_TOOL = ROOT / "tools" / "run.py"
SEEDS_TOOL = ROOT / "tools" / "seeds.py"
RUN_FIXTURE = ROOT / "configs" / "fixture.json"
RUN_CONTRACT_SECTIONS = (
    "## 1. Configuração",
    "## 2. run_id, seeds e determinismo",
    "## 3. RUN-MANIFEST",
    "## 4. Cache e imutabilidade",
    "## 5. Comandos",
    "## 6. Testes",
    "## 7. Limitações",
)
RUN_CONTRACT_TOKENS = (
    "run_id",
    "seed",
    "manifest",
    "git",
    "ambiente",
    "recursos",
    "tolerância",
    "cache",
    "imutável",
    "sha256",
    "timestamp",
    "fixture",
)
RUN_MANIFEST_REQUIRED = (
    "schema_version",
    "run_id",
    "created_at",
    "tool",
    "config",
    "config_sha256",
    "code",
    "environment",
    "seeds",
    "resources",
    "outputs",
    "status",
)
PROVENANCE_DOC = ROOT / "docs" / "research" / "PROVENANCE.md"
PROVENANCE_SCHEMA = ROOT / "schemas" / "manifest.schema.json"
PROVENANCE_TOOL = ROOT / "tools" / "manifest.py"
DOWNLOAD_TOOL = ROOT / "tools" / "download.py"
PROVENANCE_SECTIONS = (
    "## 1. Schema",
    "## 2. Validador",
    "## 3. Download idempotente",
    "## 4. Manifestos versionados",
    "## 5. Testes",
    "## 6. Limitações",
)
PROVENANCE_TOKENS = (
    "sha256",
    "range",
    "206",
    ".part",
    "credenciais",
    "idempotente",
    "nunca sobrescreve",
    "licença",
    "accessed_at",
    "https",
    "max-bytes",
    "pytest",
)
ENVIRONMENT_README = ROOT / "environment" / "README.md"
ENVIRONMENT_LOCK = ROOT / "environment" / "requirements.lock"
ENVIRONMENT_TOOL = ROOT / "tools" / "check_environment.py"
ENVIRONMENT_REPORT = ROOT / "artifacts" / "reports" / "AMBIENTE-R02.md"
ENVIRONMENT_JSON = ROOT / "artifacts" / "reports" / "AMBIENTE-R02.json"
ENVIRONMENT_TOKENS = (
    "Linux",
    "CUDA",
    "requirements.lock",
    "RTX 4060",
    "licença",
    "justificativa",
    "PyG",
    "pytest",
    "venv",
    "check_environment.py",
    "atualização",
)
ENVIRONMENT_REPORT_TOKENS = (
    "RTX 4060",
    "CUDA",
    "compute capability",
    "8.9",
    "multiplicação",
    "limitação",
    "requirements.lock",
)
ENVIRONMENT_LOCK_PACKAGES = ("numpy", "scipy", "pandas", "pyarrow", "torch", "pytest")
DATA_README = ROOT / "data" / "README.md"
DATA_MANAGEMENT = ROOT / "docs" / "research" / "DATA-MANAGEMENT.md"
DATA_HYGIENE_TOOL = ROOT / "tools" / "check_data_hygiene.py"
DATA_MANAGEMENT_SECTIONS = (
    "## 1. Princípios e fonte de verdade",
    "## 2. Layout de zonas e diretórios",
    "## 3. Releases, checksums e manifestos",
    "## 4. Retenção, backup e limpeza",
    "## 5. Licenças e redistribuição",
    "## 6. Dados regeneráveis e não regeneráveis",
    "## 7. Dados selados e firewall do alvo",
    "## 8. Segredos e credenciais",
    "## 9. Teste automatizado de higiene",
    "## 10. Limitações",
)
DATA_MANAGEMENT_TOKENS = (
    "fonte de verdade",
    "retenção",
    "backup",
    "licença",
    "redistribuição",
    "regeneráve",
    "selado",
    "limpeza",
    "checksum",
    "sha-256",
    "data/raw/source",
    "data/raw/target-public",
    "data/raw/spikes",
    "data/sealed",  # firewall-allow
    "data/manifests",
    "artifacts/reports",
    "artifacts/frozen",
    "runs/",
    "checkpoints/",
    "outputs/",
    "executor",
    "unseal",
    "custodiante",
    ".env",
    "tokens",
    "check_data_hygiene.py",
)
GITIGNORE_REQUIRED = (
    "data/sealed/",  # firewall-allow
    "*.token",
    "tokens/",
    "!/data/manifests/**",
    "/runs/",
    "/checkpoints/",
    "*.ckpt",
)
SELECTION = ROOT / "research" / "datasets" / "SELECAO.md"
SELECTION_SECTIONS = (
    "## 1. Estado e escopo",
    "## 2. Notas por dataset",
    "## 3. Ranking dos pares aprovados em D08",
    "## 4. Papéis propostos",
    "## 5. Condições de defensabilidade do MVP MANC → MCNS",
    "## 6. Matriz de fallback",
    "## 7. Efeito nos recursos (base D09)",
    "## 8. Decisões propostas (pendentes de G2)",
    "## 9. Limitações",
)
SELECTION_TOKENS = (
    "comparabilidade",
    "independência",
    "labels",
    "licença",
    "acesso",
    "escala",
    "circularidade",
    "MVP",
    "fonte",
    "alvo-piloto",
    "reserva",
    "fallback",
    "incompatibilidade",
    "acesso negado",
    "crosswalk",
    "réplica biológica",
    "mesmo indivíduo",
    "MANC",
    "MCNS",
    "BANC",
    "MAOL",
    "hemibrain",
    "PAIR-04",
    "G2",
)
SELECTION_DECISIONS = ("DEC-SEL-01", "DEC-SEL-02", "DEC-SEL-03", "DEC-SEL-04")
SELECTION_PENDING = "proposta (pendente de G2)"
RESOURCES_TOKENS = (
    "publicado",
    "medido",
    "inferido",
    "checksum",
    "COO",
    "CSR",
    "Parquet",
    "Arrow",
    "mmap",
    "32 GB",
    "8 GB",
    "VRAM",
    "intervalo",
    "margem",
    "sha256",
    "1 GB",
)
CROSSWALK_SECTIONS = (
    "## 1. Estado e escopo",
    "## 2. Método de auditoria",
    "## 3. Proposta por par (somente agregados)",
    "## 4. Sinalização de rótulos derivados",
    "## 5. Regras de selagem e acesso",
    "## 6. Decisões pendentes",
    "## 7. Limitações",
    "## 8. Aprovação humana",
)
CROSSWALK_APPROVED = "APROVADO"
CROSSWALK_PENDING = "aguardando dupla revisão humana"
ALLOWED_CROSSWALK_STATUSES = (CROSSWALK_PENDING, CROSSWALK_APPROVED)
CROSSWALK_APPROVAL_FIELDS = ("Data", "Aprovador", "Escopo")
CROSSWALK_PAIR_FIELDS = (
    "Par",
    "Interseção proposta",
    "Known/open-set",
    "Independência do rótulo",
    "Fontes",
    "Risco de circularidade",
    "Status",
)
CROSSWALK_DEC_FIELDS = ("Decisão", "Opções", "Recomendação", "Status")
CROSSWALK_RULES = (
    "zona selada",
    "dois revisores",
    "sensibilidade ou exclusão",
    "não recebe mapping exato",
)
PUBLIC_ID_RE = re.compile(r"\b\d{9,}\b")
CARD_SECTIONS = (
    "## Identidade e proveniência",
    "## Acesso e licença",
    "## Conteúdo confirmado",
    "## Riscos para comparação",
    "## Verificação local mínima",
    "## Veredito",
    "## Fontes atômicas",
)
FABRICATION_RE = re.compile(r":\s*`?confirmado", re.I)
AUDITED_STATUS_RE = re.compile(r"^auditado \(D\d{2}\)$")
CARD_VERDICTS = (
    "candidato",
    "adequado à fonte",
    "adequado ao alvo",
    "apenas exploratório",
    "rejeitado",
)
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


def check_novelty() -> tuple[list[str], int]:
    label = "NOVIDADE.md"
    if not NOVELTY.exists():
        return [f"{label}: arquivo ausente em research/literature/"], 0
    text = NOVELTY.read_text(encoding="utf-8")
    flat = " ".join(text.split()).lower()
    failures: list[str] = []
    for section in NOVELTY_SECTIONS:
        if section not in text:
            failures.append(f"{label}: seção obrigatória ausente '{section}'")
    for rule in NOVELTY_RULES:
        if rule not in flat:
            failures.append(f"{label}: regra obrigatória ausente ('{rule}')")

    rows = _ledger_rows()
    known_lit = _known_lit_ids(rows)

    gaps = parse_heading_blocks(text, r"^### (GAP-\d{2}) — (.+)$")
    if len(gaps) < 3:
        failures.append(f"{label}: esperadas ao menos 3 lacunas (achadas {len(gaps)})")
    for gap_id, block in gaps:
        for field in NOVELTY_GAP_FIELDS:
            if field_value(block, field) is None:
                failures.append(f"{label}: {gap_id} sem campo '{field}'")
        references = " ".join(
            field_value(block, field) or ""
            for field in ("Trabalhos mais próximos", "Evidência conflitante")
        )
        if not re.search(r"LIT-\d{4}", references):
            failures.append(f"{label}: {gap_id} sem referência LIT-*")
        for lit_id in sorted(set(re.findall(r"LIT-\d{4}", references))):
            if known_lit and lit_id not in known_lit:
                failures.append(f"{label}: {gap_id} referencia ledger inexistente '{lit_id}'")

    contributions = parse_heading_blocks(text, r"^### (CON-\d{2}) — (.+)$")
    if not contributions:
        failures.append(f"{label}: nenhuma contribuição proposta (CON-*)")
    if len(contributions) > 3:
        failures.append(f"{label}: mais de três contribuições propostas ({len(contributions)})")
    for con_id, block in contributions:
        for field in NOVELTY_CON_FIELDS:
            if field_value(block, field) is None:
                failures.append(f"{label}: {con_id} sem campo '{field}'")

    if len(rows) >= 2 and "query_id" in rows[0] and "fase" in rows[0]:
        qi, fi = rows[0].index("query_id"), rows[0].index("fase")
        queries = {
            row[qi] for row in rows[1:] if len(row) > max(qi, fi) and row[fi] == "L07"
        }
        for query in ("Q4", "Q5"):
            if query not in queries:
                failures.append(f"{label}: ledger sem consulta {query} em L07")

    known = {item_id for _, item_id in parse_items(PLAN.read_text(encoding="utf-8").splitlines())}
    refs = phase_refs(text)
    for ref in sorted(ref for ref in refs if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(gaps)


def check_gate_g1() -> tuple[list[str], int, str]:
    label = "G1-LITERATURA.md"
    if not GATE_G1.exists():
        return [f"{label}: arquivo ausente"], 0, "AUSENTE"
    text = GATE_G1.read_text(encoding="utf-8")
    lines = text.splitlines()
    failures: list[str] = []
    for section in GATE_G1_SECTIONS:
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

    if not GATE_G1_SNAPSHOT.exists():
        failures.append(f"{label}: snapshot G1-LEDGER-SNAPSHOT.tsv ausente")
    else:
        digest = hashlib.sha256(GATE_G1_SNAPSHOT.read_bytes()).hexdigest()
        if digest not in text:
            failures.append(f"{label}: SHA-256 do snapshot ausente no pacote ('{digest}')")

    criteria = [line for line in lines if CRITERION_RE.match(line)]
    if len(criteria) < 6:
        failures.append(f"{label}: esperados ao menos 6 critérios no formato do modelo (achados {len(criteria)})")
    if pending and not any("`NÃO VERIFICADO`" in line for line in criteria):
        failures.append(f"{label}: nenhum critério marcado 'NÃO VERIFICADO' com decisão pendente")
    if approved and any("`NÃO VERIFICADO`" in line for line in criteria):
        failures.append(f"{label}: decisão GO com critério ainda 'NÃO VERIFICADO'")
    if any("`FAIL`" in line for line in criteria):
        failures.append(f"{label}: critério FAIL exige decisão REFORMULAR/NO-GO")

    start = next((i for i, line in enumerate(lines) if line.startswith("## Assinaturas")), None)
    signature_lines = lines[start:] if start is not None else []
    signature_block = "\n".join(signature_lines)
    for field in GATE_G1_SIGNATURE_FIELDS:
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
    g1_line = next((line for line in plan_lines if "**G1 —" in line), None)
    if g1_line is None:
        failures.append(f"{label}: item G1 não encontrado no plano")
    elif pending and not g1_line.startswith("- [ ]"):
        failures.append(f"{label}: G1 marcado como concluído enquanto a decisão é AGUARDAR")
    elif approved and g1_line.startswith("- [ ]"):
        failures.append(f"{label}: decisão GO exige G1 marcado [x] no plano")

    known = {item_id for _, item_id in parse_items(plan_lines)}
    refs = phase_refs(text)
    for ref in sorted(ref for ref in refs if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    state = "GO" if approved else "AGUARDAR"
    return failures, len(criteria), state


def check_dataset_inventory() -> tuple[list[str], int]:
    label = "INVENTARIO.md"
    if not DATASETS_INVENTORY.exists():
        return [f"{label}: arquivo ausente em research/datasets/"], 0
    text = DATASETS_INVENTORY.read_text(encoding="utf-8")
    flat = " ".join(text.split()).lower()
    failures: list[str] = []
    for section in INVENTORY_SECTIONS:
        if section not in text:
            failures.append(f"{label}: seção obrigatória ausente '{section}'")
    for field in INVENTORY_FIELDS:
        if field.lower() not in flat:
            failures.append(f"{label}: campo obrigatório ausente ('{field}')")
    fabrication = FABRICATION_RE.search(text)
    if fabrication:
        failures.append(f"{label}: valor 'confirmado' sem auditoria ('{fabrication.group(0)}')")

    blocks = parse_heading_blocks(text, r"^### (CAND-\d{2}) — (.+)$")
    seen: set[str] = set()
    for cand_id, block in blocks:
        seen.add(cand_id)
        if cand_id not in INVENTORY_CANDIDATES:
            failures.append(f"{label}: candidato inesperado {cand_id}")
        card = field_value(block, "Card")
        status = field_value(block, "Status")
        if status is None:
            failures.append(f"{label}: {cand_id} sem campo 'Status'")
        elif status != "não confirmado" and not AUDITED_STATUS_RE.match(status):
            failures.append(
                f"{label}: {cand_id} status inválido '{status}' (use 'não confirmado' ou 'auditado (Dxx)')"
            )
        if card is None:
            failures.append(f"{label}: {cand_id} sem campo 'Card'")
        else:
            card_path = ROOT / card.strip("`")
            if not card_path.exists():
                failures.append(f"{label}: {cand_id} aponta card ausente '{card}'")
            else:
                card_text = card_path.read_text(encoding="utf-8")
                for section in CARD_SECTIONS:
                    if section not in card_text:
                        failures.append(f"{card_path.name}: seção do modelo ausente '{section}'")
                if status == "não confirmado":
                    if "não confirmado" not in card_text:
                        failures.append(f"{card_path.name}: sem marcação 'não confirmado'")
                    card_fabrication = FABRICATION_RE.search(card_text)
                    if card_fabrication:
                        failures.append(
                            f"{card_path.name}: valor 'confirmado' sem auditoria ('{card_fabrication.group(0)}')"
                        )
                elif status is not None and AUDITED_STATUS_RE.match(status):
                    if "Status geral: `não confirmado`" in card_text:
                        failures.append(f"{card_path.name}: card auditado ainda com status 'não confirmado'")
                    if not re.search(r"https?://|10\.\d{4,}/", card_text):
                        failures.append(f"{card_path.name}: card auditado sem URL/DOI")
                    if card_text.count("- Fonte/localização:") < 5:
                        failures.append(f"{card_path.name}: card auditado com menos de 5 fontes atômicas")
                    veredito = re.search(r"- Veredito: `([^`]+)`", card_text)
                    if not veredito or veredito.group(1) not in CARD_VERDICTS:
                        failures.append(f"{card_path.name}: veredito ausente ou inválido")
    for cand_id in INVENTORY_CANDIDATES:
        if cand_id not in seen:
            failures.append(f"{label}: candidato obrigatório ausente {cand_id}")

    known = {item_id for _, item_id in parse_items(PLAN.read_text(encoding="utf-8").splitlines())}
    refs = phase_refs(text)
    for ref in sorted(ref for ref in refs if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(blocks)


def check_dry_run() -> tuple[list[str], int]:
    label = "R08"
    failures: list[str] = []
    for path in (
        DRY_RUN_TOOL,
        ROOT / "tests" / "test_dry_run.py",
        DRY_RUN_REPORT,
        DRY_RUN_JSON,
        HANDOFF_DOC,
    ):
        if not path.exists():
            failures.append(f"{label}: arquivo ausente '{path.relative_to(ROOT)}'")
    if failures:
        return failures, 0

    report = DRY_RUN_REPORT.read_text(encoding="utf-8")
    handoff = HANDOFF_DOC.read_text(encoding="utf-8")
    flat_report = " ".join(report.split()).lower()
    for token in DRY_RUN_TOKENS:
        if token.lower() not in flat_report:
            failures.append(f"{label}: relatório sem token '{token}'")
    for token in HANDOFF_TOKENS:
        if token.lower() not in " ".join(handoff.split()).lower():
            failures.append(f"{label}: handoff sem token '{token}'")
    for path in (DRY_RUN_REPORT, HANDOFF_DOC):
        leak = PUBLIC_ID_RE.search(path.read_text(encoding="utf-8"))
        if leak:
            failures.append(f"{label}: {path.name} com possível ID cru ('{leak.group(0)}')")

    manifest = json.loads(DRY_RUN_JSON.read_text(encoding="utf-8"))
    tag = str(manifest.get("dryrun_tag", ""))
    if not re.fullmatch(r"dryrun-1\.0-[0-9a-f]{8}", tag):
        failures.append(f"{label}: dryrun_tag inválido '{tag}'")
    if tag and tag not in report:
        failures.append(f"{label}: relatório não cita a tag '{tag}'")
    stages = manifest.get("stages", {})
    for stage in ("download", "preprocess", "train", "inference"):
        if stage not in stages:
            failures.append(f"{label}: manifesto sem estágio '{stage}'")
    if manifest.get("firewall_scanner_clean") is not True:
        failures.append(f"{label}: scanner do firewall não consta limpo no manifesto")
    for field in ("predictions_sha256", "metrics_sha256"):
        if not re.fullmatch(r"[0-9a-f]{64}", str(manifest.get(field, ""))):
            failures.append(f"{label}: manifesto sem hash válido em '{field}'")
    if stages.get("inference", {}).get("rejected", 0) < 1:
        failures.append(f"{label}: dry run sem nenhuma rejeição de unknown")

    plan_lines = PLAN.read_text(encoding="utf-8").splitlines()
    known = {item_id for _, item_id in parse_items(plan_lines)}
    for ref in sorted(ref for ref in phase_refs(report + handoff) if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(DRY_RUN_TOKENS)


def check_preregistration() -> tuple[list[str], int, str]:
    label = "R07"
    failures: list[str] = []
    for path in (PREREG_PROTOCOL, PREREG_REGISTRY, PREREG_CHANGELOG, *PREREG_CARDS):
        if not path.exists():
            failures.append(f"{label}: arquivo ausente '{path.relative_to(ROOT)}'")
    if failures:
        return failures, 0, "AUSENTE"

    protocol = PREREG_PROTOCOL.read_text(encoding="utf-8")
    flat = " ".join(protocol.split()).lower().replace("**", "")
    for section in PREREG_SECTIONS:
        if section not in protocol:
            failures.append(f"{label}: PROTOCOL.md sem seção '{section}'")
    for token in PREREG_TOKENS:
        if token.lower() not in flat:
            failures.append(f"{label}: PROTOCOL.md sem token '{token}'")
    numeric_list_re = re.compile(r"^\s*[(),.\d\s]+$")
    for number, line in enumerate(protocol.splitlines(), 1):
        if any(word in line.lower() for word in ("seed", "bootstrap", "permuta")):
            continue
        if numeric_list_re.match(line):
            continue
        leak = PUBLIC_ID_RE.search(line)
        if leak:
            failures.append(
                f"{label}: PROTOCOL.md:{number} com possível ID cru ('{leak.group(0)}')"
            )
    for card in PREREG_CARDS:
        text = card.read_text(encoding="utf-8")
        found = sum(1 for section in PREREG_CARD_SECTIONS if section in text)
        if found < 6:
            failures.append(f"{label}: card '{card.name}' incompleto ({found} seções do modelo)")

    registry_lines = PREREG_REGISTRY.read_text(encoding="utf-8").splitlines()
    entries = 0
    for line in registry_lines:
        match = PREREG_HASH_RE.match(line)
        if match is None:
            continue
        digest, rel = match.groups()
        path = ROOT / rel
        if not path.exists():
            failures.append(f"{label}: artefato congelado ausente '{rel}'")
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            failures.append(f"{label}: SHA-256 divergente para '{rel}'")
        entries += 1
    if entries < 10:
        failures.append(f"{label}: esperados ao menos 10 artefatos congelados (achados {entries})")

    signature_start = next(
        (i for i, line in enumerate(registry_lines) if line.startswith("## 2. Assinaturas")), None
    )
    signature_lines = registry_lines[signature_start:] if signature_start is not None else []
    tracked_fields = (*PREREG_SIGNATURE_FIELDS, "Data da assinatura", "Hash do pacote assinado")
    for field in PREREG_SIGNATURE_FIELDS:
        if field_value(signature_lines, field) is None:
            failures.append(f"{label}: REGISTRY.md sem campo de assinatura '{field}'")
    tracked_values = [field_value(signature_lines, field) or "" for field in tracked_fields]
    pending = any("a preencher" in value.lower() for value in tracked_values)
    if not pending and "2026-" not in "\n".join(signature_lines):
        failures.append(f"{label}: assinatura preenchida sem data")
    if not pending:
        package_value = field_value(signature_lines, "Hash do pacote assinado") or ""
        match = re.search(r"[0-9a-f]{64}", package_value)
        if not match:
            failures.append(f"{label}: assinatura sem hash do pacote")
        else:
            frozen_lines = [line for line in registry_lines if PREREG_HASH_RE.match(line)]
            expected = hashlib.sha256("\n".join(frozen_lines).encode("utf-8")).hexdigest()
            if match.group(0) != expected:
                failures.append(f"{label}: hash do pacote assinado não confere com os artefatos congelados")
    changelog = PREREG_CHANGELOG.read_text(encoding="utf-8")
    if "2026-09-14" not in changelog:
        failures.append(f"{label}: CHANGELOG.md sem entrada da minuta")

    plan_lines = PLAN.read_text(encoding="utf-8").splitlines()
    r07_line = next((line for line in plan_lines if "**R07 —" in line), None)
    if r07_line is None:
        failures.append(f"{label}: item R07 não encontrado no plano")
    elif pending and not r07_line.startswith("- [ ]"):
        failures.append(f"{label}: R07 marcado concluído enquanto a assinatura está pendente")
    elif not pending and r07_line.startswith("- [ ]"):
        failures.append(f"{label}: assinatura preenchida exige R07 marcado [x]")
    known = {item_id for _, item_id in parse_items(plan_lines)}
    for ref in sorted(ref for ref in phase_refs(protocol) if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    state = "AGUARDAR" if pending else "ASSINADO"
    return failures, entries, state


def check_statistical_plan() -> tuple[list[str], int]:
    label = "R06"
    failures: list[str] = []
    for path in (
        SAP_DOC,
        PREDICTIONS_SCHEMA,
        METRICS_SCHEMA,
        EVALUATOR_TOOL,
        ROOT / "tests" / "test_evaluator_contract.py",
    ):
        if not path.exists():
            failures.append(f"{label}: arquivo ausente '{path.relative_to(ROOT)}'")
    if failures:
        return failures, 0

    doc = SAP_DOC.read_text(encoding="utf-8")
    flat_doc = " ".join(doc.split()).lower()
    for section in SAP_SECTIONS:
        if section not in doc:
            failures.append(f"{label}: SAP sem seção '{section}'")
    for token in SAP_TOKENS:
        if token.lower() not in flat_doc:
            failures.append(f"{label}: SAP sem token '{token}'")
    leak = PUBLIC_ID_RE.search(doc)
    if leak:
        failures.append(f"{label}: SAP com possível ID cru ('{leak.group(0)}')")

    predictions_schema = json.loads(PREDICTIONS_SCHEMA.read_text(encoding="utf-8"))
    metrics_schema = json.loads(METRICS_SCHEMA.read_text(encoding="utf-8"))
    spec = importlib.util.spec_from_file_location("evaluator_contract_module", EVALUATOR_TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if tuple(predictions_schema.get("required", ())) != module.PREDICTIONS_REQUIRED:
        failures.append(f"{label}: schema de predições divergente do validador")
    if tuple(metrics_schema.get("required", ())) != module.METRICS_REQUIRED:
        failures.append(f"{label}: schema de métricas divergente do validador")
    if not module.FORBIDDEN_KEYS:
        failures.append(f"{label}: validador sem lista de chaves proibidas")
    if metrics_schema["properties"]["comparisons"]["properties"]["sesoi_pp"]["const"] != 5:
        failures.append(f"{label}: SESOI deve ser 5 pontos percentuais no schema")
    if metrics_schema["properties"]["calibration"]["properties"]["bins"]["const"] != 15:
        failures.append(f"{label}: calibração deve fixar 15 bins no schema")
    if metrics_schema["properties"]["open_set"]["properties"]["tpr_target"]["const"] != 0.95:
        failures.append(f"{label}: open-set deve fixar TPR = 0,95 no schema")

    plan_lines = PLAN.read_text(encoding="utf-8").splitlines()
    known = {item_id for _, item_id in parse_items(plan_lines)}
    for ref in sorted(ref for ref in phase_refs(doc) if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(SAP_TOKENS)


def check_firewall_phase() -> tuple[list[str], int]:
    label = "R05"
    failures: list[str] = []
    for path in (FIREWALL_DOC, FIREWALL_TOOL, ROOT / "tests" / "test_firewall.py"):
        if not path.exists():
            failures.append(f"{label}: arquivo ausente '{path.relative_to(ROOT)}'")
    if failures:
        return failures, 0

    doc = FIREWALL_DOC.read_text(encoding="utf-8")
    for section in FIREWALL_SECTIONS:
        if section not in doc:
            failures.append(f"{label}: FIREWALL.md sem seção '{section}'")
    for token in FIREWALL_TOKENS:
        if token.lower() not in doc.lower():
            failures.append(f"{label}: FIREWALL.md sem token '{token}'")
    leak = PUBLIC_ID_RE.search(doc)
    if leak:
        failures.append(f"{label}: FIREWALL.md com possível ID cru ('{leak.group(0)}')")

    spec = importlib.util.spec_from_file_location("firewall_module", FIREWALL_TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    violations = module.scan_forbidden_references()
    for violation in violations:
        failures.append(f"{label}: referência proibida sem marca: {violation}")
    sealed = module.SEALED_ROOT
    if not sealed.is_dir():
        failures.append(f"{label}: zona selada ausente '{sealed.relative_to(ROOT)}'")
    else:
        for path in (sealed, sealed / "target-labels"):  # firewall-allow
            if path.exists() and (path.stat().st_mode & 0o777) != 0o700:
                failures.append(f"{label}: permissões de '{path.relative_to(ROOT)}' não são 700")
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    if "data/sealed/" not in gitignore:  # firewall-allow
        failures.append(f"{label}: data/sealed/ deve continuar ignorado pelo Git")  # firewall-allow
    return failures, len(FIREWALL_TOKENS)


def check_run_contract() -> tuple[list[str], int]:
    label = "R04"
    failures: list[str] = []
    for path in (
        RUN_CONTRACT_DOC,
        RUN_CONFIG_SCHEMA,
        RUN_MANIFEST_SCHEMA,
        RUN_TOOL,
        SEEDS_TOOL,
        RUN_FIXTURE,
        ROOT / "tests" / "test_run_contract.py",
    ):
        if not path.exists():
            failures.append(f"{label}: arquivo ausente '{path.relative_to(ROOT)}'")
    if failures:
        return failures, 0

    doc = RUN_CONTRACT_DOC.read_text(encoding="utf-8")
    for section in RUN_CONTRACT_SECTIONS:
        if section not in doc:
            failures.append(f"{label}: RUN-CONTRACT.md sem seção '{section}'")
    for token in RUN_CONTRACT_TOKENS:
        if token.lower() not in doc.lower():
            failures.append(f"{label}: RUN-CONTRACT.md sem token '{token}'")
    leak = PUBLIC_ID_RE.search(doc)
    if leak:
        failures.append(f"{label}: RUN-CONTRACT.md com possível ID cru ('{leak.group(0)}')")

    config_schema = json.loads(RUN_CONFIG_SCHEMA.read_text(encoding="utf-8"))
    manifest_schema = json.loads(RUN_MANIFEST_SCHEMA.read_text(encoding="utf-8"))
    fixture = json.loads(RUN_FIXTURE.read_text(encoding="utf-8"))
    if tuple(manifest_schema.get("required", ())) != RUN_MANIFEST_REQUIRED:
        failures.append(f"{label}: schema do manifesto divergente da lista obrigatória")
    config_props = set(config_schema.get("properties", {}))
    for key in fixture:
        if key not in config_props:
            failures.append(f"{label}: fixture usa campo fora do schema '{key}'")
    for key in fixture.get("params", {}):
        if key not in config_schema["properties"]["params"]["properties"]:
            failures.append(f"{label}: fixture usa parâmetro fora do schema '{key}'")
    if "seed" not in fixture:
        failures.append(f"{label}: fixture sem seed mestra")
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    if "/runs/" not in gitignore:
        failures.append(f"{label}: /runs/ deve continuar ignorado pelo Git")
    return failures, len(RUN_CONTRACT_TOKENS)


def check_provenance_phase() -> tuple[list[str], int]:
    label = "R03"
    failures: list[str] = []
    for path in (
        PROVENANCE_DOC,
        PROVENANCE_SCHEMA,
        PROVENANCE_TOOL,
        DOWNLOAD_TOOL,
        ROOT / "tests" / "test_manifest.py",
        ROOT / "tests" / "test_download.py",
    ):
        if not path.exists():
            failures.append(f"{label}: arquivo ausente '{path.relative_to(ROOT)}'")
    if failures:
        return failures, 0

    doc = PROVENANCE_DOC.read_text(encoding="utf-8")
    for section in PROVENANCE_SECTIONS:
        if section not in doc:
            failures.append(f"{label}: PROVENANCE.md sem seção '{section}'")
    for token in PROVENANCE_TOKENS:
        if token.lower() not in doc.lower():
            failures.append(f"{label}: PROVENANCE.md sem token '{token}'")
    leak = PUBLIC_ID_RE.search(doc)
    if leak:
        failures.append(f"{label}: PROVENANCE.md com possível ID cru ('{leak.group(0)}')")

    spec = importlib.util.spec_from_file_location("provenance_manifest", PROVENANCE_TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    schema = json.loads(PROVENANCE_SCHEMA.read_text(encoding="utf-8"))
    if tuple(schema.get("required", ())) != module.TOP_LEVEL_REQUIRED:
        failures.append(f"{label}: schema e validador divergem nos campos obrigatórios")
    manifests = sorted((ROOT / "data" / "manifests").glob("*.json"))
    if len(manifests) < 4:
        failures.append(f"{label}: esperados ao menos 4 manifestos versionados (achados {len(manifests)})")
    for path in manifests:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            failures.append(f"{path.name}: JSON inválido ({error})")
            continue
        for failure in module.validate_manifest(payload, path.name):
            failures.append(f"{label}: {failure}")
    return failures, len(manifests)


def check_environment_phase() -> tuple[list[str], int]:
    label = "R02"
    failures: list[str] = []
    for path in (ENVIRONMENT_README, ENVIRONMENT_LOCK, ENVIRONMENT_TOOL, ENVIRONMENT_REPORT):
        if not path.exists():
            failures.append(f"{label}: arquivo ausente '{path.relative_to(ROOT)}'")
    if not ENVIRONMENT_JSON.exists():
        failures.append(f"{label}: métricas ausentes 'artifacts/reports/AMBIENTE-R02.json'")
    if failures:
        return failures, 0

    readme = ENVIRONMENT_README.read_text(encoding="utf-8")
    report = ENVIRONMENT_REPORT.read_text(encoding="utf-8")
    lock = ENVIRONMENT_LOCK.read_text(encoding="utf-8")
    for token in ENVIRONMENT_TOKENS:
        if token.lower() not in readme.lower():
            failures.append(f"{label}: environment/README.md sem token '{token}'")
    for token in ENVIRONMENT_REPORT_TOKENS:
        if token.lower() not in report.lower():
            failures.append(f"{label}: relatório sem token '{token}'")
    for package in ENVIRONMENT_LOCK_PACKAGES:
        if not re.search(rf"^{package}==\d", lock, re.M):
            failures.append(f"{label}: lock sem pino '== {package}'")

    data = json.loads(ENVIRONMENT_JSON.read_text(encoding="utf-8"))
    for key in ("sistema", "python", "pacotes", "cpu", "memoria_gib", "disco_gib", "gpu", "cuda_op"):
        if key not in data:
            failures.append(f"{label}: JSON sem chave '{key}'")
    gpu = data.get("gpu", {})
    if "RTX 4060" not in str(gpu.get("nome", "")):
        failures.append(f"{label}: GPU medida não é a RTX 4060 esperada")
    if int(gpu.get("vram_mib", 0)) < 8000:
        failures.append(f"{label}: VRAM medida abaixo de 8 GB")
    if str(gpu.get("compute_cap")) != "8.9":
        failures.append(f"{label}: compute capability inesperada '{gpu.get('compute_cap')}'")
    cuda = data.get("cuda_op", {})
    if not cuda.get("cuda_available") or not cuda.get("matmul_finito"):
        failures.append(f"{label}: operação CUDA mínima não registrada como aprovada")
    if str(data.get("python", {}).get("versao")) != "3.12.2":
        failures.append(f"{label}: versão de Python medida diverge do lock documentado")
    driver = str(gpu.get("driver", ""))
    if driver and driver not in report:
        failures.append(f"{label}: relatório não cita o driver medido '{driver}'")
    for path in (ENVIRONMENT_JSON, ENVIRONMENT_REPORT, ENVIRONMENT_README):
        text = path.read_text(encoding="utf-8")
        if "/home/" in text or "iiii" in text:
            failures.append(f"{path.name}: caminho local ou usuário no artefato versionado")
        leak = PUBLIC_ID_RE.search(text)
        if leak:
            failures.append(f"{path.name}: possível ID cru de neurônio ('{leak.group(0)}')")

    plan_lines = PLAN.read_text(encoding="utf-8").splitlines()
    known = {item_id for _, item_id in parse_items(plan_lines)}
    for ref in sorted(ref for ref in phase_refs(report + readme) if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(ENVIRONMENT_TOKENS)


def check_data_management() -> tuple[list[str], int]:
    label = "DATA-MANAGEMENT.md"
    failures: list[str] = []
    if not DATA_README.exists():
        failures.append("data/README.md: arquivo ausente")
    if not DATA_MANAGEMENT.exists():
        failures.append(f"{label}: arquivo ausente em docs/research/")
    if not DATA_HYGIENE_TOOL.exists():
        failures.append("tools/check_data_hygiene.py: teste de higiene ausente")
    if not failures:
        readme = DATA_README.read_text(encoding="utf-8")
        text = DATA_MANAGEMENT.read_text(encoding="utf-8")
        for section in DATA_MANAGEMENT_SECTIONS:
            if section not in text:
                failures.append(f"{label}: seção obrigatória ausente '{section}'")
        for token in DATA_MANAGEMENT_TOKENS:
            if token.lower() not in text.lower():
                failures.append(f"{label}: token obrigatório ausente '{token}'")
        for token in ("check_data_hygiene.py", "DATA-MANAGEMENT.md"):
            if token not in readme:
                failures.append(f"data/README.md: sem referência a '{token}'")
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for token in GITIGNORE_REQUIRED:
            if token not in gitignore:
                failures.append(f".gitignore: padrão obrigatório ausente '{token}'")
        for path in (DATA_README, DATA_MANAGEMENT):
            leak = PUBLIC_ID_RE.search(path.read_text(encoding="utf-8"))
            if leak:
                failures.append(f"{path.name}: possível ID cru de neurônio ('{leak.group(0)}')")
        known_lit = set(
            re.findall(r"^(LIT-\d{4})\t", LIT_LEDGER.read_text(encoding="utf-8"), re.M)
        )
        refs = sorted(set(re.findall(r"LIT-\d{4}", text)))
        if len(refs) < 4:
            failures.append(f"{label}: menos de 4 referências LIT-* para licenças")
        for lit_id in refs:
            if known_lit and lit_id not in known_lit:
                failures.append(f"{label}: referencia ledger inexistente '{lit_id}'")
        plan_lines = PLAN.read_text(encoding="utf-8").splitlines()
        known = {item_id for _, item_id in parse_items(plan_lines)}
        for ref in sorted(ref for ref in phase_refs(text) if ref not in known):
            failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(DATA_MANAGEMENT_SECTIONS)


def check_gate_g2() -> tuple[list[str], int, str]:
    label = "G2-DADOS.md"
    if not GATE_G2.exists():
        return [f"{label}: arquivo ausente"], 0, "AUSENTE"
    text = GATE_G2.read_text(encoding="utf-8")
    lines = text.splitlines()
    failures: list[str] = []
    for section in GATE_G2_SECTIONS:
        if section not in text:
            failures.append(f"{label}: seção obrigatória ausente '{section}'")
    for field in GATE_HEADER_FIELDS:
        if field_value(lines, field) is None:
            failures.append(f"{label}: cabeçalho sem campo '{field}'")
    decision = field_value(lines, "Decisão")
    if decision is None or not decision.startswith(("AGUARDAR", "GO", "NO-GO", "REFORMULAR")):
        failures.append(f"{label}: decisão deve começar com AGUARDAR, GO, NO-GO ou REFORMULAR")
    pending = decision is not None and decision.startswith("AGUARDAR")
    approved = decision is not None and decision.startswith("GO")

    start = next((i for i, line in enumerate(lines) if line.startswith("## Cards congelados")), None)
    end = next(
        (i for i, line in enumerate(lines) if line.startswith("## ") and start is not None and i > start),
        len(lines),
    )
    frozen = lines[start:end] if start is not None else []
    entries = 0
    for line in frozen:
        match = GATE_G2_HASH_RE.match(line)
        if match is None:
            continue
        digest, rel = match.groups()
        path = ROOT / rel
        if not path.exists():
            failures.append(f"{label}: arquivo congelado ausente '{rel}'")
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            failures.append(f"{label}: SHA-256 divergente para '{rel}'")
        entries += 1
    if entries < 10:
        failures.append(f"{label}: esperados ao menos 10 arquivos congelados (achados {entries})")
    for token in GATE_G2_RELEASES:
        if token not in text:
            failures.append(f"{label}: release obrigatória ausente '{token}'")
    if "alvo confirmatório" not in text or "reservado" not in text:
        failures.append(f"{label}: alvo confirmatório reservado não declarado")

    criteria = [line for line in lines if CRITERION_RE.match(line)]
    if len(criteria) < 8:
        failures.append(f"{label}: esperados ao menos 8 critérios no formato do modelo (achados {len(criteria)})")
    if pending and not any("`NÃO VERIFICADO`" in line for line in criteria):
        failures.append(f"{label}: nenhum critério marcado 'NÃO VERIFICADO' com decisão pendente")
    if approved and any("`NÃO VERIFICADO`" in line for line in criteria):
        failures.append(f"{label}: decisão GO com critério ainda 'NÃO VERIFICADO'")
    if approved and any("`FAIL`" in line for line in criteria):
        failures.append(f"{label}: critério FAIL exige decisão NO-GO/REFORMULAR")

    start = next((i for i, line in enumerate(lines) if line.startswith("## Assinaturas")), None)
    signature_lines = lines[start:] if start is not None else []
    signature_block = "\n".join(signature_lines)
    for field in GATE_G2_SIGNATURE_FIELDS:
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

    known_lit = set(re.findall(r"^(LIT-\d{4})\t", LIT_LEDGER.read_text(encoding="utf-8"), re.M))
    refs = sorted(set(re.findall(r"LIT-\d{4}", text)))
    if len(refs) < 3:
        failures.append(f"{label}: menos de 3 referências LIT-* no pacote")
    for lit_id in refs:
        if known_lit and lit_id not in known_lit:
            failures.append(f"{label}: referencia ledger inexistente '{lit_id}'")
    leak = PUBLIC_ID_RE.search(text)
    if leak:
        failures.append(f"{label}: possível ID cru de neurônio no documento público ('{leak.group(0)}')")

    plan_lines = PLAN.read_text(encoding="utf-8").splitlines()
    g2_line = next((line for line in plan_lines if "**G2 —" in line), None)
    if g2_line is None:
        failures.append(f"{label}: item G2 não encontrado no plano")
    elif pending and not g2_line.startswith("- [ ]"):
        failures.append(f"{label}: G2 marcado como concluído enquanto a decisão é AGUARDAR")
    elif approved and g2_line.startswith("- [ ]"):
        failures.append(f"{label}: decisão GO exige G2 marcado [x] no plano")

    known = {item_id for _, item_id in parse_items(plan_lines)}
    for ref in sorted(ref for ref in phase_refs(text) if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    state = "GO" if approved else "AGUARDAR"
    return failures, len(criteria), state


def check_dataset_selection() -> tuple[list[str], int]:
    label = "SELECAO.md"
    if not SELECTION.exists():
        return [f"{label}: arquivo ausente em research/datasets/"], 0
    text = SELECTION.read_text(encoding="utf-8")
    flat = " ".join(text.split())
    failures: list[str] = []
    for section in SELECTION_SECTIONS:
        if section not in text:
            failures.append(f"{label}: seção obrigatória ausente '{section}'")
    for token in SELECTION_TOKENS:
        if token.lower() not in text.lower():
            failures.append(f"{label}: token obrigatório ausente '{token}'")
    for decision in SELECTION_DECISIONS:
        block = re.search(
            rf"### {decision} — .*?\n(.*?)(?=\n### |\n## |\Z)", text, re.S
        )
        if block is None:
            failures.append(f"{label}: decisão obrigatória ausente {decision}")
            continue
        status = field_value(block.group(1).splitlines(), "Status")
        if status != SELECTION_PENDING:
            failures.append(
                f"{label}: {decision} deve ficar como '{SELECTION_PENDING}' até o G2 (achado '{status}')"
            )
    for line in text.splitlines():
        match = re.match(r"^\s*- Status: (.+?)\s*$", line)
        if match and match.group(1).strip().rstrip(".") != SELECTION_PENDING:
            failures.append(f"{label}: status '{match.group(1).strip()}' não é proposta pendente de G2")

    known_lit = set(re.findall(r"^(LIT-\d{4})\t", LIT_LEDGER.read_text(encoding="utf-8"), re.M))
    refs = sorted(set(re.findall(r"LIT-\d{4}", text)))
    if len(refs) < 5:
        failures.append(f"{label}: menos de 5 referências LIT-* para justificar o ranking")
    for lit_id in refs:
        if known_lit and lit_id not in known_lit:
            failures.append(f"{label}: referencia ledger inexistente '{lit_id}'")

    leak = PUBLIC_ID_RE.search(text)
    if leak:
        failures.append(f"{label}: possível ID cru de neurônio no documento público ('{leak.group(0)}')")

    known = {item_id for _, item_id in parse_items(PLAN.read_text(encoding="utf-8").splitlines())}
    for ref in sorted(ref for ref in phase_refs(text) if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    pairs = sorted(set(re.findall(r"PAIR-\d{2}", text)))
    if len(pairs) < 6:
        failures.append(f"{label}: esperados ao menos 6 pares avaliados (achados {len(pairs)})")
    return failures, len(pairs)


def check_resource_estimates() -> tuple[list[str], int]:
    label = "RECURSOS.md"
    if not RESOURCES.exists():
        return [f"{label}: arquivo ausente em research/datasets/"], 0
    text = RESOURCES.read_text(encoding="utf-8")
    failures: list[str] = []
    for section in RESOURCES_SECTIONS:
        if section not in text:
            failures.append(f"{label}: seção obrigatória ausente '{section}'")
    for token in RESOURCES_TOKENS:
        if token.lower() not in text.lower():
            failures.append(f"{label}: token obrigatório ausente '{token}'")
    if "fora do Git" not in text and "não entram no repositório" not in text:
        failures.append(f"{label}: sem declaração de que amostras ficam fora do Git")

    rows = [
        line
        for line in text.splitlines()
        if line.startswith("|") and len(line.split("|")) >= 9 and re.search(r"\|\s*[\d.]+\s*\|", line)
    ]
    if len(rows) < 6:
        failures.append(f"{label}: esperadas ao menos 6 amostras com bytes na tabela (achadas {len(rows)})")

    known_lit = set(re.findall(r"^(LIT-\d{4})\t", LIT_LEDGER.read_text(encoding="utf-8"), re.M))
    refs = sorted(set(re.findall(r"LIT-\d{4}", text)))
    if len(refs) < 5:
        failures.append(f"{label}: menos de 5 referências LIT-* para contagens publicadas")
    for lit_id in refs:
        if known_lit and lit_id not in known_lit:
            failures.append(f"{label}: referencia ledger inexistente '{lit_id}'")

    leak = PUBLIC_ID_RE.search(text)
    if leak:
        failures.append(f"{label}: possível ID cru de neurônio no documento público ('{leak.group(0)}')")

    known = {item_id for _, item_id in parse_items(PLAN.read_text(encoding="utf-8").splitlines())}
    for ref in sorted(ref for ref in phase_refs(text) if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(rows)


def check_crosswalk_audit() -> tuple[list[str], int, int]:
    label = "CROSSWALK-AUDIT.md"
    if not CROSSWALK.exists():
        return [f"{label}: arquivo ausente em research/datasets/"], 0, 0
    text = CROSSWALK.read_text(encoding="utf-8")
    flat = " ".join(text.split()).lower()
    failures: list[str] = []
    for section in CROSSWALK_SECTIONS:
        if section not in text:
            failures.append(f"{label}: seção obrigatória ausente '{section}'")
    for rule in CROSSWALK_RULES:
        if rule not in flat:
            failures.append(f"{label}: regra obrigatória ausente ('{rule}')")
    leak = PUBLIC_ID_RE.search(text)
    if leak:
        failures.append(f"{label}: possível ID/mapeamento exato no documento público ('{leak.group(0)}')")

    rows = _ledger_rows()
    known_lit = _known_lit_ids(rows)

    approved = 0
    pairs = parse_heading_blocks(text, r"^### (PAIR-\d{2}) — (.+)$")
    if len(pairs) < 6:
        failures.append(f"{label}: esperados ao menos 6 pares (achados {len(pairs)})")
    for pair_id, block in pairs:
        for field in CROSSWALK_PAIR_FIELDS:
            if field_value(block, field) is None:
                failures.append(f"{label}: {pair_id} sem campo '{field}'")
        status = field_value(block, "Status")
        if status is not None:
            if status not in ALLOWED_CROSSWALK_STATUSES:
                failures.append(f"{label}: {pair_id} status inválido '{status}'")
            if status == CROSSWALK_APPROVED:
                approved += 1
        sources = field_value(block, "Fontes") or ""
        if not re.search(r"LIT-\d{4}", sources):
            failures.append(f"{label}: {pair_id} sem fontes LIT-*")
        for lit_id in sorted(set(re.findall(r"LIT-\d{4}", sources))):
            if known_lit and lit_id not in known_lit:
                failures.append(f"{label}: {pair_id} referencia ledger inexistente '{lit_id}'")

    decisions = parse_heading_blocks(text, r"^### (DEC-CW-\d{2}) — (.+)$")
    if len(decisions) < 4:
        failures.append(f"{label}: esperadas ao menos 4 decisões (achadas {len(decisions)})")
    for dec_id, block in decisions:
        for field in CROSSWALK_DEC_FIELDS:
            if field_value(block, field) is None:
                failures.append(f"{label}: {dec_id} sem campo '{field}'")
        status = field_value(block, "Status")
        if status is not None:
            if status not in ALLOWED_CROSSWALK_STATUSES:
                failures.append(f"{label}: {dec_id} status inválido '{status}'")
            if status == CROSSWALK_APPROVED:
                approved += 1

    for line in text.splitlines():
        match = re.match(r"^\s*- Status: (.+?)\s*$", line)
        if match:
            status = match.group(1).strip().rstrip(".")
            if status not in ALLOWED_CROSSWALK_STATUSES:
                failures.append(f"{label}: status '{status}' não permitido")

    if approved:
        section = re.search(r"## 8\. Aprovação humana\n(.*?)(?=\n## |\Z)", text, re.S)
        if section is None:
            failures.append(f"{label}: status APROVADO sem seção de aprovação humana")
        else:
            approval_lines = section.group(1).splitlines()
            for field in CROSSWALK_APPROVAL_FIELDS:
                if field_value(approval_lines, field) is None:
                    failures.append(f"{label}: aprovação humana sem campo '{field}'")
            approver = field_value(approval_lines, "Aprovador")
            if approver is not None and not any(
                word in approver.lower() for word in ("humano", "revisor")
            ):
                failures.append(f"{label}: aprovador não identificado como humano/revisor: '{approver}'")
            if "segundo revisor" not in flat:
                failures.append(f"{label}: aprovação sem declarar a pendência do segundo revisor")

    known = {item_id for _, item_id in parse_items(PLAN.read_text(encoding="utf-8").splitlines())}
    refs = phase_refs(text)
    for ref in sorted(ref for ref in refs if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(pairs), approved


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
        NOVELTY,
        GATE_G1,
        DATASETS_INVENTORY,
        CROSSWALK,
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
    novelty_failures, novelty_gaps = check_novelty()
    gate_g1_failures, gate_g1_criteria, gate_g1_state = check_gate_g1()
    inventory_failures, inventory_candidates = check_dataset_inventory()
    crosswalk_failures, crosswalk_pairs, crosswalk_approved = check_crosswalk_audit()
    resources_failures, resource_samples = check_resource_estimates()
    selection_failures, selection_pairs = check_dataset_selection()
    gate_g2_failures, gate_g2_criteria, gate_g2_state = check_gate_g2()
    data_management_failures, data_management_sections = check_data_management()
    environment_failures, environment_tokens = check_environment_phase()
    provenance_failures, provenance_manifests = check_provenance_phase()
    run_contract_failures, run_contract_tokens = check_run_contract()
    firewall_failures, firewall_tokens = check_firewall_phase()
    statistical_plan_failures, statistical_plan_tokens = check_statistical_plan()
    prereg_failures, prereg_entries, prereg_state = check_preregistration()
    dry_run_failures, dry_run_tokens = check_dry_run()
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
        + novelty_failures
        + gate_g1_failures
        + inventory_failures
        + crosswalk_failures
        + resources_failures
        + selection_failures
        + gate_g2_failures
        + data_management_failures
        + environment_failures
        + provenance_failures
        + run_contract_failures
        + firewall_failures
        + statistical_plan_failures
        + prereg_failures
        + dry_run_failures
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
    print(
        f"OK: research/literature/NOVIDADE.md com {novelty_gaps} lacunas e no "
        f"máximo três contribuições"
    )
    print(
        f"OK: G1-LITERATURA.md com decisão {gate_g1_state}, {gate_g1_criteria} "
        f"critérios, snapshot conferido e estado do plano coerente"
    )
    print(
        f"OK: research/datasets/INVENTARIO.md com {inventory_candidates} candidatos "
        f"e cards não confirmados"
    )
    print(
        f"OK: research/datasets/CROSSWALK-AUDIT.md com {crosswalk_pairs} pares e "
        f"{crosswalk_approved} status aprovados por humano"
    )
    print(
        f"OK: research/datasets/RECURSOS.md com {resource_samples} amostras medidas, "
        f"checksums e projeções classificadas"
    )
    print(
        f"OK: research/datasets/SELECAO.md com {selection_pairs} pares ranqueados e "
        f"decisão pendente de G2"
    )
    print(
        f"OK: docs/gates/G2-DADOS.md com {gate_g2_criteria} critérios, cards congelados "
        f"e decisão {gate_g2_state}"
    )
    print(
        f"OK: gestão de dados com {data_management_sections} seções, .gitignore "
        f"revisado e teste de higiene de sentinelas"
    )
    print(
        f"OK: ambiente R02 com {environment_tokens} tokens, lock pinado e "
        f"operação CUDA medida na RTX 4060"
    )
    print(
        f"OK: proveniência R03 com schema, validador e {provenance_manifests} "
        f"manifestos sem credenciais"
    )
    print(
        f"OK: contrato de run R04 com {run_contract_tokens} tokens, fixture "
        f"determinística e RUN-MANIFEST"
    )
    print(
        f"OK: firewall R05 com {firewall_tokens} tokens, scanner limpo e selado "
        f"com permissões restritas"
    )
    print(
        f"OK: plano estatístico R06 com {statistical_plan_tokens} tokens, schemas "
        f"de predições/métricas e avaliador selado"
    )
    print(
        f"OK: pré-registro R07 com {prereg_entries} artefatos congelados e "
        f"assinatura {prereg_state}"
    )
    print(
        f"OK: dry run R08 com {dry_run_tokens} tokens, manifesto ponta a ponta e "
        f"handoff ao custodiante"
    )
    print(f"OK: {refs} referências de fase resolvidas contra o plano")
    print(f"OK: {paths} caminhos de arquivo citados e existentes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
