# Implementação única de métricas de retrieval/classificação (B01)

Implementada em 2026-09-14. `tools/metrics.py` é a única implementação pública
de métricas do projeto: funções puras, sem I/O, sem dependências externas e sem
qualquer acesso a labels reais do alvo (recebe predições e rótulos sintéticos ou
da fonte).

## 1. API

| Função | Saída |
|---|---|
| `rank_from_scores(scores, higher_is_better)` | listas ordenadas por score; empates desfeitos por rótulo (ordem alfabética) |
| `recall_at_k(ranked, gold, k)` | macro por classe, micro por query, classes, contagens e recall por classe |
| `mean_reciprocal_rank(ranked, gold)` | MRR (multi-instance usa o primeiro gold) |
| `average_precision(ranked, gold)` | MAP com relevantes múltiplos |
| `top_k_accuracy(ranked, gold, k)` | acurácia top-k |
| `macro_f1(ranked, gold)` | F1 macro em top-1 (multi-instance conta acerto) |
| `balanced_accuracy(ranked, gold)` | acurácia balanceada (= macro Recall@1) |
| `evaluate(ranked, gold, k_values)` | pacote completo com contagens |

## 2. Regras fixadas

- **Orientação:** `higher_is_better=True` para scores (similaridade), `False`
  para distâncias; a chamada escolhe explicitamente e o teste mostra a inversão.
- **Empates:** sempre desfeitos pelo rótulo em ordem alfabética (determinístico).
- **Classes ausentes:** entram no denominador macro com recall 0.
- **Multi-instance:** acerto se qualquer gold aparece no top-k; MAP usa as
  precisões em cada posição relevante.
- **Query sem match:** excluída das métricas e contada em `queries_unmatched`.
- **Macro vs micro:** macro pondera classes igualmente; micro pondera queries.

## 3. Exemplo calculado à mão (canônico dos testes)

4 queries, 3 classes, ranked `[A,B,C]×3` e `[B,A,C]`, gold `A,B,C,A`:

| Métrica | Valor conferido |
|---|---|
| Recall@1 macro / micro | 0,166667 / 0,25 |
| Recall@5 macro / micro | 1,0 / 1,0 |
| MRR / MAP | 0,583333 / 0,583333 |
| Top-1 / Top-5 accuracy | 0,25 / 1,0 |
| Macro-F1 | 0,133333 |
| Balanced accuracy | 0,166667 |

Também cobertos: empates e orientação, classes ausentes, multi-instance, query
sem match e a garantia de que nenhuma função abre arquivos (teste intercepta
`builtins.open`).

## 4. Testes e recursos

- `tests/test_metrics.py`: 7 casos (exemplo à mão, empates/orientação, classes
  ausentes, multi-instance, sem match, ausência de I/O e gold inválido).
- Recursos: CPU apenas, milissegundos, sem GPU, sem downloads e sem leitura de
  arquivos em tempo de execução.

## 5. Limitações

- Métricas dependem de listas ranqueadas completas fornecidas pelo chamador; a
  integração com predições seladas (IDs opacos) fica com o avaliador (H04/R06).
- Calibração, open-set e incerteza pertencem a B02.
