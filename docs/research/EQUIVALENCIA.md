# Equivalência e hierarquia avaliativa (pacote para revisão humana)

Preparado em 2026-09-14 (C03) para **decisão humana obrigatória**. Este pacote
propõe hierarquia de targets, classificação epistêmica das relações e regras de
crosswalk. Nada aqui está aprovado: todas as decisões da seção 7 permanecem
`AGUARDANDO DECISÃO HUMANA`. Nenhum dataset, ontologia ou crosswalk concreto é
avaliado; fatos externos só entram via L02–L04 e D08 com fonte primária.

Convenções: IDs `EQ-nn` para relações e `DEC-EQ-nn` para decisões; regras gerais
em `docs/PROTOCOLO-EXECUCAO.md` § Decisões que exigem revisão humana e termos em
`docs/research/GLOSSARIO.md`.

## 1. Alvo primário

Proposta: T0 = recuperação de **tipo harmonizado** (GLO-13), com galeria e
rótulos definidos no congelamento e métrica primária Macro Recall@1 (C02).
Justificativa: é o nível taxonômico que a evidência pode sustentar com crosswalk
versionado, sem presumir equivalência de outra natureza.

- Decisão associada: DEC-EQ-01.
- Status: AGUARDANDO DECISÃO HUMANA.

## 2. Hierarquia avaliativa

- T0 (primário): mesmo tipo harmonizado.
- T1 (secundário): supertype harmonizado.
- T2 (diagnóstico): mesma região anatômica — contexto, não classe.
- T3 (exploratório): homólogo entre espécimes ou estágios.
- T4 (fora de escopo): mesma função (GLO-07).

Os níveis não são substitutos: T1/T2/T3 não podem substituir T0 na decisão do
MVP (C04 e G6).

## 3. Relações e classificação epistêmica

Cada relação recebe uma classificação proposta que só vale após aprovação
humana. Igualdade nominal entre projetos não é equivalência confirmada.

### EQ-01 — Mesmo tipo
- Definição operacional: igualdade de rótulo após crosswalk versionado, selado e
  aprovado por humano; igualdade nominal sozinha não basta.
- Classificação proposta: gold label, condicionada à aprovação do crosswalk.
- Condição de validade: crosswalk rastreável, com proveniência documentada e
  independente do sinal avaliado.
- Decisão associada: DEC-EQ-02.
- Status: AGUARDANDO DECISÃO HUMANA.

### EQ-02 — Supertype
- Definição operacional: agrupamento mais amplo que tipo, na granularidade que a
  ontologia de cada release sustentar (GLO-05).
- Classificação proposta: proxy, usada apenas como desfecho secundário.
- Condição de validade: agrupamento harmonizável entre fonte e alvo.
- Decisão associada: DEC-EQ-03.
- Status: AGUARDANDO DECISÃO HUMANA.

### EQ-03 — Homólogo
- Definição operacional: correspondência de linhagem entre células ou tipos de
  espécimes diferentes (GLO-06); não observada neste estudo.
- Classificação proposta: hipótese, fora do MVP.
- Condição de validade: exigiria literatura primária e decisão humana; não é
  target primário nem secundário no MVP.
- Decisão associada: DEC-EQ-04.
- Status: AGUARDANDO DECISÃO HUMANA.

### EQ-04 — Mesma região
- Definição operacional: pertencer à mesma região anatômica anotada.
- Classificação proposta: proxy contextual para diagnóstico e estratificação,
  nunca classe de tipo.
- Condição de validade: entra apenas em análise de subgrupo; não conta como
  transferência de tipo.
- Decisão associada: DEC-EQ-05.
- Status: AGUARDANDO DECISÃO HUMANA.

### EQ-05 — Mesma função
- Definição operacional: propriedade fisiológica ou de circuito (GLO-07).
- Classificação proposta: fora do escopo.
- Condição de validade: não é medida nem desfecho; nenhum resultado será
  rotulado assim.
- Decisão associada: DEC-EQ-06.
- Status: AGUARDANDO DECISÃO HUMANA.

## 4. Cardinalidade e correspondências

- one-to-one: um tipo da fonte corresponde a um tipo do alvo; caso canônico do
  T0.
- multi-instance: divisões ou fusões de anotação (1-N e N-1); proposta:
  pontuar no nível harmonizado aprovado, registrar a ambiguidade e nunca
  escolher o mapa depois de observar score.
- unknown: tipo do alvo sem correspondente na galeria; tratado como open-set
  (GLO-14), contabilizado à parte e sujeito a métricas próprias (C04 e B02).
- Decisão associada: DEC-EQ-07.
- Status: AGUARDANDO DECISÃO HUMANA.

## 5. Regras para casos-limite

- tipos ausentes: ficam fora da galeria e aparecem como consultas open-set; a
  cobertura é sempre reportada.
- tipos ambíguos: rótulo com incerteza ou dupla anotação; proposta: excluir do T0
  e reportar denominador; alternativa multi-label exige decisão humana.
- singleton: tipo com uma única consulta; proposta: manter no macro com `n`
  reportado; exclusão só com regra pré-registrada.
- rótulos conflitantes: conflito não resolvido no crosswalk exclui o par do T0,
  com registro e escalonamento para revisão humana.
- Decisão associada: DEC-EQ-08.
- Status: AGUARDANDO DECISÃO HUMANA.

## 6. Regras de crosswalk

- Versionado e rastreável: cada correspondência carrega proveniência (release,
  anotação, data, autor) e o crosswalk tem versão e hash.
- Selado: mantido com o custodiante em `data/sealed/target-labels/`; o executor
  não o lê.
- Imutável após o congelamento; mudanças exigem novo registro e nova avaliação.
- O crosswalk nunca é usado como feature de entrada; correspondências apenas
  pontuam o output (proibição C03).
- Independência: correspondência derivada do mesmo sinal que o modelo avalia é
  rejeitada (circularidade, GLO-10 e RSK-005).
- Aprovação humana obrigatória antes de qualquer avaliação.
- Decisão associada: DEC-EQ-09.
- Status: AGUARDANDO DECISÃO HUMANA.

## 7. Decisões pendentes

Nenhuma decisão foi aprovada por IA. O revisor humano deve aceitar, rejeitar ou
reformular cada item; divergências ficam registradas em G0.

### DEC-EQ-01 — Nível do target primário
- Decisão: adotar tipo harmonizado (T0) como primário?
- Opções: (a) tipo harmonizado; (b) supertype; (c) ambos com hierarquia de poder.
- Recomendação: (a), mantendo T1 como secundário.
- Status: AGUARDANDO DECISÃO HUMANA.

### DEC-EQ-02 — Classificação de “mesmo tipo”
- Decisão: aceitar gold label condicionado a crosswalk aprovado?
- Opções: (a) gold label condicionado; (b) tratar sempre como proxy.
- Recomendação: (a).
- Status: AGUARDANDO DECISÃO HUMANA.

### DEC-EQ-03 — Papel do supertype
- Decisão: manter supertype como desfecho secundário?
- Opções: (a) secundário mediante harmonização; (b) descartar do MVP.
- Recomendação: (a).
- Status: AGUARDANDO DECISÃO HUMANA.

### DEC-EQ-04 — Homologia no MVP
- Decisão: manter homólogo apenas como hipótese fora do MVP?
- Opções: (a) fora do MVP; (b) target exploratório do Nível 2.
- Recomendação: (a).
- Status: AGUARDANDO DECISÃO HUMANA.

### DEC-EQ-05 — Uso de região
- Decisão: permitir região apenas como estratificação/diagnóstico?
- Opções: (a) apenas estratificação; (b) proibir completamente.
- Recomendação: (a), nunca como classe.
- Status: AGUARDANDO DECISÃO HUMANA.

### DEC-EQ-06 — Uso do termo de função
- Decisão: confirmar que não é medida nem desfecho?
- Opções: (a) fora do escopo; (b) reabrir em fase futura com dados próprios.
- Recomendação: (a), conforme GLO-07.
- Status: AGUARDANDO DECISÃO HUMANA.

### DEC-EQ-07 — Cardinalidade das correspondências
- Decisão: aceitar as regras de one-to-one, multi-instance e unknown?
- Opções: (a) aceitar como propostas; (b) restringir o T0 a one-to-one.
- Recomendação: (a), com open-set separado.
- Status: AGUARDANDO DECISÃO HUMANA.

### DEC-EQ-08 — Casos-limite
- Decisão: aceitar as regras para ausentes, ambíguos, singleton e conflitantes?
- Opções: (a) aceitar com cobertura reportada; (b) endurecer exclusões.
- Recomendação: (a).
- Status: AGUARDANDO DECISÃO HUMANA.

### DEC-EQ-09 — Requisitos do crosswalk
- Decisão: aceitar versionamento, selo, imutabilidade, independência e proibição
  de feature?
- Opções: (a) aceitar integralmente; (b) ajustar algum requisito.
- Recomendação: (a).
- Status: AGUARDANDO DECISÃO HUMANA.

## 8. Limites deste documento

- Não define crosswalk concreto, não nomeia datasets e não confirma nenhuma
  equivalência; isso depende de L02–L04 e D08 com fonte primária.
- Não substitui a aprovação humana exigida pelo orçamento C03; a fase permanece
  `[ ]` até a revisão.
- Não escolhe par fonte/alvo (G2) nem desfechos numéricos finais (C04 e R07).
- Rastreabilidade: `docs/research/GLOSSARIO.md` (GLO-05, GLO-06, GLO-07, GLO-10,
  GLO-13 e GLO-14), `docs/research/CLAIMS.md` (CLM-015),
  `docs/research/RISCOS.md` (RSK-004 e RSK-005) e
  `docs/research/PERGUNTA-E-ESTIMANDO.md`.
- Validação: `python3 tools/validate_research.py`.
