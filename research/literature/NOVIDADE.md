# Mapa de lacuna e veredito de novidade (provisório)

Aberto em 2026-09-14 (L07). Claim por claim, com trabalhos mais próximos,
diferenças e evidência conflitante. **Ausência em uma busca não prova novidade**;
o veredito é provisório e depende da revisão humana em G1. Fontes no ledger.

## 1. Estado e escopo

- Lacunas recebem IDs `GAP-nn`; contribuições, `CON-nn` (no máximo três).
- As buscas adversariais de 2026-09-14 estão registradas no QUERY-LOG com as
  consultas Q4 e Q5.
- Nenhum dado foi baixado e nenhuma métrica foi reproduzida nesta fase.

## 2. Mapa de lacunas

### GAP-01 — Transferência zero-shot de encoder de conectividade entre connectomas
- Claim: é possível treinar um encoder indutivo sem rótulos em um connectoma-fonte e recuperar tipos harmonizados em um alvo nunca visto, sem rótulos nem âncoras no alvo, superando baselines simples.
- Trabalhos mais próximos: LIT-0058 (NTAC) e LIT-0060 (alinhamento BANC-MANC).
- Diferença proposta: NTAC tipa dentro de cada dataset, com variante semeada transdutiva, e não transfere um encoder congelado; o alinhamento BANC-MANC resolve um par de grafos anotados de forma transdutiva. O projeto congela um encoder treinado apenas na fonte e avalia em um alvo sem anotação nem correspondência.
- Evidência conflitante: NTAC mostra que conectividade isolada já recupera tipos com alta acurácia dentro de datasets, reduzindo a novidade de "conectividade funciona"; LIT-0061 relata falha de SSL genérico contra heurísticas topológicas, ameaçando o objetivo auto-supervisionado.
- Busca adversarial: consultas Q5/Q4 de 2026-09-14 (zero-shot cross-connectome; self-supervised pretraining connectome transfer; connectome foundation model). Nenhum trabalho com encoder congelado cross-connectome em Drosophila foi encontrado; ausência não prova novidade.
- Status: aberto

### GAP-02 — Objetivo auto-supervisionado topológico com controles de atalho
- Claim: um objetivo masked edge/weight sobre encoder indutivo aprende representações transferíveis sem node ID e sobrevive a negativos pareados por grau e ao controle degree-matched.
- Trabalhos mais próximos: LIT-0062 (MaskGAE), LIT-0063 (Bandana) e LIT-0039 (GraphMAE).
- Diferença proposta: os métodos existentes são genéricos e avaliados em grafos de benchmark; nenhum testa transferência entre connectomas com negativos pareados por grau ou distância e com controle de rewiring preservando grau.
- Evidência conflitante: LIT-0061 mostra SSL invariante a augmentations topológicas perdendo para Jaccard; LIT-0064 usa rewiring preservando grau como controle forte em connectoma.
- Busca adversarial: consultas Q4 de 2026-09-14 (masked edge prediction; degree-matched control).
- Status: aberto

### GAP-03 — Protocolo de avaliação zero-shot com firewall e crosswalk selado
- Claim: um protocolo pré-registrado (firewall, crosswalk selado, estados de decisão, intervalos agrupados e degree-matched) pode servir de benchmark reproduzível para transferência cross-connectome.
- Trabalhos mais próximos: LIT-0002 (definição de tipo entre cérebros), LIT-0060 (desafio público de alinhamento) e LIT-0064 (controles de rewiring).
- Diferença proposta: nenhum pacote revisado combina avaliação selada, controles de grau e métrica macro por tipo em connectoma-alvo.
- Evidência conflitante: metodologia isolada não é contribuição científica se os resultados forem negativos; LIT-0060 já organiza um desafio comunitário de alinhamento.
- Busca adversarial: consultas Q4/Q5 de 2026-09-14 já registradas.
- Status: aberto

## 3. Contribuições propostas

### CON-01 — Teste zero-shot cross-connectome com encoder congelado
- Contribuição: primeiro teste controlado, em connectomas de Drosophila, de transferência zero-shot de representações de conectividade para recuperação de tipo harmonizado em alvo nunca usado.
- Teste: M06 a M08 e G6, com firewall e crosswalk aprovados (C03 e G3).
- Versão mínima: um par fonte/alvo, GraphSAGE pequeno (1 a 3M de parâmetros), masked edge/weight, Macro Recall@1 com IC por bootstrap agrupado por tipo e baselines random, majority e degree-only.
- Risco: NTAC pode tornar a contribuição incremental se a transferência não superar baselines simples; resultado negativo permanece publicável (NIV-01/C06).
- Status: proposto (pendente de G1)

### CON-02 — Avaliação honesta do ganho e da estabilidade
- Contribuição: quantificar se o ganho sobrevive aos controles (degree-matched e balanceado por tipo) e quão estável é entre cérebros e espécimes, separando seeds de réplicas biológicas.
- Teste: M09, S03 e S08, com os estados de C04.
- Versão mínima: a de CON-01 mais degree-matched e análise de sensibilidade.
- Risco: empatar com degree-only leva ao estado parcial e deve ser reportado como tal.
- Status: proposto

### CON-03 — Pacote de controles antileakage e benchmark reproduzível
- Contribuição: pacote aberto com firewall, crosswalk selado, controle pareado por grau, permutação de rótulos e bootstrap agrupado adaptado a connectomas.
- Teste: R05 a R08 e M09.
- Versão mínima: scripts, configurações e manifests com fixtures sintéticas.
- Risco: é contribuição metodológica, não descoberta biológica; menor novidade isolada.
- Status: proposto

## 4. Alternativa sem novidade suficiente

- Se G1 concluir que NTAC (LIT-0058) e o alinhamento BANC-MANC (LIT-0060) já
  cobrem a claim central, a alternativa é declarar **não há novidade
  suficiente** e publicar o estudo negativo de transferência (NIV-01) ou
  restringir o projeto a CON-03.
- A ausência em uma busca não prova novidade; este veredito é provisório e
  depende de revisão humana.

## 5. Limitações

- Buscas adversariais limitadas a seis consultas (Q4 e Q5) nas bases do
  protocolo; literatura cinzenta pode não ter sido coberta.
- Um relato de blog sobre um modelo conectoma-LLM foi encontrado e descartado
  como evidência por não ser fonte primária.
- Nenhum dado foi baixado, nenhuma métrica foi reproduzida e nenhum veredito
  final foi emitido.
- Validação: `python3 tools/validate_research.py`.
