# Escopo NEXT — NeuroVerse Engine

## Condição de entrada

Este programa começa **depois** do encerramento validado do CrossConnectome-µ.
Para fins de planejamento, assume-se que o gate `G8` do plano principal foi
aprovado e que existem encoder, embeddings, manifests, métricas, limitações,
licenças e artefatos reproduzíveis. Durante a execução real, `NX00–NX02` devem
verificar essas evidências. Se elas não existirem, o NEXT fica bloqueado; a IA
não pode apenas “assumir concluído” porque isso aparece neste texto.

O NEXT é um novo programa científico. Resultados, labels ou datasets já usados
na primeira pesquisa não se tornam automaticamente evidência confirmatória para
uma hipótese comportamental nova.

## Perguntas separadas

### Pergunta científica imediata

> Representações estruturais congeladas do CrossConnectome-µ acrescentam poder
> preditivo para o efeito comportamental de intervenções neuronais, além de grau,
> estatísticas artesanais e metadados do protocolo, em tipos/famílias ou estudos
> mantidos fora do treino?

### Pergunta de engenharia posterior

> Uma interface comum consegue executar runtimes neuronais, corpos e ambientes
> diferentes de forma determinística, mensurável e sem esconder a origem de cada
> aproximação?

### Perguntas biológicas posteriores

- Um circuito incorporado reproduz direções de efeito observadas após ativação,
  inibição ou lesão?
- Quanto o resultado muda com dinâmica neuronal, fidelidade do grafo, sensor,
  motor e corpo?
- Um modelo congelado em animal/connectoma A prediz o resultado de intervenção
  em animal/connectoma B realmente intocado?

Essas perguntas têm hipóteses, dados e gates próprios. Uma engine correta como
software não valida um modelo biológico; uma animação plausível não valida
nenhum dos dois.

## Crítica científica incorporada ao plano

1. **Embedding estático não é dinâmica.** Ele resume posição estrutural; não
   fornece potencial de membrana, pesos efetivos, sinais excitatórios/inibitórios
   completos, neuromodulação, plasticidade ou estado fisiológico.
2. **Comportamento não pertence apenas ao neurônio.** Depende de intervenção,
   dose, duração, genética, sexo, idade, estado interno, corpo, arena, estímulo,
   protocolo de anotação e indivíduo.
3. **Driver line não é neuron ID.** Uma manipulação pode atingir vários tipos,
   variar entre animais ou ser mapeada apenas por expressão; correspondência com
   FlyWire/BANC/MANC precisa de evidência e incerteza.
4. **Trial não é réplica independente quando compartilha animal, vídeo, driver,
   tipo ou estudo.** Random split por frame/trial provavelmente vaza identidade.
5. **Rótulo bruto não mede efeito causal.** Quando houver controles adequados, o
   target preferido é a mudança induzida em relação ao controle, com incerteza,
   e não apenas “o vídeo contém walking”.
6. **Adapters podem programar a resposta.** Sensor, motor, recompensa, estado
   interno e body model recebem proveniência explícita; comportamento inserido
   manualmente não pode ser chamado emergente.
7. **Mais detalhe não implica mais verdade.** LIF ou Izhikevich sem parâmetros
   identificáveis pode acrescentar graus de liberdade e piorar a falsificabilidade.
8. **C. elegans e Drosophila não são réplicas entre si.** O primeiro valida a
   arquitetura da engine em outra escala; não confirma a hipótese principal da
   mosca.
9. **Minecraft é testbed artificial.** Sucesso nele mede compatibilidade e
   robustez de controle sob um domínio artificial, nunca fidelidade biológica.
10. **Evolução artificial é outro estudo.** Fitness e mutação definidos pela
    engine não representam automaticamente evolução natural.

## Unidade observacional e target recomendados

A linha básica do dataset analítico será uma combinação rastreável de:

- intervenção;
- entidade neural alvo, com tipo/família e incerteza de mapping;
- indivíduo e repetição;
- protocolo/estudo/laboratório;
- condição e controle;
- janela temporal;
- comportamento observado e método de anotação.

Quando vários neurônios são manipulados juntos, a unidade não será falsamente
duplicada por neurônio. O experimento deve usar target multilabel ou hierárquico
quando comportamentos coexistirem. Ativação e inibição serão trilhos separados,
a menos que o modelo represente explicitamente o sinal da intervenção.

## Informação permitida no primeiro experimento

- Encoder e embedding CrossConnectome-µ congelados antes desta pesquisa.
- Grau e estatísticas estruturais calculadas de modo idêntico ao projeto anterior.
- Metadados do protocolo que estejam disponíveis em inferência e sejam usados
  igualmente por todos os modelos.
- Indicador e confiança do mapping entre intervenção e tipo/família.

Informação proibida inclui IDs de paper/driver codificados como categorias de alta
cardinalidade, nome do comportamento dentro do nome da linha, identidade do
estudo quando ela determina diretamente a classe, frames do mesmo vídeo nos dois
lados do split e qualquer embedding ajustado com labels comportamentais antes da
comparação congelada.

## O único próximo experimento provisório

O Stage 0 deve preencher o dataset e a ontologia com evidência. Até o gate `NG1`,
nenhum nome de dataset é apresentado como escolhido.

```text
NEXT EXPERIMENT

Hypothesis:
Embeddings estruturais congelados do CrossConnectome-µ melhoram a predição do
efeito de uma intervenção neuronal sobre classes grosseiras de locomoção, além
de degree-only, estatísticas artesanais e metadados permitidos do protocolo, em
famílias/tipos ou estudos deixados fora do treino.

Dataset:
Um dataset público de Drosophila com intervenção, controles, repetições e mapping
rastreável para tipos do connectoma, a ser selecionado e congelado no NG1. Se
nenhum candidato cumprir os critérios, o experimento é NO-GO.

Input:
Embedding congelado; em braços separados, grau, estatísticas artesanais e
metadados permitidos de intervenção/protocolo. Toda variante recebe o mesmo
conjunto de covariáveis não estruturais.

Target:
Distribuição ou mudança control-adjusted em classes de locomoção escolhidas antes
do teste — por exemplo forward, backward, turning e stopping — com unknown/other
quando a ontologia justificar. O target exato depende do dataset auditado.

Baselines:
Random, majority, protocol-only, degree-only, handcrafted graph statistics,
frozen embedding e embedding + handcrafted statistics.

Model:
Regressão logística/multilabel regularizada como primária; MLP pequeno como
secundário. Random forest e gradient boosting entram apenas como comparadores
tabulares sob o mesmo split e orçamento.

Train/Test split:
Split externo por estudo quando houver pelo menos dois estudos comparáveis;
senão leave-driver/family-out ou leave-cell-type-out, mantendo todos os animais,
vídeos e trials relacionados no mesmo grupo. Random split por trial/frame é
proibido. Um segundo dataset/estudo fica intocado para confirmação quando existe.

Metrics:
Macro-F1 e balanced accuracy primárias conforme o target; AUROC/AUPR por classe,
Brier, ECE, intervalos agrupados, coverage e diferença pareada contra o melhor
baseline não-embedding. Para efeitos contínuos, correlação e erro control-adjusted
pré-registrados.

Falsification criterion:
O embedding não supera o melhor baseline estrutural simples pelo SESOI
pré-registrado, o intervalo da diferença inclui zero, o ganho desaparece no
leave-family/study-out, ou não replica no segundo estudo/dataset elegível.

Expected RAM:
Teto provisório de 8 GB para a tabela derivada e treino; substituir por medição em
NV06. Vídeos não entram no primeiro MVP, salvo validação amostral.

Expected VRAM:
0 GB para modelos tabulares em CPU; teto de 2 GB para o MLP. O encoder fica
congelado e embeddings são preferencialmente pré-computados.

Expected storage:
Teto provisório de 10 GB para metadados, labels derivados e embeddings; mídia
bruta opcional tem orçamento separado e não pode ser baixada integralmente sem
gate.

What result would justify moving to NeuroVerse Stage 2:
Ganho acima do SESOI e do melhor baseline simples, CI de 95% excluindo zero,
calibração aceitável, manutenção no split agrupado mais forte disponível e
replicação em um segundo estudo/dataset independente. Sem replicação, o resultado
é piloto e não abre o Stage 2 deste programa; um sandbox técnico seria outro
projeto, sem claim biológico.
```

## Proveniência obrigatória de componentes

Cada dataset, edge, peso, sensor, motor, estado interno, parâmetro de dinâmica,
body model e regra do ambiente recebe uma das categorias:

- `observed`: medido diretamente no dataset/release;
- `derived`: transformação determinística de algo observado;
- `experimentally_constrained`: calibrado por evidência independente;
- `learned`: ajustado em dados com split e objetivo registrados;
- `approximated`: simplificação documentada;
- `synthetic`: escolha da engine sem alegação biológica;
- `inferred_missing`: estrutura prevista, sempre com `observed=false`, confiança
  e análise separada.

Um componente pode ter várias fontes, mas nunca uma origem vazia. A claim final
deve ser limitada pelo componente mais fraco na cadeia causal relevante.

## Componentes determinísticos e aprendidos

Começam determinísticos:

- schemas, unidades e relógio;
- interface `brain.step(dt)`;
- roteamento de observações/comandos;
- logging, métricas e intervenção;
- física do mundo e body model declarados;
- mappings experimentais conhecidos, sem ajuste oculto.

Podem ser aprendidos somente em ablações controladas:

- Behavior Decoder;
- pesos efetivos quando não observados;
- SensoryEncoder e MotorDecoder;
- dinâmica latente ou parâmetros do runtime;
- preenchimento de estrutura ausente.

Sempre existe um baseline determinístico ou linear. Aprender vários módulos end
to end de uma vez é proibido porque torna impossível localizar a origem do ganho.

## Representação e limites preliminares de memória

O baseline de memória usa arrays compactos, sem objeto Python por neurônio:

```text
state[N, channels]
src[E]
dst[E]
weight[E]
```

Com `int32` para `src/dst` e `float32` para `weight`, a base COO ocupa 12 bytes
por edge: aproximadamente 12 MB para 1M, 120 MB para 10M e 600 MB para 50M edges.
Com índices `int64`, sobe para pelo menos 20 bytes por edge: 20 MB, 200 MB e 1 GB.
Um canal `float32` de estado usa 1,2 KB para 300, 40 KB para 10k, 0,4 MB para
100k, 0,6 MB para 150k e 0,8 MB para 200k neurônios; multiplicar pelo número de
canais e buffers.

Esses valores são apenas arrays crus. CSR, gradientes, mensagens, índices,
temporários e bibliotecas podem multiplicar o pico. `NC03` deve medir CPU e GPU;
50M edges não serão mantidas com autograd integral em 8 GB sem prova. As opções
preferidas são grafo em CPU, agregação neuron-to-neuron, threshold/top-k,
subgrafos, chunks, operações sparse e execução event-driven quando válida.

## Stage 0 — validar premissas

- **Objetivo:** auditar literatura, datasets comportamentais, ontologia, mapping
  e novidade; selecionar exatamente um NEXT EXPERIMENT.
- **Hipótese:** existe ao menos um conjunto com controles, repetições e mapping
  suficientemente independente para testar sinal estrutural.
- **Dataset:** inventário aberto de intervenções em Drosophila; nenhum escolhido
  antes do `NG1`.
- **Implementação:** revisão reproduzível, dataset cards, grafo de proveniência,
  amostras mínimas, power/feasibility e pré-registro.
- **Sucesso:** target, unidade, split e dataset defensáveis, com denominadores e
  licença confirmados.
- **Fracasso:** mapping circular/ambíguo, ausência de controles, unidade
  pseudorreplicada ou amostra incapaz de responder à pergunta.
- **Métricas:** cobertura de mapping, indivíduos, repetições, classes, estudos,
  missingness e risco de viés.
- **Custo:** sem treino; amostras até 2 GB e 16 GB RAM.
- **Riscos:** publication bias, driver confounding e ontologias incompatíveis.
- **Artefato:** protocolo assinado e card NEXT EXPERIMENT congelado.

## Stage 1 — Connectome → Behavior

- **Objetivo:** prever efeito comportamental offline antes de qualquer organismo.
- **Hipótese:** embedding congelado acrescenta sinal ao melhor baseline simples.
- **Dataset:** escolhido no `NG1`; segundo estudo/dataset reservado quando existe.
- **Implementação:** adapter canônico, efeitos versus controle, splits agrupados,
  modelos lineares/tabulares e MLP pequeno.
- **Sucesso:** critério do NEXT EXPERIMENT e replicação definida no protocolo.
- **Fracasso:** empate com degree/handcrafted, colapso externo, má calibração ou
  dependência de mappings de baixa confiança.
- **Métricas:** macro-F1/balanced accuracy, AUROC/AUPR, Brier/ECE, CIs agrupados e
  efeitos por nível de confiança.
- **Custo:** CPU na maior parte; MLP abaixo de 2 GB VRAM; tabela abaixo de 8 GB RAM.
- **Riscos:** pseudorreplicação, multi-target interventions, study/lab shortcuts,
  class imbalance e target behavior inconsistente.
- **Artefato:** relatório confirmatório/negativo e decisão `NG2`.

## Stage 2 — NeuroVerse Core

- **Objetivo:** implementar a menor engine species-agnostic com organismo
  sintético de 8 sensores, 32 interneurônios e 8 motores.
- **Hipótese:** interfaces, runtimes e logging podem ser trocados sem alterar o
  contrato e com reprodução bitwise/tolerância definida.
- **Dataset:** fixtures sintéticas e golden trajectories, sem claim biológico.
- **Implementação:** arrays compactos, `Organism`, `Environment`, sensor/motor,
  Runtime 0 e rate-based, intervenção e CLI headless.
- **Sucesso:** mesma config/seed reproduz; adapters e runtimes são substituíveis;
  testes detectam origem artificial de cada componente.
- **Fracasso:** comportamento depende de estado oculto, ordem, backend ou código
  específico de espécie.
- **Métricas:** determinismo, steps/s, pico RAM/VRAM, bytes de log e erro entre
  backends.
- **Custo:** CPU-first; GPU opcional abaixo de 2 GB; sem engine gráfica.
- **Riscos:** overengineering e confundir teste sintético com validação neural.
- **Artefato:** `neuroverse run <config>` reproduz um organismo sintético.

## Stage 3 — C. elegans

- **Objetivo:** validar interfaces com um organismo biológico pequeno sem
  reinventar projetos existentes.
- **Hipótese:** um adapter simplificado reproduz ao menos um benchmark publicado
  dentro de tolerância e expõe claramente o que é aproximado.
- **Dataset:** connectoma, body/behavior e baseline existentes escolhidos após
  auditoria de licença e compatibilidade.
- **Implementação:** adapter, Runtime 1 e opcional LIF se identificável, sensores,
  high-level motor e ambiente headless.
- **Sucesso:** comportamento e/ou resposta de intervenção publicados são
  reproduzidos com controle e múltiplas seeds.
- **Fracasso:** só funciona com ajuste no teste, regra manual equivalente ao
  comportamento ou parâmetros não identificáveis.
- **Métricas:** velocidade, direção, turning, chemotaxis/avoidance quando
  aplicável, trajetória e efeito de intervenção.
- **Custo:** CPU ou menos de 2 GB VRAM; armazenamento pequeno.
- **Riscos:** escolher apenas casos fáceis e alegar novidade onde há reprodução.
- **Artefato:** adapter e relatório de paridade/limites.

## Stage 4 — Drosophila subset

- **Objetivo:** executar um circuito pequeno ligado ao comportamento validado no
  Stage 1.
- **Hipótese:** um subgrafo observado preserva direção de efeito melhor que
  subgrafo aleatório/rewired sob adapters controlados.
- **Dataset:** circuito/connectoma e intervenção selecionados em `NG2`.
- **Implementação:** subgraph extractor, Runtime 0/1/2, sensor mínimo, motor
  high-level e flags observed/inferred.
- **Sucesso:** efeito esperado aparece sem regra motora que o codifique e supera
  controles estruturais.
- **Fracasso:** adapters determinam o output ou só o grafo completo ajustado no
  teste funciona.
- **Métricas:** direção/tamanho de efeito, latência, robustez, edge fraction e
  sensibilidade ao runtime.
- **Custo:** abaixo de 4 GB VRAM e 16 GB RAM.
- **Riscos:** circuito incompleto, pesos desconhecidos e causalidade indireta.
- **Artefato:** experimento headless de circuito com comparação experimental.

## Stage 5 — Drosophila embodied

- **Objetivo:** fechar o loop sensor → neural → motor → corpo → ambiente em arena
  simples, sem voo.
- **Hipótese:** o circuito mantém comportamento mensurável sob perturbações do
  ambiente sem policy manual equivalente.
- **Dataset:** Stage 4 mais trajetórias/biomecânica compatíveis quando disponíveis.
- **Implementação:** corpo 2D primeiro, walking/turning/stopping, sensores mínimos,
  high-level motor e internal states marcados como grounded ou synthetic;
  low-level/MuJoCo/FlyGym só em comparação condicional posterior.
- **Sucesso:** trajetória e resposta a estímulo generalizam a seeds e layouts
  não usados no ajuste.
- **Fracasso:** ação é scriptada por adapter, instável ou incompatível com dados.
- **Métricas:** speed, turn frequency, path entropy, distância/latência, energia
  e custo computacional.
- **Custo:** CPU-first ou até 6 GB VRAM; headless obrigatório.
- **Riscos:** body/physics dominar a conclusão e estados internos inventados.
- **Artefato:** arena reproduzível com validators separados da visualização.

## Stage 6 — intervention validation

- **Objetivo:** comparar ativação, inibição e lesão simuladas com experimentos.
- **Hipótese:** direção de efeito causal é preservada em intervenções não usadas
  para ajuste.
- **Dataset:** múltiplas intervenções com controles e protocolo mapeável.
- **Implementação:** API `activate/inhibit/lesion`, dose/tempo, sham control,
  Runtime 3 intermediário somente se justificado e evaluator causal.
- **Sucesso:** efeitos held-out têm sinal e tamanho dentro de tolerância
  pré-registrada em mais de um estudo.
- **Fracasso:** acerta apenas intervenções usadas no fit ou só após tuning por
  experimento.
- **Métricas:** signed effect, latency, dose-response, calibration e equivalence
  bounds.
- **Custo:** matriz limitada; até 6 GB VRAM e budget por intervenção.
- **Riscos:** manipulação experimental não equivaler à operação simulada.
- **Artefato:** benchmark de intervenções e matriz simulation-vs-experiment.

## Stage 7 — Cross-animal transfer

- **Objetivo:** congelar relação A e prever intervenções em B nunca usado.
- **Hipótese:** CrossConnectome permite transferir identidade estrutural e efeito
  comportamental acima de baselines.
- **Dataset:** A para desenvolvimento; B com connectoma e comportamento selados.
- **Implementação:** matching congelado, adapters sem refit, predições assinadas e
  avaliação por custodiante.
- **Sucesso:** ganho externo acima do SESOI e controles, com incerteza de mapping.
- **Fracasso:** within-A alto e cross-B nulo, ou dependência de adaptação a B.
- **Métricas:** macro-F1/effect error, calibration, coverage, mapping-stratified
  performance e within-vs-cross gap.
- **Custo:** até 8 GB VRAM com margem; sem sweep em B.
- **Riscos:** poucos animais e ontologia/cobertura diferentes.
- **Artefato:** relatório cross-animal confirmatório ou negativo.

## Stage 8 — Minecraft Adapter

- **Objetivo:** demonstrar que o ambiente é plugável sem contaminar o organismo.
- **Hipótese:** o mesmo organismo recebe observações e produz comandos pela
  interface comum em um domínio artificial.
- **Dataset:** cenários sintéticos versionados, não dados biológicos.
- **Implementação:** `EnvironmentAdapter`, sensores reduzidos, ações high-level e
  experimentos de comida, obstáculo e ameaça.
- **Sucesso:** core não importa Minecraft; determinismo/tolerância e logs passam;
  resultados são rotulados testbed artificial.
- **Fracasso:** lógica comportamental migra para o adapter ou física exige
  reescrever o organismo.
- **Métricas:** compatibilidade, success rate, trajetória, latência e throughput.
- **Custo:** cliente/servidor local; orçamento específico antes de instalar.
- **Riscos:** demo visual virar claim biológico.
- **Artefato:** adapter isolado e relatório de domain shift artificial.

## Stage 9 — Synthetic organisms

- **Objetivo:** testar controles estruturais e mutações sem confundir com animal.
- **Hipótese:** organização real supera grafos random/degree-preserving e mostra
  degradação específica sob ablações.
- **Dataset:** connectomas congelados e variantes geradas por seed/config.
- **Implementação:** edge deletion 10/25/50%, circuit deletion, rewiring,
  degree-preserving shuffle e estrutura inferida sempre sinalizada.
- **Sucesso:** diferença robusta versus controles e curva de degradação
  reproduzível; null também é aceito.
- **Fracasso:** equivalência ao controle ou ganho explicado por tamanho/grau.
- **Métricas:** task performance, robustness curve, graph metrics e custo.
- **Custo:** successive-halving; mesma escala dos Stages 4–5.
- **Riscos:** múltiplas comparações e escolher mutação pós-hoc.
- **Artefato:** benchmark real-vs-null e catálogo de variantes rastreável.

## Stage 10 — Artificial evolution

- **Objetivo:** explorar adaptação de controladores inspirados em connectoma sob
  pressão seletiva explicitamente artificial.
- **Hipótese:** diferentes priors estruturais alteram velocidade, estabilidade ou
  soluções da busca sob igual budget.
- **Dataset:** populações/configurações sintéticas e connectoma como seed, nunca
  tratado como evolução biológica observada.
- **Implementação:** mutações limitadas, fitness declarado, seeds, lineage e
  controles random/degree-preserving.
- **Sucesso:** efeito replica em seeds e budgets, sem vantagem de parâmetros
  ocultos.
- **Fracasso:** resultado instável, dependente de fitness arbitrário ou igual aos
  controles.
- **Métricas:** sample efficiency, best/median fitness, diversidade, estabilidade
  e custo.
- **Custo:** piloto CPU/GPU curto; expansão só por gate.
- **Riscos:** anthropomorphism, compute explosion e narrativa evolutiva exagerada.
- **Artefato:** estudo exploratório separado do paper biológico.
