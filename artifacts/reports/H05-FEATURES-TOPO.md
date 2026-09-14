# Remapeamento opaco e features topology-only (H05)

Executado em 2026-09-14. Define o mapeamento canônico de IDs (`tools/opaque_ids.py`),
gera features permitidas (graus, pesos, reciprocidade e self-loops) com
**fit/transform separado** (`tools/topology_features.py`) e verifica por testes
que permutar IDs e ordem preserva os resultados. Nenhum nome, tipo, região,
coordenada ou ID entra na matriz de features.

## 1. Mapeamento opaco

- `opaque_node_id(dataset, release, body) = "n" + sha256("dataset|release|body")[:16]`.
- Os adapters H02/H03 foram refatorados para usar esse módulo (mesma fórmula,
  saídas douradas inalteradas; 10 testes de adapter continuam passando).
- O mapa body→opaco existe apenas no adapter/custodiante; features guardam os
  IDs em array paralelo, nunca como número, categoria ou índice treinável.

## 2. Features e políticas fixas

| Feature | Definição | Fonte (amostra, n=16.543) mean ± std |
|---|---|---|
| in_degree | nº de arestas de entrada | 6,04 ± 5,03 |
| out_degree | nº de arestas de saída | 6,04 ± 102,35 |
| weighted_in | soma de pesos de entrada | 47,13 ± 88,84 |
| weighted_out | soma de pesos de saída | 47,13 ± 749,35 |
| reciprocity | min(w(i→j), w(j→i)) somado / weighted_out, limitado a 1 | 0,0001 ± 0,0022 |
| self_loop_weight | soma dos pesos de self-loops | 0,0000 ± 0,0000 |

- Fit (z-score) ajustado **somente na fonte** (`source-stats.json`, config
  `33ed771f…`); transform aplica os mesmos stats ao alvo.
- Missing/indefinido vira `0,0` por regra fixa (ex.: reciprocidade sem aresta
  de saída); não finitos após escala viram `0,0`; valores são clipados em ±8.
- `missing` nunca vira sentinela numérica; atributos proibidos no trilho A
  fazem o cálculo falhar.

## 3. Demonstração fonte → alvo

- Fonte: amostra MANC de 100.000 arestas (16.543 nodes, conservação de peso).
- Alvo: amostra pública MCNS de 100.000 arestas (38.442 nodes).
- Transform do alvo: 0,8 s, 0 não-finitos, 7.069 valores clipados em ±8 (cauda
  pesada de grau/peso do alvo), médias por feature `[-0,70, -0,03, 1,54, 0,37,
  0,60, 0,00]`.

## 4. Testes (6 casos)

Features exatas por tipo; permutação de IDs e de ordem preserva os vetores;
normalizador ajustado somente na fonte; política fixa para não finitos e
clipping; matriz sem IDs e sem atributos proibidos; atributo proibido falha.

## 5. Reprovações e correções

- A primeira versão do relatório de transform recalculava somas dentro de laço
  O(n²) e levava 174,9 s; corrigido para 0,8 s sem mudar resultados.

## 6. Comandos

```bash
.venv/bin/python tools/topology_features.py fit \
  --graph runs/h05/manc-sample-graph.json --stats runs/h05/source-stats.json \
  --npz runs/h05/source-features.npz --metrics runs/h05/fit-metrics.json
.venv/bin/python tools/topology_features.py transform \
  --graph runs/h03/mcns-sample-graph.json --stats runs/h05/source-stats.json \
  --npz runs/h05/target-features.npz --metrics runs/h05/transform-metrics.json
.venv/bin/python -m pytest tests/test_topology_features.py -q
```

## 7. Limitações

- Features são estatísticas de primeira ordem (graus/pesos/reciprocidade);
  assinaturas estruturais mais ricas pertencem a B04.
- O fit real definitivo deve usar o grafo completo da fonte em H08 (aqui a
  demonstração usa amostra de 100k arestas).
- O clipping ±8 é política fixa desta fase e deve ser reavaliado em H06/S06 sem
  alterar o pré-registro.
