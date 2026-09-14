# Adapter da fonte MANC → grafo canônico (H02)

Executado em 2026-09-14 pelo executor sobre a **amostra real de D09**
(`data/raw/spikes/manc_traced_connections.csv`, SHA-256 `4553191e…`, CC BY 4.0,
release `manc:v1.2.1`), não sobre o release completo — o release integral é H08.
O adapter lê apenas a tabela de adjacências traçadas (`bodyId_pre`,
`bodyId_post`, `weight`) e nunca abre o arquivo de propriedades dos neurônios.

## 1. Métricas medidas

| Métrica | Valor |
|---|---|
| Linhas de entrada (pares pré→pós) | 5.243.574 |
| Nodes (IDs opacos únicos) | 23.188 |
| Arestas após agregação | 5.243.574 |
| Multiedges agregadas (`sum`) | 0 (arquivo já vem agregado por par) |
| Self-loops encontrados | 1 (preservado; `allow_self_loops = true`) |
| Soma de pesos na entrada / saída | 30.698.527 / 30.698.527 (`weight_conserved = true`) |
| SHA-256 de entrada | `4553191e…` (idêntico ao manifesto R03) |
| SHA-256 da saída canônica | `7a21a947…` (790,7 MB JSON) |
| SHA-256 de `config` do adapter | `1db393ed…` |
| Amostra dourada | 40 nodes / 60 edges, SHA-256 `859f10f0…` |
| Tempo de build / comando completo | 13,1 s / 51,4 s |
| Pico de RSS | 6.735 MiB (serialização do JSON textual) |

Campos descartados/transformados: nada de tipo, região, posição ou neuropilo é
lido ou incluído; os nodes carregam apenas graus derivados da topologia
(`degree_in`, `degree_out`), e os IDs reais (`bodyId`) são convertidos em IDs
opacos `n<16 hex>` com mapeamento registrado apenas no adapter.

## 2. Reconciliação com a fonte oficial

- **Nodes:** 23.188 nós medidas contra “cerca de 23.000 neurônios” da página
  oficial do MANC (D05/LIT-0074); a diferença (~0,8%) é compatível com
  segmentos traçados do arquivo de adjacências e não altera a ordem de grandeza.
- **Arestas:** 5.243.574 pares pré→pós traçados. A página oficial publica
  10 milhões de sítios pré-sinápticos e 74 milhões de PSDs — unidades diferentes
  (sítios/PSDs vs pares agregados), portanto os números **não são diretamente
  reconciliáveis**; a diferença fica explicada pela granularidade.
- **Pesos:** somam 30.698.527 sinapses nas arestas traçadas; a conservação
  entrada→saída é verificada e registrada.

## 3. Verificações de aceite

- Checksums de entrada (manifesto R03) e de saída (`metrics.json`) conferidos.
- IDs opacos únicos; endpoints das arestas referenciam nodes existentes.
- Pesos inteiros ≥ 0; direção conhecida (`pre → post`); multiedges agregadas por
  soma sem perda de peso.
- Grafo de saída e amostra dourada validados pelo contrato H01
  (`tools/graph_contract.py`), sem atributos proibidos no trilho A.

## 4. Reprodução

```bash
.venv/bin/python tools/adapter_manc.py \
  --connections data/raw/spikes/manc_traced_connections.csv \
  --out runs/h02/manc-graph.json \
  --golden tests/fixtures/manc-sample-graph.json \
  --metrics artifacts/reports/H02-ADAPTER-FONTE.json
.venv/bin/python -m pytest tests/test_adapter_manc.py -q
```

## 5. Falhas e limitações

- Nenhuma falha de execução; o arquivo real não contém multiedges (o teste de
  agregação usa CSV sintético com par duplicado).
- O JSON canônico é verboso (790,7 MB para 5,2M arestas) e domina o pico de RAM
  na serialização; H08 pode precisar de escrita incremental/colunar preservando
  o mesmo contrato lógico (a decidir em H08, sem mudar o schema).
- A amostra dourada cobre 40 nodes/60 edges para testes rápidos; ela não
  substitui o grafo completo.
- O release completo e a reconciliação fina com o neuPrint ficam para H08, com
  o teto de recursos do G3.
