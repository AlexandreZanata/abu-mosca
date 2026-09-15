# Encoder GraphSAGE indutivo e bloqueio de orçamento (M02)

Executado em 2026-09-15, em modo **exploratório** (condições do G5), somente na
fonte e sem nenhum dado do alvo. O encoder está implementado e verificado, mas a
fase **permanece aberta** porque o grid congelado do pré-registro não alcança o
intervalo de 1–3M parâmetros declarado para o MVP; a decisão é humana (G5,
condição 6).

## 1. Especificação implementada

| Item | Definição |
|---|---|
| Entrada | 6 features topology-only de H05 (`in_degree`, `out_degree`, `weighted_in`, `weighted_out`, `reciprocity`, `self_loop_weight`), z-score source-fit |
| Agregação | média ponderada pelos pesos das sinapses, **separada** para vizinhos de entrada e de saída (grafo dirigido) |
| Camadas | 3 projeções por camada (self, entrada, saída) + ReLU; sem normalização por nó |
| Node ID | nenhuma tabela por node ID; nenhuma camada depende do número de nós da fonte (`per_node_parameters = 0`) |
| Neighbor sampling | expansão determinística por camada (fanout por camada, seed explícita), subgrafo esparso com arestas separadas por direção e sem duplicatas |
| Serialização | `torch.save` de configuração + `state_dict`, com recarga e saída idêntica |
| Convenção de fanout | o grid do R07 lista dois fanouts em trials de três camadas; o último valor é repetido nas camadas mais profundas (não altera a contagem de parâmetros) |

## 2. Bloqueio: orçamento de parâmetros do MVP

- Intervalo declarado para o MVP (Nível 1 / card E2): **1.000.000–3.000.000 parâmetros**.
- Grid congelado do R07 (12 trials, dim 64/128, 2–3 camadas): **13.824 a 101.760 parâmetros** — abaixo do intervalo.
- Menor configuração dentro do intervalo: **dim 576 / 2 camadas = 1.009.152** ou **dim 408 / 3 camadas = 1.009.800** (tabelas completas no JSON).
- Consequência: não é possível satisfazer “configuração padrão cabe no intervalo” usando apenas o espaço congelado; escolher dim fora do grid unilateralmente violaria o pré-registro (R07 §5/§13) e a condição 6 do G5.
- Opções registradas para decisão humana: (a) emendar o grid do pré-registro (changelog + nova revisão do G5) para incluir dim ≥ 408 (3 camadas) ou ≥ 576 (2 camadas); (b) aceitar encoder abaixo do intervalo e atualizar README/ESCOPO/PROT com o desvio; (c) outra decisão documentada.
- Decisor: revisor humano do G5. **A fase fica `[ ]` até a decisão.**

## 3. Verificações técnicas (itens de aceite)

- **Overfit controlado de tiny graph:** fixture de 40 nós, 110 arestas, 1.000 passos na taxa do grid (1e-3) → AUC de treino **0,984117**, loss 2,040574 → 0,058172, gradientes finitos.
- **Shapes e gradientes:** saída (n, dim) e todos os parâmetros com gradiente finito no smoke.
- **Determinismo:** mesma seed ⇒ embeddings idênticos (inicialização e treino).
- **Serialização:** recarga com `state_dict` idêntico e diferença máxima 0,0 na saída.
- **Inferência em grafo novo:** encoder treinado na fixture de 20 nós é aplicado a um grafo de 37 nós com saída finita; permutar IDs/ordem produz embeddings equivalentes (≤ 1e-4).
- **Sampling:** fanout respeitado por camada; com fanout completo a saída amostrada é igual à passagem completa (≤ 1e-5).
- **Sem densificação:** agregação sobre CSR; bytes esparsos / equivalentes densos = 0,013706 no grafo completo.

## 4. Diagnóstico de estabilidade (fixture)

Na fixture, taxa de aprendizado 5e-2 colapsa o decoder bilinear (embeddings → 0,
AUC 0,5), enquanto as taxas pré-registradas são estáveis: 3e-4 → AUC 0,955 e
1e-3 → AUC 0,988. Registro como evidência de estabilidade para M05; nenhuma
escolha foi feita olhando o alvo.

## 5. Recursos medidos

- Execução do relatório: 35,6 s, pico de 2,48 GB de RSS, CPU.
- Smoke no grafo completo: 20 passos, lotes de 64 nós, fanout (15, 10, 10),
  loss 4,774472 → 0,981928 em 19,9 s; a expansão de 3 camadas cobre 22.933 nós e
  293.687 arestas na última camada — sinal de que M04 precisa calibrar fanout
  neste grafo denso.
- Sonda CUDA (RTX 4060 Laptop, dim 576/2 camadas = 1.009.152 parâmetros,
  lote 512): pico de **68,4 MiB de VRAM**, muito abaixo do teto de 6,5 GB.

## 6. Limitações

- O modelo do MVP ainda não pode ser escolhido enquanto o orçamento estiver bloqueado.
- O smoke treina apenas 20 passos com um objetivo de mecânica (pares existentes
  vs. não existentes no lote amostrado); o objetivo real de M01 será usado em M05.
- A explosão de vizinhança em 3 camadas neste grafo denso exige calibração (M04).
- Resultados são internos à fonte e exploratórios; nenhum claim de transferência.
