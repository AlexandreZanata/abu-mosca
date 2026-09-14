# Auditoria de hemilinhagem e rascunho do crosswalk reformulado (H07)

Executada em 2026-09-14. Sem consultar scores. Fontes locais auditadas: MANC
`manc:v1.2.1` (propriedades, sha256 `0c447652…`) e MCNS `male-cns:v1.0`
(anotações, sha256 `2177e246…`). Colunas usadas: `hemilineage` (MANC) e
`trumanHl` (MCNS).

## 1. Interseção com K≥10 nos dois lados (sem scores)

- Normalização conservadora: maiúsculas, remoção de sufixos `_putN`; excluídos
  `TBD`, ausentes e o rótulo com K<10 em um dos lados (`21X`: 4/4).
- **41 rótulos compartilhados; 40 com K≥10 nos dois lados** (conjunto inicial de
  no máximo 40 classes válidas, como esperado).
- Rótulos marcados para revisão de ambiguidade: `20A.22A`, `20B.21B.22B`,
  `24B.25B` (nomes compostos) e `26X`, `27X` (progenia não identificada).
- Menores coberturas: `04A` 12/12; `17B` 36/46; `14B` 39/47; `24B.25B` 50/43.

## 2. Proveniência da classe (independência da conectividade)

- **MANC (documentado):** Marin et al. 2024 (eLife reviewed preprint 97766,
  acesso 2026-09-14) declara que a hemilinhagem é origem de desenvolvimento
  (“based on their developmental origin, i.e., hemilineage”) e descreve a
  identificação por imagens light-level, feixes de trato somático e NBLAST
  morfológico, com previsões de neurotransmissor para confirmar — **não pela
  conectividade sináptica usada como entrada do modelo**. No MANC, o tipo
  sistemático usa conectividade, mas o campo de hemilinhagem não.
- **MCNS (`trumanHl`, não confirmado):** o campo segue a nomenclatura de
  hemilinhagem de Truman (desenvolvimento), mas o método de atribuição não foi
  verificado em fonte primária acessível nesta auditoria (paper Cell pago e
  preprint não consultado em detalhe). **Não é possível afirmar independência
  suficiente do lado do alvo.**
- Consequência (condição 5 do responsável): o desfecho por hemilinhagem **não é
  materializado como confirmatório** enquanto essa prova não existir; a
  alternativa é declará-lo inconclusivo. NBLAST/coclustering/propagação devem
  ser registrados separadamente se surgirem como evidência.

## 3. Pacote preparado (para assinatura, status minuta)

- Rascunho `preregistration/crosswalk-hemilineage.draft.json`
  (sha256 `fdb8dbc8…`): 40 classes com proveniência individual (arquivos,
  hashes, colunas, contagens por lado, flag de incerteza) e desvio de revisor
  único declarado; nenhum ID de neurônio.
- Minuta de pré-registro v2: `preregistration/PROTOCOL-v2-hemilineage.md`
  (pergunta, estimando, H0/H1, métrica, SESOI, cobertura, exclusões, baselines
  e escada de claims para hemilinhagem; T0 rebaixado a exploratório e
  inconclusivo por circularidade).
- Changelog `2.0-draft` registrado; H07 permanece `[ ]` até sua decisão.

## 4. Recomendação

1. Confirmar a proveniência de `trumanHl` no paper do MCNS (ou pedir
   confirmação aos autores); sem isso, aplicar a opção 3 e declarar
   inconclusivo.
2. Sobre os 5 rótulos incertos: manter, excluir ou tratar como bloco — decisão
   sua na assinatura.
3. Se assinar a v2 com independência confirmada, materializar o label set sob
   custódia e seguir para H09.

## 5. Tentativa de confirmação do MCNS (2026-09-14, sem sucesso)

- Europe PMC (API, acesso 2026-09-14): registro PMID 42691995 /
  DOI 10.1016/j.cell.2026.08.015, `isOpenAccess: N`, `inEPMC: N` — sem texto
  completo.
- bioRxiv 10.1101/2025.10.09.680999 (v1 e v2, `.full`): HTTP 429
  (rate limit) em duas tentativas — texto completo não obtido.
- Conclusão da tentativa: a proveniência de `trumanHl` **continua não
  confirmada**; nenhuma evidência nova foi usada e a condição 5 permanece
  (desfecho não materializável como confirmatório até confirmação humana).
