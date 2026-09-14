# Desfechos, sucesso, nulidade e falsificação (provisório)

Aberto em 2026-09-14 (C04). Documento **provisório**: será substituído pelo
pré-registro (R07) depois do inventário de dados (D01–D10) e revisado por humano
em G0. Nenhum número final é fixado aqui e nenhum dado do alvo foi acessado.
Consistente com `docs/research/PERGUNTA-E-ESTIMANDO.md` (C02),
`docs/research/EQUIVALENCIA.md` (C03, aprovada) e
`docs/ESCOPO-E-HIPOTESES.md`.

## 1. Estado e escopo

- Fixa métrica primária, métricas secundárias, SESOI provisório, controles nulos
  e árvore de decisão antes de qualquer score do alvo.
- Números finais (SESOI, cobertura mínima e número de seeds) entram no
  pré-registro (R07).
- Métrica, limiares e exclusões são congelados antes do unseal; mudanças
  posteriores são rotuladas exploratórias e não substituem a análise
  confirmatória (`docs/PROTOCOLO-EXECUCAO.md`).

## 2. Métrica primária

- Macro Recall@1 no alvo, no nível T0 (tipo harmonizado), com ranking por
  similaridade no embedding congelado e galeria congelada (C02 e C03).
- Intervalo: IC 95% para a métrica e para a diferença Δ por bootstrap agrupado
  por tipo, respeitando a dependência entre neurônios do mesmo grafo.
- Denominador: tipos harmonizados com cobertura mínima K no alvo; K e exclusões
  são fixados em R07 e a cobertura é sempre reportada.
- Análise principal balanceada por tipo.
- Micro-média e acurácia bruta são apenas diagnósticas.

## 3. Métricas secundárias

- Recuperação e classificação: Recall@5, Recall@10, MRR, MAP, macro-F1 e
  balanced accuracy.
- Calibração: Brier score e ECE; qualquer ajuste de calibração é aprendido
  apenas na fonte e congelado antes do alvo.
- Open-set: AUROC, AUPR e FPR na taxa de verdadeiros positivos pré-especificada
  (por exemplo TPR = 95%); consultas unknown ficam fora do denominador do T0 e
  são reportadas à parte (C03).
- Diagnóstico e visual: micro-média, acurácia bruta, UMAP e t-SNE.
- Desfecho secundário pré-registrado: link prediction no alvo sem fine-tuning;
  não substitui a avaliação de tipos.

## 4. SESOI provisório

- SESOI = 5 pontos percentuais absolutos de Macro Recall@1 sobre o melhor
  baseline simples pré-registrado (ESCOPO e C02).
- Sinal exigido: mediana entre seeds de Δ ≥ SESOI, com IC 95% para Δ excluindo
  zero e ganho preservado (a) na análise balanceada por tipo e (b) no controle
  pareado por grau.
- Valores definitivos de SESOI, K e número de seeds dependem de D01–D10 e são
  fixados em R07; não há sweep aberto.

## 5. Controles nulos e robustez

- Baselines obrigatórios: aleatório, maioria, degree-only, estatísticas
  artesanais e MLP (B03–B05).
- Degree-matched control: pareamento por grau in/out; o ganho precisa sobreviver
  ao pareamento para sustentar transferência.
- Permutação de rótulos como controle negativo: o desempenho deve colapsar para
  o nível do acaso.
- Verificações de atalho: embaralhar IDs e ordem e remover metadados proibidos
  no trilho topologia (R05 e M01).
- Múltiplas seeds: reportar mediana e intervalo entre seeds; a melhor seed não
  conta como estimativa.
- Múltiplas comparações: hierarquizar ou corrigir nas ablações confirmatórias.
- Sensibilidade a thresholds de aresta e à amostragem de negativos (H06 e S06).

## 6. Gap within-vs-cross

- within: desempenho dentro da fonte em validação congruente, na mesma métrica
  primária.
- cross: desempenho no alvo congelado.
- gap within-vs-cross = within − cross; é diagnóstico de overajuste à fonte ou
  de mudança de domínio.
- Gap grande com cross compatível com a nulidade sustenta refutação, não
  sucesso; o limiar quantitativo entra em R07.

## 7. Árvore de decisão

Pré-condições de validade: cobertura de rótulos suficiente, amostra mínima,
anotação não circular e comparabilidade anatômica documentada. Se qualquer
pré-condição falhar, o estado é `inconclusivo` e o teste não é forçado.

```text
pré-condições válidas?
  não  -> inconclusivo
  sim
   |
   +-- Δ >= SESOI e IC 95% exclui zero e ganho preservado
   |   na análise balanceada e no degree-matched?  -> sucesso
   |
   +-- supera aleatório/maioria, mas empata com degree-only,
   |   estatísticas artesanais, MLP ou outro baseline simples,
   |   ou ganho positivo abaixo do SESOI?           -> parcial
   |
   +-- Δ <= 0, ou ganho desaparece no degree-matched,
   |   ou within bom com cross compatível com nulidade? -> refutado
   |
   +-- impedimento de cobertura/amostra/circularidade/
       incompatibilidade?                           -> inconclusivo
```

- **sucesso:** Δ ≥ SESOI com IC 95% excluindo zero e preservado na análise
  balanceada por tipo e no controle pareado por grau; conclusão limitada aos
  datasets observados (C02).
- **parcial:** supera aleatório e maioria, mas empata com degree-only,
  estatísticas artesanais, MLP ou outro baseline simples; ou ganho positivo
  abaixo do SESOI.
- **refutado:** Δ ≤ 0; ou o ganho desaparece no controle pareado por grau; ou
  desempenho within bom com cross compatível com a nulidade.
- **inconclusivo:** cobertura, tamanho de amostra, circularidade de anotação ou
  incompatibilidade anatômica impedem o teste; não pode ser rebatizado como
  sucesso.

Os quatro estados são mutuamente exclusivos e decididos no gate G6 a partir do
pacote congelado (M10).

## 8. Regras de reporte e proibições

- Reportar denominadores, classes excluídas, cobertura, número de seeds e método
  do intervalo.
- UMAP e t-SNE não contam como evidência; são apenas visuais.
- A melhor seed não conta como estimativa; usar mediana e intervalo entre seeds.
- Nenhuma métrica, limiar ou exclusão pode ser trocada após o unseal.
- Micro-média e acurácia bruta não substituem a métrica primária.
- Empate com baseline simples não vira sucesso nem ganha métrica nova.

## 9. Rastreabilidade e limitações

- Claims: CLM-001 (H1) e hipóteses secundárias em `docs/research/CLAIMS.md`.
- Riscos: RSK-002 (grau), RSK-004 e RSK-005 (circularidade), RSK-012
  (dependência estatística) em `docs/research/RISCOS.md`.
- Fases: C02, C03, B02–B05, B09, M08, M09, S08, R06, R07 e G6.
- Limitações: documento provisório, sem números finais; validação apenas
  estrutural; revisão humana prevista em G0; nenhum dado externo consultado.
- Validação: `python3 tools/validate_research.py`.
