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

## Regras

- Correções de forma também exigem entrada.
- O hash de assinatura é o do pacote listado em `REGISTRY.md`; qualquer edição
  posterior exige nova linha e nova assinatura quando mudar o confirmatório.
- Mudanças de métrica, SESOI, exclusões ou análise após o unseal são
  proibidas como confirmatórias; viram análise exploratória com registro.
