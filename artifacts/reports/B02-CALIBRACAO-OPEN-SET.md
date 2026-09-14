# Calibração, open-set e incerteza (B02)

Implementado em 2026-09-14. `tools/calibration.py`: funções puras, sem I/O e sem
labels reais, para Brier multiclasse, ECE com bins fixos e tabela de
confiabilidade, AUROC/AUPR, FPR@TPR pré-fixada, bootstrap agrupado e permutação
por troca de sinal com seed registrada. O limiar de rejeição é aprendido
**somente na fonte** e aplicado depois sem refit.

## 1. Convenções fixadas

- **Scores de open-set = confiança de ser conhecido** (maior = mais conhecido);
  AUROC/AUPR tratam known como positivo e unknown como negativo; a FPR é a
  fração de unknown aceitos no limiar que garante a TPR pedida em known.
- **Empates:** contam 0,5 no AUROC e mantêm ordem estável no AUPR; bins de
  confiança usam `int(conf × bins)` limitado a `bins-1`; bins fixos em 15 por
  padrão (R06).
- **Seed registrada:** `bootstrap_ci_grouped` e `permutation_p_sign_flip`
  retornam a seed usada (padrão `20260914`) e são determinísticas para a mesma
  seed.
- **Limiar somente na fonte:** `fit_threshold_source` retorna
  `fitted_on: "source"`; `apply_threshold` nunca reajusta.

## 2. Fixtures com valores esperados (testes)

| Fixture | Métrica conferida |
|---|---|
| Perfeita (probabilidades 1/0) | Brier 0,0 |
| Não calibrada (0,9/0,9/0,6) | ECE (2 bins) 0,133333; confiança média 0,8 e acurácia 0,666667 |
| Desbalanceada (100 knowns vs 2 unknowns; Brier com 3 queries) | AUROC/AUPR 1,0; Brier 0,34 |
| Degenerada (scores todos 0,5) | AUROC 0,5; AUPR 0,0 sem positivos |
| FPR@TPR: 20 positivos 0,05–1,00, negativos 0,02/0,03 | TPR ≥ 0,95 com FPR 0,0; negativo alto implica FPR 1,0 |
| Bootstrap agrupado (A=1, B=0, C=2/3) | ponto 0,555556; mesmo CI para a mesma seed |
| Permutação | zeros → p = 1,0; cinco sinais fortes → p < 0,2 |

## 3. Testes e recursos

- `tests/test_calibration.py`: 10 casos (perfeita, não calibrada, desbalanceada,
  degenerada, FPR@TPR, bootstrap com seed, permutação, limiar só na fonte e
  ausência de I/O).
- Recursos: CPU apenas, milissegundos, sem GPU, sem downloads e sem abrir
  arquivos (teste intercepta `builtins.open`).

## 4. Limitações

- A calibração de temperatura e o ajuste de limiar para o alvo acontecem apenas
  na fonte/desenvolvimento; qualquer refit no alvo é proibido (R06).
- As funções não conhecem os IDs opacos nem o selado; a integração final é do
  avaliador (H04/M08).
