# Pergunta, estimando e unidade de análise (provisório)

Aberto em 2026-09-14 (C02). Documento **provisório de planejamento**; não é
pré-registro. Deve ser revisado por humano em G0 e substituído pelo pré-registro
(R07) antes de qualquer avaliação do alvo. Nenhum dado do alvo foi acessado e
nenhuma capacidade de dataset é afirmada aqui.

## 1. Pergunta operacional

> Fixados um ou mais connectomas-fonte e um connectoma-alvo nunca usados para
> ajuste, um encoder indutivo treinado sem rótulos na fonte melhora a recuperação
> macro de rótulo de tipo harmonizado no alvo em relação ao melhor baseline
> simples pré-registrado, no trilho somente topologia?

Vocabulário conforme `docs/research/GLOSSARIO.md` (GLO-01 a GLO-14).

## 2. Estimando (*estimand*)

- Δ = θ_encoder − θ_baseline*, em pontos percentuais absolutos (pp) de Macro
  Recall@1 no alvo.
- θ_encoder: desempenho de um encoder com pesos, probe, transformações e
  limiares congelados antes do alvo (zero-shot cross-connectome, GLO-03).
- θ_baseline*: desempenho do melhor baseline simples no mesmo protocolo,
  escolhido por validação interna da fonte e congelado antes do alvo.
- Δ é estimado **condicional aos connectomas observados**: o alvo é um único
  grafo; a incerteza reportada vem de reamostragem dentro do alvo, agrupada por
  tipo, não de variação entre indivíduos.
- SESOI provisório: 5 pp (`docs/ESCOPO-E-HIPOTESES.md` § Definição provisória de
  sucesso e falsificação); o valor definitivo entra no pré-registro (R07).
- Denominador: tipos harmonizados com cobertura mínima no alvo; cobertura mínima
  e exclusões são fixadas em C04/R07, antes do unseal.
- Estratificação: análise principal balanceada por tipo e controle pareado por
  grau (B03, M09).

## 3. Hipóteses

### Hipótese primária

H1: Δ ≥ 5 pp no alvo observado, com intervalo de confiança de 95% para Δ
excluindo zero, preservado na análise balanceada por tipo e no controle pareado
por grau.

### Hipótese nula

H0: Δ ≤ 0, ou Δ compatível com zero depois de controlar desbalanceamento, grau,
atalhos de amostragem e incerteza; qualquer desempenho aparente é compatível com
propriedades triviais, ruído de anotação ou peculiaridades do dataset-fonte.

Estados de decisão (`sucesso`, `parcial`, `refutado`, `inconclusivo`) definidos
em C04 e aplicados no gate G6.

## 4. Diagrama do fluxo

```text
+----------------------------------------------+
| FONTE: grafo + rótulos permitidos            |
| data/raw/source/                             |
+----------------------------------------------+
                      |
                      v
+----------------------------------------------+
| Treino auto-supervisionado sem rótulos       |
+----------------------------------------------+
                      |
                      v
+----------------------------------------------+
| Seleção interna na fonte: probe, limiares,   |
| escolha do baseline*                          |
+----------------------------------------------+
                      |
                      v
+----------------------------------------------+
| CONGELAMENTO: encoder + probe + transformações|
| artifacts/frozen/ + hashes                    |
+----------------------------------------------+
                      |
                      v
+----------------------------------------------+
| ALVO PÚBLICO: grafo apenas, inferência        |
| indutiva; data/raw/target-public/             |
+----------------------------------------------+
                      |
                      v
+----------------------------------------------+
| AVALIADOR SELADO: rótulos, crosswalk,         |
| métricas e intervalos; data/sealed/...        |
+----------------------------------------------+
                      |
                      v
+----------------------------------------------+
| Gate G6: sucesso | parcial | refutado |       |
| inconclusivo                                  |
+----------------------------------------------+
```

## 5. Unidade de consulta e galeria

- Unidade de consulta: um neurônio do alvo.
- Galeria: neurônios/protótipos da fonte por tipo harmonizado, fixados no
  congelamento; o custodiante calcula as métricas.
- Classes conhecidas: tipos presentes na fonte e no alvo após harmonização
  aprovada por humano (C03, D08).
- Open-set: consultas cujo tipo harmonizado não existe na galeria; trilho
  secundário pré-registrado (C04, B02, S08).
- Tipos ausentes, ambíguos, singleton ou com rótulos conflitantes: regra em C03;
  inclusão e exclusão não podem depender de scores observados.

## 6. Réplicas e independência

- Seeds de treinamento são réplicas técnicas (GLO-11).
- Neurônios do mesmo grafo compartilham estrutura e não são amostras
  independentes entre si.
- Declaração canônica: “Seeds de treinamento e neurônios do mesmo grafo não são
  indivíduos biológicos independentes.”
- Intervalos e testes usam bootstrap/permutação agrupado por tipo e, quando
  aplicável, respeitando a estrutura do grafo; neurônio isolado nunca conta como
  réplica independente.
- Múltiplas seeds medem estabilidade do treino, não aumentam o tamanho da
  amostra biológica.

## 7. Limites de generalização

- A conclusão do MVP é um **estudo de transferência entre datasets observados**,
  não uma estimativa para a população de moscas.
- Com um connectoma-fonte e um connectoma-alvo, o número de indivíduos por papel
  é 1; nenhuma variância biológica é estimada.
- Alegações mais amplas exigiriam múltiplos indivíduos independentes por papel,
  o que não está no desenho inicial (Nível 3, condicional).
- Few-shot: trilho separado com orçamento explícito de exemplos; seus resultados
  nunca substituem os do zero-shot.
- O desfecho secundário de link prediction não altera o estimando primário.

## 8. Vocabulário restrito

C02 proíbe usar “universal”, “função” e “cross-individual” sem condição
verificável. Neste projeto:

- “universal”: exigiria amostragem de múltiplos espécimes, estágios e tecidos com
  replicação independente; o desenho inicial não atende e o termo fica proibido.
- “função”: o projeto mede rótulo de tipo harmonizado, não propriedade
  fisiológica (GLO-07); o termo não é desfecho e não pode descrever resultados.
- “cross-individual”: exigiria pelo menos dois espécimes independentes em cada
  papel; com um alvo único a alegação não tem condição verificável e fica
  proibida no MVP.

Fora desta seção os três termos não aparecem no documento, e a validação
automatizada rejeita ocorrências fora daqui.

## 9. Rastreabilidade

- Claims relacionados: CLM-001 (H1) e CLM-015 (circularidade), ambos `aberto` até
  haver evidência (`docs/research/CLAIMS.md`).
- Continuidade: C03 (equivalência), C04 (desfechos), G0 (revisão humana), G3
  (pré-registro/firewall), G6 (decisão do MVP), R06/R07.
- Validação: `python3 tools/validate_research.py`.

## 10. Limitações

- Este documento não congela números finais: SESOI, cobertura mínima e regras de
  exclusão dependem do inventário de dados (D01–D10) e do pré-registro.
- A separação de papéis (executor/custodiante) é procedural; sem custodiante
  independente, a avaliação ocorre em sessão separada e isso será declarado.
- Nenhum dado externo foi consultado; nenhuma release ou licença foi avaliada.
