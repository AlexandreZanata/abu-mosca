# Tarefa masked-edge/weight e auditoria de atalhos (M01)

Executado em 2026-09-15, em modo **exploratório** (condições do G5) e somente na
**fonte MANC**, sem nenhum dado do alvo. `tools/ssl_task.py` fixa o objetivo
auto-supervisionado primário do MVP (R07 §4), registra a distribuição de
negativos e mede o atalho de grau com um baseline dedicado, antes de qualquer
treino neural (que começa em M02/M05).

## 1. Especificação da tarefa

| Item | Definição |
|---|---|
| Grafo | snapshot H08 da fonte (23.188 nós, 5.243.574 arestas dirigidas e ponderadas; semântica primária de H06) |
| Máscara | 5% das arestas por hash determinístico (splitmix64 de `u,v` + seed), **com co-mascaramento do reverso** |
| Reverso | se (u,v) é retirado e (v,u) existe, ele também é retirado, para o holdout não reaparecer pela direção contrária |
| Cache | a máscara é recomputada a cada execução a partir da seed (nenhum cache é lido; teste garante reprodutibilidade) |
| Negativos | 5 por positivo, pareados pela **mesma classe de distância** (2 saltos no grafo de treino ou "far") e pela **menor diferença de grau** total (janela determinística) |
| Decoder | duas cabeças bilineares `z_u^T W z_v + b` (existência e peso), **sem nenhuma tabela por node ID** |
| Loss | `BCEWithLogits` de existência (positivos + negativos) + 1,0 × `MSE` sobre **log1p(peso)** nos positivos |
| Métrica SSL | average precision (AP) e AUC de existência nas arestas retiradas, para monitoramento/early stop |
| Seleção | Macro Recall@1 na fonte, conforme o pré-registro (R07 §5); a métrica SSL não substitui a seleção |

## 2. Resultados do smoke (CPU)

| Medida | Valor |
|---|---|
| Arestas de validação (hash inicial + reverso) | 338.135 de 5.243.574 (6,45%) |
| Co-mascaradas por reverso | 75.805 |
| Arestas de treino | 4.905.439 |
| Vazamento de holdout na visão de treino | 0 (frente e reverso) |
| Negativos amostrados (5.000 positivos × 5) | 25.000, com 0 positivos incompletos |
| Pareamento de classe de distância | 100% (24.995 classe 2 e 5 "far") |
| Diferença de grau (log) mediana / p90 | 0,0004 / 0,0017 |
| Baseline de grau — validação **pareada** | AUC 0,554359 / AP 0,192378 |
| Baseline de grau — validação **sem pareamento** | AUC 0,621656 / AP 0,581502 |
| Decoder (smoke) | 514 parâmetros (2·16² + 2), 0 por node, gradientes finitos, loss 25,38 → 0,014 |

## 3. Leitura do atalho de grau

Com negativos pareados por grau e distância, um classificador que usa apenas
grau fica próximo do acaso (AP 0,192 contra prevalência 0,167 e AUC 0,554), mas
não exatamente no acaso: resta um sinal residual pequeno e mensurável. Sem
pareamento, o mesmo baseline mantém AP 0,582 e AUC 0,622 — o atalho existe e é
substancial na distribuição ingênua. Consequência registrada: a GNN deverá ser
comparada ao **baseline de grau na mesma distribuição pareada**, e não apenas ao
acaso; o alvo de M05/M06 é superar esse comparador, não apenas o piso aleatório.

## 4. Verificações

- **Máscara determinística:** mesma seed ⇒ máscara idêntica; seed diferente ⇒
  máscara diferente (teste com hash vetorizado).
- **Separação treino/validação:** nenhuma aresta retirada (nem seu reverso)
  aparece na visão de treino; o teste de vazamento é exercitado com um caso
  sabidamente vazado e falha como esperado.
- **Negativos:** determinísticos, nunca coincidem com arestas verdadeiras nem
  com o próprio nó, com distribuição de grau e classe de distância registrada.
- **Métricas:** AUC/AP conferidas à mão (separação perfeita, invertida e com
  empates) e a loss de peso é conferida em um caso analítico.
- **Sem tabela por node ID:** o decoder não tem `Embedding` nem parâmetro que
  dependa do número de nós (contagem idêntica para dimensões diferentes).
- **Smoke do decoder:** gradientes finitos e loss decrescente em CPU.
- Testes: `tests/test_ssl_task.py` (13 casos) e `python3 tools/ssl_task.py
  check`.

## 5. Recursos e limitações

- Execução: ~32 s com cache quente (~75 s na primeira execução), pico de
  1,90 GiB (CPU), sem GPU e sem downloads.
- Auditoria por amostra declarada (5.000 positivos de validação; 20.000 pares de
  treino do baseline), não pelo grafo inteiro.
- O grafo da fonte é denso: as classes de distância observadas são apenas {2,
  "far"} (nenhum par a 1 salto após o mascaramento); o pareamento por distância
  é exato dentro dessas classes.
- Fonte única e sem réplica biológica; resultados **exploratórios**, limitados à
  fonte observada e sem claim de transferência.
