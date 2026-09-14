# Adapter selado de avaliação (H04)

Implementado em 2026-09-14 como módulo do **custodiante**
(`tools/sealed_evaluator.py`). Recebe predições por IDs opacos, valida o label
schema e a cobertura/crosswalk e devolve **apenas** métricas agregadas no schema
R06. Nenhum rótulo por neurônio é exposto ao executor de treino, e o módulo não
foi executado com labels reais — eles ainda não existem (H07); os testes usam
fixtures sintéticas.

## 1. Separação de papéis (limitação declarada)

- A fase deve rodar em sessão separada do executor de treino, com firewall
  armado e sem rede; aqui ela foi implementada pela IA executora em módulo
  isolado, sem acesso a `data/sealed/` real.
- Revisor humano e custodiante independente continuam recomendados antes de
  M08; a separação atual é procedural e está registrada em `FIREWALL.md` e
  `HANDOFF-CUSTODIAN.md`.

## 2. Label schema validado

- Obrigatórios: `label_schema_version` (`1.0`), `crosswalk_version`, `queries`,
  `gallery`, `crosswalk`.
- `queries[qid]`: `status` em `known | unknown | missing | ambiguous |
  conflicting`; `known` exige `type_t0` existente na galeria; IDs opacos
  `q<16 hex>`.
- `gallery[gid]`: `g<16 hex>` → tipo harmonizado não vazio.
- `crosswalk`: todo alvo precisa existir na galeria (checagem de cobertura).
- Falhas de schema, cobertura ou galeria interrompem a avaliação sem produzir
  métricas.

## 3. Agregação segura

- Entrada: uma ou mais predições (uma por seed), baseline obrigatório,
  controle degree-matched obrigatório e a métrica within-source já calculada na
  fonte.
- Saída: `metrics.json` no schema R06, com `inputs.predictions_sha256` e
  **`inputs.label_set_sha256`** (hash do label set registrado), contagens por
  status, métrica primária com IC 95% por bootstrap agrupado por tipo, Δ pareado
  com o melhor baseline, sensibilidade balanceada (K=10), open-set
  (AUROC/AUPR/FPR@TPR95), calibração Brier/ECE (15 bins, temperatura congelada),
  gap within-vs-cross, secundárias e p-valores por permutação (rotação de tipos
  na galeria), com família Holm de tamanho 3.
- Logs: a CLI imprime apenas hash do label set, contagens e número de classes;
  um teste verifica que nenhum `q<hex>` aparece em stdout/stderr.

## 4. Testes (5 casos)

- Métricas válidas no schema R06 e SESOI detectado quando o encoder supera o
  baseline; hash do label set correto; falha por cobertura incompleta; falha
  por `status` inválido; CLI sem vazamento de IDs de consulta.

## 5. Comandos

```bash
.venv/bin/python tools/sealed_evaluator.py \
  --predictions runs/m06/pred-seed1.json runs/m06/pred-seed2.json \
  --labels data/sealed/target-labels/labels.json \
  --baseline runs/baselines/degree-seed1.json runs/baselines/degree-seed2.json \
  --degree-matched runs/baselines/degree-matched-seed1.json runs/baselines/degree-matched-seed2.json \
  --within 0.42 --temperature 1.0 --out runs/m08/metrics.json
.venv/bin/python -m pytest tests/test_sealed_evaluator.py -q
```

## 6. Limitações

- Calibração usa aproximação top-1 (o pacote público traz top-10, não a
  distribuição completa); o valor é conservador e documentado.
- IC da sensibilidade balanceada e do degree-matched usam o bootstrap pareado
  das seeds; amostras reais exigem K e contagens do H07.
- A avaliação real única (M08) depende do crosswalk selado, do pré-registro e
  de custodiante separado.
