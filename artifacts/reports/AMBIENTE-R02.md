# Relatório de compatibilidade — ambiente e RTX 4060 (R02)

Medido em 2026-09-14 pelo executor. Métricas brutas geradas por
`python3 tools/check_environment.py --json-out artifacts/reports/AMBIENTE-R02.json`
(rodado com `.venv/bin/python`); esta tabela transcreve esse JSON. Nenhuma GPU
foi usada além do smoke de segundos; nenhum dado de dataset foi baixado.

## 1. Sistema e interpretador

| Item | Valor medido |
|---|---|
| Distro | Pop!_OS 24.04 LTS (x86_64) |
| Kernel | 7.1.5-76070105-generic |
| Python | 3.12.2 (CPython), `venv` = true |
| Executável | `.venv/bin/python` (relativo à raiz do projeto) |
| Disco | 459,5 GiB total, **23,2 GiB livres** |
| Memória | 31,0 GiB total, 13,7 GiB disponíveis no momento |

## 2. Hardware-alvo

| Item | Valor medido | Confere com o ESCOPO? |
|---|---|---|
| GPU | NVIDIA GeForce RTX 4060 Laptop GPU | sim |
| VRAM | 8.188 MiB | sim (8 GB) |
| Driver | 580.173.02 | — |
| Compute capability | 8.9 | — |
| CPU | 13th Gen Intel Core i7-13620H, 16 lógicos | sim |
| RAM | ~32 GiB | sim |

## 3. Operação CUDA mínima

| Item | Valor medido |
|---|---|
| `torch` | 2.14.0+cu130 (runtime CUDA 13.0 nos wheels) |
| `torch.cuda.is_available()` | true |
| Dispositivo | NVIDIA GeForce RTX 4060 Laptop GPU |
| Multiplicação 1024×1024 | 0,1403 s, resultado finito |
| VRAM alocada / reservada no smoke | 16,1 MiB / 42,0 MiB |
| Pico de RSS do diagnóstico | 826,8 MiB |
| Tempo total do diagnóstico | 2,93 s |

Tetos do PROTOCOLO respeitados com folga: smoke ≪ 5 min e ≪ 2 GB de VRAM.

## 4. Dependências, licenças e justificativa

| Pacote | Versão | Licença (metadado) |
|---|---|---|
| numpy | 2.5.3 | BSD-3-Clause e outras permissivas |
| scipy | 1.18.1 | BSD (OSI) |
| pandas | 3.0.5 | BSD 3-Clause |
| pyarrow | 25.0.1 | Apache-2.0 |
| torch | 2.14.0 | BSD-3-Clause/MIT/Apache-2.0 (expressão agregada) |
| pytest | 9.1.1 | MIT |
| pip | 26.2.1 | MIT |

Justificativas: pilha numérica/colunar do pré-processamento (numpy, scipy,
pandas, pyarrow) e encoder/baselines neurais (torch) previstos em
`research/literature/METHODS.md` (L06); `pytest` para os testes das fases
seguintes. PyG/DGL **não** foram instalados por não terem uso imediato.
Detalhes e política de atualização em `environment/README.md`.

## 5. Verificação de instalação limpa

- `environment/requirements.lock` tem 40 pinos derivados do venv instalado do
  zero (`.venv/`, ignorado pelo Git, 5,8 GB).
- Um venv vazio em `/tmp` resolveu o lock com `pip install --dry-run -r
  environment/requirements.lock` em 11,4 s, sem erro e sem download de wheels.
- Instalação byte a byte em outra máquina fica para P02 (reprodução do zero).

## 6. Falhas, descartes e limitações

- Nenhuma falha de instalação ou de CUDA; nenhum run descartado.
- O lock não fixa hashes de wheel (limitação registrada; evolução possível em
  R03 com `--require-hashes`).
- Disco é o recurso mais apertado: 23,2 GiB livres contra BANC (17,15 GB) e
  MCNS (31,32 GB) completos; ingestão integral continua condicionada a
  armazenamento externo (D09/G2).
- Driver NVIDIA proprietário fora do Git e não redistribuído.
