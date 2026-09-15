# Decisão do gate G5 — benchmark, baselines e liberação do MVP neural

Pacote preparado pela IA executora em 2026-09-15 09:12 -04; **nenhum critério
científico foi aprovado pela IA**. A decisão `AGUARDAR` cabe à revisão humana de
método. O dataset permanece **exploratório** (G4) e o desfecho confirmatório
segue **inconclusivo por circularidade** (H07; changelog 2.3), de modo que
qualquer liberação só pode ser exploratória. O executor não inicia a fase
seguinte antes da assinatura.

- Data/hora e fuso: preparação em 2026-09-15 09:12 -04 (commit desta fase)
- Commit e estado dirty: preparação sobre HEAD `c6ce188` (B09); árvore de fase limpa
- Revisores: revisão humana de método pendente (`a preencher`)
- Decisão: AGUARDAR (pacote preparado; nenhum critério assinado pela IA)

## Pacote de revisão

- **Escopo:** confirmar que avaliação, nulos e comparadores são confiáveis antes
  do MVP neural (M01–M10).
- **Avaliação (B01/B02):** uma única implementação de métricas com exemplo
  canônico conferido à mão (Macro Recall@1 0,166667; MRR/MAP 0,583333) e
  calibração/open-set com bins fixos e limiar ajustado somente na fonte.
- **Comparadores obrigatórios (B03–B08):** executados dentro da fonte —
  random estratificado 0,005662; maioria 0,001927; degree-only 0,149547;
  artesanal 0,383676; MLP 100k 0,472795, 500k 0,554048 e pareado 1-3M
  0,579626; deepwalk 0,168601; node2vec 0,158941; svd dirigido 0,324158; ase
  simetrizado 0,310022. Julgados inaplicáveis com motivo: NBLAST e NeuronBridge
  (morfologia/serviço, Experimento C), SGM (sementes = correspondências
  proibidas), bisected graph matching (referência bilateral) e FINAL
  (atributos). REGAL foi reproduzido (B08) com paridade de artefato do
  repositório e permanece transdutivo, não comparável zero-shot.
- **Nulos (B09):** permutação de rótulos degrada até 0,004817 (real 0,383676;
  p = 0,047619); rewiring preservando grau derruba o artesanal de 0,383676 para
  0,050154; permutação de IDs é invariante no nível de features (diferença
  máxima 0,0) com partição carregada idêntica. Pendência registrada: negativos
  pareados por grau mantiveram o degree-only acima do acaso (0,494810 vs
  0,090909) — investigado como insuficiência do pareamento por mediana; o
  comparador degree-only pré-registrado permanece o controle principal e
  estratos por consulta ficam para M09.
- **Congelamento:** `data/manifests/baselines-b09.json` (SHA-256
  `9359862d398f90370d68588e64ce6bd0e838a1b550d278e0c3fb269076163c52`),
  `target_data_used: false`, 11 comparadores ranqueados, melhor comparador
  **MLP pareado 1-3M** (regra source-only: maior mediana de Macro Recall@1;
  empate → mais simples) e melhor clássico artesanal, com 27/27 artefatos de
  predição verificados por SHA-256.
- **Leakage e confinamento:** firewall R05 com testes e scanner limpo; nenhum
  rótulo, crosswalk ou arquivo selado lido em B01–B09; manifesto analítico com
  `labels_used: false`.
- **Hardware:** o pré-registro fixa teto de 6,5 GB de VRAM (R07 §7) e 28 GB de
  RAM (H08); as estimativas de L06 para GraphSAGE ficam em 3–5 GB. A medição
  real de sampling/recursos é da M04 e não foi antecipada aqui.
- **Consequência de H07:** sem label set materializado, a avaliação selada
  (M08) não tem desfecho; G5 pode liberar apenas o caminho exploratório
  (M01–M07 e diagnósticos) e M08 exige decisão humana própria.
- **Perguntas a decidir:** os testes métricos e de leakage são confiáveis? os
  comparadores executados e os julgamentos de inaplicabilidade cobrem o
  necessário? o budget planejado do MVP cabe no hardware com a medição da M04
  como condição? liberar M01–M10 apenas em modo exploratório, sem unseal, sem
  rótulos-alvo e sem claims confirmatórios?

## Artefatos e hashes

- SHA-256 `ce70daff9323496943d9ed3b296ee56f07b94fff6ffd17cf3345ed40e8b1c58a` — `artifacts/reports/B09-CONTROLES.md`
- SHA-256 `e91e2d939d3a6040f5d44a294c0d07da92d79de438d539904e1f9da53394c31c` — `artifacts/reports/B09-CONTROLES.json`
- SHA-256 `9359862d398f90370d68588e64ce6bd0e838a1b550d278e0c3fb269076163c52` — `data/manifests/baselines-b09.json`
- SHA-256 `1c23a437a2392f56ff64c255772c72d8abd022c331fd4772470b808505c1bfd9` — `artifacts/reports/B01-METRICAS.md`
- SHA-256 `cc804dd5592f0513be1d74541966aaac95837879c1720edf0b9e83ad68ef505a` — `artifacts/reports/B02-CALIBRACAO-OPEN-SET.md`
- SHA-256 `05e3fbdb33086fc41d020415a5a0089baff856fa455a75601a90afd8c48a1dd6` — `artifacts/reports/B04-ARTESANAL.json`
- SHA-256 `906e9de5fd6c723613cb72e4738eb47da0a0ee9e564d5ebd8d359680b2c998d1` — `artifacts/reports/B05-MLP.json`
- SHA-256 `e905227484bb94b4ea5e7b12d024fa8a2796f8e38bb94e4023753b80b780ba65` — `artifacts/reports/B06-NODE2VEC.json`
- SHA-256 `062781f5f722348510b7fcf34747d022b8c1a59867dc2bdda0e6da65fdd0866e` — `artifacts/reports/B07-ESPECTRAL.json`
- SHA-256 `4144e1f5b5f131eb9033e1ad97e80a45a4fdcc516607ea4de8992c78ebc9e7e7` — `artifacts/reports/B08-REGAL.json`
- SHA-256 `8357d449c718a2ee2fb50b8fdda9eefcf664d4416dba19d31bec862e7c265cfb` — `docs/research/FIREWALL.md`
- SHA-256 `d4175fe78a0b895accf7400b54203ec90880287ff4b935d0a5c32bae2603732f` — `data/manifests/analitico-v1.json`

## Critérios

- Testes métricos e de classificação passam: `PASS` — 215 testes; exemplo canônico B01 conferido à mão e sem I/O.
- Calibração, open-set e incerteza com bins/threshold congelados: `PASS` — B02 com fixtures conferidas e limiar ajustado somente na fonte.
- Testes de leakage e firewall passam: `PASS` — R05 com scanner limpo, pipeline público sem selado e tentativas sentinela detectadas.
- Nulos degradam como esperado: `PASS` — B09: rótulos ≤ 0,004817 contra 0,383676; rewiring 0,383676 → 0,050154; IDs invariantes em features.
- Comparadores obrigatórios executados ou julgados inaplicáveis: `PASS` — B03–B07 executados e B08 reproduzido; NBLAST/NeuronBridge/SGM/bisected GM/FINAL julgados com motivo.
- Pacote congelado íntegro e melhor baseline pela regra source-only: `PASS` — manifesto `9359862d…`, 27/27 predições com SHA-256; melhor comparador MLP pareado 1-3M.
- Nenhuma métrica, rótulo ou estatística do alvo usada em B01–B09: `PASS` — nenhum acesso a `data/sealed/`; manifesto analítico com `labels_used: false`.
- Budget do MVP permanece dentro do hardware (planejado): `PASS` — teto de 6,5 GB de VRAM e 28 GB de RAM; estimativas 3–5 GB; medição obrigatória na M04.
- Revisor de método/estatística confirma que avaliação, nulos e comparadores são confiáveis: `NÃO VERIFICADO` — revisão humana pendente.
- Responsável científico confirma cobertura, limites (H07 inconclusivo) e libera o MVP apenas exploratório: `NÃO VERIFICADO` — revisão humana pendente.

## Riscos e divergências

- H07 inconclusivo: não existe desfecho confirmatório nem label set; M08/M09 ficam bloqueadas até decisão humana específica.
- Pendência B09: negativos pareados por grau não neutralizam o grau (0,494810 vs acaso 0,090909); M09 deve usar o comparador degree-only e/ou estratos por consulta.
- B06/B07 são transdutivos e não comparáveis zero-shot; B08 é transdutivo e a paridade numérica com a publicação é não verificável (só figura).
- Um único indivíduo-fonte e nenhuma réplica biológica; revisor único acumulando papéis.
- Rewiring preserva graus de contagem, não graus ponderados; a partição por hash depende do ID (sensibilidade +0,028130 registrada).

## Condições do G5

- Com `GO`: liberar M01–M10 apenas em modo exploratório, sobre o dataset
  congelado, sem unseal, sem rótulos-alvo, sem claim confirmatório e sem
  publicação.
- M08 (avaliação selada) exige decisão humana prévia sobre H07/label set.
- A medição de recursos da M04 é pré-condição para qualquer treino longo; o
  teto de 6,5 GB de VRAM do R07 não pode ser elevado sem novo gate.
- Qualquer alteração material em dataset, firewall ou pré-registro exige nova
  versão e re-execução deste gate.

## Escopo liberado

- Próximas microfases autorizadas com `GO`: M01–M10 na ordem do plano e em modo
  exploratório; implementações e smoke (M01–M04) imediatos.
- Trilhos explicitamente não autorizados: unseal, leitura de dados selados,
  tuning no alvo, alegação confirmatória, publicação e Experimento C.
- Orçamento aprovado (proposto): IA baixa por microfase; GPU smoke/piloto
  conforme R07; teto de 6,5 GB de VRAM.

## Assinaturas

- Responsável científico: a preencher
- Custodiante do alvo: a preencher
- Revisor de método/estatística: a preencher
