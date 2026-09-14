# Escala medida e projeção de recursos (D09)

Status: concluída em 2026-09-14 pelo executor (fase D09). Este documento
substitui estimativas vagas por medições de amostras autorizadas e projeções com
intervalo e margem. Nenhum dump integral foi baixado. Orçamento da fase: IA
baixa, CPU, até 1 GB de disco temporário, sem GPU; usado: 226 MB de amostras
(21,4% do teto).

Fontes de contagem: cards auditados em D02–D07 (LIT-0001, LIT-0006, LIT-0010,
LIT-0019, LIT-0020, LIT-0072, LIT-0074, LIT-0079) e APIs oficiais de Zenodo,
Google Cloud Storage e Harvard Dataverse, acessadas em 2026-09-14. Toda linha
deste documento é classificada como **publicado** (declarado pela fonte),
**medido** (observado localmente nesta fase) ou **inferido** (calculado a partir
de medições, com fórmula, intervalo e margem explícitos).

## 1. Amostras baixadas, checksums e custo de carga (medido)

Todas as amostras ficam fora do Git em `data/raw/spikes/` (dados não entram no
repositório). O md5 local foi conferido contra o md5 oficial da fonte quando
publicado; o sha256 foi calculado localmente para toda amostra.

| Dataset (release) | Arquivo | Bytes | md5 oficial (fonte) | sha256 local (prefixo) | Linhas × colunas | Carga (s) | Pico RSS (MB) | Licença |
|---|---|---|---|---|---|---|---|---|
| FlyWire (783) | `proofread_root_ids_783.npy` | 1.114.168 | `e0e6c19732fd8c7a4e39a2d170105421` (Zenodo) | `7c7b7e818e92…` | 139.255 × 1 | 0,22 | 27,6 | CC BY 4.0 |
| FlyWire (783) | `per_neuron_neuropil_count_pre_783.feather` | 16.853.770 | `90fcdb42c1ba05ed92820840fa1e6ba0` (Zenodo) | `35442a46f076…` | 2.781.037 × 3 | 0,97 | 233,6 | CC BY 4.0 |
| MCNS (`male-cns:v1.0`) | `body-annotations-…-minconf-0.5.feather` | 14.483.314 | `50a7718770c57220f160ba4f431ab89e` (GCS) | `2177e246113e…` | 211.577 × 36 | 0,58 | 238,2 | CC BY 4.0 |
| MANC (`v1.0`) | `manc-v1.0-neuron-properties.feather` | 17.188.218 | `f4673117559cc727e1befcb022b6a143` (GCS) | `0c4476528906…` | 102.369 × 56 | 2,99 | 727,0 | CC BY 4.0 |
| MANC (`v1.0`) | `traced-connections.csv` | 75.262.163 | `c543dc9a0c367d9f7c88901d892d78a0` (GCS) | `4553191e8fd0…` | 5.243.574 × 3 | 1,88 | 259,2 | CC BY 4.0 |
| BANC (888) | `banc_888_meta.feather` | 57.550.610 | `6275eda42f98c49539d1ab513d979d09` (Dataverse) | `819bbcff476e…` | 188.508 × 81 | 0,87 | 383,1 | CC BY 4.0 |

Checksums completos ficam no histórico da sessão e podem ser recalculados com
`sha256sum data/raw/spikes/*`; o md5 oficial confere em 6/6 amostras.

Downloads medidos (wall clock): MANC propriedades 17,19 MB em 2,0 s (8,6 MB/s);
MANC conexões 75,26 MB em 4,3 s (17,7 MB/s); BANC meta 57,55 MB em 9,1 s
(6,4 MB/s); FlyWire `proofread_root_ids` 1,11 MB em 4,0 s (dominado por
latência). Taxa de referência para projeções: 6,4–17,7 MB/s.

## 2. Tamanhos de release completos (publicado/listado, não baixado)

- FlyWire v783 — Zenodo (LIT-0001), 5 arquivos somando 10.596.831.504 B
  (9,87 GiB): `flywire_synapses_783.feather` 9.492.998.242 B (md5
  `f8f1b97c9d4b0ea9b4c8b287f6b99091`); `proofread_connections_783.feather`
  852.022.274 B; `per_neuron_neuropil_count_post_783.feather` 233.843.050 B;
  `per_neuron_neuropil_count_pre_783.feather` 16.853.770 B;
  `proofread_root_ids_783.npy` 1.114.168 B.
- MANC v1.0 — bucket `flyem-manc-exports` (LIT-0074): `Neuprint_Neurons` 917,9
  MB; `Neuprint_Neuron_Connections` 736,3 MB; `Neuprint_Synapse_Connections`
  619,8 MB; `traced-connections-per-roi.csv` 159,2 MB; `traced-connections.csv`
  75,3 MB; `manc-v1.0-neuron-properties.feather` 17,2 MB.
- MCNS `male-cns:v1.0` — bucket `flyem-male-cns` (LIT-0079), 11 arquivos
  somando 31.318.683.398 B: `syn-points` 13,06 GB; `syn-partners` 6,78 GB;
  `tbar-neurotransmitters` 2,65 GB; `connectome-weights` 1,05 GB; `body-stats`
  778 MB; `connectome-weights` traced-only 508 MB e significant-only 502 MB;
  `body-neurotransmitters` 43,3 MB; `body-annotations` 14,5 MB (baixado).
- BANC 888 — Dataverse (LIT-0010, LIT-0072): `banc_888_meta.feather` 57,55 MB
  (baixado); `banc_888_synapses_v2_enriched.parquet` 17.146.564.854 B com
  168.951.110 linhas (101,5 B/linha comprimido).
- MAOL `optic-lobe:v1.1` — contagens publicadas: 52.445 neurônios e 6.484.936
  conexões (LIT-0020). Varredura do bucket público `flyem-optic-lobe` (20.000
  objetos, paginada, teto de varredura) encontrou apenas arquivos de imagem
  `.shard`; nenhum arquivo tabular apareceu, então o spike de tabela do MAOL foi
  zero bytes e o acesso tabular segue dependente de conta no neuPrint.
- hemibrain v1.2 — ~25.000 neurônios e ~20M sinapses químicas publicadas
  (LIT-0006); tamanho de arquivo e checksum continuam `não encontrados`.

Divergências a reconciliar em fase própria (não bloqueiam D09): o total FlyWire
citado no card (10,69 GB) difere da soma da API (10,60 GB); BANC meta tem
188.508 linhas medidas contra 188.162 declaradas no card; a varredura do MAOL
tem teto de 20.000 objetos e não prova ausência de tabelas.

## 3. Custo por linha/aresta e compressão (medido)

Rodada `Parquet` (zstd) com leitura por `mmap` em `pandas`/`pyarrow`:

| Tabela | Feather (B) | Parquet zstd (B) | Razão | Escrita (s) | Leitura mmap (s) |
|---|---|---|---|---|---|
| FlyWire neuropil pré | 16.853.770 | 8.577.321 | 0,509 | 0,43 | 0,13 |
| MCNS anotações | 14.483.314 | 4.658.279 | 0,322 | 0,47 | 0,12 |
| MANC propriedades | 17.188.218 | 8.790.622 | 0,511 | 2,96 | 2,57 |
| BANC meta | 57.550.610 | 21.686.179 | 0,377 | 1,12 | 0,14 |

Intervalo de conversão `feather/CSV → Parquet+Arrow zstd` medido: 0,322–0,511×.
A leitura `mmap` foi 1,4–6,7× mais rápida que a carga completa nos arquivos
maiores e não materializa o arquivo inteiro em RAM.

Custo COO/CSR medido com o grafo traçado do MANC (5.243.574 arestas, 23.188 nós
indexados, peso `float32`):

- COO: 20,0 B/aresta com índices `int64` (pre, post) + peso `float32`;
  construção CSR 1,52 s (0,29 µs/aresta, single-thread), pico de RSS 379,1 MB.
- CSR (`scipy`): 8,02 B/nnz com índices `int32` (4 B dados + 4 B índices +
  indptr), 42,0 MB para 5,24M nnz.

## 4. Projeções com intervalo e margem (inferido)

Fórmulas (por aresta `e` e por nnz; `idx` = 4 B `int32` ou 8 B `int64`):

- COO steady: `e × (2×idx + peso)`; compressão Parquet: `bytes × 0,322–0,511`.
- CSR steady: `nnz × (4 + idx) + (n+1) × idx`; `idx` = 4 B enquanto nnz e nós
  couberem em 2³¹.
- Pico de construção em RAM: 3× o steady (CSV bruto + arrays + estrutura), com
  margem adicional de 25% aplicada ao resultado.

| Alvo | Arestas (fonte) | COO 12–24 B/aresta | Pico de construção (3× + 25%) | CSR (4/8 B índices) | Disco Parquet |
|---|---|---|---|---|---|
| BANC sinapses v2 | 168.951.110 (publicado) | 2,03–4,05 GB | 7,6–15,2 GB | 1,35–2,03 GB | 17,15 GB publicado |
| MCNS pesos minconf 0.5 | não publicado | não projetado | não projetado | não projetado | 1,05 GB listado |
| MAOL | 6.484.936 (publicado) | 0,08–0,16 GB | 0,29–0,59 GB | 0,05–0,08 GB | não acessível sem conta |
| hemibrain | ~20.000.000 (publicado) | 0,24–0,48 GB | 0,90–1,80 GB | 0,16–0,24 GB | não medido |
| MANC traçado | 5.243.574 (medido) | 0,06–0,13 GB | 0,24–0,47 GB | 0,04–0,06 GB | 0,0008 GB (estimado) |
| FlyWire | não publicado | não projetado | não projetado | não projetado | 9,87 GB listado |

Tempo de transferência na taxa medida (6,4–17,7 MB/s): BANC v2 17,15 GB →
16–45 min; MCNS completo 31,32 GB → 29–82 min; FlyWire completo 10,60 GB →
10–28 min. Pré-processamento medido (coalescer duplicatas + CSR) a 0,29 µs/aresta
single-thread → BANC 168,95M arestas ≈ 49 s, com margem de 1,5×: 1–2 min.

## 5. Consequências para 32 GB de RAM e 8 GB de VRAM (inferido)

- RAM: o pico projetado do BANC cabe em 32 GB com folga de 2–4×; mas o disco
  local tem 34 GB livres no host atual (medido), menores que BANC (17,15 GB)
  somado a MCNS (31,32 GB); qualquer ingestão completa exige armazenamento
  externo ou liberação de espaço antes das fases de ingestão.
- VRAM: `edge_index` `int32` no padrão PyG consome 8 B/aresta → BANC ≈ 1,35 GB,
  cabe em 8 GB; `int64` ≈ 2,70 GB, ainda cabe, mas sem espaço para features, então
  a política padrão da fase de modelagem será `int32` com lotes por
  `NeighborLoader`/subgrafo (1M arestas ≈ 8 MB) e `mmap` para colunas.
- Trabalho em CPU: carregar as tabelas de metadados inteiras custa menos de
  1,2 GB de pico; o gargalo real é disco (transferência e conversão), não RAM.

## 6. Falhas, descartes e limitações

- MAOL: nenhuma tabela pública alcançada sem credencial; registro como resultado
  negativo medido (varredura com teto), não como ausência provada.
- hemibrain: sem tamanho/checksum oficiais; projeções usam apenas a contagem
  publicada de sinapses e ficam marcadas como inferidas.
- FlyWire e MCNS: contagem de linhas por arquivo não é publicada; RAM não foi
  projetada para esses alvos para não extrapolar sem base.
- Nenhum arquivo acima de 100 MB foi baixado; nenhuma GPU usada; nenhuma
  credencial, conta ou token; nenhum dado entrou no Git.
- As projeções são intervalos analíticos derivados das amostras MANC/BANC, com
  margem de 25% e pico 3×; elas não substituem medição no momento da ingestão.

## 7. Reprodução

- `python3 tools/spike_d09.py inspect <arquivo>` — bytes, linhas, colunas,
  dtipos, tempo e pico de RSS.
- `python3 tools/spike_d09.py parquet <arquivo>` — rodada Parquet zstd e leitura
  `mmap` com tamanho final.
- `python3 tools/spike_d09.py csr <csv> --pre … --post … --weight …` — custo
  COO/CSR e nós indexados.
- Checksums: `md5sum`/`sha256sum` em `data/raw/spikes/*`; md5 oficiais nas APIs
  citadas no item 2.
