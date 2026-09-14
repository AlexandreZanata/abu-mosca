# Experiment card — E2: MVP zero-shot MANC → MCNS (M06–M09)

## Pergunta e status

- Trilha: `confirmatória`
- Hipótese: H1 — o encoder small, treinado sem rótulos na fonte, supera o melhor
  baseline simples pré-registrado na recuperação macro por tipo no alvo nunca
  visto, no trilho somente-topologia.
- Alteração em relação ao pré-registro: nenhuma (minuta R07).
- Dependências aprovadas: G2, R03–R06, H02/H03/H05/H06, M01–M05.

## Dados

- Fonte(s), releases e hashes: MANC `manc:v1.2.1` (SHA-256 no download/manifest).
- Alvo, release e hash público: MCNS `male-cns:v1.0`; grafo público apenas em
  inferência; SHA-256 local registrado (sem checksum oficial).
- Hash dos rótulos selados: registrado pelo custodiante em M08/H07; nunca
  exposto ao executor.
- População/classe incluída: T0 com tipo harmonizado na galeria; K = 10 para a
  sensibilidade balanceada.
- Exclusões e justificativas: missing/ambíguo/conflitante fora do T0 com
  contagens; singleton permanece com n = 1; regras congeladas em H07.
- Crosswalk versionado: `CROSSWALK-AUDIT.md` (D08) com dois revisores antes de
  H07 e sensibilidade a rótulos circulares (DEC-CW-03).

## Informação permitida

- Node features: topologia source-fit (graus e padrões de vizinhança).
- Edge features: direção e peso.
- Informação proibida: tipo, região, posição, neurotransmissor, morfologia,
  crosswalk, IDs numéricos; qualquer estatística global do alvo.
- Transformações ajustadas somente em: fonte; aplicadas ao alvo sem refit.

## Método

- Baseline/modelo e número exato de parâmetros: GraphSAGE primário e GIN
  comparável (1–3M; contagem exata no congelamento); MLP de controle
  (≈100k/≈500k/pareado); baselines aleatório, maioria, degree-only e
  estatísticas artesanais.
- Objetivo/decoder e negativos: masked edge/weight com negativos
  degree/distance-matched.
- Sampling/batch/precision: configuração vencedora do grid de 12 trials (E1).
- Espaço e orçamento de hiperparâmetros: congelado; nenhum ajuste pós-alvo.
- Critério de seleção sem alvo: E1 na fonte; pacote congelado em `artifacts/frozen/`.
- Seeds: 1342714389145479246, 8142193368363737116, 495739693416096352,
  8602629889984631926, 7682391451267186339 (5 seeds finais).

## Avaliação

- Métrica primária e direção: Macro Recall@1 no T0; maior é melhor.
- Menor efeito relevante: SESOI = 5 p.p. sobre o melhor baseline simples.
- Métricas secundárias: Recall@5/10, MRR, MAP, macro-F1, balanced accuracy,
  open-set (AUROC/AUPR/FPR@TPR95), Brier/ECE (15 bins), gap within-vs-cross.
- Unidade de reamostragem/inferência: tipos (bootstrap/permutação agrupados);
  nunca o neurônio isolado.
- Open-set e calibração: limiar e temperatura congelados na fonte antes do alvo.
- Controles negativos e de atalhos: permutação de rótulos na fonte e no alvo
  (custodiante), degree-matched, shuffle de IDs/ordem, micro-média diagnóstica.

## Orçamento e parada

- Tempo/VRAM/RAM/disco máximos: treino confirmatório sob teto do G3; pico
  ≤ 6,5 GB VRAM (M04) e ≤ 28 GB RAM (H08).
- Critério de early stop: paciência 20 épocas, máximo 200 (fonte).
- Critério go/no-go: sucesso/parcial/refutado/inconclusivo conforme
  `DESFECHOS-E-FALSIFICACAO.md` e a família Holm de 3 testes.

## Artefatos esperados

- Configuração congelada: encoder, probe, transformações e hashes em
  `artifacts/frozen/`.
- Métricas estruturadas: `metrics.json` no schema R06, produzido pelo
  custodiante em M08.
- Testes/validações: firewall armado, predições sem rótulos, una execução por
  chave lógica.
- Figura/tabela gerada: tabela primária, curvas de calibração e análise
  within-vs-cross.
