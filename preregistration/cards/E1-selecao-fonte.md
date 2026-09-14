# Experiment card — E1: seleção de modelo somente na fonte (M05)

## Pergunta e status

- Trilha: `confirmatória`
- Hipótese: o espaço congelado contém uma configuração estável que generaliza
  dentro da fonte sem qualquer sinal do alvo.
- Alteração em relação ao pré-registro: nenhuma (minuta R07).
- Dependências aprovadas: G2, R03–R06, H02 (adapter da fonte).

## Dados

- Fonte(s), releases e hashes: MANC `manc:v1.2.1`; manifests em
  `data/manifests/manc-v1.0.json`; SHA-256 no download.
- Alvo, release e hash público: não usado nesta etapa.
- Hash dos rótulos selados: não se aplica.
- População/classe incluída: neurônios da fonte com tipo harmonizado.
- Exclusões e justificativas: mesmas regras do pré-registro (missing, ambíguo,
  conflitante); nenhuma exclusão orientada por score.
- Crosswalk versionado: `CROSSWALK-AUDIT.md` aprovado (D08).

## Informação permitida

- Node features: derivadas de topologia, source-fit.
- Edge features: direção e peso (contagem de sinapses).
- Informação proibida: tipo como feature, região, posição, neurotransmissor,
  morfologia, IDs numéricos.
- Transformações ajustadas somente em: fonte (fit/transform congelado).

## Método

- Baseline/modelo e número exato de parâmetros: GraphSAGE e GIN (1–3M;
  contagem exata registrada por trial) e MLP de controle.
- Objetivo/decoder e negativos: masked edge/weight com negativos
  degree/distance-matched (M01).
- Sampling/batch/precision: fanouts do grid; batch e precisão do trial.
- Espaço e orçamento de hiperparâmetros: 12 trials fixados na seção 5 do
  pré-registro; sem sweep aberto.
- Critério de seleção sem alvo: Macro Recall@1 de validação congruente na
  fonte, mediana das 3 seeds de seleção.
- Seeds: 297979363399525401, 1699981902186354598, 3729859090210297070
  (seleção); finais distintas (seção 6 do pré-registro).

## Avaliação

- Métrica primária e direção: mesma do MVP, apenas dentro da fonte.
- Menor efeito relevante: não se aplica à seleção; usado para ranking.
- Métricas secundárias: Recall@5/10, MRR, MAP, macro-F1, balanced accuracy.
- Unidade de reamostragem/inferência: tipos.
- Open-set e calibração: não avaliados nesta etapa.
- Controles negativos e de atalhos: permutação de rótulos, shuffle de IDs/ordem,
  degree-only.

## Orçamento e parada

- Tempo/VRAM/RAM/disco máximos: piloto ≤ 30 min por trial; pico ≤ 6,5 GB VRAM;
  disco conforme D09.
- Critério de early stop: paciência 20 épocas, máximo 200.
- Critério go/no-go: ≥ 1 configuração estável (sem OOM e dentro do teto);
  nenhuma orientação pelo alvo.

## Artefatos esperados

- Configuração congelada: `artifacts/frozen/` (M06).
- Métricas estruturadas: ledger de trials (inclusive falhos) em `runs/`.
- Testes/validações: RUN-MANIFEST e schema de predições.
- Figura/tabela gerada: curva de treino por trial e ranking source-only.
