# Dataset card — BANC (auditado em D04)

Status geral: `auditado (D04)` — campos preenchidos apenas com fonte primária
consultada em 2026-09-14; o que não foi verificado permanece `não confirmado`.

## Identidade e proveniência

- Nome oficial: BANC (Brain And Nerve Cord), conectoma GridTape-TEM do sistema
  nervoso central de uma fêmea adulta de *Drosophila melanogaster*.
- Projeto/instituição: Harvard Medical School (Lee lab, Phelps e Kim), com
  segmentação da Zetta AI, prova de leitura comunitária (FlyWire Consortium e
  Aelysia) e anotação por Bates e Yang (Wilson lab) (LIT-0072).
- Espécime, sexo, estágio e indivíduo: fêmea adulta única; um único espécime
  (LIT-0072, LIT-0009).
- Tecido/região e cobertura: cérebro, zona subesofágica, conectivo cervical e
  todo o cordão nervoso ventral; lamina e gânglio ocelar ausentes (LIT-0009).
- Release/data: preprint v626 (Dataverse `10.7910/DVN/8TFGGB`, snapshot
  2025-07-21) e publicação v888 (Dataverse `10.7910/DVN/7WTH1N`, versão 3.0
  liberada em 2026-07-01, snapshot CAVE 888 em 2026-04-17) (LIT-0010, LIT-0011).
- Paper primário/DOI: Bates, Phelps, Kim, Yang et al. 2026, Nature,
  `10.1038/s41586-026-10735-w` (LIT-0009).
- Página oficial: `https://banc.community` (redireciona para a wiki oficial em
  `https://github.com/jasper-tms/the-BANC-fly-connectome/wiki`), portal
  `https://codex.flywire.ai/banc` e bucket
  `gs://lee-lab_brain-and-nerve-cord-fly-connectome` (LIT-0072).
- Data de acesso: 2026-09-14.

## Acesso e licença

- Licença/termos, com fonte exata: o depósito Dataverse da publicação declara
  `license.name` "CC BY 4.0" (API do Harvard Dataverse); o repositório
  `htem/BANC-project` **não declara licença** (`license: null`, API do GitHub).
- Exige conta, token ou aprovação: o depósito tem `fileAccessRequest: true` e
  277 de 379 arquivos marcados como `restricted`; a camada CAVE pública
  (`brain_and_nerve_cord_public`) exige login Google no endpoint `/info`
  (verificado em 2026-09-14). Parte do dump **não é baixável sem pedido**.
- API, dump ou ambos: ambos — Dataverse (dump), bucket GCS, CAVE/FlyWire Codex
  (navegação e consulta), BossDB para imagens e camadas de segmentação
  (DOI `10.60533/boss-2025-941r`).
- URLs/identificadores persistentes: DOI de publicação
  `10.7910/DVN/7WTH1N`; DOI de preprint `10.7910/DVN/8TFGGB`; DOI de imagens
  `10.60533/boss-2025-941r`.
- Formatos e compressão: Feather, Parquet, CSV gzip, SWC (esqueletos), ZIP para
  meshes e snapshots de código (descrições oficiais dos arquivos no Dataverse).
- Tamanho anunciado e medido: 536.062.963.020 bytes somando 379 arquivos na
  versão 3.0 (API do Dataverse); não medido localmente.
- Checksum fornecido ou calculado: MD5 por arquivo (o depósito usa apenas MD5;
  SHA-256 `não encontrado`). Exemplos: `banc_888_meta.feather`
  `6275eda42f98c49539d1ab513d979d09` (57.550.610 bytes);
  `banc_888_synapses_v2_enriched.parquet` `8f0fa43f80dd3f7bcb011564ca640e55`
  (17.146.564.854 bytes).

## Conteúdo confirmado

- IDs de neurônio: `root_id` estável por materialização (coluna descrita em 18
  arquivos do depósito); `pre_root_id` e `post_root_id` nas tabelas de sinapse.
- Arestas dirigidas e pesos: `banc_888_synapses_v2_enriched.parquet` com
  168.951.110 linhas × 21 colunas e IDs pré/pós; contagens de sinapse por par
  nos arquivos de conectividade.
- Definição de peso/sinapse: sinapses previstas pela segmentação automática
  (Zetta AI) com versões v2/v3 de snapshot de sinapse (LIT-0010, LIT-0072).
- Cell types/supertypes: `banc_888_meta.feather` com 188.162 linhas × 79
  colunas e hierarquia `super_class > cell_class > cell_sub_class > cell_type`
  (descrição oficial do arquivo).
- Proveniência dos rótulos: anotação manual por especialistas e comunidade,
  com revisão de metadados por especialistas (LIT-0009, LIT-0072).
- Neurotransmissores: coluna `neurotransmitter` no meta e predições por sinapse
  nos arquivos enriquecidos (descrição oficial dos arquivos; LIT-0034).
- Regiões/neuropilos/posição: ROI/nervos nas tabelas e visualização oficial
  (LIT-0009, LIT-0072).
- Skeletons/morfologia: meshes e esqueletos SWC listados no depósito (LIT-0010).
- Correspondências/crosswalks: matrizes de similaridade NBLAST entre BANC e
  hemibrain, FAFB, FANC, MANC e maleCNS (LIT-0010); uso avaliativo sujeito a
  selo em D08, nunca como feature.
- Campos ausentes ou ambíguos: contagens de neurônios/sinapses variam por
  versão e fonte — Nature cita ~140.000 no cérebro e ~20.000 no VNC; a meta
  v888 tem 188.162 linhas; versões v2 do parquet têm ~169 milhões de sinapses;
  não misturar.

## Riscos para comparação

- Diferenças biológicas: um único espécime fêmea; conclusão limitada aos
  datasets observados (C02).
- Diferenças de reconstrução/threshold: GridTape-TEM e segmentação Zetta AI,
  distintas de FAFB e hemibrain; snapshots v2/v3 de sinapse coexistem.
- Circularidade dos labels: anotação de tipo pode ter usado conectividade e
  morfologia; auditoria em D08 (RSK-004).
- Cobertura e seleção: cérebro + VNC + conectivo; sem lamina nem gânglio
  ocelar; 277 arquivos restritos limitam reprodução integral.
- Atualizações/mutabilidade de IDs: materializações e versões distintas
  coexistindo (v626, v888); fixar materialização e release.
- Restrições de redistribuição: CC BY 4.0 no depósito com atribuição, mas
  arquivos restritos exigem pedido; repositório de código sem licença; BossDB
  com termos próprios não verificados.

## Verificação local mínima

- Comando de download da amostra: não executado; há arquivo abaixo de 100 MB
  (`banc_888_meta.feather`, ~57,6 MB, `restricted: false`), reservado para fase
  autorizada futura.
- Comando de inspeção: planejado `python3 -c "import pandas as pd;
  print(pd.read_feather('banc_888_meta.feather').head())"` e conferência MD5.
- Contagens observadas: nenhuma (sem download).
- Invariantes PASS/FAIL: planejados; nenhum executado.
- Pico de RAM/disco/tempo: 0 MB (nenhum download).

## Veredito

- Veredito: `candidato`
- Justificativa e nível de confiança: escopo único (cérebro + VNC do mesmo
  indivíduo), conectividade e anotações ricas e licença CC BY no depósito, mas
  com parte dos arquivos restrita e licença de código ausente. Confiança média;
  adequado como comparador e possível fonte, condicionado a acesso e ao selo.
- Questões abertas: quais arquivos restritos são essenciais; termos do BossDB;
  qual materialização usar (v626 ou v888); harmonização de tipos com FlyWire e
  hemibrain (C03/D08).

## Fontes atômicas

1. Claim: fêmea adulta única; GridTape-TEM; CNS completo com cérebro, VNC e
   conectivo; lamina e gânglio ocelar ausentes.
   - Fonte/localização: Bates et al. 2026, Nature,
     `10.1038/s41586-026-10735-w`, resumo e Methods; wiki oficial
     `jasper-tms/the-BANC-fly-connectome` Home; acesso 2026-09-14.
   - Status: confirmado
   - Impacto: define escopo e comparabilidade biológica.
2. Claim: depósito v888 (versão 3.0, liberada em 2026-07-01) com licença
   CC BY 4.0 e `fileAccessRequest: true`; 277 de 379 arquivos restritos.
   - Fonte/localização: API do Harvard Dataverse, `doi:10.7910/DVN/7WTH1N`,
     campos `license`, `fileAccessRequest`, `restricted`; acesso 2026-09-14.
   - Status: confirmado
   - Impacto: acesso parcial exige pedido; redistribuição condicionada.
3. Claim: 379 arquivos somam 536.062.963.020 bytes e usam MD5 como único
   checksum.
   - Fonte/localização: API do Harvard Dataverse, `files` e `checksumTypes`;
     acesso 2026-09-14.
   - Status: confirmado
   - Impacto: checagem de integridade por MD5; SHA-256 indisponível.
4. Claim: `banc_888_meta.feather` tem 188.162 linhas × 79 colunas com
   hierarquia de classes e `neurotransmitter`; sinapses v2 enriquecidas têm
   168.951.110 linhas × 21 colunas com IDs pré/pós.
   - Fonte/localização: descrições oficiais dos arquivos no depósito
     Dataverse; acesso 2026-09-14.
   - Status: confirmado
   - Impacto: nomes/tipos de campos comprovados por schema oficial; viabiliza
     H02/H03.
5. Claim: a camada CAVE pública exige login Google no endpoint de informação.
   - Fonte/localização: requisição a
     `https://global.daf-apis.com/info/datastack/brain_and_nerve_cord_public`
     redireciona para login Google; acesso 2026-09-14.
   - Status: confirmado
   - Impacto: acesso programático requer conta; anotar no firewall e em H03.
6. Claim: o repositório `htem/BANC-project` não declara licença e teve último
   push em 2026-07-20.
   - Fonte/localização: API do GitHub; acesso 2026-09-14.
   - Status: confirmado
   - Impacto: reuso do código sem licença declarada fica não confirmado.
7. Claim: existem matrizes NBLAST entre BANC e hemibrain, FAFB, FANC, MANC e
   maleCNS no depósito.
   - Fonte/localização: descrição do depósito Dataverse e LIT-0010; acesso
     2026-09-14.
   - Status: confirmado
   - Impacto: correspondências existem, mas uso avaliativo deve ser selado
     (D08) e nunca virar feature.
8. Claim: contagens de neurônios/sinapses divergem por versão e fonte.
   - Fonte/localização: Nature (140.000 cérebro + 20.000 VNC) vs meta v888
     (188.162) vs parquet v2 (~169 milhões de sinapses) vs README do GitHub
     (~188.000 neurônios e 199 milhões de sinapses); acesso 2026-09-14.
   - Status: conflitante
   - Impacto: fixar definição e materialização; não misturar contagens.
