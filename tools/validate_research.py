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
B05_TOOL = ROOT / "tools" / "mlp_control.py"
B05_REPORT = ROOT / "artifacts" / "reports" / "B05-MLP.md"
B05_METRICS = ROOT / "artifacts" / "reports" / "B05-MLP.json"
B05_TOKENS = (
    "mlp",
    "mesmas features",
    "source-fit",
    "não linearidade",
    "smoke",
    "overfit",
    "determinístico",
    "sem nenhum dado do alvo",
)
B06_TOOL = ROOT / "tools" / "node2vec_baseline.py"
B06_REPORT = ROOT / "artifacts" / "reports" / "B06-NODE2VEC.md"
B06_METRICS = ROOT / "artifacts" / "reports" / "B06-NODE2VEC.json"
B06_TOKENS = (
    "node2vec",
    "deepwalk",
    "transdutivo",
    "não comparável zero-shot",
    "rotação",
    "permutação",
    "source-fit",
    "sem nenhum dado do alvo",
)
B07_TOOL = ROOT / "tools" / "spectral_baseline.py"
B07_REPORT = ROOT / "artifacts" / "reports" / "B07-ESPECTRAL.md"
B07_METRICS = ROOT / "artifacts" / "reports" / "B07-ESPECTRAL.json"
B07_TOKENS = (
    "espectral",
    "sparse",
    "svd",
    "simetriz",
    "direção",
    "sinal",
    "rotação",
    "within-source",
    "não comparável zero-shot",
    "sem nenhum dado do alvo",
)
B04_TOOL = ROOT / "tools" / "artisanal_features.py"
B04_REPORT = ROOT / "artifacts" / "reports" / "B04-ARTESANAL.md"
B04_METRICS = ROOT / "artifacts" / "reports" / "B04-ARTESANAL.json"
B04_TOKENS = (
    "famílias",
    "ablação",
    "invariância",
    "grafo conhecido",
    "probe",
    "interrompida",
    "source-fit",
    "sem nenhum dado do alvo",
)
B03_TOOL = ROOT / "tools" / "baselines_source.py"
B03_REPORT = ROOT / "artifacts" / "reports" / "B03-BASELINES-FONTE.md"
B03_METRICS = ROOT / "artifacts" / "reports" / "B03-BASELINES-FONTE.json"
B03_TOKENS = (
    "random estratificado",
    "maioria",
    "degree-only",
    "source-fit",
    "chance analítica",
    "simulado",
    "seeds",
    "congeláveis",
)
B02_TOOL = ROOT / "tools" / "calibration.py"
B02_REPORT = ROOT / "artifacts" / "reports" / "B02-CALIBRACAO-OPEN-SET.md"
B02_TOKENS = (
    "brier",
    "ece",
    "auroc",
    "aupr",
    "fpr@tpr",
    "bootstrap",
    "permuta",
    "seed",
    "somente na fonte",
    "sem i/o",
)
B01_TOOL = ROOT / "tools" / "metrics.py"
B01_REPORT = ROOT / "artifacts" / "reports" / "B01-METRICAS.md"
B01_TOKENS = (
    "recall@1",
    "micro",
    "macro",
    "empates",
    "multi-instance",
    "sem match",
    "orientação",
    "sem i/o",
)
GATE_G4 = ROOT / "docs" / "gates" / "G4-DADOS-ANALITICOS.md"
GATE_G4_SECTIONS = (
    "## Pacote de revisão",
    "## Artefatos e hashes",
    "## Critérios",
    "## Riscos e divergências",
    "## Condições do G4",
    "## Escopo liberado",
    "## Assinaturas",
)
GATE_G4_SIGNATURE_FIELDS = (
    "Responsável científico",
    "Custodiante dos dados",
    "Revisor de método/estatística",
)
GATE_G4_HASH_RE = re.compile(r"^- SHA-256 `([0-9a-f]{64})` — `([^`]+)`$")
H09_TOOL = ROOT / "tools" / "data_quality.py"
H09_REPORT = ROOT / "artifacts" / "reports" / "DATA-QUALITY.md"
H09_METRICS = ROOT / "artifacts" / "reports" / "DATA-QUALITY.json"
H09_MANIFEST = ROOT / "data" / "manifests" / "analitico-v1.json"
H09_TOKENS = (
    "exploratório",
    "duplicad",
    "componentes",
    "reciprocidade",
    "drift",
    "congel",
    "inconclusiv",
    "nenhum rótulo",
)
H08_TOOL = ROOT / "tools" / "snapshot_build.py"
H08_REPORT = ROOT / "artifacts" / "reports" / "H08-SNAPSHOTS.md"
H08_METRICS = ROOT / "artifacts" / "reports" / "H08-SNAPSHOTS.json"
H08_TOKENS = (
    "idempot",
    "28 gb",
    "segment-to-segment",
    "nível-neurônio",
    "sem labels",
    "conservada",
    "retomada",
    "cached",
)
H07_TOOL = ROOT / "tools" / "sealed_labels.py"
H07_PACKAGE = ROOT / "docs" / "research" / "H07-PACKAGE.md"
H07_HEMI_METRICS = ROOT / "artifacts" / "reports" / "H07-HEMILINEAGE-AUDIT.json"
H07_HEMI_DRAFT = ROOT / "preregistration" / "crosswalk-hemilineage.draft.json"
H07_AUDIT_MD = ROOT / "artifacts" / "reports" / "H07-PROVENANCE-AUDIT.md"
H07_AUDIT_JSON = ROOT / "artifacts" / "reports" / "H07-PROVENANCE-AUDIT.json"
H07_DRAFT = ROOT / "preregistration" / "crosswalk-manc-mcns.draft.json"
H07_DRAFT_METRICS = ROOT / "artifacts" / "reports" / "H07-CROSSWALK-DRAFT.json"
H07_TOKENS = (
    "dupla revisão",
    "segundo revisor",
    "bloquead",
    "custodiante",
    "circular",
    "cobertura",
    "hashes",
    "zona selada",
)
EDGE_TOOL = ROOT / "tools" / "edge_transform.py"
EDGE_PRIMARY = ROOT / "configs" / "edge-primary.json"
EDGE_VARIANTS = ROOT / "configs" / "edge-variants.json"
EDGE_REPORT = ROOT / "artifacts" / "reports" / "H06-EDGES-VARIANTES.md"
EDGE_METRICS = ROOT / "artifacts" / "reports" / "H06-EDGES-VARIANTES.json"
EDGE_TOKENS = (
    "peso zero",
    "self-loops",
    "isolados",
    "conservação",
    "threshold",
    "symmetrized",
    "log1p",
    "pré-registro",
    "sem usar nenhuma estatística do alvo",
    "limitaç",
)
TOPOLOGY_TOOL = ROOT / "tools" / "topology_features.py"
OPAQUE_TOOL = ROOT / "tools" / "opaque_ids.py"
TOPOLOGY_REPORT = ROOT / "artifacts" / "reports" / "H05-FEATURES-TOPO.md"
TOPOLOGY_TOKENS = (
    "opaco",
    "fit",
    "transform",
    "somente na fonte",
    "permutar",
    "não finitos",
    "clip",
    "proibido",
    "reciprocidade",
    "limitaç",
)
SEALED_EVALUATOR_TOOL = ROOT / "tools" / "sealed_evaluator.py"
SEALED_EVALUATOR_REPORT = ROOT / "artifacts" / "reports" / "H04-AVALIADOR-SELADO.md"
SEALED_EVALUATOR_TOKENS = (
    "custodiante",
    "label schema",
    "cobertura",
    "crosswalk",
    "hash do label set",
    "logs",
    "sessão separada",
    "firewall",
    "métricas agregadas",
    "limitaç",
)
TARGET_ADAPTER_TOOL = ROOT / "tools" / "adapter_mcns.py"
TARGET_ADAPTER_REPORT = ROOT / "artifacts" / "reports" / "H03-ADAPTER-ALVO.md"
TARGET_ADAPTER_METRICS = ROOT / "artifacts" / "reports" / "H03-ADAPTER-ALVO.json"
TARGET_ADAPTER_GOLDEN = ROOT / "tests" / "fixtures" / "mcns-sample-graph.json"
TARGET_ADAPTER_TOKENS = (
    "adapter",
    "conserv",
    "self-loop",
    "reconcilia",
    "trilho a",
    "amostra dourada",
    "checksum",
    "data/sealed",  # firewall-allow
    "limitaç",
)
ADAPTER_TOOL = ROOT / "tools" / "adapter_manc.py"
ADAPTER_REPORT = ROOT / "artifacts" / "reports" / "H02-ADAPTER-FONTE.md"
ADAPTER_METRICS = ROOT / "artifacts" / "reports" / "H02-ADAPTER-FONTE.json"
ADAPTER_GOLDEN = ROOT / "tests" / "fixtures" / "manc-sample-graph.json"
ADAPTER_TOKENS = (
    "adapter",
    "agregação",
    "conserv",
    "self-loop",
    "reconcilia",
    "trilho a",
    "checksum",
    "amostra dourada",
    "limitaç",
)
GRAPH_SCHEMA = ROOT / "schemas" / "graph.schema.json"
GRAPH_CONTRACT_DOC = ROOT / "docs" / "research" / "GRAPH-CONTRACT.md"
GRAPH_TOOL = ROOT / "tools" / "graph_contract.py"
GRAPH_FIXTURE = ROOT / "tests" / "fixtures" / "graph-fixture.json"
GRAPH_SECTIONS = (
    "## 1. Princípios",
    "## 2. Nodes",
    "## 3. Edges",
    "## 4. Grafo e agregados",
    "## 5. Proveniência",
    "## 6. Missingness",
    "## 7. Round-trip",
    "## 8. Constraints e validação",
    "## 9. Limitações",
)
GRAPH_TOKENS = (
    "multiedge",
    "self-loop",
    "peso zero",
    "nan",
    "threshold",
    "agregação",
    "proveniência",
    "missingness",
    "opaco",
    "round-trip",
    "unidades",
    "conservação",
)
GATE_G3 = ROOT / "docs" / "gates" / "G3-PREREGISTRO.md"
GATE_G3_SECTIONS = (
    "## Pacote de revisão",
    "## Artefatos e hashes",
    "## Critérios",
    "## Riscos e divergências",
    "## Condições do G3",
    "## Escopo liberado",
    "## Assinaturas",
)
GATE_G3_SIGNATURE_FIELDS = (
    "Responsável científico",
    "Revisor de estatística",
    "Custodiante designado",
)
GATE_G3_HASH_RE = re.compile(r"^- SHA-256 `([0-9a-f]{64})` — `([^`]+)`$")
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


def check_b04_artisanal() -> tuple[list[str], int]:
    label = "B04"
    failures: list[str] = []
    for path in (B04_TOOL, B04_REPORT, B04_METRICS, ROOT / "tests" / "test_artisanal_features.py"):
        if not path.exists():
            failures.append(f"{label}: arquivo ausente '{path.relative_to(ROOT)}'")
    if failures:
        return failures, 0
    report = B04_REPORT.read_text(encoding="utf-8")
    flat = " ".join(report.split()).lower()
    for token in B04_TOKENS:
        if token.lower() not in flat:
            failures.append(f"{label}: relatório sem token '{token}'")
    leak = PUBLIC_ID_RE.search(report)
    if leak:
        failures.append(f"{label}: relatório com possível ID cru ('{leak.group(0)}')")
    source = B04_TOOL.read_text(encoding="utf-8")
    for token in ("male-cns", "data/sealed", "target_labels", "crosswalk"):  # firewall-allow
        if token in source:
            failures.append(f"{label}: features artesanais não podem referenciar o alvo ('{token}')")
    metrics = json.loads(B04_METRICS.read_text(encoding="utf-8"))
    results = metrics.get("results", {})
    if set(results) != {"degree", "reciprocity", "clustering", "motifs", "neighborhood", "all"}:
        failures.append(f"{label}: famílias da ablação divergentes")
    for family, data in results.items():
        value = float(data.get("macro_recall@1", -1))
        if not 0.0 <= value <= 1.0:
            failures.append(f"{label}: macro fora de [0,1] em '{family}'")
    if abs(results["degree"]["macro_recall@1"] - metrics.get("baseline_degree_only_macro@1", -1)) > 1e-6:
        failures.append(f"{label}: família degree deve reproduzir o baseline B03")
    if not metrics.get("interrupted_features"):
        failures.append(f"{label}: feature interrompida não registrada")
    if not re.fullmatch(r"[0-9a-f]{64}", str(metrics.get("predictions", {}).get("sha256", ""))):
        failures.append(f"{label}: predição sem hash válido")
    plan_lines = PLAN.read_text(encoding="utf-8").splitlines()
    known = {item_id for _, item_id in parse_items(plan_lines)}
    for ref in sorted(ref for ref in phase_refs(report) if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(B04_TOKENS)


def check_b05_mlp() -> tuple[list[str], int]:
    label = "B05"
    failures: list[str] = []
    for path in (B05_TOOL, B05_REPORT, B05_METRICS, ROOT / "tests" / "test_mlp_control.py"):
        if not path.exists():
            failures.append(f"{label}: arquivo ausente '{path.relative_to(ROOT)}'")
    if failures:
        return failures, 0
    report = B05_REPORT.read_text(encoding="utf-8")
    flat = " ".join(report.split()).lower()
    for token in B05_TOKENS:
        if token.lower() not in flat:
            failures.append(f"{label}: relatório sem token '{token}'")
    leak = PUBLIC_ID_RE.search(report)
    if leak:
        failures.append(f"{label}: relatório com possível ID cru ('{leak.group(0)}')")
    source = B05_TOOL.read_text(encoding="utf-8")
    for token in ("male-cns", "data/sealed", "target_labels", "crosswalk"):  # firewall-allow
        if token in source:
            failures.append(f"{label}: MLP de controle não pode referenciar o alvo ('{token}')")
    metrics = json.loads(B05_METRICS.read_text(encoding="utf-8"))
    if metrics.get("schema") != "b05-mlp-control":
        failures.append(f"{label}: schema do relatório divergente")
    if list(metrics.get("features", [])) != [
        "in_degree",
        "out_degree",
        "weighted_in",
        "weighted_out",
        "reciprocal_weight_ratio",
        "reciprocal_count_ratio",
        "clustering_undirected",
        "feedforward_paths",
        "bottleneck_ratio",
        "successor_out_degree_mean",
        "predecessor_in_degree_mean",
    ]:
        failures.append(f"{label}: MLP deve usar as mesmas features de B04")
    results = metrics.get("results", {})
    if set(results) != {"s", "m", "l"}:
        failures.append(f"{label}: configs divergentes (esperado s/m/l)")
    for name, data in results.items():
        value = float(data.get("median_macro_recall@1", -1))
        if not 0.0 <= value <= 1.0:
            failures.append(f"{label}: macro fora de [0,1] em '{name}'")
        if len(data.get("per_seed", [])) != 3:
            failures.append(f"{label}: config '{name}' sem as 3 seeds do pré-registro")
    if list(metrics.get("seeds", [])) != [297979363399525401, 1699981902186354598, 3729859090210297070]:
        failures.append(f"{label}: seeds divergentes do pré-registro")
    params = {name: int(data.get("n_params", -1)) for name, data in results.items()}
    if not 80_000 <= params.get("s", -1) <= 130_000:
        failures.append(f"{label}: config 's' fora do budget ~100k")
    if not 400_000 <= params.get("m", -1) <= 600_000:
        failures.append(f"{label}: config 'm' fora do budget ~500k")
    if not 1_000_000 <= params.get("l", -1) <= 3_000_000:
        failures.append(f"{label}: config 'l' fora da faixa pareada 1-3M")
    if str(metrics.get("hyperparameters", {}).get("device", "")) != "cpu":
        failures.append(f"{label}: dispositivo deve ser cpu nesta fase")
    for entry in metrics.get("predictions", []):
        if not re.fullmatch(r"[0-9a-f]{64}", str(entry.get("sha256", ""))):
            failures.append(f"{label}: predição sem hash válido")
    if len(metrics.get("predictions", [])) != 9:
        failures.append(f"{label}: esperado 9 pacotes de predições (3 configs x 3 seeds)")
    plan_lines = PLAN.read_text(encoding="utf-8").splitlines()
    known = {item_id for _, item_id in parse_items(plan_lines)}
    for ref in sorted(ref for ref in phase_refs(report) if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(B05_TOKENS)


def check_b06_transductive() -> tuple[list[str], int]:
    label = "B06"
    failures: list[str] = []
    for path in (B06_TOOL, B06_REPORT, B06_METRICS, ROOT / "tests" / "test_node2vec_baseline.py"):
        if not path.exists():
            failures.append(f"{label}: arquivo ausente '{path.relative_to(ROOT)}'")
    if failures:
        return failures, 0
    report = B06_REPORT.read_text(encoding="utf-8")
    flat = " ".join(report.split()).lower()
    for token in B06_TOKENS:
        if token.lower() not in flat:
            failures.append(f"{label}: relatório sem token '{token}'")
    leak = PUBLIC_ID_RE.search(report)
    if leak:
        failures.append(f"{label}: relatório com possível ID cru ('{leak.group(0)}')")
    source = B06_TOOL.read_text(encoding="utf-8")
    for token in ("male-cns", "data/sealed", "target_labels", "crosswalk"):  # firewall-allow
        if token in source:
            failures.append(f"{label}: baseline transdutivo não pode referenciar o alvo ('{token}')")
    metrics = json.loads(B06_METRICS.read_text(encoding="utf-8"))
    if metrics.get("schema") != "b06-node2vec":
        failures.append(f"{label}: schema do relatório divergente")
    if metrics.get("verdict") != "não comparável zero-shot":
        failures.append(f"{label}: veredito deve marcar não comparável zero-shot")
    results = metrics.get("results", {})
    if set(results) != {"deepwalk", "node2vec"}:
        failures.append(f"{label}: configs divergentes (esperado deepwalk/node2vec)")
    if results.get("deepwalk", {}).get("p") != 1.0 or results.get("deepwalk", {}).get("q") != 1.0:
        failures.append(f"{label}: deepwalk deve ser p=q=1")
    if results.get("node2vec", {}).get("p") != 1.0 or results.get("node2vec", {}).get("q") != 0.5:
        failures.append(f"{label}: node2vec deve ser p=1, q=0.5")
    for name, data in results.items():
        value = float(data.get("median_macro_recall@1", -1))
        if not 0.0 <= value <= 1.0:
            failures.append(f"{label}: macro fora de [0,1] em '{name}'")
        if len(data.get("per_seed", [])) != 3:
            failures.append(f"{label}: config '{name}' sem as 3 seeds do pré-registro")
        agreement = float(data.get("rotation_agreement", -1))
        if not 0.0 <= agreement <= 1.0:
            failures.append(f"{label}: concordância pós-rotação fora de [0,1] em '{name}'")
        cosines = data.get("seed_cosine", {})
        if set(cosines) != {"0x1", "0x2", "1x2"}:
            failures.append(f"{label}: pares de cosseno entre seeds incompletos em '{name}'")
        for pair, cosine in cosines.items():
            if not -1.0 <= float(cosine) <= 1.0:
                failures.append(f"{label}: cosseno fora de [-1,1] em '{name}/{pair}'")
            if abs(float(cosine)) >= 0.2:
                failures.append(f"{label}: coordenadas entre seeds deveriam ser arbitrárias em '{name}/{pair}'")
    if list(metrics.get("seeds", [])) != [297979363399525401, 1699981902186354598, 3729859090210297070]:
        failures.append(f"{label}: seeds divergentes do pré-registro")
    hyper = metrics.get("hyperparameters", {})
    for key, expected in (("walks_per_node", 4), ("walk_length", 25), ("window", 5), ("dim", 64),
                          ("epochs", 2), ("negatives", 5), ("batch", 16384)):
        if hyper.get(key) != expected:
            failures.append(f"{label}: hiperparâmetro '{key}' divergente do fixado ({expected})")
    if str(hyper.get("device", "")) != "cpu":
        failures.append(f"{label}: dispositivo deve ser cpu nesta fase")
    for entry in metrics.get("predictions", []):
        if not re.fullmatch(r"[0-9a-f]{64}", str(entry.get("sha256", ""))):
            failures.append(f"{label}: predição sem hash válido")
    if len(metrics.get("predictions", [])) != 6:
        failures.append(f"{label}: esperado 6 pacotes de predições (2 configs x 3 seeds)")
    for entry in metrics.get("embeddings", []):
        if not re.fullmatch(r"[0-9a-f]{64}", str(entry.get("sha256", ""))):
            failures.append(f"{label}: embedding sem hash válido")
        if not (ROOT / entry.get("path", "")).exists():
            failures.append(f"{label}: arquivo de embedding ausente '{entry.get('path', '')}'")
    if len(metrics.get("embeddings", [])) != 6:
        failures.append(f"{label}: esperado 6 pacotes de embeddings (2 configs x 3 seeds)")
    plan_lines = PLAN.read_text(encoding="utf-8").splitlines()
    known = {item_id for _, item_id in parse_items(plan_lines)}
    for ref in sorted(ref for ref in phase_refs(report) if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(B06_TOKENS)


def check_b07_spectral() -> tuple[list[str], int]:
    label = "B07"
    failures: list[str] = []
    for path in (B07_TOOL, B07_REPORT, B07_METRICS, ROOT / "tests" / "test_spectral_baseline.py"):
        if not path.exists():
            failures.append(f"{label}: arquivo ausente '{path.relative_to(ROOT)}'")
    if failures:
        return failures, 0
    report = B07_REPORT.read_text(encoding="utf-8")
    flat = " ".join(report.split()).lower()
    for token in B07_TOKENS:
        if token.lower() not in flat:
            failures.append(f"{label}: relatório sem token '{token}'")
    leak = PUBLIC_ID_RE.search(report)
    if leak:
        failures.append(f"{label}: relatório com possível ID cru ('{leak.group(0)}')")
    source = B07_TOOL.read_text(encoding="utf-8")
    for token in ("male-cns", "data/sealed", "target_labels", "crosswalk"):  # firewall-allow
        if token in source:
            failures.append(f"{label}: espectral não pode referenciar o alvo ('{token}')")
    for token in (".toarray(", ".todense(", "todense()", "asmatrix("):
        if token in source:
            failures.append(f"{label}: código não pode densificar a matriz ('{token}')")
    for token in ("spla.svds(", "spla.eigsh("):
        if token not in source:
            failures.append(f"{label}: solver esparso ausente ('{token}')")
    metrics = json.loads(B07_METRICS.read_text(encoding="utf-8"))
    if metrics.get("schema") != "b07-spectral":
        failures.append(f"{label}: schema do relatório divergente")
    if metrics.get("verdict") != "restrito ao diagnóstico within-source (não comparável zero-shot)":
        failures.append(f"{label}: veredito deve restringir a within-source e não comparável zero-shot")
    results = metrics.get("results", {})
    if set(results) != {"svd_dirigido", "ase_simetrizado"}:
        failures.append(f"{label}: configs divergentes (esperado svd_dirigido/ase_simetrizado)")
    expected_dims = {"svd_dirigido": 64, "ase_simetrizado": 32}
    for name, data in results.items():
        if int(data.get("k_components", -1)) != 32:
            failures.append(f"{label}: componentes divergentes em '{name}'")
        if int(data.get("dims", -1)) != expected_dims.get(name, -1):
            failures.append(f"{label}: dimensões divergentes em '{name}'")
        if len(data.get("per_seed", [])) != 3:
            failures.append(f"{label}: config '{name}' sem as 3 seeds do pré-registro")
        value = float(data.get("median_macro_recall@1", -1))
        if not 0.0 <= value <= 1.0:
            failures.append(f"{label}: macro fora de [0,1] em '{name}'")
        equivariant = float(data.get("rotation_agreement_equivariant_probe", -1))
        if equivariant != 1.0:
            failures.append(f"{label}: rotação com probe equívariante deve ser 1,0 em '{name}'")
        sign = float(data.get("sign_agreement", -1))
        if sign != 1.0:
            failures.append(f"{label}: sinal deve preservar decisões em '{name}'")
        standard = float(data.get("rotation_agreement_standard_probe", -1))
        if not 0.0 <= standard <= 1.0:
            failures.append(f"{label}: sensibilidade padrão fora de [0,1] em '{name}'")
        seed_agreement = data.get("prediction_agreement_seed0", {})
        if set(seed_agreement) != {"0x1", "0x2"}:
            failures.append(f"{label}: concordância entre seeds incompleta em '{name}'")
        for pair, agreement in seed_agreement.items():
            if float(agreement) != 1.0:
                failures.append(f"{label}: predições entre seeds devem concordar em '{name}/{pair}'")
        subspaces = data.get("subspace_cosines", {})
        if set(subspaces) != {"0x1", "0x2", "1x2"}:
            failures.append(f"{label}: pares de subespaço incompletos em '{name}'")
        for pair, angles in subspaces.items():
            for key in ("min_cos", "mean_cos"):
                value = float(angles.get(key, -1))
                if not 0.0 <= value <= 1.0:
                    failures.append(f"{label}: cosseno de subespaço fora de [0,1] em '{name}/{pair}/{key}'")
                if value < 0.999:
                    failures.append(f"{label}: subespaço entre seeds deve ser estável em '{name}/{pair}/{key}'")
    if list(metrics.get("seeds", [])) != [297979363399525401, 1699981902186354598, 3729859090210297070]:
        failures.append(f"{label}: seeds divergentes do pré-registro")
    hyper = metrics.get("hyperparameters", {})
    if int(hyper.get("components", -1)) != 32:
        failures.append(f"{label}: componentes do pré-registro divergentes")
    if "sparse" not in str(hyper.get("solver", "")).lower():
        failures.append(f"{label}: solver deve declarar operador esparso")
    resources = metrics.get("resources", {})
    if int(resources.get("nodes", -1)) != 23188 or int(resources.get("directed_nnz", -1)) != 5243574:
        failures.append(f"{label}: contagens do snapshot H08 divergentes")
    matrix_bytes = float(resources.get("directed_matrix_bytes", -1))
    dense_bytes = float(resources.get("directed_dense_equivalent_bytes", -1))
    if dense_bytes <= 0 or matrix_bytes <= 0 or matrix_bytes >= dense_bytes / 10:
        failures.append(f"{label}: matriz deveria permanecer esparsa (sem densificação)")
    if int(resources.get("ram_cap_gib", -1)) != 24:
        failures.append(f"{label}: teto de RAM da fase divergente")
    if str(resources.get("device", "")) != "cpu":
        failures.append(f"{label}: dispositivo deve ser cpu nesta fase")
    for entry in metrics.get("predictions", []):
        if not re.fullmatch(r"[0-9a-f]{64}", str(entry.get("sha256", ""))):
            failures.append(f"{label}: predição sem hash válido")
        if not (ROOT / entry.get("path", "")).exists():
            failures.append(f"{label}: arquivo de predição ausente '{entry.get('path', '')}'")
    if len(metrics.get("predictions", [])) != 6:
        failures.append(f"{label}: esperado 6 pacotes de predições (2 configs x 3 seeds)")
    for entry in metrics.get("embeddings", []):
        if not re.fullmatch(r"[0-9a-f]{64}", str(entry.get("sha256", ""))):
            failures.append(f"{label}: embedding sem hash válido")
        if not (ROOT / entry.get("path", "")).exists():
            failures.append(f"{label}: arquivo de embedding ausente '{entry.get('path', '')}'")
    if len(metrics.get("embeddings", [])) != 6:
        failures.append(f"{label}: esperado 6 pacotes de embeddings (2 configs x 3 seeds)")
    plan_lines = PLAN.read_text(encoding="utf-8").splitlines()
    known = {item_id for _, item_id in parse_items(plan_lines)}
    for ref in sorted(ref for ref in phase_refs(report) if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(B07_TOKENS)


def check_b03_source_baselines() -> tuple[list[str], int]:
    label = "B03"
    failures: list[str] = []
    for path in (B03_TOOL, B03_REPORT, B03_METRICS, ROOT / "tests" / "test_baselines_source.py"):
        if not path.exists():
            failures.append(f"{label}: arquivo ausente '{path.relative_to(ROOT)}'")
    if failures:
        return failures, 0
    report = B03_REPORT.read_text(encoding="utf-8")
    flat = " ".join(report.split()).lower()
    for token in B03_TOKENS:
        if token.lower() not in flat:
            failures.append(f"{label}: relatório sem token '{token}'")
    leak = PUBLIC_ID_RE.search(report)
    if leak:
        failures.append(f"{label}: relatório com possível ID cru ('{leak.group(0)}')")
    source = B03_TOOL.read_text(encoding="utf-8")
    for token in ("male-cns", "data/sealed", "target_labels", "crosswalk"):  # firewall-allow
        if token in source:
            failures.append(f"{label}: baselines da fonte não podem referenciar o alvo ('{token}')")
    metrics = json.loads(B03_METRICS.read_text(encoding="utf-8"))
    results = metrics.get("results", {})
    majority = results.get("baselines", {}).get("majority", {})
    if abs(float(majority.get("simulated_accuracy", 0)) - float(majority.get("analytical_accuracy", -1))) > 1e-5:
        failures.append(f"{label}: maioria simulada difere da analítica")
    random_result = results.get("baselines", {}).get("stratified_random", {})
    if abs(float(random_result.get("simulated_draws_mean", 0)) - float(random_result.get("analytical_accuracy", -1))) > 0.01:
        failures.append(f"{label}: random simulado não concorda com a chance analítica")
    if list(random_result.get("seeds", [])) != [297979363399525401, 1699981902186354598, 3729859090210297070]:
        failures.append(f"{label}: seeds divergentes do pré-registro")
    degree = results.get("baselines", {}).get("degree_only", {}).get("recall", {}).get("@1", {})
    if not 0.0 <= float(degree.get("macro", -1)) <= 1.0:
        failures.append(f"{label}: macro do degree-only fora de [0,1]")
    if metrics.get("labels", {}).get("nodes_used", 0) < 1:
        failures.append(f"{label}: sem nodes usados")
    for entry in metrics.get("predictions", []):
        if not re.fullmatch(r"[0-9a-f]{64}", str(entry.get("sha256", ""))):
            failures.append(f"{label}: predição sem hash válido")
    plan_lines = PLAN.read_text(encoding="utf-8").splitlines()
    known = {item_id for _, item_id in parse_items(plan_lines)}
    for ref in sorted(ref for ref in phase_refs(report) if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(B03_TOKENS)


def check_b02_calibration() -> tuple[list[str], int]:
    label = "B02"
    failures: list[str] = []
    for path in (B02_TOOL, B02_REPORT, ROOT / "tests" / "test_calibration.py"):
        if not path.exists():
            failures.append(f"{label}: arquivo ausente '{path.relative_to(ROOT)}'")
    if failures:
        return failures, 0
    report = B02_REPORT.read_text(encoding="utf-8")
    flat = " ".join(report.split()).lower()
    for token in B02_TOKENS:
        if token.lower() not in flat:
            failures.append(f"{label}: relatório sem token '{token}'")
    leak = PUBLIC_ID_RE.search(report)
    if leak:
        failures.append(f"{label}: relatório com possível ID cru ('{leak.group(0)}')")
    source = B02_TOOL.read_text(encoding="utf-8")
    for token in ("open(", "read_text", "pathlib"):
        if token in source:
            failures.append(f"{label}: calibração não pode fazer I/O ('{token}')")
    spec = importlib.util.spec_from_file_location("calibration_module", B02_TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if module.brier_multiclass({"q": {"A": 1.0}}, {"q": "A"}) != 0.0:
        failures.append(f"{label}: Brier perfeito deveria ser 0")
    ece = module.expected_calibration_error([0.9, 0.9, 0.6], [True, True, False], bins=2)
    if abs(ece - 0.133333) > 1e-6:
        failures.append(f"{label}: ECE canônico divergente")
    if module.auroc([0.5, 0.5], [0.5, 0.5]) != 0.5:
        failures.append(f"{label}: AUROC degenerado deveria ser 0,5")
    first = module.bootstrap_ci_grouped({"A": [1, 1], "B": [0, 0]}, iterations=100, seed=3)
    second = module.bootstrap_ci_grouped({"A": [1, 1], "B": [0, 0]}, iterations=100, seed=3)
    if first != second or first["seed"] != 3:
        failures.append(f"{label}: bootstrap não determinístico ou sem seed registrada")
    fitted = module.fit_threshold_source([0.9, 0.6], [0.1], tpr=1.0)
    if fitted.get("fitted_on") != "source":
        failures.append(f"{label}: limiar deve ser ajustado somente na fonte")
    plan_lines = PLAN.read_text(encoding="utf-8").splitlines()
    known = {item_id for _, item_id in parse_items(plan_lines)}
    for ref in sorted(ref for ref in phase_refs(report) if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(B02_TOKENS)


def check_b01_metrics() -> tuple[list[str], int]:
    label = "B01"
    failures: list[str] = []
    for path in (B01_TOOL, B01_REPORT, ROOT / "tests" / "test_metrics.py"):
        if not path.exists():
            failures.append(f"{label}: arquivo ausente '{path.relative_to(ROOT)}'")
    if failures:
        return failures, 0
    report = B01_REPORT.read_text(encoding="utf-8")
    flat = " ".join(report.split()).lower()
    for token in B01_TOKENS:
        if token.lower() not in flat:
            failures.append(f"{label}: relatório sem token '{token}'")
    leak = PUBLIC_ID_RE.search(report)
    if leak:
        failures.append(f"{label}: relatório com possível ID cru ('{leak.group(0)}')")
    source = B01_TOOL.read_text(encoding="utf-8")
    for token in ("open(", "read_text", "pathlib", "json.load"):
        if token in source:
            failures.append(f"{label}: métricas não podem fazer I/O ('{token}')")
    spec = importlib.util.spec_from_file_location("metrics_module", B01_TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    ranked = {"q1": ["A", "B", "C"], "q2": ["A", "B", "C"], "q3": ["A", "B", "C"], "q4": ["B", "A", "C"]}
    gold = {"q1": "A", "q2": "B", "q3": "C", "q4": "A"}
    result = module.evaluate(ranked, gold)
    if abs(result["recall"]["@1"]["macro"] - 0.166667) > 1e-6:
        failures.append(f"{label}: exemplo canônico divergente em Recall@1 macro")
    if abs(result["mrr"] - 0.583333) > 1e-6 or abs(result["macro_f1"] - 0.133333) > 1e-6:
        failures.append(f"{label}: exemplo canônico divergente em MRR/macro-F1")
    plan_lines = PLAN.read_text(encoding="utf-8").splitlines()
    known = {item_id for _, item_id in parse_items(plan_lines)}
    for ref in sorted(ref for ref in phase_refs(report) if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(B01_TOKENS)


def check_gate_g4() -> tuple[list[str], int, str]:
    label = "G4-DADOS-ANALITICOS.md"
    if not GATE_G4.exists():
        return [f"{label}: arquivo ausente"], 0, "AUSENTE"
    text = GATE_G4.read_text(encoding="utf-8")
    lines = text.splitlines()
    failures: list[str] = []
    for section in GATE_G4_SECTIONS:
        if section not in text:
            failures.append(f"{label}: seção obrigatória ausente '{section}'")
    for field in GATE_HEADER_FIELDS:
        if field_value(lines, field) is None:
            failures.append(f"{label}: cabeçalho sem campo '{field}'")
    decision = field_value(lines, "Decisão")
    if decision is None or not decision.startswith(("AGUARDAR", "GO", "NO-GO", "REFORMULAR")):
        failures.append(f"{label}: decisão inválida")
    pending = decision is not None and decision.startswith("AGUARDAR")
    approved = decision is not None and decision.startswith("GO")
    entries = 0
    for line in lines:
        match = GATE_G4_HASH_RE.match(line)
        if match is None:
            continue
        digest, rel = match.groups()
        path = ROOT / rel
        if not path.exists():
            failures.append(f"{label}: artefato ausente '{rel}'")
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            failures.append(f"{label}: SHA-256 divergente para '{rel}'")
        entries += 1
    if entries < 8:
        failures.append(f"{label}: esperados ao menos 8 artefatos com hash (achados {entries})")
    manifest = json.loads((ROOT / "data" / "manifests" / "analitico-v1.json").read_text(encoding="utf-8"))
    if manifest.get("analytic_sha256") not in text:
        failures.append(f"{label}: hash analítico ausente no pacote")
    criteria = [line for line in lines if CRITERION_RE.match(line)]
    if len(criteria) < 8:
        failures.append(f"{label}: esperados ao menos 8 critérios (achados {len(criteria)})")
    if pending and not any("`NÃO VERIFICADO`" in line for line in criteria):
        failures.append(f"{label}: nenhum critério 'NÃO VERIFICADO' com decisão pendente")
    if approved and any("`NÃO VERIFICADO`" in line for line in criteria):
        failures.append(f"{label}: decisão GO com critério ainda 'NÃO VERIFICADO'")
    if approved and any("`FAIL`" in line for line in criteria):
        failures.append(f"{label}: critério FAIL exige decisão NO-GO/REFORMULAR")
    start = next((i for i, line in enumerate(lines) if line.startswith("## Assinaturas")), None)
    signature_lines = lines[start:] if start is not None else []
    for field in GATE_G4_SIGNATURE_FIELDS:
        value = field_value(signature_lines, field)
        if value is None:
            failures.append(f"{label}: assinatura sem campo '{field}'")
            continue
        if pending and "a preencher" not in value.lower():
            failures.append(f"{label}: assinatura '{field}' preenchida antes da revisão humana")
        if approved and "a preencher" in value.lower():
            failures.append(f"{label}: assinatura '{field}' ainda pendente com decisão GO")
    if approved and "2026-" not in "\n".join(signature_lines):
        failures.append(f"{label}: assinaturas sem data")
    leak = PUBLIC_ID_RE.search(text)
    if leak:
        failures.append(f"{label}: possível ID cru ('{leak.group(0)}')")
    plan_lines = PLAN.read_text(encoding="utf-8").splitlines()
    g4_line = next((line for line in plan_lines if "**G4 —" in line), None)
    if g4_line is None:
        failures.append(f"{label}: item G4 não encontrado no plano")
    elif pending and not g4_line.startswith("- [ ]"):
        failures.append(f"{label}: G4 marcado concluído enquanto a decisão é AGUARDAR")
    elif approved and g4_line.startswith("- [ ]"):
        failures.append(f"{label}: decisão GO exige G4 marcado [x] no plano")
    known = {item_id for _, item_id in parse_items(plan_lines)}
    for ref in sorted(ref for ref in phase_refs(text) if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    state = "GO" if approved else "AGUARDAR"
    return failures, entries, state


def check_h09_quality() -> tuple[list[str], int]:
    label = "H09"
    failures: list[str] = []
    for path in (H09_TOOL, H09_REPORT, H09_METRICS, H09_MANIFEST, ROOT / "tests" / "test_data_quality.py"):
        if not path.exists():
            failures.append(f"{label}: arquivo ausente '{path.relative_to(ROOT)}'")
    if failures:
        return failures, 0
    report = H09_REPORT.read_text(encoding="utf-8")
    flat = " ".join(report.split()).lower()
    for token in H09_TOKENS:
        if token.lower() not in flat:
            failures.append(f"{label}: relatório sem token '{token}'")
    leak = PUBLIC_ID_RE.search(report)
    if leak:
        failures.append(f"{label}: relatório com possível ID cru ('{leak.group(0)}')")
    metrics = json.loads(H09_METRICS.read_text(encoding="utf-8"))
    if metrics.get("mode") != "exploratory-only":
        failures.append(f"{label}: auditoria deve ser exploratória")
    for side in ("source", "target_public"):
        data = metrics.get(side, {})
        if data.get("duplicate_pairs") != 0:
            failures.append(f"{label}: duplicatas em '{side}'")
        if data.get("negative_weight_edges") != 0:
            failures.append(f"{label}: pesos negativos em '{side}'")
        if data.get("degree_mismatch_in") != 0 or data.get("degree_mismatch_out") != 0:
            failures.append(f"{label}: graus divergentes em '{side}'")
        if data.get("schema", {}).get("edges", {}).get("drift") or data.get("schema", {}).get("nodes", {}).get("drift"):
            failures.append(f"{label}: drift de schema em '{side}'")
    manifest = json.loads(H09_MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("status") != "exploratory-only" or manifest.get("labels_used") is not False:
        failures.append(f"{label}: manifesto analítico deve ser exploratório e sem rótulos")
    if "inconclusiv" not in str(manifest.get("confirmatory_outcome", "")).lower():
        failures.append(f"{label}: manifesto analítico sem desfecho inconclusivo")
    if not re.fullmatch(r"[0-9a-f]{64}", str(manifest.get("analytic_sha256", ""))):
        failures.append(f"{label}: hash analítico ausente")
    if metrics.get("analytic_manifest", {}).get("analytic_sha256") != manifest.get("analytic_sha256"):
        failures.append(f"{label}: hash analítico divergente entre relatório e manifesto")
    plan_lines = PLAN.read_text(encoding="utf-8").splitlines()
    h09_line = next((line for line in plan_lines if "**H09 —" in line), None)
    if h09_line is None or not h09_line.startswith("- [x]"):
        failures.append(f"{label}: H09 deve estar marcada [x] com evidência")
    known = {item_id for _, item_id in parse_items(plan_lines)}
    for ref in sorted(ref for ref in phase_refs(report) if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(H09_TOKENS)


def check_h08_snapshots() -> tuple[list[str], int]:
    label = "H08"
    failures: list[str] = []
    for path in (H08_TOOL, H08_REPORT, H08_METRICS, ROOT / "tests" / "test_snapshot_build.py"):
        if not path.exists():
            failures.append(f"{label}: arquivo ausente '{path.relative_to(ROOT)}'")
    if failures:
        return failures, 0
    report = H08_REPORT.read_text(encoding="utf-8")
    flat = " ".join(report.split()).lower()
    for token in H08_TOKENS:
        if token.lower() not in flat:
            failures.append(f"{label}: relatório sem token '{token}'")
    leak = PUBLIC_ID_RE.search(report)
    if leak:
        failures.append(f"{label}: relatório com possível ID cru ('{leak.group(0)}')")
    metrics = json.loads(H08_METRICS.read_text(encoding="utf-8"))
    source = metrics.get("source", {})
    target = metrics.get("target_neuron_level", {})
    if source.get("rows") != 5243574 or source.get("nodes") != 23188:
        failures.append(f"{label}: contagens da fonte divergem de H02")
    if source.get("weight_sum") != 30698527:
        failures.append(f"{label}: peso da fonte não conservado")
    if target.get("rows") != 26028386 or target.get("nodes") != 211577:
        failures.append(f"{label}: contagens do alvo nível-neurônio divergem do medido")
    if target.get("annotations_columns_used") != ["bodyId"] or target.get("no_labels") is not True:
        failures.append(f"{label}: alvo sem a garantia de 'somente bodyId, sem labels'")
    for key in ("source", "target_neuron_level", "target_segment_level"):
        peak = metrics.get(key, {}).get("peak_rss_mib")
        if not isinstance(peak, (int, float)) or peak >= 28 * 1024:
            failures.append(f"{label}: pico de RAM inválido ou acima de 28 GB em '{key}'")
        for field in ("snapshot_set_sha256", "input_sha256"):
            if not re.fullmatch(r"[0-9a-f]{64}", str(metrics[key].get(field, ""))):
                failures.append(f"{label}: hash ausente/inválido em '{key}.{field}'")
    plan_lines = PLAN.read_text(encoding="utf-8").splitlines()
    known = {item_id for _, item_id in parse_items(plan_lines)}
    for ref in sorted(ref for ref in phase_refs(report) if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(H08_TOKENS)


def check_h07_blocked() -> tuple[list[str], int]:
    label = "H07"
    failures: list[str] = []
    for path in (
        H07_TOOL,
        H07_PACKAGE,
        ROOT / "tests" / "test_sealed_labels.py",
        H07_DRAFT,
        H07_DRAFT_METRICS,
        ROOT / "tools" / "label_provenance_audit.py",
        ROOT / "tests" / "test_label_provenance_audit.py",
        H07_AUDIT_MD,
        H07_AUDIT_JSON,
        ROOT / "tools" / "hemilineage_crosswalk.py",
        ROOT / "tests" / "test_hemilineage_crosswalk.py",
        ROOT / "artifacts" / "reports" / "H07-HEMILINEAGE-AUDIT.md",
        H07_HEMI_METRICS,
        H07_HEMI_DRAFT,
        ROOT / "preregistration" / "PROTOCOL-v2-hemilineage.md",
    ):
        if not path.exists():
            failures.append(f"{label}: arquivo ausente '{path.relative_to(ROOT)}'")
    if failures:
        return failures, 0
    doc = H07_PACKAGE.read_text(encoding="utf-8")
    flat = " ".join(doc.split()).lower()
    for token in H07_TOKENS:
        if token.lower() not in flat:
            failures.append(f"{label}: H07-PACKAGE.md sem token '{token}'")
    leak = PUBLIC_ID_RE.search(doc)
    if leak:
        failures.append(f"{label}: H07-PACKAGE.md com possível ID cru ('{leak.group(0)}')")

    spec = importlib.util.spec_from_file_location("sealed_labels_module", H07_TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    audit = json.loads(H07_AUDIT_JSON.read_text(encoding="utf-8"))
    conclusion = audit.get("conclusion", {})
    if conclusion.get("non_circular_subset_for_t0_types") is not False:
        failures.append(f"{label}: auditoria deve registrar ausência de subconjunto não circular para T0")
    if "inconclusivo" not in str(conclusion.get("primary_benchmark", "")).lower():
        failures.append(f"{label}: benchmark primário deve ser registrado como inconclusivo por circularidade")
    if len(conclusion.get("reformulation_options", [])) < 3:
        failures.append(f"{label}: auditoria deve apresentar opções de reformulação")
    if audit.get("genetic_label_coverage", {}).get("classes_with_k_min", 0) < 1:
        failures.append(f"{label}: cobertura K=10 do rótulo genético ausente")
    audit_digest = hashlib.sha256(H07_AUDIT_JSON.read_bytes()).hexdigest()
    if not re.fullmatch(r"[0-9a-f]{64}", audit_digest):
        failures.append(f"{label}: hash da auditoria inválido")
    audit_report = H07_AUDIT_MD.read_text(encoding="utf-8")
    for token in ("inconclusivo por circularidade", "k=10", "fruDsx", "trumanHl", "nenhum ID"):
        if token.lower() not in " ".join(audit_report.split()).lower():
            failures.append(f"{label}: auditoria sem token '{token}'")
    leak = PUBLIC_ID_RE.search(audit_report)
    if leak:
        failures.append(f"{label}: auditoria com possível ID cru ('{leak.group(0)}')")
    hemi_metrics = json.loads(H07_HEMI_METRICS.read_text(encoding="utf-8"))
    hemi_draft = json.loads(H07_HEMI_DRAFT.read_text(encoding="utf-8"))
    if hemi_metrics.get("k_min") != 10 or hemi_metrics.get("classes_k_min_both", 0) < 1:
        failures.append(f"{label}: cobertura K=10 da hemilinhagem ausente ou inválida")
    if hemi_metrics.get("classes_k_min_both") != len(hemi_draft.get("mappings", [])) or hemi_metrics.get("classes_k_min_both", 0) < 30:
        failures.append(f"{label}: rascunho de hemilinhagem divergente das métricas")
    for label in ("20A.22A", "20B.21B.22B", "24B.25B", "26X", "27X"):
        if any(mapping["source_type"] == label for mapping in hemi_draft.get("mappings", [])):
            failures.append(f"{label}: rótulo incerto não pode constar do crosswalk")
    if hemi_metrics.get("shared_labels", 0) < hemi_metrics.get("classes_k_min_both", 0):
        failures.append(f"{label}: interseção de hemilinhagem inconsistente")
    if not (hemi_metrics.get("uncertain_labels") or hemi_metrics.get("excluded_uncertain_labels")):
        failures.append(f"{label}: rótulos incertos de hemilinhagem devem ser listados")
    hemi_report = (ROOT / "artifacts" / "reports" / "H07-HEMILINEAGE-AUDIT.md").read_text(encoding="utf-8")
    for token in ("pmc12636603", "transferência", "co-clustering", "k≥10", "exploratório", "inconclusivo", "trumanhl"):
        if token.lower() not in " ".join(hemi_report.split()).lower():
            failures.append(f"{label}: auditoria de hemilinhagem sem token '{token}'")
    changelog_text = (ROOT / "preregistration" / "CHANGELOG.md").read_text(encoding="utf-8")
    if "| 2.0-draft |" not in changelog_text:
        failures.append(f"{label}: changelog 2.0-draft ausente")
    draft = json.loads(H07_DRAFT.read_text(encoding="utf-8"))
    draft_failures = module.validate_crosswalk(draft, H07_DRAFT.name)
    for failure in draft_failures:
        failures.append(f"{label}: rascunho inválido: {failure}")
    if any(not mapping.get("provenance", {}).get("source_sha256") for mapping in draft.get("mappings", [])):
        failures.append(f"{label}: rascunho com mapeamento sem proveniência")
    if any(mapping.get("provenance", {}).get("support_neurons", 0) < 1 for mapping in draft.get("mappings", [])):
        failures.append(f"{label}: rascunho com mapeamento sem suporte de neurônios")
    draft_metrics = json.loads(H07_DRAFT_METRICS.read_text(encoding="utf-8"))
    draft_digest = hashlib.sha256(H07_DRAFT.read_bytes()).hexdigest()
    if draft_metrics.get("crosswalk_sha256") != draft_digest:
        failures.append(f"{label}: sha256 do rascunho diverge das métricas")
    changelog = (ROOT / "preregistration" / "CHANGELOG.md").read_text(encoding="utf-8")
    lowered = changelog.lower()
    if "| 1.1 |" not in changelog or not ("revisão única" in lowered or "revisor humano único" in lowered):
        failures.append(f"{label}: desvio de revisor único não registrado no changelog 1.1")
    for tool_path in (
        ROOT / "tools" / "topology_features.py",
        ROOT / "tools" / "adapter_manc.py",
        ROOT / "tools" / "adapter_mcns.py",
        ROOT / "tools" / "edge_transform.py",
        ROOT / "tools" / "run.py",
    ):
        text = tool_path.read_text(encoding="utf-8").lower()
        if "crosswalk-manc-mcns" in text or "labels.json" in text or "target-labels" in text:  # firewall-allow
            failures.append(
                f"{label}: {tool_path.name} referencia artefato avaliativo (proibido em features/tuning)"
            )
    mapping = {
        "source_type": "S1",
        "target_type": "T1",
        "kind": "one-to-one",
        "reviewer1": "A",
        "reviewer2": "B",
        "sources": ["LIT-0001"],
    }
    crosswalk = {"crosswalk_version": "check-1.0", "dataset_pair": ["F", "A"], "mappings": [mapping]}
    label_set, _ = module.build_label_set(crosswalk, {"b1": "T1"})
    if label_set["crosswalk"] != {"S1": "T1"}:
        failures.append(f"{label}: ferramenta não materializa o crosswalk esperado")
    try:
        module.build_label_set({**crosswalk, "mappings": [{**mapping, "reviewer2": "A"}]}, {"b1": "T1"})
    except module.SealedError:
        pass
    else:
        failures.append(f"{label}: ferramenta aceitou revisão única")

    plan_lines = PLAN.read_text(encoding="utf-8").splitlines()
    h07_line = next((line for line in plan_lines if "**H07 —" in line), None)
    if h07_line is None or not h07_line.startswith("- [x]"):
        failures.append(f"{label}: H07 deve estar encerrada [x] por decisão humana (condição 5)")
    else:
        index = plan_lines.index(h07_line)
        note = " ".join(" ".join(plan_lines[index:index + 40]).split()).lower()
        for token in ("inconclusiv", "circularidade", "sem materialização confirmatória"):
            if token not in note:
                failures.append(f"{label}: encerramento sem o token '{token}'")
    return failures, len(H07_TOKENS)


def check_edge_transform() -> tuple[list[str], int]:
    label = "H06"
    failures: list[str] = []
    for path in (
        EDGE_TOOL,
        EDGE_PRIMARY,
        EDGE_VARIANTS,
        EDGE_REPORT,
        EDGE_METRICS,
        ROOT / "tests" / "test_edge_transform.py",
    ):
        if not path.exists():
            failures.append(f"{label}: arquivo ausente '{path.relative_to(ROOT)}'")
    if failures:
        return failures, 0

    report = EDGE_REPORT.read_text(encoding="utf-8")
    flat = " ".join(report.split()).lower()
    for token in EDGE_TOKENS:
        if token.lower() not in flat:
            failures.append(f"{label}: relatório sem token '{token}'")
    leak = PUBLIC_ID_RE.search(report)
    if leak:
        failures.append(f"{label}: relatório com possível ID cru ('{leak.group(0)}')")

    spec = importlib.util.spec_from_file_location("edge_module", EDGE_TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    primary = json.loads(EDGE_PRIMARY.read_text(encoding="utf-8"))
    if module.validate_config(primary):
        failures.append(f"{label}: configuração primária inválida")
    if primary.get("direction") != "directed" or primary.get("weight") != "raw":
        failures.append(f"{label}: primária deve ser dirigida e com peso bruto")
    variants = json.loads(EDGE_VARIANTS.read_text(encoding="utf-8"))
    names = [item["variant"] for item in variants.get("variants", [])]
    if len(names) < 8 or len(set(names)) != len(names):
        failures.append(f"{label}: variantes pré-registradas incompletas ou duplicadas")
    for item in variants.get("variants", []):
        if module.validate_config(item):
            failures.append(f"{label}: variante inválida '{item.get('variant')}'")
    metrics = json.loads(EDGE_METRICS.read_text(encoding="utf-8"))
    for variant in ("primary", "binary", "log1p", "symmetrized"):
        if variant not in metrics:
            failures.append(f"{label}: métricas ausentes para variante '{variant}'")
    primary_metrics = metrics.get("primary", {})
    for side in ("source_manc_100k", "target_mcns_100k"):
        side_metrics = primary_metrics.get(side, {})
        if side_metrics.get("weight_in") != side_metrics.get("weight_out"):
            failures.append(f"{label}: conservação primária falhou em '{side}'")
    symmetrized = metrics.get("symmetrized", {})
    for side in ("source_manc_100k", "target_mcns_100k"):
        if symmetrized.get(side, {}).get("weight_in") != symmetrized.get(side, {}).get("weight_out"):
            failures.append(f"{label}: conservação da simetrização falhou em '{side}'")

    plan_lines = PLAN.read_text(encoding="utf-8").splitlines()
    known = {item_id for _, item_id in parse_items(plan_lines)}
    for ref in sorted(ref for ref in phase_refs(report) if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(EDGE_TOKENS)


def check_topology_features() -> tuple[list[str], int]:
    label = "H05"
    failures: list[str] = []
    for path in (
        TOPOLOGY_TOOL,
        OPAQUE_TOOL,
        TOPOLOGY_REPORT,
        ROOT / "tests" / "test_topology_features.py",
    ):
        if not path.exists():
            failures.append(f"{label}: arquivo ausente '{path.relative_to(ROOT)}'")
    if failures:
        return failures, 0

    report = TOPOLOGY_REPORT.read_text(encoding="utf-8")
    flat = " ".join(report.split()).lower()
    for token in TOPOLOGY_TOKENS:
        if token.lower() not in flat:
            failures.append(f"{label}: relatório sem token '{token}'")
    leak = PUBLIC_ID_RE.search(report)
    if leak:
        failures.append(f"{label}: relatório com possível ID cru ('{leak.group(0)}')")

    spec = importlib.util.spec_from_file_location("topology_module", TOPOLOGY_TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    opaque_spec = importlib.util.spec_from_file_location("opaque_module", OPAQUE_TOOL)
    opaque_module = importlib.util.module_from_spec(opaque_spec)
    opaque_spec.loader.exec_module(opaque_module)

    def make_graph(edges):
        labels = sorted({label_value for edge in edges for label_value in edge[:2]})
        return {
            "schema_version": "1.0",
            "provenance": {
                "dataset": "CHECK",
                "release": "v1",
                "license": "CC0-1.0",
                "source_files": [{"path": "x.csv", "sha256": "0" * 64}],
                "adapter": {"name": "x", "version": "1", "config_sha256": "1" * 64},
                "created_at": "2026-09-14",
            },
            "graph": {
                "directed": True, "weighted": True, "weight_units": "synapse_count",
                "allow_self_loops": True, "aggregation": "sum",
                "threshold": {"weight_min": 0, "rule": "keep"},
            },
            "nodes": [
                {"id": opaque_module.opaque_node_id("CHECK", "v1", value), "attributes": {}, "missing": []}
                for value in labels
            ],
            "edges": [
                {
                    "source": opaque_module.opaque_node_id("CHECK", "v1", pre),
                    "target": opaque_module.opaque_node_id("CHECK", "v1", post),
                    "weight": weight,
                    "attributes": {},
                    "missing": [],
                }
                for pre, post, weight in edges
            ],
        }

    small = make_graph([("a", "b", 5), ("b", "a", 2), ("a", "a", 1)])
    ids, matrix = module.raw_features(small)
    if len(matrix[0]) != len(module.FEATURE_NAMES):
        failures.append(f"{label}: matriz com largura diferente das features")
    if any(isinstance(value, str) for row in matrix for value in row):
        failures.append(f"{label}: matriz contém valores não numéricos")
    stats = module.fit(small)
    _, _, report_data = module.transform(small, stats)
    if report_data["nonfinite_replaced"] != 0:
        failures.append(f"{label}: política de não finitos não é fixa")
    if any(abs(value) > module.CLIP_Z for row in module.transform(small, stats)[1] for value in row):
        failures.append(f"{label}: clipping não aplicado")
    if opaque_module.opaque_node_id("CHECK", "v1", "a") != opaque_module.opaque_node_id("CHECK", "v1", "a"):
        failures.append(f"{label}: mapeamento opaco não determinístico")

    plan_lines = PLAN.read_text(encoding="utf-8").splitlines()
    known = {item_id for _, item_id in parse_items(plan_lines)}
    for ref in sorted(ref for ref in phase_refs(report) if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(TOPOLOGY_TOKENS)


def check_sealed_evaluator() -> tuple[list[str], int]:
    label = "H04"
    failures: list[str] = []
    for path in (
        SEALED_EVALUATOR_TOOL,
        SEALED_EVALUATOR_REPORT,
        ROOT / "tests" / "test_sealed_evaluator.py",
    ):
        if not path.exists():
            failures.append(f"{label}: arquivo ausente '{path.relative_to(ROOT)}'")
    if failures:
        return failures, 0

    report = SEALED_EVALUATOR_REPORT.read_text(encoding="utf-8")
    flat = " ".join(report.split()).lower()
    for token in SEALED_EVALUATOR_TOKENS:
        if token.lower() not in flat:
            failures.append(f"{label}: relatório sem token '{token}'")
    leak = PUBLIC_ID_RE.search(report)
    if leak:
        failures.append(f"{label}: relatório com possível ID cru ('{leak.group(0)}')")

    source = SEALED_EVALUATOR_TOOL.read_text(encoding="utf-8")
    if "data/sealed" in source:  # firewall-allow
        failures.append(f"{label}: avaliador referencia caminho da zona selada real")
    spec = importlib.util.spec_from_file_location("sealed_evaluator_module", SEALED_EVALUATOR_TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for attribute in ("validate_label_set", "evaluate", "LABEL_STATUSES"):
        if not hasattr(module, attribute):
            failures.append(f"{label}: módulo sem '{attribute}'")
    if "known" not in module.LABEL_STATUSES or "unknown" not in module.LABEL_STATUSES:
        failures.append(f"{label}: status de label incompletos")

    plan_lines = PLAN.read_text(encoding="utf-8").splitlines()
    known = {item_id for _, item_id in parse_items(plan_lines)}
    for ref in sorted(ref for ref in phase_refs(report) if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(SEALED_EVALUATOR_TOKENS)


def check_adapter_target() -> tuple[list[str], int]:
    label = "H03"
    failures: list[str] = []
    for path in (
        TARGET_ADAPTER_TOOL,
        TARGET_ADAPTER_REPORT,
        TARGET_ADAPTER_METRICS,
        TARGET_ADAPTER_GOLDEN,
        ROOT / "tests" / "test_adapter_mcns.py",
    ):
        if not path.exists():
            failures.append(f"{label}: arquivo ausente '{path.relative_to(ROOT)}'")
    if failures:
        return failures, 0

    report = TARGET_ADAPTER_REPORT.read_text(encoding="utf-8")
    flat = " ".join(report.split()).lower()
    for token in TARGET_ADAPTER_TOKENS:
        if token.lower() not in flat:
            failures.append(f"{label}: relatório sem token '{token}'")
    leak = PUBLIC_ID_RE.search(report)
    if leak:
        failures.append(f"{label}: relatório com possível ID cru ('{leak.group(0)}')")

    source = TARGET_ADAPTER_TOOL.read_text(encoding="utf-8")
    for token in ("body-annotations", "flywireType", "hemibrainType", "annotations"):
        if token in source:
            failures.append(f"{label}: adapter menciona arquivo avaliativo ('{token}')")

    spec = importlib.util.spec_from_file_location("target_adapter_module", TARGET_ADAPTER_TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    golden = json.loads(TARGET_ADAPTER_GOLDEN.read_text(encoding="utf-8"))
    graph_spec = importlib.util.spec_from_file_location("graph_module", GRAPH_TOOL)
    graph_module = importlib.util.module_from_spec(graph_spec)
    graph_spec.loader.exec_module(graph_module)
    failures += [f"{label}: {f}" for f in graph_module.validate_graph(golden, TARGET_ADAPTER_GOLDEN.name)]
    if len(golden.get("nodes", [])) != 40:
        failures.append(f"{label}: amostra dourada fora do tamanho esperado (40 nodes)")
    if not 40 <= len(golden.get("edges", [])) <= 60:
        failures.append(f"{label}: amostra dourada com número de arestas inesperado")
    for node in golden.get("nodes", []):
        if set(node.get("attributes", {})) & set(module.FORBIDDEN_NODE_ATTRIBUTES):
            failures.append(f"{label}: atributo proibido no trilho A na amostra dourada")

    metrics = json.loads(TARGET_ADAPTER_METRICS.read_text(encoding="utf-8"))
    if metrics.get("sample_weight_conserved") is not True:
        failures.append(f"{label}: peso da amostra não conservado")
    if not isinstance(metrics.get("rows_full"), int) or metrics["rows_full"] < 100000000:
        failures.append(f"{label}: métricas sem contagem do arquivo completo")
    if metrics.get("self_loops_full", 0) < 1:
        failures.append(f"{label}: self-loops do arquivo completo não registrados")
    if tuple(metrics.get("columns", ())) != ("body_pre", "body_post", "weight"):
        failures.append(f"{label}: colunas lidas divergentes do esperado")
    manifest_path = ROOT / "data" / "manifests" / "mcns-v1.0.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entry = next(
            (item for item in manifest["files"] if item["path"].endswith("mcns_connectome_weights.feather")),
            None,
        )
        if entry is not None and metrics.get("input_sha256") != entry["sha256"]:
            failures.append(f"{label}: sha256 de entrada diverge do manifesto R03")
    digest = hashlib.sha256(TARGET_ADAPTER_GOLDEN.read_bytes()).hexdigest()
    if metrics.get("golden_sha256") != digest:
        failures.append(f"{label}: sha256 da amostra dourada diverge das métricas")

    plan_lines = PLAN.read_text(encoding="utf-8").splitlines()
    known = {item_id for _, item_id in parse_items(plan_lines)}
    for ref in sorted(ref for ref in phase_refs(report) if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(TARGET_ADAPTER_TOKENS)


def check_adapter_source() -> tuple[list[str], int]:
    label = "H02"
    failures: list[str] = []
    for path in (
        ADAPTER_TOOL,
        ADAPTER_REPORT,
        ADAPTER_METRICS,
        ADAPTER_GOLDEN,
        ROOT / "tests" / "test_adapter_manc.py",
    ):
        if not path.exists():
            failures.append(f"{label}: arquivo ausente '{path.relative_to(ROOT)}'")
    if failures:
        return failures, 0

    report = ADAPTER_REPORT.read_text(encoding="utf-8")
    flat = " ".join(report.split()).lower()
    for token in ADAPTER_TOKENS:
        if token.lower() not in flat:
            failures.append(f"{label}: relatório sem token '{token}'")
    leak = PUBLIC_ID_RE.search(report)
    if leak:
        failures.append(f"{label}: relatório com possível ID cru ('{leak.group(0)}')")

    spec = importlib.util.spec_from_file_location("adapter_module", ADAPTER_TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    golden = json.loads(ADAPTER_GOLDEN.read_text(encoding="utf-8"))
    graph_spec = importlib.util.spec_from_file_location("graph_module", GRAPH_TOOL)
    graph_module = importlib.util.module_from_spec(graph_spec)
    graph_spec.loader.exec_module(graph_module)
    failures += [f"{label}: {f}" for f in graph_module.validate_graph(golden, ADAPTER_GOLDEN.name)]
    if len(golden.get("nodes", [])) != 40 or len(golden.get("edges", [])) != 60:
        failures.append(f"{label}: amostra dourada fora do tamanho esperado (40 nodes/60 edges)")
    for node in golden.get("nodes", []):
        if set(node.get("attributes", {})) & set(module.FORBIDDEN_NODE_ATTRIBUTES):
            failures.append(f"{label}: atributo proibido no trilho A na amostra dourada")

    metrics = json.loads(ADAPTER_METRICS.read_text(encoding="utf-8"))
    if metrics.get("weight_conserved") is not True:
        failures.append(f"{label}: peso não conservado nas métricas")
    if not isinstance(metrics.get("rows_in"), int) or metrics["rows_in"] < 1:
        failures.append(f"{label}: métricas sem linhas de entrada")
    if not isinstance(metrics.get("nodes"), int) or metrics["nodes"] < 1:
        failures.append(f"{label}: métricas sem nodes")
    manifest_path = ROOT / "data" / "manifests" / "manc-v1.0.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entry = next(
            (item for item in manifest["files"] if item["path"].endswith("manc_traced_connections.csv")),
            None,
        )
        if entry is not None and metrics.get("input_sha256") != entry["sha256"]:
            failures.append(f"{label}: sha256 de entrada diverge do manifesto R03")
    digest = hashlib.sha256(ADAPTER_GOLDEN.read_bytes()).hexdigest()
    if metrics.get("golden_sha256") != digest:
        failures.append(f"{label}: sha256 da amostra dourada diverge das métricas")

    plan_lines = PLAN.read_text(encoding="utf-8").splitlines()
    known = {item_id for _, item_id in parse_items(plan_lines)}
    for ref in sorted(ref for ref in phase_refs(report) if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(ADAPTER_TOKENS)


def check_graph_contract() -> tuple[list[str], int]:
    label = "H01"
    failures: list[str] = []
    for path in (
        GRAPH_SCHEMA,
        GRAPH_CONTRACT_DOC,
        GRAPH_TOOL,
        GRAPH_FIXTURE,
        ROOT / "tests" / "test_graph_contract.py",
    ):
        if not path.exists():
            failures.append(f"{label}: arquivo ausente '{path.relative_to(ROOT)}'")
    if failures:
        return failures, 0

    doc = GRAPH_CONTRACT_DOC.read_text(encoding="utf-8")
    for section in GRAPH_SECTIONS:
        if section not in doc:
            failures.append(f"{label}: GRAPH-CONTRACT.md sem seção '{section}'")
    flat = " ".join(doc.split()).lower()
    for token in GRAPH_TOKENS:
        if token.lower() not in flat:
            failures.append(f"{label}: GRAPH-CONTRACT.md sem token '{token}'")
    leak = PUBLIC_ID_RE.search(doc)
    if leak:
        failures.append(f"{label}: GRAPH-CONTRACT.md com possível ID cru ('{leak.group(0)}')")

    schema = json.loads(GRAPH_SCHEMA.read_text(encoding="utf-8"))
    spec = importlib.util.spec_from_file_location("graph_contract_module", GRAPH_TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if tuple(schema.get("required", ())) != module.TOP_REQUIRED:
        failures.append(f"{label}: schema do grafo divergente do validador")
    fixture = json.loads(GRAPH_FIXTURE.read_text(encoding="utf-8"))
    failures += [f"{label}: {failure}" for failure in module.validate_graph(fixture, "graph-fixture.json")]
    _, preserved = module.roundtrip(GRAPH_FIXTURE)
    if not preserved:
        failures.append(f"{label}: round-trip da fixture não preserva os dados")

    edges = fixture.get("edges", [])
    pairs = [(edge.get("source"), edge.get("target")) for edge in edges]
    if len(pairs) == len(set(pairs)):
        failures.append(f"{label}: fixture sem multiedge para testar conservação")
    if not any(edge.get("source") == edge.get("target") for edge in edges):
        failures.append(f"{label}: fixture sem self-loop")
    if not any(edge.get("weight") == 0 for edge in edges):
        failures.append(f"{label}: fixture sem peso zero preservado")
    provenance = fixture.get("provenance", {})
    if not all(provenance.get(field) for field in module.PROVENANCE_REQUIRED):
        failures.append(f"{label}: fixture com proveniência incompleta")

    plan_lines = PLAN.read_text(encoding="utf-8").splitlines()
    known = {item_id for _, item_id in parse_items(plan_lines)}
    for ref in sorted(ref for ref in phase_refs(doc) if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    return failures, len(GRAPH_TOKENS)


def check_gate_g3() -> tuple[list[str], int, str]:
    label = "G3-PREREGISTRO.md"
    if not GATE_G3.exists():
        return [f"{label}: arquivo ausente"], 0, "AUSENTE"
    text = GATE_G3.read_text(encoding="utf-8")
    lines = text.splitlines()
    failures: list[str] = []
    for section in GATE_G3_SECTIONS:
        if section not in text:
            failures.append(f"{label}: seção obrigatória ausente '{section}'")
    for field in GATE_HEADER_FIELDS:
        if field_value(lines, field) is None:
            failures.append(f"{label}: cabeçalho sem campo '{field}'")
    decision = field_value(lines, "Decisão")
    if decision is None or not decision.startswith(("AGUARDAR", "GO", "NO-GO", "REFORMULAR")):
        failures.append(f"{label}: decisão inválida")
    pending = decision is not None and decision.startswith("AGUARDAR")
    approved = decision is not None and decision.startswith("GO")

    entries = 0
    for line in lines:
        match = GATE_G3_HASH_RE.match(line)
        if match is None:
            continue
        digest, rel = match.groups()
        path = ROOT / rel
        if not path.exists():
            failures.append(f"{label}: artefato ausente '{rel}'")
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            failures.append(f"{label}: SHA-256 divergente para '{rel}'")
        entries += 1
    if entries < 10:
        failures.append(f"{label}: esperados ao menos 10 artefatos com hash (achados {entries})")

    registry_path = ROOT / "preregistration" / "REGISTRY.md"
    if registry_path.exists():
        registry_lines = registry_path.read_text(encoding="utf-8").splitlines()
        frozen_lines = [line for line in registry_lines if PREREG_HASH_RE.match(line)]
        package_hash = hashlib.sha256("\n".join(frozen_lines).encode("utf-8")).hexdigest()
        if package_hash not in text:
            failures.append(f"{label}: hash do pacote do pré-registro ausente ou divergente")
    else:
        failures.append(f"{label}: REGISTRY.md ausente")
    if "dryrun-1.0-" not in text:
        failures.append(f"{label}: pacote sem referência ao dry run/tag do protocolo")

    criteria = [line for line in lines if CRITERION_RE.match(line)]
    if len(criteria) < 8:
        failures.append(f"{label}: esperados ao menos 8 critérios (achados {len(criteria)})")
    if pending and not any("`NÃO VERIFICADO`" in line for line in criteria):
        failures.append(f"{label}: nenhum critério 'NÃO VERIFICADO' com decisão pendente")
    if approved and any("`NÃO VERIFICADO`" in line for line in criteria):
        failures.append(f"{label}: decisão GO com critério ainda 'NÃO VERIFICADO'")
    if approved and any("`FAIL`" in line for line in criteria):
        failures.append(f"{label}: critério FAIL exige decisão NO-GO/REFORMULAR")

    start = next((i for i, line in enumerate(lines) if line.startswith("## Assinaturas")), None)
    signature_lines = lines[start:] if start is not None else []
    for field in GATE_G3_SIGNATURE_FIELDS:
        value = field_value(signature_lines, field)
        if value is None:
            failures.append(f"{label}: assinatura sem campo '{field}'")
            continue
        if pending and "a preencher" not in value.lower():
            failures.append(f"{label}: assinatura '{field}' preenchida antes da revisão humana")
        if approved and "a preencher" in value.lower():
            failures.append(f"{label}: assinatura '{field}' ainda pendente com decisão GO")
    if approved and "2026-" not in "\n".join(signature_lines):
        failures.append(f"{label}: assinaturas sem data")

    leak = PUBLIC_ID_RE.search(text)
    if leak:
        failures.append(f"{label}: possível ID cru ('{leak.group(0)}')")
    plan_lines = PLAN.read_text(encoding="utf-8").splitlines()
    g3_line = next((line for line in plan_lines if "**G3 —" in line), None)
    if g3_line is None:
        failures.append(f"{label}: item G3 não encontrado no plano")
    elif pending and not g3_line.startswith("- [ ]"):
        failures.append(f"{label}: G3 marcado concluído enquanto a decisão é AGUARDAR")
    elif approved and g3_line.startswith("- [ ]"):
        failures.append(f"{label}: decisão GO exige G3 marcado [x] no plano")
    known = {item_id for _, item_id in parse_items(plan_lines)}
    for ref in sorted(ref for ref in phase_refs(text) if ref not in known):
        failures.append(f"{label}: referência de fase inexistente '{ref}'")
    state = "GO" if approved else "AGUARDAR"
    return failures, entries, state


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
        if "status" in payload and "dataset" not in payload:
            continue  # manifesto de congelamento analítico (H09), schema próprio
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
    gate_g3_failures, gate_g3_entries, gate_g3_state = check_gate_g3()
    graph_contract_failures, graph_contract_tokens = check_graph_contract()
    adapter_source_failures, adapter_source_tokens = check_adapter_source()
    adapter_target_failures, adapter_target_tokens = check_adapter_target()
    sealed_evaluator_failures, sealed_evaluator_tokens = check_sealed_evaluator()
    topology_failures, topology_tokens = check_topology_features()
    edge_transform_failures, edge_transform_tokens = check_edge_transform()
    h07_failures, h07_tokens = check_h07_blocked()
    h08_failures, h08_tokens = check_h08_snapshots()
    h09_failures, h09_tokens = check_h09_quality()
    gate_g4_failures, gate_g4_entries, gate_g4_state = check_gate_g4()
    b01_failures, b01_tokens = check_b01_metrics()
    b02_failures, b02_tokens = check_b02_calibration()
    b03_failures, b03_tokens = check_b03_source_baselines()
    b04_failures, b04_tokens = check_b04_artisanal()
    b05_failures, b05_tokens = check_b05_mlp()
    b06_failures, b06_tokens = check_b06_transductive()
    b07_failures, b07_tokens = check_b07_spectral()
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
        + gate_g3_failures
        + graph_contract_failures
        + adapter_source_failures
        + adapter_target_failures
        + sealed_evaluator_failures
        + topology_failures
        + edge_transform_failures
        + h07_failures
        + h08_failures
        + h09_failures
        + gate_g4_failures
        + b01_failures
        + b02_failures
        + b03_failures
        + b04_failures
        + b05_failures
        + b06_failures
        + b07_failures
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
    print(
        f"OK: gate G3 com {gate_g3_entries} hashes e decisão {gate_g3_state}"
    )
    print(
        f"OK: contrato de grafo H01 com {graph_contract_tokens} tokens, fixture "
        f"dirigida/ponderada e round-trip preservado"
    )
    print(
        f"OK: adapter H02 com {adapter_source_tokens} tokens, amostra dourada e "
        f"peso conservado"
    )
    print(
        f"OK: adapter público do alvo H03 com {adapter_target_tokens} tokens, "
        f"amostra sem labels e arquivo completo contado"
    )
    print(
        f"OK: avaliador selado H04 com {sealed_evaluator_tokens} tokens, label "
        f"schema validado e métricas sem IDs"
    )
    print(
        f"OK: features topology-only H05 com {topology_tokens} tokens, IDs opacos "
        f"e fit/transform separado"
    )
    print(
        f"OK: semântica de arestas H06 com {edge_transform_tokens} tokens, "
        f"primária conservada e variantes pré-registradas"
    )
    print(
        f"OK: H07 encerrada ({h07_tokens} tokens) — desfecho inconclusivo por "
        f"circularidade, sem materialização confirmatória"
    )
    print(
        f"OK: snapshots H08 com {h08_tokens} tokens, idempotência e picos abaixo "
        f"de 28 GB"
    )
    print(
        f"OK: auditoria H09 com {h09_tokens} tokens, dataset congelado em modo "
        f"exploratório e hash analítico"
    )
    print(
        f"OK: gate G4 com {gate_g4_entries} hashes e decisão {gate_g4_state}"
    )
    print(
        f"OK: métricas B01 com {b01_tokens} tokens, exemplo canônico conferido e "
        f"sem I/O"
    )
    print(
        f"OK: calibração B02 com {b02_tokens} tokens, fixtures conferidas e "
        f"limiar só na fonte"
    )
    print(
        f"OK: baselines da fonte B03 com {b03_tokens} tokens, chance analítica "
        f"concordando com a simulada"
    )
    print(
        f"OK: estatísticas artesanais B04 com {b04_tokens} tokens, ablação por "
        f"família e invariância a IDs"
    )
    print(
        f"OK: MLP de controle B05 com {b05_tokens} tokens, 3 budgets e "
        f"mesmas features de B04"
    )
    print(
        f"OK: transdutivos B06 com {b06_tokens} tokens, 2 configs e "
        f"veredito não comparável zero-shot"
    )
    print(
        f"OK: espectral B07 com {b07_tokens} tokens, 2 configs, ambiguidade de "
        f"sinal/rotação controlada e matriz esparsa"
    )
    print(f"OK: {refs} referências de fase resolvidas contra o plano")
    print(f"OK: {paths} caminhos de arquivo citados e existentes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
