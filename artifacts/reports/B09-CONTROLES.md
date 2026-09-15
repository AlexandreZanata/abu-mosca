# Controles nulos e congelamento dos baselines (B09)

Executado em 2026-09-15, somente na **fonte MANC** e sem nenhum dado do alvo.
`tools/null_controls.py` roda os controles nulos declarados, registra as
invariantes e gera o pacote congelado dos comparadores de B03–B08
(`data/manifests/baselines-b09.json`). Nenhuma métrica do alvo foi aberta; o
relatório é restrito ao diagnóstico within-source.

## 1. Regras declaradas antes da execução

- permutação de rótulos: 20 sorteios, dentro de cada split (contagens por
  classe preservadas), com p-valor empírico `(1 + excedências) / 21`;
- rewiring: trocas dirigidas de alvo preservando graus de contagem, alvo de
  **10×E = 52.435.740 trocas aceitas**, sem self-loops novos nem multiedges;
  pesos ficam nos slots das arestas (multiconjunto preservado; graus
  ponderados **não** são invariantes e isso é registrado);
- permutação de IDs: permutação aleatória dos 23.188 IDs de nó com os rótulos
  seguindo a permutação; a métrica deve ser invariante com a partição
  carregada;
- negativos pareados por grau: B = 10 negativos por consulta, acaso
  `1/(B+1) = 0,090909`; regra "fine" pareia os negativos pela mediana de
  log-grau **da classe verdadeira**; "coarse" usa o bin de piso do log-grau da
  consulta; "none" sorteia sem pareamento;
- melhor baseline: **maior mediana de Macro Recall@1 na validação da fonte**
  (regra source-only pré-registrada); empate resolve pelo método mais simples.

## 2. Resultados

| Controle | Resultado | Interpretação |
|---|---|---|
| permutação de rótulos (todas as features) | real 0,383676; nulos média 0,002250, máx 0,004817, p = 0,047619 | degradou como esperado |
| permutação de rótulos (features de grau) | real 0,149547; nulos média 0,002175, máx 0,004496, p = 0,047619 | degradou como esperado |
| rewiring (10×E, 56.636.046 tentativas, 52.435.740 aceitas) | artesanal 0,383676 → **0,050154**; família degree 0,087579; graus in/out preservados (True/True); 0 self-loops novos; pares únicos 5.243.574 → 5.243.574 | degradou como esperado |
| permutação de IDs | features equívocas (diferença máxima 0,0), 0 rótulos divergentes, partição carregada 0,383676 (idêntica); split por hash re-sorteado = 0,411806 (Δ +0,028130) | invariante como esperado |
| negativos pareados (grau, fine/coarse/none) | degree-only 0,494810 / 0,492608 / 0,677886; artesanal 0,754325 / 0,766908 / 0,853728; acaso 0,090909 | **investigação pendente** |

## 3. Investigação dos negativos pareados por grau

O pareamento por mediana de log-grau da classe verdadeira **não neutraliza** o
atalho de grau: um comparador que usa apenas as quatro features de grau ainda
acerta 0,494810 contra acaso de 0,090909. A explicação é estrutural: o probe
compara a consulta ao **centroide** (vetor médio) de cada classe, não apenas à
mediana; como a consulta é amostrada da distribuição de grau da própria classe,
a distância ao centroide verdadeiro é sistematicamente menor, mesmo com
negativos de mediana pareada. Ou seja, o grau do nó carrega informação de
classe ao nível da distribuição, e nenhum pareamento por resumo (mediana/bin)
consegue removê-lo.

Consequência registrada para o gate: (a) o controle apropriado para o atalho de
grau é o **comparador degree-only pré-registrado**, não a amostragem de
negativos por classe; (b) controles mais duros por consulta (estratos de grau
com negativos de distribuição equivalente) ficam como pendência para M09; (c)
o resultado reforça que qualquer ganho da GNN deverá ser medido **sobre** o
degree-only, como já exige o pré-registro. Pendências: `degree_matched_degree_features`
e `degree_matched_all_features`.

## 4. Pacote congelado dos baselines

`data/manifests/baselines-b09.json` (schema `b09-baseline-package`,
`target_data_used: false`, SHA-256 `9359862d…`) congela o ranking dos 11
comparadores within-source, com relatório e hash de cada um, mais os 27 artefatos
de predição verificados por SHA-256 (27/27 `ok`):

| Método | Macro Recall@1 (fonte) |
|---|---|
| MLP pareado 1-3M | 0,579626 |
| MLP 500k | 0,554048 |
| MLP 100k | 0,472795 |
| artesanal (todas) | 0,383676 |
| svd dirigido | 0,324158 |
| ase simetrizado | 0,310022 |
| deepwalk | 0,168601 |
| node2vec | 0,158941 |
| degree-only | 0,149547 |
| random estratificado | 0,005662 |
| majority | 0,001927 |

Melhor comparador pela regra source-only: **MLP pareado 1-3M**; melhor
baseline simples clássico: **artesanal (todas)**. Nenhum baseline forte foi
descartado. O comparador transdutivo publicado (REGAL, B08) fica fora do
ranking por não compartilhar a partição de tipos.

## 5. Recursos e limitações

- Execução: 840,6 s, pico de 6.466,7 MiB (extração de features), CPU apenas,
  sem GPU e sem downloads novos; rewiring a ~293 mil trocas/s.
- Limitações: o rewiring preserva graus de **contagem** e o multiconjunto de
  pesos, mas não os graus ponderados; a permutação de IDs mostrou que a
  partição determinística por hash depende do ID (sensibilidade técnica de
  +0,028130 registrada); o controle de negativos por classe não neutraliza o
  grau (investigado acima); resultados são internos à fonte e não sustentam
  claim de transferência.
