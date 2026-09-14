# Changelog do pré-registro

Toda alteração após a assinatura entra aqui com motivo, impacto, diff resumido e
hash; nenhuma configuração ou resultado anterior é sobrescrito. Depois do
unseal, mudanças são rotuladas `exploratória` e não substituem a análise
confirmatória (`docs/PROTOCOLO-EXECUCAO.md`).

| Data | Versão | Autor | Motivo/impacto | Diff/hash | Trilha |
|---|---|---|---|---|---|
| 2026-09-14 | 1.0-draft | IA executora (R07) | minuta inicial; nenhuma análise rodada | `preregistration/REGISTRY.md` | — |
| 2026-09-14 | 1.0 | Alexandre Zanata (revisor humano único) | assinatura do pré-registro como está; três papéis acumulados com limitação declarada; nenhum artefato congelado alterado | hash do pacote `9411af0ca15501b253934f5e2134d978a95526dcf2c4cb7923a677a685f658b1` | confirmatória |

## Regras

- Correções de forma também exigem entrada.
- O hash de assinatura é o do pacote listado em `REGISTRY.md`; qualquer edição
  posterior exige nova linha e nova assinatura quando mudar o confirmatório.
- Mudanças de métrica, SESOI, exclusões ou análise após o unseal são
  proibidas como confirmatórias; viram análise exploratória com registro.
