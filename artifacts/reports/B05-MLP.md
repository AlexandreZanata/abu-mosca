# MLP de controle sobre as mesmas features (B05)

Executado em 2026-09-14, somente na **fonte MANC**, em modo exploratório e sem
nenhum dado do alvo. `tools/mlp_control.py` treina um MLP sobre as **mesmas
features** artesanais de B04 (11 features somente-topologia), com a mesma
seleção source-only de B03 (split determinístico por hash e as 3 seeds do
pré-registro R07), normalização z-score com ajuste source-fit só no treino e o
mesmo avaliador de B01. O objetivo é isolar o ganho da **não linearidade** do
ganho que um futuro encoder (M02) precisará demonstrar além deste controle.

## 1. Configurações e contagem exata de parâmetros

| Config | Ocultas | Parâmetros exatos | Budget |
|---|---|---|---|
| s | 256, 128 | 102919 | ~100k |
| m | 512, 512 | 535047 | ~500k |
| l | 1024, 768 | 1198599 | pareado-provisório na faixa de 1–3M do encoder |

A contagem é exata (soma dos tensores, conferida contra fórmula fechada em
teste) e inclui a camada de saída para as classes da partição. O pareamento
exato com o encoder fica para M02, quando a arquitetura existir; a config `l`
apenas ocupa a mesma faixa de capacidade para comparação honesta.

## 2. Resultados (validação interna, mesma partição de B03 e B04)

| Config | Seed 0 macro/micro | Seed 1 macro/micro | Seed 2 macro/micro | Mediana macro |
|---|---|---|---|---|
| s | 0,476455 / 0,493866 | 0,472795 / 0,486631 | 0,460429 / 0,482542 | **0,472795** |
| m | 0,554048 / 0,559610 | 0,555326 / 0,554577 | 0,551316 / 0,552375 | **0,554048** |
| l | 0,579626 / 0,577855 | 0,581120 / 0,576282 | 0,576238 / 0,575024 | **0,579626** |

Leitura: o MLP supera o probe linear por centroide sobre as mesmas features
(todas em B04: 0,384 macro) já na config `s`, e o ganho cresce com a
capacidade até 0,580 na config `l`. Isso confirma que a não linearidade
extrai sinal adicional das mesmas features — exatamente o efeito que este
controle existe para medir, antes de qualquer claim sobre GNN.

## 3. Verificações

- **Contagem exata:** cada config tem os parâmetros somados do modelo e
  conferidos contra a fórmula em teste e no próprio run.
- **Mesma seleção source-only:** split determinístico idêntico ao de B03 e
  B04, mesmas seeds do pré-registro e mesmo avaliador (B01).
- **Source-fit:** média/desvio ajustados só no treino e aplicados à
  validação; sem estatística de outro conjunto.
- **Smoke em fixture:** treino mínimo de 5 épocas converge e produz métricas
  no intervalo válido em segundos.
- **Overfit em fixture:** em aglomerados separáveis, o MLP atinge macro
  acima de 0,95 no treino, provando capacidade de ajuste.
- **Determinístico:** mesma seed ⇒ mesmas previsões; threads fixas e
  algoritmos determinísticos no treino em CPU.
- Predições congeláveis: `runs/b05/predictions-mlp-{s,m,l}-seed{0,1,2}.json`
  com SHA-256 registrado no relatório de métricas.

## 4. Recursos e limites

- Execução: cerca de 294 s, pico de 5132 MiB (CPU), sem GPU e sem downloads.
- Limitações: resultados são internos à fonte e **não** sustentam claim de
  transferência; hiperparâmetros fixos (50 épocas, lote 1024, taxa 1e-3, sem
  dropout) sem busca; o pareamento definitivo com o encoder aguarda M02; sem
  nenhum dado do alvo em qualquer etapa.
