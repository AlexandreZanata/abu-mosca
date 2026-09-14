# Plano de microfases NEXT — NeuroVerse Engine

## Condição absoluta de entrada

Este plano só pode começar quando `G8` de `docs/PLANO-MICROFASES.md` estiver
`[x]` com evidência verificável. O texto do briefing que manda “assumir
concluído” é uma premissa de desenho, não substitui os artefatos reais. `NX00`
faz essa auditoria e bloqueia o programa se o handoff não existir.

Aplicam-se `docs/PROTOCOLO-EXECUCAO.md` e
`docs/ESCOPO-NEXT-NEUROVERSE.md`. Execute somente a primeira microfase `[ ]`
cujas dependências estejam `[x]`. Gates `NG0–NG11` exigem revisão humana.

Este plano contém 71 microfases e 12 gates. Stages posteriores são condicionais;
não existe obrigação de chegar a Minecraft ou evolução. Uma fase dispensada por
gate recebe `[x]` com evidência `dispensada`, nunca uma aprovação fictícia.

Nota histórica: C00 registrou e validou a versão inicial do NEXT com 69
microfases. O pedido posterior acrescentou explicitamente `NO07` e `NI03`, sem
alterar aquela evidência já concluída. A contagem corrente de 71 deve ser validada
no handoff `NX00` antes da execução do NEXT.

## Orçamento padrão

- **IA econômica:** uma sessão e uma microfase.
- **Revisão humana:** obrigatória em ontologia, mapping, leakage, estatística,
  licença, claims e gates.
- **Smoke:** até 5 minutos, 2 GB VRAM e fixture mínima.
- **Piloto:** até 30 minutos, 4 GB VRAM.
- **Confirmatório:** teto pré-registrado, pico abaixo de 6,5 GB para preservar
  margem na RTX 4060 de 8 GB; exceção exige gate e medição.

Nenhuma fase autoriza publicação, upload, aceite de termos, criação de conta,
compra, contato externo ou download integral de mídia sem aprovação explícita.

## Handoff do CrossConnectome-µ

- [ ] **NX00 — Auditar o encerramento real do plano principal.**
  - Objetivo: confirmar que o NEXT começa sobre evidência e artefatos existentes,
    não sobre uma narrativa de conclusão.
  - Entregas: `docs/next/HANDOFF-AUDIT.md` com estado de G0–G8, commits, releases,
    datasets, encoder, embeddings, métricas, limitações, licenças e checksums;
    validador estrutural do plano NEXT.
  - Aceite: G8 está aprovado; reprodução P02/P03 e auditoria P08 são verificáveis;
    encoder/config/manifests resolvem; claims permitidos e resultados negativos
    estão listados; 71 microfases/12 gates, seis campos, IDs, dependências e links
    do NEXT validam; qualquer ausência bloqueia ou reduz o escopo.
  - Proibições: não marcar fase anterior como concluída retroativamente e não
    executar novo experimento.
  - Dependências: G8 do plano principal.
  - Orçamento: IA econômica; leitura/CPU; sem GPU.

- [ ] **NX01 — Congelar o pacote de entrada e namespace NEXT.**
  - Objetivo: impedir que treinamento comportamental altere silenciosamente o
    encoder que será avaliado.
  - Entregas: manifest imutável de encoder/embeddings/features, política de cache,
    estrutura `next/`, schemas de versão e teste de hash/read-only.
  - Aceite: recomputação opcional reproduz a tolerância do P02; embedding fica
    frozen; qualquer fine-tuning recebe novo ID e trilho exploratório; artefatos
    NEXT não sobrescrevem os do estudo principal.
  - Proibições: não retreinar encoder com comportamento no braço confirmatório.
  - Dependências: NX00.
  - Orçamento: IA econômica; CPU; GPU apenas para verificação já prevista.

- [ ] **NX02 — Fixar fronteiras de claim e provenance dos componentes.**
  - Objetivo: separar estrutura, dinâmica, sensor, motor, corpo, ambiente e
    comportamento antes de construir qualquer cadeia causal.
  - Entregas: `docs/next/CLAIMS-E-PROVENANCE.md`, registro de riscos e instâncias
    do schema `COMPONENT-PROVENANCE` para o handoff.
  - Aceite: usa categorias observed, derived, experimentally_constrained,
    learned, approximated, synthetic e inferred_missing; cada claim tem
    falsificador e componente limitante; “simulação”, “reprodução”, “predição” e
    “emergência” são definidos.
  - Proibições: nenhum componente sem origem e nenhum comportamento de adapter é
    atribuído ao connectoma.
  - Dependências: NX01.
  - Orçamento: IA econômica + revisão científica; sem GPU.

- [ ] **NG0 — Aprovar a entrada no NEXT.**
  - Objetivo: decidir se o handoff sustenta uma pesquisa comportamental nova.
  - Entregas: `docs/gates/NG0-HANDOFF-NEXT.md` com `GO`, `NO-GO` ou `REFORMULAR`.
  - Aceite: responsável científico confirma evidência anterior, licença,
    congelamento e escada de claims; orçamento e papéis do custodiante são
    definidos.
  - Proibições: premissa do briefing não substitui verificação e IA não assina.
  - Dependências: NX00–NX02.
  - Orçamento: pacote por IA econômica; revisão humana obrigatória.

## Stage 0 — validar premissas

- [ ] **NV01 — Definir vocabulário, estimando (*estimand*) e unidade comportamental.**
  - Objetivo: formular o efeito a prever sem tratar comportamento como atributo
    fixo de um neurônio.
  - Entregas: `docs/next/BEHAVIOR-ESTIMAND.md` com intervenção, controle, janela,
    animal, trial, tipo/família, protocolo e target multilabel/hierárquico.
  - Aceite: distingue ocorrência bruta de mudança versus controle; ativação,
    inibição e lesão; indivíduo de trial/frame; efeito de classe de trajetória;
    define missing, unknown, dose e multi-target intervention.
  - Proibições: não usar frame/trial como réplica biológica independente.
  - Dependências: NG0.
  - Orçamento: IA econômica + revisão de método; sem GPU.

- [ ] **NV02 — Pré-especificar e executar revisão sobre Connectome → Behavior.**
  - Objetivo: localizar evidência e trabalhos mais próximos sem cherry-picking.
  - Entregas: protocolo de busca, ledger de papers e síntese de conectividade,
    optogenética/inibição, descending neurons, predição funcional e comportamento.
  - Aceite: queries, bases, datas, inclusão/exclusão e citation chaining são
    repetíveis; cada claim usa fonte primária; resultados favoráveis e negativos
    aparecem; anterioridade do embedding→behavior é testada adversarialmente.
  - Proibições: snippets, blogs e resumos de IA não validam claim central.
  - Dependências: NV01, literatura congelada do plano principal.
  - Orçamento: IA econômica; web; sem GPU; limite de fontes pré-fixado.

- [ ] **NV03 — Revisar engines e modelos incorporados existentes.**
  - Objetivo: evitar reinventar OpenWorm, simuladores neuronais, FlyGym/MuJoCo ou
    trabalhos equivalentes e separar novidade científica de engenharia.
  - Entregas: `research/next/RELATED-ENGINES.md` com interface, espécie, dinâmica,
    body, ambiente, dados, licença, hardware, validação e lacuna de cada projeto.
  - Aceite: fontes oficiais/primárias e versões; identifica componentes a
    reutilizar, incompatibilidades e três claims máximos possíveis; inclui opção
    “engine genérica não é novidade”.
  - Proibições: não instalar ou adaptar engine nesta fase.
  - Dependências: NV02.
  - Orçamento: IA econômica + revisão; web; sem GPU.

- [ ] **NV04 — Descobrir e triar datasets de intervenção comportamental.**
  - Objetivo: criar inventário público de ativação, inibição e manipulação com
    locomoção, turning, grooming, feeding, escape, courtship, flight ou walking.
  - Entregas: ledger e dataset cards preliminares com IDs/tipos, intervenção,
    comportamento, vídeos, indivíduos, repetições, controles, licença e acesso.
  - Aceite: anúncio é distinto de dump; número de frames não substitui animais;
    cada candidato tem fonte oficial ou `não confirmado`; shortlist tem limite
    pré-fixado e justificativa.
  - Proibições: não baixar todos os vídeos e não inferir mapping por nome parecido.
  - Dependências: NV01, NV02.
  - Orçamento: IA econômica; web; amostras/metadados até 500 MB.

- [ ] **NV05 — Auditar mapping intervenção → entidade neural → connectoma.**
  - Objetivo: medir se o target experimental pode ser associado ao embedding sem
    circularidade ou falsa precisão.
  - Entregas: grafo de proveniência, categorias exact type/family/driver/multi-hit,
    confiança, conflitos, cobertura e mapping selado quando avaliativo.
  - Aceite: papers/recursos oficiais confirmam cada ponte; dois revisores em
    mapping manual; uma intervenção multi-hit permanece conjunto; análises por
    confiança e exclusões são pré-definidas.
  - Proibições: driver line, nome de figura ou ID local não vira neuron ID global.
  - Dependências: NV04, NX01, escopo de equivalência do plano principal.
  - Orçamento: IA econômica + dupla revisão humana; sem GPU.

- [ ] **NV06 — Escolher ontologia, split, amostra e orçamento.**
  - Objetivo: selecionar o comportamento mais testável, não o mais vistoso.
  - Entregas: comparação de targets, classes/contagens, matched controls,
    missingness, estudo/família/driver groups, power/precision e RAM/disco reais.
  - Aceite: escolhe split externo mais forte possível; proíbe random por
    trial/frame; estima incerteza no nível correto; mede amostra; define fallback
    se locomoção não for defensável; mídia integral tem budget separado.
  - Proibições: não escolher classes após ver desempenho de modelo.
  - Dependências: NV04, NV05.
  - Orçamento: IA econômica; CPU; amostras até 2 GB; sem GPU.

- [ ] **NV07 — Congelar exatamente um NEXT EXPERIMENT.**
  - Objetivo: preencher e assinar o template com dataset, target e análise reais.
  - Entregas: `preregistration/NEXT-EXPERIMENT.md`, analysis plan, firewall do
    estudo/dataset confirmatório e árvore de decisões condicionais.
  - Aceite: fixa releases/hashes, input, covariáveis comuns, baselines, modelos,
    split, SESOI, métricas, CIs, calibração, trials, seeds, recursos, exclusões,
    falsificação e critério Stage 2; segundo estudo fica selado quando existe.
  - Proibições: não listar dois experimentos “principais” e não acessar resultados
    confirmatórios antes do freeze.
  - Dependências: NV01–NV06.
  - Orçamento: IA econômica para minuta; revisão estatística/científica e
    custodiante obrigatórios.

- [ ] **NG1 — Aprovar premissas e o único próximo experimento.**
  - Objetivo: decidir se existe experimento Connectome → Behavior defensável.
  - Entregas: `docs/gates/NG1-NEXT-EXPERIMENT.md` e hashes do pré-registro.
  - Aceite: dataset/licença, mapping, target, controles, indivíduos, split,
    power, leakage, novelty e orçamento passam; `NO-GO` gera feasibility report.
  - Proibições: sem dataset adequado, não substituir por dado sintético e chamar
    de validação comportamental.
  - Dependências: NV01–NV07.
  - Orçamento: pacote por IA econômica; painel humano.

## Stage 1 — Connectome → Behavior

- [ ] **NB01 — Fixar schema canônico de intervenção e comportamento.**
  - Objetivo: representar datasets sem apagar protocolo, hierarquia e dependência.
  - Entregas: schema para study, animal, trial, intervenção, target neural,
    controle, dose/tempo, comportamento, janela, mapping e provenance; fixtures.
  - Aceite: multi-target/multilabel, repeated measures, unknown, missing e
    confidence têm semântica; constraints e round-trip passam; nenhuma coluna
    de alta cardinalidade entra automaticamente como feature.
  - Proibições: não achatar animal/trial/frame como linhas independentes.
  - Dependências: NG1, NV01.
  - Orçamento: IA econômica; CPU.

- [ ] **NB02 — Ingerir o dataset de desenvolvimento com proveniência.**
  - Objetivo: converter release e controles ao schema canônico de modo idempotente.
  - Entregas: manifests/checksums, adapter, amostra dourada, QC e perfil de
    RAM/disco/tempo.
  - Aceite: totais reconciliam fonte; exclusões são codificadas; indivíduo,
    vídeo/trial e lote permanecem; raw é imutável; rerun gera mesmo hash.
  - Proibições: não corrigir label manualmente sem registro e não ingerir mídia
    integral se o protocolo usa labels publicados.
  - Dependências: NB01, R03/R04 do plano principal, NG1.
  - Orçamento: IA econômica; CPU; teto do NV06.

- [ ] **NB03 — Preparar o dataset confirmatório selado.**
  - Objetivo: preservar um estudo/dataset externo para avaliação única.
  - Entregas: adapter do custodiante, manifest/hash selado, schema público sem
    labels, teste antileakage e contrato de métricas agregadas.
  - Aceite: executor desenvolve sem montar labels; estudo/animal/family groups não
    aparecem em cache proibido; tentativa sentinela falha; unseal tem chave e
    incidente idempotente.
  - Proibições: se só houver um dataset, não fabricar confirmação; registrar
    Stage 1 como piloto.
  - Dependências: NB01, NV07; execução pelo custodiante.
  - Orçamento: IA econômica em sessão separada; CPU.

- [ ] **NB04 — Juntar embeddings congelados com mappings auditados.**
  - Objetivo: produzir features estruturais por intervenção sem falsa precisão.
  - Entregas: agregadores para single-type/multi-hit, confidence/missing masks,
    manifests de embedding e testes de invariância a ID/ordem.
  - Aceite: hash do encoder é NX01; nenhum gradiente; conjuntos multi-hit usam
    regra pré-registrada; coverage e perdas são relatadas; mapping confirmatório
    permanece selado.
  - Proibições: não escolher um único neurônio conveniente em intervenção ampla.
  - Dependências: NB02, NB03, NV05, NX01.
  - Orçamento: IA econômica; CPU; RAM abaixo do teto NV06.

- [ ] **NB05 — Materializar splits agrupados e provar ausência de leakage.**
  - Objetivo: manter parentesco experimental e neural fora de folds opostos.
  - Entregas: manifests de leave-study, leave-driver/family e leave-cell-type-out
    elegíveis, temporal quando válido, além de scanner de sobreposição.
  - Aceite: animal, vídeo, trial, driver, tipo/família e duplicatas obedecem ao
    grupo; hashes congelados; prevalências/coverage são reportadas sem usar
    resultado; random split só aparece como diagnóstico rotulado fraco.
  - Proibições: frames/trials relacionados nunca cruzam treino e teste.
  - Dependências: NB02, NB04, NV06, NV07.
  - Orçamento: IA econômica; CPU.

- [ ] **NB06 — Construir targets control-adjusted e ontologia final.**
  - Objetivo: estimar direção/tamanho de efeito em vez de mera ocorrência bruta.
  - Entregas: transformador de controles, janelas, labels hierárquicos/multilabel,
    incerteza e análise bruta secundária.
  - Aceite: matching de controles é pré-fixado; baseline temporal/animal é
    preservado; target não usa informação pós-split; classes raras/missing têm
    regra; exemplos manuais reproduzem cálculo.
  - Proibições: ausência de controle não vira efeito zero e ativação/inibição não
    são fundidas sem sinal explícito.
  - Dependências: NB01, NB02, NB05, NV01.
  - Orçamento: IA econômica + revisão estatística; CPU.

- [ ] **NB07 — Implementar evaluator, CIs e calibração.**
  - Objetivo: usar uma única implementação para todos os modelos.
  - Entregas: macro-F1, balanced accuracy, AUROC/AUPR, Brier, ECE, métricas de
    efeito contínuo quando aplicáveis, CIs/permutação agrupados e testes manuais.
  - Aceite: degeneração, multilabel, missing, group bootstrap e diferenças
    pareadas passam; métrica primária/SESOI são os de NV07; output selado não
    revela linhas individuais.
  - Proibições: não tratar trials como amostras independentes no CI.
  - Dependências: NB05, NB06, plano estatístico NV07.
  - Orçamento: IA econômica; CPU.

- [ ] **NB08 — Executar baselines sem embedding.**
  - Objetivo: estabelecer chance, prevalência e sinal trivial/protocolar.
  - Entregas: random, majority, protocol-only, degree-only e handcrafted graph
    statistics sob splits/configs comuns, com todas as seeds e falhas.
  - Aceite: covariáveis não estruturais são idênticas entre braços; IDs de
    estudo/driver não viram atalhos; melhor baseline é escolhido somente no
    desenvolvimento; controles de label permutation passam.
  - Proibições: não enfraquecer handcrafted para favorecer embedding.
  - Dependências: NB04–NB07.
  - Orçamento: IA econômica; CPU.

- [ ] **NB09 — Treinar predictors com embedding e congelar o pacote.**
  - Objetivo: comparar regressão logística/multilabel, MLP pequeno e comparadores
    tabulares sob o budget pré-registrado.
  - Entregas: embedding-only e embedding+handcrafted, configs, trials, seeds,
    curvas e pacote read-only para o alvo.
  - Aceite: encoder continua frozen; regressão é modelo primário; MLP abaixo de
    2 GB; RF/boosting recebem mesmas features/splits; seleção usa somente
    desenvolvimento; todos os trials ficam no ledger.
  - Proibições: sem tuning no estudo/dataset confirmatório e sem melhor seed.
  - Dependências: NB08, NV07.
  - Orçamento: IA econômica; CPU; GPU piloto até 2 GB para MLP.

- [ ] **NB10 — Avaliar cegamente e executar robustez pré-registrada.**
  - Objetivo: testar generalização para grupos e estudo/dataset mantidos fora.
  - Entregas: predições assinadas, unseal único, métricas agregadas, diferenças
    versus melhor baseline, mapping-confidence sensitivity e cross-vs-within gap.
  - Aceite: hashes batem NB09; nenhuma atualização; CIs e multiplicidade seguem
    NB07; todas as seeds são agregadas; se não houver confirmação externa, output
    é explicitamente piloto.
  - Proibições: não mudar ontologia, split, SESOI ou exclusões após unseal.
  - Dependências: NB03, NB07–NB09; execução final pelo custodiante.
  - Orçamento: IA econômica em sessão separada; CPU.

- [ ] **NB11 — Redigir resultado Connectome → Behavior.**
  - Objetivo: decidir se embeddings acrescentam informação comportamental
    utilizável para a próxima etapa.
  - Entregas: `artifacts/reports/CONNECTOME-BEHAVIOR.md`, figures/tables geradas,
    claims, custos, limitações e relatório negativo completo quando aplicável.
  - Aceite: todos os modelos/seeds/grupos aparecem; efeito e CI contra melhor
    baseline; calibração, mapping, indivíduos e replicação são explícitos;
    nenhuma afirmação de dinâmica/causalidade excede o desenho.
  - Proibições: bom within-dataset não substitui teste externo.
  - Dependências: NB10.
  - Orçamento: IA econômica + revisão científica/estatística; sem nova GPU.

- [ ] **NG2 — Decidir se a evidência libera NeuroVerse Core.**
  - Objetivo: aplicar o critério do NEXT EXPERIMENT sem mover a trave.
  - Entregas: `docs/gates/NG2-CONNECTOME-BEHAVIOR.md` com claim autorizado.
  - Aceite: `GO` exige SESOI, CI, split forte, calibração e replicação; piloto sem
    replicação ou `NO-GO` não abre o Core neste programa e preserva o resultado.
    Um sandbox puramente técnico exigiria autorização e plano separados.
  - Proibições: engine visual não é solução para resultado científico nulo.
  - Dependências: NB01–NB11.
  - Orçamento: pacote por IA econômica; painel humano obrigatório.

## Stage 2 — NeuroVerse Core

- [ ] **NC01 — Fixar arquitetura mínima, interfaces e ADRs.**
  - Objetivo: definir uma engine species/environment/runtime-agnostic sem
    generalização prematura.
  - Entregas: ADRs e contratos para `Organism`, `NervousSystem`, `SensorySystem`,
    `MotorSystem`, `Body`, `InternalState`, `Environment` e `step(dt)`, além de
    provenance obrigatório por componente.
  - Aceite: dependências apontam core → interfaces, adapters → core; nenhum
    import de Minecraft/MuJoCo/espécie entra no core; tempo, unidades, shapes,
    reset, seed, erro e ciclo de vida são definidos; alternativas são registradas.
  - Proibições: não criar módulo sem uso no organismo sintético e não codificar
    comportamento em interface.
  - Dependências: NG2 aprovado segundo o critério biológico.
  - Orçamento: IA econômica + revisão arquitetural; sem GPU.

- [ ] **NC02 — Escolher e medir representação compacta do sistema neural.**
  - Objetivo: validar arrays sparse/vectorized e limites reais na máquina-alvo.
  - Entregas: spike COO/CSR e, quando útil, event-driven/chunked; benchmark para
    300/10k/100k/150k/200k nodes e 1M/10M/50M edges; relatório CPU/GPU.
  - Aceite: mede alocação crua e pico real, step/s, conversões, int32/int64,
    float16/32 e custo de buffers; não densifica; caminho seguro para 8 GB é
    escolhido com critério e fallback CPU.
  - Proibições: estimativa teórica não substitui medição e OOM não é sucesso.
  - Dependências: NC01, hardware reproduzido do plano principal.
  - Orçamento: IA econômica; CPU até 24 GB RAM; GPU smoke/piloto, sem 50M com
    autograd integral.

- [ ] **NC03 — Implementar Runtime 0 abstrato e contrato `brain.step(dt)`.**
  - Objetivo: validar estado, conectividade, reset, seed e intervenção sem alegar
    dinâmica biológica.
  - Entregas: runtime linear/abstrato em arrays, CPU-first, golden tests e adapter
    para grafo sintético.
  - Aceite: mesmo input/config/seed reproduz; direção e peso têm semântica;
    batch/individual isolation passa; runtime troca sem mudar organism API;
    provenance é `synthetic/approximated`.
  - Proibições: não chamar ativação abstrata de spike ou potencial de membrana.
  - Dependências: NC01, NC02.
  - Orçamento: IA econômica; CPU; GPU smoke opcional.

- [ ] **NC04 — Implementar Runtime 1 rate-based.**
  - Objetivo: adicionar dinâmica contínua mínima com parâmetros explícitos.
  - Entregas: update rate-based vectorized, estabilidade numérica, masks sparse,
    CPU/GPU equivalence e config versionada.
  - Aceite: testes analíticos de sistemas pequenos, sensibilidade a `dt`, limites
    de estado, determinismo/tolerância e benchmark passam; parâmetros têm origem
    synthetic ou experimentally_constrained.
  - Proibições: não ajustar parâmetros para golden trajectory escondida.
  - Dependências: NC03.
  - Orçamento: IA econômica; GPU smoke abaixo de 2 GB.

- [ ] **NC05 — Construir Organism 0 e mundo headless.**
  - Objetivo: integrar 8 sensores, 32 interneurônios e 8 motores artificiais com
    body e arena mínimos.
  - Entregas: organismo sintético, sensores/motores determinísticos, corpo
    cinemático, ambiente 2D headless e duas golden tasks sem dado biológico.
  - Aceite: Runtime 0 e 1 podem ser trocados; observação→sensor→brain→motor→body
    fecha o loop; componentes têm provenance; reset e múltiplos organismos não
    compartilham estado.
  - Proibições: golden task não conta como comportamento emergente/biológico.
  - Dependências: NC03, NC04.
  - Orçamento: IA econômica; CPU.

- [ ] **NC06 — Implementar configs, CLI, manifests e níveis de logging.**
  - Objetivo: executar qualquer experimento sem parâmetro oculto ou log explosivo.
  - Entregas: schema YAML/JSON, `neuroverse run <experiment>`, run manifest e
    logging `summary`, `sampled`, `event`, `full-debug` para sensor, neural, motor,
    position/velocity/energy, body, ambiente, behavior labels e eventos; benchmark
    de Parquet, HDF5, Zarr e NumPy mmap conforme o padrão de acesso.
  - Aceite: schema rejeita desconhecido; config efetiva, model/connectome/engine
    versions, hashes, seed e hardware são gravados; estimador de bytes bloqueia
    log acima do budget; formatos eficientes são comparados e round-trip passa.
  - Proibições: `full-debug` não é default e config não executa código arbitrário.
  - Dependências: NC01, NC05, template RUN-MANIFEST.
  - Orçamento: IA econômica; CPU; arquivos smoke abaixo de 100 MB.

- [ ] **NC07 — Implementar validadores e hooks de intervenção genéricos.**
  - Objetivo: separar visualização de métricas e preparar causal tests futuros.
  - Entregas: interfaces BehaviorMetrics, NeuralMetrics e TrajectoryMetrics;
    hooks activate/inhibit/lesion com timeline e sham em fixture sintética.
  - Aceite: speed, turn frequency, path entropy, distância, latency e estados têm
    testes manuais; métricas não alteram simulação; intervenções são reversíveis
    quando especificado e aparecem no log/provenance.
  - Proibições: sem semântica biológica para amplitude/dose nesta fase.
  - Dependências: NC05, NC06.
  - Orçamento: IA econômica; CPU.

- [ ] **NC08 — Executar gate técnico reproduzível do Core.**
  - Objetivo: provar determinismo, modularidade e recursos antes de organismo real.
  - Entregas: clean-environment build, testes unitários/integração/property/chaos,
    CPU↔GPU, benchmarks de NC02, golden runs e relatório arquitetural.
  - Aceite: configs reproduzem dentro da tolerância; runtime/ambiente/organismo são
    substituíveis; zero estado oculto/global; RAM/VRAM/disco/steps/s documentados;
    scanner de claims/provenance passa.
  - Proibições: demo visual não substitui gate headless.
  - Dependências: NC01–NC07.
  - Orçamento: IA econômica; CPU/GPU piloto total pré-fixado.

- [ ] **NG3 — Aprovar NeuroVerse Core.**
  - Objetivo: decidir se a engine mínima é confiável para um adapter biológico.
  - Entregas: `docs/gates/NG3-CORE.md` com versão de contrato congelada.
  - Aceite: testes, determinismo, provenance, logs, intervenção e hardware passam;
    escopo C. elegans é aprovado sem claim comportamental antecipado.
  - Proibições: correção de software não equivale a validação biológica.
  - Dependências: NC01–NC08.
  - Orçamento: pacote por IA econômica; revisão humana técnica/científica.

## Stage 3 — C. elegans

- [ ] **NE01 — Auditar dados, projetos e licença de C. elegans.**
  - Objetivo: selecionar um benchmark existente e evitar reimplementar trabalho
    já disponível.
  - Entregas: dataset/project cards para connectoma, dinâmica, body, ambiente,
    comportamento e intervenções; análise build-vs-adapt.
  - Aceite: versões, indivíduos, mappings, licenças, formatos, validação e hardware
    são confirmados em fontes oficiais/primárias; incompatibilidades e lacunas
    permanecem explícitas.
  - Proibições: “connectoma conhecido” não implica parâmetros completos.
  - Dependências: NG3, NV03.
  - Orçamento: IA econômica; web; amostras até 500 MB; sem GPU.

- [ ] **NE02 — Escolher um comportamento e pré-registrar reprodução.**
  - Objetivo: limitar C. elegans a um benchmark de arquitetura, não nova plataforma.
  - Entregas: experiment card com forward/backward/turning/chemotaxis/avoidance
    escolhido por evidência, dataset, baseline publicado, tolerância e controles.
  - Aceite: exatamente um primário; parâmetros de ajuste e teste separados;
    sensory/motor/body provenance definida; critério de não equivalência e
    falha estão assinados.
  - Proibições: não selecionar comportamento depois de rodar todos.
  - Dependências: NE01, NC08.
  - Orçamento: IA econômica + revisão humana; sem GPU.

- [ ] **NE03 — Implementar C. elegans adapter e runtime mapeado.**
  - Objetivo: converter o sistema escolhido ao contrato Core preservando origem.
  - Entregas: loader/schema, neural mapping, Runtime 1, tests de
    contagem/unidade e flags de aproximação. Runtime 2 permanece para o Stage 4.
  - Aceite: dados reconciliam fonte; observado/inferido não se mistura; runtime
    mantém `step(dt)`; parâmetros ausentes não recebem valor “padrão biológico”.
  - Proibições: não preencher conexões/pesos silenciosamente.
  - Dependências: NE02, NC03, NC04.
  - Orçamento: IA econômica; CPU/GPU smoke abaixo de 2 GB.

- [ ] **NE04 — Implementar sensores, motor e body mínimos.**
  - Objetivo: conectar o benchmark sem programar sua resposta esperada.
  - Entregas: adapters e body model reutilizados quando licenciados, mappings com
    provenance e null adapters de igual dimensionalidade.
  - Aceite: cada regra aponta a experimento, aproximação ou source code; high-level
    motor é declarado; null/scrambled sensor e motor detectam comportamento
    inserido; nenhum target label entra na lógica.
  - Proibições: não codificar “se estímulo então virar”.
  - Dependências: NE03, NC05–NC07.
  - Orçamento: IA econômica; CPU.

- [ ] **NE05 — Executar reprodução e intervenções held-out.**
  - Objetivo: comparar trajetória/comportamento com referência sob protocolo
    congelado.
  - Entregas: runs/seeds, controles, intervention effects, métricas e comparação
    com baseline publicado.
  - Aceite: ajuste usa somente desenvolvimento; held-out não é tocado; múltiplas
    seeds; direction/speed/turn ou target escolhido e intervenção têm intervalos;
    null adapters/graphs degradam conforme esperado ou a falha é analisada.
  - Proibições: não calibrar no teste nem usar visualização como score.
  - Dependências: NE02–NE04.
  - Orçamento: IA econômica; CPU/GPU piloto sob pré-registro.

- [ ] **NE06 — Redigir relatório de paridade e portabilidade.**
  - Objetivo: decidir se o adapter valida a arquitetura sem inflar contribuição.
  - Entregas: `artifacts/reports/C-ELEGANS.md`, resultados, custos, componentes
    reutilizados, divergências e claim máximo.
  - Aceite: comportamento, intervenção, controls, seeds, provenance e diferenças
    do trabalho original aparecem; reproduction e novelty são separadas.
  - Proibições: não apresentar reprodução como descoberta principal.
  - Dependências: NE05.
  - Orçamento: IA econômica + revisão; sem nova GPU.

- [ ] **NG4 — Aprovar o adapter C. elegans.**
  - Objetivo: decidir se a engine aceita um organismo real sem regras ocultas.
  - Entregas: `docs/gates/NG4-C-ELEGANS.md`.
  - Aceite: reprodução/tolerância, intervention control, provenance, recursos e
    portabilidade passam; se falhar, Drosophila fica bloqueada até correção ou
    reformulação justificada.
  - Proibições: não pular organismo pequeno só porque a mosca é objetivo final.
  - Dependências: NE01–NE06.
  - Orçamento: pacote por IA econômica; revisão humana.

## Stage 4 — Drosophila subset

- [ ] **ND01 — Selecionar um circuito e comportamento do Stage 1.**
  - Objetivo: construir a menor ponte entre resultado offline e dinâmica.
  - Entregas: experiment card com circuito, intervenção, comportamento, nodes,
    edges, coverage, controles, peso/estado desconhecido e SESOI.
  - Aceite: escolha segue NG2/NB11, não estética; circuito cabe no hardware;
    referência experimental tem held-out; comportamento é um só primário.
  - Proibições: não começar pela Drosophila inteira ou voo.
  - Dependências: NG4, NG2, NB11.
  - Orçamento: IA econômica + revisão científica; sem GPU.

- [ ] **ND02 — Extrair subgrafo com provenance e controles estruturais.**
  - Objetivo: representar circuito observado sem completar lacunas ocultamente.
  - Entregas: subgraph manifest, regras boundary/top-k/threshold, flags
    `observed`, `confidence`, missing edges e grafos random/degree-preserving.
  - Aceite: contagens/checksums reconciliam; edge inferida fica em braço separado;
    boundary e fraction preservada são mensuradas; IDs não viram parâmetros.
  - Proibições: conexão prevista nunca substitui observed silenciosamente.
  - Dependências: ND01, NX01, NC02.
  - Orçamento: IA econômica; CPU; RAM abaixo de 16 GB.

- [ ] **ND03 — Definir sensory e motor adapters mínimos.**
  - Objetivo: ligar estímulo e saída high-level sem codificar o target.
  - Entregas: mappings experimentais/aproximados, null/scrambled adapters,
    descending-neuron aggregation e comandos forward/turn/stop quando aplicáveis.
  - Aceite: origem e confiança por mapping; mesma dimensionalidade nos controles;
    output motor não contém nome do comportamento; low-level fica fora do Stage.
  - Proibições: regra explícita equivalente ao resultado invalida o experimento.
  - Dependências: ND01, ND02, NC01, NC07.
  - Orçamento: IA econômica + revisão científica; CPU.

- [ ] **ND04 — Comparar Runtime 0/1 e Runtime 2 LIF.**
  - Objetivo: medir se fidelidade dinâmica altera o efeito sem multiplicar graus
    de liberdade injustamente.
  - Entregas: LIF vectorized plugável, parâmetros/provenance, budgets pareados,
    stability/dt tests e comparação com runtimes simples.
  - Aceite: interface `step(dt)` idêntica; LIF só abre com parâmetros/priors
    declarados; seleção não usa held-out; custo e sensibilidade aparecem.
  - Proibições: mais parâmetros não podem receber mais tuning para vencer.
  - Dependências: ND02, ND03, NC03, NC04.
  - Orçamento: IA econômica; GPU piloto abaixo de 4 GB.

- [ ] **ND05 — Executar intervenção headless no circuito.**
  - Objetivo: prever direção/latência do efeito com held-out experimental.
  - Entregas: baseline, activate/inhibit ou lesion escolhida, sham, null graphs,
    seeds, metrics e blind evaluation.
  - Aceite: protocolo imutável; efeito não usado no fit; original supera ou é
    comparado honestamente a random/degree-preserving; adapters controls passam;
    runtime differences têm CIs.
  - Proibições: não ajustar sensor/motor após ver comportamento held-out.
  - Dependências: ND02–ND04, experiment card ND01.
  - Orçamento: IA econômica; GPU confirmatória abaixo de 4 GB.

- [ ] **ND06 — Quantificar limites e relatar o subset.**
  - Objetivo: decidir se o circuito sustenta incorporação mais completa.
  - Entregas: `artifacts/reports/DROSOPHILA-SUBSET.md`, claim/provenance graph,
    recursos, sensitivity e resultado negativo quando aplicável.
  - Aceite: deixa claro o que veio de connectoma, runtime, adapters e fit; reporta
    held-out, nulls, seeds, efeito e incerteza; não extrapola ao animal inteiro.
  - Proibições: movimento plausível sem comparação não é sucesso.
  - Dependências: ND05.
  - Orçamento: IA econômica + revisão; sem nova GPU.

- [ ] **NG5 — Aprovar Drosophila subset.**
  - Objetivo: decidir se um circuito merece fechar o loop incorporado.
  - Entregas: `docs/gates/NG5-DROSOPHILA-SUBSET.md`.
  - Aceite: held-out effect, controls estruturais/adapters, runtime, provenance e
    recursos passam; claim autorizado permanece no nível do circuito.
  - Proibições: resultado nulo não é contornado aumentando o organismo.
  - Dependências: ND01–ND06.
  - Orçamento: pacote por IA econômica; painel humano.

## Stage 5 — Drosophila embodied

- [ ] **NO01 — Implementar body 2D e motor high-level.**
  - Objetivo: introduzir walking/turning/stopping com física mínima mensurável.
  - Entregas: body cinemático/dinâmico simples, comandos normalizados, limites,
    unidades, null motor e testes analíticos.
  - Aceite: mesma sequência motora gera trajetória esperada; body não contém
    goal-seeking; high-level é rotulado approximation; caminho low-level é apenas
    interface futura.
  - Proibições: sem voo, pernas detalhadas ou MuJoCo antes deste gate.
  - Dependências: NG5, NC05.
  - Orçamento: IA econômica; CPU.

- [ ] **NO02 — Implementar sensory adapters mínimos com provenance.**
  - Objetivo: codificar somente estímulos necessários ao comportamento primário.
  - Entregas: vision/olfaction/touch/temperature subset aplicável, metadata de
    origem, noise model, null/scrambled sensors e testes de transformação.
  - Aceite: mapping experimental/approximation/synthetic explícito; sensor não vê
    estado futuro, target ou ação ótima; dimensões/normalização/latência são fixas.
  - Proibições: observação não inclui distância/ângulo privilegiado salvo braço
    explicitamente sintético.
  - Dependências: NO01, ND03, NC01.
  - Orçamento: IA econômica; CPU.

- [ ] **NO03 — Modelar internal state sem biologizar abstrações.**
  - Objetivo: introduzir apenas estado necessário e testar sua contribuição.
  - Entregas: energia/hunger/fatigue/arousal individualmente aprovados ou estado
    mínimo nulo, provenance, dinâmica e ablação.
  - Aceite: cada estado tem source ou é `synthetic`; não carrega resposta ótima;
    initial distribution/updates são config; modelo sem estado é baseline.
  - Proibições: nome biológico não transforma variável inventada em medição.
  - Dependências: NO01, NO02, NX02.
  - Orçamento: IA econômica + revisão científica; CPU.

- [ ] **NO04 — Fechar o loop em arena headless.**
  - Objetivo: executar sensor→neural→motor→body→world com perturbações novas.
  - Entregas: arena/configs, food/obstacle/looming subset pré-aprovado, batches de
    seeds, reset/multi-organism isolation e run manifests.
  - Aceite: layouts train/test separados; zero regra por cenário; deterministic
    replay/tolerance; runtime e adapters são substituíveis; logs respeitam budget.
  - Proibições: visualização não participa do update nem da avaliação.
  - Dependências: NO01–NO03, NC06, ND04.
  - Orçamento: IA econômica; CPU/GPU piloto até 6 GB.

- [ ] **NO05 — Validar comportamento, trajetória e origem do efeito.**
  - Objetivo: comparar mundo incorporado com referência e controles de adapter.
  - Entregas: speed, turns, latency, distance, path entropy, intervention effects,
    adapter/null graph ablations e comparação experimental possível.
  - Aceite: múltiplas seeds/layouts; CIs agrupados; nenhuma métrica escolhida pela
    animação; comportamento chamado emergente só se passa seis condições do
    escopo; discrepâncias são atribuídas com cautela.
  - Proibições: sem analogia experimental, usar “comportamento da engine”.
  - Dependências: NO04, NC07, ND06.
  - Orçamento: IA econômica; CPU para análise.

- [ ] **NO06 — Medir fidelidade estrutural versus custo.**
  - Objetivo: estimar qual fração do grafo preserva o comportamento observado.
  - Entregas: grafo completo quando couber, neuron-to-neuron agregado, thresholds,
    top-k, subgraphs, chunks, sparse/event-driven e curvas qualidade/custo.
  - Aceite: uma variável por ablação; mesmos adapters/runtime/seeds; edge fraction,
    RAM/VRAM/steps/s e efeito com CI; 50M-edge path só roda após spike seguro.
  - Proibições: configuração OOM não é descartada sem registro e velocidade não
    substitui fidelidade.
  - Dependências: NO04, NO05, NC02.
  - Orçamento: IA econômica; successive-halving; teto de 6,5 GB VRAM e 28 GB RAM.

- [ ] **NO07 — Abrir ou dispensar motor low-level e body biomecânico.**
  - Objetivo: comparar comandos high-level com joint torques/leg phases/muscle
    activation somente depois do body 2D validado.
  - Entregas: auditoria e adapter opcional para biomecânica existente, incluindo
    MuJoCo/FlyGym quando apropriado e licenciado; mapping motor, provenance,
    baseline high-level, métricas e custo; ou relatório `dispensado`.
  - Aceite: parâmetros/body têm fontes; mesma tarefa e circuito; ganho mínimo e
    tolerância são pré-fixados; low-level não recebe trajetória-alvo; headless e
    contrato Core permanecem; custo cabe na máquina.
  - Proibições: detalhe de pernas não abre por apelo visual nem substitui falha do
    high-level; nenhuma dependência é instalada antes da auditoria.
  - Dependências: NO05, NO06, NV03.
  - Orçamento: IA econômica; auditoria sem GPU, piloto opcional até 6,5 GB;
    dispensar é válido.

- [ ] **NG6 — Aprovar Drosophila embodied.**
  - Objetivo: decidir se o loop fechado é válido para intervenção causal.
  - Entregas: `docs/gates/NG6-DROSOPHILA-EMBODIED.md`.
  - Aceite: held-out layouts, validators, adapter/null controls, provenance,
    structural fidelity e custo passam; claim máximo é assinado.
  - Proibições: uma demo bonita não libera Stage 6.
  - Dependências: NO01–NO07.
  - Orçamento: pacote por IA econômica; painel humano.

## Stage 6 — intervention validation

- [ ] **NI01 — Fixar semântica de activate, inhibit e lesion.**
  - Objetivo: tornar intervenção simulada explícita, testável e comparável.
  - Entregas: API temporal com IDs/conjuntos opacos, intensidade, início,
    duração, ramp, reversibilidade, sham e provenance; testes por runtime.
  - Aceite: operação tem efeito definido em Runtime 0/1/2; intervenção não muda
    conectividade salvo lesion explícita; baseline retorna ao estado esperado;
    eventos são logados e reproduzidos.
  - Proibições: “ativar” não recebe semântica experimental sem tradução NI02.
  - Dependências: NG6, NC07, ND04.
  - Orçamento: IA econômica; CPU/GPU smoke.

- [ ] **NI02 — Traduzir protocolos experimentais para intervenções simuladas.**
  - Objetivo: mapear técnica, alvo, dose e tempo com incerteza declarada.
  - Entregas: protocol cards, mapping experimental→runtime, faixas plausíveis,
    sham/negative controls e parâmetros que permanecem não identificados.
  - Aceite: cada tradução cita fonte; optogenética/inibição/ablação não são
    tratadas como equivalentes; multi-hit e dose têm sensitivity pré-fixada;
    parâmetros calibrados usam dados distintos do teste.
  - Proibições: não ajustar amplitude para obter o comportamento esperado.
  - Dependências: NI01, NV02, NB01–NB06.
  - Orçamento: IA econômica + revisão experimental; sem GPU.

- [ ] **NI03 — Abrir ou dispensar Runtime 3 intermediário.**
  - Objetivo: testar Izhikevich ou dinâmica equivalente somente se Runtime 2
    demonstrou limitação relevante e parâmetros puderem ser restringidos.
  - Entregas: gate técnico interno, implementação plugável opcional, provenance,
    stability/dt tests, budget pareado e comparação source-only com Runtime 1/2;
    ou relatório formal `dispensado`.
  - Aceite: `step(dt)` não muda; hipótese e ganho mínimo são pré-fixados; número
    de parâmetros/trials é pareado; parâmetros têm fonte ou prior explícito;
    held-out experimental não seleciona runtime.
  - Proibições: complexidade dinâmica não abre por realismo aparente; runtime
    biofísico detalhado permanece fora deste plano.
  - Dependências: NG6, ND04, NI02.
  - Orçamento: IA econômica; GPU piloto abaixo de 4 GB; dispensar é válido.

- [ ] **NI04 — Executar matriz limitada de intervenções held-out.**
  - Objetivo: testar previsão causal em intervenções não usadas no fit.
  - Entregas: configs congeladas, baseline/sham, activate/inhibit/lesion elegíveis,
    seeds e run manifests com budget comum.
  - Aceite: matriz não excede pré-registro; ordem/seeds são fixas; nenhum tuning
    por intervenção; falhas/instabilidade permanecem; dados experimentais de
    teste ficam selados até predições assinadas.
  - Proibições: não executar só intervenções conhecidas por funcionar.
  - Dependências: NI02, NI03, NO04–NO06.
  - Orçamento: IA econômica; GPU confirmatória até 6,5 GB, successive-halving.

- [ ] **NI05 — Comparar efeitos simulados e experimentais.**
  - Objetivo: avaliar direção, tamanho, latência e dose-response com controles.
  - Entregas: signed effects, equivalence bounds, calibration, sham/null graph,
    CIs agrupados e análise por qualidade de mapping.
  - Aceite: evaluator congelado; indivíduos/estudos são unidade correta; acerto de
    sinal e magnitude ficam separados; multiplicidade e missing seguem plano;
    output não expõe labels selados por exemplo.
  - Proibições: correlação agregada não vira causalidade individual.
  - Dependências: NI04, NB07; execução final pelo custodiante.
  - Orçamento: IA econômica em sessão separada; CPU.

- [ ] **NI06 — Replicar e redigir benchmark de intervenção.**
  - Objetivo: exigir mais de um estudo/condição antes de claim forte.
  - Entregas: reprodução independente, análise cross-study, relatório
    `artifacts/reports/INTERVENTIONS.md`, custos e claim-evidence map.
  - Aceite: segundo estudo ou condição independente pré-definida; todas as
    intervenções/seeds; diferença contra baselines; adapter/runtime limitations;
    sem replicação, conclusão permanece piloto.
  - Proibições: repetir seeds não substitui repetir animais/estudos.
  - Dependências: NI05.
  - Orçamento: IA econômica + revisão independente; GPU conforme uma réplica.

- [ ] **NG7 — Aprovar validação por intervenção.**
  - Objetivo: decidir se há correspondência causal suficiente para tentar
    transferência entre animais.
  - Entregas: `docs/gates/NG7-INTERVENTIONS.md`.
  - Aceite: held-out, sham/null, signed effect, replicação, mapping, provenance e
    custo passam; falha bloqueia Stage 7 e preserva o resultado.
  - Proibições: predição correlacional do Stage 1 não substitui este gate.
  - Dependências: NI01–NI06.
  - Orçamento: pacote por IA econômica; painel humano científico/estatístico.

## Stage 7 — Cross-animal transfer

- [ ] **NT01 — Selecionar e selar animal/connectoma B.**
  - Objetivo: reservar um teste realmente novo de connectoma e comportamento.
  - Entregas: dataset cards, releases/hashes, comparabilidade, crosswalk sob
    custódia, behavior protocol e firewall B.
  - Aceite: B não participou de treino, arquitetura, runtime/adapters, thresholds
    ou seleção; indivíduo/estudo é independente; mapping e labels ficam selados;
    power/coverage e fallback são aprovados.
  - Proibições: não reutilizar alvo já revelado como confirmação nova.
  - Dependências: NG7, inventários NV04–NV06, handoff CrossConnectome.
  - Orçamento: IA econômica + revisão/custodiante; sem GPU.

- [ ] **NT02 — Congelar matching A→B e propagação de incerteza.**
  - Objetivo: associar tipos/famílias sem usar comportamento de B.
  - Entregas: embeddings/matcher frozen, candidate sets, confidence/open-set,
    coverage e controles degree/handcrafted.
  - Aceite: zero label comportamental de B; weights/hash do matcher são os do
    plano principal ou protocolo novo inteiramente source-only; ambiguous/missing
    não recebem match forçado; uncertainty chega ao predictor.
  - Proibições: não escolher correspondência que melhora behavior score.
  - Dependências: NT01, NX01, equivalência validada no plano principal.
  - Orçamento: IA econômica; CPU/GPU inferência abaixo de 4 GB.

- [ ] **NT03 — Congelar predictor, runtime e adapters antes de B.**
  - Objetivo: preparar todas as predições cross-animal sem adaptação oculta.
  - Entregas: configs/hashes de Behavior Decoder, NeuralRuntime, sensory/motor,
    body, thresholds, seeds e analysis plan; dry run sintético.
  - Aceite: zero optimizer/fit em B; normalizadores source-only; todos os ramos e
    exclusões são condicionais pré-fixados; scanner antileakage passa.
  - Proibições: não recalibrar dinâmica ou motor com trajetória de B.
  - Dependências: NT02, NI06, NV07.
  - Orçamento: IA econômica; CPU/GPU smoke.

- [ ] **NT04 — Predizer B cegamente e avaliar uma única vez.**
  - Objetivo: executar o alvo científico cross-animal do NeuroVerse.
  - Entregas: predições/intervention effects assinados, run manifests, unseal,
    métricas agregadas e within-A vs cross-B gap.
  - Aceite: hashes batem NT03; zero update; macro/effect/calibration, coverage,
    mapping strata e baselines completos; todas as seeds; incidente de reexecução
    mantém mesma chave/config.
  - Proibições: não inspecionar exemplos de B antes do veredito congelado.
  - Dependências: NT01–NT03; avaliação pelo custodiante.
  - Orçamento: IA econômica em sessão separada; GPU inferência até 6,5 GB.

- [ ] **NT05 — Auditar, reproduzir e redigir cross-animal.**
  - Objetivo: determinar se a transferência resiste a revisão independente.
  - Entregas: relatório `artifacts/reports/CROSS-ANIMAL-BEHAVIOR.md`, reprodução,
    leakage audit, atualização de literatura/novidade e claim máximo.
  - Aceite: resultado negativo/inconclusivo permanece; n biológico e limites de
    B explícitos; análise pós-unseal rotulada exploratória; revisor independente
    tenta refutar mapping, stats e adapters.
  - Proibições: um A/B não autoriza universalidade por espécie.
  - Dependências: NT04.
  - Orçamento: IA econômica + revisão científica independente; GPU de uma réplica.

- [ ] **NG8 — Decidir a alegação cross-animal.**
  - Objetivo: aprovar paper/resultados antes de testbeds artificiais.
  - Entregas: `docs/gates/NG8-CROSS-ANIMAL.md` com opção paper positivo,
    negativo, benchmark ou encerramento.
  - Aceite: novelty, validade, replicação, efeito, incerteza, licença e claims são
    julgados; Stages artificiais não alteram este resultado.
  - Proibições: Minecraft não pode recuperar um gate biológico reprovado.
  - Dependências: NT01–NT05.
  - Orçamento: pacote por IA econômica; painel humano.

## Stage 8 — Minecraft Adapter

- [ ] **NM01 — Auditar dependência e congelar contrato Minecraft.**
  - Objetivo: definir um EnvironmentAdapter artificial sem acoplar o core.
  - Entregas: versão/licença/API, arquitetura de processo, observações, ações,
    clock, determinismo, segurança, budget e threat/confound model.
  - Aceite: organismo só vê sensor/internal/motor; core não importa Minecraft;
    rede/conta/servidor e termos têm aprovação antes de uso; claim é `testbed`.
  - Proibições: não instalar, autenticar ou baixar nesta fase sem autorização.
  - Dependências: NG8 e NG3; publicação biológica pode encerrar antes deste Stage.
  - Orçamento: IA econômica; web; sem GPU.

- [ ] **NM02 — Implementar bridge mínimo e testes de contrato.**
  - Objetivo: transportar observações e comandos sem lógica comportamental.
  - Entregas: MinecraftWorld adapter, sensor representation reduzida, ações
    high-level, reset/seed/timestamps e mock server determinístico.
  - Aceite: contract tests sem jogo real; mensagens versionadas; latência e
    desconexão tratadas; adapter não conhece target/reward interno do organismo.
  - Proibições: não colocar pathfinding ou policy ótima na bridge.
  - Dependências: NM01, NC01, NC06.
  - Orçamento: IA econômica; CPU; mock primeiro.

- [ ] **NM03 — Executar cenários artificiais pré-registrados.**
  - Objetivo: testar portabilidade em comida/arena, obstáculos e ameaça simples.
  - Entregas: três configs no máximo, layouts held-out, seeds, metrics, replay e
    comparação com arena headless.
  - Aceite: mesmos organism/runtime weights; sem ajuste por cenário; success,
    trajectory, latency e throughput com CIs; domain shift e falhas reportados.
  - Proibições: animação não entra como métrica nem valida biologia.
  - Dependências: NM02, NO04–NO05.
  - Orçamento: IA econômica; cliente local; teto medido no NM01.

- [ ] **NM04 — Auditar acoplamento e relatar o testbed.**
  - Objetivo: confirmar que Minecraft permaneceu um adapter substituível.
  - Entregas: dependency test, adapter ablations, performance report, vídeo
    opcional como demonstração e linguagem de claim revisada.
  - Aceite: remover Minecraft não altera core/organism API; comportamento vem dos
    mesmos componentes; limitações de física/sensores aparecem; artifacts são
    reproduzíveis sem vídeo.
  - Proibições: não chamar sucesso no jogo de comportamento animal validado.
  - Dependências: NM03.
  - Orçamento: IA econômica + revisão; sem treino novo.

- [ ] **NG9 — Aprovar Minecraft apenas como testbed.**
  - Objetivo: decidir se o adapter é tecnicamente útil e cientificamente rotulado.
  - Entregas: `docs/gates/NG9-MINECRAFT.md`.
  - Aceite: desacoplamento, determinismo, recursos, termos e claim passam;
    problemas do adapter não alteram resultados NG2–NG8.
  - Proibições: gate não concede validação biológica.
  - Dependências: NM01–NM04.
  - Orçamento: pacote por IA econômica; revisão humana.

## Stage 9 — Synthetic organisms

- [ ] **NS01 — Definir schema de variantes e mutações rastreáveis.**
  - Objetivo: distinguir connectoma observado de alteração artificial/inferida.
  - Entregas: operations manifest para delete/add/rewire/weight, lineage, seeds,
    `observed`/`confidence`, invariantes e restore do original.
  - Aceite: operação é determinística e reversível quando possível; hash pai/filho;
    inferred_missing nunca sobrescreve observed; mesma escala/budget entre braços.
  - Proibições: variante sintética não é chamada de animal mutante real.
  - Dependências: NG9 ou NG8 se Minecraft for dispensado, ND02.
  - Orçamento: IA econômica; CPU.

- [ ] **NS02 — Executar real versus random e degree-preserving controls.**
  - Objetivo: testar se organização superior oferece inductive bias além de
    tamanho e graus.
  - Entregas: ensembles random, degree-preserving e original, parâmetros
    aprendíveis pareados, tasks/seeds/budget comuns e sanity checks de grafos.
  - Aceite: número de nodes/edges e distribuição de grau preservados conforme
    braço; múltiplos grafos por seed; selection não favorece original; performance
    e sample efficiency com CIs.
  - Proibições: um único shuffle não representa a nulidade.
  - Dependências: NS01, NO04–NO06.
  - Orçamento: IA econômica; successive-halving sob teto de 6,5 GB.

- [ ] **NS03 — Executar deleção, rewiring e estrutura inferida.**
  - Objetivo: medir quais propriedades/frações preservam o comportamento.
  - Entregas: edge deletion 10/25/50%, circuit deletion, random/degree rewiring,
    top-k/threshold e inferred edges em braço separado.
  - Aceite: matriz pré-registrada, mesmas seeds/adapters/runtime; curvas monotônicas
    não são presumidas; missing structure tem confidence; múltiplas comparações
    controladas.
  - Proibições: não selecionar mutação pós-hoc pelo efeito mais interessante.
  - Dependências: NS02, NO06.
  - Orçamento: IA econômica; matriz reduzida por successive-halving.

- [ ] **NS04 — Analisar emergência, robustez e redigir benchmark.**
  - Objetivo: interpretar variantes sem antropomorfismo ou claim biológico falso.
  - Entregas: real-vs-null effects, degradation curves, graph metrics, seis testes
    de emergência, custos e relatório separado.
  - Aceite: comportamento “emergente” não tem regra/sensor/motor equivalente,
    aparece em seeds, liga-se a dinâmica e é preferencialmente comparável a
    experimento; caso contrário recebe descrição operacional neutra.
  - Proibições: vídeo inesperado não é evidência suficiente.
  - Dependências: NS02, NS03.
  - Orçamento: IA econômica + revisão; CPU.

- [ ] **NG10 — Aprovar estudo de organismos sintéticos.**
  - Objetivo: decidir se os nulls/ablações sustentam uma exploração evolutiva.
  - Entregas: `docs/gates/NG10-SYNTHETIC.md`.
  - Aceite: controles pareados, CIs, multiplicidade, provenance, recursos e claims
    passam; resultado nulo é aceito e pode encerrar o programa.
  - Proibições: Stage 10 não abre só porque é tecnicamente possível.
  - Dependências: NS01–NS04.
  - Orçamento: pacote por IA econômica; painel humano.

## Stage 10 — Artificial evolution

- [ ] **NA01 — Formular e pré-registrar evolução estritamente artificial.**
  - Objetivo: definir pergunta, fitness, mutações, população e controles sem
    analogia biológica indevida.
  - Entregas: experiment card, claim máximo, budgets, stopping, seeds, priors
    original/random/degree-preserving e análise estatística.
  - Aceite: exatamente uma hipótese exploratória; fitness não codifica solução;
    budgets e parâmetros aprendíveis pareados; termos “seleção artificial na
    engine” usados consistentemente.
  - Proibições: não afirmar recapitulação de evolução natural.
  - Dependências: NG10.
  - Orçamento: IA econômica + revisão humana; sem GPU.

- [ ] **NA02 — Implementar lineage, mutação, seleção e replay.**
  - Objetivo: tornar cada geração auditável e reproduzível.
  - Entregas: population manifest, parent hashes, mutations, fitness components,
    RNG streams, checkpoints idempotentes e replay de lineage.
  - Aceite: mesma seed reproduz população; resume não duplica geração; lineage
    não perde indivíduos falhos; fitness e compute por candidato são iguais entre
    priors; testes pequenos passam.
  - Proibições: não descartar runs falhas ou alterar fitness durante uma run.
  - Dependências: NA01, NS01, NC06.
  - Orçamento: IA econômica; CPU/GPU smoke.

- [ ] **NA03 — Executar piloto e controles sob budget fixo.**
  - Objetivo: comparar adaptação sem explosão de compute.
  - Entregas: múltiplas seeds, curva best/median, sample efficiency, diversidade,
    estabilidade, custo e early-stop para cada prior.
  - Aceite: mesmo número de avaliações/steps; todas as seeds; intervalos e
    diferenças pareadas; no improvement/instabilidade são resultados; nenhum
    aumento de budget após olhar vencedor.
  - Proibições: melhor indivíduo isolado não define conclusão.
  - Dependências: NA02.
  - Orçamento: IA econômica; piloto total aprovado no NG10, pico ≤6,5 GB VRAM.

- [ ] **NA04 — Reproduzir e comunicar o estudo exploratório.**
  - Objetivo: fechar a linha artificial separada da evidência biológica.
  - Entregas: reprodução independente, relatório, artifacts/configs, limitações,
    energia/custo aproximado e comparação com NG2–NG8 sem fundir claims.
  - Aceite: resultado replica ou falha é mantida; fitness arbitrariness,
    anthropomorphism e generalização são discutidos; todos os dados sintéticos
    têm lineage/hashes.
  - Proibições: não usar Stage 10 para reforçar retrospectivamente claim animal.
  - Dependências: NA03.
  - Orçamento: IA econômica + revisão independente; uma réplica do piloto.

- [ ] **NG11 — Encerrar o programa NEXT.**
  - Objetivo: registrar desfecho de cada Stage e preservar artefatos/claims.
  - Entregas: `docs/gates/NG11-ENCERRAMENTO-NEUROVERSE.md`, índice de releases,
    datasets, runs, custos, publicações, negativos e questões abertas.
  - Aceite: NG0–NG10 reconciliados; resultados biológicos, engenharia, Minecraft,
    synthetic e evolution permanecem separados; licenças/preservação passam;
    prompt NEXT é aposentado.
  - Proibições: encerramento não exige chegar ao Stage 10 nem resultado positivo.
  - Dependências: NA01–NA04 ou encerramento formal anterior por gate.
  - Orçamento: IA econômica + aprovação humana final.

## Evidência por microfase

Ao concluir, inserir abaixo do item sem mudar seu contrato:

```text
Evidência (AAAA-MM-DD, executor): arquivos; fontes/releases; comandos/testes;
resultado; RAM/VRAM/disco/tempo; decisão/limitação; commit <hash>.
```

Gates usam `docs/templates/DECISAO-GATE.md`; datasets comportamentais usam
`docs/templates/BEHAVIOR-DATASET-CARD.md`; simulações usam
`docs/templates/SIMULATION-EXPERIMENT-CARD.md`. Não antecipe evidência.
