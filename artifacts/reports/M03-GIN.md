# GIN comparável ao GraphSAGE (M03)

Executado em 2026-09-15, em modo **exploratório** (condições do G5), somente na
fonte e sem nenhum dado do alvo. O encoder GIN foi implementado sob o **mesmo
harness** de M01/M02 (features de H05, mesmo neighbor sampling, mesmo
decoder/loss e mesmos testes) e pareado em parâmetros com o grid emendado.
O smoke no grafo real **divergiu** por soma não normalizada; a incompatibilidade
é explicitada conforme R07 §4, sem silenciá-la nem adicionar features extras.

## 1. Pareamento com o GraphSAGE (mesmo orçamento, mesma dimensão)

| Camadas | GraphSAGE (trial do grid) | GIN pareado | Δ parâmetros | Fanout/dropout |
|---|---|---|---|---|
| 2 | T01 dim 576 — 1.009.152 | dim 578 — 1.008.034 | 1.118 (0,11%) | (10, 10) / 0,1 |
| 3 | T03 dim 408 — 1.009.800 | dim 448 — 1.008.899 | 901 (0,09%) | (15, 10, 10) / 0,1 |

Ambos dentro do intervalo de 1–3M; contagens exatas conferidas contra fórmula
fechada. O dim do GIN é maior porque o MLP interno consome mais parâmetros por
unidade de dimensão — diferença inevitável registrada.

## 2. Diferenças inevitáveis (registradas)

- **Soma sem normalização** em vez de média ponderada: mensagens crescem com o
  grau; a escala não é invariante à densidade.
- **Peso binário** (variante pré-registrada de H06) como peso de mensagem: a soma
  do GIN pressupõe arestas sem peso (L06/M-10). Com peso **bruto** houve
  divergência numérica (loss 2,1e23 na primeira execução), registrada como run
  descartada; o objetivo (existência + log1p do peso bruto) e o decoder
  permanecem os mesmos.
- **MLP interno (Linear→ReLU→Linear)** no lugar das três projeções lineares.
- **epsilon aprendível** por camada (1 parâmetro extra por camada).
- **Direção por duas somas separadas** (entrada/saída), adaptação explícita — o
  GIN original não define direção.

## 3. Verificações na fixture (contratos de M02)

- Overfit controlado: AUC de treino **0,994318** (dim 16, 2 camadas, 4.000
  passos, lr 1e-3 — a soma exige ~4× mais passos que a média), loss 86,211990 →
  0,117320; gradientes finitos.
- Determinismo: mesma seed ⇒ embeddings idênticos; serialização com diferença
  0,0 e configuração restaurada.
- Nenhuma tabela por node ID; nenhuma dependência do número de nós.
- A soma ponderada difere da média no fixture (teste dedicado), confirmando que
  a ablação de agregação é real.

## 4. Smoke no grafo completo: divergência registrada

Com o peso binário, o GIN pareado (3 camadas, dim 448) **divergiu** no grafo
denso: loss inicial 5,1e12 e final 3,8e12 em 10 passos (critério declarado:
não finito, crescimento >10× ou magnitude inicial >1e6). Com peso bruto, a
divergência é ainda maior (2,1e23). A run bruta foi descartada e mantida no
registro. Consequência: `usable_in_m05_as_implemented = false`; uma variante
normalizada (LayerNorm/grau) mudaria arquitetura e orçamento e exige decisão
humana (G5, condição 6). O R07 §4 prevê exatamente este desfecho: relatar a
incompatibilidade com direção/peso, não silenciá-la.

## 5. Recursos e limitações

- Relatório: 70,1 s (fixture 4.000 passos ×2 + dois smokes), pico de 2,35 GB.
- Smoke binário: 13,5 s em CUDA (pico 1.778,7 MiB de VRAM, dentro do teto de
  6,5 GB); 286.509 arestas amostradas na última camada para 64 alvos.
- Limitações: o GIN não é utilizável como candidato no M05 sem uma decisão sobre
  normalização; os contrastes de escala entre arquiteturas são intrínsecos;
  resultados internos à fonte e exploratórios, sem claim de transferência.
