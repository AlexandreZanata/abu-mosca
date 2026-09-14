# Auditoria de qualidade e congelamento do dataset analítico (H09)

Executada em 2026-09-14 em **modo estritamente exploratório** (H07 inconclusiva
por circularidade). Fontes: snapshots canônicos de H08
(`runs/h08/source` e `runs/h08/target-neuron`), somente topologia pública;
nenhum rótulo, crosswalk, score ou arquivo selado foi consultado. Métricas
brutas em `artifacts/reports/DATA-QUALITY.json`; congelamento em
`data/manifests/analitico-v1.json`.

## 1. Checks realizados

| Check | Fonte (MANC) | Alvo público (MCNS) |
|---|---|---|
| Nodes / arestas | 23.188 / 5.243.574 | 211.577 / 26.028.386 |
| Soma de pesos | 30.698.527 | 125.365.933 |
| Pares duplicados | 0 | 0 |
| Componentes conexas | 1 | 22.944 |
| Nodes isolados | 0 | 22.799 |
| Self-loops | 1 | 112 |
| Reciprocidade (arestas com reversa) | 0,3044 | 0,2979 |
| Graus conferidos (divergência máx.) | 0 | 0 |
| Pesos zero / negativos | 0 / 0 | 0 / 0 |
| Drift de schema | nenhum | nenhum |
| Missingness | não se aplica (topologia pura; sem atributos no snapshot) | idem |

Assimetria direcional: reciprocidade de ~30% nos dois lados e distribuição de
grau com cauda pesada (mín. 1, sem zeros); sem sentinelas.

## 2. Desvios encontrados e corrigidos nesta fase

1. **Semântica de grau divergente:** o snapshot da fonte armazenava contagem de
   arestas e o do alvo, soma ponderada (divergência máx. 21.935). Padronizado
   como `weighted_sum` nos dois e a fonte foi reconstruída (o `nodes.parquet`
   da fonte mudou; o de arestas não).
2. **Não determinismo na agregação do alvo:** a ordem do `group_by` variava
   entre execuções. A agregação passou a ordenar por `(source, target)`;
   duas reconstruções independentes geraram hashes idênticos
   (`edges.parquet` `485c7a93…`).
3. **Nível do alvo:** o arquivo público é segmento-a-segmento; o snapshot usa o
   nível-neurônio (26.028.386 de 151.856.684 arestas; 125.828.298 descartadas
   por lado não anotado) — documentado em H08.

## 3. Reconciliação com os cards e contagens publicadas

- MANC: 23.188 nodes vs ~23.000 neurônios publicados (LIT-0074), ~0,8% acima
  (segmentos traçados).
- MCNS: 211.577 bodies anotados vs 166.700 neurônios curados (LIT-0023); a
  diferença é de definição de anotação e não de dados.
- Desfecho confirmatório: **inexistente** — T0 e hemilinhagem inconclusivos por
  circularidade (H07, changelog 2.3); nenhum claim confirmatório autorizado.

## 4. Congelamento

- `data/manifests/analitico-v1.json`: status `exploratory-only`,
  `labels_used: false`, `confirmatory_outcome: nenhum`, hashes dos quatro
  arquivos Parquet e **hash analítico**
  `5c7b96bd4939e285e5fd41d80a1012d686b69c608d627f47a1ee17dd746f9737`.
- O hash é derivado apenas dos snapshots públicos; mudanças exigem nova versão
  e registro no changelog.

## 5. Recursos e limites

- Execução: ~45 s e pico de 5.485 MiB (CPU), sem GPU, sem downloads.
- Limitações: 22.799 bodies anotados ficaram isolados no subgrafo mantido;
  o recorte T0 é da custódia e não há rótulo confirmatório; revisor único.
- Validação: `python3 tools/validate_research.py`.
