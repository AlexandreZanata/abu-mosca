# Changelog do pré-registro

Toda alteração após a assinatura entra aqui com motivo, impacto, diff resumido e
hash; nenhuma configuração ou resultado anterior é sobrescrito. Depois do
unseal, mudanças são rotuladas `exploratória` e não substituem a análise
confirmatória (`docs/PROTOCOLO-EXECUCAO.md`).

| Data | Versão | Autor | Motivo/impacto | Diff/hash | Trilha |
|---|---|---|---|---|---|
| 2026-09-14 | 1.0-draft | IA executora (R07) | minuta inicial; nenhuma análise rodada | `preregistration/REGISTRY.md` | — |
| 2026-09-14 | 1.0 | Alexandre Zanata (revisor humano único) | assinatura do pré-registro como está; três papéis acumulados com limitação declarada; nenhum artefato congelado alterado | hash do pacote `9411af0ca15501b253934f5e2134d978a95526dcf2c4cb7923a677a685f658b1` | confirmatória |
| 2026-09-14 | 1.1 | Alexandre Zanata (revisor humano único) | desvio formal: H07 materializará o crosswalk MANC→MCNS com revisão única (D08 tinha um revisor), com revisão final e assinatura do responsável; mitigação: revisão final humana, circularidade obrigatória em sensibilidade e transferência para revisor independente antes de M08, se disponível. Impacto científico: risco de viés de mapeamento permanece registrado e o crosswalk não entra como feature nem como tuning. | hash do pacote inalterado; crosswalk rascunho `4ca34aabe20964df4d9dac5384f6dd7ce28ca2a6a6b039382ee9395ff860446f` | confirmatória (desvio) |
| 2026-09-14 | 2.0-draft | IA executora (H07 reformulação) | desfecho primário reformulado para hemilinhagem de desenvolvimento (`hemilineage` MANC ↔ `trumanHl` MCNS) por decisão do responsável (opção 2); T0 rebaixado a exploratório e inconclusivo por circularidade; cobertura K≥10 nos dois lados = 40 classes (41 compartilhadas); independência do MANC documentada (Marin et al. 2024) e do MCNS **não confirmada**; assinatura pendente e materialização bloqueada até confirmação (condição 5) | crosswalk `fdb8dbc8e0844dfc52b984fd629ec23d22540d3ecc8782c96ae9d547e28e1bbe`; pacote v2 | confirmatória (minuta) |
| 2026-09-14 | 2.0-draft (rev b) | IA executora (H07) | tentativa de confirmação da proveniência de `trumanHl` (Europe PMC sem OA; bioRxiv 429) falhou; condição 5 mantida | auditoria `H07-HEMILINEAGE-AUDIT.md` §5 | confirmatória (minuta) |
| 2026-09-14 | 2.2-draft | IA executora (H07, correções do responsável) | exclusão dos 5 rótulos incertos (cobertura 35 classes K≥10 nos dois lados); H1′ corrigida para permitir a conectividade pública do alvo apenas em inferência congelada; auditoria atualizada com PMC12636603, que revela transferência de hemilinhagem por correspondência (NBLAST + co-clustering de conectividade) → independência não demonstrada e condição 5 em vigor (não confirmatório até justificativa humana); T0 segue exploratório/inconclusivo | crosswalk `2dc94f8a2845d7c6e75cea9f63286b00f1ae21c259a5053357292eb9ca9d28df` | confirmatória (minuta, pendente) |
| 2026-09-14 | 2.3 | Alexandre Zanata (revisor humano único) | **desfecho de hemilinhagem declarado inconclusivo por circularidade** (condição 5): NBLAST combinado com co-clustering de conectividade não oferece independência suficiente para um modelo que usa conectividade, e excluir apenas correspondências many:1/ambíguas não elimina o problema; H07 encerrada **sem materialização confirmatória** de label set; artefatos e hashes preservados; nenhum claim confirmatório de transferência autorizado; H09 prossegue em modo estritamente exploratório | hash do pacote inalterado; crosswalk `2dc94f8a…` mantido como artefato provisório | inconclusiva |

| 2026-09-15 | 3.0 | Alexandre Zanata (decisão humana registrada pela IA executora) | **emenda do grid de parâmetros do R07 §5**: o grid congelado (dim 64/128; 2–3 camadas) rendia 13.824–101.760 parâmetros, abaixo do intervalo de 1–3M declarado para o MVP; decisão pela opção (a) da nota de bloqueio da M02. Diff: coluna Dim passa a 576 (trials de 2 camadas) e 408 (trials de 3 camadas); Camadas, Fanout, LR, Batch, Dropout e o budget de 12 trials inalterados. Contagens exatas: 2 camadas/576 = 1.009.152; 3 camadas/408 = 1.009.800. Impacto: capacidade do encoder dentro do intervalo do MVP; nenhum dado, desfecho, métrica, SESOI, seed, exclusão ou análise alterados; seleção segue source-only. Revisões: G3 e G5 (condição 6) re-revisados na mesma decisão; hash do pacote atualizado no REGISTRY e no G3. Hash do pacote anterior 9411af0ca15501b253934f5e2134d978a95526dcf2c4cb7923a677a685f658b1. | pacote novo `1ef26bcb80f516dbca40f4aea192c1dba330625a83d1ecac5f5498678d7459e8`; PROTOCOL.md `1f5a90ab1e49f2988a46294035c941e8a0c5a0335a000897aea891fcf9884a26` | confirmatória (emenda autorizada) |

## Regras

- Correções de forma também exigem entrada.
- O hash de assinatura é o do pacote listado em `REGISTRY.md`; qualquer edição
  posterior exige nova linha e nova assinatura quando mudar o confirmatório.
- Mudanças de métrica, SESOI, exclusões ou análise após o unseal são
  proibidas como confirmatórias; viram análise exploratória com registro.
