# Dataset card — FlyWire/FAFB (auditado em D02)

Status geral: `auditado (D02)` — campos preenchidos apenas com fonte primária
consultada em 2026-09-14; o que não foi verificado permanece `não confirmado`.

## Identidade e proveniência

- Nome oficial: FlyWire whole-brain connectome (FAFB); release de conectividade
  v783 e anotações v2.1.0/v3.0.0/v3.1.0 (LIT-0003, LIT-0038).
- Projeto/instituição: FlyWire Consortium, criado na Princeton University, com
  suporte do US Brain Initiative (Codex, `about_flywire`; LIT-0068).
- Espécime, sexo, estágio e indivíduo: fêmea adulta de *Drosophila
  melanogaster*; um único espécime (LIT-0001).
- Tecido/região e cobertura: cérebro inteiro, incluindo cérebro central e lobos
  ópticos; lamina e gânglio ocelar presentes no FAFB (LIT-0001, LIT-0009).
- Release/data: conectividade v783 publicada em 2024-06-02 (Zenodo API);
  anotações v2.1.0 em 2024-07-30, v3.0.0 em 2025-10-09 e v3.1.0 em 2026-07-21
  (GitHub API de releases).
- Paper primário/DOI: Dorkenwald et al. 2024, Nature,
  `10.1038/s41586-024-07558-y`; anotação companheira Schlegel et al. 2024,
  `10.1038/s41586-024-07686-5`.
- Página oficial: `https://codex.flywire.ai/` (portal primário; LIT-0001) e
  `https://flywire.ai/tos` (termos).
- Data de acesso: 2026-09-14.

## Acesso e licença

- Licença/termos, com fonte exata: release Zenodo `10.5281/zenodo.10676866` é
  `access_right: open` e licença `CC BY 4.0` (Zenodo API, campo `license`).
- Anotações (`flyconnectome/flywire_annotations`): a API do GitHub retorna
  `license: null`; licença de redistribuição `não confirmado` (LIT-0038).
- Codex: termos em `https://flywire.ai/tos`; regras de acesso pré-publicação
  documentadas na página oficial (LIT-0068). Exigência de conta para consulta
  pública: `ambíguo` (menu de conta existe; não verificado se obrigatório).
- Exige conta, token ou aprovação: `não` para o dump do Zenodo; `não
  confirmado` para as camadas vivas do Codex/CAVE.
- API, dump ou ambos: dump Feather/NPY no Zenodo; endpoints do Codex
  (`/api/download`, `/api/map_root_ids`) e acesso programático via CAVEclient,
  navis, fafbseg e natverse (LIT-0001, LIT-0068).
- URLs/identificadores persistentes: DOI `10.5281/zenodo.10676866`; portal
  `https://codex.flywire.ai/`.
- Formatos e compressão: Feather (Arrow) e `.npy` (Zenodo, descrição oficial).
- Tamanho anunciado e medido: 10.686.849.820 bytes somando os cinco arquivos do
  Zenodo (não medido localmente); `flywire_synapses_783.feather` tem
  9.492.998.242 bytes, acima do teto de 100 MB desta fase, portanto não baixado.
- Checksum fornecido ou calculado: MD5 fornecido pelo Zenodo para cada arquivo;
  exemplos: `flywire_synapses_783.feather` `f8f1b97c9d4b0ea9b4c8b287f6b99091`;
  `proofread_connections_783.feather` `f48f972d262323a102aed49af1396b8a`;
  `proofread_root_ids_783.npy` `e0e6c19732fd8c7a4e39a2d170105421`.

## Conteúdo confirmado

- IDs de neurônio: `root_id` de 64 bits; `proofread_root_ids_783.npy` traz a
  lista dos neurônios prova de leitura (Zenodo, descrição oficial).
- Arestas dirigidas e pesos: `proofread_connections_783.feather` contém pares
  pré/pós com `syn_count` por neuropila (Zenodo, descrição oficial).
- Definição de peso/sinapse: número de sinapses; `cleft_score` com threshold 50
  aplicado à release; `connection_score` não foi usado para corte (Zenodo).
- Cell types/supertypes: 8.453 tipos anotados no total; hierarquia com classe,
  tipo, hemilinagem e supertype (LIT-0002; LIT-0038 releases v2.1.0 a v3.1.0).
- Proveniência dos rótulos: NBLAST (morfologia) + rodadas de CBLAST
  (conectividade) + revisão manual e consenso entre hemisférios; 7% dos tipos
  vinham da literatura e 90% eram novos de um hemisfério (LIT-0002). Rótulos
  livres da comunidade e anotações hierárquicas por Schlegel et al. (LIT-0068).
- Neurotransmissores: probabilidades por sinapse (`gaba`, `ach`, `glut`, `oct`,
  `ser`, `da`) e médias por par em `proofread_connections`; predição de Eckstein
  et al. 2024 (LIT-0034, Zenodo).
- Regiões/neuropilos/posição: `neuropil` por sinapse e coordenadas pré/pós em
  nanômetros (Zenodo); nomenclatura em `https://codex.flywire.ai/app/neuropils`
  e em Ito et al. 2014 (LIT-0037).
- Skeletons/morfologia: morfologias reconstruídas e prova de leitura existem
  (LIT-0001); formato e endpoint de esqueleto `não confirmado` nesta auditoria.
- Correspondências/crosswalks: matching morfológico FlyWire↔hemibrain e
  heurísticas de conexão confiável (LIT-0002); anotações v3.0.0/v3.1.0 incluem
  `hemibrain_type`, `supertype`, `matching_notes` e `dimorphism` com o MaleCNS
  (LIT-0038); matching EM-LM via NeuronBridge (LIT-0027).
- Campos ausentes ou ambíguos: licença das anotações `não encontrado`;
  esqueleto `não confirmado`; migração de detecção de sinapses após julho/2025
  para o método de Yu et al. 2025, distinta da release 783, que usa Buhmann et
  al. 2021 refinado por Heinrich et al. 2018 (LIT-0068).

## Riscos para comparação

- Diferenças biológicas: um único espécime fêmea; conclusão limitada aos
  datasets observados (C02).
- Diferenças de reconstrução/threshold: corte em `cleft_score` 50 e mudança de
  método de detecção de sinapses entre releases (LIT-0068).
- Circularidade dos labels: tipos combinam morfologia e conectividade; 32% dos
  tipos do hemibrain não foram reidentificados (LIT-0002), exigindo auditoria de
  circularidade (RSK-004).
- Cobertura e seleção: cérebro inteiro, sem cordão nervoso ventral; lamina e
  gânglio ocelar presentes (LIT-0009); neurônios não prova de leitura existem no
  arquivo de sinapses (Zenodo).
- Atualizações/mutabilidade de IDs: `root_id` muda com edições; há ferramenta
  oficial de mapeamento (`/api/map_root_ids`, LIT-0068); usar materialização.
- Restrições de redistribuição: conectividade CC BY 4.0; anotações sem licença
  declarada; Codex sujeito aos termos de uso.

## Verificação local mínima

- Comando de download da amostra: não executado; apenas o arquivo de 1,1 MB
  (`proofread_root_ids_783.npy`) estaria dentro do teto de 100 MB, se necessário
  em fase futura.
- Comando de inspeção: planejado `python3 -c "import pandas as pd;
  print(pd.read_feather('proofread_connections_783.feather').head())"` e
  conferência `md5sum` contra o Zenodo.
- Contagens observadas: nenhuma (sem download nesta fase).
- Invariantes PASS/FAIL: planejados; nenhum executado.
- Pico de RAM/disco/tempo: 0 MB (nenhum download); apenas leitura de páginas
  oficiais.

## Veredito

- Veredito: `candidato`
- Justificativa e nível de confiança: conectividade dirigida e ponderada com
  licença CC BY, tipos harmonizáveis e boa documentação; confiança média-alta
  para papel de fonte, condicionada à licença das anotações e ao pareamento.
- Questões abertas: licença de redistribuição das anotações; formato/endpoint de
  esqueleto; qual materialização viva usar; custo de acesso às camadas CAVE.

## Fontes atômicas

1. Claim: release de conectividade v783, publicada em 2024-06-02, com licença
   CC BY 4.0 e cinco arquivos com MD5.
   - Fonte/localização: Zenodo API record 10676866, campos `metadata.version`,
     `metadata.license`, `files[].checksum`; acesso 2026-09-14.
   - Status: confirmado
   - Impacto: permite baixar dump estático com checksum; alvo pode usar o grafo
     público; sem token.
2. Claim: fêmea adulta única, cérebro inteiro com cérebro central e lobos
   ópticos reconstruídos e prova de leitura.
   - Fonte/localização: Dorkenwald et al. 2024, Nature,
     `10.1038/s41586-024-07558-y`, resumo e Fig. 1; acesso 2026-09-14.
   - Status: confirmado
   - Impacto: define comparabilidade biológica e limite de generalização.
3. Claim: 8.453 tipos anotados, com proveniência NBLAST+CBLAST+manual e 32% dos
   tipos do hemibrain não reidentificados.
   - Fonte/localização: Schlegel et al. 2024, Nature,
     `10.1038/s41586-024-07686-5`, resumo e Results; acesso 2026-09-14.
   - Status: confirmado
   - Impacto: insumo para C03/D08 e alerta de circularidade/estabilidade.
4. Claim: anotações versionadas v2.1.0 (2024-07-30), v3.0.0 (2025-10-09) e
   v3.1.0 (2026-07-21), com supertype, dimorfismo e vínculo ao MaleCNS.
   - Fonte/localização: GitHub API releases do repositório
     `flyconnectome/flywire_annotations`; acesso 2026-09-14.
   - Status: confirmado
   - Impacto: versões não podem ser misturadas; exige fixar release.
5. Claim: o repositório de anotações não declara licença (`license: null`).
   - Fonte/localização: GitHub API do repositório; acesso 2026-09-14.
   - Status: confirmado (ausência declarada)
   - Impacto: redistribuição de anotações permanece não confirmada.
6. Claim: sinapses da release 783 usam detecção de Buhmann et al. 2021
   refinada por Heinrich et al. 2018; releases após julho de 2025 usam o método
   de Yu et al. 2025.
   - Fonte/localização: Codex `about_flywire`, seção Data Sources; acesso
     2026-09-14.
   - Status: confirmado
   - Impacto: separar versões no pré-processamento e na comparação.
7. Claim: `cleft_score` com threshold 50 e `connection_score` não usado para
   corte; probabilidades de seis neurotransmissores por sinapse.
   - Fonte/localização: Zenodo record 10676866, descrição dos arquivos; acesso
     2026-09-14.
   - Status: confirmado
   - Impacto: define semântica de arestas e disponibilidade de atributos.
8. Claim: acesso programático por CAVEclient, navis, fafbseg e natverse, com
   portal primário Codex.
   - Fonte/localização: Dorkenwald et al. 2024, Fig. 1c e Data availability;
     acesso 2026-09-14.
   - Status: confirmado
   - Impacto: viabiliza ingestão sem download integral, conforme D03+ e H02.
9. Claim: formato/endpoint de esqueleto e exigência de conta no Codex não foram
   verificados.
   - Fonte/localização: não verificado nesta auditoria.
   - Status: não encontrado
   - Impacto: permanece pendência para H02/H03 e para o firewall.
