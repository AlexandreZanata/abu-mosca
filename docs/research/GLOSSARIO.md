# Glossário operacional

Aberto em 2026-09-14 (C01). Definições **provisórias para uso interno**, ancoradas
no contrato do projeto (`docs/ESCOPO-E-HIPOTESES.md` e
`docs/PROTOCOLO-EXECUCAO.md`). Não substituem revisão humana nem auditoria de
ontologias. Termo com status `aberto até ...` não foi confirmado em fonte
primária e não pode ser usado como fato científico.

Convenções:

- ID estável `GLO-nn`. Revisões futuras acrescentam versão/nota; a definição
  anterior não é reescrita silenciosamente.
- Status: `definido provisoriamente`, `aberto até <fase>` ou
  `revisado por humano em <gate>`.
- Responsável é um papel do protocolo (planejador, executor, revisor humano).

- **GLO-01 — Fonte**
  - Definição operacional: connectoma cujo grafo pode ser usado no treino
    auto-supervisionado; seus rótulos só podem ser usados pelos baselines/probes
    definidos e pela avaliação interna da fonte.
  - Âncora: `docs/ESCOPO-E-HIPOTESES.md` § Definições operacionais.
  - Status: definido provisoriamente.
  - Responsável: planejador; revisão humana em G0.
  - Aberto: qual connectoma exercerá o papel e se a licença permite treino
    (D01–D10, G2).

- **GLO-02 — Alvo**
  - Definição operacional: connectoma nunca usado para ajustar pesos,
    arquitetura, hiperparâmetros, limiares, normalizadores ou escolhas
    analíticas. O grafo público pode ser entrada de inferência; rótulos,
    crosswalk avaliativo e estatísticas globais ficam fora do ajuste.
  - Âncora: `docs/ESCOPO-E-HIPOTESES.md` § Definições operacionais.
  - Status: definido provisoriamente.
  - Responsável: planejador; revisão humana em G2.

- **GLO-03 — Zero-shot cross-connectome**
  - Definição operacional: pesos, transformações, limiares e probe congelados
    antes de tocar o alvo; nenhuma atualização com rótulo do alvo. Se houver
    ajuste com rótulo do alvo, o resultado não pode ser chamado de zero-shot.
  - Âncora: `docs/ESCOPO-E-HIPOTESES.md` § Definições operacionais;
    `docs/PROTOCOLO-EXECUCAO.md` § Firewall do connectoma-alvo.
  - Status: definido provisoriamente.
  - Responsável: planejador; congelamento avaliado em G3.

- **GLO-04 — Tipo (rótulo de tipo anotado)**
  - Definição operacional: rótulo de classe atribuído por uma ontologia/release
    específicos de um dataset. O projeto não presume que “tipo” seja verdade
    natural, livre de ruído ou idêntico entre datasets; comparações usam
    crosswalk versionado e aprovado por revisão humana.
  - Âncora: `docs/ESCOPO-E-HIPOTESES.md` § Pergunta científica e § Definições
    operacionais (“Mesmo tipo”).
  - Status: aberto até C03/D08 (granularidade e regras de harmonização).
  - Responsável: revisor humano de ontologia; executor prepara opções.

- **GLO-05 — Supertype**
  - Definição operacional: agrupamento mais amplo que “tipo”, usado por algumas
    ontologias de connectoma. O projeto ainda não adota lista, definição ou
    hierarquia; nenhum supertype será usado como alvo ou feature sem fonte
    primária da release e decisão humana.
  - Âncora: `docs/PLANO-MICROFASES.md` C03; `docs/ESCOPO-E-HIPOTESES.md`
    § Candidatos a auditar.
  - Status: aberto até L02/D08/C03.
  - Responsável: revisor humano; executor registra evidências.

- **GLO-06 — Homologia**
  - Definição operacional: relação de correspondência evolutiva entre células ou
    tipos de espécimes diferentes. O projeto não afirma homologia entre
    candidatos; quando a comparação exigir essa noção, ela terá granularidade
    explícita, fonte primária e revisão humana.
  - Âncora: `docs/PLANO-MICROFASES.md` C03 e D08; `docs/ESCOPO-E-HIPOTESES.md`
    § Definições operacionais.
  - Status: aberto até L02–L04/C03.
  - Responsável: revisor humano.

- **GLO-07 — Função**
  - Definição operacional: propriedade fisiológica ou de circuito de um
    neurônio. **Não é desfecho deste projeto**: nenhum resultado de
    conectividade será apresentado como função. O alvo primário é transferência
    de rótulo de tipo harmonizado.
  - Âncora: `docs/ESCOPO-E-HIPOTESES.md` § Pergunta científica e § Fora do
    escopo inicial.
  - Status: fora do escopo (declarado).
  - Responsável: planejador.

- **GLO-08 — Embedding**
  - Definição operacional: vetor latente produzido pelo encoder indutivo a
    partir de entrada permitida no trilho, sem tabela de parâmetros por node ID;
    usado para recuperação, classificação, calibração e open-set. Distância no
    embedding é construto operacional, não medida biológica.
  - Âncora: `docs/ESCOPO-E-HIPOTESES.md` § Tarefas auto-supervisionadas e
    § Trilhos de informação.
  - Status: definido provisoriamente; dimensão/arquitetura em M02–M05.
  - Responsável: executor; revisão de método em G5.

- **GLO-09 — Leakage**
  - Definição operacional: uso, em treino/seleção/limiar, de informação que não
    estará disponível na avaliação do alvo ou que codifica o próprio alvo;
    inclui atalhos triviais (IDs, ordem, grau, posição) e vazamento procedural.
  - Âncora: `docs/PROTOCOLO-EXECUCAO.md` § Firewall e § Normalização;
    `docs/PLANO-MICROFASES.md` C05.
  - Status: aberto até C05 (modelagem e testes).
  - Responsável: executor; revisão humana em G3.

- **GLO-10 — Circularidade**
  - Definição operacional: situação em que o rótulo avaliativo foi produzido
    usando informação que o modelo também usa como entrada (por exemplo, tipo
    anotado com base em conectividade), inflando o desempenho sem demonstrar
    transferência. Exige auditoria da proveniência da anotação e decisão humana.
  - Âncora: `docs/PROTOCOLO-EXECUCAO.md` § Decisões que exigem revisão humana;
    `docs/PLANO-MICROFASES.md` D08/L04.
  - Status: aberto até D08/L04/C03.
  - Responsável: revisor humano.

- **GLO-11 — Réplica técnica**
  - Definição operacional: repetição da mesma análise/treino sobre o mesmo dado,
    variando seed, configuração ou hardware. Não aumenta o número de indivíduos
    biológicos; incerteza por seed é reportada separadamente da incerteza
    biológica.
  - Âncora: `docs/PROTOCOLO-EXECUCAO.md` § Regras estatísticas;
    `docs/ESCOPO-E-HIPOTESES.md` § Definições operacionais.
  - Status: definido provisoriamente; plano estatístico em R06.
  - Responsável: executor; revisão humana em G3.

- **GLO-12 — Réplica biológica**
  - Definição operacional: novo espécime/connectoma independente. No desenho
    inicial há no máximo um connectoma-fonte e um alvo; portanto **não há
    replicação biológica** e nenhuma conclusão populacional além dos datasets
    observados pode ser emitida.
  - Âncora: `docs/ESCOPO-E-HIPOTESES.md` § Definições operacionais;
    `docs/PROTOCOLO-EXECUCAO.md` § Regras estatísticas.
  - Status: definido provisoriamente.
  - Responsável: planejador; revisão humana em G0/G6.

- **GLO-13 — Mesmo tipo (rótulo harmonizado)**
  - Definição operacional: igualdade após crosswalk versionado e rastreável
    entre ontologias, limitada ao nível taxonômico que a evidência sustenta.
    Crosswalk avaliativo é selado e só o custodiante o lê.
  - Âncora: `docs/ESCOPO-E-HIPOTESES.md` § Definições operacionais;
    `docs/PROTOCOLO-EXECUCAO.md` § Decisões que exigem revisão humana.
  - Status: aberto até C03/D08; aprovação humana obrigatória.
  - Responsável: revisor humano.

- **GLO-14 — Open-set**
  - Definição operacional: consulta do alvo cujo tipo harmonizado não existe na
    galeria da fonte; o sistema deve poder rejeitá-la como desconhecida. Classes
    conhecidas e open-set são definidas no protocolo congelado, não após olhar
    erros individuais.
  - Âncora: `docs/ESCOPO-E-HIPOTESES.md` § Definições operacionais;
    `docs/PROTOCOLO-EXECUCAO.md` § Normalização e uso permitido do alvo.
  - Status: definido provisoriamente; métricas em B02/S08.
  - Responsável: executor; revisão humana em G3.
