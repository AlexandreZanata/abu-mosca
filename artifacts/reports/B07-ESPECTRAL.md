# Fatoração espectral esparsa dentro da fonte (B07)

Executado em 2026-09-15, somente na **fonte MANC**, em modo exploratório e sem
nenhum dado do alvo. `tools/spectral_baseline.py` compara a estrutura global
linear de baixo custo contra os demais baselines, com operadores esparsos
(`scipy.sparse.linalg`, ARPACK) e **sem densificar a matriz completa**:

- `svd_dirigido`: SVD truncada da adjacência dirigida e ponderada
  (A ≈ U·S·Vᵀ, k = 32); o embedding concatena `U·√S` e `V·√S` (64 dims), de
  modo que os papéis de origem e destino ficam separados e o peso entra
  diretamente na matriz; a direção é tratada pela SVD assimétrica.
- `ase_simetrizado`: decomposição própria da matriz simetrizada
  W = (A + Aᵀ)/2 (k = 32, 32 dims), com escala assinada `sign(λ)·√|λ|`.

Avaliação com o mesmo split, as mesmas 3 seeds, o mesmo probe por centroide
source-fit e o mesmo avaliador de B01/B03–B06. O veredito é **restrito ao
diagnóstico within-source (não comparável zero-shot)**: a base espectral é
específica do grafo e não há mecanismo de alinhamento não supervisionado
permitido e pré-registrado que autorize uso entre grafos.

## 1. Tratamento da ambiguidade de sinal e rotação

- **Sinal:** convenção canônica fixa (maior carga em módulo positiva, empate
  pelo menor índice) aplicada a cada vetor; a troca de sinal de colunas
  preserva as decisões do probe exatamente (concordância **1,0** nos dois
  métodos).
- **Rotação:** subespaço líder idêntico entre as 3 seeds (menor cosseno de
  ângulo principal **1,0** para todos os pares), logo o vetor inicial do
  ARPACK não altera a decomposição; as predições entre seeds concordam
  **1,0**. Com um probe diagnóstico equívariante (normalização L2 por linha),
  girar a base também preserva as decisões **1,0**.
- **Probe padrão:** o probe de comparação usa z-score por coluna ajustado no
  treino (o mesmo de B03–B06) e **não** é equívariante a rotações: girar a base
  muda a escala efetiva e produz sensibilidade medida de 0,8616 (`svd_dirigido`)
  e 0,8352 (`ase_simetrizado`). Essa sensibilidade é um diagnóstico, não uma
  autorização: a base canônica não deve ser girada e o método fica restrito ao
  diagnóstico within-source.
- **Alinhamento:** nenhum; matching com pares conhecidos é proibido
  (proibições da fase e de L03/L06).

## 2. Resultados (validação interna, mesma partição de B03–B06)

| Método | Seed 0 macro/micro | Seed 1 macro/micro | Seed 2 macro/micro | Mediana macro |
|---|---|---|---|---|
| svd_dirigido | 0,324158 / 0,270211 | 0,324158 / 0,270211 | 0,324158 / 0,270211 | **0,324158** |
| ase_simetrizado | 0,310022 / 0,279648 | 0,310022 / 0,279648 | 0,310022 / 0,279648 | **0,310022** |

Contexto dos baselines na mesma partição: degree-only 0,149547; deepwalk
0,168601; node2vec 0,158941; estatísticas artesanais 0,383676; MLP 0,579626.
A estrutura global linear (SVD) supera os baselines transdutivos e o
degree-only, mas fica abaixo do probe artesanal não linear e do MLP — leitura
diagnóstica, sem claim de transferência.

## 3. Recursos medidos e teto de RAM

| Medida | Valor |
|---|---|
| Nodes / arestas | 23.188 / 5.243.574 |
| nnz da matriz dirigida | 5.243.574 (0 duplicata, 0 peso zero) |
| Bytes esparsos (CSR) | 63.015.644 (~60,1 MiB) |
| Equivalente denso (n²) | ~4,3 GB; razão esparso/denso = 0,01465 |
| Tempo total | 134,5 s (build 2,1 s; decomposições 5,1–17,1 s por seed) |
| Pico de RSS | 1.162,8 MiB |
| Aceleração | CPU apenas, sem GPU e sem downloads |

O teto de 24 GB de RAM da fase nunca foi aproximado: o pico (~1,1 GiB) fica
muito abaixo, e a matriz permaneceu esparsa. A estimativa inferida de D09 para
o método espectral (4–6 GB, com risco sem SVD aleatorizada) não se confirmou
porque nenhuma matriz densa completa foi construída; a diferença entre
estimativa e medição fica registrada.

## 4. Verificações

- **Fixture exata:** matriz esparsa confere valores, soma de arestas repetidas,
  self-loop e peso zero preservado; SVD de caminho dirigido ponderado reproduz
  o espectro conhecido (7 e 5) e os vetores esperados; ASE de caminho
  bidirecional reproduz λ = 2·cos(π/(n+1)) e o autovetor senoidal.
- **Sem densificação:** teste estático garante ausência de `.toarray(` /
  `todense` no código e presença dos solvers esparsos; a razão esparso/denso é
  verificada em teste e no run real.
- **Invariância à ordem:** tabelas embaralhadas produzem matriz e embeddings
  idênticos (ordem canônica de nós e arestas).
- **Determinismo:** mesma seed reproduz embeddings e predições idênticos.
- **Controles de ambiguidade:** os testes do item 1.
- Predições congeláveis: `runs/b07/predictions-{svd_dirigido,ase_simetrizado}-seed{0,1,2}.json`
  e embeddings `runs/b07/embeddings-{svd_dirigido,ase_simetrizado}-seed{0,1,2}.npy`,
  com SHA-256 registrado no relatório de métricas (12/12 conferidos).

## 5. Limitações

- Resultados internos à fonte e **não** sustentam claim de transferência;
  nenhum uso entre grafos é proposto.
- k = 32 componentes fixo (sem sweep); um valor maior ou menor pode mudar o
  desempenho e não foi explorado nesta fase.
- As 3 seeds controlam apenas o vetor inicial do ARPACK: o subespaço convergido
  é o mesmo, então a variação entre seeds não mede incerteza biológica nem
  técnica adicional.
- O método é transdutivo: os autovetores valem para este grafo; qualquer
  comparação entre grafos exigiria alinhamento permitido e pré-registrado, que
  não existe nesta fase.
