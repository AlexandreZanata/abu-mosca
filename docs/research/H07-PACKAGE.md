# Pacote H07 — crosswalk e conjuntos avaliativos sob custódia (bloqueado)

Preparado em 2026-09-14. **H07 não foi concluída**: a fase exige materializar o
crosswalk real com **duas revisões humanas** nos mapeamentos manuais e execução
pelo custodiante, e nenhuma das duas condições existe hoje (o D08 foi aprovado
por um único revisor, com a pendência do segundo registrada). Este documento
descreve a ferramenta pronta, o checklist da curadoria e o bloqueio.

## 1. O que está pronto (ferramenta do custodiante)

- `tools/sealed_labels.py`: constrói o label set no schema de H04 a partir de um
  crosswalk revisado + anotações do alvo.
  - Exige `reviewer1` e `reviewer2` **distintos** por mapeamento e fonte em
    `sources`; recusa revisão única.
  - Aplica a regra explícita de **muitos-para-um** (grupos listados no
    relatório) e a classe canônica é o tipo do alvo.
  - Sinaliza **tipos circulares** para a análise de sensibilidade e permite
    excluir `ambiguous`/`conflicting` (DEC-EQ-08 e DEC-CW-03).
  - Escreve label set e relatório **somente dentro da zona selada** e o
    relatório contém apenas agregados (sem qualquer `q`/`g` id ou body).
  - Registra `label_set_sha256` e `crosswalk_sha256` e emite relatório de
    cobertura agregado por status e por tipo.
- `tests/test_sealed_labels.py` (6 casos): build válido, dupla revisão
  obrigatória, exclusões, relatório sem IDs, exigência de zona selada e CLI
  ponta a ponta.

## 2. Checklist da curadoria humana (bloqueio)

1. **Segundo revisor humano**: indicar uma pessoa distinta para revisar cada
   mapeamento manual (pré-condição registrada em D08/`CROSSWALK-AUDIT.md`).
2. **Curadoria do crosswalk MANC → MCNS**: preencher
   `source_type`, `target_type`, `kind`, `reviewer1`, `reviewer2` e `sources`
   (literatura, NBLAST ou reidentificação), respeitando DEC-CW-02 e DEC-EQ-07.
3. **Listas de exclusão/sensibilidade**: definir `ambiguous_types`,
   `conflicting_types` e `circular_types` (tipos derivados de conectividade).
4. **Custodiante**: executar a ferramenta dentro de `data/sealed/`, registrar
   hashes e compartilhar somente o relatório de cobertura agregado.

## 3. Comandos previstos

```bash
.venv/bin/python tools/sealed_labels.py \
  --crosswalk preregistration/crosswalk-manc-mcns.json \
  --target-annotations data/sealed/target-labels/annotations.json \
  --sealed-dir data/sealed --out data/sealed/target-labels/labels.json \
  --report data/sealed/target-labels/coverage.json \
  --circular-types <tipos> --ambiguous-types <tipos> --conflicting-types <tipos>
```

## 3b. Rascunho do crosswalk (decisão 2b executada)

- `preregistration/crosswalk-manc-mcns.draft.json` construído **somente** da
  coluna `mancType` das anotações públicas auditadas do MCNS (`male-cns:v1.0`,
  LIT-0079/D07; arquivo com sha256 `2177e246…`), com proveniência individual por
  correspondência (arquivo, colunas, suporte de neurônios, contagens de
  multiplicidade).
- Números: **4.217** correspondências tipo-a-tipo cobrindo **4.182** tipos do
  MCNS e **3.893** tipos do MANC; kinds: 3.734 one-to-one, 429 one-to-many, 22
  many-to-one, 32 many-to-many; 19 grupos many-to-one e 137 tipos do MANC que
  se dividem em mais de um tipo do MCNS.
- Circularidade (decisão 4): todos os 4.182 tipos do alvo entram em
  `circular_types` e na sensibilidade obrigatória; `ambiguous_types` e
  `conflicting_types` vazios. K=10 mantido (decisão 5a).
- Desvio de revisor único registrado no `CHANGELOG.md` versão 1.1 (decisão 1b),
  com motivo, impacto e hash do rascunho
  `4ca34aabe20964df4d9dac5384f6dd7ce28ca2a6a6b039382ee9395ff860446f`.
- Garantia de não-leakage: crosswalk e rótulos não são lidos por adapters,
  features, transformador de arestas nem pelo contrato de run (checado no
  validador); nada de ID por neurônio no rascunho.

## 3c. Resultado da reformulação (passos 1–4 executados)

- **Passo 1 — proveniência tipo a tipo** (`tools/label_provenance_audit.py`):
  11.751 tipos com `type`; canais: correspondência entre datasets 11.751,
  linhagem 10.461, genético 909, apenas curadoria manual 2. Nenhum canal
  documenta tipo atribuído sem conectividade/morfologia (LIT-0023/D07).
- **Passo 2 — subconjunto não circular:** **não existe** para o desfecho T0;
  benchmark primário formalmente **inconclusivo por circularidade**.
- **Passo 3 — cobertura K=10 sem scores:** rótulos alternativos com canal
  independente — genético `fruDsx` (6 classes, todas ≥10, 4.976 neurônios,
  menor classe 16) e linhagem `trumanHl` (64 classes ≥10, 17.704 neurônios).
- **Passo 4 — novo relatório e hashes:**
  `artifacts/reports/H07-PROVENANCE-AUDIT.md` + `.json` (agregados; nenhum ID);
  rascunho `draft-1.0` mantido sem alteração.
- **Passo 5 — decisão humana:** escolher uma das opções de reformulação (trocar
  para `fruDsx`, trocar para linhagem, manter T0 exploratório com inconclusivo,
  ou buscar novo par de datasets) com novo pré-registro quando mudar o
  estimando.

## 3d. Decisão final (2026-09-14, humano)

- Aplicada a **condição 5**: o desfecho de hemilinhagem foi declarado
  **inconclusivo por circularidade** (NBLAST + co-clustering de conectividade
  não dão independência suficiente; excluir apenas many:1/ambíguos não
  resolve).
- H07 encerrada **sem materialização confirmatória**; nenhum label set foi
  escrito em `data/sealed/`; artefatos e hashes preservados como provisórios.
- Nenhum claim confirmatório de transferência é autorizado; H09 prossegue em
  modo estritamente exploratório.

## 4. Estado do bloqueio

- Revisor único: **decisão 1b registrada** no changelog 1.1 (desvio formal com
  limitação declarada); segundo revisor transferido para verificação futura, se
  houver pessoa independente antes de M08.
- Rascunho do crosswalk: **pronto**, aguardando **revisão final e assinatura**
  do responsável (decisão 2b); nenhuma materialização selada foi feita.
- Custodiante: acumulado pelo responsável com limitação declarada (decisão 3b).
- Benchmark primário: **inconclusivo por circularidade** registrado; o
  rascunho `draft-1.0` não será assinado e a coluna `mancType` não vira gold
  confirmatório.
- Próximo passo: **decisão humana sobre a reformulação** (seção 3c) e, se
  houver, segundo revisor antes de M08.
