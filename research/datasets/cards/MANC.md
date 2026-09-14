# Dataset card — MANC (auditado em D05)

Status geral: `auditado (D05)` — campos preenchidos apenas com fonte primária
consultada em 2026-09-14; o que não foi verificado permanece `não confirmado`.

## Identidade e proveniência

- Nome oficial: MANC (Male Adult Nerve Cord) connectome; dataset `manc` no
  neuPrint, release v1.2.1 (LIT-0074).
- Projeto/instituição: FlyEM Project Team (HHMI Janelia), Cambridge
  Connectomics Group e Google Research (LIT-0074).
- Espécime, sexo, estágio e indivíduo: macho adulto; um único espécime
  (LIT-0074, LIT-0014).
- Tecido/região e cobertura: **cordão nervoso ventral completo** de macho,
  ~25% do SNC; sem cérebro nem lobos ópticos; conecta-se ao cérebro pelo
  conectivo cervical (LIT-0074). Cérebro e VNC não entram no mesmo benchmark sem
  hipótese anatômica explícita (proibição D05).
- Release/data: v1.0 em 2023-06-06 e v1.2 em 2024-03-11; neuPrint serve
  `manc:v1.2.1` (LIT-0074, LIT-0017).
- Paper primário/DOI: Takemura et al. 2024, eLife,
  `10.7554/eLife.97769`; anotação por Marin et al. 2024,
  `10.7554/eLife.97766`; circuito pré-motor por Cheong et al. 2024,
  `10.7554/eLife.96084` (LIT-0014, LIT-0015, LIT-0016).
- Página oficial: `https://www.janelia.org/project-team/flyem/manc-connectome`
  e `https://neuprint.janelia.org` (LIT-0074).
- Data de acesso: 2026-09-14.

## Acesso e licença

- Licença/termos, com fonte exata: "The MANC is licensed under CC-BY" com link
  para CC BY 4.0 na página oficial (LIT-0074).
- Exige conta, token ou aprovação: neuPrint exige conta Google para a interface
  (mesma plataforma do hemibrain); os arquivos flat do bucket público
  `flyem-manc-exports` não exigem conta.
- API, dump ou ambos: ambos — neuPrint HTTP API, `neuprint-python` e
  `neuprintr`, pacote `malevnc` (R) e flat files no bucket público; subvolumes
  de imagem via TensorStore/cloud-volume (LIT-0074).
- URLs/identificadores persistentes: portal
  `https://neuprint.janelia.org/?dataset=manc:v1.2.1`; bucket
  `https://console.cloud.google.com/storage/browser/flyem-manc-exports`;
  Neuroglancer `gs://manc-seg-v1p2/manc-v1.2.3-neuprint-layers.json`.
- Formatos e compressão: flat files no bucket (CSV/feather conforme exports),
  neuroglancer precomputed volumes para imagem/segmentação, esqueletos via
  API; formatos exatos por arquivo `não confirmado` nesta auditoria.
- Tamanho anunciado e medido: não anunciado na página; nenhum arquivo baixado
  (teto de 100 MB).
- Checksum fornecido ou calculado: `não encontrado` na página oficial.

## Conteúdo confirmado

- IDs de neurônio: IDs de segmento/corpo no neuPrint, estáveis por release
  (LIT-0074).
- Arestas dirigidas e pesos: conectoma sináptico com direção e contagem por
  sinapse; 10 milhões de sítios pré-sinápticos e 74 milhões de PSDs (LIT-0074).
- Definição de peso/sinapse: sinapses detectadas automaticamente e
  prova de leitura pela comunidade (LIT-0074, LIT-0014).
- Cell types/supertypes: anotação em diferentes granularidades por Marin et al.
  2024, com tipos sistemáticos para sensoriais, intrínsecos, ascendentes e
  eferentes não motores (LIT-0015).
- Proveniência dos rótulos: anotação sistemática com hierarquia coarse-to-fine,
  agrupamento por segmento e por hemilinagem, cruzando literatura e
  conectividade (LIT-0015).
- Neurotransmissores: predições de Eckstein et al. 2024 disponíveis para o
  MANC (LIT-0034, LIT-0074).
- Regiões/neuropilos/posição: ROIs de neuropilas e nervos definidos no volume;
  registro para o template JRC 2018 VNC disponível (LIT-0074).
- Skeletons/morfologia: esqueletos via neuPrint e pacote `malevnc` (LIT-0074).
- Correspondências/crosswalks: matches EM-LM via NeuronBridge (LIT-0027);
  comparação com o VNC feminino FANC, parcialmente prova de leitura (LIT-0074);
  vínculo ao MaleCNS nas anotações do FlyWire v3.0.0+ (LIT-0038).
- Campos ausentes ou ambíguos: formatos/tamanhos/checksums por arquivo e
  granularidade final dos tipos `não confirmados`.

## Riscos para comparação

- Diferenças biológicas: macho adulto; comparar com conectomas de fêmea (BANC,
  FANC) exige hipótese anatômica explícita e cuidado com dimorfismo.
- Diferenças de reconstrução/threshold: FIB-SEM e segmentação Google, distinta
  de FAFB (ssTEM), BANC (GridTape) e hemibrain (FIB-SEM com outro pipeline).
- Circularidade dos labels: anotação usa conectividade e morfologia (LIT-0015);
  auditoria em D08 (RSK-004).
- Cobertura e seleção: só VNC; truncamento no conectivo cervical; sem cérebro
  nem lobos ópticos (LIT-0074).
- Atualizações/mutabilidade de IDs: releases v1.0/v1.2 e materializações do
  neuPrint; fixar release.
- Restrições de redistribuição: CC BY 4.0 com atribuição; interface web exige
  conta Google.

## Verificação local mínima

- Comando de download da amostra: não executado; bucket flat files disponível
  para fase futura dentro do teto de 100 MB.
- Comando de inspeção: planejado listar o bucket e baixar um arquivo pequeno de
  anotações, conferindo contagens e esquema.
- Contagens observadas: nenhuma (sem download).
- Invariantes PASS/FAIL: planejados; nenhum executado.
- Pico de RAM/disco/tempo: 0 MB (nenhum download).

## Veredito

- Veredito: `candidato`
- Justificativa e nível de confiança: VNC completo de macho, denso e bem
  anotado, com licença CC BY e vários canais de acesso; confiança média-alta
  como candidato, condicionada à hipótese anatômica se comparado a conectomas
  de cérebro.
- Questões abertas: formatos e tamanhos por arquivo; checksum; granularidade dos
  tipos para harmonização (C03/D08); uso do FANC para comparação sexual.

## Fontes atômicas

1. Claim: ~23.000 neurônios, 10 milhões de sítios pré-sinápticos e 74 milhões
   de PSDs; VNC completo de macho, ~25% do SNC.
   - Fonte/localização: Janelia, página oficial do MANC, Getting started e
     rail; acesso 2026-09-14.
   - Status: confirmado
   - Impacto: define escala, tecido e cobertura.
2. Claim: MANC é licenciado sob CC-BY (CC BY 4.0).
   - Fonte/localização: Janelia, página oficial do MANC; acesso 2026-09-14.
   - Status: confirmado
   - Impacto: uso e redistribuição com atribuição.
3. Claim: releases v1.0 (2023-06-06) e v1.2 (2024-03-11); neuPrint serve
   `manc:v1.2.1`.
   - Fonte/localização: Janelia, página oficial, News e Getting started;
     acesso 2026-09-14.
   - Status: confirmado
   - Impacto: versões não podem ser misturadas.
4. Claim: dump flat files público em `flyem-manc-exports`; subvolumes via
   TensorStore/cloud-volume; esqueletos e consultas por neuPrint/malevnc.
   - Fonte/localização: Janelia, página oficial, seções de acesso; acesso
     2026-09-14.
   - Status: confirmado
   - Impacto: viabiliza ingestão sem download integral e define formatos.
5. Claim: tipos anotados sistematicamente com hierarquia e agrupamento por
   segmento/hemilinagem (Marin et al. 2024).
   - Fonte/localização: Marin et al. 2024, eLife,
     `10.7554/eLife.97766`, resumo; acesso 2026-09-14.
   - Status: confirmado
   - Impacto: insumo para harmonização e auditoria de circularidade.
6. Claim: pacote `malevnc` é GPL-3.0 e teve último push em 2026-07-16.
   - Fonte/localização: API do GitHub, `natverse/malevnc`; acesso 2026-09-14.
   - Status: confirmado
   - Impacto: licença de código compatível com uso interno; sem impacto nos
     dados.
7. Claim: formatos, tamanhos e checksums por arquivo não foram encontrados.
   - Fonte/localização: não encontrado na página oficial; acesso 2026-09-14.
   - Status: não encontrado
   - Impacto: integridade e planejamento de disco dependem de inspeção futura.
