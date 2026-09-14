# Semântica de arestas, thresholds e variantes (H06)

Executado em 2026-09-14. Fixa a semântica primária das arestas vinda do
pré-registro assinado (`configs/edge-primary.json`: direção `pre → post`, peso
bruto em contagem de sinapses, threshold `keep` em 0, self-loops preservados) e
pré-registra oito variantes de ablação (`configs/edge-variants.json`). O
transformador (`tools/edge_transform.py`) aplica a mesma configuração à fonte e
ao alvo, sem usar nenhuma estatística do alvo, e valida o contrato H01 na saída.

## 1. Regras explícitas

- **Peso zero:** preservado na configuração primária (nunca descartado em
  silêncio); só sai por variante `drop_below` declarada, com peso descartado
  contabilizado.
- **Self-loops:** preservados por padrão; `drop_self_loops` remove e registra
  contagem e peso; nunca removidos implicitamente.
- **Componentes isolados:** nodes nunca são removidos; a contagem de nós sem
  aresta ativa é registrada em todas as variantes.
- **Conservação:** na primária, `peso_entrada = peso_saída` (verificado); em
  `sum` de multiedges a conservação já vem dos adapters; em `symmetrized` o peso
  total é conservado ao fundir pares recíprocos; em `drop_below` vale
  `peso_saída = peso_entrada − peso_descartado`.
- **Unidades por variante:** `raw` = contagem de sinapses; `binary` = 0/1;
  `log1p` = log(1+x) — o contrato H01 foi ampliado para aceitar qualquer número
  finito ≥ 0 (antes só inteiro), mantendo a proibição de `NaN`/`Inf`.

## 2. Variantes pré-registradas e efeito nas amostras de 100k arestas

| Variante | Arestas fonte | Peso fonte | Arestas alvo | Peso alvo |
|---|---|---|---|---|
| primary | 100.000 | 779.707 | 100.000 | 12.750.241 |
| binary | 100.000 | 100.000 | 100.000 | 100.000 |
| log1p | 100.000 | 150.158,37 | 100.000 | 476.490,77 |
| threshold_2 | 64.068 | 743.775 | 100.000 | 12.750.241 |
| threshold_5 | 31.248 | 655.842 | 100.000 | 12.750.241 |
| threshold_10 | 17.208 | 564.147 | 100.000 | 12.750.241 |
| symmetrized | 99.624 | 779.707 | 96.646 | 12.750.241 |
| drop_self_loops | 100.000 | 779.707 | 100.000 | 12.750.241 |

As amostras não têm self-loops (o arquivo completo do alvo tem 123; a fonte,
1), por isso `drop_self_loops` não altera os totais aqui; a regra é verificada
por testes com fixture própria. Nenhum threshold foi escolhido olhando o alvo:
as oito variantes são fixas no pré-registro e aplicadas igualmente aos dois
lados.

## 3. Testes (15 casos)

Conservação da primária com zero/self-loop/isolado; todas as variantes validam
no contrato H01 e preservam os nodes; binária e log1p; contabilização de peso
descartado no threshold; conservação da simetrização; remoção explícita de
self-loops; configurações inválidas falham; aplicação idêntica e independente de
estatística do alvo.

## 4. Comandos

```bash
.venv/bin/python tools/edge_transform.py \
  --graph runs/h05/manc-sample-graph.json --config configs/edge-primary.json \
  --out runs/h06/manc-primary.json --metrics runs/h06/manc-primary-metrics.json
.venv/bin/python -m pytest tests/test_edge_transform.py -q
```

## 5. Limitações

- A primária é a única autorizada para o confirmatório; variantes são ablações
  pré-registradas (S06) e não podem ser escolhidas por score do alvo.
- O threshold definitivo da ablação entra no pré-registro (R07) e qualquer
  mudança exige changelog.
- O transformador não recalcula agregação de multiedges (isso é do adapter);
  ele assume o grafo canônico já agregado.
