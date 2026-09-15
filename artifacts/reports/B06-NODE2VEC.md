# Baselines transdutivos Node2Vec/DeepWalk (B06)

Executado em 2026-09-14/15, somente **dentro da fonte MANC** e em modo
exploratório. Implementa caminhadas de segunda ordem (node2vec, LIT-0049) e de
primeira ordem (deepwalk, p=q=1, LIT-0050) no grafo dirigido e ponderado da
fonte, Skip-gram determinístico com negativos em CPU, e probe por centroide
source-fit com o mesmo split, as mesmas seeds e o mesmo avaliador de B01/B03,
sem nenhum dado do alvo.

**Veredito registrado: `não comparável zero-shot`** — embeddings transdutivos
vivem em espaços arbitrários por grafo; sem mecanismo de alinhamento não
supervisionado permitido e pré-registrado (Procrustes com pares gold é
proibido), não há uso entre grafos.

## 1. Configuração executada

- Configs: `deepwalk` (p=1, q=1) e `node2vec` (p=1, q=0.5); 4 caminhadas/nó, 25
  passos, janela 5, dimensão 64, 2 épocas, 5 negativos, batch 16.384, lr 1e-3,
  CPU com 1 thread determinística; seeds de seleção do pré-registro (3).
- Base: 14.847 nodes, 519 classes (K≥10), split determinístico de B03
  (11.668 treino / 3.179 validação).

## 2. Resultados (validação interna da fonte)

| Config | Macro Recall@1 (mediana) | Por seed | Concordância sob rotação | Cosseno médio entre seeds |
|---|---|---|---|---|
| deepwalk | **0,1686** | 0,1630 / 0,1702 / 0,1686 | 0,875 | 0,012 / 0,079 / −0,009 |
| node2vec | **0,1589** | 0,1589 / 0,1568 / 0,1630 | 0,876 | 0,012 / 0,025 / −0,014 |

Contexto interno (não é comparação confirmatória): degree-only B03 = 0,1495 e
estatísticas artesanais B04 = 0,3837. Os baselines transdutivos ficam próximos
do piso de grau e **abaixo** do extrator artesanal; o cosseno entre seeds é
quase nulo, evidência direta de que cada execução vive em um espaço arbitrário.

## 3. Estabilidade a rotação/permutação

- `rotation_agreement` ≈ 0,875/0,876: girar o espaço por matriz ortogonal
  preserva previsões na maior parte dos nós; as discordâncias vêm de empates
  numéricos no probe (a invariância exata é testada em fixture, onde fica 1,0).
- Permutação de IDs/ordem da tabela: o carregador usa ordem canônica por ID e o
  teste confirma caminhadas/pesos idênticos após embaralhar o arquivo.
- Seeds mudam coordenadas (cosseno baixo) sem mudar o protocolo.

## 4. Artefatos congeláveis

- `runs/b06/predictions-{deepwalk,node2vec}-seed{0,1,2}.json` e
  `embeddings-*.npy` (35 MB no total), com SHA-256 no relatório JSON.
- Métricas brutas: `artifacts/reports/B06-NODE2VEC.json`.

## 5. Recursos e limites

- Computação interna: 1.396,5 s (~23 min), pico de 3.551,6 MiB (CPU, sem GPU).
- Anomalia de parede registrada: o comando ficou ~45.906 s de relógio de parede
  (provável suspensão do host durante a noite); o tempo de CPU/interno é o
  valor usado no orçamento.
- Limitações: espaços não alinhados ⇒ **sem qualquer uso cross-graph como
  zero-shot**; nenhum label, score ou arquivo do alvo foi tocado; resultados são
  internos à fonte e não sustentam claim de transferência.
