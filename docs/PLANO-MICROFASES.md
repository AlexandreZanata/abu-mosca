# Plano de microfases — CrossConnectome-µ

## Como usar

Este plano é uma fila executável. Vale integralmente o protocolo de
`docs/PROTOCOLO-EXECUCAO.md`. A próxima IA executa somente a primeira microfase
`[ ]` cujas dependências estejam concluídas. Gates exigem revisão humana e nunca
são aprovados apenas porque o executor terminou os arquivos.

Uma fase pode ser encerrada como não aplicável somente por decisão de gate. Nesse
caso ela recebe `[x]` e evidência explícita `dispensada`, com motivo; isso não
equivale a resultado positivo.

## Escala de orçamento

- **IA baixa:** extração, implementação ou documentação guiada por critérios
  objetivos; usar o modelo econômico padrão.
- **IA baixa + revisão:** o executor prepara; uma pessoa revisa a decisão.
- **GPU smoke:** até 5 minutos e 2 GB de VRAM.
- **GPU piloto:** até 30 minutos e 6 GB de VRAM.
- **GPU confirmatória:** teto definido no pré-registro, sempre abaixo de 8 GB com
  margem operacional.

Não há autorização implícita para download sujeito a termos, publicação, upload,
compra de serviço, contato com autores ou uso de dados não públicos.

## Nível 0 — contrato científico e viabilidade

### Contrato da pergunta

- [x] **C00 — Congelar o baseline de planejamento.**
  - Objetivo: transformar estes arquivos ainda não versionados no ponto inicial
    limpo para todas as execuções futuras.
  - Entregas: validação de links/IDs/campos, prova de que `.local/` e dados/runs
    estão ignorados, registro `docs/gates/BASELINE-PLANEJAMENTO.md` e primeiro
    commit local `fase C00: congelar baseline de planejamento`.
  - Aceite: existem 81 microfases/9 gates no plano principal e 69 microfases/12
    gates no NEXT, todos com seis campos; links atuais resolvem;
    `git diff --check` passa; ambos os prompts `.local/` existem e
    `git check-ignore` confirma que não integram o commit; após o commit o status
    rastreável está limpo.
  - Proibições: não executar pesquisa, baixar dados, instalar dependências ou
    incluir o prompt privado no Git.
  - Dependências: plano atual.
  - Orçamento: IA baixa; sem GPU; uma sessão curta.
  Evidência (2026-09-14, executor): arquivos `tools/validate_plan.py`,
  `docs/gates/BASELINE-PLANEJAMENTO.md` e esta linha; fontes/versões: repositório
  local, Python 3.12.2 (stdlib) e Git 2.43.0, sem fonte externa; comandos e
  testes: `python3 tools/validate_plan.py` e smoke negativo inline,
  `git check-ignore -v .local/PROMPT-CONTINUAR.md data/raw/x runs/y artifacts/z`,
  `git diff --cached --check` e `git status --porcelain`; resultado: 81
  microfases e 9 gates com seis campos cada, 331 referências de dependência e 5
  links relativos resolvidos, `.local/`, `data/`, `runs/` e `artifacts/`
  ignorados; recursos: 13,6 MB de RAM e 0,06 s no validador, sem GPU; decisão/
  limitação: baseline congelado, validação apenas estrutural, sem julgar conteúdo
  científico; linha em branco final removida de 6 documentos preexistentes para o
  diff check passar; commit 3e9863464078d80b588a55366a8ee3d8183bc13e.

- [x] **C01 — Abrir glossário, registro de claims e registro de riscos.**
  - Objetivo: transformar termos ambíguos do briefing em vocabulário auditável.
  - Entregas: `docs/research/GLOSSARIO.md`, `CLAIMS.md` e `RISCOS.md`, com IDs
    estáveis, status e responsáveis.
  - Aceite: define fonte, alvo, zero-shot, tipo, supertype, homologia, função,
    embedding, leakage, circularidade, réplica técnica e biológica; cada claim
    futuro pode apontar para uma evidência ou permanecer explicitamente aberto.
  - Proibições: não resolver lacunas com memória da IA e não declarar dataset
    disponível.
  - Dependências: C00.
  - Orçamento: IA baixa; sem GPU; uma sessão.
  Evidência (2026-09-14, executor): arquivos `docs/research/GLOSSARIO.md`,
  `docs/research/CLAIMS.md`, `docs/research/RISCOS.md`,
  `tools/validate_research.py` e esta linha; fontes/versões: apenas documentos
  internos do projeto (`ESCOPO-E-HIPOTESES`, `PROTOCOLO-EXECUCAO` e plano),
  nenhuma fonte externa consultada, Python 3.12.2 (stdlib); comandos e testes:
  `python3 tools/validate_research.py` com smoke negativo inline (termo ausente,
  claim confirmado sem evidência, risco mitigado sem artefato e caminho citado
  quebrado), `python3 tools/validate_plan.py`, `git diff --cached --check` e
  `git status --porcelain`; resultado: 14 termos (12 obrigatórios), 15 claims
  abertos, 16 riscos abertos, 65 referências de fase e 27 caminhos citados
  válidos, nenhum dataset declarado disponível; recursos: 13,4 MB de RAM e 0,06 s
  no validador, sem GPU; decisão/limitação: registros abertos com IDs estáveis e
  definições provisórias, `confirmado`/`mitigado` exigem evidência ou artefato;
  arquivos não relacionados surgidos na árvore durante a sessão foram preservados
  fora deste commit; commit 1d103a3c649cb58dad70324a266dbd5437b23875.

- [x] **C02 — Fixar pergunta, estimando (*estimand*) e unidade de análise provisórios.**
  - Objetivo: dizer exatamente o que será estimado e em qual população observada.
  - Entregas: `docs/research/PERGUNTA-E-ESTIMANDO.md` com H0/H1, diagrama do fluxo,
    unidade de consulta, galeria e limites de generalização.
  - Aceite: separa transferência entre datasets observados de generalização para
    a população de moscas; declara que seeds e neurônios não são indivíduos.
  - Proibições: não usar “universal”, “função” ou “cross-individual” sem condição
    verificável.
  - Dependências: C01.
  - Orçamento: IA baixa + revisão; sem GPU.
  Evidência (2026-09-14, executor): arquivos
  `docs/research/PERGUNTA-E-ESTIMANDO.md`, `tools/validate_research.py` (funções
  de C02) e esta linha; fontes/versões: apenas documentos internos do projeto
  (ESCOPO, PROTOCOLO e registros de C01), nenhuma fonte externa consultada,
  Python 3.12.2 (stdlib); comandos e testes: `python3 tools/validate_research.py`
  com smoke negativo inline (seção ausente, termo restrito fora da seção,
  declaração de independência ausente e fase inexistente),
  `python3 tools/validate_plan.py`, `git diff --cached --check` e
  `git status --porcelain`; resultado: Δ condicional ao par observado, H0/H1,
  diagrama do fluxo, unidade de consulta e galeria, limites de generalização, 7
  seções obrigatórias, 22 referências de fase e 30 caminhos citados válidos;
  recursos: 13,9 MB de RAM e 0,06 s no validador, sem GPU; decisão/limitação:
  documento provisório com revisão humana pendente para G0; números finais
  (SESOI e cobertura mínima) dependem de C04/R07; nenhum dado externo consultado;
  arquivos não relacionados preservados fora do commit; commit
  cb5094be70b42beeb89e8ea740bb879d08e0bcc8.

- [x] **C03 — Definir “neurônio equivalente” e a hierarquia avaliativa.**
  - Objetivo: escolher targets cientificamente defensáveis antes de ver scores.
  - Entregas: `docs/research/EQUIVALENCIA.md` com target primário, targets
    secundários, casos one-to-one, multi-instance, unknown e regras de crosswalk.
  - Aceite: distingue mesmo tipo, supertype, homólogo, mesma região e mesma função;
    documenta quando cada relação é gold label, proxy ou hipótese; inclui regra
    para tipos ausentes, ambíguos, singleton e rótulos conflitantes.
  - Proibições: não tratar igualdade nominal entre projetos como equivalência
    confirmada e não usar correspondência no input se ela pontua o output.
  - Dependências: C01, C02.
  - Orçamento: IA baixa + revisão humana obrigatória; sem GPU.
  Bloqueio (2026-09-14, executor): pacote preparado em
  `docs/research/EQUIVALENCIA.md` (hierarquia T0–T4, relações EQ-01–EQ-05 e
  decisões DEC-EQ-01–DEC-EQ-09, todas `AGUARDANDO DECISÃO HUMANA`); fase mantida
  `[ ]` porque o orçamento C03 exige revisão humana obrigatória e o protocolo
  reserva ao revisor humano aprovar “mesmo tipo” e crosswalk; validação
  estrutural com smoke negativo em `tools/validate_research.py` (14,2 MB de RAM,
  0,07 s, sem GPU); próxima ação humana: revisar as 9 decisões; commit
  3533c2a70e51c68d0d3897143c9bbf3520957e3c.
  Evidência (2026-09-14, executor + revisor humano): arquivos
  `docs/research/EQUIVALENCIA.md` (status de EQ-01–EQ-05 e DEC-EQ-01–DEC-EQ-09
  aprovados; seção 9 com data, aprovador e escopo), `tools/validate_research.py`
  (validação de aprovação humana) e esta linha; fontes/versões: decisão do
  revisor humano registrada na sessão de 2026-09-14 (aprovação integral, sem
  exceções) e documentos internos, nenhuma fonte externa, Python 3.12.2
  (stdlib); comandos e testes: `python3 tools/validate_research.py` com smoke
  negativo inline (APROVADO sem seção de aprovação, aprovador não humano, campo
  de aprovação ausente e status inválido), `python3 tools/validate_plan.py`,
  `git diff --cached --check` e `git status --porcelain`; resultado: 9 decisões
  aprovadas por humano, 5 relações com classificação aprovada, 36 caminhos e 65
  referências de fase válidos; recursos: 14,0 MB de RAM e 0,06 s no validador,
  sem GPU; decisão/limitação: aprovação integral mantém H1 definida e congela as
  regras do MVP; a validação é estrutural e não substitui julgamento científico;
  arquivos não relacionados preservados fora do commit; commit
  40552405b9e5447c8790cb5052c54dc76beae5e4.

- [x] **C04 — Fixar desfechos, sucesso, nulidade e falsificação provisórios.**
  - Objetivo: impedir que a conclusão seja escolhida depois do resultado.
  - Entregas: `docs/research/DESFECHOS-E-FALSIFICACAO.md` com métrica primária,
    métricas secundárias, SESOI provisório, controles nulos e árvore de decisão.
  - Aceite: inclui recuperação macro, classificação, calibração, open-set,
    intervalos, degree-matched control, within-vs-cross gap e estados `sucesso`,
    `parcial`, `refutado` e `inconclusivo`.
  - Proibições: UMAP/t-SNE não contam como evidência e melhor seed não conta como
    estimativa.
  - Dependências: C02, C03.
  - Orçamento: IA baixa + revisão; sem GPU.
  Evidência (2026-09-14, executor): arquivos
  `docs/research/DESFECHOS-E-FALSIFICACAO.md`, `tools/validate_research.py`
  (funções de C04) e esta linha; fontes/versões: apenas documentos internos
  (ESCOPO, PROTOCOLO, estimando de C02 e equivalência de C03 aprovada), nenhuma
  fonte externa consultada, Python 3.12.2 (stdlib); comandos e testes:
  `python3 tools/validate_research.py` com smoke negativo inline (estado ausente,
  métrica ausente, proibição removida, seção ausente e fase inexistente),
  `python3 tools/validate_plan.py`, `git diff --cached --check` e
  `git status --porcelain`; resultado: métrica primária Macro Recall@1, 17
  marcadores obrigatórios (recuperação, classificação, calibração, open-set,
  intervalos, degree-matched, gap within-vs-cross e SESOI), 4 estados de decisão
  e proibições de UMAP/t-SNE e melhor seed; recursos: 14,6 MB de RAM e 0,06 s no
  validador, sem GPU; decisão/limitação: desfechos provisórios, números finais
  (SESOI, K e seeds) dependem de R07, estados decididos em G6 e a validação é
  apenas estrutural; arquivos não relacionados preservados fora do commit; commit
  7341d27cc4ff0b53e350787870e7b9c6b094d5d1.

- [x] **C05 — Modelar ameaças à validade e leakage.**
  - Objetivo: listar como o estudo poderia acertar pelo motivo errado.
  - Entregas: `docs/research/AMEACAS-A-VALIDADE.md` com severidade, teste de
    detecção, mitigação e risco residual.
  - Aceite: cobre IDs/ordem, grau, coordenadas/regiões, labels derivados de
    conectividade/morfologia, crosswalk circular, normalização no alvo,
    amostragem de negativos, duplicação de neurônios, sexo, tecido, cobertura,
    reconstrução, threshold e tuning pós-unseal.
  - Proibições: não classificar risco como mitigado sem teste ou artefato.
  - Dependências: C03, C04.
  - Orçamento: IA baixa + revisão; sem GPU.
  Evidência (2026-09-14, executor): arquivos
  `docs/research/AMEACAS-A-VALIDADE.md`, `tools/validate_research.py` (funções
  de C05) e esta linha; fontes/versões: apenas documentos internos (RISCOS de
  C01, estimando de C02, equivalência aprovada em C03 e desfechos de C04),
  nenhuma fonte externa consultada, Python 3.12.2 (stdlib); comandos e testes:
  `python3 tools/validate_research.py` com smoke negativo inline (tema ausente,
  mitigação sem artefato, proibição removida, severidade inválida, risco
  inexistente e seção ausente), `python3 tools/validate_plan.py`,
  `git diff --cached --check` e `git status --porcelain`; resultado: 14 ameaças
  cobrindo os 14 temas do aceite, cada uma com severidade, cenário, teste de
  detecção, mitigação planejada e risco residual `não verificado`; nenhuma
  classificação `mitigado` sem artefato; recursos: 14,8 MB de RAM e 0,07 s no
  validador, sem GPU; decisão/limitação: modelo provisório, sem código/dados e
  sem mitigação executada, severidades a revisar em D01–D10; arquivos não
  relacionados preservados fora do commit; commit
  aef8c11cee0dd61e5fa9ab890924632350ab4380.

- [x] **C06 — Criar contrato de claims e saídas negativas.**
  - Objetivo: limitar a linguagem final ao nível de evidência alcançado.
  - Entregas: `docs/research/ESCADA-DE-CLAIMS.md` e esqueleto do relatório de
    inviabilidade/reformulação.
  - Aceite: mapeia evidência mínima para “sinal topológico”, “transferência entre
    dois datasets”, “cross-individual”, “multi-connectome” e “potencialmente
    novo”; prevê publicação de resultado negativo e de benchmark inviável.
  - Proibições: não prometer paper, novidade ou causalidade.
  - Dependências: C02–C05.
  - Orçamento: IA baixa; sem GPU.
  Evidência (2026-09-14, executor): arquivos
  `docs/research/ESCADA-DE-CLAIMS.md`,
  `docs/research/RELATORIO-INVIABILIDADE-ESQUELETO.md`,
  `tools/validate_research.py` (funções de C06) e esta linha; fontes/versões:
  apenas documentos internos (CLAIMS de C01, estimando de C02, equivalência
  aprovada em C03, desfechos de C04 e ameaças de C05), nenhuma fonte externa,
  Python 3.12.2 (stdlib); comandos e testes: `python3 tools/validate_research.py`
  com smoke negativo inline (nível ausente, status inválido, liberação sem
  evidência congelada, proibição removida, claim inexistente, esqueleto sem
  marcadores e seção do esqueleto ausente), `python3 tools/validate_plan.py`,
  `git diff --cached --check` e `git status --porcelain`; resultado: 5 níveis
  (sinal topológico, transferência entre dois datasets, cross-individual,
  multi-connectome e potencialmente novo) todos `bloqueado`, saídas negativas e
  benchmark inviável previstos e esqueleto com 7 seções não preenchidas;
  recursos: 15,1 MB de RAM e 0,07 s no validador, sem GPU; decisão/limitação:
  contrato de linguagem provisório, sem dados, nenhum nível liberado e revisão
  humana em G0; arquivos não relacionados preservados fora do commit; commit
  42259a2fbfcdb0d3b47578a605c347a5eb191219.

- [x] **G0 — Aprovar o contrato científico provisório.**
  - Objetivo: decidir se a pergunta é testável antes de buscar confirmação.
  - Entregas: `docs/gates/G0-CONTRATO.md` usando o modelo de decisão.
  - Aceite: revisão humana aprova ou reformula H0/H1, equivalência, desfecho,
    falsificação e escada de claims; toda divergência fica registrada.
  - Proibições: executor de IA não assina sozinho e `AGUARDAR` não vira `GO`.
  - Dependências: C01–C06.
  - Orçamento: IA baixa para pacote; revisão humana de método.
  Bloqueio (2026-09-14, executor): pacote do gate preparado em
  `docs/gates/G0-CONTRATO.md` com decisão `AGUARDAR` e 9 critérios; os critérios
  científicos (H0/H1, equivalência, desfechos, falsificação, ameaças, firewall e
  escada de claims) estão `NÃO VERIFICADO` aguardando revisão humana de método; a
  IA não assinou nem aprovou; validação estrutural com smoke negativo em
  `tools/validate_research.py` (15,3 MB de RAM, 0,07 s, sem GPU); próxima ação
  humana: decidir GO/NO-GO/REFORMULAR e assinar; commit
  505619c3a5e545044cbc29023f8376cb6ad38673.
  Evidência (2026-09-14, executor + revisor humano): arquivos
  `docs/gates/G0-CONTRATO.md` (decisão GO, 9 critérios `PASS`, condições do GO e
  assinaturas registradas), `tools/validate_research.py` (estado aprovado do
  gate) e esta linha; fontes/versões: parecer do revisor humano de 2026-09-14
  (GO integral; nome não informado na aprovação) e documentos internos de
  C01–C06, nenhuma fonte externa, Python 3.12.2 (stdlib); comandos e testes:
  `python3 tools/validate_research.py` com smoke negativo inline (decisão GO com
  G0 aberto, assinatura pendente com GO, critério `NÃO VERIFICADO` com GO e
  critério `FAIL`), `python3 tools/validate_plan.py`, `git diff --cached --check`
  e `git status --porcelain`; resultado: GO registrado, escopo liberado para
  L01–L07 e D01–D10 conforme dependências, condições de R05/R07/G3 registradas;
  recursos: 15,3 MB de RAM e 0,07 s no validador, sem GPU; decisão/limitação:
  aprovação humana apenas registrada pelo executor, nome do responsável não
  informado, riscos seguem abertos e não mitigados; arquivos não relacionados
  preservados fora do commit; commit
  ad336fe72e1c3e97f728d05501e48442cd72a1ec.

### Literatura e novidade

- [x] **L01 — Pré-especificar a revisão de literatura.**
  - Objetivo: tornar a busca atualizável e menos suscetível a cherry-picking.
  - Entregas: `research/literature/PROTOCOL.md` com bases, strings, período,
    idiomas, inclusão/exclusão, deduplicação e esquema do ledger.
  - Aceite: consultas cobrem neuron matching, connectome alignment, cell type por
    conectividade, graph representation learning, cross-animal, morfologia e
    embeddings de connectomas; um segundo executor consegue repetir a busca.
  - Proibições: não usar apenas snippets, blogs ou resumos de IA como evidência.
  - Dependências: G0.
  - Orçamento: IA baixa + revisão; sem GPU.
  Evidência (2026-09-14, executor): arquivos `research/literature/PROTOCOL.md`,
  `tools/validate_research.py` (funções de L01) e esta linha; fontes/versões:
  apenas documentos internos (ESCOPO, PROTOCOLO, CLAIMS de C01 e gate G0),
  nenhuma fonte externa consultada, Python 3.12.2 (stdlib); comandos e testes:
  `python3 tools/validate_research.py` com smoke negativo inline (consulta
  ausente, base ausente, campo de consulta ausente, regra de evidência removida,
  campo de ledger ausente e fase inexistente), `python3 tools/validate_plan.py`,
  `git diff --cached --check` e `git status --porcelain`; resultado: 7 consultas
  (Q1–Q7) cobrindo neuron matching, connectome alignment, cell type por
  conectividade, graph representation learning, cross-animal, morfologia e
  embeddings de connectomas; 8 bases, janelas W1/W2, critérios de
  inclusão/exclusão, deduplicação, esquema de ledger/log e runbook para segundo
  executor; recursos: 15,6 MB de RAM e 0,07 s no validador, sem GPU; decisão/
  limitação: protocolo pré-especificado, nenhuma busca executada e revisão humana
  em G1; arquivos não relacionados preservados fora do commit; commit
  eca334e094c4127ab3d9a979b0ef36086401749e.

- [x] **L02 — Mapear papers primários dos connectomas candidatos.**
  - Objetivo: localizar releases, papers de dados e estudos comparativos que
    definem o contexto biológico.
  - Entregas: ledger versionado com DOI/URL, data, dataset, claim atômico e status.
  - Aceite: cada candidato tem fonte oficial ou é marcado `não encontrada`; inclui
    citation chaining para versões/subconjuntos sem misturá-los.
  - Proibições: ainda não preencher dataset cards por inferência.
  - Dependências: L01.
  - Orçamento: IA baixa; web; sem GPU; limite de fontes definido no protocolo.
  Evidência (2026-09-14, executor): arquivos `research/literature/LEDGER.tsv`,
  `research/literature/QUERY-LOG.tsv`, `research/literature/PROTOCOL.md` (v2 com
  consulta Q0 e colunas `dataset`/`claim_atomico`, registrado na seção 11),
  `tools/validate_research.py` (funções de L02) e esta linha; fontes/versões:
  buscas web de 2026-09-14 com verificação em fontes primárias (Nature, eLife,
  Zenodo, Dataverse, bioRxiv, Crossref, PMC, Codex, Janelia, banc.community e
  male-cns.janelia.org), URLs/DOIs no ledger; Python 3.12.2 (stdlib); comandos e
  testes: `python3 tools/validate_research.py` com smoke negativo inline
  (candidato sem fonte incluída, `lit_id` duplicado, status inválido, incluído
  sem DOI/URL, sem claim atômico, coluna ausente e query log ausente),
  `python3 tools/validate_plan.py`, `git diff --cached --check` e
  `git status --porcelain`; resultado: 25 registros, 10 consultas no log (inclui
  1 run descartada do PubMed) e 6 candidatos com fonte oficial — FlyWire/FAFB
  (release v783), hemibrain, BANC (v888 e v626), MANC (v1.0 e v1.2), MAOL (v1.1)
  e MCNS (male-cns v1.0), com versões separadas e sem misturar subconjuntos;
  recursos: 15,6 MB de RAM e 0,07 s no validador, sem GPU; decisão/limitação:
  mapeamento provisório, contagens do MCNS divergentes entre resumo publicado e
  PMC/preprint registradas como ambíguas, nenhum dataset card preenchido e
  revisão humana em G1; arquivos não relacionados preservados fora do commit;
  commit 581ae8d299f2182df1a36d31cdc1a992914071db.

- [x] **L03 — Revisar neuron matching e graph alignment.**
  - Objetivo: identificar métodos, supervisão, pressupostos e baselines publicados.
  - Entregas: `research/literature/ALIGNMENT.md` e entradas no ledger.
  - Aceite: para cada método registra input, uso de âncoras/rótulos, caráter
    transdutivo/indutivo, datasets, código/licença, métrica e inadequações ao
    zero-shot proposto.
  - Proibições: não chamar método supervisionado de baseline não supervisionado.
  - Dependências: L01, L02.
  - Orçamento: IA baixa; sem GPU.
  Evidência (2026-09-14, executor): arquivos `research/literature/ALIGNMENT.md`,
  `research/literature/LEDGER.tsv` (LIT-0026 a LIT-0032),
  `research/literature/QUERY-LOG.tsv` (consultas Q1/Q2),
  `tools/validate_research.py` (funções de L03) e esta linha; fontes/versões:
  buscas de 2026-09-14 verificadas em fontes primárias — Costa 2016
  (10.1016/j.neuron.2016.06.012), Clements 2024 (10.1186/s12859-024-05732-7),
  Pedigo 2022 (10.1162/netn_a_00287), Fishkind 2019
  (10.1016/j.patcog.2018.09.014), Heimann 2018 (10.1145/3269206.3271788), Zhang
  e Tong 2016 (10.1145/2939672.2939766) e Stürner 2024
  (10.1101/2024.06.04.596633); Python 3.12.2 (stdlib); comandos e testes:
  `python3 tools/validate_research.py` com smoke negativo inline (campo ausente,
  supervisão inválida, supervisão/âncora inconsistente, LIT inexistente, consulta
  Q1/Q2 ausente e seção ausente), `python3 tools/validate_plan.py`,
  `git diff --cached --check` e `git status --porcelain`; resultado: 6 métodos
  (NBLAST, NeuronBridge, bisected GM, SGM, REGAL e FINAL) com input, âncoras,
  supervisão, caráter, datasets, código/licença, métrica e inadequações; nenhum
  método transdutivo apresentado como zero-shot; 32 registros no ledger e 16
  consultas no log; recursos: 16,4 MB de RAM e 0,07 s no validador, sem GPU;
  decisão/limitação: licenças de código marcadas como não verificadas quando a
  fonte não as declarava, nenhuma métrica reproduzida e revisão humana em G1;
  arquivos não relacionados preservados fora do commit; commit
  22c58cae53b12ad7d3693cc1f412370de22ed1c0.

- [x] **L04 — Revisar predição de tipo por conectividade e morfologia.**
  - Objetivo: testar a plausibilidade e a circularidade da hipótese biológica.
  - Entregas: `research/literature/CELL-TYPE.md` com evidência a favor, contra e
    condições de validade.
  - Aceite: distingue connectivity-only, morphology-only, posição, região,
    neurotransmissor e função; registra como os labels foram originalmente
    produzidos.
  - Proibições: correlação dentro de um indivíduo não prova transferência.
  - Dependências: L01, L02.
  - Orçamento: IA baixa + revisão; sem GPU.
  Evidência (2026-09-14, executor): arquivos `research/literature/CELL-TYPE.md`,
  `research/literature/LEDGER.tsv` (LIT-0033 a LIT-0038),
  `research/literature/QUERY-LOG.tsv` (consultas Q3/Q6),
  `tools/validate_research.py` (funções de L04) e esta linha; fontes/versões:
  buscas de 2026-09-14 verificadas em fontes primárias — Scheffer 2020 e
  Schlegel 2024 (já no ledger), Mehta 2023 (10.1162/netn_a_00283), Eckstein 2024
  (10.1016/j.cell.2024.03.016), NeuNet 2024 (10.1609/aaai.v38i1.27771), CBLAST
  (github.com/connectome-neuprint/CBLAST), Ito 2014
  (10.1016/j.neuron.2013.12.017) e flywire_annotations (v2.1.0 e v3.0.0);
  Python 3.12.2 (stdlib); comandos e testes: `python3 tools/validate_research.py`
  com smoke negativo inline (campo ausente, modalidade ausente, proibição
  removida, LIT inexistente, proveniência insuficiente, consulta Q3/Q6 ausente e
  seção ausente), `python3 tools/validate_plan.py`, `git diff --cached --check` e
  `git status --porcelain`; resultado: 6 modalidades (conectividade, morfologia,
  posição, região, neurotransmissor e função) com evidência a favor, contra e
  condições de validade, 4 registros de proveniência de rótulos (hemibrain,
  FlyWire, conectomas masculinos com BANC e MANC, e nomenclatura de regiões) e a
  proibição "correlação dentro de um indivíduo não prova transferência"
  registrada; 38 registros no ledger e 23 consultas no log; recursos: 16,6 MB de
  RAM e 0,08 s no validador, sem GPU; decisão/limitação: revisão documental, sem
  dados baixados e sem métricas reproduzidas; revisão humana em G1; arquivos não
  relacionados preservados fora do commit; commit
  f70de5f59229c03e223589811525a746398ce543.

- [x] **L05 — Revisar aprendizado auto-supervisionado e embeddings de grafo.**
  - Objetivo: selecionar objetivos que possam generalizar sem node IDs.
  - Entregas: `research/literature/SSL-GRAFOS.md` com masked edge/weight,
    neighborhood reconstruction, contrastive, autoencoders e link prediction.
  - Aceite: cada família tem hipótese de sinal, atalhos prováveis, custo, suporte
    a grafo dirigido/ponderado e capacidade indutiva; inclui embeddings de
    connectomas e alegações de graph foundation models encontradas.
  - Proibições: não assumir Transformer superior nem comparar espaços
    transdutivos desalinhados como se fossem comuns.
  - Dependências: L01, L03, L04.
  - Orçamento: IA baixa; sem GPU.
  Evidência (2026-09-14, executor): arquivos `research/literature/SSL-GRAFOS.md`,
  `research/literature/LEDGER.tsv` (LIT-0039 a LIT-0048),
  `research/literature/QUERY-LOG.tsv` (consultas Q4/Q7),
  `tools/validate_research.py` (funções de L05) e esta linha; fontes/versões:
  buscas de 2026-09-14 verificadas em fontes primárias — GraphMAE 2022
  (10.1145/3534678.3539321), DGI 2019 (10.17863/cam.40744), GraphCL 2020
  (10.48550/arXiv.2010.13902), VGAE 2016 (10.48550/arXiv.1611.07308), GraphSAGE
  2017 (arXiv 1706.02216), MagNet 2021 (arXiv 2102.11391), Rosenthal 2018
  (10.1038/s41467-018-04614-w), Liu 2023 (10.48550/arXiv.2310.11829), Wang 2025
  (10.1145/3711896.3736568) e Mao 2024 (PMLR v235); Python 3.12.2 (stdlib);
  comandos e testes: `python3 tools/validate_research.py` com smoke negativo
  inline (campo, família, proibição, LIT, CEM, GFM, consulta Q4/Q7 e seção
  ausentes), `python3 tools/validate_plan.py`, `git diff --cached --check` e
  `git status --porcelain`; resultado: 5 famílias (masked edge/weight,
  neighborhood reconstruction, contrastive, autoencoders e link prediction) com
  hipótese de sinal, atalhos prováveis, custo, suporte a grafo dirigido/ponderado
  e capacidade indutiva, 1 connectome embedding e 3 alegações de graph foundation
  model com riscos; proibições de Transformer superior e de comparação entre
  espaços transdutivos registradas; 48 registros no ledger e 31 consultas no log;
  recursos: 17,1 MB de RAM e 0,08 s no validador, sem GPU; decisão/limitação:
  revisão documental sem treino e sem medição real de custo; revisão humana em
  G1; arquivos não relacionados preservados fora do commit; commit
  6a253668348f0ade2206bce2cae74d4174440ba8.

- [x] **L06 — Montar matriz de métodos, baselines e implementações auditáveis.**
  - Objetivo: transformar literatura em opções realmente executáveis.
  - Entregas: `research/literature/METHODS.md` com random, degree, handcrafted,
    Node2Vec, DeepWalk, espectral, MLP, GraphSAGE, GIN, GAT, relacional,
    Transformer pequeno e pelo menos um método publicado de matching.
  - Aceite: registra parâmetros, complexidade, dependências, licença, manutenção,
    suporte sparse/sampling e estimativa conservadora para 8 GB; marca
    incompatibilidades sem fabricar adaptação.
  - Proibições: não instalar nem executar pacotes nesta fase.
  - Dependências: L03–L05.
  - Orçamento: IA baixa; sem GPU.
  Evidência (2026-09-14, executor): arquivos `research/literature/METHODS.md`,
  `research/literature/LEDGER.tsv` (LIT-0049 a LIT-0057),
  `research/literature/QUERY-LOG.tsv` (consultas Q4) e
  `tools/validate_research.py` (funções de L06) e esta linha; fontes/versões:
  buscas de 2026-09-14 verificadas em fontes primárias — node2vec
  (10.1145/2939672.2939754), DeepWalk (10.1145/2623330.2623732), GIN
  (10.48550/arXiv.1810.00826), GAT (10.48550/arXiv.1710.10903), R-GCN
  (10.1007/978-3-319-93417-4_38), Graphormer (10.48550/arXiv.2106.05234), PyG
  (MIT, release 2.8.0), DGL (Apache-2.0) e NetworkX (BSD-3-Clause), além de
  LIT-0026, LIT-0027, LIT-0028, LIT-0033 e LIT-0043 já no ledger; Python 3.12.2
  (stdlib); comandos e testes: `python3 tools/validate_research.py` com smoke
  negativo inline (método ausente, campo ausente, proibição removida, LIT
  inexistente, consulta Q4 ausente, tópico ausente e seção ausente),
  `python3 tools/validate_plan.py`, `git diff --cached --check` e
  `git status --porcelain`; resultado: 15 métodos (random, majority, degree-only,
  handcrafted, Node2Vec, DeepWalk, espectral, MLP, GraphSAGE, GIN, GAT,
  relacional, Transformer pequeno, NBLAST e NeuronBridge) com parâmetros,
  complexidade, dependências, licença, manutenção, suporte sparse/sampling,
  estimativa conservadora para 8 GB e incompatibilidades; nenhum pacote foi
  instalado ou executado; 57 registros no ledger e 41 consultas no log; recursos:
  17,4 MB de RAM e 0,08 s no validador, sem GPU; decisão/limitação: estimativas
  não medidas, licenças não verificadas ficam marcadas e a matriz não decide o
  par fonte/alvo (G2); revisão humana em G1; arquivos não relacionados
  preservados fora do commit; commit
  c8f8d7907ffbb76c40b6719a0ba71dea2bbdfea7.

- [x] **L07 — Produzir mapa de lacuna e veredito de novidade provisório.**
  - Objetivo: distinguir contribuição possível de repetição.
  - Entregas: `research/literature/NOVIDADE.md`, claim por claim, com trabalhos
    mais próximos, diferenças e evidência conflitante.
  - Aceite: propõe no máximo três contribuições testáveis e uma versão mínima;
    inclui a alternativa “não há novidade suficiente” e buscas adversariais para
    tentar refutar cada lacuna.
  - Proibições: ausência em uma busca não prova novidade.
  - Dependências: L02–L06.
  - Orçamento: IA baixa + revisão humana.
  Evidência (2026-09-14, executor): arquivos `research/literature/NOVIDADE.md`,
  `research/literature/LEDGER.tsv` (LIT-0058 a LIT-0067),
  `research/literature/QUERY-LOG.tsv` (consultas Q4/Q5 adversariais),
  `tools/validate_research.py` (funções de L07) e esta linha; fontes/versões:
  buscas adversariais de 2026-09-14 verificadas em fontes primárias — NTAC 2026
  (10.1038/s41467-025-68044-1), alinhamento BANC-MANC (bioRxiv
  10.64898/2026.06.14.732053v2), caso de falha de SSL (arXiv 2602.03217),
  MaskGAE (arXiv 2205.10053), Bandana (arXiv 2402.03814), FlyGM
  (arXiv 2602.17997), GraphDINO (arXiv 2112.12482), pré-treino de connectome
  funcional (10.1523/ENEURO.0370-25.2026) e CAME (Genome Research 33:96);
  Python 3.12.2 (stdlib); comandos e testes: `python3 tools/validate_research.py`
  com smoke negativo inline (lacuna ausente, campo ausente, regra removida, LIT
  inexistente, mais de três contribuições, consulta Q5 ausente e seção ausente),
  `python3 tools/validate_plan.py`, `git diff --cached --check` e
  `git status --porcelain`; resultado: 3 lacunas (zero-shot com encoder
  congelado, SSL topológico com controles de grau e protocolo selado), 3
  contribuições com versão mínima e riscos, alternativa “não há novidade
  suficiente” registrada e buscas adversariais arquivadas; 67 registros no
  ledger e 47 consultas no log; recursos: 17,6 MB de RAM e 0,08 s no validador,
  sem GPU; decisão/limitação: veredito provisório, ausência em busca não prova
  novidade e revisão humana obrigatória em G1; arquivos não relacionados
  preservados fora do commit; commit
  946dc2d853bdcec0de3eb261a1d88cf0bedd34e0.

- [x] **G1 — Aprovar viabilidade teórica e lacuna provisória.**
  - Objetivo: decidir se vale auditar dados e qual pergunta merece prioridade.
  - Entregas: `docs/gates/G1-LITERATURA.md` e snapshot do ledger.
  - Aceite: revisor confirma cobertura, trabalhos mais próximos, hipótese
    reformulada quando necessário e nível honesto de novidade.
  - Proibições: gate não aprova paper; apenas autoriza a auditoria de dados.
  - Dependências: L01–L07.
  - Orçamento: IA baixa para síntese; revisão humana científica.
  Bloqueio (2026-09-14, executor): pacote preparado em
  `docs/gates/G1-LITERATURA.md` com decisão `AGUARDAR` e 8 critérios, mais o
  snapshot `docs/gates/G1-LEDGER-SNAPSHOT.tsv` com SHA-256 conferido contra o
  ledger; os critérios científicos (nível honesto de novidade e eventual
  reformulação de H0/H1) estão `NÃO VERIFICADO` aguardando revisão humana; a IA
  não assinou nem aprovou; validação estrutural com smoke negativo em
  `tools/validate_research.py` (21,4 MB de RAM, 0,09 s, sem GPU); próxima ação
  humana: decidir GO/NO-GO/REFORMULAR e assinar; commit
  f83d3cf57c7823e96ef454197eead85e7b0bd964.
  Evidência (2026-09-14, executor + revisor humano): arquivos
  `docs/gates/G1-LITERATURA.md` (decisão GO com novidade incremental, 8
  critérios `PASS` e assinatura de Alexandre Zanata), snapshot
  `docs/gates/G1-LEDGER-SNAPSHOT.tsv` conferido por SHA-256,
  `tools/validate_research.py` (estado aprovado do gate) e esta linha;
  fontes/versões: parecer do revisor humano Alexandre Zanata de 2026-09-14 e
  documentos internos de L01–L07, nenhuma fonte externa nova, Python 3.12.2
  (stdlib); comandos e testes: `python3 tools/validate_research.py` com smoke
  negativo inline (decisão GO com G1 aberto, snapshot divergente, hash ausente,
  assinatura pendente, critério `NÃO VERIFICADO` com GO e seção ausente),
  `python3 tools/validate_plan.py`, `git diff --cached --check` e
  `git status --porcelain`; resultado: GO registrado com novidade
  incremental/provisória e sem reformulação de H0/H1; D01–D10 autorizadas
  conforme dependências, sem download, treino, unseal ou leitura de
  `data/sealed/`; recursos: 21,4 MB de RAM e 0,09 s no validador, sem GPU;
  decisão/limitação: novidade incremental aprovada pelo revisor, licenças
  seguem pendentes de auditoria em D01–D07; arquivos não relacionados
  preservados fora do commit; commit
  a639f08b94f658950a748df37c94070a23034d11.

### Auditoria de datasets

- [x] **D01 — Congelar esquema de dataset card e inventário de candidatos.**
  - Objetivo: comparar datasets pelos mesmos critérios.
  - Entregas: cópias versionadas do modelo para cada candidato e
    `research/datasets/INVENTARIO.md` com campos obrigatórios e status vazio.
  - Aceite: inclui release, indivíduo/sexo/estágio/tecido, cobertura, IDs, tipos,
    proveniência de labels, neurotransmissores, regiões, edges, skeletons,
    crosswalks, licença, API/dump, formato, tamanho e checksum.
  - Proibições: campos desconhecidos permanecem `não confirmado`.
  - Dependências: G1.
  - Orçamento: IA baixa; sem GPU.
  Evidência (2026-09-14, executor): arquivos `research/datasets/INVENTARIO.md`,
  `research/datasets/cards/FLYWIRE-FAFB.md`, `HEMIBRAIN.md`, `BANC.md`,
  `MANC.md`, `MAOL.md` e `MCNS.md` (cópias versionadas de
  `docs/templates/DATASET-CARD.md` com status `não confirmado`),
  `tools/validate_research.py` (funções de D01) e esta linha; fontes/versões:
  apenas documentos internos (modelo de dataset card e G1 aprovado), nenhuma
  fonte externa consultada, Python 3.12.2 (stdlib); comandos e testes:
  `python3 tools/validate_research.py` com smoke negativo inline (card ausente,
  status confirmado, seção ausente, valor fabricado, campo ausente e candidato
  ausente), `python3 tools/validate_plan.py`, `git diff --cached --check` e
  `git status --porcelain`; resultado: 16 campos congelados (CAMPO-01 a
  CAMPO-16), 6 candidatos com cards vazios e status `não confirmado`, nenhum
  dado de dataset declarado e nenhuma licença avaliada; recursos: 21,3 MB de RAM
  e 0,09 s no validador, sem GPU; decisão/limitação: esquema congelado e campos
  desconhecidos permanecem `não confirmado`; as auditorias D02–D07 preenchem um
  card por vez com fonte primária; arquivos não relacionados preservados fora do
  commit; commit 77a5196d85b9a44dff6f051e215c2169cf3c7881.

- [x] **D02 — Auditar FlyWire/FAFB release por release.**
  - Objetivo: registrar apenas capacidades verificadas desse candidato.
  - Entregas: dataset card, claims atômicos e lista de endpoints/dumps oficiais.
  - Aceite: duas fontes quando uma propriedade altera o desenho; versões não são
    misturadas; amostra ou schema oficial comprova nomes/tipos de campos.
  - Proibições: sem download integral e sem token/conta sem autorização.
  - Dependências: D01, L02.
  - Orçamento: IA baixa; web; disco máximo 100 MB para amostra autorizada.
  Evidência (2026-09-14, executor): arquivos
  `research/datasets/cards/FLYWIRE-FAFB.md` (auditado em D02),
  `research/datasets/INVENTARIO.md` (CAND-01 auditado),
  `research/literature/LEDGER.tsv` (LIT-0068 e LIT-0069),
  `research/literature/QUERY-LOG.tsv` (leituras oficiais registradas) e
  `tools/validate_research.py` (funções de D02) e esta linha; fontes/versões:
  Zenodo API record 10676866 (v783.0, 2024-06-02, CC BY 4.0, MD5 por arquivo),
  Dorkenwald 2024 (10.1038/s41586-024-07558-y), Schlegel 2024
  (10.1038/s41586-024-07686-5), GitHub API de `flywire_annotations` (v2.1.0,
  v3.0.0 e v3.1.0; `license: null`) e Codex `about_flywire`, acesso 2026-09-14;
  Python 3.12.2 (stdlib); comandos e testes: `python3 tools/validate_research.py`
  com smoke negativo inline (status inválido, card sem seções, poucas fontes,
  status não confirmado em card auditado, veredito inválido e card vazio
  rotulado auditado), `python3 tools/validate_plan.py`,
  `git diff --cached --check` e `git status --porcelain`; resultado: card do
  FlyWire/FAFB preenchido com 9 fontes atômicas (8 `confirmado` e 1 `não
  encontrado`), esquema de 16 campos referenciado e pendências explícitas
  (licença das anotações, esqueleto e conta no Codex); nenhum download integral;
  o único arquivo dentro do teto (1,1 MB) não foi baixado; recursos: 21,8 MB de
  RAM e 0,09 s no validador, sem GPU e sem download; decisão/limitação:
  FlyWire/FAFB permanece `candidato`, licença das anotações `não encontrado`,
  esqueleto `não confirmado` e conta no Codex `ambíguo`; arquivos não
  relacionados preservados fora do commit; commit
  59ec9ef58769512996d5712ec22e4e4a7169501c.

- [x] **D03 — Auditar hemibrain release por release.**
  - Objetivo: avaliar o comparador cerebral sem presumir cobertura equivalente.
  - Entregas: dataset card, claims e interfaces de acesso oficiais.
  - Aceite: mesmos critérios de D02, incluindo espécime, cobertura parcial,
    ontologia e proveniência das anotações.
  - Proibições: não tratar sobreposição anatômica como identidade de população.
  - Dependências: D01, L02.
  - Orçamento: IA baixa; web; amostra até 100 MB.
  Evidência (2026-09-14, executor): arquivos `research/datasets/cards/HEMIBRAIN.md`
  (auditado em D03), `research/datasets/INVENTARIO.md` (CAND-02 auditado),
  `research/literature/LEDGER.tsv` (LIT-0070 e LIT-0071),
  `research/literature/QUERY-LOG.tsv` (leituras oficiais registradas) e
  `tools/validate_research.py` e esta linha; fontes/versões: Scheffer et al.
  2020 (10.7554/eLife.57443), página oficial Janelia do hemibrain, GitHub API
  `connectome-neuprint/neuPrint` (BSD-3-Clause, último push 2023-02-24) e
  Schlegel et al. 2024 (10.1038/s41586-024-07686-5), acesso 2026-09-14;
  Python 3.12.2 (stdlib); comandos e testes: `python3 tools/validate_research.py`
  com a validação de cards auditados já coberta pelo smoke de D02,
  `python3 tools/validate_plan.py`, `git diff --cached --check` e
  `git status --porcelain`; resultado: card do hemibrain com 8 fontes atômicas
  (6 `confirmado`, 1 `não encontrado` e 1 `conflitante` por critério de
  contagem), fêmea única de 5 dias, cobertura parcial, licença CC BY 4.0,
  releases v1.0–v1.2, exports CSV e interfaces neuPrint/DVID/Neuroglancer;
  nenhum download; recursos: 21,8 MB de RAM e 0,09 s no validador, sem GPU e sem
  download; decisão/limitação: hemibrain permanece `candidato`, contagens de
  tipos conflitantes entre fontes e sobreposição anatômica com o FlyWire não
  tratada como identidade de população; arquivos não relacionados preservados
  fora do commit; commit 04afe8e57d57cee235518b6338b7e693a326e2ea.

- [x] **D04 — Auditar BANC release por release.**
  - Objetivo: verificar acesso, escopo anatômico e rótulos realmente liberados.
  - Entregas: dataset card, claims, formatos e requisitos de acesso.
  - Aceite: distingue anúncio, paper, portal navegável e dump processável; registra
    o que não pode ser obtido localmente.
  - Proibições: portal visual não conta automaticamente como dataset baixável.
  - Dependências: D01, L02.
  - Orçamento: IA baixa; web; amostra até 100 MB se permitida.
  Evidência (2026-09-14, executor): arquivos `research/datasets/cards/BANC.md`
  (auditado em D04), `research/datasets/INVENTARIO.md` (CAND-03 auditado),
  `research/literature/LEDGER.tsv` (LIT-0072 e LIT-0073),
  `research/literature/QUERY-LOG.tsv` (leituras oficiais registradas) e esta
  linha; fontes/versões: Bates et al. 2026 (10.1038/s41586-026-10735-w), API do
  Harvard Dataverse para `10.7910/DVN/7WTH1N` (v3.0, CC BY 4.0, 379 arquivos,
  536.062.963.020 bytes, MD5, 277 restritos), API do GitHub de
  `htem/BANC-project` (sem licença, último push 2026-07-20), wiki oficial do
  BANC e endpoint CAVE (login Google), acesso 2026-09-14; Python 3.12.2
  (stdlib) e um agente de exploração para ler o JSON grande; comandos e testes:
  `python3 tools/validate_research.py` (validação de card auditado coberta pelo
  smoke de D02), `python3 tools/validate_plan.py`, `git diff --cached --check` e
  `git status --porcelain`; resultado: card do BANC com 8 fontes atômicas (6
  `confirmado`, 1 `não encontrado` e 1 `conflitante`), escopo cérebro + VNC de
  fêmea única, canais de acesso (Dataverse, GCS, Codex, CAVE e BossDB),
  277/379 arquivos restritos e nenhum download; recursos: 21,8 MB de RAM e
  0,09 s no validador, sem GPU e com teto de 100 MB não utilizado; decisão/
  limitação: BANC permanece `candidato`, acesso parcial depende de pedido e o
  repositório de código não declara licença; arquivos não relacionados
  preservados fora do commit; commit
  45f784d84118221f17a35a65a4133f1354047918.

- [x] **D05 — Auditar MANC release por release.**
  - Objetivo: verificar comparabilidade do cordão nervoso e suas anotações.
  - Entregas: dataset card e claims oficiais.
  - Aceite: registra sexo, tecido, cobertura, direção/peso de arestas, tipos e
    possíveis correspondências, além de licença e formatos.
  - Proibições: cérebro e VNC não são colocados no mesmo benchmark sem hipótese
    anatômica explícita.
  - Dependências: D01, L02.
  - Orçamento: IA baixa; web; amostra até 100 MB.
  Evidência (2026-09-14, executor): arquivos `research/datasets/cards/MANC.md`
  (auditado em D05), `research/datasets/INVENTARIO.md` (CAND-04 auditado),
  `research/literature/LEDGER.tsv` (LIT-0074 e LIT-0075),
  `research/literature/QUERY-LOG.tsv` (leituras oficiais registradas) e esta
  linha; fontes/versões: página oficial Janelia do MANC (v1.2.1), Takemura et
  al. 2024 (10.7554/eLife.97769), Marin et al. 2024 (10.7554/eLife.97766),
  Cheong et al. 2024 (10.7554/eLife.96084) e API do GitHub de
  `natverse/malevnc` (GPL-3.0), acesso 2026-09-14; Python 3.12.2 (stdlib);
  comandos e testes: `python3 tools/validate_research.py` (card auditado
  coberto pelo smoke de D02), `python3 tools/validate_plan.py`,
  `git diff --cached --check` e `git status --porcelain`; resultado: card do
  MANC com 7 fontes atômicas (6 `confirmado` e 1 `não encontrado`), ~23.000
  neurônios, VNC completo de macho, CC BY 4.0, releases v1.0/v1.2, acessos
  neuPrint/malevnc/bucket flat e crosswalks EM-LM via NeuronBridge; nenhum
  download; recursos: 21,8 MB de RAM e 0,09 s no validador, sem GPU e com teto
  de 100 MB não utilizado; decisão/limitação: MANC permanece `candidato`, cobre
  apenas o VNC e seu uso em benchmark com cérebro exige hipótese anatômica
  explícita; arquivos não relacionados preservados fora do commit; commit
  72d7dd081c3b2be4151a4431888e3a74345460b3.

- [x] **D06 — Auditar MAOL release por release.**
  - Objetivo: verificar se o candidato de lobo óptico sustenta comparação local.
  - Entregas: dataset card e claims oficiais.
  - Aceite: confirma expansão do acrônimo, espécime, região, cobertura,
    conectividade, morfologia, labels, formatos e termos; ambiguidade é registrada.
  - Proibições: não inferir campos pelo nome do projeto.
  - Dependências: D01, L02.
  - Orçamento: IA baixa; web; amostra até 100 MB.
  Evidência (2026-09-14, executor): arquivos `research/datasets/cards/MAOL.md`
  (auditado em D06), `research/datasets/INVENTARIO.md` (CAND-05 auditado),
  `research/literature/LEDGER.tsv` (LIT-0076 e LIT-0077),
  `research/literature/QUERY-LOG.tsv` (leituras oficiais registradas) e esta
  linha; fontes/versões: página oficial Janelia do Optic Lobe (v1.1), Nern et
  al. 2025 (10.1038/s41586-025-08746-0) e API do GitHub do repositório
  `reiserlab/male-drosophila-visual-system-connectome` (CC-BY-4.0), acesso
  2026-09-14; Python 3.12.2 (stdlib); comandos e testes:
  `python3 tools/validate_research.py` (card auditado coberto pelo smoke de
  D02), `python3 tools/validate_plan.py`, `git diff --cached --check` e
  `git status --porcelain`; resultado: MAOL confirmado como conectoma do lobo
  óptico **direito** de macho adulto, >50.000 neurônios e >700 tipos, CC BY 4.0,
  neuPrint `optic-lobe:v1.1` (52.445 neurônios e 6.484.936 conexões), lamina
  ausente/subcontada e 7 fontes atômicas (6 `confirmado` e 1 `não encontrado`);
  nenhum download; recursos: 21,8 MB de RAM e 0,09 s no validador, sem GPU e com
  teto de 100 MB não utilizado; decisão/limitação: MAOL permanece `candidato`,
  sem confundir com o lobo óptico feminino do FAFB e com formatos/checksums por
  arquivo ainda não confirmados; arquivos não relacionados preservados fora do
  commit; commit 5418a3e3e5ee45f3979ea3d32f23b5ac39fdc94c.

- [x] **D07 — Auditar MCNS release por release.**
  - Objetivo: verificar se o candidato de sistema nervoso central sustenta os
    experimentos propostos.
  - Entregas: dataset card e claims oficiais.
  - Aceite: confirma expansão do acrônimo, relação com outros releases,
    indivíduo, cobertura, labels, arestas, skeletons, formatos e acesso.
  - Proibições: não fundir releases ou indivíduos por semelhança de nome.
  - Dependências: D01, L02.
  - Orçamento: IA baixa; web; amostra até 100 MB.
  Evidência (2026-09-14, executor): arquivos `research/datasets/cards/MCNS.md`
  (auditado em D07), `research/datasets/INVENTARIO.md` (CAND-06 auditado),
  `research/literature/LEDGER.tsv` (LIT-0078 e LIT-0079),
  `research/literature/QUERY-LOG.tsv` (leituras oficiais registradas) e esta
  linha; fontes/versões: páginas oficiais do Male CNS (Janelia e
  janelia-flyem.github.io/male-cns/download) e Berg et al. 2026
  (10.1016/j.cell.2026.08.015), acesso 2026-09-14; Python 3.12.2 (stdlib);
  comandos e testes: `python3 tools/validate_research.py` (card auditado coberto
  pelo smoke de D02), `python3 tools/validate_plan.py`,
  `git diff --cached --check` e `git status --porcelain`; resultado: MCNS
  confirmado como SNC completo de macho único (cérebro, lobos ópticos e VNC,
  conectivo cervical intacto), releases v0.9/v1.0 (v1.0 em 2026-06-08), CC-BY
  4.0, bulk Feather com tamanhos por arquivo (anotações 13 MB; conectividade
  1,1 GB; sin-partners 6,8 GB com schema confirmado), esqueletos SWC/precomputed
  e neo4j; contagens 166.700/11.710 (publicado) vs 166.691/11.691 (PMC/preprint)
  registradas como conflitantes; 7 fontes atômicas (5 `confirmado`, 1
  `conflitante` e 1 `não encontrado`); nenhum download; recursos: 21,8 MB de RAM
  e 0,09 s no validador, sem GPU e com teto de 100 MB não utilizado; decisão/
  limitação: MCNS permanece `candidato`, sem fundir releases ou indivíduos por
  semelhança de nome (MANC é outro espécime) e com checksums por arquivo ainda
  não encontrados; arquivos não relacionados preservados fora do commit; commit
  57148f8dcb9b7894200129fc1924caa1a339cf7f.

- [ ] **D08 — Auditar ontologias, crosswalks e independência dos rótulos.**
  - Objetivo: saber se “mesmo tipo” pode ser pontuado sem circularidade indevida.
  - Entregas: `research/datasets/CROSSWALK-AUDIT.md` público apenas com método,
    proveniência e agregados; proposta de interseção/known/open-set para cada par;
    mapping exato, quando necessário, guardado somente na zona selada.
  - Aceite: toda regra de mapeamento aponta para fonte; mapeamentos manuais têm
    dois revisores; rótulos derivados da conectividade ou do próprio matching
    ficam sinalizados para análise de sensibilidade ou exclusão.
  - Proibições: o executor de treino não recebe mapping exato nem associação por
    neurônio do alvo.
  - Dependências: C03, D02–D07.
  - Orçamento: IA baixa + dupla revisão humana; sem GPU.

- [ ] **D09 — Estimar escala e fazer spikes mínimos de acesso.**
  - Objetivo: substituir estimativas vagas por medições sem baixar tudo.
  - Entregas: `research/datasets/RECURSOS.md` com nodes, edges, bytes por tabela,
    projeções de RAM/disco, tempo de download/preprocessamento e método de cálculo.
  - Aceite: amostras autorizadas têm checksum; projeções separam valor publicado,
    medido e inferido; inclui sparse COO/CSR, Parquet/Arrow, mmap e margem para 32
    GB RAM/8 GB VRAM.
  - Proibições: não extrapolar amostra sem intervalo/margem e não baixar dump
    integral antes do gate.
  - Dependências: D02–D07.
  - Orçamento: IA baixa; CPU; até 1 GB total de disco temporário; sem GPU.

- [ ] **D10 — Ranquear pares, escolher papéis e definir fallback.**
  - Objetivo: selecionar fonte, alvo-piloto, alvo confirmatório e reservas com
    justificativa multicritério.
  - Entregas: `research/datasets/SELECAO.md` com ranking por comparabilidade,
    independência, labels, licença, acesso, escala e risco de circularidade.
  - Aceite: escolhe um MVP A→B somente se defensável; reserva terceiro dataset
    quando possível; define fallback para incompatibilidade, acesso negado,
    ausência de crosswalk e falta de réplica biológica.
  - Proibições: conveniência de download não supera validade; não chamar recorte
    do mesmo indivíduo de cross-individual.
  - Dependências: D08, D09.
  - Orçamento: IA baixa + revisão humana; sem GPU.

- [ ] **G2 — Aprovar dados e par do MVP.**
  - Objetivo: decidir `GO`, `NO-GO` ou `REFORMULAR` antes do download completo.
  - Entregas: `docs/gates/G2-DADOS.md`, cards congelados e papéis dos datasets.
  - Aceite: licença/acesso, comparabilidade, target, cobertura, recursos,
    crosswalk e circularidade têm parecer; alvo confirmatório fica reservado.
  - Proibições: se nenhum par passar, não substituir silenciosamente por split do
    mesmo connectoma; produzir relatório de inviabilidade/reformulação.
  - Dependências: D01–D10.
  - Orçamento: pacote por IA baixa; revisão humana científica e de termos.

## Nível 1 — infraestrutura, dados e MVP confirmatório

### Reprodutibilidade, avaliação selada e pré-registro

- [ ] **R01 — Criar estrutura mínima e plano de gestão de dados.**
  - Objetivo: separar código, manifestos, dados, runs, documentos e material
    selado antes de qualquer download integral.
  - Entregas: diretórios documentados, `data/README.md`,
    `docs/research/DATA-MANAGEMENT.md` e revisão do `.gitignore`.
  - Aceite: política define fonte de verdade, retenção, backup, licença,
    redistribuição, dados regeneráveis, dados selados e procedimento de limpeza;
    teste prova que arquivos sentinela sensíveis são ignorados pelo Git.
  - Proibições: não adicionar dados, tokens, rótulos-alvo ou checkpoints ao Git.
  - Dependências: G2.
  - Orçamento: IA baixa; sem GPU.

- [ ] **R02 — Fixar ambiente e capturar hardware.**
  - Objetivo: obter instalação repetível e compatível com a máquina-alvo.
  - Entregas: versão Python, lockfile, instruções Linux/CUDA, script de diagnóstico
    e relatório de compatibilidade da RTX 4060.
  - Aceite: ambiente limpo instala; importações e operação CUDA mínima passam;
    versões, driver, CPU, RAM, GPU/VRAM e disco ficam registrados; dependências
    têm justificativa e licença.
  - Proibições: não adicionar framework pesado sem uso aprovado e não atualizar
    dependência fora do lock silenciosamente.
  - Dependências: R01, L06.
  - Orçamento: IA baixa; GPU smoke de segundos; rede apenas para pacotes aprovados.

- [ ] **R03 — Implementar proveniência, manifests e download idempotente.**
  - Objetivo: tornar toda entrada identificável e reobtível.
  - Entregas: schema de manifest, validador, comandos de download por release e
    testes com fixture/local HTTP; manifests versionados sem credenciais.
  - Aceite: resume download interrompido quando seguro, valida tamanho/checksum,
    nunca sobrescreve arquivo divergente e registra URL, release, licença e data.
  - Proibições: não automatizar bypass de termos nem registrar URL assinada/token.
  - Dependências: R01, R02, cards aprovados no G2.
  - Orçamento: IA baixa; CPU; fixture pequena.

- [ ] **R04 — Fixar contrato de configuração, run e determinismo.**
  - Objetivo: eliminar parâmetros escondidos e resultados sem linhagem.
  - Entregas: schema de configuração, implementação do `RUN-MANIFEST`, seeds
    centralizadas, captura de Git/ambiente/recursos e teste de repetição.
  - Aceite: duas execuções determinísticas da fixture geram mesmas saídas ou a
    tolerância numérica documentada; toda opção efetiva é serializada; run ID é
    imutável e outputs divergentes não colidem no cache.
  - Proibições: sem default dependente da máquina ou timestamp usado como seed.
  - Dependências: R02, R03.
  - Orçamento: IA baixa; CPU; sem treino real.

- [ ] **R05 — Implementar o firewall do alvo e teste antileakage.**
  - Objetivo: impedir acesso acidental do executor aos labels e crosswalk
    avaliativo do alvo.
  - Entregas: layout de zonas, permissões/processo de custódia, scanner de
    dependências, fixture selada e teste que falha se treino importar, abrir ou
    logar caminho/coluna proibidos.
  - Aceite: pipeline público roda sem montar `data/sealed`; pacote congelado só
    contém hashes dos labels; tentativas sentinela são detectadas; procedimento
    de unseal e invalidação está documentado.
  - Proibições: não copiar labels para notebooks, caches, nomes de classe ou
    mensagens de debug.
  - Dependências: R01, R04, C05.
  - Orçamento: IA baixa + revisão de segurança metodológica; sem GPU.

- [ ] **R06 — Especificar o plano estatístico e avaliador selado.**
  - Objetivo: definir cálculo, incerteza e outputs antes de observar o alvo.
  - Entregas: `docs/research/STATISTICAL-ANALYSIS-PLAN.md`, schema de predições e
    contrato do comando avaliador.
  - Aceite: fixa métrica primária, SESOI, denominadores, macro/micro, CIs,
    bootstrap agrupado, permutações, múltiplas comparações, seeds, missing labels,
    classes pequenas, open-set, calibração e formato de resultado sem IDs/labels.
  - Proibições: não tratar nós como observações biológicas independentes.
  - Dependências: C04, D08, D10, R05.
  - Orçamento: IA baixa + revisão humana de estatística; sem GPU.

- [ ] **R07 — Redigir e assinar o pré-registro.**
  - Objetivo: congelar protocolo confirmatório e seus ramos condicionais.
  - Entregas: `preregistration/PROTOCOL.md`, cards dos experimentos previstos e
    registro assinado com hash.
  - Aceite: fixa fonte/alvo, versão, população, features, modelo, baselines,
    hiperparâmetros pesquisáveis, budget de trials, seeds, stopping, métricas,
    SESOI, exclusões, análises e decisões condicionais do Nível 2; separa
    explicitamente exploratório de confirmatório.
  - Proibições: não ler resultados-alvo; alteração posterior segue changelog.
  - Dependências: R03–R06, G2.
  - Orçamento: IA baixa para minuta; assinatura humana obrigatória.

- [ ] **R08 — Ensaiar o protocolo completo em dados sintéticos e congelar versão.**
  - Objetivo: descobrir falhas operacionais antes de gastar o alvo ou a GPU.
  - Entregas: fixture com classes conhecidas/unknown, execução ponta a ponta,
    relatório de dry run, tag/hash interno do protocolo e pacote de handoff ao
    custodiante.
  - Aceite: download local, preprocessamento, treino trivial, freeze, inferência,
    avaliação selada e relatório passam sem acesso indevido; teste proposital de
    leakage falha; todos os schemas validam.
  - Proibições: dados reais do alvo não entram no dry run.
  - Dependências: R03–R07.
  - Orçamento: IA baixa; CPU/GPU smoke até 5 minutos.

- [ ] **G3 — Aprovar pré-registro e firewall.**
  - Objetivo: autorizar ingestão integral sem mudar a pergunta durante o caminho.
  - Entregas: `docs/gates/G3-PREREGISTRO.md` com hashes do protocolo, schemas e
    teste antileakage.
  - Aceite: revisor científico, estatístico e custodiante aprovam; alvo(s)
    confirmatório(s) e política pós-unseal ficam explícitos.
  - Proibições: nenhuma análise real inicia com critério `não verificado`.
  - Dependências: R01–R08.
  - Orçamento: pacote por IA baixa; revisão humana obrigatória.

### Ingestão e harmonização

- [ ] **H01 — Especificar schema canônico de grafo e fixtures.**
  - Objetivo: representar todos os datasets sem apagar diferenças relevantes.
  - Entregas: contrato versionado para nodes, edges, direção, peso, atributos,
    provenance e missingness; fixture sintética dirigida/ponderada.
  - Aceite: tipos, unidades, constraints, multiedges, self-loops, zero/NaN,
    threshold e agregação estão definidos; round-trip da fixture preserva dados.
  - Proibições: não criar campo “comum” que um dataset não possui.
  - Dependências: G3, D02–D09.
  - Orçamento: IA baixa; CPU.

- [ ] **H02 — Implementar e validar o adapter da fonte.**
  - Objetivo: converter a release-fonte imutável ao schema canônico.
  - Entregas: adapter, testes de schema, amostra dourada, contagens e relatório de
    campos descartados/transformados.
  - Aceite: checksums de entrada/saída, IDs únicos, endpoints válidos, pesos não
    negativos, direção conhecida e totais reconciliados com a fonte oficial ou
    diferença explicada.
  - Proibições: não incluir tipo/posição/região no tensor do trilho A.
  - Dependências: H01, R03.
  - Orçamento: IA baixa; primeiro amostra, depois CPU/RAM conforme D09.

- [ ] **H03 — Implementar e validar o adapter público do alvo.**
  - Objetivo: converter apenas o grafo/features permitidos do alvo sem tocar
    labels selados.
  - Entregas: adapter separado, testes de schema, amostra dourada sem labels,
    contagens e relatório de transformações.
  - Aceite: roda com `data/sealed` ausente; schema público não contém nome/tipo,
    crosswalk ou correspondência; mesmas invariantes de H02 passam.
  - Proibições: não abrir adapter/arquivo avaliativo “só para conferir”.
  - Dependências: H01, R05.
  - Orçamento: IA baixa; primeiro amostra, depois CPU/RAM conforme D09.

- [ ] **H04 — Implementar o adapter selado de avaliação.**
  - Objetivo: permitir pontuação sem expor rótulos por neurônio ao executor.
  - Entregas: módulo/ambiente do custodiante, validação de label schema,
    agregação segura e teste em fixture.
  - Aceite: recebe predições por IDs opacos, valida cobertura/crosswalk e devolve
    apenas métricas/contagens autorizadas; hash do label set é registrado; logs
    não revelam exemplos individuais.
  - Proibições: executor de treino não executa esta fase nem recebe seus fixtures
    reais.
  - Dependências: H01, R05, R06; execução pelo custodiante.
  - Orçamento: IA baixa em sessão separada; revisão humana.

- [ ] **H05 — Remapear IDs e produzir features topology-only.**
  - Objetivo: gerar features comparáveis sem deixar identidade ou ordem virar
    atalho.
  - Entregas: mapeamento opaco, features permitidas, fit/transform separado,
    testes de permutação de IDs e relatório de distribuição.
  - Aceite: permutar IDs e ordem mantém resultados equivalentes; normalizadores
    são ajustados somente na fonte; features não carregam label, região,
    coordenada ou nome; missing/inf são tratados de modo fixo.
  - Proibições: node ID não entra como número, categoria ou índice treinável.
  - Dependências: H02, H03.
  - Orçamento: IA baixa; CPU.

- [ ] **H06 — Fixar semântica de arestas, thresholds e variantes.**
  - Objetivo: separar decisões necessárias de ablações futuras.
  - Entregas: transformador de edges, configuração primária e variantes
    pré-registradas para direção, peso, log de peso, threshold e reciprocidade.
  - Aceite: conservação/agregação de sinapses é testada; escolhas são aplicadas
    igualmente sem estatística do alvo; zero-edge, self-loop e componentes
    isolados têm regra explícita.
  - Proibições: não escolher threshold observando métrica no alvo.
  - Dependências: H02, H03, H05, R07.
  - Orçamento: IA baixa; CPU.

- [ ] **H07 — Materializar crosswalk e conjuntos avaliativos sob custódia.**
  - Objetivo: transformar a decisão ontológica em arquivos imutáveis de scoring.
  - Entregas: crosswalk versionado, conjuntos `known`, `unknown`, ambíguo e
    excluído, hashes e relatório de cobertura por dataset.
  - Aceite: duas revisões nos mapeamentos manuais; regra de muitos-para-um
    explícita; labels circulares sinalizados; executor recebe apenas contagens
    agregadas necessárias ao pré-registro.
  - Proibições: lista por node ID não sai da zona selada.
  - Dependências: D08, H04, R07; execução pelo custodiante.
  - Orçamento: IA baixa + dupla revisão humana; sem GPU.

- [ ] **H08 — Processar releases completas e medir recursos.**
  - Objetivo: gerar snapshots canônicos reproduzíveis no hardware-alvo.
  - Entregas: manifests, hashes, logs estruturados, dados fonte e alvo-público
    processados, perfil de tempo/RAM/disco e procedimento de retomada.
  - Aceite: execução desde raw é idempotente; picos ficam abaixo de 28 GB RAM e
    limite de disco aprovado; contagens batem H02/H03; nenhum label selado aparece
    no snapshot público.
  - Proibições: não corrigir dado bruto in-place nem aceitar OOM parcial.
  - Dependências: H02, H03, H05, H06, G3.
  - Orçamento: IA baixa; CPU; teto de recursos do G3.

- [ ] **H09 — Executar auditoria de qualidade e congelar dataset analítico.**
  - Objetivo: decidir se os dados preparados ainda suportam o protocolo.
  - Entregas: `artifacts/reports/DATA-QUALITY.md`, manifests finais, estatísticas
    permitidas e lista de desvios.
  - Aceite: duplicatas, componentes, graus, pesos, missingness, isolados,
    assimetrias, cobertura e drift de schema têm checks; desvios do card são
    reconciliados; hash analítico é congelado.
  - Proibições: não consultar distribuição de acerto ou labels do alvo.
  - Dependências: H07, H08.
  - Orçamento: IA baixa; CPU; sem GPU.

- [ ] **G4 — Aprovar o gate de dados analíticos.**
  - Objetivo: liberar baselines somente se qualidade e isolamento passarem.
  - Entregas: `docs/gates/G4-DADOS-ANALITICOS.md` com checksums e desvios aceitos.
  - Aceite: custodiante confirma separação; responsável científico confirma
    cobertura/validade; qualquer alteração material atualiza pré-registro antes
    de resultados.
  - Proibições: dataset reprovado não é “limpo” manualmente sem nova proveniência.
  - Dependências: H01–H09.
  - Orçamento: IA baixa para pacote; revisão humana.

### Avaliação e baselines obrigatórios

- [ ] **B01 — Implementar retrieval/classification e testes matemáticos.**
  - Objetivo: ter uma única implementação de métricas para todos os métodos.
  - Entregas: evaluator público de predições sintéticas para Recall@1/5/10, MRR,
    MAP, top-k, macro-F1 e balanced accuracy.
  - Aceite: exemplos pequenos calculados à mão, empates, classes ausentes,
    multi-instance, query sem match e macro/micro passam em testes; orientação de
    distância é inequívoca.
  - Proibições: implementação não lê labels reais do alvo.
  - Dependências: G4, R06.
  - Orçamento: IA baixa; CPU.

- [ ] **B02 — Implementar calibração, open-set e incerteza.**
  - Objetivo: evitar que toda consulta seja forçada a uma classe conhecida.
  - Entregas: Brier, ECE com bins fixos, reliability data, AUROC/AUPR open-set,
    FPR@TPR pré-fixada, bootstrap/permutação agrupados e testes.
  - Aceite: fixtures perfeitas, não calibradas, desbalanceadas e degeneradas têm
    valores esperados; limiar é aprendido somente na fonte/desenvolvimento
    autorizado; seed do bootstrap é registrada.
  - Proibições: não ajustar bins/threshold no alvo confirmatório.
  - Dependências: B01, R06.
  - Orçamento: IA baixa; CPU.

- [ ] **B03 — Executar random, majority e degree-only.**
  - Objetivo: estabelecer pisos e o principal controle de atalho.
  - Entregas: configs, modelos, predições congeláveis e métricas internas da fonte
    para aleatório estratificado, maioria e features de grau.
  - Aceite: chance analítica e simulada concordam; degree-only usa exatamente as
    transformações source-fit; classes e seeds seguem o pré-registro.
  - Proibições: não avaliar rótulos reais do alvo ainda.
  - Dependências: B01, B02, H09.
  - Orçamento: IA baixa; CPU.

- [ ] **B04 — Implementar estatísticas artesanais.**
  - Objetivo: comparar a GNN com assinaturas estruturais interpretáveis.
  - Entregas: feature extractor versionado para graus ponderados, reciprocidade,
    clustering/motifs e resumos de vizinhança permitidos; classifier/probe comum.
  - Aceite: invariância a IDs, testes em grafos conhecidos, custo/memória medidos
    e ablação que identifica cada família; nenhuma feature proibida entra.
  - Proibições: feature escolhida após olhar alvo vira exploratória.
  - Dependências: B03, H05, H06.
  - Orçamento: IA baixa; CPU; interromper feature inviável e registrar.

- [ ] **B05 — Implementar o MLP de controle.**
  - Objetivo: separar ganho do encoder de ganho causado apenas por não linearidade.
  - Entregas: MLP sobre as mesmas features, budgets de aproximadamente 100k,
    500k e tamanho pareado ao encoder quando possível.
  - Aceite: contagem exata de parâmetros, mesma seleção source-only, mesmas seeds
    e evaluator; smoke e overfit em fixture passam.
  - Proibições: MLP não recebe embedding pré-calculado com alvo.
  - Dependências: B03, B04, R04.
  - Orçamento: IA baixa; GPU smoke/piloto.

- [ ] **B06 — Implementar Node2Vec/DeepWalk com caveat transdutivo.**
  - Objetivo: medir baselines clássicos sem fingir alinhamento entre espaços.
  - Entregas: execução dentro da fonte, teste de estabilidade a rotação/permutação
    e proposta de uso cross-graph somente se houver mecanismo não supervisionado
    permitido e pré-registrado.
  - Aceite: relatório marca `não comparável zero-shot` quando necessário;
    qualquer alinhamento usa zero label/correspondência do alvo e tem baseline de
    sensibilidade.
  - Proibições: Procrustes com pares gold ou comparação direta de coordenadas
    arbitrárias não entra como zero-shot.
  - Dependências: L03, L06, B01, H09.
  - Orçamento: IA baixa; CPU/GPU piloto apenas se aplicável.

- [ ] **B07 — Implementar fatoração/espectral com o mesmo rigor.**
  - Objetivo: comparar contra estrutura global linear de baixo custo.
  - Entregas: método sparse, tratamento de direção/peso, orientação/alinhamento
    documentado, teste em fixture e perfil de recursos.
  - Aceite: ambiguity de sinal/rotação é controlada ou o método fica restrito ao
    diagnóstico within-source; sem densificar matriz completa.
  - Proibições: não executar decomposição densa que exceda RAM estimada.
  - Dependências: B01, H09, D09.
  - Orçamento: IA baixa; CPU; teto de 24 GB RAM.

- [ ] **B08 — Reproduzir um baseline publicado de neuron matching.**
  - Objetivo: comparar com o trabalho mais próximo compatível encontrado em L03.
  - Entregas: versão/licença fixadas, adaptação mínima documentada, teste de
    paridade com resultado público ou justificativa de não reprodutibilidade.
  - Aceite: inputs supervisionados são declarados; variantes com informação
    extra ficam em trilho separado; resultado ausente/falho é reportado, não
    substituído por método inventado.
  - Proibições: não alterar protocolo do método até “funcionar” no alvo.
  - Dependências: L03, L06, B01, H09.
  - Orçamento: IA baixa; CPU/GPU piloto conforme método; gate se exceder 8 GB.

- [ ] **B09 — Executar controles nulos e congelar pacote de baselines.**
  - Objetivo: provar que o harness detecta atalhos e que todos os comparadores
    obedecem ao mesmo protocolo.
  - Entregas: label permutation na fonte, rewiring preservando grau, IDs
    permutados, negativos degree-matched, relatório within-source e pacote
    congelado das configurações/predições necessárias.
  - Aceite: nulos degradam como esperado ou a falha é investigada; nenhuma
    métrica de label-alvo foi aberta; melhor baseline é escolhido pela regra
    source-only pré-registrada.
  - Proibições: não descartar baseline forte para favorecer GNN.
  - Dependências: B01–B08.
  - Orçamento: IA baixa; CPU/GPU piloto limitado pelo R07.

- [ ] **G5 — Aprovar o benchmark e liberar o MVP neural.**
  - Objetivo: confirmar que avaliação, nulos e baselines são confiáveis.
  - Entregas: `docs/gates/G5-BASELINES.md` com cobertura, falhas e hashes.
  - Aceite: testes métricos e de leakage passam; comparadores obrigatórios foram
    executados ou formalmente julgados inaplicáveis; budget do MVP permanece
    dentro do hardware.
  - Proibições: não liberar treino neural para mascarar evaluator inconsistente.
  - Dependências: B01–B09.
  - Orçamento: IA baixa para pacote; revisão humana de método.

### MVP auto-supervisionado

- [ ] **M01 — Fixar masked-edge/weight task e auditar atalhos.**
  - Objetivo: definir o objetivo SSL primário sem memorizar identidade do nó.
  - Entregas: máscara determinística por seed, negativos degree/distance-matched,
    decoder por pares de embeddings e testes de separação train/validation.
  - Aceite: nenhuma tabela por node ID; edge holdout não reaparece via reverse ou
    cache; distribuição de negativos é registrada; baseline de grau mede o
    atalho; pesos têm loss/transformação especificada.
  - Proibições: não mascarar no alvo durante treino confirmatório.
  - Dependências: G5, H06, R07.
  - Orçamento: IA baixa; CPU/GPU smoke.

- [ ] **M02 — Implementar GraphSAGE indutivo de 1–3M parâmetros.**
  - Objetivo: criar o candidato primário compatível com neighbor sampling.
  - Entregas: encoder dirigido/ponderado conforme protocolo, contagem exata de
    parâmetros, inferência em grafo novo e testes em fixture.
  - Aceite: overfit controlado de tiny graph, shapes/gradientes, determinismo,
    serialização e inferência sem IDs/labels passam; configuração padrão cabe no
    intervalo e não densifica o grafo.
  - Proibições: sem camada específica para número fixo de nós da fonte.
  - Dependências: M01, R04, H05.
  - Orçamento: IA baixa; GPU smoke.

- [ ] **M03 — Implementar GIN como candidato comparável.**
  - Objetivo: testar agregação alternativa sob o mesmo orçamento e harness.
  - Entregas: encoder GIN, configuração pareada em parâmetros/dimensão, testes e
    relatório de diferenças inevitáveis.
  - Aceite: mesmos contratos de M02; parâmetro, sampling e objective são
    comparáveis; incompatibilidade com direção/peso é explicitada.
  - Proibições: não favorecer um modelo com budget ou features extras.
  - Dependências: M01, M02.
  - Orçamento: IA baixa; GPU smoke.

- [ ] **M04 — Fazer smoke e calibrar sampling/recursos.**
  - Objetivo: encontrar batch/fanout seguro antes do treino completo.
  - Entregas: grid pequeno pré-definido de fanouts, embedding 64/128, batch e
    precision; perfil de tempo, RAM/VRAM e throughput.
  - Aceite: escolhe configuração abaixo de 6,5 GB de pico, sem OOM, com margem;
    confirma neighbor sampling, CPU workers e reproducibilidade; estimativa por
    epoch é comparada à medição.
  - Proibições: smoke não seleciona por resultado-alvo.
  - Dependências: M02, M03, H08.
  - Orçamento: IA baixa; GPU piloto até 30 minutos total.

- [ ] **M05 — Selecionar modelo somente dentro da fonte.**
  - Objetivo: ajustar o espaço de hiperparâmetros congelado sem gastar o alvo.
  - Entregas: trials previstos no R07, splits source-only, curva de treino,
    critério de early stop e ranking reproduzível.
  - Aceite: número de trials não excede budget; seed de seleção distinta das
    seeds finais; seleção usa métrica SSL/validação na fonte pré-definida; todos
    os trials, inclusive falhos, permanecem no ledger.
  - Proibições: nenhum score, label, crosswalk ou estatística do alvo orienta a
    escolha.
  - Dependências: M04, B09, R07.
  - Orçamento: IA baixa; GPU confirmatória conforme teto do G3/R07.

- [ ] **M06 — Treinar seeds finais e congelar encoder/probe.**
  - Objetivo: produzir todos os artefatos finais antes do primeiro unseal.
  - Entregas: encoder, transformações, probe treinado somente com labels-fonte,
    configs e manifests para todas as seeds pré-registradas.
  - Aceite: hashes, contagem de parâmetros, curvas, seleção, RAM/VRAM/tempo e
    source metrics completos; scanner antileakage passa; pacote é somente leitura.
  - Proibições: não escolher depois apenas seeds favoráveis e não sobrescrever
    checkpoint.
  - Dependências: M05, R05.
  - Orçamento: IA baixa; GPU confirmatória; preferencialmente 5 seeds do protocolo.

- [ ] **M07 — Gerar embeddings e predições cegas do alvo público.**
  - Objetivo: aplicar o pacote congelado ao grafo-alvo sem adaptação.
  - Entregas: embeddings/predições por ID opaco para cada seed, logs de recursos,
    schema validado e hashes entregues ao custodiante.
  - Aceite: pesos e transformações são byte a byte os de M06; `data/sealed` não
    está montado; zero passo de optimizer; outputs cobrem queries previstas e não
    contêm labels.
  - Proibições: não inspecionar vizinhos “interessantes” usando nomes/tipos.
  - Dependências: M06, H03, H09.
  - Orçamento: IA baixa; GPU/CPU inferência sob teto do protocolo.

- [ ] **M08 — Executar avaliação selada uma única vez.**
  - Objetivo: obter as métricas pré-registradas sem liberar exemplos individuais.
  - Entregas: pacote assinado de métricas/intervalos/contagens, log de unseal,
    checksums de inputs e veredito automático contra critérios pré-fixados.
  - Aceite: custodiante valida hashes, executa ambiente limpo, não muda config,
    devolve somente saídas autorizadas e registra qualquer falha antes de nova
    tentativa com a mesma chave lógica.
  - Proibições: executor do modelo não acessa labels; reexecução divergente exige
    incidente documentado.
  - Dependências: M07, H04, H07, B01, B02; execução pelo custodiante.
  - Orçamento: IA baixa em sessão separada; CPU.

- [ ] **M09 — Executar análises pré-registradas de robustez e atalhos.**
  - Objetivo: determinar se o resultado sobrevive aos controles definidos.
  - Entregas: agregação das seeds, diferença pareada contra melhor baseline,
    degree-matched, nulidades, within-vs-cross gap, classes/cobertura e análise de
    sensibilidade a labels circulares já prevista.
  - Aceite: usa apenas outputs previstos e imutáveis; CIs/multiplicidade seguem
    R06; separa variação técnica de limitação biológica; toda análise nova é
    rotulada exploratória sem retreino confirmatório.
  - Proibições: não mudar exclusões, métrica ou seed após ver score.
  - Dependências: M08, B09.
  - Orçamento: IA baixa; CPU.

- [ ] **M10 — Redigir relatório do MVP e pacote do gate.**
  - Objetivo: responder se há sinal adicional à topologia trivial no par testado.
  - Entregas: `artifacts/reports/MVP.md`, figures/tables geradas, claim ledger
    atualizado, custos reais e opções `prosseguir`, `reformular` ou `encerrar`.
  - Aceite: relata todos os baselines/seeds, efeitos e CIs, falhas, coverage,
    leakage audit, hardware e diferença within/cross; linguagem segue C06.
  - Proibições: não esconder resultado nulo nem chamar um par de universal.
  - Dependências: M09.
  - Orçamento: IA baixa + revisão; sem nova GPU.

- [ ] **G6 — Decidir o MVP e abrir ou encerrar o Nível 2.**
  - Objetivo: aplicar os critérios de falsificação sem mover a trave.
  - Entregas: `docs/gates/G6-MVP.md` com decisão e ramos do pré-registro liberados.
  - Aceite: `GO` exige sinal e controles previstos; `REFORMULAR` distingue nova
    hipótese exploratória; `NO-GO` preserva resultado negativo; identifica se há
    alvo confirmatório ainda intocado.
  - Proibições: não reutilizar alvo revelado como confirmação de hipótese nova.
  - Dependências: M01–M10.
  - Orçamento: pacote por IA baixa; revisão humana científica/estatística.

## Nível 2 — experimento sério

As microfases S executam apenas ramos condicionais já previstos em R07. Depois do
primeiro unseal, qualquer hipótese ou ajuste novo sobre o mesmo alvo é
exploratório. Uma afirmação confirmatória nova exige alvo reservado e intocado.

- [ ] **S01 — Comparar objetivos self-supervised pré-registrados.**
  - Objetivo: testar se masked edge/weight é melhor que reconstrução de
    vizinhança, contrastive controlado e link prediction zero-shot.
  - Entregas: implementações sob encoder/budget comum, testes de augmentations,
    configs e relatório de atalhos por objetivo.
  - Aceite: cada objetivo altera uma variável por vez; contrastive demonstra que
    views preservam sinal; negativos têm controles; link prediction no alvo é
    secundário e não usa fine-tuning.
  - Proibições: não escolher augmentations olhando labels-alvo nem usar masked
    attributes no trilho A.
  - Dependências: G6 com ramo autorizado, M01–M10.
  - Orçamento: IA baixa; GPU conforme budget condicional do R07.

- [ ] **S02 — Executar a escada de arquiteturas.**
  - Objetivo: verificar se complexidade além de GraphSAGE/GIN agrega valor.
  - Entregas: comparação pareada com GAT, relacional/heterogênea quando os dados
    sustentarem e Transformer pequeno apenas no último degrau.
  - Aceite: features, objective, split, seeds e budget de parâmetros são
    controlados; cada degrau só abre se o anterior superar o limiar condicional;
    custo incremental e CI do ganho são reportados.
  - Proibições: sem Transformer por prestígio e sem modelo acima de 20M.
  - Dependências: G6, S01 quando o objetivo mudar; ramo previsto em R07.
  - Orçamento: IA baixa; GPU limitada, com parada por ganho/custo.

- [ ] **S03 — Executar ablações de atributos locais.**
  - Objetivo: medir contribuição incremental de neurotransmissor, região,
    posição/soma e neuropilo no Experimento B.
  - Entregas: adapters/features separados, missingness explícita, baselines por
    modalidade e sequência topology → +atributo individual → combinação;
    representações com região como atributo, nó/bipartido ou grafo heterogêneo
    aparecem em ablações distintas, assim como edges por neurotransmissor.
  - Aceite: atributo existe e é harmonizável em fonte/alvo; encoder e baseline
    recebem a mesma informação; transformações são source-fit; leakage e
    circularidade são reavaliados.
  - Proibições: ausência de campo não vira zero sem máscara e região não entra
    escondida no trilho A.
  - Dependências: G6, cards D02–D08, ramo previsto em R07.
  - Orçamento: IA baixa; CPU/GPU conforme budget; pular com evidência se inviável.

- [ ] **S04 — Abrir ou encerrar o trilho de morfologia.**
  - Objetivo: comparar morphology-only, connectivity-only e combinação quando os
    skeletons forem realmente compatíveis.
  - Entregas: gate interno de escala/cobertura, features/encoder morfológico
    pequeno, controles de posição e comparação pareada, ou relatório de
    inviabilidade.
  - Aceite: unidades, orientação, registro espacial, resampling, missingness e
    cobertura passam; morphology-only não recebe conectividade; combinação usa
    budget controlado.
  - Proibições: não forçar skeletons incompatíveis nem usar registro criado com
    correspondências gold no teste zero-shot.
  - Dependências: G6, D08–D10, ramo previsto em R07.
  - Orçamento: IA baixa; CPU/GPU limitada; gate antes de processamento integral.

- [ ] **S05 — Medir a curva mínima de parâmetros.**
  - Objetivo: estimar a menor capacidade que preserva o sinal transferível.
  - Entregas: configurações aproximadamente 100k, 500k, 1M, 3M e 5M; 10M/20M
    apenas se o pré-registro e a curva justificarem; gráfico ganho/custo.
  - Aceite: arquitetura/objetivo/dados constantes, contagem exata, seeds comuns,
    intervalo por ponto, tempo/energia aproximada e regra de saturação.
  - Proibições: não interpretar parâmetro nominal sem reportar capacidade real e
    não abrir tamanhos maiores após plateau.
  - Dependências: G6, melhor configuração confirmatória congelada.
  - Orçamento: IA baixa; GPU com successive-halving pré-registrado.

- [ ] **S06 — Testar representação, sampling e domain shift.**
  - Objetivo: verificar robustez a decisões de grafo e caracterizar por que a
    transferência cai.
  - Entregas: ablações topology binária, +pesos, thresholds, direção,
    reciprocidade, fanout/subgraph; diagnósticos de sexo, tecido, cobertura,
    reconstrução, densidade e distribuição de grau.
  - Aceite: uma variável por ablação, mesmas seeds, correção de multiplicidade e
    métricas de shift sem usar labels para tuning; conclusões biológicas e
    técnicas permanecem separadas.
  - Proibições: correlação de shift não vira causa e subgrupos pós-hoc ficam
    exploratórios.
  - Dependências: G6, H06, ramo previsto em R07.
  - Orçamento: IA baixa; CPU/GPU conforme matriz reduzida do pré-registro.

- [ ] **S07 — Avaliar estrutura emergente dos embeddings.**
  - Objetivo: testar associação não supervisionada com tipo, neurotransmissor,
    região, pathway e função anotada.
  - Entregas: métricas de clustering e probes definidos, controles por grau,
    permutações e visualizações UMAP/t-SNE rotuladas como ilustração.
  - Aceite: ARI/NMI ou métricas escolhidas têm nulos e CIs; probes respeitam
    source/target; múltiplas labels e missingness são relatadas; figuras não são
    evidência primária.
  - Proibições: não selecionar projeção visual mais bonita nem inferir função
    ausente.
  - Dependências: G6, M06–M09, atributos aprovados quando usados.
  - Orçamento: IA baixa; CPU, sem novo treino salvo ramo previsto.

- [ ] **S08 — Aprofundar calibração, open-set e análises de sensibilidade.**
  - Objetivo: medir confiança e rejeição sob mudanças de prevalência e classes.
  - Entregas: calibration curves geradas, ECE sensitivity, Brier, AUROC/AUPR,
    FPR@TPR, coverage-risk, thresholds source-only e análises por tamanho de tipo.
  - Aceite: conhecida/desconhecida segue H07; calibração é avaliada sem refit no
    alvo; CIs e denominadores aparecem; resultados com e sem labels circulares
    são comparados.
  - Proibições: não calibrar temperatura ou limiar no alvo confirmatório.
  - Dependências: G6, B02, M08, ramo previsto em R07.
  - Orçamento: IA baixa; CPU.

- [ ] **S09 — Executar direção inversa quando cientificamente válida.**
  - Objetivo: testar assimetria A→B versus B→A sem apresentar reuso como nova
    confirmação independente.
  - Entregas: protocolo espelhado, novas transformações source-fit, recursos e
    comparação de cobertura/shift.
  - Aceite: papéis e acesso a labels são redefinidos; limitações de o alvo antigo
    virar fonte são declaradas; alvo da direção inversa não orienta tuning.
  - Proibições: não somar as duas direções como réplicas biológicas independentes.
  - Dependências: G6, compatibilidade aprovada em D10 e ramo previsto em R07.
  - Orçamento: IA baixa; GPU confirmatória ou exploratória conforme pré-registro.

- [ ] **S10 — Executar multi-source leave-one-connectome-out.**
  - Objetivo: testar se diversidade de fontes melhora transferência para um
    terceiro connectoma totalmente deixado de fora.
  - Entregas: folds por connectoma, normalização sem alvo, harmonização comum,
    baseline single-source e pacote de avaliação para cada holdout elegível.
  - Aceite: pelo menos três datasets biologicamente defensáveis; nenhum node do
    holdout entra no treino/seleção; métricas são agregadas por connectoma e não
    apenas por neurônio.
  - Proibições: não chamar recortes do mesmo indivíduo de fontes independentes.
  - Dependências: G6, G2 com datasets extras, ramo previsto em R07.
  - Orçamento: IA baixa; GPU por fold com teto total pré-aprovado; dispensar se
    não houver três datasets.

- [ ] **S11 — Consolidar estatística e atualizar a auditoria de novidade.**
  - Objetivo: integrar efeitos, incerteza, robustez e literatura contemporânea
    sem inflar a conclusão.
  - Entregas: analysis dataset imutável, relatório confirmatório/exploratório
    separado, atualização reproduzível de L01–L07 e claims finais candidatos.
  - Aceite: todas as runs previstas e falhas aparecem; efeitos por connectoma,
    classe e seed não são confundidos; multiplicidade segue R06; busca de
    anterioridade é repetida até a data do manuscrito.
  - Proibições: análise exploratória não é movida retroativamente para o plano
    confirmatório.
  - Dependências: S01–S10 executadas ou dispensadas com evidência.
  - Orçamento: IA baixa + revisão estatística/científica; CPU.

- [ ] **S12 — Fazer auditoria adversarial independente.**
  - Objetivo: tentar refutar resultados antes do gate de paper.
  - Entregas: revisão de leakage, código de métricas, provenance, labels,
    estatística, cherry-picking, hardware e claims; lista de achados por
    severidade e correções rastreadas.
  - Aceite: revisor não é a sessão executora; achados críticos/altos são
    corrigidos e reavaliados sem apagar histórico; mudança pós-unseal é marcada
    exploratória ou exige novo alvo.
  - Proibições: não reduzir severidade para liberar o gate.
  - Dependências: S11.
  - Orçamento: IA econômica em contexto separado + revisão humana.

- [ ] **G7 — Decidir se a evidência sustenta um projeto de paper.**
  - Objetivo: escolher entre paper de resultado, paper negativo/benchmark,
    relatório técnico ou encerramento.
  - Entregas: `docs/gates/G7-PAPER.md` com escopo de claims e pendências.
  - Aceite: validade, novidade, número de indivíduos, reprodutibilidade,
    licenças, efeito, incerteza e auditoria são julgados; título/abstract
    provisórios não excedem C06.
  - Proibições: significância isolada não aprova paper e revisão humana é
    obrigatória.
  - Dependências: S01–S12.
  - Orçamento: pacote por IA baixa; painel humano científico/estatístico.

## Nível 3 — reprodução e comunicação científica

- [ ] **P01 — Congelar o pacote de resultados e sua linhagem.**
  - Objetivo: criar uma fonte única e imutável para o manuscrito.
  - Entregas: release candidate interna com código, configs, manifests, métricas,
    hashes, logs de desvios e claim-evidence map; sem dados não redistribuíveis.
  - Aceite: cada número planejado aponta para run/manifests; checksums validam;
    falhas e resultados nulos permanecem; ambiente e hardware são capturados.
  - Proibições: não editar métricas ou figures manualmente.
  - Dependências: G7.
  - Orçamento: IA baixa; CPU.

- [ ] **P02 — Reproduzir do zero no hardware-alvo.**
  - Objetivo: provar que instruções e caches não escondem dependências.
  - Entregas: clone/ambiente limpo, obtenção de dados conforme licença,
    preprocessamento, pelo menos uma seed representativa e geração integral dos
    resultados agregados permitidos.
  - Aceite: tolerâncias numéricas pré-fixadas passam; tempo/RAM/VRAM/disco são
    medidos; nenhum cache externo é necessário; divergência abre incidente.
  - Proibições: não copiar ambiente ou artifacts antigos para “reproduzir”.
  - Dependências: P01.
  - Orçamento: IA baixa; GPU confirmatória conforme orçamento publicado.

- [ ] **P03 — Obter reprodução independente.**
  - Objetivo: testar se outra sessão/pessoa consegue repetir sem conhecimento
    tácito.
  - Entregas: protocolo entregue apenas com documentação pública, relatório do
    reprodutor, comparação de hashes/métricas e issues resolvidas.
  - Aceite: reprodutor não foi executor principal; resultado passa tolerância ou
    falha é publicada como limitação; instruções corrigidas não reescrevem o
    relatório original.
  - Proibições: autor principal não guia passo a passo durante a tentativa cega.
  - Dependências: P02.
  - Orçamento: IA econômica em sessão separada + pessoa independente quando
    possível; GPU conforme uma reprodução.

- [ ] **P04 — Gerar figuras, tabelas e suplemento automaticamente.**
  - Objetivo: comunicar resultados sem transcrição manual ou seleção estética.
  - Entregas: scripts/configs de figuras, dados agregados, legendas, tabelas de
    datasets/modelos/recursos/métricas e suplemento de ablações.
  - Aceite: build limpo regenera tudo; paleta acessível e incerteza/denominadores
    visíveis; UMAP/t-SNE identificados como exploratórios; números reconciliam
    com P01.
  - Proibições: não omitir baseline/seed por aparência.
  - Dependências: P01, P02.
  - Orçamento: IA baixa; CPU.

- [ ] **P05 — Atualizar related work e fechar a claim de novidade.**
  - Objetivo: verificar anterioridade até a data de submissão.
  - Entregas: rerun de L01, novos trabalhos triados, comparação direta com os mais
    próximos e claim de contribuição revisada.
  - Aceite: datas/strings/resultados da atualização são registrados; paper novo
    que reduz novidade altera título/claim; ausência de acesso fica explícita.
  - Proibições: não ignorar trabalho concorrente inconveniente.
  - Dependências: P01, S11.
  - Orçamento: IA baixa; web; revisão científica.

- [ ] **P06 — Redigir manuscrito e declaração de limites.**
  - Objetivo: escrever métodos reproduzíveis e conclusões proporcionais.
  - Entregas: título, abstract, introdução, related work, métodos, resultados,
    discussão, limitações, ética/licenças e checklist de reprodutibilidade.
  - Aceite: cada claim quantitativo aponta a artefato; diferença entre técnica e
    réplica biológica aparece; negativos/circularidade/domain shift e hardware
    estão no texto; linguagem segue G7.
  - Proibições: não dizer “reconhece função” quando target é tipo anotado.
  - Dependências: P03–P05.
  - Orçamento: IA baixa para redação guiada + revisão humana de autores.

- [ ] **P07 — Preparar pacote público conforme licença e FAIR.**
  - Objetivo: maximizar repetibilidade sem redistribuir material proibido.
  - Entregas: README de reprodução, licença do código, CITATION, manifests,
    scripts de obtenção, model/data cards, SBOM/dependency audit e instruções para
    rótulos/dados que o usuário deve obter na origem.
  - Aceite: scanner não encontra token, caminho local, label selado ou dado bruto;
    licenças são compatíveis; checksums e versões persistentes existem; pacote
    instala em ambiente limpo.
  - Proibições: não fazer upload ou publicar nesta microfase.
  - Dependências: P01–P06.
  - Orçamento: IA baixa + revisão de licença; CPU.

- [ ] **P08 — Submeter o pacote a revisão interna final.**
  - Objetivo: realizar peer review adversarial de ciência, estatística, segurança
    de dados e comunicação.
  - Entregas: pareceres independentes, resposta item a item, revisions rastreadas
    e gate checklist atualizado.
  - Aceite: achados críticos/altos fechados com evidência; análises novas são
    rotuladas corretamente; reprodução continua passando após revisão.
  - Proibições: não remover crítica não resolvida do histórico.
  - Dependências: P06, P07.
  - Orçamento: duas sessões econômicas separadas + revisores humanos.

- [ ] **P09 — Arquivar e decidir publicação.**
  - Objetivo: produzir um snapshot citável e uma decisão humana de divulgação.
  - Entregas: pacote final, hashes, changelog, versão, destino proposto, checklist
    de autoria/conflitos/licenças e plano de preservação; publicação somente em
    ação separada e autorizada.
  - Aceite: artefato local pode ser reconstruído; autores aprovam texto e claims;
    termos de cada dataset permitem o conteúdo; DOI/repositório são registrados
    apenas depois de existirem.
  - Proibições: IA não submete paper, cria conta, aceita termos ou publica sem
    autorização explícita.
  - Dependências: P08.
  - Orçamento: IA baixa para pacote; decisão humana.

- [ ] **G8 — Encerrar o projeto de pesquisa.**
  - Objetivo: registrar o desfecho real, inclusive negativo ou inconclusivo.
  - Entregas: `docs/gates/G8-ENCERRAMENTO.md`, índice dos artefatos, custos totais,
    questões abertas e próximos estudos que não sejam vendidos como concluídos.
  - Aceite: estado de todas as fases, desvios, datasets, runs, claims, publicação
    e preservação é reconciliado; prompt principal é aposentado. O NEXT não abre
    automaticamente: seu handoff começa em `docs/PLANO-MICROFASES-NEXT.md`.
  - Proibições: gate não depende de resultado positivo.
  - Dependências: P01–P09 executadas ou formalmente encerradas conforme G7.
  - Orçamento: IA baixa + aprovação humana final.

## Evidência por microfase

Ao concluir uma fase, inserir logo abaixo do item, sem reescrever objetivo ou
aceite:

```text
Evidência (AAAA-MM-DD, executor): arquivos; fontes/versões; comandos e testes;
resultado resumido; recursos medidos; decisão/limitação; commit <hash>.
```

Gates usam `docs/templates/DECISAO-GATE.md`. Não preencha evidências
antecipadamente.
