# Registro de claims

Aberto em 2026-09-14 (C01). **Nenhum claim foi validado**; esta lista inicial
registra proposições que o projeto pretende testar, não resultados. Nenhum
dataset é declarado disponível: capacidades de dados permanecem `aberto` até as
auditorias D02–D07.

Regras:

- ID estável `CLM-nnn`. Claims não são removidos; mudam de status com evidência.
- Claim atômico e verificável; um claim por proposição.
- Tipo: `hipótese`, `capacidade de dado`, `literatura` ou `método`.
- Status permitido: `aberto`, `confirmado`, `ambíguo`, `conflitante`,
  `não encontrado` ou `refutado`.
- `confirmado` exige `Evidência` com artefato versionado, URL/DOI, versão e data
  de acesso. Sem isso, o claim permanece `aberto`.
- Toda afirmação factual externa segue o padrão mínimo de evidência de
  `docs/PROTOCOLO-EXECUCAO.md`; memória da IA não preenche lacuna.
- Responsável é um papel; a fase de resolução aponta para o plano.

## Hipóteses do projeto

- **CLM-001 — Transferência zero-shot supera o melhor baseline simples.**
  - Claim: em classes presentes na fonte e no alvo, o encoder indutivo treinado
    sem rótulos supera o melhor baseline simples pré-registrado em recuperação
    macro por tipo no alvo, no trilho topologia.
  - Tipo: hipótese.
  - Status: aberto.
  - Evidência: pendente; será produzida em M06–M08 e avaliada em G6.
  - Responsável: executor; revisão humana em G0/G6.
  - Fase de resolução: M08, G6.

- **CLM-002 — Atributos locais acrescentam sinal transferível.**
  - Claim: neurotransmissor, região, posição do soma ou neuropilos acrescentam
    sinal além da topologia, quando disponíveis e harmonizáveis.
  - Tipo: hipótese.
  - Status: aberto.
  - Evidência: pendente; ablações pré-registradas em S03.
  - Responsável: executor; revisão humana em G7.
  - Fase de resolução: S03.

- **CLM-003 — Morfologia acrescenta sinal quando comparável.**
  - Claim: morfologia acrescenta sinal além da conectividade quando skeletons,
    escalas, cobertura e pré-processamento são comparáveis.
  - Tipo: hipótese.
  - Status: aberto.
  - Evidência: pendente; decisão de abertura do trilho em S04.
  - Responsável: executor; revisão humana em S04.
  - Fase de resolução: S04.

- **CLM-004 — Multi-source melhora a fonte deixada de fora.**
  - Claim: treinar em mais de uma fonte melhora a generalização para uma fonte
    deixada de fora, sem adaptação supervisionada ao alvo.
  - Tipo: hipótese.
  - Status: aberto.
  - Evidência: pendente; requer datasets extras aprovados em G2.
  - Responsável: executor; revisão humana em G7.
  - Fase de resolução: S10.

- **CLM-005 — O ganho satura em modelo pequeno.**
  - Claim: o ganho de transferência, se existir, satura na faixa de 0,5–5M de
    parâmetros; aumentar parâmetros além do necessário não é contribuição.
  - Tipo: hipótese.
  - Status: aberto.
  - Evidência: pendente; curva de escala pré-registrada em S05.
  - Responsável: executor; revisão humana em G7.
  - Fase de resolução: S05.

- **CLM-006 — Distância no embedding sustenta open-set calibrado.**
  - Claim: distância no embedding permite rejeição open-set razoavelmente
    calibrada para tipos ausentes da fonte.
  - Tipo: hipótese.
  - Status: aberto.
  - Evidência: pendente; avaliação em S08 com métricas pré-registradas.
  - Responsável: executor; revisão humana em G7.
  - Fase de resolução: S08.

## Literatura

- **CLM-007 — Conectividade já recuperou tipos dentro de um connectoma.**
  - Claim: existe evidência publicada de que conectividade, isolada, recupera
    tipos neuronais acima de baselines triviais dentro de um connectoma.
  - Tipo: literatura.
  - Status: aberto.
  - Evidência: pendente; revisão sistemática em L04.
  - Responsável: executor; revisão humana em G1.
  - Fase de resolução: L04.

- **CLM-008 — Existe baseline publicado de neuron matching reproduzível.**
  - Claim: existe método publicado de neuron matching com input, licença e
    métrica documentados, reproduzível sob as restrições de hardware do projeto.
  - Tipo: literatura.
  - Status: aberto.
  - Evidência: pendente; L03 e reprodução em B08.
  - Responsável: executor; revisão humana em G1/G5.
  - Fase de resolução: B08.

## Capacidade de dados (não declara disponibilidade)

- **CLM-009 — FlyWire/FAFB possui release oficial auditável.**
  - Claim: existe release oficial do FlyWire/FAFB com grafo, tipos documentados,
    proveniência de anotação, licença utilizável e acesso programático
    reproduzível.
  - Tipo: capacidade de dado.
  - Status: aberto.
  - Evidência: pendente; auditoria D02 em fonte oficial.
  - Responsável: executor; revisão humana em G2.
  - Fase de resolução: D02.

- **CLM-010 — hemibrain possui release oficial auditável.**
  - Claim: existe release oficial do hemibrain com grafo, tipos documentados,
    proveniência de anotação, licença utilizável e acesso programático
    reproduzível.
  - Tipo: capacidade de dado.
  - Status: aberto.
  - Evidência: pendente; auditoria D03 em fonte oficial.
  - Responsável: executor; revisão humana em G2.
  - Fase de resolução: D03.

- **CLM-011 — BANC possui release oficial auditável.**
  - Claim: existe release oficial do BANC com grafo, tipos documentados,
    proveniência de anotação, licença utilizável e acesso programático
    reproduzível.
  - Tipo: capacidade de dado.
  - Status: aberto.
  - Evidência: pendente; auditoria D04 em fonte oficial.
  - Responsável: executor; revisão humana em G2.
  - Fase de resolução: D04.

- **CLM-012 — MANC possui release oficial auditável.**
  - Claim: existe release oficial do MANC com grafo, tipos documentados,
    proveniência de anotação, licença utilizável e acesso programático
    reproduzível.
  - Tipo: capacidade de dado.
  - Status: aberto.
  - Evidência: pendente; auditoria D05 em fonte oficial.
  - Responsável: executor; revisão humana em G2.
  - Fase de resolução: D05.

- **CLM-013 — MAOL possui release oficial auditável.**
  - Claim: existe release oficial do MAOL com grafo, tipos documentados,
    proveniência de anotação, licença utilizável e acesso programático
    reproduzível.
  - Tipo: capacidade de dado.
  - Status: aberto.
  - Evidência: pendente; auditoria D06 em fonte oficial.
  - Responsável: executor; revisão humana em G2.
  - Fase de resolução: D06.

- **CLM-014 — MCNS possui release oficial auditável.**
  - Claim: existe release oficial do MCNS com grafo, tipos documentados,
    proveniência de anotação, licença utilizável e acesso programático
    reproduzível.
  - Tipo: capacidade de dado.
  - Status: aberto.
  - Evidência: pendente; auditoria D07 em fonte oficial.
  - Responsável: executor; revisão humana em G2.
  - Fase de resolução: D07.

- **CLM-015 — Os rótulos do alvo não tornam a avaliação circular.**
  - Claim: para o par escolhido, a anotação de tipo do alvo não foi produzida
    exclusivamente a partir das features usadas pelo modelo, de modo que a
    avaliação mede transferência e não reconstrução da anotação.
  - Tipo: capacidade de dado.
  - Status: aberto.
  - Evidência: pendente; auditoria de proveniência em D08/L04 e revisão humana.
  - Responsável: revisor humano; executor prepara evidências.
  - Fase de resolução: D08, L04.
