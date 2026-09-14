# Escada de claims e saídas negativas (provisório)

Aberto em 2026-09-14 (C06). Documento **provisório**: define qual linguagem de
claim cada nível de evidência autoriza antes de qualquer resultado. Nenhum nível
está liberado. Esta escada não promete paper, novidade nem causalidade.
Consistente com `docs/research/CLAIMS.md`, `PERGUNTA-E-ESTIMANDO.md` (C02),
`EQUIVALENCIA.md` (C03), `DESFECHOS-E-FALSIFICACAO.md` (C04) e
`AMEACAS-A-VALIDADE.md` (C05). Revisão humana em G0.

## 1. Regras gerais

- Os níveis são cumulativos e ordenados: não se pula nível nem se usa linguagem
  de um nível sem a evidência mínima dele.
- Evidência de um nível não implica o seguinte; resultado misto fica no nível
  mais baixo sustentado.
- Cada nível exige protocolo congelado e avaliação selada; números só entram na
  redação a partir dos arquivos de métricas congelados.
- Seeds não são indivíduos biológicos; neurônios do mesmo grafo também não são.
- Nenhum nível pode ser liberado sem artefato de evidência congelado; a IA não
  promove nível sozinha.

## 2. Níveis de evidência e linguagem

### NIV-01 — Sinal topológico
- Alegação permitida: há sinal preditivo de topologia dentro da fonte, sob os
  controles pré-registrados, sem afirmar transferência.
- Evidência mínima: supera baselines triviais dentro da fonte em validação
  congruente e sobrevive ao controle pareado por grau; empate com degree-only
  rebaixa a linguagem (C04).
- Fase de decisão: M05, M06 e G6.
- Não autoriza: transferência entre datasets, cross-individual, multi-connectome
  ou novidade.
- Claims relacionados: —
- Status: bloqueado

### NIV-02 — Transferência entre dois datasets observados
- Alegação permitida: no par observado, sob protocolo congelado, o encoder
  zero-shot transferiu para o alvo (estado `sucesso` de C04).
- Evidência mínima: pacote congelado (M06) e avaliação selada (M08) com Δ ≥ SESOI,
  IC 95% excluindo zero e ganho preservado na análise balanceada por tipo e no
  degree-matched, com cobertura reportada.
- Fase de decisão: G6.
- Não autoriza: cross-individual, multi-connectome, novidade ou linguagem
  populacional além dos datasets observados.
- Claims relacionados: CLM-001
- Status: bloqueado

### NIV-03 — Cross-individual
- Alegação permitida: o efeito se repete entre indivíduos independentes.
- Evidência mínima: pelo menos dois espécimes independentes por papel, com
  congelamento e avaliação selada; seeds não são indivíduos biológicos.
- Condição verificável: cross-individual só com pelo menos dois espécimes
  independentes por papel; sem condição verificável o termo fica proibido (C02).
- Fase de decisão: fora do MVP (um fonte e um alvo); condicional ao Nível 3.
- Não autoriza: usar a expressão no MVP nem extrapolar para a população de
  moscas.
- Claims relacionados: —
- Status: bloqueado

### NIV-04 — Multi-connectome
- Alegação permitida: treinar em mais de uma fonte melhora a generalização para
  uma fonte deixada de fora, sem adaptação supervisionada ao alvo.
- Evidência mínima: datasets extras aprovados em G2 e execução congelada de S10
  com os controles de C04.
- Fase de decisão: S10 e G7.
- Não autoriza: generalização para a população de moscas, cross-individual
  automático ou novidade.
- Claims relacionados: CLM-004
- Status: bloqueado

### NIV-05 — Potencialmente novo
- Alegação permitida: a combinação pergunta, método e resultado é candidata a
  novidade provisória segundo buscas adversariais.
- Evidência mínima: L01–L07, veredito de G1 e rechecagem pós-resultado (S11 e
  P05); ausência em busca não prova novidade.
- Fase de decisão: G1, S11 e P05.
- Não autoriza: “primeiro”, “novo” como fato, paper prometido ou causalidade.
- Claims relacionados: —
- Status: bloqueado

## 3. Saídas negativas

- Resultado negativo publicável: se o estado for `refutado`, `parcial` ou
  `inconclusivo` (C04), publicar protocolo, controles, denominadores, cobertura e
  limitações; resultado nulo é resultado e não será rebatizado como sucesso.
- Benchmark inviável: se o gate de dados reprovar por licença, cobertura,
  circularidade ou incompatibilidade anatômica, publicar o relatório de
  inviabilidade e reformulação sem treinar.
- Esqueleto do relatório: `docs/research/RELATORIO-INVIABILIDADE-ESQUELETO.md`,
  preenchido apenas quando houver decisão.
- Nenhum resultado negativo autoriza linguagem de transferência, de nível 3 ou
  de novidade.

## 4. Proibições e limitações

- Esta escada não promete paper, novidade nem causalidade; também não promete
  que os níveis serão alcançados.
- Nenhuma métrica nova, subgrupo ou nível pode ser introduzido após o unseal
  para salvar uma claim.
- Linguagem de um nível exige o artefato congelado correspondente; sem artefato,
  a redação fica no nível anterior.
- Limitação: documento provisório, sem dados; validado apenas estruturalmente em
  `python3 tools/validate_research.py`.
