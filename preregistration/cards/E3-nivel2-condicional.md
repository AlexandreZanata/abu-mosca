# Experiment card — E3: ramos condicionais do Nível 2 (S01–S12)

## Pergunta e status

- Trilha: `condicional` — cada ramo só abre conforme o resultado do G6 e o
  orçamento aprovado; análises novas fora daqui são `exploratórias`.
- Hipótese: hipóteses secundárias do ESCOPO (atributos, morfologia, multi-fonte,
  saturação de capacidade, open-set calibrado).
- Alteração em relação ao pré-registro: nenhuma; mudanças via `CHANGELOG.md`.
- Dependências aprovadas: G6 (ramo), M01–M10, H06, D08–D10.

## Dados

- Fonte(s), releases e hashes: MANC (fonte); BANC `v888` reservado como alvo
  confirmatório independente; FlyWire `v783` reserva; hemibrain comparador.
- Alvo, release e hash público: apenas alvos reservados e intocados; nenhum
  reuso do alvo já revelado como confirmação.
- Hash dos rótulos selados: por alvo, sob custódia (H04/H07).
- População/classe incluída: definida por ramo com as mesmas regras do T0.
- Exclusões e justificativas: pré-registradas por ramo, nunca pós-hoc.
- Crosswalk versionado: D08 + dois revisores antes de qualquer mapeamento manual.

## Informação permitida

- Node features: topologia; atributos locais apenas em S03 como ablação
  separada com máscara de missingness.
- Edge features: direção/peso/threshold conforme H06.
- Informação proibida: as mesmas do E2, mais qualquer correspondência gold
  usada como feature.
- Transformações ajustadas somente em: fonte (por ramo, com hashes).

## Método

- Baseline/modelo e número exato de parâmetros: definidos por ramo (S01
  objetivos; S02 arquiteturas; S03 atributos; S04 morfologia; S05 curva de
  capacidade; S06 shift; S07 estrutura; S08 calibração; S09 direção inversa;
  S10 leave-one-connectome-out; S11 consolidação; S12 auditoria adversarial).
- Objetivo/decoder e negativos: por ramo, com controles degree-matched.
- Sampling/batch/precision: por ramo, dentro do teto do G6.
- Espaço e orçamento de hiperparâmetros: por ramo, fixado antes de rodar.
- Critério de seleção sem alvo: source-only; ramos nunca selecionam no alvo.
- Seeds: as seeds finais do E2 por padrão; novas seeds só com registro.

## Avaliação

- Métrica primária e direção: a mesma do E2 por ramo, salvo ramo explicitamente
  definido pelo SAP.
- Menor efeito relevante: SESOI herdado (5 p.p.) quando comparável; ramos
  diagnósticos reportam efeito e IC sem claim de superioridade.
- Métricas secundárias: conforme SAP.
- Unidade de reamostragem/inferência: tipos; agregação por connectoma em S10.
- Open-set e calibração: S08 aprofunda sem refit no alvo.
- Controles negativos e de atalhos: nulos e sensibilidades do E2 por ramo.

## Orçamento e parada

- Tempo/VRAM/RAM/disco máximos: orçamento condicional aprovado no G6/R07.
- Critério de early stop: por ramo, com successive-halving quando previsto.
- Critério go/no-go: ramo só abre se o anterior superar o limiar condicional
  fixado no pré-registro; custo incremental e IC do ganho reportados.

## Artefatos esperados

- Configuração congelada: por ramo em `artifacts/frozen/`.
- Métricas estruturadas: `metrics.json` (R06) por ramo, agregado por connectoma.
- Testes/validações: firewalls, hashes, changelog e auditoria adversarial S12.
- Figura/tabela gerada: por ramo, com incerteza e denominadores visíveis.
