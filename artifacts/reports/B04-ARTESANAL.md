# Estatísticas artesanais com probe comum (B04)

Executado em 2026-09-14, somente na **fonte MANC**, em modo exploratório e sem
nenhum dado do alvo. `tools/artisanal_features.py` extrai famílias de features
somente-topologia, aplica o **mesmo probe da fase B03** (z-score source-fit no
treino + centroide mais próximo) e mede cada família isolada e combinada
(ablação). Nenhuma feature proibida (tipo, região, posição, morfologia, label)
entra na matriz.

## 1. Famílias de features (versão 1.0)

| Família | Features |
|---|---|
| degree | `in_degree`, `out_degree`, `weighted_in`, `weighted_out` |
| reciprocity | `reciprocal_weight_ratio`, `reciprocal_count_ratio` |
| clustering | `clustering_undirected` (triângulos não dirigidos / pares de vizinhos) |
| motifs | `feedforward_paths` (in×out), `bottleneck_ratio` |
| neighborhood | `successor_out_degree_mean`, `predecessor_in_degree_mean` |

Feature interrompida e registrada: `directed_triangle_ratio` (o produto esparso
para triângulos dirigidos poderia densificar; fica para uma versão futura com
custo controlado).

## 2. Resultado da ablação (validação interna, mesma partição de B03)

| Família | Macro Recall@1 | Micro Recall@1 |
|---|---|---|
| degree | **0,149547** (= B03, conferência) | 0,135892 |
| reciprocity | 0,026732 | 0,028311 |
| clustering | 0,014742 | 0,018559 |
| motifs | 0,030519 | 0,033029 |
| neighborhood | 0,036956 | 0,040893 |
| **todas** | **0,383676** | 0,353570 |

A ablação identifica as famílias: grau é a assinatura isolada mais forte e a
combinação eleva o macro a 0,384 — sem qualquer feature proibida. Isso
estabelece o comparador artesanal para a GNN e para o MLP (B05).

## 3. Verificações

- **Invariância a IDs/ordem:** teste embaralha nodes e arestas e confirma
  features idênticas por ID.
- **Grafo conhecido:** clustering, reciprocidade, motivos e vizinhança
  conferidos à mão (teste detectou e corrigiu dupla contagem de triângulos).
- **Probe determinístico:** mesmas entradas ⇒ mesmas previsões; empatado por
  nome de classe.
- Predições congeláveis: `runs/b04/predictions-artesanal-all.json` com SHA-256
  no relatório.

## 4. Recursos e limites

- Execução: ~56 s, pico de 5.327 MiB (CPU), sem GPU e sem downloads.
- Limitações: features source-fit e sem peso além dos graus; motivos dirigidos
  restritos; resultados são internos à fonte e não sustentam claim de
  transferência; qualquer escolha de feature após ver o alvo seria exploratória.
