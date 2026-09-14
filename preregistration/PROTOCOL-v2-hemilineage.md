# Pré-registro v2 (minuta) — desfecho por hemilinhagem de desenvolvimento

**Status: MINUTA — assinatura humana pendente e independência do lado do alvo
não confirmada.** Preparada em 2026-09-14 como reformulação da H07 (opção 2 do
responsável). Substitui o desfecho de tipo harmonizado (T0), que fica
**exploratório e inconclusivo por circularidade**. Nenhum score do alvo foi
consultado; nenhum label set foi materializado.

## 1. Pergunta e estimando

- Pergunta: um encoder indutivo pequeno, treinado sem rótulos na conectividade
  da fonte (MANC `manc:v1.2.1`), recupera a **hemilinhagem de desenvolvimento**
  de neurônios em um alvo nunca visto (MCNS `male-cns:v1.0`), no trilho
  somente-topologia?
- Estimando primário: Macro Recall@1 no nível de **hemilinhagem compartilhada**
  (`hemilineage` no MANC ↔ `trumanHl` no MCNS), com galeria congelada por
  hemilinhagem da fonte.
- Declaração: hemilinhagem é rótulo de desenvolvimento, não tipo funcional; a
  conclusão vale para transferência de rótulo de linhagem entre os datasets
  observados.

## 2. Hipóteses

- H1′: o encoder supera o melhor baseline simples pré-registrado em
  recuperação macro por hemilinhagem no alvo. O grafo público do alvo pode ser
  usado **somente em inferência congelada** (topology-only); é proibido usar
  rótulos, crosswalk, morfologia, posição, IDs, tuning ou estatísticas globais
  ajustadas no alvo.
- H0′: após controlar grau, atalhos e incerteza, o encoder não supera o
  baseline por diferença relevante; o desempenho é compatível com estrutura
  trivial, ruído de anotação ou peculiaridades da fonte.

## 3. Métrica, SESOI e cobertura

- Métrica primária: `macro-recall@1-hemilineage` (IC 95% por bootstrap agrupado
  por classe; mediana entre as 5 seeds; SAP/R06 para o restante).
- SESOI: 5 pontos percentuais absolutos sobre o melhor baseline simples; sucesso
  exige Δ ≥ SESOI, IC excluindo zero e ganho preservado na sensibilidade
  balanceada e no controle pareado por grau (família Holm de 3).
- Cobertura: classes com **K≥10 nos dois lados**, sem consultar scores —
  41 rótulos compartilhados, **35 classes elegíveis** após exclusões
  (`crosswalk-hemilineage.draft.json`, versão `hemilineage-2.0-draft`).
- Exclusões: `TBD`, ausentes, `21X` (K<10) e os cinco incertos
  (`20A.22A`, `20B.21B.22B`, `24B.25B`, `26X`, `27X`).

## 4. Independência do rótulo (condição de validade)

- MANC: documentado (Marin et al. 2024): hemilinhagem por origem de
  desenvolvimento (light-level, trato somático, NBLAST morfológico), não por
  conectividade sináptica — independente do trilho topológico.
- MCNS (PMC12636603): semântica de desenvolvimento, mas atribuição por
  **transferência via correspondência** (NBLAST + co-clustering de
  conectividade); independência em relação à conectividade de entrada **não
  demonstrada** — desfecho **não materializável como confirmatório** (condição
  5) sem justificativa humana registrada. A independência declarada é em
  relação à conectividade sináptica, **não** em relação à morfologia.
- Trilho de morfologia (Experimento C) fica **proibido** para este desfecho,
  pois a atribuição de hemilinhagem usa morfologia no MANC.

## 5. Features, modelo e baselines

- Trilho A (topologia): direção, peso e graus; proibido tipo, hemilinhagem,
  região, posição, morfologia e IDs.
- Modelo: GraphSAGE 1–3M e GIN comparável; MLP de controle; baselines
  aleatório, maioria, degree-only e estatísticas artesanais; grid de 12 trials
  e 5 seeds do pré-registro v1 (reutilizados como hiperparâmetros congelados).
- Open-set: consultas sem hemilinhagem na galeria; AUROC/AUPR/FPR@TPR95.
- Calibração: Brier/ECE (15 bins) com temperatura ajustada só na fonte.

## 6. Escada de claims

- Permitido em caso de sucesso: “a topologia da fonte transfere informação
  sobre hemilinhagem de desenvolvimento para o alvo observado”.
- Proibido: chamar hemilinhagem de tipo funcional, inferir função, generalizar
  para a população de moscas ou reutilizar T0 como confirmação.

## 7. Estados e decisão

- T0 (tipo harmonizado): **exploratório; inconclusivo por circularidade**.
- Hemilinhagem: confirmatório somente se a independência do MCNS for
  confirmada e este pré-registro for assinado; caso contrário,
  **inconclusivo** (opção 3 do responsável).
- Alterações após assinatura seguem o `CHANGELOG.md`; nenhum unseal antes de
  G3/novo pré-registro.
