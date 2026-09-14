# Decisão do gate G1 — Viabilidade teórica e lacuna provisória

Pacote preparado pela IA executora; **nenhum critério científico foi aprovado
pela IA**. A decisão foi tomada pela revisão humana; o executor apenas registrou
o parecer.

- Data/hora e fuso: 2026-09-14 09:20 -04 (preparação); GO registrado em
  2026-09-14 09:24 -04
- Commit e estado dirty: preparação em HEAD `b46402a`; snapshot do ledger em
  `docs/gates/G1-LEDGER-SNAPSHOT.tsv` com SHA-256
  `53bb627624a06ec53c09d05a4a4cb5244661bdb712023886b9983bd818f2b53d`
  (igual ao `research/literature/LEDGER.tsv` no momento do pacote); QUERY-LOG
  com SHA-256 `b2e792be9957a8b7c98167b0e3a67c8da8d0f32abf8c97fe9444d05f2adeb13b`;
  árvore com modificações não relacionadas do NEXT preservadas
- Revisores: Alexandre Zanata (revisor humano / responsável científico) — GO
  registrado em 2026-09-14
- Decisão: GO (aprovada pela revisão humana em 2026-09-14 com novidade
  incremental/provisória; executor apenas registrou a decisão)

## Pacote de revisão

- Protocolo e registros: `research/literature/PROTOCOL.md`,
  `docs/gates/G1-LEDGER-SNAPSHOT.tsv` e `research/literature/QUERY-LOG.tsv`.
- Sínteses: `research/literature/ALIGNMENT.md`, `CELL-TYPE.md`,
  `SSL-GRAFOS.md` e `METHODS.md`.
- Lacunas e contribuições: `research/literature/NOVIDADE.md`.
- Perguntas a decidir: a cobertura L01–L07 é suficiente? os trabalhos mais
  próximos (NTAC e alinhamento BANC–MANC) estão corretos? a hipótese precisa de
  reformulação? qual é o nível honesto de novidade? autorizar D01–D10?

## Critérios

- Cobertura do protocolo de busca: `PASS` — 47 consultas registradas cobrindo
  Q0–Q7 e as oito bases, com falhas registradas e descartadas.
- Ledger íntegro e versionado: `PASS` — 67 registros, seis candidatos com fonte
  incluída e snapshot com SHA-256 idêntico ao ledger.
- Trabalhos mais próximos identificados: `PASS` — NTAC
  (10.1038/s41467-025-68044-1), alinhamento BANC–MANC
  (bioRxiv 10.64898/2026.06.14.732053v2) e evidência conflitante de SSL
  (arXiv 2602.03217) registrados em `NOVIDADE.md`.
- Nível de novidade provisório: `PASS` — aprovado pela revisão humana em
  2026-09-14 como **incremental/provisório** em relação a NTAC e ao alinhamento
  BANC–MANC, sem inflar a claim.
- Hipótese reformulada quando necessário: `PASS` — decisão humana: **sem
  reformulação de H0/H1**; a conclusão permanece limitada aos datasets
  observados (C02 e C06).
- Validação estrutural do pacote: `PASS` — `python3 tools/validate_research.py`
  e `python3 tools/validate_plan.py` sem falhas.
- Licenças e termos: `PASS` — pendências declaradas no pacote; a auditoria
  permanece obrigatória em D01–D07 e o GO não a dispensa.
- Nenhum dado externo baixado ou unseal: `PASS` — apenas fontes públicas
  consultadas por leitura, nenhum download de dataset.

## Riscos e divergências

- Evidência conflitante: NTAC mostra que conectividade isolada tipa neurônios
  dentro de um dataset, reduzindo a originalidade da premissa; o alinhamento
  BANC–MANC mostra transferência de tipos por alinhamento transdutivo.
- SSL topológico: o caso de falha em benchmark neuro-inspirado (arXiv
  2602.03217) torna incerto o ganho do objetivo masked edge/weight; resultado
  negativo continua publicável (NIV-01).
- Limites da busca: seis consultas adversariais em Q4/Q5; literatura cinzenta
  pode não ter sido coberta; ausência em busca não prova novidade.
- Licenças pendentes: manutenção e licenças de repositórios originais marcadas
  como não verificadas.
- Proibição do gate: este gate não aprova paper; apenas autoriza a auditoria de
  dados, se aprovado.

## Condições do G1

- Com `GO`, liberar apenas D01–D10 conforme dependências; não liberar download,
  treino, unseal ou leitura de `data/sealed/`.
- O nível honesto de novidade deve ficar registrado pelo revisor, sem inflar a
  claim (por exemplo, “estudo entre datasets observados”).
- Qualquer reformulação de H0/H1 deve ser registrada neste gate e refletida em
  C02/C06 antes de G3.

## Escopo liberado

- Próximas microfases autorizadas: D01–D10 conforme dependências, a começar por
  D01 (esquema de dataset card).
- Trilhos explicitamente não autorizados pelo GO: qualquer download, treino,
  unseal, leitura de `data/sealed/` ou publicação de resultado.
- Orçamento aprovado: IA baixa por microfase; sem GPU; nenhum download ou
  serviço autorizado por este gate.

## Assinaturas

- Responsável científico: Alexandre Zanata — GO registrado em 2026-09-14
- Custodiante do alvo, quando aplicável: não designado; designação aplicável
  apenas antes do unseal (R05 e G3)
- Revisor de literatura/novidade: Alexandre Zanata — parecer registrado em
  2026-09-14 (novidade incremental, sem reformulação de H0/H1)
