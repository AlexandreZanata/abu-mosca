# Encoder GraphSAGE indutivo e emenda do grid (M02)

Executado em 2026-09-15, em modo **exploratório** (condições do G5), somente na
fonte e sem nenhum dado do alvo. O encoder está implementado, verificado e
liberado para o MVP após a emenda do grid de parâmetros autorizada pela decisão
humana (opção (a) da nota de bloqueio anterior).

## 1. Especificação implementada

| Item | Definição |
|---|---|
| Entrada | 6 features topology-only de H05 (`in_degree`, `out_degree`, `weighted_in`, `weighted_out`, `reciprocity`, `self_loop_weight`), z-score source-fit |
| Agregação | média ponderada pelos pesos das sinapses, **separada** para vizinhos de entrada e de saída (grafo dirigido) |
| Camadas | 3 projeções por camada (self, entrada, saída) + ReLU |
| Node ID | nenhuma tabela por node ID; nenhuma camada depende do número de nós da fonte (`per_node_parameters = 0`) |
| Neighbor sampling | expansão determinística por camada (fanout por camada, seed explícita), subgrafo esparso com arestas separadas por direção e sem duplicatas |
| Serialização | configuração + `state_dict` com recarga e saída idêntica |
| Convenção de fanout | o grid lista dois fanouts em trials de três camadas; o último valor é repetido nas camadas mais profundas |

## 2. Emenda do grid de parâmetros (bloqueio resolvido)

- **Bloqueio anterior:** o grid congelado do R07 §5 (dim 64/128; 2–3 camadas)
  rendia 13.824–101.760 parâmetros, abaixo do intervalo de **1–3M** declarado
  para o MVP (README, PROT §4, card E2).
- **Decisão humana (opção (a), Alexandre Zanata, 2026-09-15):** emendar o grid.
- **Diff (changelog 3.0):** coluna Dim passa a **576** (trials de 2 camadas,
  1.009.152 parâmetros) e **408** (trials de 3 camadas, 1.009.800 parâmetros);
  Camadas, Fanout, LR, Batch, Dropout e o budget de 12 trials inalterados.
- **Revisões:** G3 e G5 (condição 6) re-revisados na mesma decisão; hashes do
  pré-registro atualizados (`PROTOCOL.md` `1f5a90ab…`, pacote `1ef26bcb…`).
- **Estado:** grid vigente dentro do intervalo (**1.009.152–1.009.800**),
  `blocking_issue.present = false` e resolução registrada no JSON.

## 3. Verificações técnicas (itens de aceite)

- **Overfit controlado de tiny graph:** fixture de 40 nós e 110 arestas, 1.000
  passos na taxa do grid (1e-3) → AUC de treino **0,984117**, loss 2,040574 →
  0,058172, gradientes finitos.
- **Shapes e gradientes:** saída (n, dim) e todos os parâmetros com gradiente
  finito no smoke.
- **Determinismo:** mesma seed ⇒ embeddings idênticos (inicialização e treino).
- **Serialização:** recarga idêntica, diferença máxima 0,0.
- **Inferência em grafo novo:** encoder treinado na fixture de 20 nós aplicado a
  um grafo de 37 nós, com equivalência sob permutação de IDs (≤ 1e-4).
- **Sampling:** fanout respeitado por camada; com fanout completo a saída
  amostrada é igual à passagem completa (≤ 1e-5).
- **Sem densificação:** agregação sobre CSR; bytes esparsos / densos = 0,013706.

## 4. Diagnóstico de estabilidade (fixture)

Na fixture, taxa de aprendizado 5e-2 colapsa o decoder bilinear (embeddings → 0,
AUC 0,5), enquanto as taxas pré-registradas são estáveis: 3e-4 → AUC 0,955 e
1e-3 → AUC 0,988. Registro como evidência de estabilidade para M05; nenhuma
escolha foi feita olhando o alvo.

## 5. Recursos medidos

- Execução do relatório: 120,6 s, pico de 2,34 GB de RSS, CPU.
- Smoke no grafo completo (configuração de mecânica, dim 128; **não** é o modelo
  do grid): 20 passos, lotes de 64 nós, fanout (15, 10, 10), loss 4,774472 →
  0,981928; a expansão de 3 camadas cobre 22.933 nós e 293.687 arestas na última
  camada — M04 deve calibrar fanout neste grafo denso.
- Sonda CUDA (RTX 4060 Laptop, dim 576/2 camadas = 1.009.152 parâmetros, lote
  512): pico de **68,4 MiB de VRAM**, muito abaixo do teto de 6,5 GB.

## 6. Limitações

- O smoke treina apenas 20 passos com um objetivo de mecânica (pares existentes
  vs. não existentes no lote amostrado); o objetivo real de M01 será usado em M05.
- A explosão de vizinhança em 3 camadas exige calibração (M04).
- Resultados internos à fonte e exploratórios; nenhum claim de transferência.
