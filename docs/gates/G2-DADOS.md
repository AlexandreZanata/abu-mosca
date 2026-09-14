# Decisão do gate G2 — Dados e par do MVP

Pacote preparado pela IA executora em 2026-09-14 (D10 → G2); **nenhum critério
científico foi aprovado pela IA**. A decisão `GO`, `NO-GO` ou `REFORMULAR`
pertence à revisão humana científica e de termos. Este pacote apenas consolida
evidência, congela os cards e propõe papéis; o executor não autoriza download
integral, treino, unseal ou leitura de `data/sealed/`.

- Data/hora e fuso: 2026-09-14 10:35 -04 (preparação); decisão humana pendente
- Commit e estado dirty: preparação sobre HEAD `3ec2e6e`; modificações não
  relacionadas do workstream NEXT preservadas fora do commit; nenhum dado bruto
  no Git
- Revisores: a preencher (revisão humana científica e de termos)
- Decisão: AGUARDAR (pacote preparado; nenhuma decisão tomada pela IA)

## Pacote de revisão

- Perguntas a decidir: aprovar o MVP MANC `manc:v1.2.1` → MCNS `male-cns:v1.0`
  (DEC-SEL-01)? reservar BANC `v888` como alvo confirmatório e FlyWire `v783`
  como reserva alternativa (DEC-SEL-02)? aceitar a matriz de fallback
  (DEC-SEL-03)? manter MAOL fora do MVP e hemibrain `v1.2.1` apenas como
  comparador (DEC-SEL-04)?
- Documentos: `research/datasets/SELECAO.md`, `CROSSWALK-AUDIT.md` (D08),
  `RECURSOS.md` (D09), `INVENTARIO.md`, os seis cards, `docs/research/
  EQUIVALENCIA.md` (C03), `ESCOPO-E-HIPOTESES.md` e `PROTOCOLO-EXECUCAO.md`.
- Papéis propostos: fonte MANC (macho, VNC completo, CC BY, bucket público com
  MD5 conferido em D09); alvo-piloto MCNS (macho, SNC completo, CC BY, grafo
  público); alvo confirmatório reservado BANC; reserva alternativa FlyWire;
  comparador hemibrain; MAOL apenas uso interno (mesmo indivíduo do MCNS).
- Releases fixados: MANC `manc:v1.2.1`, MCNS `male-cns:v1.0`, BANC `v888`,
  FlyWire `v783`, hemibrain `v1.2.1`, MAOL `optic-lobe:v1.1`; trocar release
  invalida este pacote.
- Evidência externa: LIT-0001, LIT-0002, LIT-0006, LIT-0009, LIT-0010, LIT-0015,
  LIT-0019, LIT-0023, LIT-0060, LIT-0074, LIT-0078, LIT-0079.

## Cards congelados

Os arquivos abaixo foram congelados no momento do pacote; qualquer edição
posterior invalida a decisão e exige novo G2.

- SHA-256 `24ce8aa6fa14e449e0bf20043c4be1fb1a383f2fdcca6faafa1b015cff6eecc7` — `research/datasets/cards/BANC.md`
- SHA-256 `384fc927d45dba4090d792eae9545d51210a20464f6e44fae7d83a48bcf3d0b1` — `research/datasets/cards/FLYWIRE-FAFB.md`
- SHA-256 `cae2074606b87ecd40ef14a2f7a021060fe8517412ea91a62f9f92aa0a5db453` — `research/datasets/cards/HEMIBRAIN.md`
- SHA-256 `52fdffcbadda7c8cf3038fa9644243a6c328bc21438746d9e7da17a75a823a9f` — `research/datasets/cards/MANC.md`
- SHA-256 `b4c443a1f1f50be6bcbfb12eb3ba277e37b4de32fa5a1e6ad26a509bbb7d6eeb` — `research/datasets/cards/MAOL.md`
- SHA-256 `d6962dff17e7c9f5e3a6bcff1c4ea6c1bc3d6308d5db6bed0ffd80926a0b0d96` — `research/datasets/cards/MCNS.md`
- SHA-256 `a1c0016c92b2fd3078d10cc1d14f7bd2562e394f949a71f3122f5e369c0c764e` — `research/datasets/CROSSWALK-AUDIT.md`
- SHA-256 `9ecdbcc25c4c834601eae903013f65320aeab00d5e654ff75afb0b1bcd72026e` — `research/datasets/SELECAO.md`
- SHA-256 `2dd6c9a7d2f0e893bdfcc1e87539555cd58fdfa4d446d2a192d1d5d67f334505` — `research/datasets/RECURSOS.md`
- SHA-256 `6a85de2d95e3683f5ecf958fbb0e1c9b62f0c0f48bf291cbb33188c093fcc524` — `research/datasets/INVENTARIO.md`

## Critérios

- Integridade estrutural do pacote: `PASS` — `python3 tools/validate_research.py`
  confere cards congelados por SHA-256 e `python3 tools/validate_plan.py` sem
  falhas.
- Licença e termos da fonte e do alvo: `NÃO VERIFICADO` — CC BY 4.0 declarado no
  MANC e no MCNS (LIT-0074, LIT-0078/0079); revisão humana de termos e de
  redistribuição pendente.
- Comparabilidade biológica do par: `NÃO VERIFICADO` — machos adultos, VNC do
  MANC contido no SNC do MCNS, indivíduos distintos conforme auditoria D07;
  parecer científico humano pendente.
- Alvo, releases e papéis fixados: `PASS` — MANC `manc:v1.2.1` → MCNS
  `male-cns:v1.0`; BANC `v888` reservado; FlyWire `v783` como reserva;
  hemibrain `v1.2.1` comparador; MAOL excluído do MVP.
- Cobertura e qualidade dos rótulos: `NÃO VERIFICADO` — MCNS com 11.710 tipos e
  prova de leitura completa (LIT-0023); quantos tipos do MANC entram em
  known/open-set ainda depende do crosswalk com dois revisores.
- Crosswalk e circularidade: `NÃO VERIFICADO` — PAIR-04 aprovado em D08 por um
  único revisor; segundo revisor e análise de sensibilidade a rótulos derivados
  de conectividade (DEC-CW-03) pendentes.
- Recursos e hardware: `PASS` — medido em D09: 6 amostras com MD5 oficial
  conferido, projeções para 32 GB de RAM e 8 GB de VRAM; condição de
  armazenamento externo registrada para o bulk do MCNS.
- Alvo confirmatório reservado e intocado: `PASS` — BANC `v888` não foi baixado
  nem inspecionado além de metadados públicos; nenhum download integral foi
  feito (apenas amostras de D09 sob o teto de 1 GB).
- Antileakage e desenho zero-shot: `PASS` — nenhum acesso a `data/sealed`;
  papéis, zonas e firewall definidos no PROTOCOLO; R05 ainda precisa
  implementar o teste automatizado.

## Riscos e divergências

- Evidência conflitante: total de bytes do FlyWire no card diverge da soma da
  API Zenodo (10,69 GB vs 10,60 GB); BANC meta tem 188.508 linhas medidas
  contra 188.162 declaradas; varredura do MAOL no bucket público tem teto de
  20.000 objetos e não prova ausência de tabelas; contagens do MCNS divergem
  entre resumo (166.700/11.710) e PMC (166.691/11.691).
- Leakage/circularidade: anotações de tipo dos dois lados usam conectividade e
  morfologia (LIT-0002, LIT-0015, LIT-0023); MAOL é recorte do mesmo indivíduo
  do MCNS e não pode ser tratado como cross-individual; alinhamento BANC–MANC
  não pode virar feature.
- Limites biológicos/estatísticos: um indivíduo por dataset (regra C02); sem
  réplica biológica, a conclusão fica limitada aos datasets observados; a
  premissa "MCNS e MANC são espécimes distintos" é ponto de checagem humana.
- Limites de hardware/licença: 34 GB livres no host contra bulk do MCNS de
  31,3 GB; 277 de 379 arquivos do BANC restritos; anotações do FlyWire sem
  licença declarada; export do hemibrain sem tamanho/checksum oficiais.
- Proibição do gate: se nenhum par passar, não substituir por split do mesmo
  connectoma; produzir relatório de inviabilidade/reformulação com as opções
  restantes.

## Condições do G2

- Com `GO`: liberar apenas R01–R08 conforme dependências; nenhum download
  integral antes do G3, e a ingestão completa (H08) só depois do pré-registro
  aprovado.
- Antes de qualquer mapeamento manual em H07, exigir o segundo revisor do
  crosswalk e o registro de sensibilidade a rótulos circulares (DEC-CW-03).
- Antes do bulk do MCNS, resolver armazenamento externo e registrar SHA-256
  local (o dataset não publica checksum oficial).
- O alvo confirmatório reservado (BANC `v888`) permanece intocado até G6 e
  pré-registro; nenhuma análise sua pode orientar o MVP.
- Qualquer troca de release, par ou papel invalida este pacote e exige novo G2.

## Escopo liberado

- Próximas microfases autorizadas com `GO`: R01 e seguintes, na ordem do plano,
  limitadas a infraestrutura, avaliador e pré-registro.
- Trilhos explicitamente não autorizados por este gate: download integral,
  treino real, unseal, leitura de `data/sealed/` e publicação.
- Orçamento aprovado: IA baixa por microfase; sem GPU; nenhuma compra,
  cadastro, token ou contato externo autorizado por este gate.

## Assinaturas

- Responsável científico: a preencher
- Custodiante do alvo, quando aplicável: a preencher
- Revisor de termos/licenças: a preencher
