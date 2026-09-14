# Decisão do gate G3 — pré-registro e firewall

Pacote preparado pela IA executora em 2026-09-14 11:27 -0400; **nenhum
critério científico foi aprovado pela IA**. A decisão `GO`, `NO-GO` ou
`REFORMULAR` pertence aos revisores humano científico, estatístico e
custodiante. Este pacote apenas consolida hashes, testes e política pós-unseal;
o executor não autoriza ingestão integral, treino, unseal ou leitura de
`data/sealed/`.

- Data/hora e fuso: 2026-09-14 11:27 -0400
- Commit e estado dirty: preparação sobre HEAD `f5f39e8`; modificações não
  relacionadas do workstream NEXT preservadas fora do commit
- Revisores: a preencher (científico, estatístico e custodiante)
- Decisão: AGUARDAR (pacote preparado; nenhuma decisão tomada pela IA)

## Pacote de revisão

- Pré-registro assinado: `preregistration/PROTOCOL.md` (15 seções) e
  `preregistration/REGISTRY.md` com 12 artefatos congelados e pacote
  `9411af0ca15501b253934f5e2134d978a95526dcf2c4cb7923a677a685f658b1`.
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

- SHA-256 `c649a5a5763ac93de3e0ab83bcc32efd31ac5e5990d78cb12f58317e922253f7` — `preregistration/REGISTRY.md`
- SHA-256 `fb54cafb92be40085b296417393e72276b99640c785acc99e9dc18253725ee6a` — `preregistration/PROTOCOL.md`
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
- Aprovação científica, estatística e do custodiante: `NÃO VERIFICADO` — assinaturas humanas pendentes neste gate.

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

## Escopo liberado

- Próximas microfases autorizadas com `GO`: H01 e seguintes na ordem do plano,
  conforme dependências.
- Trilhos não autorizados por este gate: unseal, leitura de `data/sealed/`,
  treino confirmatório e publicação.
- Orçamento aprovado: IA baixa por microfase; sem GPU nesta etapa.

## Assinaturas

- Responsável científico: a preencher
- Revisor de estatística: a preencher
- Custodiante designado: a preencher
