# Aprendizado auto-supervisionado e embeddings de grafo (revisão)

Aberto em 2026-09-14 (L05). Revisão das famílias de objetivos auto-supervisionados
e de embeddings aplicáveis ao trilho topologia, com hipótese de sinal, atalhos,
custo, suporte a grafo dirigido/ponderado e capacidade indutiva. Inclui
embeddings de connectomas e alegações de graph foundation models encontradas.
Fontes primárias no ledger; nenhum treino foi executado.

## 1. Estado e escopo

- Famílias recebem IDs `SSL-nn`; embeddings de connectoma, `CEM-nn`; alegações de
  graph foundation models, `GFM-nn`.
- Proibições registradas: nenhuma evidência revisada demonstra vantagem de
  Transformer, e o projeto não assume Transformer superior; a escolha seguirá
  custo e ganho (L06, M02 e M03). Espaços transdutivos independentes não são
  comparáveis sem alinhamento permitido; nenhuma comparação desse tipo será
  feita.
- O alvo é um objetivo que aprenda sem node ID e produza embedding indutivo,
  utilizável no alvo sem fine-tuning.

## 2. Famílias de objetivos

### SSL-01 — Masked edge/weight
- Referência: LIT-0042, LIT-0039.
- Hipótese de sinal: prever arestas ou pesos mascarados força o encoder a
  capturar regularidades locais de conectividade que generalizam sem node ID.
- Atalhos prováveis: grau e tipos dominantes resolvem a tarefa; negativos fáceis
  inflam a métrica; reconstruir estrutura pode apenas copiar proximidade trivial,
  o que o GraphMAE evita ao reconstruir features (LIT-0039).
- Custo: baixo a médio, com decoder de produto interno ou MLP sobre embeddings.
- Grafo dirigido/ponderado: VGAE cobre grafos não dirigidos e sem pesos
  (LIT-0042); direção e peso exigem decoder próprio (ver LIT-0044).
- Capacidade indutiva: baixa no VGAE; depende de encoder indutivo (LIT-0043).
- Status: documentado

### SSL-02 — Neighborhood reconstruction
- Referência: LIT-0040, LIT-0041.
- Hipótese de sinal: resumir a vizinhança (patch) contra o resumo global captura
  contexto estrutural para além do nó isolado (LIT-0040).
- Atalhos prováveis: grau e centralidade; vizinhanças amostradas podem dominar a
  tarefa.
- Custo: médio; exige encoder de agregação e amostragem de vizinhança.
- Grafo dirigido/ponderado: agregação precisa respeitar direção e peso.
- Capacidade indutiva: o DGI declara aplicabilidade transdutiva e indutiva
  (LIT-0040).
- Status: documentado

### SSL-03 — Contrastive
- Referência: LIT-0040, LIT-0041.
- Hipótese de sinal: invariança a augmentations que preservam a identidade
  biológica relevante aproxima views do mesmo neurônio e afasta negativos.
- Atalhos prováveis: augmentations heurísticas (nó, aresta, subgrafo) podem
  destruir sinal biológico ou criar atalhos; precisam de auditoria (C05, M01).
- Custo: alto; duas views, negativos e treino mais longo.
- Grafo dirigido/ponderado: depende do encoder; augmentations precisam preservar
  direção e peso.
- Capacidade indutiva: depende do encoder; GraphCL pré-treina GNNs (LIT-0041).
- Status: documentado

### SSL-04 — Autoencoders
- Referência: LIT-0039, LIT-0042.
- Hipótese de sinal: reconstrução robusta gera representações úteis; GraphMAE
  mostra que reconstruir features é mais eficaz que reconstruir estrutura.
- Atalhos prováveis: reconstrução trivial da estrutura, colapso de representação
  e dependência de features de atributos (indisponíveis no trilho somente
  topologia).
- Custo: médio; decoders adicionais.
- Grafo dirigido/ponderado: VGAE não cobre; GraphMAE é agnóstico à direção, mas
  requer features.
- Capacidade indutiva: encoder de GNN permite inferência em nós novos após o
  treino.
- Status: documentado

### SSL-05 — Link prediction
- Referência: LIT-0042, LIT-0044.
- Hipótese de sinal: prever arestas ausentes mede a regularidade da topologia e
  serve como objetivo de pré-treino.
- Atalhos prováveis: grau e proximidade; negativos aleatórios são fáceis; no
  projeto, link prediction no alvo é desfecho secundário e não substitui a
  avaliação de tipo (ESCOPO).
- Custo: baixo.
- Grafo dirigido/ponderado: VGAE não cobre (LIT-0042); MagNet lida com direção,
  mas não escala bem e não resolve pesos mistos (LIT-0044).
- Capacidade indutiva: exige encoder indutivo para o alvo.
- Status: documentado

## 3. Embeddings de connectomas

### CEM-01 — Connectome embedding (word2vec/node2vec)
- Referência: LIT-0045.
- Input: grafo estrutural de um conectoma humano de difusão, com nós = regiões
  cerebrais; embeddings por caminhadas aleatórias.
- Resultado relatado: melhora o mapeamento estrutura-função e revela conexões
  homotópicas ausentes da reconstrução original (LIT-0045).
- Limitação: nós são regiões cerebrais humanas, não neurônios de connectoma EM;
  embeddings são transdutivos e exigem alinhamento dedicado entre espaços.
- Status: documentado

## 4. Alegações de graph foundation models

### GFM-01 — Survey de conceitos
- Referência: LIT-0046.
- Alegação: GFMs são definidos e classificados em baseados em GNN, em LLM e
  híbridos; emergência e homogeneização seguem incertas e a contagem de
  parâmetros de GNNs é muito menor que a de LLMs.
- Risco/limitação: survey sem validação em connectomas; não autoriza modelo
  gigante nem justifica arquitetura por si só.
- Status: documentado

### GFM-02 — Survey de desafios
- Referência: LIT-0047.
- Alegação: os desafios centrais são heterogeneidade de features, de estrutura e
  de tarefas; o campo permanece com perguntas abertas em transferência.
- Risco/limitação: nenhuma evidência específica para grafos esparsos de
  conectoma.
- Status: documentado

### GFM-03 — Position paper
- Referência: LIT-0048.
- Alegação: defende que GFMs já existem sob a ótica de um graph vocabulary com
  invariâncias transferíveis, e não de uma arquitetura específica.
- Risco/limitação: posição/hipótese, sem resultados em connectomas; não promove
  Transformer a padrão.
- Status: documentado

## 5. Síntese e limitações

- Para o trilho somente topologia, o candidato natural é masked edge/weight com
  decoder baseado em embeddings e negativos pareados por grau e distância
  (origem: LIT-0042 e LIT-0039; execução em M01), sobre encoder indutivo
  (LIT-0043; M02 e M03).
- Contrastive fica condicionado a auditoria de augmentations (LIT-0040,
  LIT-0041); autoencoders de features não se aplicam sem atributos (LIT-0039).
- Custos, VRAM e tempo não foram medidos nesta fase; tetos ficam nos smoke e
  pilotos de M04.
- Nenhum trabalho revisado demonstra transferência zero-shot entre connectomas
  de Drosophila; as alegações de GFMs não substituem essa evidência.
- Validação: `python3 tools/validate_research.py`.
