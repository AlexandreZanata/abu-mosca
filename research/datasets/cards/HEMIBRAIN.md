# Dataset card — hemibrain (auditado em D03)

Status geral: `auditado (D03)` — campos preenchidos apenas com fonte primária
consultada em 2026-09-14; o que não foi verificado permanece `não confirmado`.

## Identidade e proveniência

- Nome oficial: hemibrain connectome (dataset `hemibrain` no neuPrint; release
  atual v1.2.1, LIT-0006 e LIT-0007).
- Projeto/instituição: FlyEM Project Team, Janelia Research Campus (HHMI), com
  segmentação do Connectomics Group do Google (LIT-0070).
- Espécime, sexo, estágio e indivíduo: fêmea de 5 dias, linhagem Canton S
  G1 x w1118; um único indivíduo (LIT-0006, Methods).
- Tecido/região e cobertura: **parcial** — grande porção do cérebro central
  (mushroom body e central complex incluídos) e a maioria dos neurônios do lobo
  óptico que entram no cérebro central; neurônios truncados nas bordas do
  volume (LIT-0006, LIT-0070). Não é o cérebro inteiro nem o cordão ventral.
- Release/data: v1.0 em 2020-01-22, v1.1 em 2020-06 e v1.2 em 2020-12-23 (notas
  oficiais de release); neuPrint serve `hemibrain` v1.2.1 (LIT-0070, LIT-0007).
- Paper primário/DOI: Scheffer et al. 2020, eLife 9:e57443,
  `10.7554/eLife.57443` (LIT-0006).
- Página oficial: `https://www.janelia.org/project-team/flyem/hemibrain` e
  `https://neuprint.janelia.org` (LIT-0070).
- Data de acesso: 2026-09-14.

## Acesso e licença

- Licença/termos, com fonte exata: "Hemibrain is licensed under CC-BY" com link
  para CC BY 4.0 na página oficial (LIT-0070). O paper também declara dados
  públicos "without restriction, with only the requirement to cite the source"
  (LIT-0006, bioRxiv/eLife).
- Exige conta, token ou aprovação: neuPrint web exige login via conta Google;
  usuários que queiram permanecer anônimos podem criar conta apenas para acesso
  (LIT-0006). Os dumps em CSV/objeto não exigem conta.
- API, dump ou ambos: ambos — neuPrint HTTP API e `neuprint-python` para
  consultas; exports CSV por release em bucket oficial; DVID para reconstrução
  completa; visualização em Neuroglancer v1.2 (LIT-0070).
- URLs/identificadores persistentes: DOI Janelia
  `10.25378/janelia.11676099.v2`; portal `https://neuprint.janelia.org`; dump
  v1.2 `https://storage.cloud.google.com/hemibrain/v1.2/exported-traced-adjacencies-v1.2.tar.gz`.
- Formatos e compressão: CSV compactado nos exports; JSON/Cypher na API
  neuPrint; DVID para voxels/segmentação; SWC para esqueletos via neuPrint
  (LIT-0070; LIT-0006 para existência de esqueletos).
- Tamanho anunciado e medido: não anunciado na página; export v1.2 não baixado
  nesta fase (teto de 100 MB; tamanho não verificado).
- Checksum fornecido ou calculado: não encontrado na página oficial nesta
  auditoria (`não encontrado`).

## Conteúdo confirmado

- IDs de neurônio: IDs de corpo/segmento no neuPrint, estáveis por release;
  neurônios truncados na borda do volume (LIT-0006).
- Arestas dirigidas e pesos: ~20 milhões de sinapses químicas; export CSV traz
  conexões e decomposição por região cerebral (LIT-0006, LIT-0070).
- Definição de peso/sinapse: contagem de sinapses químicas detectadas
  automaticamente (LIT-0006).
- Cell types/supertypes: mais de 4.000 tipos distintos segundo a página oficial
  (LIT-0070); a tipagem por clustering descreve 5.235 tipos morfológicos
  (NBLAST) e 640 tipos de conectividade (CBLAST), 5.620 no total, com revisão
  manual (LIT-0002). Contagens divergem por critério e não devem ser misturadas.
- Proveniência dos rótulos: combinação de NBLAST (morfologia), CBLAST
  (conectividade) e extensa revisão manual; 7% dos tipos vinham da literatura,
  90% eram novos de um único hemisfério, com política de dividir em caso de
  incerteza (LIT-0002).
- Neurotransmissores: predições de Eckstein et al. 2024 aplicadas ao hemibrain
  (LIT-0034).
- Regiões/neuropilos/posição: decomposição de conexões por região no export CSV
  e localização das sinapses (LIT-0006, LIT-0070).
- Skeletons/morfologia: cada neurônio documentado com voxels, esqueleto com
  diâmetros de segmento e parceiros sinápticos (LIT-0006).
- Correspondências/crosswalks: matching morfológico e de conectividade com o
  FlyWire, com 32% dos tipos do hemibrain não reidentificados (LIT-0002).
- Campos ausentes ou ambíguos: checksum `não encontrado`; tamanho do export não
  verificado; contagem de tipos varia entre fontes (4.000+ na página; 5.235
  morfológicos e 5.620 totais no estudo de tipagem).

## Riscos para comparação

- Diferenças biológicas: um único espécime fêmea; conclusão limitada aos
  datasets observados (C02).
- Diferenças de reconstrução/threshold: FIB-SEM e segmentação flood-filling,
  distintos do FAFB (ssTEM); truncamento de borda cria neurônios parciais
  (LIT-0006).
- Circularidade dos labels: tipos derivados de morfologia e conectividade; 32%
  não reidentificados no FlyWire (LIT-0002), exigindo auditoria (RSK-004).
- Cobertura e seleção: cobertura parcial do cérebro central; sobreposição
  anatômica com o FlyWire não implica identidade de população (proibição D03).
- Atualizações/mutabilidade de IDs: releases v1.0 a v1.2 com errata documentada
  (LIT-0070); neuPrint serve v1.2.1; fixar release antes de usar.
- Restrições de redistribuição: CC BY 4.0 com atribuição; login Google para a
  interface web.

## Verificação local mínima

- Comando de download da amostra: não executado; nenhum arquivo do export foi
  baixado nesta fase.
- Comando de inspeção: planejado `tar -tzf exported-traced-adjacencies-v1.2.tar.gz`
  seguido de leitura CSV, se autorizado em fase futura dentro do teto.
- Contagens observadas: nenhuma (sem download).
- Invariantes PASS/FAIL: planejados; nenhum executado.
- Pico de RAM/disco/tempo: 0 MB (nenhum download).

## Veredito

- Veredito: `candidato`
- Justificativa e nível de confiança: cobertura parcial, mas densa e com
  tipagem rica e licença CC BY; adequado como comparador/fonte potencial.
  Confiança média-alta, condicionada a fixar release e à auditoria de
  circularidade.
- Questões abertas: checksum e tamanho do export; qual release usar (v1.2 ou
  v1.2.1); relação de tipos com o FlyWire após harmonização (C03/D08).

## Fontes atômicas

1. Claim: hemibrain é fêmea de 5 dias, Canton S G1 x w1118, de um único
   espécime; ~25.000 neurônios e ~20 milhões de sinapses; cobertura parcial do
   cérebro central.
   - Fonte/localização: Scheffer et al. 2020, eLife 9:e57443,
     `10.7554/eLife.57443`, Results e Methods; acesso 2026-09-14.
   - Status: confirmado
   - Impacto: define comparabilidade biológica e cobertura não equivalente.
2. Claim: hemibrain é licenciado sob CC-BY (CC BY 4.0).
   - Fonte/localização: Janelia, página oficial `/project-team/flyem/hemibrain`,
     Getting started; acesso 2026-09-14.
   - Status: confirmado
   - Impacto: permite uso com atribuição; redistribuição dos derivados OK.
3. Claim: releases v1.0 (2020-01-22), v1.1 (2020-06) e v1.2 (2020-12-23), com
   exports CSV oficiais e notas de errata.
   - Fonte/localização: Janelia, página oficial, News e Resources; acesso
     2026-09-14.
   - Status: confirmado
   - Impacto: versões não podem ser misturadas; fixar release.
4. Claim: neuPrint exige conta Google para a interface web, com opção de conta
   anônima; dados completos disponíveis por API e DVID.
   - Fonte/localização: Scheffer et al. 2020, eLife v2, seção de acesso a dados;
     acesso 2026-09-14.
   - Status: confirmado
   - Impacto: acesso programático requer conta; dumps CSV não.
5. Claim: tipagem combinou NBLAST (5.235 tipos morfológicos), CBLAST (640 tipos
   de conectividade; 5.620 total) e revisão manual; 32% dos tipos não
   reidentificados no FlyWire.
   - Fonte/localização: Schlegel et al. 2024, Nature,
     `10.1038/s41586-024-07686-5`, Results; acesso 2026-09-14.
   - Status: confirmado
   - Impacto: circularidade e estabilidade dos rótulos entram em C05/D08.
6. Claim: cada neurônio tem voxels, esqueleto com diâmetros e parceiros
   sinápticos documentados.
   - Fonte/localização: Scheffer et al. 2020, eLife, Results; acesso 2026-09-14.
   - Status: confirmado
   - Impacto: viabiliza Experimento C e inspeção local futura.
7. Claim: checksum oficial do export não foi encontrado nesta auditoria.
   - Fonte/localização: não encontrado na página oficial; acesso 2026-09-14.
   - Status: não encontrado
   - Impacto: verificação de integridade dependerá de hash calculado no download.
8. Claim: contagem de tipos difere entre fontes ("more than 4,000" na página
   oficial; 5.235/5.620 no estudo de tipagem).
   - Fonte/localização: Janelia página oficial vs. Schlegel et al. 2024;
     acesso 2026-09-14.
   - Status: conflitante (por critério de contagem)
   - Impacto: não misturar contagens; usar a definição do estudo de tipagem.
