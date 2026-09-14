# Auditoria de proveniência dos rótulos e reformulação do desfecho (H07)

Executada em 2026-09-14 por exigência do responsável, após ele **não assinar** o
rascunho `draft-1.0`. Fontes: anotações públicas auditadas do MCNS
(`male-cns:v1.0`, sha256 `2177e246…`, LIT-0079/D07) e a descrição de proveniência
de rótulos do paper (LIT-0023: prova de leitura completa, anotação manual com
revisão de especialistas e uso de conectividade/morfologia). Nenhum score foi
consultado e nenhum nó foi listado.

## 1. Canais de evidência por tipo (11.751 tipos com `type` preenchido)

| Canal | Tipos |
|---|---|
| Correspondência entre datasets (`flywireType`/`hemibrainType`/`vfbId`) | 11.751 |
| Linhagem de desenvolvimento (`trumanHl` ou `itoleeHl`) | 10.461 |
| Genético (`fruDsx`) | 909 |
| Apenas curadoria manual (sem qualquer canal acima) | 2 |

Todos os tipos têm ao menos um canal não-manual preenchido, mas nenhum canal
**documenta** que o tipo foi atribuído sem conectividade/morfologia: a
correspondência entre datasets deriva de matching, e linhagem/expressão são
evidências adicionais registradas após a tipagem. O paper não publica
proveniência por tipo; não há, portanto, subconjunto do desfecho T0 com
independência demonstrável de conectividade/morfologia.

## 2. Conclusão formal

- **Benchmark primário: inconclusivo por circularidade.** Os rótulos de tipo do
  alvo dependem do mesmo sinal que o modelo avalia; a sensibilidade sem tipos
  circulares é vazia, e assinar o `draft-1.0` apenas transferiria o bloqueio
  para a avaliação.
- A coluna `mancType` **não** é promovida a gold label confirmatório.
- O rascunho `draft-1.0` permanece artefato provisório de engenharia, sem
  remoção de tipos de `circular_types`.

## 3. Rótulos alternativos com canal independente (cobertura K=10, sem scores)

| Rótulo alternativo | Classes | Classes com n ≥ 10 | Neurônios cobertos | Menor classe |
|---|---|---|---|---|
| Genético `fruDsx` (`fru_low`, `fru_high`, `dsx_*`, `coexpress_*`) | 6 | 6 | 4.976 | 16 |
| Linhagem `trumanHl` | 75 | 64 | 17.704 | 12 |

Ambos sustentam cobertura suficiente para um **desfecho reformulado**, mas
exigem novo pré-registro (mudam o estimando) e mantêm ressalva: a atribuição do
rótulo ao neurônio usa pipelines de anotação (núcleos/expressão/linhagem), não
conectividade — ainda assim, é um alvo diferente de “recuperação de tipo”.

## 4. Opções de reformulação (decisão humana)

1. Trocar o desfecho primário para o rótulo genético `fruDsx` (K=10; 6 classes)
   com novo pré-registro e análise de sensibilidade própria.
2. Trocar para linhagem de desenvolvimento `trumanHl` (K=10; 64 classes).
3. Manter T0 apenas exploratório e declarar o benchmark primário inconclusivo
   por circularidade no relatório final.
4. Buscar outro par de datasets com proveniência de rótulo independente
   (exige nova auditoria D02–D10 e novo G2).

## 5. Dados e reprodutibilidade

- `tools/label_provenance_audit.py` gera
  `artifacts/reports/H07-PROVENANCE-AUDIT.json` (agregados; nenhum ID de
  neurônio); testes sintéticos em `tests/test_label_provenance_audit.py`.
- Nenhum rótulo selado foi criado; H07 permanece `[ ]` aguardando a decisão
  humana sobre a opção de reformulação (e o segundo revisor, se houver, antes
  de M08).
