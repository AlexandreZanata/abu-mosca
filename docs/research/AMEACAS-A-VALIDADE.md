# Ameaças à validade e leakage (provisório)

Aberto em 2026-09-14 (C05). Documento **provisório** de modelagem de ameaças,
derivado de `docs/research/RISCOS.md` (C01), do estimando (C02), da equivalência
aprovada (C03) e dos desfechos (C04). Nenhum risco é declarado mitigado: sem
teste ou artefato verificável, a classificação permanece aberta. Nenhum dado
externo foi consultado e nenhum dataset é declarado disponível.

## 1. Estado e escopo

- Cada ameaça recebe ID estável `AMA-nn`, tema, severidade provisória, cenário,
  teste de detecção planejado, mitigação planejada e risco residual.
- Severidade provisória é julgada pelo impacto no desfecho primário
  (Macro Recall@1 no alvo), não por conveniência.
- Mitigação planejada não é mitigação obtida; o risco residual fica
  `não verificado` até existir teste ou artefato.
- Ameaças que impedem o teste viram estado `inconclusivo` (C04), nunca sucesso.

## 2. Método de classificação

- **Severidade provisória alta:** pode fabricar um falso positivo no desfecho
  primário (atalho, circularidade ou vazamento direto).
- **Severidade provisória média:** pode inflar o desempenho, encolher cobertura
  ou tornar a conclusão frágil sem necessariamente criar falso positivo.
- **Severidade provisória baixa:** afeta interpretação secundária ou limita
  generalização declarada.
- Nenhum risco é classificado como mitigado sem teste ou artefato verificável
  (proibição C05). Campos `Artefato` só serão preenchidos quando existirem.
- Testes de detecção apontam a fase do plano que os produz.

## 3. Ameaças

### AMA-01 — IDs e ordem como atalho
- Tema: IDs/ordem
- Categoria: leakage
- Severidade provisória: alta
- Cenário: o encoder memoriza identidade ou ordem dos nodes e o probe reaproveita
  esses padrões, inflando a recuperação no alvo sem transferência.
- Teste de detecção planejado: permutar IDs/ordem, remover features de identidade
  e exigir invariância do desempenho (R05 e M01).
- Mitigação planejada: entradas sem node ID, embaralhamento e teste antileakage
  obrigatório antes do congelamento.
- Risco residual: não verificado
- Status: aberto
- Riscos relacionados: RSK-001

### AMA-02 — Confundimento por grau
- Tema: grau
- Categoria: estatístico
- Severidade provisória: alta
- Cenário: tipos diferem trivialmente em grau in/out; o encoder aprende grau e o
  ganho desaparece no controle pareado.
- Teste de detecção planejado: baseline degree-only e avaliação pareada por grau;
  Δ que não sobrevive leva a `refutado` (B03 e M09; C04).
- Mitigação planejada: negativos pareados por grau e degree-matched como controle
  confirmatório.
- Risco residual: não verificado
- Status: aberto
- Riscos relacionados: RSK-002

### AMA-03 — Coordenadas, regiões e posição
- Tema: coordenadas/regiões
- Categoria: leakage
- Severidade provisória: alta
- Cenário: posição do soma ou região codifica o tipo anotado e vaza para o
  trilho topologia.
- Teste de detecção planejado: auditoria de colunas por trilho e ablação com e
  sem posição/região (C05 e H05).
- Mitigação planejada: trilho A proíbe posição e região; trilho B separa
  modalidades com baseline próprio e auditoria de leakage.
- Risco residual: não verificado
- Status: aberto
- Riscos relacionados: RSK-003

### AMA-04 — Rótulos derivados de conectividade ou morfologia
- Tema: rótulos derivados de conectividade/morfologia
- Categoria: circularidade
- Severidade provisória: alta
- Cenário: o tipo foi anotado usando o mesmo sinal que o modelo recebe; o modelo
  reconstrói a anotação em vez de transferir.
- Teste de detecção planejado: auditoria de proveniência da anotação em L04 e D08
  (CLM-015), com registro de como cada ontologia foi produzida.
- Mitigação planejada: excluir ou rebaixar anotações circulares por decisão
  humana (C03 e D08); correspondência nunca entra como feature.
- Risco residual: não verificado
- Status: aberto
- Riscos relacionados: RSK-004

### AMA-05 — Crosswalk circular
- Tema: crosswalk circular
- Categoria: circularidade
- Severidade provisória: alta
- Cenário: a correspondência entre tipos foi construída com o mesmo sinal que o
  modelo avalia, e a métrica passa a medir o crosswalk.
- Teste de detecção planejado: rastrear proveniência e independência de cada
  correspondência (D08).
- Mitigação planejada: crosswalk versionado, selado, imutável e independente
  (DEC-EQ-09); nenhuma correspondência como feature.
- Risco residual: não verificado
- Status: aberto
- Riscos relacionados: RSK-005

### AMA-06 — Normalização ou estatística ajustada no alvo
- Tema: normalização no alvo
- Categoria: leakage
- Severidade provisória: alta
- Cenário: transformações aprendidas no alvo introduzem informação do alvo no
  trilho confirmatório.
- Teste de detecção planejado: auditoria de onde cada transformação é ajustada
  (R05 e H05).
- Mitigação planejada: ajustar apenas na fonte; adaptação não supervisionada só
  em análise pré-registrada separada; congelar em `artifacts/frozen/`.
- Risco residual: não verificado
- Status: aberto
- Riscos relacionados: RSK-006

### AMA-07 — Amostragem de negativos não pareada
- Tema: amostragem de negativos
- Categoria: método/estatístico
- Severidade provisória: média
- Cenário: negativos fáceis inflam a tarefa auto-supervisionada sem sinal
  transferível.
- Teste de detecção planejado: comparar tarefas com negativos pareados por grau
  ou distância (M01 e S01).
- Mitigação planejada: esquema de negativos pré-registrado e análise de
  sensibilidade ao esquema (S06).
- Risco residual: não verificado
- Status: aberto
- Riscos relacionados: RSK-007

### AMA-08 — Duplicação de neurônios entre releases
- Tema: duplicação de neurônios
- Categoria: leakage/dados
- Severidade provisória: alta
- Cenário: o mesmo neurônio aparece na fonte e no alvo por sobreposição de
  releases, quebrando a separação treino/alvo.
- Teste de detecção planejado: checar sobreposição de IDs/coordenadas e linhagem
  de releases (D08, H02 e H03).
- Mitigação planejada: proveniência por release e exclusão documentada antes do
  congelamento.
- Risco residual: não verificado
- Status: aberto
- Riscos relacionados: RSK-008

### AMA-09 — Sexo não comparável
- Tema: sexo
- Categoria: biológico/dados
- Severidade provisória: média
- Cenário: sexo difere entre fonte e alvo e a transferência fica confundida com
  diferença sexual.
- Teste de detecção planejado: inventário D01–D10 registra sexo por release;
  comparabilidade avaliada em D10.
- Mitigação planejada: escolher par comparável ou declarar estudo entre os
  datasets observados, com hipótese explícita quando não comparável.
- Risco residual: não verificado
- Status: aberto
- Riscos relacionados: RSK-009

### AMA-10 — Tecido ou região corporal não comparável
- Tema: tecido
- Categoria: biológico/dados
- Severidade provisória: média
- Cenário: fonte e alvo cobrem tecidos diferentes (por exemplo cérebro e cordão
  nervoso) e o modelo aprende a diferença anatômica.
- Teste de detecção planejado: inventário D01–D10 com tecido e cobertura por
  release.
- Mitigação planejada: comparabilidade anatômica decidida em G2; tecidos
  diferentes exigem hipótese explícita e não entram no mesmo benchmark por
  padrão.
- Risco residual: não verificado
- Status: aberto
- Riscos relacionados: RSK-009

### AMA-11 — Cobertura incompleta ou desigual
- Tema: cobertura
- Categoria: dados
- Severidade provisória: média
- Cenário: o alvo cobre apenas parte do volume da fonte; classes e regiões ficam
  desbalanceadas e a métrica macro fica instável.
- Teste de detecção planejado: medir cobertura por release e por classe (D01–D10
  e H09).
- Mitigação planejada: reportar denominadores e cobertura; classes excluídas
  documentadas; cobertura mínima K em R07.
- Risco residual: não verificado
- Status: aberto
- Riscos relacionados: RSK-009

### AMA-12 — Artefatos de reconstrução
- Tema: reconstrução
- Categoria: dados/método
- Severidade provisória: média
- Cenário: diferenças de reconstrução entre releases criam sinal espúrio que o
  encoder explora como se fosse biologia.
- Teste de detecção planejado: documentar pipeline de reconstrução e variantes;
  análise de sensibilidade com subamostras (C05 e H06).
- Mitigação planejada: registrar proveniência e versão das reconstruções;
  separar diagnóstico de comparabilidade em D08–D10.
- Risco residual: não verificado
- Status: aberto
- Riscos relacionados: RSK-010

### AMA-13 — Semântica de arestas e threshold
- Tema: threshold
- Categoria: dados/método
- Severidade provisória: média
- Cenário: o corte de sinapses difere entre fonte e alvo; a distribuição de
  arestas muda e o ganho reflete o threshold, não a biologia.
- Teste de detecção planejado: congelar semântica de arestas por trilho e rodar
  análise de sensibilidade a variantes (H06 e S06).
- Mitigação planejada: documentar thresholds por release, fixar variante
  principal antes do congelamento e reportar variantes como diagnóstico.
- Risco residual: não verificado
- Status: aberto
- Riscos relacionados: RSK-010

### AMA-14 — Tuning após o unseal
- Tema: tuning pós-unseal
- Categoria: protocolo/estatístico
- Severidade provisória: alta
- Cenário: decisões de arquitetura, limiar ou exclusão tomadas depois de ver
  métricas do alvo transformam a avaliação em validação.
- Teste de detecção planejado: trilha de auditoria de configuração e commits;
  checklist do avaliador em R06 e R08.
- Mitigação planejada: congelamento em `artifacts/frozen/`, avaliação em sessão
  separada e novo alvo intocado para qualquer alegação confirmatória.
- Risco residual: não verificado
- Status: aberto
- Riscos relacionados: RSK-011

## 4. Controles transversais

- Degree-matched control, permutação de rótulos, shuffle de IDs e bootstrap
  agrupado por tipo são exigidos pelo desfecho primário (C04).
- Firewall de quatro zonas e rótulos selados valem para todas as ameaças de
  leakage (`docs/PROTOCOLO-EXECUCAO.md`).
- Dependência estatística (RSK-012), baselines transdutivos (RSK-013), licença
  (RSK-014), hardware (RSK-015) e vazamento por metadados/nomes (RSK-016)
  permanecem no registro de riscos e não são renomeados como resolvidos aqui.

## 5. Mapa para o registro de riscos

- AMA-01→RSK-001; AMA-02→RSK-002; AMA-03→RSK-003; AMA-04→RSK-004;
  AMA-05→RSK-005; AMA-06→RSK-006; AMA-07→RSK-007; AMA-08→RSK-008;
  AMA-09, AMA-10 e AMA-11→RSK-009; AMA-12 e AMA-13→RSK-010; AMA-14→RSK-011.
- Nenhum risco ganha status `mitigado` nesta fase; o detalhamento apenas
  prepara os testes das fases R05, M01, M09, H05, H06, D08–D10 e R06–R08.

## 6. Limitações

- Documento provisório; severidades são julgamentos iniciais e serão revistas
  com dados reais (D01–D10).
- Não há código, dados ou artefatos nesta fase; nenhuma mitigação foi executada
  ou verificada.
- Validação apenas estrutural: `python3 tools/validate_research.py`.
