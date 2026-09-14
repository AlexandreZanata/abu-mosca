# Dataset card — MAOL (auditado em D06)

Status geral: `auditado (D06)` — campos preenchidos apenas com fonte primária
consultada em 2026-09-14; o que não foi verificado permanece `não confirmado`.

## Identidade e proveniência

- Nome oficial: MAOL — Male Adult (right) Optic Lobe connectome; dataset
  `optic-lobe:v1.1` no neuPrint (LIT-0076, LIT-0019).
- Projeto/instituição: FlyEM Project Team (HHMI Janelia) com o Connectomics
  group do Google; catálogo complementar pela Reiser Lab (LIT-0076, LIT-0077).
- Espécime, sexo, estágio e indivíduo: **macho** adulto; mesmo indivíduo do
  volume completo de SNC masculino (cérebro, lobos ópticos e VNC interligados)
  (LIT-0019, LIT-0076).
- Tecido/região e cobertura: **lobo óptico direito**; todos os neuropilas do
  lobo óptico exceto a **lamina** (mais periférica), com R7/R8 e células da
  lamina subcontadas (LIT-0019). Não é o lobo óptico feminino do FAFB
  (LIT-0022); essa confusão é proibida nesta fase.
- Release/data: `optic-lobe:v1.1` no neuPrint; catálogo Cell Type Explorer
  publicado em 2024-06 e atualizado até 2026-07-20 (LIT-0077).
- Paper primário/DOI: Nern et al. 2025, Nature,
  `10.1038/s41586-025-08746-0` (LIT-0019).
- Página oficial: `https://www.janelia.org/project-team/flyem/optic-lobe`,
  `https://neuprint.janelia.org/?dataset=optic-lobe%3Av1.1` e
  `https://reiserlab.github.io/male-drosophila-visual-system-connectome/`
  (LIT-0076, LIT-0077).
- Data de acesso: 2026-09-14.

## Acesso e licença

- Licença/termos, com fonte exata: "The FlyEM optic lobe is licensed under
  CC-BY" com link para CC BY 4.0 (LIT-0076). O catálogo da Reiser Lab é
  CC-BY-4.0 conforme a API do GitHub (LIT-0077).
- Exige conta, token ou aprovação: neuPrint exige conta Google para a interface;
  o bucket flat e o site do catálogo não exigem conta (LIT-0076).
- API, dump ou ambos: ambos — neuPrint HTTP API, `neuprint-python` e
  `neuprintr`; flat files no bucket público `flyem-optic-lobe`; subvolumes via
  TensorStore/cloud-volume (LIT-0076).
- URLs/identificadores persistentes: `optic-lobe:v1.1` no neuPrint; DOI
  `10.1038/s41586-025-08746-0`; neuroglancer
  `gs://flyem-optic-lobe/v1.1/optic-lobe-v1.1.json`.
- Formatos e compressão: flat files no bucket (CSV/feather conforme exports),
  neuroglancer precomputed para imagem/segmentação, esqueletos via API;
  formatos exatos por arquivo `não confirmado` nesta auditoria.
- Tamanho anunciado e medido: não anunciado na página; nenhum arquivo baixado
  (teto de 100 MB).
- Checksum fornecido ou calculado: `não encontrado`.

## Conteúdo confirmado

- IDs de neurônio: IDs de segmento/corpo no neuPrint `optic-lobe:v1.1`
  (LIT-0076).
- Arestas dirigidas e pesos: conectoma sináptico do lobo óptico direito;
  contagens do neuPrint v1.1 citam 52.445 neurônios e 6.484.936 conexões
  (LIT-0020) e o paper classifica ~53.000 neurônios (LIT-0019).
- Definição de peso/sinapse: sinapses detectadas automaticamente com prova de
  leitura das regiões visuais de um lado; prova de leitura do SNC continua
  (LIT-0019).
- Cell types/supertypes: 732 tipos em quatro grupos principais — intrínsecos
  (~16.000; ~150 tipos), conectores (~32.000; 90+ tipos), projeção (~4.500;
  350 tipos) e centrífugos (280+; 100+ tipos) (LIT-0076); ~metade dos tipos
  nomeados de novo (LIT-0019).
- Proveniência dos rótulos: classificação por curadoria especializada
  integrando morfologia, conectividade, neurotransmissor e catálogo genético
  (split-GAL4) (LIT-0019).
- Neurotransmissores: identidade de neurotransmissor integrada à curadoria
  (LIT-0019); predições de Eckstein 2024 disponíveis para o volume masculino
  (LIT-0034).
- Regiões/neuropilos/posição: cinco neuropilas do lobo óptico (LA, ME, AME, LO,
  LOP), com a lamina ausente na contagem principal (LIT-0019).
- Skeletons/morfologia: morfologias reconstruídas e catálogo com morfologia
  quantificada; esqueletos via API (LIT-0019, LIT-0076).
- Correspondências/crosswalks: o MAOL é a região visual do mesmo indivíduo do
  MCNS (LIT-0023); comparação com o lobo óptico feminino do FAFB exige
  crosswalk e não é equivalência presumida (LIT-0022).
- Campos ausentes ou ambíguos: contagens divergem entre fontes (">50.000
  neurônios" na página; ~53.000 no paper; 52.445 no neuPrint v1.1);
  formatos/tamanhos/checksums por arquivo `não confirmados`.

## Riscos para comparação

- Diferenças biológicas: macho adulto, lobo óptico direito apenas; comparar com
  fêmea ou com o lobo esquerdo exige hipótese explícita.
- Diferenças de reconstrução/threshold: FIB-SEM e pipeline Google; lamina
  ausente e R7/R8 subcontados (LIT-0019).
- Circularidade dos labels: curadoria usa conectividade e morfologia (LIT-0019);
  auditoria em D08 (RSK-004).
- Cobertura e seleção: só o lobo óptico direito; assimetria entre completude de
  pré e pós-sinapses no v1.1 (LIT-0019).
- Atualizações/mutabilidade de IDs: releases do neuPrint e atualizações do
  catálogo (último push 2026-07-20); fixar versão.
- Restrições de redistribuição: CC BY 4.0 com atribuição; interface neuPrint
  exige conta Google.

## Verificação local mínima

- Comando de download da amostra: não executado; bucket flat disponível para
  fase futura dentro do teto de 100 MB.
- Comando de inspeção: planejado listar o bucket e conferir esquema de um
  arquivo pequeno de anotações contra as contagens do neuPrint.
- Contagens observadas: nenhuma (sem download).
- Invariantes PASS/FAIL: planejados; nenhum executado.
- Pico de RAM/disco/tempo: 0 MB (nenhum download).

## Veredito

- Veredito: `candidato`
- Justificativa e nível de confiança: lobo óptico masculino completo fora da
  lamina, com catálogo de tipos extenso, CC BY e canais de acesso claros;
  confiança média-alta, condicionada a crosswalk e ao selo de correspondências.
- Questões abertas: reconciliar contagens; definir uso da lamina subcontada;
  crosswalk com FAFB feminino (C03/D08); granularidade de tipos.

## Fontes atômicas

1. Claim: conectoma do lobo óptico **direito** de um macho adulto; primeiro
   região cerebral prova de leitura do volume de SNC completo do mesmo
   indivíduo; >50.000 neurônios e >700 tipos.
   - Fonte/localização: Janelia, página oficial do Optic Lobe; acesso
     2026-09-14.
   - Status: confirmado
   - Impacto: define lateralidade, sexo e cobertura.
2. Claim: licença CC-BY (CC BY 4.0) para o lobo óptico, confirmada na página
   oficial; catálogo da Reiser Lab também CC-BY-4.0.
   - Fonte/localização: página oficial Janelia e API do GitHub do repositório
     `reiserlab/male-drosophila-visual-system-connectome`; acesso 2026-09-14.
   - Status: confirmado
   - Impacto: uso e redistribuição com atribuição.
3. Claim: ~53.000 neurônios classificados em 732 tipos; lamina ausente e R7/R8
   subcontados; ~metade dos tipos nomeados de novo.
   - Fonte/localização: Nern et al. 2025, Nature,
     `10.1038/s41586-025-08746-0`, resumo e Results; acesso 2026-09-14.
   - Status: confirmado
   - Impacto: base para C03/D08 e para a auditoria de cobertura.
4. Claim: neuPrint serve `optic-lobe:v1.1`, com 52.445 neurônios e 6.484.936
   conexões.
   - Fonte/localização: Codex, dataset MAOL v1.1; acesso 2026-09-14 (LIT-0020).
   - Status: confirmado
   - Impacto: contagem do portal difere do paper; registrar versão.
5. Claim: acessos incluem neuPrint, neuroglancer precomputed, subvolumes via
   TensorStore/cloud-volume e flat files no bucket `flyem-optic-lobe`.
   - Fonte/localização: página oficial Janelia, Getting started; acesso
     2026-09-14.
   - Status: confirmado
   - Impacto: viabiliza ingestão futura com teto de disco.
6. Claim: o MAOL pertence ao mesmo volume do MCNS; o lobo óptico feminino do
   FAFB é outro dataset.
   - Fonte/localização: LIT-0023 (MCNS, Cell 2026) e LIT-0022 (parts list do
     FAFB feminino, Nature 2024); acesso 2026-09-14.
   - Status: confirmado
   - Impacto: impede misturar MAOL com o lobo óptico feminino (proibição D06).
7. Claim: formatos, tamanhos e checksums por arquivo não foram encontrados.
   - Fonte/localização: não encontrado na página oficial; acesso 2026-09-14.
   - Status: não encontrado
   - Impacto: planejamento de disco e integridade dependem de inspeção futura.
