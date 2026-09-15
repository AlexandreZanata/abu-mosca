# Decisão do gate G5 — benchmark, baselines e liberação do MVP neural

Pacote preparado pela IA executora em 2026-09-15 09:12 -04; **nenhum critério
científico foi aprovado pela IA**. A decisão `GO` foi tomada pela revisão humana
em 2026-09-15, **condicionada ao modo exploratório**; o executor apenas
registrou o parecer. O dataset permanece **exploratório** (G4) e o desfecho
confirmatório segue **inconclusivo por circularidade** (H07; changelog 2.3), sem
label set; M08–M10 não ficam automaticamente autorizadas.

- Data/hora e fuso: pacote preparado em 2026-09-15 09:12 -04 (commit `4c9a0dd`);
  decisão humana registrada em 2026-09-15 (hora não informada pelo revisor)
- Commit e estado dirty: registro no commit desta fase; preparação sobre HEAD
  `4c9a0dd`; árvore de fase limpa
- Revisores: Alexandre Zanata (revisor único; responsável científico, custódia
  do alvo e método/estatística acumulados; limitação declarada)
- Decisão: GO condicionado ao modo exploratório (registrado pelo executor a
  partir do parecer humano de 2026-09-15)

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
  máxima 0,0) com partição carregada idêntica. Pendência aberta: negativos
  pareados por grau mantiveram o degree-only acima do acaso (0,494810 vs
  0,090909) — insuficiência do pareamento por mediana; o comparador degree-only
  pré-registrado permanece o controle principal e o novo pareamento/
  estratificação por consulta deve ser definido e testado antes de qualquer
  avaliação futura (M09).
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
  (M08) não tem desfecho; o GO libera apenas o caminho exploratório (M01–M07 e
  diagnósticos) e M08 exige decisão humana própria.
- **Decisão do revisor (2026-09-15):** as quatro perguntas do pacote foram
  respondidas com `GO` condicionado; os dois critérios humanos foram marcados
  `PASS` exclusivamente para o escopo exploratório, sem representar validação
  confirmatória.

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
- Revisor de método/estatística confirma que avaliação, nulos e comparadores são confiáveis: `PASS` — PASS para exploração: implementação e controles suficientes para desenvolvimento e comparação interna na fonte; a pendência do pareamento por grau impede tratá-los como validação confirmatória (Alexandre Zanata, 2026-09-15).
- Responsável científico confirma cobertura, limites (H07 inconclusivo) e libera o MVP apenas exploratório: `PASS` — PASS para exploração: H07 reconhecido como inconclusivo, limites aceitos e nenhuma autorização de avaliação selada ou claim confirmatório (Alexandre Zanata, 2026-09-15).

## Riscos e divergências

- H07 inconclusivo: não existe desfecho confirmatório nem label set; M08–M10 ficam bloqueadas até decisão humana específica com desfecho independente válido.
- Pendência B09 aberta: negativos pareados por grau não neutralizam o grau (0,494810 vs acaso 0,090909); não é mitigação concluída — M09 deve definir e testar novo pareamento/estratificação por consulta, mantendo o degree-only obrigatório.
- B06/B07 são transdutivos e não comparáveis zero-shot; B08 é transdutivo e a paridade numérica com a publicação é não verificável (só figura).
- Um único indivíduo-fonte e nenhuma réplica biológica; revisor único acumulando papéis (limitação declarada).
- Rewiring preserva graus de contagem, não graus ponderados; a partição por hash depende do ID (sensibilidade +0,028130 registrada).
- Todos os resultados são exploratórios e limitados à fonte observada; nenhum claim de transferência é autorizado.

## Condições do G5

1. Liberar imediatamente M01–M07 e a medição de recursos de M04, sempre em modo
   exploratório.
2. M08–M10 não ficam automaticamente autorizadas. M08 exige nova decisão humana
   e um desfecho independente válido; H07 permanece inconclusivo por
   circularidade e não existe label set confirmatório.
3. Proibir unseal, acesso a rótulos-alvo, tuning no alvo, publicação e qualquer
   claim confirmatório de transferência.
4. A falha dos negativos pareados por grau permanece pendência aberta, não
   mitigação concluída; o baseline degree-only continua obrigatório e o novo
   pareamento/estratificação por consulta deve ser definido e testado antes de
   qualquer avaliação futura.
5. M04 deve medir VRAM, RAM e tempo antes de treino longo; o teto de 6,5 GB de
   VRAM não pode ser aumentado sem nova decisão.
6. Qualquer mudança em dataset, firewall, métricas, rótulos ou protocolo exige
   nova versão e nova revisão do gate.
7. Todos os resultados devem ser identificados claramente como exploratórios e
   limitados à fonte observada.

## Escopo liberado

- Próximas microfases autorizadas: M01–M07 e a medição de recursos de M04, em
  modo exploratório.
- Não autorizadas: M08–M10 (M08 exige nova decisão humana e desfecho
  independente válido), unseal, leitura de dados selados, acesso a rótulos-alvo,
  tuning no alvo, publicação, claims confirmatórios e Experimento C.
- Orçamento aprovado: IA baixa por microfase; GPU smoke/piloto conforme R07;
  teto de 6,5 GB de VRAM, sem aumento sem nova decisão.

## Emenda 3.0 — revisão da condição 6 (2026-09-15)

A emenda do grid de parâmetros do R07 §5 (changelog 3.0; decisão humana opção
(a) da nota de bloqueio da M02, Alexandre Zanata, 2026-09-15) foi revisada
conforme a condição 6 deste gate: o grid passa a produzir **1.009.152–1.009.800
parâmetros** (dim 576/2 camadas e dim 408/3 camadas), dentro do intervalo de
1–3M do MVP, sem qualquer outra alteração de protocolo. Verificações do M02
regeradas com o grid emendado (`artifacts/reports/M02-GRAPHSAGE.md` e `.json`;
teto de 6,5 GB de VRAM preservado, sonda CUDA em 68,4 MiB). As demais condições
do G5 permanecem inalteradas e a liberação continua **apenas exploratória**.

## Assinaturas

- Responsável científico: Alexandre Zanata — GO condicionado ao modo exploratório em 2026-09-15 (revisor único, papel acumulado, limitação declarada)
- Custodiante do alvo: Alexandre Zanata — papel acumulado; nenhum unseal autorizado, 2026-09-15
- Revisor de método/estatística: Alexandre Zanata — revisão única, válida somente para o escopo exploratório, 2026-09-15
