# M04 — Smoke e calibração de sampling/recursos

- Executor: agente executante; data 2026-09-15.
- Status: **exploratory-only** (modo exploratório); **somente fonte**; **sem nenhum dado do alvo**.
- Dependências: M02, M03, H08 (todas concluídas). Grid do R07 §5 (emenda 3.0) usado
  como fronteira congelada; nenhum trial foi alterado.
- Objetivo: encontrar batch/fanout/precisão seguros antes do treino completo, com
  perfis de tempo, RAM/VRAM e throughput.
- Proibição respeitada: o smoke não seleciona por resultado-alvo; a escolha usa
  apenas recursos (pico de VRAM, OOM e tempo por passo). Nenhuma métrica do alvo
  existe ou foi aberta.

## Hardware e ambiente

| Item | Valor |
|---|---|
| GPU | NVIDIA GeForce RTX 4060 Laptop GPU, 7,62 GiB totais |
| Software | torch do lock R02 (2.14.0+cu130), `.venv/bin/python` |
| CPUs | 16 |
| Pico de RSS do processo | 2,51 GB |
| Orçamento de GPU desta fase | 177,5 s (limite 30 min) |

## Grid pré-declarado (16 configurações)

Seis configurações de **sampling** (dim 64/128) calibraram o custo de vizinhança e
batch; dez configurações do **MVP** confirmaram o orçamento dos trials. Métricas:
tempo por passo, fração de CPU em neighbor sampling, pico alocado/reservado de
VRAM e throughput.

| Config | Dim | Camadas | Fanout | Batch | Prec | Checkpoint | Passos | s/passo | Amostragem (s) | Pico aloc. (MiB) | Pico res. (MiB) | Margem mín. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| s64_2l_f10_b512 | 64 | 2 | 10,10 | 512 | fp32 | não | 8 | 0,423 | 0,410 | 104,3 | 128,0 | 0,98 |
| s64_2l_f15_b512 | 64 | 2 | 15,10 | 512 | fp32 | não | 8 | 0,495 | 0,484 | 125,6 | 150,0 | 0,98 |
| s64_2l_f10_b1024 | 64 | 2 | 10,10 | 1024 | fp32 | não | 8 | 0,594 | 0,582 | 144,6 | 168,0 | 0,97 |
| s128_2l_f10_b512 | 128 | 2 | 10,10 | 512 | fp32 | não | 8 | 0,396 | 0,380 | 184,8 | 246,0 | 0,96 |
| s128_2l_f15_b1024 | 128 | 2 | 15,10 | 1024 | fp32 | não | 8 | 0,761 | 0,737 | 309,5 | 636,0 | 0,90 |
| s128_3l_f15_b512 | 128 | 3 | 15,10,10 | 512 | fp32 | não | 8 | 1,432 | 1,380 | 929,9 | 1.038,0 | 0,84 |
| mvp576_2l_f10_b512 | 576 | 2 | 10,10 | 512 | fp32 | não | 8 | 0,455 | 0,379 | 772,5 | 1.582,0 | 0,76 |
| mvp408_3l_f1510_b512 | 408 | 3 | 15,10,10 | 512 | fp32 | não | 8 | 1,461 | 1,277 | 2.874,6 | 5.202,0 | 0,22 |
| mvp576_2l_f1510_b1024 | 576 | 2 | 15,10 | 1024 | fp32 | não | 8 | 0,681 | 0,582 | 1.321,8 | 1.610,0 | 0,76 |
| mvp408_3l_f1510_b1024 | 408 | 3 | 15,10,10 | 1024 | fp32 | não | 8 | 1,457 | 1,257 | 3.284,4 | 5.438,0 | 0,18 |
| mvp408_3l_f1510_b1024_ckpt | 408 | 3 | 15,10,10 | 1024 | fp32 | sim | 8 | 1,779 | 1,468 | 1.977,7 | 3.110,0 | 0,53 |
| mvp576_2l_f10_b512_amp | 576 | 2 | 10,10 | 512 | amp | não | 8 | 0,376 | 0,344 | 416,2 | 824,0 | 0,88 |
| mvp408_3l_f1510_b512_amp | 408 | 3 | 15,10,10 | 512 | amp | não | 8 | 1,152 | 1,061 | 1.473,8 | 2.386,0 | 0,64 |
| mvp576_2l_f1510_b1024_amp | 576 | 2 | 15,10 | 1024 | amp | não | 8 | 0,585 | 0,544 | 692,4 | 830,0 | 0,88 |
| mvp408_3l_f1510_b1024_amp | 408 | 3 | 15,10,10 | 1024 | amp | não | 8 | 1,405 | 1,287 | 1.681,4 | 2.168,0 | 0,67 |
| mvp408_3l_f1510_b1024_ckpt_amp | 408 | 3 | 15,10,10 | 1024 | amp | sim | 8 | 2,118 | 1,956 | 1.012,4 | 1.584,0 | 0,76 |

Margem mínima = menor margem entre o pico alocado e o reservado pelo allocator,
sob o teto de 6,5 GB (6.656 MiB) exigido pelo gate.

## Envelope dos 12 trials congelados do R07

Regra declarada: cada trial é limitado por dominância (mesmo dim/camadas, fanout e
batch maiores ou iguais) pela configuração medida; a precisão/checkpoint vem da
primeira combinação viável na ordem declarada (fp32 → fp32+checkpoint → amp →
amp+checkpoint), sempre com margem ≥ 25% sob o teto no pico alocado **e** no
reservado.

| Trial | Dim | Camadas | Fanout | Batch | Config limitante | Pico aloc. (MiB) | Pico res. (MiB) | Margem mín. | Recomendação |
|---|---|---|---|---|---|---|---|---|---|
| T01 | 576 | 2 | 10,10 | 512 | mvp576_2l_f10_b512 | 772,5 | 1.582,0 | 0,76 | fp32 |
| T02 | 576 | 2 | 10,10 | 512 | mvp576_2l_f10_b512 | 772,5 | 1.582,0 | 0,76 | fp32 |
| T03 | 408 | 3 | 15,10,10 | 1024 | mvp408_3l_f1510_b1024_ckpt | 1.977,7 | 3.110,0 | 0,53 | fp32 + checkpoint |
| T04 | 408 | 3 | 15,10,10 | 1024 | mvp408_3l_f1510_b1024_ckpt | 1.977,7 | 3.110,0 | 0,53 | fp32 + checkpoint |
| T05 | 576 | 2 | 10,10 | 1024 | mvp576_2l_f1510_b1024 | 1.321,8 | 1.610,0 | 0,76 | fp32 |
| T06 | 576 | 2 | 10,10 | 512 | mvp576_2l_f10_b512 | 772,5 | 1.582,0 | 0,76 | fp32 |
| T07 | 408 | 3 | 15,10,10 | 512 | mvp408_3l_f1510_b1024_ckpt | 1.977,7 | 3.110,0 | 0,53 | fp32 + checkpoint |
| T08 | 408 | 3 | 15,10,10 | 1024 | mvp408_3l_f1510_b1024_ckpt | 1.977,7 | 3.110,0 | 0,53 | fp32 + checkpoint |
| T09 | 576 | 2 | 15,10 | 1024 | mvp576_2l_f1510_b1024 | 1.321,8 | 1.610,0 | 0,76 | fp32 |
| T10 | 408 | 3 | 10,10,10 | 512 | mvp408_3l_f1510_b1024_ckpt | 1.977,7 | 3.110,0 | 0,53 | fp32 + checkpoint |
| T11 | 576 | 2 | 15,10 | 512 | mvp576_2l_f1510_b1024 | 1.321,8 | 1.610,0 | 0,76 | fp32 |
| T12 | 408 | 3 | 10,10,10 | 1024 | mvp408_3l_f1510_b1024_ckpt | 1.977,7 | 3.110,0 | 0,53 | fp32 + checkpoint |

Conclusão do envelope: todos os 12 trials cabem abaixo de 6,5 GB de pico, sem OOM,
com margem ≥ 0,53; nenhum trial congelado precisou de mudança de fanout/batch. Os
trials de 3 camadas usam o modo `checkpoint` como medida de recursos (a
matemática é preservada; equivalência medida abaixo).

## Achados principais

- **OOM real e sua causa.** A primeira medição do formato pesado (408, 3 camadas,
  fanout 15,10,10, batch 1024) **falhou com OOM** em fp32 sem checkpoint: o pico
  alocado era modesto (3.284,4 MiB), mas o **reservado pelo allocator** chegou a
  ~5,4 GB, e a fragmentação impediu novas alocações. Por isso a calibração passou
  a registrar e exigir margem sobre o pico reservado, e o formato pesado foi
  remapeado para `checkpoint` (1.977,7 MiB alocados / 3.110,0 MiB reservados).
- **Gargalo é CPU, não GPU.** No ponto escolhido, o passo médio é 0,345 s, dos
  quais 0,269 s (78%) são neighbor sampling em CPU (Python/numpy) e apenas
  0,076 s são compute de GPU. O throughput futuro depende mais de workers de
  dados do que de VRAM.
- **Época: estimativa comparada à medição.** Para o ponto escolhido, a projeção a
  partir dos 10 primeiros passos (mediana) é 22,69 s e a época medida (46 passos)
  é 22,80 s — erro relativo 0,54% (tolerância declarada 25%).
- **Reprodutibilidade de workers.** Os lotes amostrados são idênticos com
  `num_workers` 0 e 2 (hashes SHA-256 iguais em 4 itens, 16 CPUs), confirmando
  neighbor sampling determinístico por índice.
- **Mixed precision.** bfloat16 vs fp32: perda média 70,907390 contra 71,232818,
  diferença relativa 0,004568 (tolerância 0,01); o modo amp reduz o pico do pior
  caso a 1.012,4 MiB com checkpoint.
- **Checkpoint preserva a matemática.** Com dropout 0 e avaliação, a diferença
  relativa entre o modo normal e o modo checkpoint é 0,0 (4 lotes); em treino o
  modo é aplicado por trial conforme o envelope.

## Ponto escolhido para o treino completo

`mvp576_2l_f10_b512` (dim 576, 2 camadas, fanout 10,10, batch 512, fp32, sem
checkpoint): 772,5 MiB alocados, 1.582,0 MiB reservados, margem mínima 0,76,
passo 0,455 s em regime curto e 0,495 s por época. Regra de escolha apenas de
recursos (maior margem mínima; desempate por menor tempo/passo).

## Arquivos, comandos e validação

- `tools/resource_smoke.py` (grid pré-declarado, medições, envelope, check);
- `tests/test_resource_smoke.py` (10 casos: grid, espelho do R07, época,
  dominância/envelope, check válido e adulterado, workers, checkpoint, fontes);
- `artifacts/reports/M04-RECURSOS.md` e `.json`;
- refactor mínimo em `tools/gnn_graphsage.py`: parâmetro `checkpoint` opcional em
  `forward_sampled` (padrão desligado; 13+9 testes de M02/M03 preservados) e
  índices de aresta içados para fora do laço de camadas;
- checagem M04 no `tools/validate_research.py`.

Comandos: `.venv/bin/python tools/resource_smoke.py run --device cuda --workdir
runs/m04 --report artifacts/reports/M04-RECURSOS.json` (177,5 s), o `check`
correspondente, `.venv/bin/python -m pytest tests/test_resource_smoke.py -q`
(10 casos) e a suíte completa em `tests/`.
