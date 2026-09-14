# Decisão do gate G1 — Viabilidade teórica e lacuna provisória

Pacote preparado pela IA executora; **nenhum critério científico foi aprovado
pela IA**. A decisão exige revisão humana científica.

- Data/hora e fuso: 2026-09-14 09:20 -04
- Commit e estado dirty: preparação em HEAD `b46402a`; snapshot do ledger em
  `docs/gates/G1-LEDGER-SNAPSHOT.tsv` com SHA-256
  `53bb627624a06ec53c09d05a4a4cb5244661bdb712023886b9983bd818f2b53d`
  (igual ao `research/literature/LEDGER.tsv` no momento do pacote); QUERY-LOG
  com SHA-256 `b2e792be9957a8b7c98167b0e3a67c8da8d0f32abf8c97fe9444d05f2adeb13b`;
  árvore com modificações não relacionadas do NEXT preservadas
- Revisores: A preencher pela revisão humana (nenhum assinado pela IA)
- Decisão: AGUARDAR (pacote preparado; aprovação pendente de revisão humana)

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
- Nível de novidade provisório: `NÃO VERIFICADO` — a IA avalia a contribuição
  como incremental em relação a NTAC e ao alinhamento BANC–MANC; o grau
  depende de julgamento humano.
- Hipótese reformulada quando necessário: `NÃO VERIFICADO` — nenhuma
  reformulação foi proposta pela IA; a decisão de manter ou reformular H0/H1
  é do revisor.
- Validação estrutural do pacote: `PASS` — `python3 tools/validate_research.py`
  e `python3 tools/validate_plan.py` sem falhas.
- Licenças e termos: `NÃO VERIFICADO` — licenças de código marcadas como não
  verificadas no ledger; a auditoria ocorre em D01–D07.
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

- Próximas microfases autorizadas: nenhuma enquanto a decisão for `AGUARDAR`.
  Com `GO`, a primeira autorizada é D01 (esquema de dataset card).
- Trilhos explicitamente não autorizados: qualquer download, treino, unseal,
  leitura de `data/sealed/` ou publicação de resultado.
- Orçamento aprovado: nenhum; a IA executora encerra após entregar o pacote.

## Assinaturas

- Responsável científico: A preencher pela revisão humana
- Custodiante do alvo, quando aplicável: A preencher pela revisão humana
- Revisor de literatura/novidade: A preencher pela revisão humana
