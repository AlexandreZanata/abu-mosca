# Inventário de datasets candidatos (esquema congelado)

Aberto em 2026-09-14 (D01). Congela o esquema de comparação e abre o inventário
dos seis candidatos com **status vazio**. Nenhum campo foi verificado nesta
fase: todo campo desconhecido permanece `não confirmado`, e nenhum dataset é
declarado disponível. As auditorias D02–D07 preenchem os cards um a um.

## 1. Estado e escopo

- Objetivo: permitir comparação dos datasets pelos mesmos critérios.
- Os cards versionados ficam em `research/datasets/cards/`, um por candidato,
  criados a partir do modelo `docs/templates/DATASET-CARD.md`.
- Nenhum download, amostra, API ou licença foi acessada nesta fase.

## 2. Esquema congelado

Campos obrigatórios do inventário e dos cards (identificadores estáveis):

- `CAMPO-01` Release (versão/materialização e data).
- `CAMPO-02` Indivíduo/sexo/estágio/tecido.
- `CAMPO-03` Cobertura (região e completeza).
- `CAMPO-04` IDs de neurônio e estabilidade.
- `CAMPO-05` Tipos e supertypes anotados.
- `CAMPO-06` Proveniência dos rótulos.
- `CAMPO-07` Neurotransmissores.
- `CAMPO-08` Regiões/neuropilos/posição.
- `CAMPO-09` Edges dirigidas e pesos.
- `CAMPO-10` Skeletons/morfologia.
- `CAMPO-11` Crosswalks e correspondências.
- `CAMPO-12` Licença/termos.
- `CAMPO-13` API/dump.
- `CAMPO-14` Formato.
- `CAMPO-15` Tamanho.
- `CAMPO-16` Checksum.

## 3. Inventário dos candidatos

### CAND-01 — FlyWire/FAFB
- Card: `research/datasets/cards/FLYWIRE-FAFB.md`
- Status: auditado (D02)
- Pendências: licença das anotações (`não encontrado`), formato/endpoint de
  esqueleto (`não confirmado`) e exigência de conta no Codex (`ambíguo`);
  auditoria de release viva em D02 é a de 2026-09-14.

### CAND-02 — hemibrain
- Card: `research/datasets/cards/HEMIBRAIN.md`
- Status: auditado (D03)
- Pendências: checksum e tamanho do export (`não encontrado`), escolha entre
  releases v1.2 e v1.2.1 e harmonização de tipos com o FlyWire (C03/D08).

### CAND-03 — BANC
- Card: `research/datasets/cards/BANC.md`
- Status: auditado (D04)
- Pendências: arquivos restritos (277/379 exigem pedido), termos do BossDB e do
  repositório de código, escolha entre v626/v888 e harmonização de tipos com
  FlyWire/hemibrain (C03/D08).

### CAND-04 — MANC
- Card: `research/datasets/cards/MANC.md`
- Status: auditado (D05)
- Pendências: formatos/tamanhos/checksums por arquivo (`não confirmado`) e
  granularidade de tipos para harmonização (C03/D08).

### CAND-05 — MAOL
- Card: `research/datasets/cards/MAOL.md`
- Status: não confirmado
- Pendências: todos os campos CAMPO-01 a CAMPO-16; auditoria em D06.

### CAND-06 — MCNS
- Card: `research/datasets/cards/MCNS.md`
- Status: não confirmado
- Pendências: todos os campos CAMPO-01 a CAMPO-16; auditoria em D07.

## 4. Regras de preenchimento

- Campo sem fonte primária permanece `não confirmado`; nenhuma célula é
  preenchida por inferência.
- Cada valor preenchido em D02–D07 exige fonte, localização, versão e data de
  acesso no card e no ledger.
- Cada campo usa um dos estados permitidos, a saber `confirmado`, `ambíguo`,
  `conflitante` ou `não encontrado`, sempre com fonte anexada.
- O status geral do card só muda com auditoria concluída e evidência anexada.
- Divergência entre releases nunca é misturada; versões são registradas
  separadamente.

## 5. Limitações

- Esquema provisório de conteúdo, congelado como processo; pode receber campo
  novo apenas com registro e justificativa antes de D02.
- Nenhuma capacidade, licença ou disponibilidade é afirmada aqui.
- Validação: `python3 tools/validate_research.py`.
