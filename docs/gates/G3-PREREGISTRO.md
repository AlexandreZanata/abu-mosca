# Decisão do gate G3 — pré-registro e firewall

Pacote preparado pela IA executora em 2026-09-14 11:27 -0400; **nenhum
critério científico foi aprovado pela IA**. A decisão `GO` foi tomada pela
revisão humana (científica, estatística e do custodiante) em 2026-09-14 12:10
-04; o executor apenas registrou o parecer. Este pacote consolida hashes,
testes e política pós-unseal; o executor não autoriza ingestão integral, treino,
unseal ou leitura de `data/sealed/`.

- Data/hora e fuso: preparação em 2026-09-14 11:27 -04 (commit `ecb3975`);
  decisão humana registrada em 2026-09-14 12:10 -04
- Commit e estado dirty: preparação sobre HEAD `f5f39e8`; decisão registrada no
  commit desta fase; modificações não relacionadas do workstream NEXT
  preservadas fora do commit
- Revisores: Alexandre Zanata (revisor humano) — acumula responsável
  científico, revisão de estatística e custódia; limitação declarada
- Decisão: GO (registrada pela revisão humana em 2026-09-14; executor apenas
  registrou o parecer)

## Pacote de revisão

- Pré-registro assinado: `preregistration/PROTOCOL.md` (15 seções) e
  `preregistration/REGISTRY.md` com 12 artefatos congelados e pacote
  `1ef26bcb80f516dbca40f4aea192c1dba330625a83d1ecac5f5498678d7459e8`.
- Estatística: `docs/research/STATISTICAL-ANALYSIS-PLAN.md` (R06) e schemas de
  predições e métricas.
- Firewall: `docs/research/FIREWALL.md` (R05), `tools/firewall.py` e testes
  antileakage de R05/R08.
- Dry run: `artifacts/reports/DRY-RUN-R08.md` e `DRY-RUN-R08.json`
  (tag `dryrun-1.0-f90a4927`).
- Perguntas a decidir: aprovar o pré-registro assinado? aprovar o firewall e o
  teste antileakage? confirmar a política pós-unseal e a designação do
  custodiante? autorizar a ingestão integral (H01–H09) sob o pré-registro?

## Artefatos e hashes

- SHA-256 `a248a357274e4498c235834dd5bff28814a0291de8d4a46761be542300ac92ab` — `preregistration/REGISTRY.md`
- SHA-256 `1f5a90ab1e49f2988a46294035c941e8a0c5a0335a000897aea891fcf9884a26` — `preregistration/PROTOCOL.md`
- SHA-256 `2ae11d2bbe7589280b4dbf82433dd64b8839819fef49b2e65dc5a2a6bbd15160` — `docs/research/STATISTICAL-ANALYSIS-PLAN.md`
- SHA-256 `8357d449c718a2ee2fb50b8fdda9eefcf664d4416dba19d31bec862e7c265cfb` — `docs/research/FIREWALL.md`
- SHA-256 `7287021f722ec63fb72eecc3ae99400f5010e6939f98bd021135196c0f2c1f1f` — `schemas/predictions.schema.json`
- SHA-256 `5a9f809b8a942de621f557b7eefd5441ce76572304e480ba5cbd32d135a4913e` — `schemas/metrics.schema.json`
- SHA-256 `45c8a022f989fc4613d419c1442718196bf84f955e8778dee5b7204a836a6b30` — `tools/firewall.py`
- SHA-256 `3bd775def84946e122710499386d552f17274574f2191d8fdf2c0b896c4119a9` — `tools/evaluator_contract.py`
- SHA-256 `e8da5447f2df74048604500dc93e21a5101711034aca28800182eb1b09f8fee7` — `tools/dry_run.py`
- SHA-256 `462757b9f9569c557d6e42ab59be3c146d8be45be7195ae7b068e8ca95715bf6` — `artifacts/reports/DRY-RUN-R08.json`

## Critérios

- Pré-registro assinado e íntegro: `PASS` — REGISTRY.md com três assinaturas (revisor único acumulando papéis, limitação declarada) e hash do pacote conferido pelo validador.
- Schemas de predições e métricas válidos: `PASS` — tools/evaluator_contract.py valida os dois pacotes e recusa rótulos e IDs crus.
- Firewall implementado e testado: `PASS` — scanner limpo, permissões 700 no selado, auditoria de abertura/listagem e filtro de log.
- Teste proposital de leakage falha como esperado: `PASS` — auditoria bloqueia abertura do selado sintético e predição com label é recusada (R08).
- Dry run ponta a ponta: `PASS` — download idempotente, treino trivial, freeze, inferência opaca e avaliação selada em fixture sintética.
- Suíte de testes: `PASS` — 75 testes automatizados passando na suíte completa.
- Política pós-unseal explícita: `PASS` — pré-registro e PROTOCOLO definem unseal único pelo custodiante e invalidação por reabertura de tuning.
- Aprovação científica, estatística e do custodiante: `PASS` — GO aprovado por Alexandre Zanata em 2026-09-14, acumulando os três papéis com limitação declarada.

## Riscos e divergências

- Revisor único acumulando os três papéis é limitação declarada; o
  ceticismo independente permanece ausente.
- Custodiante ainda não designado em separado; a avaliação real exige sessão
  separada do executor.
- A ingestão integral depende de armazenamento externo (D09/G2) e dos adapters
  H01–H03, ainda não implementados.
- Fixture do dry run é trivial e não sustenta nenhuma claim científica.

## Condições do G3

- Com `GO`: liberar H01–H09 conforme dependências, mantendo o pré-registro
  congelado; nenhum tuning no alvo e nenhuma análise real com critério
  `não verificado`.
- Designar o custodiante e registrar a política de unseal antes de M08.
- Resolver armazenamento externo antes do bulk do MCNS (H08).
- Qualquer edição nos artefatos congelados invalida este pacote e exige novo G3.
- Decisão registrada: `GO` aprovando o pré-registro assinado, o firewall e a
  política pós-unseal, com a limitação de revisor único acumulando científico,
  estatística e custódia; designar custodiante independente antes de M08
  permanece obrigatório no fluxo.

## Escopo liberado

- Próximas microfases autorizadas com `GO`: H01 e seguintes na ordem do plano,
  conforme dependências.
- Trilhos não autorizados por este gate: unseal, leitura de `data/sealed/`,
  treino confirmatório e publicação.
- Orçamento aprovado: IA baixa por microfase; sem GPU nesta etapa.

## Emenda 3.0 — grid de parâmetros (revisão do G3 em 2026-09-15)

Decisão humana (opção (a) da nota de bloqueio da M02, Alexandre Zanata,
2026-09-15): o grid congelado do R07 §5 (dim 64/128; 2–3 camadas; 13.824–101.760
parâmetros) foi emendado para o intervalo de 1–3M do MVP — coluna Dim passa a
**576** (trials de 2 camadas; 1.009.152 parâmetros) e **408** (trials de 3
camadas; 1.009.800 parâmetros), com Camadas, Fanout, LR, Batch, Dropout e o
budget de 12 trials inalterados. Nenhum dado, desfecho, métrica, SESOI, seed,
exclusão ou análise foi alterado. O pré-registro segue válido com os novos
hashes: PROTOCOL.md `1f5a90ab1e49f2988a46294035c941e8a0c5a0335a000897aea891fcf9884a26`, REGISTRY.md `a248a357274e4498c235834dd5bff28814a0291de8d4a46761be542300ac92ab`, pacote
`1ef26bcb80f516dbca40f4aea192c1dba330625a83d1ecac5f5498678d7459e8` (changelog 3.0). Assinaturas originais preservadas e emenda
registrada na seção de assinaturas do REGISTRY.

## Assinaturas

- Responsável científico: Alexandre Zanata — GO registrado em 2026-09-14
- Revisor de estatística: Alexandre Zanata — GO registrado em 2026-09-14
  (mesmo revisor acumulando papéis; limitação declarada)
- Custodiante designado: Alexandre Zanata — designado em 2026-09-14
  (acumula a custódia; limitação declarada; custodiante independente segue
  recomendado antes de M08)
