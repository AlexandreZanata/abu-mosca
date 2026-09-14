# Contrato de configuração, run e determinismo (R04)

Implementado em 2026-09-14. Elimina parâmetros escondidos e resultados sem
linhagem: toda opção efetiva é serializada, toda seed deriva de uma seed mestra,
e cada execução produz um `RUN-MANIFEST` imutável com Git, ambiente, recursos e
hashes das saídas. Nenhum treino real foi executado; a fixture é sintética.

## 1. Configuração

- Schema: `schemas/run-config.schema.json` (draft 2020-12, sem campos extras).
- Campos: `experiment` (`[a-z0-9-]+`), `seed` (inteiro 0–2⁶³−1), `params`
  (`n_bytes` 1–1.000.000, `repeats` 1–64) e `notes` opcional.
- Defaults documentados e sempre serializados: `n_bytes = 4096`,
  `repeats = 2`; `tools/run.py` preenche e grava a configuração resolvida, de
  modo que nenhum parâmetro efetivo fica implícito.
- Exemplo versionado: `configs/fixture.json`.

## 2. run_id, seeds e determinismo

- `run_id = sha256(canonical(config resolvida) + commit do Git + versão da
  ferramenta)[:16]`; mesmo código e mesma configuração geram o mesmo ID.
- Seeds centralizadas em `tools/seeds.py`: `derive_seed(mestre, contexto…)`
  usa SHA-256 e não depende de relógio nem de máquina. Toda seed derivada usada
  é registrada no manifesto (`seeds.derived`).
- O `created_at` (timestamp) é registrado apenas para linhagem e **nunca** entra
  como seed ou conteúdo de saída; teste cobre isso trocando o relógio.
- Tolerância numérica: **zero** (igualdade exata). A fixture usa inteiros e
  hashes; qualquer operação de ponto flutuante futura precisará declarar
  tolerância aqui antes de ser considerada determinística.

## 3. RUN-MANIFEST

- Schema: `schemas/run-manifest.schema.json`; gravado em
  `runs/<run_id>/manifest.json` (diretório ignorado pelo Git).
- Campos: `run_id`, `created_at`, `tool`, `config` resolvida, `config_sha256`,
  `code` (`git_commit`, `git_dirty`, `dirty_diff_sha256`), `environment`
  (Python, plataforma e versões instaladas), `seeds` (mestre e derivadas),
  `resources` (tempo de parede, pico de RSS, disco livre) e `outputs`
  (`path`, `bytes`, `sha256`), além de `status`.
- Exemplo medido (fixture): `run_id=f39e7779b00ad433`, `stream.bin` 8192 bytes
  `sha256=35c06f34…`, `wall_s=0.0005`, `peak_rss_mib=23,03`.

## 4. Cache e imutabilidade

- O run ID é imutável: se `runs/<run_id>/` existe com manifesto e saídas que
  conferem em SHA-256, a execução vira `cached` sem reescrever nada.
- Saída adulterada ou manifesto divergente: erro e **nada é sobrescrito**;
  um diretório de run sem manifesto também bloqueia e exige limpeza manual.
- Configuração ou commit diferentes produzem outro `run_id`; não há colisão
  silenciosa de resultados divergentes.

## 5. Comandos

```bash
.venv/bin/python tools/run.py --config configs/fixture.json
.venv/bin/python tools/run.py --config configs/fixture.json --runs-dir /tmp/opencode/runs-comparacao
.venv/bin/python -m pytest tests/test_run_contract.py -q
```

## 6. Testes

18 casos em `tests/test_run_contract.py`: validação e resolução da configuração,
schema contra código, `run_id` determinístico e sensível ao commit, duas
execuções com saídas idênticas, cache sem reescrita, saída divergente bloqueada,
diretório sem manifesto bloqueado, relógio trocado sem efeito nas saídas,
manifesto completo e seeds centralizadas (18 + 24 anteriores = 42 na suíte).

## 7. Limitações

- A fixture não treina nada; ela prova o contrato de run, não desempenho.
- `git_dirty=true` é esperado enquanto o workstream NEXT mantiver alterações
  locais; o `dirty_diff_sha256` registra o estado exato usado.
- O manifesto captura pacotes instalados de forma best-effort; o lock de R02
  continua sendo a fonte das versões.
- Retomada de run interrompido não é automática: diretório sem manifesto exige
  limpeza manual para preservar a imutabilidade.
- Validação: `python3 tools/validate_research.py`.
