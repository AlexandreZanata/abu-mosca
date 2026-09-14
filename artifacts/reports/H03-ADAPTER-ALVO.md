# Adapter público do alvo MCNS → grafo canônico (H03)

Executado em 2026-09-14 pelo executor sobre o grafo público do alvo
(`data/raw/target-public/mcns_connectome_weights.feather`, release
`male-cns:v1.0`, CC BY 4.0, MD5 oficial do GCS `f30e9dcc…`, SHA-256 local
`e35da783…`, 1.051.241.946 bytes). O adapter lê **somente** as três colunas de
grafo (`body_pre`, `body_post`, `weight`) e nunca abre anotações, tipos,
crosswalk ou qualquer arquivo avaliativo; `data/sealed` não é tocado.

## 1. Métricas medidas

| Métrica | Valor |
|---|---|
| Linhas do arquivo completo | 151.856.684 |
| Soma de pesos (sinapses) | 311.833.243 |
| Peso mínimo | 1 (sem zeros nem negativos) |
| Self-loops no arquivo completo | 123 (preservados; exigem flag em H08) |
| Amostra determinística | primeiras 100.000 linhas |
| Nodes da amostra | 38.442 (IDs opacos únicos) |
| Arestas após agregação | 100.000 (0 multiedges no arquivo) |
| Conservação de peso na amostra | 12.750.241 = 12.750.241 |
| Colunas lidas | exatamente `body_pre`, `body_post`, `weight` |
| SHA-256 de entrada | `e35da783…` (igual ao manifesto R03) |
| SHA-256 do grafo de amostra | `4b1ed387…` (20,8 MB JSON, em `runs/`) |
| SHA-256 de `config` do adapter | `d11334ff…` |
| Amostra dourada | 40 nodes / 57 edges, SHA-256 `4b30c6e3…` |
| Tempo / pico de RSS | 8,2 s / 5.240,9 MiB (comando completo 8,8 s, 5,37 GB) |

Transformações: nenhuma coluna descartada (o schema público tem apenas o
necessário); IDs reais viram IDs opacos `n<16 hex>`; `degree_in/degree_out` são
derivados apenas da topologia da amostra. Nenhum nome, tipo, região ou
correspondência entra no grafo.

## 2. Reconciliação

- Publicado no card D07: 166.700 neurônios e 11.710 tipos (LIT-0023); a
  contagem exata de nodes únicos do arquivo completo exige operação pesada e
  fica para H08. A amostra de 100.000 arestas já cobre 38.442 nós distintos.
- Pares-agregados (151,9M de arestas) não são diretamente comparáveis a
  contagens de sítios/PSDs; a unidade canônica é contagem de sinapses e a soma
  total (311,8M) fica registrada para conferência em H08.
- 123 self-loops existem no arquivo completo; a amostra não contém nenhum, por
  isso `allow_self_loops = false` no grafo da amostra — H08 deve ativar a flag
  no grafo completo.

## 3. Verificações de aceite

- Roda sem `data/sealed` e sem qualquer arquivo de anotação; o schema de
  entrada é exigido com exatamente três colunas e falha se aparecer extra.
- Checksums de entrada (manifesto R03) e de saída conferidos; IDs únicos;
  endpoints válidos; pesos ≥ 0; direção `pre → post`; conservação de peso.
- Grafo e amostra dourada validados pelo contrato H01
  (`tools/graph_contract.py`), sem atributos proibidos no trilho A.

## 4. Reprodução

```bash
.venv/bin/python tools/adapter_mcns.py \
  --weights data/raw/target-public/mcns_connectome_weights.feather \
  --out runs/h03/mcns-sample-graph.json \
  --golden tests/fixtures/mcns-sample-graph.json \
  --metrics artifacts/reports/H03-ADAPTER-ALVO.json
.venv/bin/python -m pytest tests/test_adapter_mcns.py -q
```

## 5. Falhas e limitações

- Nenhuma falha de execução; testes cobrem colunas extras (ex.: `type`) e pesos
  negativos, que falham como esperado.
- Atributos de grau são locais à amostra (não representam o grau no grafo
  completo); o grafo integral fica para H08.
- O JSON canônico da amostra tem 20,8 MB para 100k arestas; H08 deve reutilizar
  a leitura colunar/mmap e considerar escrita incremental sem mudar o schema.
