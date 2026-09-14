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

- [x] **D08 — Auditar ontologias, crosswalks e independência dos rótulos.**
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
  Bloqueio (2026-09-14, executor): pacote preparado em
  `research/datasets/CROSSWALK-AUDIT.md` com 7 pares (PAIR-01 a PAIR-07) e 4
  decisões (DEC-CW-01 a DEC-CW-04), todas `aguardando dupla revisão humana`;
  nenhum mapping exato foi gerado e o documento público contém apenas método,
  proveniência e agregados; a fase fica `[ ]` porque o orçamento exige dupla
  revisão humana e o protocolo reserva a aprovação de crosswalk ao revisor;
  validação estrutural com smoke negativo em `tools/validate_research.py`
  (21,8 MB de RAM, 0,09 s, sem GPU); próxima ação humana: revisar e assinar as
  decisões; commit c20399bc6da8303dce2cbd6311f50171fea1d071.
  Evidência (2026-09-14, executor + revisor humano): arquivos
  `research/datasets/CROSSWALK-AUDIT.md` (status dos 7 pares e das 4 decisões
  `APROVADO`; seção 8 com data, aprovador e escopo), `tools/validate_research.py`
  (estado aprovado do crosswalk) e esta linha; fontes/versões: aprovação do
  revisor humano Alexandre Zanata em 2026-09-14 e documentos internos de
  C03/D02–D07, nenhuma fonte externa nova, Python 3.12.2 (stdlib); comandos e
  testes: `python3 tools/validate_research.py` com smoke negativo inline (seção
  ausente, pendência do segundo revisor não declarada, aprovador não humano,
  campo ausente e status inválido), `python3 tools/validate_plan.py`,
  `git diff --cached --check` e `git status --porcelain`; resultado: DEC-CW-01 a
  DEC-CW-04 e PAIR-01 a PAIR-07 aprovados integralmente, mapping exato selado e
  ausente do repositório, guarda contra IDs no documento público ativa; recursos:
  21,8 MB de RAM e 0,09 s no validador, sem GPU; decisão/limitação: aprovação
  registrada por um único revisor humano; a dupla revisão permanece pré-condição
  para criar ou validar qualquer mapeamento manual concreto nas fases seguintes;
  arquivos não relacionados preservados fora do commit; commit
  11f71a184a01b47dcfc70d47aa53cd44dbaed834.

- [x] **D09 — Estimar escala e fazer spikes mínimos de acesso.**
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
  Evidência (2026-09-14, executor): arquivos `research/datasets/RECURSOS.md`
  (7 seções, 6 amostras medidas com md5 oficial e sha256, projeções separando
  publicado/medido/inferido com intervalo e margem), `research/datasets/INVENTARIO.md`
  (link para RECURSOS.md), `tools/spike_d09.py` (sondas inspect/parquet/csr) e
  `tools/validate_research.py` (checagem D09 com smoke negativo inline);
  fontes/versões: Zenodo 10.5281/zenodo.10676866, buckets GCS
  `flyem-manc-exports`/`flyem-male-cns`/`flyem-optic-lobe`, Dataverse
  10.7910/DVN/7WTH1N, LIT-0001/0006/0010/0019/0020/0072/0074/0079, acessos
  2026-09-14, Python 3.12.2 (pandas 3.0.3, pyarrow 24.0.0, scipy 1.18.0, numpy);
  comandos e testes: `python3 tools/spike_d09.py inspect|parquet|csr` nas 6
  amostras, `md5sum`/`sha256sum` contra md5 oficial das APIs, smoke negativo da
  checagem D09 (seção, token, menos de 6 amostras, LIT inexistente, ID cru),
  `python3 tools/validate_research.py`, `python3 tools/validate_plan.py` e
  `git diff --cached --check`; resultado: 6/6 md5 oficiais conferem, MANC
  traçado com 5.243.574 arestas a 20,0 B/aresta COO e 8,02 B/nnz CSR,
  Parquet+Arrow zstd 0,322–0,511× do feather, BANC com pico projetado de
  7,6–15,2 GB em 32 GB, MAOL sem tabela pública (varredura de 20.000 objetos) e
  FlyWire/MCNS/hemibrain sem contagem de linhas publicada (não projetados);
  recursos medidos: 226,2 MB de disco temporário (21,4% do teto), pico de RSS
  1.122,5 MB, sem GPU, transferência 6,4–17,7 MB/s; decisão/limitação: nenhum
  dump integral antes do gate; disco local com 34 GB livres não comporta
  BANC+MCNS completos, exigindo armazenamento externo antes da ingestão;
  divergências registradas para reconciliar (total FlyWire do card vs API,
  188.508 vs 188.162 linhas no BANC, varredura MAOL com teto); commit
  fe08b5024f7b0085a4b53dea4fd156423a97fbfc.

- [x] **D10 — Ranquear pares, escolher papéis e definir fallback.**
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
  Evidência (2026-09-14, executor): arquivos `research/datasets/SELECAO.md`
  (9 seções: notas dos 6 datasets, ranking de 7 pares, MVP MANC→MCNS com 7
  condições de defensabilidade, matriz de fallback com 6 modos de falha e
  DEC-SEL-01 a DEC-SEL-04), `research/datasets/INVENTARIO.md` (link) e
  `tools/validate_research.py` (checagem D10 com smoke negativo inline);
  fontes/versões: cards D02–D07, CROSSWALK-AUDIT aprovado em D08 (PAIR-01 a
  PAIR-07, DEC-CW-01 a DEC-CW-04), RECURSOS.md (D09), LIT-0001/0002/0006/0007/
  0009/0010/0011/0014/0015/0016/0019/0020/0023/0027/0034/0038/0060/0068/0070/
  0072/0074/0076/0078/0079 e reconferência das páginas Janelia do MaleCNS e do
  MANC em 2026-09-14, sem download; comandos e testes: `python3
  tools/validate_research.py` (smoke negativo: seção, token, status aprovado
  indevido, LIT inexistente, menos de 6 pares e ID cru), `python3
  tools/validate_plan.py` e `git diff --cached --check`; resultado: MVP proposto
  MANC `manc:v1.2.1` → MCNS `male-cns:v1.0` (mesmo sexo, tecidos sobrepostos,
  PAIR-04 aprovado, CC BY nos dois lados), reserva confirmatória BANC `v888`,
  reserva alternativa FlyWire `v783`, hemibrain como comparador e MAOL proibido
  no MVP por ser o mesmo indivíduo do MCNS; recursos medidos: 0 download
  adicional (0 MB), sem GPU, sem acesso a `data/sealed`; decisão/limitação: a
  escolha do par exige revisão humana no G2 conforme PROTOCOLO, as quatro
  decisões ficam `proposta (pendente de G2)` e nenhuma foi aprovada pela IA;
  condições incluem crosswalk com dois revisores, sensibilidade a
  circularidade, checksum ausente do MCNS a registrar no download e
  armazenamento externo para o bulk; commit
  ca50f4b26fa97651f4e781ac4cd0ce43de2d2105.

- [x] **G2 — Aprovar dados e par do MVP.**
  - Objetivo: decidir `GO`, `NO-GO` ou `REFORMULAR` antes do download completo.
  - Entregas: `docs/gates/G2-DADOS.md`, cards congelados e papéis dos datasets.
  - Aceite: licença/acesso, comparabilidade, target, cobertura, recursos,
    crosswalk e circularidade têm parecer; alvo confirmatório fica reservado.
  - Proibições: se nenhum par passar, não substituir silenciosamente por split do
    mesmo connectoma; produzir relatório de inviabilidade/reformulação.
  - Dependências: D01–D10.
  - Orçamento: pacote por IA baixa; revisão humana científica e de termos.
  Evidência (2026-09-14, executor): pacote `docs/gates/G2-DADOS.md` com 9
  critérios, 10 arquivos congelados por SHA-256 e releases fixados; decisão
  humana `GO` registrada em 2026-09-14 por Alexandre Zanata (revisor único
  acumulando responsável científico e termos/licenças; limitação declarada),
  aprovando DEC-SEL-01 a DEC-SEL-04 (MVP MANC `manc:v1.2.1` → MCNS
  `male-cns:v1.0`; reservas BANC `v888` e FlyWire `v783`; matriz de fallback;
  MAOL excluído e hemibrain comparador); o executor apenas registrou a decisão;
  fontes/versões: D08/D09/D10 e LIT-0001/0002/0006/0009/0010/0015/0019/0023/
  0060/0074/0078/0079, acessos 2026-09-14; comandos e testes: `python3
  tools/validate_research.py` (checagem G2 com smoke negativo e hashes
  conferidos), `python3 tools/validate_plan.py` e `git diff --cached --check`;
  resultado: `GO` condicionado liberando apenas R01–R08, sem download integral
  antes de G3, treino, unseal ou leitura de `data/sealed`; recursos medidos: 0
  download nesta fase, sem GPU; decisão/limitação: revisor único (segundo
  revisor do crosswalk segue obrigatório antes de H07), armazenamento externo e
  SHA-256 local do MCNS antes do bulk, alvo confirmatório BANC intocado, e a
  limitação de revisor único deve constar do pré-registro em R07; commit
  29ded3a2c5fe6d3dc0d3f84871479ddefbe8ae04.

## Nível 1 — infraestrutura, dados e MVP confirmatório

### Reprodutibilidade, avaliação selada e pré-registro

- [x] **R01 — Criar estrutura mínima e plano de gestão de dados.**
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
  Evidência (2026-09-14, executor): arquivos `data/README.md` (zonas e regras
  rápidas), `docs/research/DATA-MANAGEMENT.md` (10 seções: fonte de verdade,
  layout, releases/checksums, retenção/backup/limpeza, licenças/redistribuição,
  regeneráveis, selados/firewall, segredos, teste, limitações),
  `tools/check_data_hygiene.py` (11 sentinelas, 3 arquivos permitidos e 10
  diretórios) e `.gitignore` (bloco explícito `data/sealed/`, `*.token` e
  `tokens/`); fontes/versões: G2 `GO`, D09/D10, PROTOCOLO (zonas e firewall),
  cards D02–D07 e LIT-0001/0010/0070/0074/0076/0078/0079, acessos 2026-09-14,
  Python 3.12.2 (stdlib); comandos e testes: `python3
  tools/check_data_hygiene.py` (PASS: 11 sentinelas ignoradas, 0 vazamento em
  `git status`, 3 arquivos permitidos rastreáveis, 10 diretórios presentes,
  13.252 KB de RSS, 0,11 s), `python3 tools/validate_research.py` (nova checagem
  R01 com smoke negativo: seção, token, link, `.gitignore`, ID cru e LIT
  inexistente), `python3 tools/validate_plan.py` e `git diff --cached --check`;
  resultado: layout criado (`data/raw/source`, `data/raw/target-public`,
  `data/raw/spikes`, `data/manifests`, `data/sealed/target-labels`,
  `artifacts/reports`, `artifacts/frozen`, `runs`, `checkpoints`, `outputs`) e
  política separando raw, manifestos, selados e regeneráveis; falha encontrada e
  corrigida antes do commit: o primeiro teste de higiene tratava
  `data/README.md` como sentinela gravável e o apagava, ajustado para verificar
  o arquivo sem sobrescrevê-lo; recursos medidos: 0 download, 0 MB, sem GPU;
  decisão/limitação: backup externo ainda não designado e schema de manifestos
  fica para R03; a zona `data/sealed/target-labels/` foi criada vazia e nenhum
  dado selado foi lido ou gerado; commit
  f92f721f0d1d73c8b7bcc1170242480011781fde.

- [x] **R02 — Fixar ambiente e capturar hardware.**
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
  Evidência (2026-09-14, executor): arquivos `environment/README.md`
  (requisitos, instalação Linux/CUDA, justificativa e licença por dependência),
  `environment/requirements.lock` (40 pinos do venv limpo),
  `tools/check_environment.py` (diagnóstico + operação CUDA mínima),
  `artifacts/reports/AMBIENTE-R02.md` e `artifacts/reports/AMBIENTE-R02.json`
  (métricas geradas pelo script) e `.venv/` local ignorado (5,8 GB); fontes/
  versões medidas: Pop!_OS 24.04 LTS, kernel 7.1.5-76070105-generic, Python
  3.12.2 (CPython), RTX 4060 Laptop 8.188 MiB driver 580.173.02 compute 8.9,
  torch 2.14.0+cu130 com runtime CUDA 13.0, numpy 2.5.3, scipy 1.18.1, pandas
  3.0.5, pyarrow 25.0.1, pytest 9.1.1, pip 26.2.1; licenças lidas dos metadados
  (BSD-3-Clause/BSD, Apache-2.0, MIT e expressão agregada do torch) e
  justificativa em `research/literature/METHODS.md` (L06); comandos e testes:
  criação de venv + instalação (3m45s), `.venv/bin/python
  tools/check_environment.py --json-out artifacts/reports/AMBIENTE-R02.json`
  PASS (CUDA disponível, multiplicação 1024² em 0,14 s com resultado finito,
  42 MiB de VRAM reservada, RSS 826,8 MiB, 2,93 s), resolução do lock em venv
  vazio com `pip install --dry-run` em 11,4 s, nova checagem R02 no
  `validate_research.py` com smoke negativo (token, pino, GPU, CUDA, driver,
  caminho local e ID cru), `validate_plan.py` e `git diff --cached --check`;
  resultado: ambiente limpo reproduzível com lock pinado e smoke CUDA aprovado,
  hardware conferindo com o ESCOPO; recursos medidos: disco livre caiu de 31,5
  para 23,2 GiB (venv de 5,8 GB), sem download de dados e sem GPU além do
  smoke; decisão/limitação: lock sem hashes de wheel (evoluível em R03), PyG/DGL
  adiados para M02/M03 por não terem uso imediato, driver NVIDIA proprietário
  fora do Git, instalação byte a byte em outra máquina fica para P02; commit
  fff7f62bc640635c98c8bd79d82409d0214f8389.

- [x] **R03 — Implementar proveniência, manifests e download idempotente.**
  - Objetivo: tornar toda entrada identificável e reobtível.
  - Entregas: schema de manifest, validador, comandos de download por release e
    testes com fixture/local HTTP; manifests versionados sem credenciais.
  - Aceite: resume download interrompido quando seguro, valida tamanho/checksum,
    nunca sobrescreve arquivo divergente e registra URL, release, licença e data.
  - Proibições: não automatizar bypass de termos nem registrar URL assinada/token.
  - Dependências: R01, R02, cards aprovados no G2.
  - Orçamento: IA baixa; CPU; fixture pequena.
  Evidência (2026-09-14, executor): arquivos `schemas/manifest.schema.json`
  (JSON Schema draft 2020-12), `tools/manifest.py` (validador stdlib com
  `--check-files`/`--schema-only`), `tools/download.py` (download idempotente
  com `.part`, `Range`/206, verificação e `--max-bytes`), `tests/test_manifest.py`
  e `tests/test_download.py` (servidor HTTP local, fixture de 64 KiB),
  `docs/research/PROVENANCE.md` (6 seções) e 4 manifestos versionados
  (`data/manifests/flywire-783.json`, `manc-v1.0.json`, `mcns-v1.0.json`,
  `banc-888.json`) cobrindo as 6 amostras de D09; fontes/versões: cards D02–D07,
  D09/G2, GCS/Dataverse/Zenodo (URLs públicas, sem credenciais), Python 3.12.2
  (stdlib; sem dependência nova e sem alterar o lock de R02); comandos e testes:
  `.venv/bin/python -m pytest tests/ -q` (24 passaram em 4,57 s),
  `python3 tools/manifest.py validate --check-files` (4 manifestos válidos com
  bytes/sha256/md5 revalidados) e `--schema-only`,
  `python3 tools/download.py --manifest … --path …` (dois arquivos `skipped`,
  0 bytes transferidos e 0 requisições), nova checagem R03 no
  `validate_research.py` com smoke negativo (seção, token, ID cru, URL com
  credencial, licença e sha256 inválidos), `validate_plan.py` e
  `git diff --cached --check`; resultado: toda entrada tem manifesto com URL,
  release, licença, data, bytes e sha256; download retoma interrompido com 206,
  nunca sobrescreve divergente e confere checksum antes de promover; falha
  encontrada e corrigida pelo teste: transferência incompleta era tratada como
  checksum divergente e apagava o `.part`, agora preserva para retomada;
  recursos medidos: CPU apenas, ~0,1 s por manifesto, 4,57 s de suíte, sem GPU
  e sem downloads externos; decisão/limitação: retomada não detecta mudança
  remota com a mesma URL (sha256 final é a salvaguarda), MCNS sem checksum
  oficial usa sha256 local, manifestos cobrem só as amostras D09 e o validador
  é implementação própria (sem `jsonschema`) para não alterar o lock; commit
  ab1836f6e1ee55f3d2745260e65de27ae2dc2352.

- [x] **R04 — Fixar contrato de configuração, run e determinismo.**
  - Objetivo: eliminar parâmetros escondidos e resultados sem linhagem.
  - Entregas: schema de configuração, implementação do `RUN-MANIFEST`, seeds
    centralizadas, captura de Git/ambiente/recursos e teste de repetição.
  - Aceite: duas execuções determinísticas da fixture geram mesmas saídas ou a
    tolerância numérica documentada; toda opção efetiva é serializada; run ID é
    imutável e outputs divergentes não colidem no cache.
  - Proibições: sem default dependente da máquina ou timestamp usado como seed.
  - Dependências: R02, R03.
  - Orçamento: IA baixa; CPU; sem treino real.
  Evidência (2026-09-14, executor): arquivos `schemas/run-config.schema.json` e
  `schemas/run-manifest.schema.json` (JSON Schema 2020-12), `tools/run.py`
  (config resolvida, `run_id` imutável, cache verificado por SHA-256,
  RUN-MANIFEST em `runs/<run_id>/manifest.json`), `tools/seeds.py` (seeds
  centralizadas e independentes de relógio), `configs/fixture.json`,
  `tests/test_run_contract.py` (18 casos) e `docs/research/RUN-CONTRACT.md`
  (7 seções); fontes/versões: R02/R03 e PROTOCOLO, Python 3.12.2, sem
  dependência nova, sem download de dados e sem GPU; comandos e testes:
  `.venv/bin/python -m pytest tests/ -q` (42 passaram em 4,71 s; 18 novos),
  `.venv/bin/python tools/run.py --config configs/fixture.json` (completed;
  segunda execução `cached` sem reescrita; `run_id=f39e7779b00ad433`;
  `outputs/stream.bin` 8192 bytes `sha256=35c06f34…`; `outputs/summary.json`
  983 bytes `sha256=9d18bdc4…`), nova checagem R04 no `validate_research.py`
  com smoke negativo (seção, token, campo fora do schema, seed ausente e ID
  cru), `validate_plan.py` e `git diff --cached --check`; resultado: toda opção
  efetiva serializada (defaults `n_bytes=4096`, `repeats=2` sempre gravados),
  `run_id` derivado de configuração + commit + versão, seeds derivadas por
  SHA-256 e registradas, timestamp nunca usado como seed, duas execuções com
  saídas byte a byte idênticas e saída divergente bloqueada sem sobrescrita;
  recursos medidos: fixture em 0,0005 s, pico de RSS 23,03 MiB, disco livre
  149,83 GiB, CPU apenas; decisão/limitação: fixture sintética prova o contrato
  e não desempenho; tolerância numérica zero documentada; `git_dirty=true` é
  esperado pelo workstream NEXT e o diff exato fica em `dirty_diff_sha256`;
  run interrompido sem manifesto exige limpeza manual para preservar a
  imutabilidade; commit 71f81864305110854c44feb947c8e82903971add.

- [x] **R05 — Implementar o firewall do alvo e teste antileakage.**
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
  Evidência (2026-09-14, executor): arquivos `tools/firewall.py` (scanner de
  referências, trilha de auditoria para `open`/`os.listdir`/`os.scandir`,
  abertura guardada, filtro de log por caminho/coluna e inventário só com
  hashes), `docs/research/FIREWALL.md` (8 seções: zonas, permissões/custódia,
  scanner, barreiras de runtime, inventário, testes, unseal/invalidação e
  limitações) e `tests/test_firewall.py` (7 casos, incluindo auditoria e
  pipeline público em subprocesso); permissões `700` aplicadas a
  `data/sealed/` e `data/sealed/target-labels/`; marcas `firewall-allow` nos
  pontos legítimos de `tools/check_data_hygiene.py` e
  `tools/validate_research.py`; fontes/versões: R01/R04, C05, PROTOCOLO
  (zonas e firewall) e fases H07/G3/M08, Python 3.12.2 (stdlib, sem
  dependência nova), sem download e sem GPU; comandos e testes: `.venv/bin/python
  -m pytest tests/ -q` (49 passaram em 4,83 s; 7 novos), `python3
  tools/firewall.py scan` (limpo) e `inventory` (`count=0`),
  `python3 tools/validate_research.py` (nova checagem R05 com smoke negativo de
  seção/token/ID cru e smoke de permissões: 755 reprova, 700 aprova),
  `python3 tools/validate_plan.py` e `git diff --cached --check`; resultado: o
  pipeline público roda com o firewall armado sem tocar o selado, tentativas
  sentinela de abrir/listar são bloqueadas, logs com caminho ou coluna proibidos
  falham, inventário expõe apenas hashes e o repositório não tem referências
  proibidas fora das marcas; recursos medidos: CPU apenas, suíte em 4,83 s, sem
  GPU e sem dados brutos; decisão/limitação: usuário único torna a separação
  procedural (limitação declarada), a revisão de segurança metodológica fica
  para o G3, a lista final de colunas proibidas virá do schema selado de H07 e o
  hook de auditoria é permanente por processo (usado no avaliador/subprocesso,
  não na sessão do executor); commit
  a9b8a2dccd7ad19d77db9c13ca28cf5662952bca.

- [x] **R06 — Especificar o plano estatístico e avaliador selado.**
  - Objetivo: definir cálculo, incerteza e outputs antes de observar o alvo.
  - Entregas: `docs/research/STATISTICAL-ANALYSIS-PLAN.md`, schema de predições e
    contrato do comando avaliador.
  - Aceite: fixa métrica primária, SESOI, denominadores, macro/micro, CIs,
    bootstrap agrupado, permutações, múltiplas comparações, seeds, missing labels,
    classes pequenas, open-set, calibração e formato de resultado sem IDs/labels.
  - Proibições: não tratar nós como observações biológicas independentes.
  - Dependências: C04, D08, D10, R05.
  - Orçamento: IA baixa + revisão humana de estatística; sem GPU.
  Evidência (2026-09-14, executor): arquivos
  `docs/research/STATISTICAL-ANALYSIS-PLAN.md` (12 seções fixando métrica
  primária Macro Recall@1 no T0, cálculo exato, SESOI de 5 pontos percentuais,
  denominadores, missing/ambíguo/conflitante/singleton/classes pequenas,
  bootstrap agrupado por tipo com 10.000 reamostragens, permutações, família
  Holm de 3 testes, 5 seeds com mediana e intervalo, open-set AUROC/AUPR/
  FPR@TPR95, calibração Brier/ECE com 15 bins e temperatura source-fit,
  ordem da análise e contrato do avaliador),
  `schemas/predictions.schema.json` (IDs opacos `q`/`g`, top-10, sem rótulos) e
  `schemas/metrics.schema.json` (agregados com hashes de entrada, contagens,
  CIs, p-valores; sem resultados por neurônio), `tools/evaluator_contract.py`
  (validação dos dois pacotes e recusa de rótulos/IDs crus) e
  `tests/test_evaluator_contract.py` (21 casos); fontes/versões: C02–C05, D08,
  D10, R04/R05, PROTOCOLO e árvore de C04, Python 3.12.2 (stdlib, sem
  dependência nova), sem download e sem GPU; comandos e testes:
  `.venv/bin/python -m pytest tests/ -q` (70 passaram em 4,88 s; 21 novos),
  `python3 tools/evaluator_contract.py validate predictions|metrics`,
  nova checagem R06 no `validate_research.py` (28 tokens, seções, sincronia
  schema/validador e smoke negativo de seção/token/ID cru),
  `python3 tools/validate_plan.py` e `git diff --cached --check`; resultado: o
  cálculo, a incerteza e o formato dos resultados ficam definidos antes do
  alvo, sem IDs ou labels no pacote público e com a regra explícita de que
  neurônios do mesmo grafo e seeds de treino não são réplicas biológicas
  independentes; recursos medidos: CPU apenas, suíte em 4,88 s, sem GPU e sem
  dados brutos; decisão/limitação: K de cobertura, limiar do gap within-vs-cross
  e contagem final de seeds ficam marcados `R07`, a revisão humana de
  estatística é obrigatória em R07/G3 e as contagens reais de classes dependem
  de H07; commit 71cac93531312d5d6798308774faf610750843b3.

- [x] **R07 — Redigir e assinar o pré-registro.**
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
  Evidência (2026-09-14, executor): pré-registro **assinado** — decisão humana
  `(a) assinar como está`, com Alexandre Zanata acumulando os três papéis
  (responsável científico, revisor de estatística e custodiante; limitação
  declarada) em 2026-09-14; arquivos `preregistration/PROTOCOL.md` (15 seções:
  fonte MANC `manc:v1.2.1` → alvo MCNS `male-cns:v1.0`, BANC `v888` reservado e
  FlyWire `v783` reserva, população, features do trilho A, modelo/baselines,
  grid fixo de 12 trials, 5 seeds finais, stopping 20/200, métricas/SESOI de
  5 p.p./K=10/exclusões, análises, condicionais do Nível 2, exploratório vs
  confirmatório, unseal e changelog), cards `E1`–`E3`, `CHANGELOG.md` e
  `REGISTRY.md` com 12 artefatos congelados por SHA-256 e hash de pacote
  `9411af0c…`; o executor apenas registrou a decisão, sem alterar nenhum
  artefato congelado; fontes/versões: R03–R06, G2, C02–C05, D08–D10 e
  PROTOCOLO, Python 3.12.2 (stdlib, sem dependência nova); comandos e testes:
  `python3 tools/validate_research.py` (checagem R07 agora `ASSINADO`, com
  verificação do hash do pacote contra os 12 artefatos e smoke negativo de
  hash divergente/seção ausente/assinatura com plano aberto),
  `python3 tools/validate_plan.py`, `.venv/bin/python -m pytest tests/ -q`
  (70 passaram) e `git diff --cached --check`; resultado: protocolo
  confirmatório congelado com fonte/alvo/versões, features, modelo, baselines,
  grid de 12 trials, seeds, stopping, métricas, SESOI, exclusões e decisões
  condicionais; recursos medidos: CPU apenas, sem GPU, sem downloads e sem
  acesso a `data/sealed`; decisão/limitação: revisor único acumula os três
  papéis (declarado no `REGISTRY.md` e no changelog), a versão assinada `1.0`
  mantém os mesmos bytes da minuta e qualquer mudança futura exige changelog e
  nova assinatura; commit f162f693cf41059f3850a6f2f199f5b79ca2446d.

- [x] **R08 — Ensaiar o protocolo completo em dados sintéticos e congelar versão.**
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
  Evidência (2026-09-14, executor): arquivos `tools/dry_run.py` (fixture
  sintética com 3 tipos conhecidos e 1 unknown, estágios de geração, download
  local via HTTP + `tools/download.py`, pré-processamento, treino trivial MLP
  em CPU, congelamento com hashes, inferência opaca e avaliação selada no
  ambiente sintético sob firewall), `tests/test_dry_run.py` (5 casos, incluindo
  sabotagem proposital de leakage que falha como esperado e recusa de predição
  com label), `artifacts/reports/DRY-RUN-R08.md` e `DRY-RUN-R08.json` e
  `docs/research/HANDOFF-CUSTODIAN.md` (pacote de handoff); tag interna do
  protocolo `dryrun-1.0-f90a4927`; hashes de predições `9f1ad2cf…` e métricas
  `bbbf9e82…`; fontes/versões: R03–R07, schemas R06, PROTOCOLO e firewall R05,
  Python 3.12.2 com torch do lock R02 (sem dependência nova), nenhum dado real
  de fonte ou alvo; comandos e testes: `.venv/bin/python tools/dry_run.py
  --workdir runs/dryrun-r08` (ponta a ponta, 70 consultas, 13 rejeições, scanner
  de firewall limpo, download idempotente `skipped` na segunda chamada),
  `.venv/bin/python -m pytest tests/ -q` (75 passaram; 5 novos), nova checagem
  R08 no `validate_research.py` com smoke negativo (tag inválida, scanner sujo,
  zero rejeições, tag ausente no relatório e token ausente no handoff),
  `python3 tools/validate_plan.py` e `git diff --cached --check`; resultado:
  fluxo completo passa sem acesso indevido, leakage proposital é detectado,
  todos os schemas de predições/métricas validam e o pacote de handoff ao
  custodiante está definido; recursos medidos: dry run em 4,81 s com pico de
  874 MB de RSS, CPU apenas, sem GPU; decisão/limitação: a fixture é separável
  e trivial e não gera evidência científica; a avaliação selada real segue com
  o custodiante em H04/H07/M08 e a versão do protocolo fica congelada pela tag
  interna; commit de71950ee6715362de87a4c792cfd8acdd4cdf2a.

- [x] **G3 — Aprovar pré-registro e firewall.**
  - Objetivo: autorizar ingestão integral sem mudar a pergunta durante o caminho.
  - Entregas: `docs/gates/G3-PREREGISTRO.md` com hashes do protocolo, schemas e
    teste antileakage.
  - Aceite: revisor científico, estatístico e custodiante aprovam; alvo(s)
    confirmatório(s) e política pós-unseal ficam explícitos.
  - Proibições: nenhuma análise real inicia com critério `não verificado`.
  - Dependências: R01–R08.
  - Orçamento: pacote por IA baixa; revisão humana obrigatória.
  Evidência (2026-09-14, executor): decisão humana `GO` registrada em
  2026-09-14 12:10 -04 por Alexandre Zanata, acumulando os três papéis
  (responsável científico, revisor de estatística e custodiante; limitação
  declarada), aprovando o pré-registro assinado (`REGISTRY.md` com 12 artefatos
  e hash de pacote `9411af0c…`), o firewall (R05), o teste antileakage e o dry
  run (R08, tag `dryrun-1.0-f90a4927`); o executor apenas registrou o parecer;
  arquivos `docs/gates/G3-PREREGISTRO.md` (8 critérios, 10 artefatos hashados,
  condições e escopo liberado para H01–H09 sob o pré-registro) e esta linha;
  comandos e testes: `python3 tools/validate_research.py` (checagem G3 agora
  `GO`, com hash do pacote do pré-registro conferido e smoke negativo),
  `python3 tools/validate_plan.py`, `.venv/bin/python -m pytest tests/ -q`
  (75 testes) e `git diff --cached --check`; resultado: ingestão integral
  autorizada conforme dependências, com custodiante independente ainda
  recomendado antes de M08 e nenhuma análise com critério `não verificado`;
  recursos medidos: CPU apenas, sem GPU, sem downloads e sem acesso a
  `data/sealed`; decisão/limitação: revisor único acumula os três papéis;
  qualquer edição nos artefatos congelados invalida o pacote; commit
  a12c35a66f6f7a55fbb81bcdcbd6abf522213349.

### Ingestão e harmonização

- [x] **H01 — Especificar schema canônico de grafo e fixtures.**
  - Objetivo: representar todos os datasets sem apagar diferenças relevantes.
  - Entregas: contrato versionado para nodes, edges, direção, peso, atributos,
    provenance e missingness; fixture sintética dirigida/ponderada.
  - Aceite: tipos, unidades, constraints, multiedges, self-loops, zero/NaN,
    threshold e agregação estão definidos; round-trip da fixture preserva dados.
  - Proibições: não criar campo “comum” que um dataset não possui.
  - Dependências: G3, D02–D09.
  - Orçamento: IA baixa; CPU.
  Evidência (2026-09-14, executor): arquivos `schemas/graph.schema.json`
  (contrato versionado 1.0), `docs/research/GRAPH-CONTRACT.md` (9 seções: nodes,
  edges, grafo/agregados, proveniência, missingness, round-trip, constraints),
  `tools/graph_contract.py` (`validate` e `roundtrip` em stdlib),
  `tests/fixtures/graph-fixture.json` (6 nodes, 8 edges dirigidas e ponderadas,
  com multiedge conservando soma 8, self-loop permitido, peso zero preservado,
  atributo ausente explícito em `missing` e proveniência completa) e
  `tests/test_graph_contract.py` (16 casos); fontes/versões: G3 `GO`, D02–D09,
  PROTOCOLO e ESCOPO, Python 3.12.2 (sem dependência nova), sem download e sem
  GPU; comandos e testes: `python3 tools/graph_contract.py validate` e
  `roundtrip` (OK: round-trip preserva nodes, edges, multiedges, missingness e
  proveniência), `.venv/bin/python -m pytest tests/ -q` (91 passaram em 11,5 s;
  16 novos), nova checagem H01 no `validate_research.py` com smoke negativo
  (seção, token, multiedge ausente, self-loop ausente, peso zero, ID cru),
  `python3 tools/validate_plan.py` e `git diff --cached --check`; resultado:
  tipos, unidades (contagem de sinapses), constraints, multiedges, self-loops,
  zero/NaN, threshold, agregação, proveniência e missingness ficam definidos e
  o round-trip da fixture preserva os dados; falhas reais encontradas e
  corrigidas pelos testes: peso `null` era aceito em grafo ponderado e `null`
  de atributo sem `missing` não era detectado; recursos medidos: CPU apenas,
  suíte em 11,5 s, sem GPU e sem dados brutos; decisão/limitação: atributos de
  região/neurotransmissor entram apenas como chaves opcionais do Experimento B
  e a conversão de cada dataset fica para os adapters H02/H03; commit
  037a61e98750807b056cbebc6e0aa3e156b32178.

- [x] **H02 — Implementar e validar o adapter da fonte.**
  - Objetivo: converter a release-fonte imutável ao schema canônico.
  - Entregas: adapter, testes de schema, amostra dourada, contagens e relatório de
    campos descartados/transformados.
  - Aceite: checksums de entrada/saída, IDs únicos, endpoints válidos, pesos não
    negativos, direção conhecida e totais reconciliados com a fonte oficial ou
    diferença explicada.
  - Proibições: não incluir tipo/posição/região no tensor do trilho A.
  - Dependências: H01, R03.
  - Orçamento: IA baixa; primeiro amostra, depois CPU/RAM conforme D09.
  Evidência (2026-09-14, executor): arquivos `tools/adapter_manc.py`
  (conversão somente-topologia da tabela `bodyId_pre,bodyId_post,weight` para o
  contrato H01, agregação por soma com conservação, IDs opacos, graus derivados
  e recusa de atributos proibidos), `tests/test_adapter_manc.py` (5 casos,
  incluindo integração com a amostra real e conferência do sha256 contra o
  manifesto R03), amostra dourada `tests/fixtures/manc-sample-graph.json`
  (40 nodes/60 edges, sha256 `859f10f0…`) e `artifacts/reports/H02-ADAPTER-FONTE.md`
  + `.json` com métricas e reconciliação; fontes/versões: MANC `manc:v1.2.1`
  (bucket flat v1.0), amostra de D09 com sha256 `4553191e…` conferido, LIT-0074
  para contagens oficiais, contrato H01 e manifesto R03, Python 3.12.2 (stdlib,
  sem dependência nova), sem GPU; comandos e testes: `.venv/bin/python
  tools/adapter_manc.py --connections data/raw/spikes/manc_traced_connections.csv
  --out runs/h02/manc-graph.json --golden tests/fixtures/manc-sample-graph.json
  --metrics artifacts/reports/H02-ADAPTER-FONTE.json` (5.243.574 linhas, 23.188
  nodes, 1 self-loop preservado, 0 multiedges no arquivo real, soma de pesos
  30.698.527 conservada, saída `7a21a947…`), `.venv/bin/python -m pytest tests/
  -q` (96 passaram; 5 novos), nova checagem H02 no `validate_research.py` com
  smoke negativo (token, peso não conservado, sha divergente do manifesto,
  atributo proibido e ID cru), `python3 tools/validate_plan.py` e
  `git diff --cached --check`; resultado: grafo canônico validado, IDs únicos,
  endpoints válidos, pesos não negativos, direção `pre→post` e totais
  reconciliados com explicação (`nodes` ~0,8% acima de ~23.000 publicados e
  pares vs sítios/PSDs em unidades diferentes); recursos medidos: build 13,1 s,
  comando completo 51,4 s, pico de 6.735 MiB (serialização do JSON de 790,7 MB),
  CPU apenas; decisão/limitação: release completo e eventual escrita colunar
  ficam para H08 sem mudar o schema, e a amostra dourada não substitui o grafo
  completo; commit 45239ab2298c2ce876825fad5f306140b0233e4c.

- [x] **H03 — Implementar e validar o adapter público do alvo.**
  - Objetivo: converter apenas o grafo/features permitidos do alvo sem tocar
    labels selados.
  - Entregas: adapter separado, testes de schema, amostra dourada sem labels,
    contagens e relatório de transformações.
  - Aceite: roda com `data/sealed` ausente; schema público não contém nome/tipo,
    crosswalk ou correspondência; mesmas invariantes de H02 passam.
  - Proibições: não abrir adapter/arquivo avaliativo “só para conferir”.
  - Dependências: H01, R05.
  - Orçamento: IA baixa; primeiro amostra, depois CPU/RAM conforme D09.
  Evidência (2026-09-14, executor): arquivos `tools/adapter_mcns.py` (leitura
  exclusiva de `body_pre`, `body_post`, `weight` com schema exigido de três
  colunas, recusa de coluna extra/avaliativa, IDs opacos, graus derivados,
  agregação por soma com conservação e métricas de arquivo completo por
  coluna), `tests/test_adapter_mcns.py` (5 casos, incluindo integração com o
  arquivo público e ausência de menção a anotações), amostra dourada
  `tests/fixtures/mcns-sample-graph.json` (40 nodes/57 edges, sha256
  `4b30c6e3…`) e `artifacts/reports/H03-ADAPTER-ALVO.md` + `.json`; fontes/
  versões: MCNS `male-cns:v1.0` (grafo público baixado por `curl` e registrado
  no manifesto R03 com sha256 `e35da783…` e md5 oficial do GCS `f30e9dcc…`),
  LIT-0023 para contagens publicadas, contrato H01 e firewall R05, Python
  3.12.2 com pyarrow/pandas do lock R02, sem GPU; comandos e testes:
  `.venv/bin/python tools/adapter_mcns.py --weights
  data/raw/target-public/mcns_connectome_weights.feather --out
  runs/h03/mcns-sample-graph.json --golden tests/fixtures/mcns-sample-graph.json
  --metrics artifacts/reports/H03-ADAPTER-ALVO.json` (151.856.684 linhas,
  soma de pesos 311.833.243, peso mínimo 1, 123 self-loops no arquivo completo,
  amostra de 100.000 linhas com 38.442 nodes, 0 multiedges e conservação
  12.750.241), `python3 tools/manifest.py validate --check-files` (4 manifestos
  válidos com o novo arquivo), `.venv/bin/python -m pytest tests/ -q`
  (101 testes; 5 novos), nova checagem H03 no `validate_research.py` com smoke
  negativo (token, peso não conservado, sha divergente do manifesto, atributo
  proibido, menção a arquivo avaliativo e ID cru), `python3
  tools/validate_plan.py` e `git diff --cached --check`; resultado: adapter
  roda sem `data/sealed`, sem anotação e sem qualquer campo avaliativo, com
  schema público contendo apenas topologia e mesmas invariantes de H02
  (checksums, IDs únicos, endpoints válidos, pesos ≥ 0, direção conhecida,
  totais reconciliados/explicados); recursos medidos: 8,2 s de execução, pico
  de 5.240,9 MiB, CPU apenas, 1,05 GB baixado dentro do teto aprovado;
  decisão/limitação: contagem exata de nodes únicos do arquivo completo e a
  flag de self-loops no grafo integral ficam para H08, e o JSON verboso
  continua candidato a escrita incremental/colunar sem mudar o schema; commit
  ce7a6152b49d8b443216f9f5671aeeada2dcf041.

- [x] **H04 — Implementar o adapter selado de avaliação.**
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
  Evidência (2026-09-14, executor): módulo do custodiante
  `tools/sealed_evaluator.py` (validação de label schema e cobertura/crosswalk,
  agregação segura multi-seed com bootstrap agrupado por tipo, open-set,
  calibração, permutação por rotação de tipos na galeria, família Holm de 3,
  registro do hash do label set e escrita de `metrics.json` no schema R06),
  `tests/test_sealed_evaluator.py` (5 casos: métricas válidas com SESOI
  detectado, hash do label set, cobertura incompleta, status inválido e CLI sem
  vazamento de IDs) e `artifacts/reports/H04-AVALIADOR-SELADO.md`; fontes/
  versões: H01 (contrato de grafo), R05 (firewall), R06 (schemas/schemas de
  métricas e predições) e HANDOFF-CUSTODIAN, Python 3.12.2 (stdlib), nenhum
  rótulo real e nenhum acesso a `data/sealed`; comandos e testes:
  `.venv/bin/python -m pytest tests/ -q` (106 passaram; 5 novos),
  `.venv/bin/python tools/sealed_evaluator.py …` (CLI validada em subprocesso,
  sem `q<hex>` em stdout/stderr), nova checagem H04 no `validate_research.py`
  com smoke negativo (token, ID cru e referência à zona selada),
  `python3 tools/validate_plan.py` e `git diff --cached --check`; resultado:
  predições opacas e labels selados geram apenas métricas/contagens agregadas
  no schema R06, com hash do label set registrado e sem exposição de exemplos
  individuais; falha real corrigida nos testes: o teste de permutação usava
  rótulos permutados entre consultas (macro trivialmente 1), substituído por
  rotação dos tipos na galeria; recursos medidos: CPU apenas, suíte em ~40 s,
  sem GPU e sem dados reais; decisão/limitação: papel de custodiante exercido na
  mesma sessão por acumulação procedural (revisor/custodiante independente
  recomendado antes de M08), calibração usa aproximação top-1 e a avaliação
  real única depende de H07/M08; commit 6f632932bfaa08f29f95128893ba96c1b918a745.

- [x] **H05 — Remapear IDs e produzir features topology-only.**
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
  Evidência (2026-09-14, executor): arquivos `tools/opaque_ids.py` (mapeamento
  canônico `n<sha256(dataset|release|body)[:16]>` usado pelos adapters
  H02/H03, refatorados sem mudar as saídas douradas), `tools/topology_features.py`
  (features `in_degree`, `out_degree`, `weighted_in`, `weighted_out`,
  `reciprocity`, `self_loop_weight`; fit z-score só na fonte; transform com
  não-finitos → 0,0 e clipping ±8 por regra fixa; IDs em array paralelo, nunca
  na matriz), `tests/test_topology_features.py` (6 casos: valores exatos,
  permutação de IDs/ordem preserva vetores, normalizador da fonte, política de
  não finitos/clip, matriz sem IDs, atributo proibido falha) e
  `artifacts/reports/H05-FEATURES-TOPO.md`; fontes/versões: contratos H01,
  amostras H02/H03 (MANC 100k arestas e MCNS 100k arestas), Python 3.12.2 com
  numpy do lock R02, sem GPU e sem dados selados; comandos e testes: fit na
  amostra MANC (16.543 nodes, stats `33ed771f…`, 0,68 s) e transform na amostra
  MCNS (38.442 nodes, 0 não-finitos, 7.069 clipados, 0,8 s),
  `.venv/bin/python -m pytest tests/ -q` (112 passaram; 6 novos), nova
  checagem H05 no `validate_research.py` com smoke negativo (token e ID cru),
  `python3 tools/validate_plan.py` e `git diff --cached --check`; resultado:
  permutar IDs e ordem mantém resultados equivalentes, normalizadores ficam
  ajustados somente na fonte, features não carregam label/região/coordenada/nome
  e missing/inf têm regra fixa; falha real corrigida: o relatório de transform
  recalculava somas em laço O(n²) (174,9 s), reduzido a 0,8 s sem mudar valores;
  recursos medidos: CPU apenas, pico 118 MiB no transform, suíte em ~41 s;
  decisão/limitação: features de primeira ordem ficam disponíveis para baselines
  B03/B04, assinaturas mais ricas e o fit do grafo completo ficam para
  B04/H08, e o clipping ±8 deve ser reavaliado em H06/S06 sem alterar o
  pré-registro; commit d589a4c35e4e623435258db6f58ac2610d8b9983.

- [x] **H06 — Fixar semântica de arestas, thresholds e variantes.**
  - Objetivo: separar decisões necessárias de ablações futuras.
  - Entregas: transformador de edges, configuração primária e variantes
    pré-registradas para direção, peso, log de peso, threshold e reciprocidade.
  - Aceite: conservação/agregação de sinapses é testada; escolhas são aplicadas
    igualmente sem estatística do alvo; zero-edge, self-loop e componentes
    isolados têm regra explícita.
  - Proibições: não escolher threshold observando métrica no alvo.
  - Dependências: H02, H03, H05, R07.
  - Orçamento: IA baixa; CPU.
  Evidência (2026-09-14, executor): arquivos `tools/edge_transform.py`
  (transformador com validação de configuração, conservação de peso, regras
  explícitas para peso zero, self-loops e componentes isolados, e registro de
  `config_sha256` na proveniência), `configs/edge-primary.json` (primária do
  pré-registro: dirigida, peso bruto, threshold `keep`, self-loops preservados)
  e `configs/edge-variants.json` (8 variantes pré-registradas: binary, log1p,
  threshold 2/5/10, symmetrized, drop_self_loops),
  `tests/test_edge_transform.py` (15 casos) e `artifacts/reports/H06-EDGES-VARIANTES.md`
  + `.json` com o efeito de cada variante nas amostras de 100k arestas da fonte
  e do alvo; fontes/versões: H02/H03/H05, R07 assinado, contrato H01 (ampliado
  para aceitar peso número finito ≥ 0, necessário para `log1p`, mantendo
  proibição de `NaN`/`Inf`), Python 3.12.2 (stdlib), sem GPU e sem dados
  selados; comandos e testes: aplicação das 8 variantes nas duas amostras
  (primária conserva `peso_entrada = peso_saída`; threshold_2/5/10 na fonte
  descartam 743.775/655.842/564.147 do peso; symmetrized funde 376 pares na
  fonte e 3.354 no alvo conservando o total), `.venv/bin/python -m pytest
  tests/ -q` (128 passaram; 15 novos), nova checagem H06 no
  `validate_research.py` com smoke negativo (token, conservação, variante
  ausente e ID cru), `python3 tools/validate_plan.py` e
  `git diff --cached --check`; resultado: decisões necessárias (primária)
  separadas das ablações (variantes), conservação/agregação testadas, escolhas
  aplicadas igualmente aos dois lados sem estatística do alvo, e regras de
  zero/self-loop/isolados explícitas; recursos medidos: CPU apenas, aplicação
  das variantes em segundos por amostra, sem GPU; decisão/limitação: nenhum
  threshold foi escolhido olhando o alvo (variantes fixas no pré-registro) e a
  ampliação do contrato H01 está documentada em `GRAPH-CONTRACT.md`; commit
  ea63e7faa0f0c1ba4922ef2265360d3cf6129208.

- [x] **H07 — Materializar crosswalk e conjuntos avaliativos sob custódia.**
  - Objetivo: transformar a decisão ontológica em arquivos imutáveis de scoring.
  - Entregas: crosswalk versionado, conjuntos `known`, `unknown`, ambíguo e
    excluído, hashes e relatório de cobertura por dataset.
  - Aceite: duas revisões nos mapeamentos manuais; regra de muitos-para-um
    explícita; labels circulares sinalizados; executor recebe apenas contagens
    agregadas necessárias ao pré-registro.
  - Proibições: lista por node ID não sai da zona selada.
  - Dependências: D08, H04, R07; execução pelo custodiante.
  - Orçamento: IA baixa + dupla revisão humana; sem GPU.
  Evidência (2026-09-14, executor): decisão humana registrada — condição 5
  aplicada e **desfecho de hemilinhagem inconclusivo por circularidade**:
  NBLAST + co-clustering de conectividade não dão independência suficiente para
  um modelo que usa conectividade (excluir only many:1/ambíguos não resolve),
  com registro no `CHANGELOG.md` 2.3; H07 encerrada **sem materialização
  confirmatória** de label set (nada escrito em `data/sealed/`) e **sem claims
  confirmatórios de transferência**. Artefatos e hashes preservados:
  `preregistration/crosswalk-hemilineage.draft.json` (sha256 `2dc94f8a…`,
  35 classes K≥10 nos dois lados, 5 incertos excluídos, proveniência por
  classe), `docs/research/H07-PACKAGE.md` (pacote do custodiante com dupla
  revisão obrigatória e desvio de revisor único), auditorias
  `artifacts/reports/H07-PROVENANCE-AUDIT.{md,json}` e
  `H07-HEMILINEAGE-AUDIT.{md,json}` (fonte PMC12636603; transferência por
  correspondência), `tools/sealed_labels.py` + 6 testes e
  `tools/hemilineage_crosswalk.py` + 4 testes; fontes/versões: D07/LIT-0023,
  PMC12636603 (acesso 2026-09-14), LIT-0015, R07/G3 e manifestos R03, Python
  3.12.2 com pyarrow do lock R02, sem GPU; comandos e testes:
  `.venv/bin/python -m pytest tests/ -q` (145 passaram), `python3
  tools/validate_research.py` (checagem H07 ajustada ao encerramento por
  decisão humana) e `python3 tools/validate_plan.py`; resultado: T0 e
  hemilinhagem formalmente inconclusivos por circularidade, nenhum score do
  alvo consultado, nenhum unseal e nenhuma lista por node ID fora do selado;
  recursos medidos: CPU apenas, sem downloads novos e sem GPU; decisão/
  limitação: revisor único acumulando papéis (segundo revisor indisponível),
  `mancType` não é gold confirmatório e qualquer análise futura com esses
  rótulos é exploratória; H09 segue em modo estritamente exploratório; commit
  <hash>.

- [x] **H08 — Processar releases completas e medir recursos.**
  - Objetivo: gerar snapshots canônicos reproduzíveis no hardware-alvo.
  - Entregas: manifests, hashes, logs estruturados, dados fonte e alvo-público
    processados, perfil de tempo/RAM/disco e procedimento de retomada.
  - Aceite: execução desde raw é idempotente; picos ficam abaixo de 28 GB RAM e
    limite de disco aprovado; contagens batem H02/H03; nenhum label selado aparece
    no snapshot público.
  - Proibições: não corrigir dado bruto in-place nem aceitar OOM parcial.
  - Dependências: H02, H03, H05, H06, G3.
  - Orçamento: IA baixa; CPU; teto de recursos do G3.
  Evidência (2026-09-14, executor): arquivos `tools/snapshot_build.py`
  (snapshots Parquet canônicos `edges.parquet` com `source/target/weight` e
  `nodes.parquet` com `id/degree_in/degree_out`, IDs opacos, `provenance.json`
  e `SHA256SUMS`; idempotente por hash, recusa sobrescrita divergente e valida
  conservação e contagens), `tests/test_snapshot_build.py` (3 casos),
  `artifacts/reports/H08-SNAPSHOTS.md` e `H08-SNAPSHOTS.json`; achado corrigido
  nesta fase: a documentação oficial do MCNS descreve `connectome-weights` como
  segmento-a-segmento (“This is the full connection graph”), então o snapshot
  do MVP passou a usar o grafo **nível-neurônio** (arestas restritas aos
  `bodyId` anotados e agregadas por par, coluna usada só como chave pública);
  medições: fonte 5.243.574 arestas, 23.188 nodes, peso 30.698.527 conservado,
  1 self-loop, 13,8 MB de Parquet, 5,5 s e 1.024 MiB de pico; alvo nível-
  neurônio 26.028.386 arestas mantidas de 151.856.684 (125.828.298 descartadas
  por lado não anotado), 211.577 nodes, peso 125.365.933 conservado, 112
  self-loops, 257,4 MB, 27,3 s e 11.055 MiB de pico; intermediário
  segmento-a-segmento registrado (151.856.684 / 88.384.522 / 311.833.243; 593 s
  e 16.588 MiB); reexecuções `cached` com hashes conferidos; fontes/versões:
  MANC `manc:v1.2.1` e MCNS `male-cns:v1.0` conforme manifestos R03, página
  oficial de download do MCNS (2026-09-14), H01/H06 e G3; comandos e testes:
  `python3 tools/snapshot_build.py manc|mcns …` (ok, `cached` na segunda
  execução), `.venv/bin/python -m pytest tests/ -q` (137 testes; 3 novos), nova
  checagem H08 no `validate_research.py` com smoke negativo (token, contagens,
  labels e picos), `python3 tools/validate_plan.py` e
  `git diff --cached --check`; resultado: snapshots completos reproduzíveis com
  picos bem abaixo de 28 GB, contagens reconciliadas com H02/H03 no nível
  correto e nenhum label selado ou coluna de tipo no snapshot público; recursos
  medidos: CPU apenas, disco 144 GB livres após a fase, sem GPU; decisão/
  limitação: snapshots ficam em `runs/` (fora do Git), a cobertura do alvo
  exclui 125,8M arestas não anotadas e o recorte T0 é decisão da custódia (H07
  segue bloqueada por circularidade e reformulação exigida pelo responsável);
  commit 1bb229c67aa113839b23cf1b7b36b80c1e35abcf.

- [ ] **H09 — Executar auditoria de qualidade e congelar dataset analítico.**
  - Nota (2026-09-14, humano): executar em **modo estritamente exploratório**
    (H07 inconclusiva por circularidade); sem claims confirmatórios de
    transferência e sem materialização de rótulos como confirmação.
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
