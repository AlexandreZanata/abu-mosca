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

## 4. Estado do bloqueio

- Segundo revisor humano: **ausente**.
- Crosswalk curado: **não existe** (nenhum mapeamento manual foi criado).
- Custodiante independente: **não designado** (acumulação procedimental, já
  declarada no G2/R07/G3).
- Próximo passo: decisão humana sobre o segundo revisor (ou registro formal de
  desvio com limitação declarada, com emenda ao pré-registro pelo changelog).
