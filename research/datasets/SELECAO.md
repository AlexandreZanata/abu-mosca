# Seleção de datasets, papéis e fallback (D10 — proposta para o gate G2)

Documento preparado pelo executor em 2026-09-14 (D10). Contém uma **proposta
técnica de papel por dataset, um MVP A→B e uma matriz de fallback**, todos
pendentes de revisão humana no gate G2: escolher o par fonte/alvo e confirmar
comparabilidade biológica é decisão humana (PROTOCOLO-EXECUCAO, seção
"Decisões que exigem revisão humana"). Nenhuma decisão deste documento está
aprovada pela IA; nenhum download integral foi feito; nenhum arquivo selado foi
lido.

## 1. Estado e escopo

- Entradas: cards auditados D02–D07, `docs/research/EQUIVALENCIA.md` (C03),
  `research/datasets/CROSSWALK-AUDIT.md` (D08 aprovado: PAIR-01 a PAIR-07 e
  DEC-CW-01 a DEC-CW-04), `research/datasets/RECURSOS.md` (D09),
  `docs/ESCOPO-E-HIPOTESES.md` (H1/H0, trilhos A/B/C) e regras do
  PROTOCOLO.
- Critérios de ranking: comparabilidade biológica (sexo/estágio/tecido),
  independência (indivíduo e proveniência do rótulo), cobertura e qualidade de
  labels, licença, acesso (conta, dump, checksum), escala frente à RTX 4060
  (8 GB VRAM, 32 GB RAM) e risco de circularidade.
- Escala de notas de 0 a 3 por critério; para circularidade a nota é invertida
  (3 = risco baixo). Notas resumem evidência dos cards; não somam critérios
  heterogêneos em um índice único.
- Situação de acesso nesta fase: somente as amostras mínimas de D09 foram
  baixadas; nada além disso foi obtido.

## 2. Notas por dataset

| Dataset (release) | Comparabilidade | Independência | Labels | Licença | Acesso | Escala | Circularidade (inv.) | Papel proposto |
|---|---|---|---|---|---|---|---|---|
| MANC (`manc:v1.2.1`) | 3 (macho; VNC completo) | 3 (espécime distinto do MCNS/MAOL por D07) | 3 (anotação sistemática, hierarquia; LIT-0015) | 3 (CC BY 4.0; LIT-0074) | 3 (bucket público; MD5 conferido em D09) | 3 (23 mil neurônios; 5,24M arestas traçadas medidas) | 2 (rótulo usa conectividade+morfologia) | Fonte primária |
| MCNS (`male-cns:v1.0`) | 3 (macho; SNC completo inclui o VNC) | 3 (espécime distinto do MANC; mesmo do MAOL; LIT-0023) | 3 (prova de leitura completa; 11.710 tipos; LIT-0023) | 3 (CC BY 4.0; LIT-0078/0079) | 2 (flat público; checksum oficial não encontrado; bulk 31,3 GB) | 2 (166.700 neurônios; alvo para inferência; pesos 1,05 GB) | 2 (rótulo usa conectividade+morfologia) | Alvo-piloto |
| BANC (`v888`) | 2 (fêmea; SNC completo; sexo distinto) | 2 (um espécime; parte do dump restrita) | 3 (hierarquia de classes; 188.508 linhas medidas) | 2 (CC BY 4.0 no depósito; 277/379 arquivos restritos; código sem licença) | 1 (depósito com pedido de acesso; CAVE exige login) | 2 (169M sinapses; pico projetado 7,6–15,2 GB; parquet 17,15 GB) | 2 (anotação manual) | Alvo confirmatório reservado |
| FlyWire (`v783`) | 2 (fêmea; cérebro completo; sexo distinto) | 2 (um espécime; anotações sem licença declarada) | 2 (8.453 tipos, mas 32% dos tipos do hemibrain não reidentificados; LIT-0002) | 2 (grafo CC BY 4.0; anotações `license: null`; LIT-0001/D02) | 3 (Zenodo com MD5; sem conta; 10,60 GB listados) | 2 (139.255 neurônios medidos; 9,49 GB de sinapses) | 1 (tipos derivados de conectividade e morfologia) | Reserva alternativa de alvo |
| hemibrain (`v1.2.1`) | 1 (fêmea; cérebro parcial; bordas truncadas) | 2 (um espécime) | 2 (5.235/5.620 tipos; 32% não reidentificados; LIT-0002) | 3 (CC BY 4.0; LIT-0070) | 1 (export sem tamanho/checksum; interface exige conta) | 3 (~25 mil neurônios; ~20M sinapses) | 1 (mesma proveniência do FlyWire) | Comparador obrigatório (ESCOPO) |
| MAOL (`optic-lobe:v1.1`) | 2 (macho; lobo óptico direito) | 1 (mesmo indivíduo do MCNS; LIT-0019) | 3 (732 tipos; LIT-0019) | 3 (CC BY 4.0; LIT-0076) | 2 (tabelas não expostas no bucket público em D09; neuPrint exige conta) | 3 (52.445 neurônios; 6,48M conexões) | 2 (uso interno) | Uso interno apenas; proibido no MVP |

## 3. Ranking dos pares aprovados em D08

| Ordem | Par (PAIR) | Por que está nesta posição | Veredito para o MVP |
|---|---|---|---|
| 1 | PAIR-04 MCNS ↔ MANC (VNC de machos distintos) | Mesmo sexo; tecido sobreposto (VNC dentro do SNC); crosswalk aprovado com tipos correspondentes documentados (LIT-0038, LIT-0015, LIT-0079) | **MVP proposto: MANC → MCNS** |
| 2 | PAIR-02 FlyWire ↔ MCNS (fêmea ↔ macho) | Dimorfismo já anotado (LIT-0038); Crosswalk médio; custo de alvo aceitável; dependente de licença das anotações do FlyWire | Reserva alternativa de alvo |
| 3 | PAIR-07 BANC ↔ MCNS (fêmea ↔ macho) | CNS completos; crosswalk por isomorfismo/dimorfismo; acesso parcial restrito | Alvo confirmatório alternativo |
| 4 | PAIR-06 BANC ↔ FlyWire | NBLAST disponível (LIT-0010), mas os dois lados femininos exigem hipótese; sem sexo cruzado não replica o MVP | Reserva de Nível 2 |
| 5 | PAIR-05 MANC ↔ BANC | Mesma região (VNC), sexos distintos; alinhamento topológico publicado (LIT-0060) gera circularidade alta se virar feature | Fallback de emergência |
| 6 | PAIR-01 FlyWire ↔ hemibrain | Sobreposição parcial de cérebro; circularidade alta; 32% dos tipos não reidentificados; acesso do hemibrain sem checksum | Comparador/baseline, nunca MVP |
| 7 | PAIR-03 MCNS ↔ MAOL | **Mesmo indivíduo**: é recorte anatômico, não correspondência entre indivíduos | **Proibido no MVP**; só checagem interna |

Por que não escolher o par mais barato de baixar: FlyWire→hemibrain tem escala
pequena, mas acumula circularidade alta, tipos não reidentificados e acesso sem
tamanho/checksum. O MVP MANC→MCNS se justifica por comparabilidade (mesmo sexo,
mesma região) e crosswalk aprovado; o custo menor do MANC é consequência, não
critério (proibição de conveniência de download).

## 4. Papéis propostos

- **Fonte: MANC (`manc:v1.2.1`).** Grafo e rótulos de tipo podem ser usados para
  treino auto-supervisionado, probe e avaliação interna; release fixada em
  v1.2.1; flat files públicos com MD5 verificável (D09). Rótulos entram apenas
  no probe/baselines definidos; nenhum campo de região, posição ou
  neurotransmissor no trilho A.
- **Alvo-piloto: MCNS (`male-cns:v1.0`).** Grafo público usado somente em
  inferência; tipos e crosswalk avaliativo ficam selados com o custodiante;
  known/open-set e regra de circularidade seguem PAIR-04/DEC-CW-03.
- **Alvo confirmatório reservado: BANC (`v888`).** Independente em indivíduo,
  sexo e pipeline; só se abre depois de G6/pré-registro, com checagem de acesso
  restrito e de disco; não orienta nenhum ajuste do MVP.
- **Reserva alternativa de alvo: FlyWire (`v783`).** Usar apenas se o MCNS falhar
  por acesso/termos; pendência de licença das anotações permanece registrada.
- **Comparador obrigatório: hemibrain (`v1.2.1`)** mais dados do FlyWire para
  reidentificação por NBLAST, conforme `ESCOPO-E-HIPOTESES.md`; entra como
  literatura/baseline, não como alvo.
- **Uso interno: MAOL.** Só checagens anatômicas; é proibido tratar MAOL↔MCNS
  como transferência entre indivíduos ou somar os dois como réplicas.
- **Independência de indivíduos:** MCNS e MANC são espécimes distintos conforme
  a auditoria D07; qualquer evidência nova que contrarie isso bloqueia o MVP e
  exige decisão humana (proibição de chamar recorte do mesmo indivíduo de
  cross-individual).

## 5. Condições de defensabilidade do MVP MANC → MCNS

1. Crosswalk PAIR-04 confirmado por dois revisores antes de qualquer mapeamento
   manual em H07 (limitação já registrada em D08); known/open-set por tipo
   ficam no pacote selado.
2. Sensibilidade a rótulos circulares (tipos anotados com conectividade) com
   exclusão opcional já prevista em DEC-CW-03.
3. Acesso: MANC com MD5 oficial conferido (D09); MCNS sem checksum oficial, logo
   tamanho oficial (API GCS) + SHA-256 local registrados no download (R03/H03).
4. Disco: 34 GB livres hoje não comportam MCNS completo (31,3 GB) com margem;
   exige armazenamento externo ou liberação de espaço antes da ingestão.
5. Escala: treino da fonte dentro de 6,5 GB de VRAM (M04); o alvo é apenas
   inferência; nenhum treino no MCNS.
6. Licença: CC BY 4.0 nos dois lados, com atribuição; nenhum dado bruto no Git.
7. Se qualquer condição falhar, aplicar a matriz de fallback da seção 6 e manter
   a fase bloqueada até G2.

## 6. Matriz de fallback

| Falha | Gatilho/verificação | Fallback definido |
|---|---|---|
| Incompatibilidade de crosswalk | known/open-set insuficiente (ex.: menos de ~20 tipos harmonizáveis ou dois revisores não concordam) | Trocar para PAIR-05 (MANC→BANC, mesma região, hipótese de dimorfismo explícita) ou reduzir a avaliação a supertype/família e registrar limitação; se nada harmonizar, declarar inconclusivo no G2 |
| Acesso negado (termos, restrição ou conta) | MCNS bulk indisponível, pedido de acesso não aprovado ou token obrigatório para o grafo | Alvo alternativo FlyWire v783 (Zenodo, MD5, sem conta, LIT-0001) com PAIR-02; se nenhum alvo sobrar, NO-GO documentado no G2 |
| Ausência de crosswalk | Nenhuma correspondência publicada aceitável para o par | Usar apenas matrizes/linhagens já publicadas sob selagem (BANC LIT-0010; FlyWire dimorphism LIT-0038) e dois revisores; sem isso, não substituir por proxy nem por split do mesmo connectoma |
| Falta de réplica biológica | Um indivíduo por dataset (regra C02), sem segundo macho disponível | Declarar o estudo como transferência entre os datasets observados; replicação só no Nível 2 (S10 leave-one-connectome-out com BANC) e nunca como réplica biológica independente |
| Escala/disco insuficiente | Bulk do alvo excede o disco aprovado | Reduzir alvo ao `connectome-weights` (1,05 GB) sem `syn-points`/`syn-partners`; se ainda exceder, adiar por armazenamento externo ou usar API neuPrint sob conta aprovada |
| Licença das anotações (FlyWire) | Redistribuição do probe proibida | Não usar FlyWire como fonte de rótulos; mantê-lo como alvo com labels selados e registrar a limitação |

## 7. Efeito nos recursos (base D09)

- MVP MANC→MCNS: download mínimo para treino da fonte e inferência no alvo ≈
  MANC flat files de conectividade (1,7 GB) + anotações MCNS (14,5 MB) + pesos
  MCNS (1,05 GB) ≈ 2,8 GB, contra 34 GB livres medidos — folga suficiente.
- Se o alvo virar BANC: parquet de sinapses 17,15 GB e pico de construção de
  7,6–15,2 GB de RAM, exigindo decisão de armazenamento.
- Nenhuma projeção acima substitui medição; tetos de VRAM continuam os do
  PROTOCOLO (smoke ≤ 5 min/2 GB; piloto ≤ 30 min/6 GB).

## 8. Decisões propostas (pendentes de G2)

### DEC-SEL-01 — Aprovar o MVP MANC → MCNS
- Decisão: adotar MANC `manc:v1.2.1` como fonte e MCNS `male-cns:v1.0` como
  alvo-piloto do MVP?
- Opções: (a) aprovar; (b) reformular o par; (c) encerrar por inviabilidade.
- Recomendação: (a), cumpridas as sete condições da seção 5.
- Status: proposta (pendente de G2)

### DEC-SEL-02 — Reservas
- Decisão: reservar BANC `v888` como alvo confirmatório e FlyWire `v783` como
  reserva alternativa?
- Opções: (a) reservar ambos; (b) reservar só BANC; (c) outro.
- Recomendação: (a), sem abrir nenhum antes de G6/pré-registro.
- Status: proposta (pendente de G2)

### DEC-SEL-03 — Fallback
- Decisão: aceitar a matriz de fallback da seção 6?
- Opções: (a) aceitar; (b) endurecer gatilhos.
- Recomendação: (a).
- Status: proposta (pendente de G2)

### DEC-SEL-04 — Exclusões
- Decisão: manter MAOL fora do MVP (mesmo indivíduo) e hemibrain apenas como
  comparador?
- Opções: (a) manter; (b) rever.
- Recomendação: (a), conforme PAIR-03 e ESCOPO.
- Status: proposta (pendente de G2)

## 9. Limitações

- O ranking usa apenas evidência já auditada e registrada; nenhuma fonte nova
  foi consultada para decidir papéis, exceto a reconfirmação pública de que o
  MCNS estende o MAOL do mesmo espécime.
- Decisão final do par, comparabilidade e termos pertence ao G2 (revisão
  humana); a IA não aprova nem inicia download integral.
- MCNS e MANC foram tratados como espécimes distintos por decisão registrada em
  D07; a verificação dessa premissa é ponto de checagem do G2.
- Validação: `python3 tools/validate_research.py`.
