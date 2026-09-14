# Plano de análise estatística e avaliador selado (R06)

Especificado em 2026-09-14. Define, antes de observar o alvo, o cálculo, a
incerteza e o formato dos resultados, substituindo as definições provisórias de
C04 por algoritmos concretos. Nenhum score do alvo foi calculado; nenhum rótulo
selado foi lido. A revisão humana de estatística e o congelamento de números
pendentes ocorrem em R07/G3.

## 1. Estado e escopo

- Base: `PERGUNTA-E-ESTIMANDO.md` (C02), `EQUIVALENCIA.md` (C03 aprovada),
  `DESFECHOS-E-FALSIFICACAO.md` (C04), `AMEACAS-A-VALIDADE.md` (C05),
  `CROSSWALK-AUDIT.md` (D08), `SELECAO.md` (D10), `FIREWALL.md` (R05) e o
  contrato de seeds/run de `RUN-CONTRACT.md` (R04).
- Nada aqui pode ser trocado após o unseal; mudanças posteriores são
  exploratórias e não substituem a análise confirmatória (PROTOCOLO).
- Números marcados `R07` (K de cobertura, limiar do gap, contagem final de
  seeds) são congelados no pré-registro com esta estrutura.

## 2. Métrica primária e cálculo exato

- Estimando: **Macro Recall@1 no alvo no nível T0** (tipo harmonizado).
- Score: similaridade de cosseno entre o embedding congelado da consulta e cada
  protótipo de tipo da galeria congelada (média dos embeddings da fonte por
  tipo); a previsão é o protótipo mais próximo.
- Macro: média não ponderada do recall por tipo, com cada tipo valendo igual;
  micro-média e acurácia bruta são apenas diagnósticas.
- `denominador`: consultas T0 elegíveis (tipo conhecido na galeria, sem
  ambiguidade/conflito/exclusão); `n_classes` e o tamanho de cada classe são
  sempre reportados.
- Intervalo: IC 95% da métrica e da diferença Δ por **bootstrap agrupado por
  tipo** com 10.000 reamostragens de tipos (com reposição) e seed derivada de
  R04 (`derive_seed(mestre, run_id, "bootstrap")`); o mesmo conjunto de
  reamostragens é usado em Δ (bootstrap pareado).

## 3. SESOI, Δ e regra de decisão

- **SESOI = 5 pontos percentuais absolutos** de Macro Recall@1 sobre o melhor
  baseline simples escolhido apenas na fonte (B09).
- Δ = encoder − baseline; estatística principal: mediana de Δ entre as 5 seeds
  pré-registradas, com IC 95% da mediana por bootstrap agrupado por tipo.
- `sucesso`: Δ ≥ SESOI, IC 95% excluindo zero e ganho preservado (a) na
  sensibilidade balanceada por tipo e (b) no controle pareado por grau; os três
  testes formam a família confirmatória e usam **Holm** com α = 0,05.
- `parcial`, `refutado` e `inconclusivo` seguem a árvore de C04 sem alteração.

## 4. Denominadores, missing labels e classes pequenas

- Elegibilidade decidida no congelamento (H07) e nunca em função de scores.
- `missing`: consulta com rótulo ausente sai do T0 e entra apenas em contagens.
- `ambíguo`: rótulo com dupla anotação sai do T0 (alternativa multi-label exige
  decisão humana, C03/DEC-EQ-08).
- `conflitante`: par não resolvido no crosswalk sai do T0 com registro e
  escalonamento humano.
- `singleton`: permanece no macro com n = 1 reportado; exclusão só com regra
  pré-registrada.
- `classe pequena`: classes com n < K participam do macro; a sensibilidade
  balanceada restringe a classes com n ≥ K. K é fixado em R07 (candidato 10) e
  nunca alterado após o unseal.
- Cobertura = consultas T0 elegíveis / consultas totais do alvo; reportada
  sempre, junto com todas as exclusões.

## 5. Dependência, agrupamento e nulos

- Declaração canônica: **neurônios do mesmo grafo e seeds de treino não são
  réplicas biológicas independentes**; nenhum teste trata nó como observação
  independente.
- Toda incerteza usa bootstrap/permutação agrupada por tipo; quando a estrutura
  do grafo importar, blocos são componentes conexas em vez de nós.
- Nulos: permutação de rótulos na fonte (B09), pareamento por grau in/out
  (B03–B05), embaralhamento de IDs/ordem (M01, R05).
- Nulo no alvo: o custodiante executa permutação de rótulos entre consultas
  T0 (10.000 permutações, seed registrada) e devolve apenas a distribuição e o
  p-valor; nenhum mapeamento por neurônio sai do selado.

## 6. Open-set, calibração e incerteza

- Open-set: consultas cujo tipo harmonizado não existe na galeria; ficam fora
  do denominador T0 e são avaliadas por AUROC, AUPR e FPR na TPR fixada em
  95% (`FPR@TPR95`), com IC por bootstrap agrupado por tipo.
- Rejeição: limiar de distância/cosseno escolhido apenas na fonte (validação
  interna) e congelado em M06; previsões podem marcar `rejected`.
- Calibração: probabilidades por softmax sobre similaridades com **temperatura
  ajustada somente na fonte** e congelada; Brier multiclasse e ECE com **15
  bins fixos de largura igual**; curvas de confiabilidade anexadas; nenhum refit
  de temperatura no alvo.
- Múltiplas seeds: reportar mediana, intervalo entre seeds e intervalo dentro
  de cada seed; a melhor seed nunca é a estimativa.

## 7. Métricas secundárias

Recall@5, Recall@10, MRR, MAP, macro-F1 e balanced accuracy, na mesma galeria e
mesmo congelamento; micro-média e acurácia bruta apenas diagnósticas; UMAP/t-SNE
nunca contam como evidência. Link prediction permanece desfecho secundário
pré-registrado e não substitui a métrica primária.

## 8. Sensibilidade e circularidade

- Análise primária com tipos sinalizados como derivados de conectividade
  (DEC-CW-03) e análise pareada sem eles; a diferença entra como sensibilidade
  obrigatória, não como métrica alternativa de sucesso.
- Sensibilidade a threshold de aresta, direção/reciprocidade e amostragem de
  negativos conforme H06/S06, sempre source-fit.

## 9. Formato de predições (schema)

- Arquivo validado por `schemas/predictions.schema.json`: `run_id`, `seed`,
  tamanho/contagem da galeria e lista de consultas com **IDs opacos**
  (`q<hex>`/`g<hex>`), top-10 com scores e flag `rejected`.
- Proibido no pacote de predições: qualquer label, nome de tipo, região,
  `bodyId`/`root_id` cru ou mapeamento de IDs.
- O executor do modelo nunca vê a chave opaca real; o mapeamento para IDs do
  alvo existe apenas no ambiente do custodiante.

## 10. Contrato do comando avaliador

- Comando: `python3 tools/evaluator_contract.py validate predictions|metrics <arquivo>`
  valida o contrato; a implementação real roda no ambiente do custodiante (H04).
- Interface do avaliador: entradas = pacote de predições + conjunto de rótulos
  selados com hash; saída = um único `metrics.json` no schema
  `schemas/metrics.schema.json`; execução em sessão separada, com firewall
  armado e sem rede.
- Invariantes: valida os schemas antes de pontuar; registra
  `inputs.predictions_sha256` e `inputs.label_set_sha256`; devolve apenas
  agregados, contagens, CIs e p-valores; **nunca** IDs por neurônio, listas de
  acertos ou exemplos individuais; logs passam pelo filtro do firewall.
- Unicidade: uma execução por chave lógica (M08); reexecução divergente exige
  incidente documentado com hashes e motivo.
- Determinismo: mesmos arquivos + seed registrada produzem o mesmo
  `metrics.json`; tolerância numérica zero.

## 11. Ordem da análise confirmatória

1. métrica primária e IC; 2. Δ pareado e Holm (família de 3); 3. gap
within-vs-cross; 4. open-set; 5. calibração; 6. secundárias; 7. sensibilidades.
Nenhuma etapa pode ser reordenada para escolher resultado.

## 12. Rastreabilidade e limitações

- Fases: C02–C05, B02–B09, M06–M09, H04/H07, R06/R07, G3/G6.
- A revisão humana de estatística é obrigatória em R07/G3; este documento é a
  minuta técnica revisável e não substitui a assinatura.
- Contagens finais de classes e de cobertura dependem de H07 (crosswalk sob
  custódia); K, limiar de gap e número final de seeds ficam `R07`.
- Validação: `python3 tools/validate_research.py`.
