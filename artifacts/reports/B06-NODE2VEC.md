# Node2Vec/DeepWalk com caveat transdutivo (B06)

Executado em 2026-09-15, somente na **fonte MANC**, em modo exploratório e sem
nenhum dado do alvo. `tools/node2vec_baseline.py` implementa caminhadas de
primeira ordem (DeepWalk como caso p=q=1, LIT-0050) e de segunda ordem
(Node2Vec com p=1 e q=0,5, LIT-0049) sobre o grafo dirigido e ponderado da
fonte, mais Skip-gram com negativos em CPU determinística. A avaliação usa a
mesma partição, as mesmas seeds e o mesmo avaliador de B01/B03, com probe por
centroide source-fit sobre os embeddings. O veredito desta fase é
**não comparável zero-shot**: embeddings transdutivos vivem em espaços
arbitrários por grafo (M-05/M-06 em L06), e não há mecanismo de alinhamento
não supervisionado permitido e pré-registrado que autorize uso entre grafos.

## 1. Configurações fixas

| Config | p | q | Caminhadas/nó | Comprimento | Janela | Dim | Épocas | Negativos | Lote | Taxa |
|---|---|---|---|---|---|---|---|---|---|---|
| deepwalk | 1,0 | 1,0 | 4 | 25 | 5 | 64 | 2 | 5 | 16384 | 1e-3 |
| node2vec | 1,0 | 0,5 | 4 | 25 | 5 | 64 | 2 | 5 | 16384 | 1e-3 |

Treino por Skip-gram com embeddings esparsos (SparseAdam), CPU em thread
única e algoritmos determinísticos; mesma seed ⇒ mesmas caminhadas e mesmos
embeddings (testado). Nós sem saída encerram a caminhada; pesos de sinapse
ponderam as transições, preservando a semântica de H06.

## 2. Resultados (validação interna, mesma partição de B03–B05)

| Config | Seed 0 macro/micro | Seed 1 macro/micro | Seed 2 macro/micro | Mediana macro |
|---|---|---|---|---|
| deepwalk | 0,163047 / 0,131173 | 0,170178 / 0,138723 | 0,168601 / 0,140296 | **0,168601** |
| node2vec | 0,158941 / 0,127399 | 0,156781 / 0,134319 | 0,163043 / 0,132432 | **0,158941** |

Leitura diagnóstica, sem claim de transferência: as caminhadas superam de
pouco o degree-only (0,150 macro) e ficam bem abaixo das estatísticas
artesanais (0,384) e do MLP (0,580). O viés de segunda ordem (q=0,5) não
adiciona nada sobre p=q=1 neste protocolo — diferença entre medianas abaixo
de um ponto percentual, dentro da variação entre seeds.

## 3. Estabilidade e o caveat transdutivo

- **Permutação:** o carregador ordena os nós canonicamente, de modo que a
  ordem arbitrária da tabela não altera caminhadas nem embeddings (testado).
- **Rotação:** aplicar uma rotação ortogonal aos embeddings preserva as
  decisões do probe em 0,8748 (deepwalk) e 0,8757 (node2vec) dos nós de
  validação. O resíduo vem de empates próximos decididos por ruído de ponto
  flutuante num espaço com centenas de classes, não de quebra da propriedade.
- **Seeds e coordenadas arbitrárias:** sem nenhum alinhamento, a cosseno
  média por nó entre seeds é 0,0124, 0,0789 e −0,0092 (deepwalk) e 0,0117,
  0,0250 e −0,0145 (node2vec) — todas próximas de zero. As coordenadas de
  uma seed não significam nada na outra: comparação direta de coordenadas
  entre espaços independentes é inválida, e nenhum alinhamento com rótulos
  ou correspondências do alvo foi executado (proibição da fase).
- **Proposta de uso entre grafos:** nenhuma. Não existe mecanismo permitido
  e pré-registrado para levar estes espaços ao alvo; o método fica restrito
  a diagnóstico within-source, com baseline de sensibilidade dado pela
  variação entre as 3 seeds acima.

## 4. Verificações

- **Somente fonte:** split, seeds e avaliador idênticos aos de B03; nenhum
  rótulo, score ou arquivo do alvo foi lido em qualquer etapa.
- **Determinístico:** mesma seed ⇒ caminhadas, embeddings e predições
  idênticos (teste ponta a ponta; a seed inicial do run final reproduz o
  piloto descartado bit a bit nas métricas).
- **Smoke em fixture:** grafo sintético de 20 nós treina de ponta a ponta
  em segundos, com métricas no intervalo válido e artefatos hashados.
- Predições congeláveis: `runs/b06/predictions-{deepwalk,node2vec}-seed{0,1,2}.json`
  e embeddings `runs/b06/embeddings-{deepwalk,node2vec}-seed{0,1,2}.npy`,
  todos com SHA-256 registrado no relatório de métricas.

## 5. Recursos e limites

- Execução final: 1434,7 s de processo (2 configs × 3 seeds), pico de 3437 MiB
  (CPU), sem GPU, sem downloads e sem nenhum dado do alvo.
- Calibragem descartada: quatro pilotos de 1 config/1 seed (motivo exclusivo:
  tempo por run acima do teto de 30 min do piloto); a otimização do amostrador,
  os negativos pré-computados e os hiperparâmetros da tabela acima são a
  configuração final, sem nenhuma escolha orientada por métrica.
- Limitações: esforço de treino em escala de piloto (2 épocas); resultados
  internos à fonte e **não** sustentam claim de transferência; o veredito
  **não comparável zero-shot** é o resultado esperado e honesto desta fase.
