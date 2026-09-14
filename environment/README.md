# Ambiente reprodutível (R02)

Instalação fixada em 2026-09-14 para a máquina-alvo do projeto. O ambiente é
um `venv` local (`.venv/`, ignorado pelo Git) reproduzido a partir do **lock**
`environment/requirements.lock`; o diagnóstico é
`tools/check_environment.py` e o relatório medido fica em
`../artifacts/reports/AMBIENTE-R02.md`.

## 1. Requisitos

- Linux x86_64 (testado em Pop!_OS 24.04 LTS, kernel 7.1.5).
- Python 3.12.2 (CPython) — versão fixada pelo lock.
- Driver NVIDIA ≥ 580 (testado: 580.173.02) para a RTX 4060 Laptop de 8.188 MiB
  (compute capability 8.9); o runtime CUDA 13.0 vem nos wheels do PyTorch.
- Disco: ~6 GB para o venv; o host tem 23,2 GiB livres — ingestão completa de
  BANC/MCNS exige armazenamento externo (D09/G2).
- Nenhuma GPU é usada fora do smoke de segundos; nenhum serviço pago ou conta.

## 2. Instalação (Linux/CUDA)

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r environment/requirements.lock
.venv/bin/python tools/check_environment.py --json-out artifacts/reports/AMBIENTE-R02.json
```

O script imprime o JSON de diagnóstico, grava o arquivo de métricas e falha com
código 1 se `torch.cuda.is_available()` ou a multiplicação de matrizes mínima na
GPU não passarem. O lock contém os 40 pacotes resolvidos (diretos e
transitivos), incluindo os wheels `nvidia-*` do CUDA 13.0.

## 3. Dependências, justificativa e licença

| Pacote | Versão | Licença (metadado do pacote) | Justificativa |
|---|---|---|---|
| numpy | 2.5.3 | BSD-3-Clause e outras permissivas | álgebra e arrays do pré-processamento (D09/H01) |
| scipy | 1.18.1 | BSD (OSI) | esparsos COO/CSR e estatística (B04/B07) |
| pandas | 3.0.5 | BSD 3-Clause | tabelas colunares dos adapters (H02/H03) |
| pyarrow | 25.0.1 | Apache-2.0 | Feather/Parquet e `mmap` (D09/H01) |
| torch | 2.14.0+cu130 | BSD-3-Clause/MIT/Apache-2.0 (expressão agregada) | encoder e baselines neurais (METHODS.md, L06; licença confirmada na instalação) |
| pytest | 9.1.1 | MIT | testes automatizados das fases R03+ |
| pip | 26.2.1 | MIT | instalador; não entra no lock |

- Não instalar PyG/DGL agora: sem uso imediato e proibição de framework pesado
  sem uso aprovado; entram quando M02/M03 abrirem, com justificativa própria.
- Driver NVIDIA é proprietário e não é redistribuído; o runtime CUDA vem nos
  wheels do PyTorch sob as licenças acima.

## 4. Regra de atualização

- O lock é a única fonte de verdade das versões; instalar/atualizar algo fora
  dele é proibido sem novo registro.
- Atualização exige: novo lock gerado em venv limpo, nota de motivo e impacto,
  reexecução do diagnóstico e registro em evidência de fase.
- O lock não tem hashes de wheel (limitação registrada); R03 pode evoluir para
  `pip install --require-hashes` quando o download idempotente for implementado.

## 5. Limitações

- Reprodução verificada por resolução em venv vazio e smoke CUDA local; uma
  instalação byte a byte em outra máquina só é exigida em P02.
- Sem CUDA toolkit de sistema: o runtime é o dos wheels, suficiente para o
  escopo do plano.
- Sem contêiner: o isolamento é o `venv`; a versão do sistema operacional e do
  driver fica registrada no relatório e deve ser conferida em P02.
