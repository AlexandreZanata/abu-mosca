# Snapshots canônicos das releases completas (H08)

Executado em 2026-09-14. Materializa o grafo canônico (H01) em Parquet —
`edges.parquet` (`source`, `target`, `weight`) e `nodes.parquet` (`id`,
`degree_in`, `degree_out`) — para a fonte completa e para o alvo público, com
`provenance.json` e `SHA256SUMS`. Nenhum rótulo selado ou coluna de tipo entra
nos snapshots; as anotações do alvo são lidas apenas na coluna `bodyId`.

## 1. Achado de semântica corrigido nesta fase

A documentação oficial do MCNS descreve `connectome-weights` como
“segment-to-segment connection strengths for all segments ... This is the full
connection graph” (página de download, acesso 2026-09-14). O arquivo completo
tem **151.856.684 arestas entre segmentos e 88.384.522 segmentos** — não são os
166.700 neurônios curados. O snapshot do MVP é, portanto, o grafo
**nível-neurônio** obtido restringindo as arestas aos `bodyId` anotados e
agregando por par (soma de peso), com a coluna `bodyId` das anotações usada
somente como chave pública. O snapshot segmento-a-segmento fica registrado como
intermediário bruto.

## 2. Snapshot da fonte (MANC `manc:v1.2.1`)

| Métrica | Valor |
|---|---|
| Arestas | 5.243.574 |
| Nodes | 23.188 |
| Soma de pesos | 30.698.527 (conservada) |
| Self-loops | 1 |
| `edges.parquet` / `nodes.parquet` | 13,8 MB / 0,3 MB |
| SHA-256 do conjunto | `1b12335a…` |
| Tempo / pico de RAM | 5,5 s / 1.024 MiB |
| Idempotência | segunda execução `cached` (hashes conferidos) |

## 3. Snapshot do alvo público (MCNS `male-cns:v1.0`, nível-neurônio)

| Métrica | Valor |
|---|---|
| Arestas do arquivo bruto (segmentos) | 151.856.684 |
| Arestas mantidas (ambos os lados anotados) | 26.028.386 |
| Arestas descartadas (lado não anotado) | 125.828.298 |
| Arestas após agregação por par | 26.028.386 |
| Nodes (bodies anotados) | 211.577 |
| Soma de pesos | 125.365.933 (conservada no subconjunto) |
| Self-loops | 112 |
| `edges.parquet` / `nodes.parquet` | 257,4 MB / 2,6 MB |
| SHA-256 do conjunto | `d9d61287…` |
| Tempo / pico de RAM | 27,3 s / 11.055 MiB |
| Idempotência | segunda execução `cached` |

## 4. Intermediário bruto (segmento-a-segmento)

151.856.684 arestas, 88.384.522 segmentos, peso 311.833.243, 123 self-loops;
593 s e pico de 16.588 MiB. Mantido apenas para rastreabilidade do achado.

## 5. Critérios de aceite

- **Idempotente:** reexecuções retornam `cached` com hashes conferidos
  (`SHA256SUMS`); entrada divergente falha sem sobrescrever.
- **Recursos:** picos de 1.024 MiB e 11.055 MiB, abaixo do teto de 28 GB; disco
  livre de 144 GB após a fase; nenhum OOM ou run parcial aceito.
- **Contagens batem H02/H03** para a fonte (5.243.574 / 23.188 / 30.698.527) e
  para o alvo nos totais de segmento (151.856.684 / 311.833.243 / 123), com a
  correção de nível documentada.
- **Sem labels:** colunas fixas; anotações usadas só em `bodyId`; nenhum tipo,
  região, crosswalk ou rótulo no snapshot.

## 6. Retomada e reprodução

```bash
.venv/bin/python tools/snapshot_build.py manc --connections data/raw/spikes/manc_traced_connections.csv \
  --manifest data/manifests/manc-v1.0.json --out runs/h08/source
.venv/bin/python tools/snapshot_build.py mcns --weights data/raw/target-public/mcns_connectome_weights.feather \
  --annotations data/raw/spikes/mcns_body_annotations.feather --manifest data/manifests/mcns-v1.0.json \
  --out runs/h08/target-neuron
.venv/bin/python -m pytest tests/test_snapshot_build.py -q
```

Snapshots ficam em `runs/` (fora do Git); a retomada é a própria reexecução:
entrada igual → `cached`; divergente → erro sem sobrescrita.

## 7. Limitações

- O snapshot do alvo exclui arestas com lado não anotado (125,8M): a cobertura
  é documentada e a decisão de quais bodies entram no T0 é da custódia (H07).
- `body-stats` (780 MB) ainda não foi usado; contagens por segmento ficam no
  intermediário.
- A agregação por par aplica a regra `sum` de H06; variantes de peso continuam
  no transformador H06 e não alteram o snapshot.
