# Dados — layout de zonas e regras de uso

Este diretório guarda **dados brutos e material restrito**, que não entram no
Git. O que é versionado aqui é apenas documentação (`data/README.md`) e
manifestos (`data/manifests/`). A política completa está em
`../docs/research/DATA-MANAGEMENT.md` (R01) e o teste de higiene é
`python3 tools/check_data_hygiene.py`.

## 1. Zonas

| Diretório | Conteúdo | Versionado | Regra |
|---|---|---|---|
| `data/raw/source/` | grafo e metadados permitidos da fonte (MANC) | não | imutável por release; nunca editar in-place |
| `data/raw/target-public/` | grafo e features públicos do alvo (MCNS) | não | apenas o que a fase autorizar em inferência |
| `data/raw/spikes/` | amostras mínimas medidas em D09 (226 MB) | não | regeneráveis; removíveis após H08 e registro de hashes |
| `data/sealed/target-labels/` | tipos, rótulos e crosswalk avaliativo do alvo | não | custódia; **o executor nunca lê** |
| `data/manifests/` | checksums, releases, licenças, datas e URLs | sim | sem tokens, sem URL assinada, sem rótulos |
| `../artifacts/reports/` | relatórios agregados reproduzíveis | sim | sem IDs por neurônio e sem dados brutos |
| `../artifacts/frozen/` | encoder, probe, transformações e hashes congelados | não | somente leitura após o congelamento |
| `../runs/`, `../checkpoints/`, `../outputs/` | execuções, pesos e saídas | não | regeneráveis; nunca versionados |

## 2. Regras rápidas

- Fonte de verdade: raw imutável identificado por release + checksum; snapshots
  canônicos são regenerados por código e configuração, nunca editados à mão.
- Todo download registra URL, release, data de acesso, licença, bytes e SHA-256
  (MD5 oficial quando existir); o MCNS não publica checksum e exige registro do
  SHA-256 local (D09/G2).
- Dados regeneráveis podem ser apagados após o registro de hash; dados selados
  nunca são apagados sem o custodiante.
- Segredos ficam apenas em `.env` local ignorado; nunca em manifestos, logs,
  notebooks ou nomes de arquivo.
- Antes de qualquer commit, rode `python3 tools/check_data_hygiene.py`, que
  prova por sentinelas que dados, runs, selados e tokens estão fora do Git.
