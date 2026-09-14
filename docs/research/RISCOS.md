# Registro de riscos

Aberto em 2026-09-14 (C01). **Nenhum risco está mitigado**: mitigação só pode ser
marcada com teste ou artefato verificável (`docs/PROTOCOLO-EXECUCAO.md` §
Decisões; C05). Severidade, detecção detalhada, mitigação e risco residual serão
modelados em C05; aqui apenas se abrem os riscos com IDs estáveis.

Regras:

- ID estável `RSK-nnn`; riscos não são removidos, mudam de status.
- Status permitido: `aberto`, `em detalhamento`, `mitigado com artefato`,
  `aceito com justificativa` ou `refutado`.
- `mitigado com artefato` exige registro do artefato/teste que sustenta a
  mitigação; sem ele o risco permanece `aberto`.
- Responsável é um papel do protocolo.

- **RSK-001 — Atalho por IDs ou ordem de node.**
  - Risco: o modelo memoriza identidade/ordem de neurônios em vez de aprender
    conectividade; desempenho não transfere.
  - Categoria: leakage.
  - Status: aberto.
  - Detecção planejada: teste de invariância a permutação de IDs e remoção de
    features de identidade (R05, M01).
  - Mitigação planejada: entradas sem node ID, embaralhamento, controle nulo.
  - Fase de detalhamento: C05/R05.
  - Responsável: executor; revisão humana em G3.

- **RSK-002 — Confundimento por grau.**
  - Risco: tipos diferem trivialmente em grau in/out; o encoder aprende grau e
    não uma gramática de conectividade.
  - Categoria: estatístico.
  - Status: aberto.
  - Detecção planejada: baseline degree-only e análise pareada por grau (B03,
    M09).
  - Mitigação planejada: negativos pareados por grau, controle de grau nos
    desfechos.
  - Fase de detalhamento: C05/B03.
  - Responsável: executor; revisão de estatística em G5/G6.

- **RSK-003 — Atalho por coordenadas, regiões ou posição.**
  - Risco: features espaciais codificam o tipo anotado e vazam para o trilho
    topologia.
  - Categoria: leakage.
  - Status: aberto.
  - Detecção planejada: auditoria de colunas por trilho (H05, C05).
  - Mitigação planejada: trilho A proíbe posição/região; trilho B separa
    modalidades com baseline próprio.
  - Fase de detalhamento: C05/H05.
  - Responsável: executor; revisão humana em G3/G4.

- **RSK-004 — Rótulo derivado das próprias features.**
  - Risco: tipos foram anotados usando conectividade/morfologia; a avaliação
    vira reconstrução da anotação.
  - Categoria: circularidade.
  - Status: aberto.
  - Detecção planejada: auditoria de proveniência em L04/D08 (CLM-015).
  - Mitigação planejada: decisão humana sobre aceitação; possivelmente excluir
    anotações circulares ou reformular a claim.
  - Fase de detalhamento: L04/D08.
  - Responsável: revisor humano.

- **RSK-005 — Crosswalk circular entre ontologias.**
  - Risco: a correspondência entre tipos foi construída com o mesmo sinal que o
    modelo avalia.
  - Categoria: circularidade.
  - Status: aberto.
  - Detecção planejada: rastrear proveniência e independência do crosswalk
    (D08).
  - Mitigação planejada: crosswalk versionado, selado e aprovado por revisão
    humana; correspondência nunca é feature.
  - Fase de detalhamento: C03/C05/D08.
  - Responsável: revisor humano.

- **RSK-006 — Normalização ou estatística ajustada no alvo.**
  - Risco: transformações aprendidas no alvo introduzem informação do alvo no
    trilho confirmatório.
  - Categoria: leakage.
  - Status: aberto.
  - Detecção planejada: auditoria de onde cada transformação é ajustada (R05,
    H05).
  - Mitigação planejada: ajustar só na fonte; adaptação não supervisionada
    apenas em análise pré-registrada separada.
  - Fase de detalhamento: C05/R05.
  - Responsável: executor; revisão humana em G3.

- **RSK-007 — Amostragem de negativos não pareada.**
  - Risco: negativos fáceis inflam a tarefa auto-supervisionada sem sinal
    transferível.
  - Categoria: método/estatístico.
  - Status: aberto.
  - Detecção planejada: comparação de tarefas com negativos pareados por
    grau/distância (M01, S01).
  - Mitigação planejada: amostragem pareada pré-registrada.
  - Fase de detalhamento: M01/S01.
  - Responsável: executor.

- **RSK-008 — Duplicação de neurônios entre releases.**
  - Risco: o mesmo neurônio reaparece em mais de uma release/conjunto,
    quebrando a separação treino/alvo.
  - Categoria: leakage/dados.
  - Status: aberto.
  - Detecção planejada: checagem de sobreposição de IDs/coordenadas e
    linhagem de releases (D08/H02/H03).
  - Mitigação planejada: proveniência por release; exclusão documentada.
  - Fase de detalhamento: D08/H03.
  - Responsável: executor; revisão humana em G4.

- **RSK-009 — Sexo, estágio, tecido ou cobertura não comparáveis.**
  - Risco: diferenças entre datasets são biológicas/experimentais e não
    metodológicas; a transferência não é interpretável.
  - Categoria: biológico/dados.
  - Status: aberto.
  - Detecção planejada: inventário D01–D10 com fonte primária.
  - Mitigação planejada: escolher par comparável ou declarar estudo entre
    datasets observados; hipótese anatômica explícita.
  - Fase de detalhamento: D08–D10.
  - Responsável: revisor humano.

- **RSK-010 — Artefatos de reconstrução e threshold de arestas.**
  - Risco: critérios de reconstrução e corte de sinapses variam por release e
    criam diferenças espúrias entre fonte e alvo.
  - Categoria: dados/método.
  - Status: aberto.
  - Detecção planejada: documentar thresholds e variantes (H06); sensibilidade.
  - Mitigação planejada: congelar semântica de arestas por trilho; análise de
    sensibilidade pré-registrada.
  - Fase de detalhamento: H06/S06.
  - Responsável: executor; revisão humana em G4.

- **RSK-011 — Tuning após o unseal.**
  - Risco: decisões tomadas depois de ver métricas do alvo transformam o alvo
    em validação.
  - Categoria: protocolo/estatístico.
  - Status: aberto.
  - Detecção planejada: trilha de auditoria de configuração e commits; checklist
    do avaliador (R06/R08).
  - Mitigação planejada: congelamento em `artifacts/frozen/` e avaliação em
    sessão separada; reabertura exige novo alvo.
  - Fase de detalhamento: R06–R08/G3.
  - Responsável: custodiante/avaliador; revisão humana.

- **RSK-012 — Dependência estatística tratada como independência.**
  - Risco: neurônios do mesmo grafo e seeds do mesmo modelo são tratados como
    réplicas independentes, inflando significância.
  - Categoria: estatístico.
  - Status: aberto.
  - Detecção planejada: revisão do plano estatístico (R06).
  - Mitigação planejada: bootstrap agrupado por tipo/grafo; seeds separadas da
    incerteza biológica; sem seleção da melhor seed.
  - Fase de detalhamento: C04/R06.
  - Responsável: revisor de estatística.

- **RSK-013 — Baseline transdutivo apresentado como zero-shot.**
  - Risco: Node2Vec/DeepWalk e espectrais não embutem o alvo no mesmo espaço;
    compará-los como zero-shot direto é inválido.
  - Categoria: método.
  - Status: aberto.
  - Detecção planejada: revisão de adequação de cada baseline (B06/B07/B09).
  - Mitigação planejada: rotular limitações e separar trilhos; sem alinhamento
    com âncoras proibidas.
  - Fase de detalhamento: B06–B09.
  - Responsável: executor; revisão de método em G5.

- **RSK-014 — Licença ou termos de uso impedem treino/republicação.**
  - Risco: release auditada não permite o uso pretendido ou redistribuição de
    artefatos derivados.
  - Categoria: licença.
  - Status: aberto.
  - Detecção planejada: auditoria de licença por candidato (D02–D07).
  - Mitigação planejada: consultar termos na fonte oficial; não baixar nem
    redistribuir sem autorização; buscar alternativa auditada.
  - Fase de detalhamento: D01–D10/G2.
  - Responsável: revisor humano.

- **RSK-015 — Estouro de hardware (VRAM/RAM/disco).**
  - Risco: datasets e modelos excedem 8 GB de VRAM ou 32 GB de RAM e o
    experimento fica irreprodutível no hardware-alvo.
  - Categoria: hardware.
  - Status: aberto.
  - Detecção planejada: spikes D09, smoke M04 e medições em H08.
  - Mitigação planejada: formatos sparse/colunares, sampling, mixed precision
    após teste; tetos de orçamento por fase.
  - Fase de detalhamento: D09/H08/M04.
  - Responsável: executor.

- **RSK-016 — Vazamento por metadados, nomes de arquivo ou logs.**
  - Risco: rótulos do alvo acessíveis ao executor por nomes, ordem de arquivos,
    logs ou estatísticas agregadas não autorizadas.
  - Categoria: leakage/protocolo.
  - Status: aberto.
  - Detecção planejada: teste antileakage do firewall (R05) e revisão de
    diretórios.
  - Mitigação planejada: zonas `data/sealed/` inacessíveis ao executor;
    avaliador separado; nomes neutros.
  - Fase de detalhamento: R05/R06.
  - Responsável: custodiante; revisão humana em G3.
