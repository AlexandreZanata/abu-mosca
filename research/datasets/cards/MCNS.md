# Dataset card — MCNS (auditado em D07)

Status geral: `auditado (D07)` — campos preenchidos apenas com fonte primária
consultada em 2026-09-14; o que não foi verificado permanece `não confirmado`.

## Identidade e proveniência

- Nome oficial: MaleCNS — conectoma completo do sistema nervoso central
  masculino de *Drosophila melanogaster*; dataset `male-cns:v1.0` no neuPrint
  (LIT-0078).
- Projeto/instituição: FlyEM (HHMI Janelia), University of Cambridge, MRC LMB e
  Google Research (LIT-0078).
- Espécime, sexo, estágio e indivíduo: **macho** adulto; um único indivíduo;
  inclui conectivo cervical intacto (LIT-0078, LIT-0023).
- Tecido/região e cobertura: cérebro central, lobos ópticos e cordão nervoso
  ventral completos, do mesmo indivíduo do MAOL; sem lamina/ocelo (LIT-0078,
  LIT-0023).
- Release/data: v0.9 em 2025-10-03 e v1.0 em 2026-06-08; publicação oficial em
  2026-09-03 (Cell) (LIT-0078).
- Paper primário/DOI: Berg, Beckett, Costa et al. 2026, Cell,
  `10.1016/j.cell.2026.08.015`; preprint `10.1101/2025.10.09.680999` (LIT-0023).
- Página oficial: `https://www.janelia.org/project-team/flyem/male-cns-connectome`,
  download em `https://janelia-flyem.github.io/male-cns/download/` e
  `https://neuprint.janelia.org/?dataset=male-cns%3Av1.0` (LIT-0078, LIT-0079).
- Data de acesso: 2026-09-14.

## Acesso e licença

- Licença/termos, com fonte exata: "The FlyEM Male CNS dataset is licensed under
  CC-BY" (CC BY 4.0), declarado na página oficial e na página de download
  (LIT-0078, LIT-0079).
- Exige conta, token ou aprovação: neuPrint exige conta e token de API para
  consultas; arquivos flat no bucket público não exigem conta (LIT-0079).
- API, dump ou ambos: ambos — neuPrint API, `neuprint-python`, `neuprintr` e
  pacote `malecns`; bulk em `gs://flyem-male-cns/v1.0/` (feather, SWC,
  precomputed, neo4j) (LIT-0078, LIT-0079).
- URLs/identificadores persistentes: `male-cns:v1.0`; DOI
  `10.1016/j.cell.2026.08.015`; neuroglancer
  `gs://flyem-male-cns/v1.0/male-cns-v1.0.json`.
- Formatos e compressão: Apache Arrow Feather (anotações, conectividade,
  sinapses, neurotransmissores), SWC e precomputed (esqueletos), N5 e
  precomputed (imagem/segmentação), neo4j (banco) (LIT-0079).
- Tamanho anunciado e medido: arquivos individuais anunciados com tamanho —
  anotações 13 MB, neurotransmissores 42 MB, estatísticas 780 MB, pesos de
  conectoma 1,1 GB, sin-points 12,7 GB, sin-partners 6,8 GB, tbar-NT 2,7 GB;
  nenhum foi baixado (teto de 100 MB).
- Checksum fornecido ou calculado: `não encontrado` nas páginas oficiais.

## Conteúdo confirmado

- IDs de neurônio: `body`/`body_pre`/`body_post` (segment IDs) nas tabelas de
  sinapse e conectividade; materialização v1.0 (LIT-0079).
- Arestas dirigidas e pesos: `connectome-weights` com forças de conexão
  segmento-a-segmento (grafo completo, 1,1 GB); `syn-partners` com pares
  pré/pós, confianças e neuropila primária (LIT-0079).
- Definição de peso/sinapse: contagem/força de sinapses com limiar de confiança
  `minconf-0.5` nos nomes dos arquivos (LIT-0079).
- Cell types/supertypes: tipos curados por classe, lado e hierarquia; 11.710
  tipos no resumo publicado e 11.691 no PMC/preprint; 262 específicos do macho,
  114 dimórficos e 69/71 específicos da fêmea conforme a versão (LIT-0023).
- Proveniência dos rótulos: prova de leitura completa e anotação manual com
  revisão de especialistas; expressão de *fruitless*/*doublesex* incluída
  (LIT-0023, LIT-0078).
- Neurotransmissores: `body-neurotransmitters` (agregado por neurônio) e
  `tbar-neurotransmitters` (probabilidades por pré-sinapse) (LIT-0079).
- Regiões/neuropilos/posição: segmentações de ROI de cérebro e VNC (256 nm) e
  neuropila primária por sinapse (LIT-0079).
- Skeletons/morfologia: SWC e precomputed em espaço EM, versões espelhadas e
  transformadas para o template unisex JRC2018 (LIT-0079).
- Correspondências/crosswalks: mesmo indivíduo do MAOL (lobo óptico direito);
  comparação entre sexos com o FlyWire feminino; matches EM-LM via NeuronBridge
  desde 2025-11-07; vínculos com o MANC nas anotações FlyWire v3.0+ (LIT-0078,
  LIT-0038).
- Campos ausentes ou ambíguos: contagens de neurônios e tipos divergem entre
  resumo publicado (166.700/11.710) e PMC/preprint (166.691/11.691); checksums
  por arquivo `não encontrados`.

## Riscos para comparação

- Diferenças biológicas: macho adulto; comparar com fêmea exige crosswalk e
  modelo de dimorfismo (LIT-0023).
- Diferenças de reconstrução/threshold: FIB-SEM e pipeline Google com limiar
  `minconf 0.5`; releases v0.9/v1.0 coexistem (LIT-0079).
- Circularidade dos labels: anotação usa conectividade, morfologia e expressão
  gênica (LIT-0023); auditoria em D08 (RSK-004).
- Cobertura e seleção: SNC completo sem lamina/ocelo; prova de leitura completa
  declarada (LIT-0078).
- Atualizações/mutabilidade de IDs: v0.9 e v1.0 têm materializações distintas;
  **não fundir releases nem indivíduos por semelhança de nome** — MCNS e MANC
  são espécimes diferentes (proibição D07).
- Restrições de redistribuição: CC BY 4.0 com atribuição; token neuPrint para
  API.

## Verificação local mínima

- Comando de download da amostra: não executado; o arquivo de anotações de
  13 MB está dentro do teto e é reservado para fase autorizada futura.
- Comando de inspeção: planejado baixar
  `body-annotations-male-cns-v1.0-minconf-0.5.feather` e conferir contagens e
  esquema com pandas; conferir `body-stats` apenas se necessário.
- Contagens observadas: nenhuma (sem download).
- Invariantes PASS/FAIL: planejados; nenhum executado.
- Pico de RAM/disco/tempo: 0 MB (nenhum download).

## Veredito

- Veredito: `candidato`
- Justificativa e nível de confiança: SNC completo de macho com anotações ricas,
  esqueletos em múltiplos espaços, bulk acessível e licença CC BY; confiança
  média-alta, condicionada a fixar v1.0 e a resolver a divergência de contagens.
- Questões abertas: contagens oficiais; checksums; uso das versões espelhadas;
  harmonização com FlyWire/MAOL (C03/D08) e papéis no benchmark (G2).

## Fontes atômicas

1. Claim: primeiro conectoma completo do SNC masculino (cérebro, lobos ópticos
   e VNC) com conectivo cervical intacto; estende o MAOL do mesmo espécime.
   - Fonte/localização: Janelia, página oficial do Male CNS Connectome; acesso
     2026-09-14.
   - Status: confirmado
   - Impacto: define indivíduo e cobertura.
2. Claim: licença CC-BY (CC BY 4.0), declarada na página oficial e na página de
   download.
   - Fonte/localização: Janelia e janelia-flyem.github.io/male-cns/download;
     acesso 2026-09-14.
   - Status: confirmado
   - Impacto: uso e redistribuição com atribuição.
3. Claim: releases v0.9 (2025-10-03) e v1.0 (2026-06-08); publicação Cell em
   2026-09-03; NeuronBridge desde 2025-11-07.
   - Fonte/localização: Janelia, página oficial, seção News; acesso
     2026-09-14.
   - Status: confirmado
   - Impacto: fixar release; histórico de atualizações.
4. Claim: bulk em `gs://flyem-male-cns/v1.0/` com anotações (13 MB),
   neurotransmissores (42 MB), estatísticas (780 MB), pesos de conectoma
   (1,1 GB), sin-points (12,7 GB), sin-partners (6,8 GB) e tbar-NT (2,7 GB),
   em Feather; esqueletos em SWC/precomputed e neo4j.
   - Fonte/localização: página oficial de download, seções Annotations,
     Connectivity e Skeletons; acesso 2026-09-14.
   - Status: confirmado
   - Impacto: formatos, tamanhos e acesso programático comprovados.
5. Claim: `syn-partners` tem colunas `x_pre`, `y_pre`, `z_pre`, `body_pre`,
   `conf_pre`, `x_post`, `y_post`, `z_post`, `body_post`, `conf_post`,
   `primary_post`.
   - Fonte/localização: página oficial de download; acesso 2026-09-14.
   - Status: confirmado
   - Impacto: schema de arestas comprovado para H02/H03.
6. Claim: contagens divergem entre resumo publicado (166.700 neurônios,
   11.710 tipos) e PMC/preprint (166.691 e 11.691).
   - Fonte/localização: Cell e PMC (LIT-0023); acesso 2026-09-14.
   - Status: conflitante
   - Impacto: registrar versão e não misturar contagens.
7. Claim: checksums por arquivo não foram encontrados.
   - Fonte/localização: não encontrado nas páginas oficiais; acesso 2026-09-14.
   - Status: não encontrado
   - Impacto: integridade dependerá de hash calculado no download.
