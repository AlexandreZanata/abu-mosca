# Baselines internos da fonte (B03)

Executado em 2026-09-14, somente **dentro da fonte MANC** (`manc:v1.2.1`), em
modo exploratório. Nenhum rótulo, score ou arquivo do alvo foi consultado;
nenhum unseal. Rótulos de tipo da fonte são públicos (propriedades do MANC) e o
split/transformações são exclusivamente source-fit.

## 1. Base usada

- Rótulos: `manc_neuron_properties.feather` → IDs opacos; classes com n ≥ 10
  (K do pré-registro). 405 nodes rotulados ficaram fora do snapshot de arestas
  traçadas (sem aresta traçada) e foram descartados com registro.
- Nodes usados: 14.847 em 519 classes; split determinístico por hash de ID
  (80/20): 11.668 treino / 3.179 validação, com cobertura das 519 classes.

## 2. Resultados (validação interna da fonte)

| Baseline | Valor | Conferência |
|---|---|---|
| Chance uniforme (analítica) | 0,001927 | — |
| Random estratificado (analítica) | 0,004920 | simulado em 200 sorteios: **0,004931** (concorda) |
| Random estratificado (3 seeds do pré-registro) | mediana 0,005662 | seeds registradas |
| Maioria | **0,022963** | chance analítica idêntica à simulada (exato) |
| Degree-only (centroide em grau z-scored) | macro Recall@1 **0,149547** | usa exatamente as transformações source-fit (4 features de grau) |

A chance analítica e a simulada concordam (maioria exata; random dentro de ~1,1e-5). O degree-only fica bem acima do piso e será o principal controle de atalho nas
fases seguintes; nenhuma conclusão além disso é feita aqui.

## 3. Artefatos congeláveis

- `runs/b03/predictions-random-seed{0,1,2}.json`,
  `predictions-majority.json` e `predictions-degree-only.json`, com SHA-256
  registrado no relatório de métricas.
- Estatísticas source-fit (média/desvio por feature de grau) registradas no
  JSON; o transform do degree-only usa esses valores e nada do alvo.
- Métricas brutas: `artifacts/reports/B03-BASELINES-FONTE.json`.

## 4. Recursos e limites

- Execução: 30,9 s, pico de 1.139 MiB (CPU), sem GPU, sem downloads.
- Limitações: classes com n < 10 fora (519 de 2.448 tipos); 405 nodes sem
  features no snapshot; resultados são internos à fonte e **não** são claims de
  transferência; o alvo permanece intocado.
