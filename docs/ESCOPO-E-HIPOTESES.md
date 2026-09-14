# Escopo e hipóteses

## Estado deste documento

Este é um contrato **provisório de planejamento**, não um resultado científico
nem um pré-registro. Os nomes de datasets abaixo formam apenas a lista inicial a
ser auditada. Disponibilidade, licença, campos, comparabilidade e novidade só
podem ser afirmadas depois das microfases correspondentes.

## Pergunta científica refinada

> Um encoder indutivo pequeno, treinado de forma auto-supervisionada somente em
> um ou mais connectomas-fonte, aprende representações baseadas em conectividade
> que transferem para a recuperação de tipos neuronais em um connectoma-alvo
> completamente ausente do treinamento e da seleção de hiperparâmetros?

A formulação evita afirmar que conectividade determina função, que “tipo” é uma
verdade natural sem ruído ou que dois neurônios são indivíduos one-to-one. O
alvo primário é transferência de **rótulo de tipo harmonizado**, não equivalência
funcional completa.

## Hipóteses provisórias

### Hipótese primária H1

Em classes presentes na fonte e no alvo, um encoder indutivo treinado sem
rótulos na fonte supera, no alvo nunca visto, o melhor baseline simples
pré-registrado em recuperação macro por tipo, sem usar IDs, coordenadas,
morfologia, neurotransmissor, regiões ou estatísticas ajustadas no alvo no trilho
“somente topologia”.

### Hipótese nula H0

Depois de controlar desbalanceamento, grau, atalhos de amostragem e incerteza,
o encoder não supera o melhor baseline simples por uma diferença cientificamente
relevante; qualquer desempenho aparente é compatível com propriedades triviais,
ruído de anotação ou peculiaridades do dataset-fonte.

### Hipóteses secundárias

- Atributos locais acrescentam sinal transferível além da topologia.
- Morfologia acrescenta sinal quando as reconstruções são comparáveis.
- Treinar em mais de uma fonte melhora a generalização para uma fonte deixada de
  fora, sem adaptação supervisionada ao alvo.
- O ganho, se existir, satura em um modelo pequeno; aumentar parâmetros além do
  necessário não é contribuição por si só.
- Distância do embedding pode sustentar rejeição open-set razoavelmente
  calibrada para tipos ausentes da fonte.

## Definições operacionais

- **Fonte:** connectoma cujo grafo pode ser usado no treino auto-supervisionado;
  seus rótulos só podem ser usados pelos baselines/probes definidos e pela
  avaliação interna da fonte.
- **Alvo:** connectoma nunca usado para ajustar pesos, arquitetura,
  hiperparâmetros, limiares, normalizadores ou escolhas analíticas.
- **Grafo do alvo:** pode ser usado em inferência pelo encoder indutivo, pois é a
  entrada do problema. Isso não autoriza usar rótulos, crosswalks avaliativos ou
  estatísticas globais do alvo no treino.
- **Rótulos selados:** tipos e correspondências do alvo, isolados do executor e
  lidos apenas pelo avaliador depois do congelamento da análise.
- **Zero-shot cross-connectome:** pesos, transformações, limiares e probe
  congelados antes do alvo; nenhuma atualização com rótulo do alvo.
- **Few-shot:** trilho separado, explicitamente rotulado, com orçamento de
  exemplos e resultados que jamais substituem o zero-shot.
- **Mesmo tipo:** igualdade após crosswalk versionado e rastreável entre
  ontologias, limitado ao nível taxonômico que a evidência sustenta.
- **Open-set:** consulta do alvo cujo tipo harmonizado não existe na galeria da
  fonte; deve poder ser rejeitada como desconhecida.
- **Indivíduo biológico:** um connectoma de um espécime. Seeds de treinamento e
  neurônios do mesmo grafo não são réplicas biológicas independentes.

## Desfechos

O desfecho primário será escolhido e congelado antes da avaliação do alvo. A
preferência inicial é recuperação macro por tipo — por exemplo Macro Recall@1 —
com intervalo de confiança por bootstrap agrupado por tipo. Métricas secundárias
incluem Recall@5/10, MRR, MAP, macro-F1, balanced accuracy, Brier Score, ECE e
métricas open-set como AUROC/AUPR e FPR em uma taxa de verdadeiros positivos
pré-especificada.

Micro-médias e acurácia bruta serão apenas diagnósticas porque tipos frequentes
podem dominá-las. UMAP e t-SNE serão exclusivamente visuais.

## Definição provisória de sucesso e falsificação

O pré-registro deverá substituir estes padrões por números justificados após o
inventário dos dados. Até lá, o gate do MVP considera:

- **sinal promissor:** melhoria mediana de pelo menos 5 pontos percentuais
  absolutos sobre o melhor baseline simples na métrica primária, com intervalo
  de confiança de 95% para a diferença excluindo zero, preservada na análise
  balanceada por tipo e no controle pareado por grau;
- **resultado parcial:** supera aleatório/majoritário, mas empata com degree-only,
  estatísticas artesanais, MLP ou outro baseline simples;
- **refutação da alegação de gramática transferível:** não supera o baseline
  simples, o ganho desaparece em negativos pareados por grau, ou o desempenho
  cross-connectome fica compatível com a nulidade apesar de bom desempenho
  dentro da fonte;
- **inconclusivo:** cobertura de rótulos, tamanho de amostra, circularidade da
  anotação ou incompatibilidade anatômica impedem o teste. “Inconclusivo” não
  deve ser rebatizado como sucesso.

Mesmo um ganho estatístico não autoriza uma afirmação populacional forte quando
há somente um indivíduo-fonte e um indivíduo-alvo. Nesse caso, a conclusão será
um estudo de transferência entre os datasets observados.

## Trilhos de informação

### Experimento A — topologia

Permitido: direção, pesos de sinapse, graus in/out, padrões de vizinhança e
motivos computados sem rótulo. Proibido: IDs numéricos como feature, posição,
região, neurotransmissor, morfologia, tipo e qualquer campo derivado diretamente
do target avaliativo.

### Experimento B — topologia e atributos locais

Pode acrescentar, em ablações separadas e somente quando disponíveis e
harmonizáveis: neurotransmissor, região, posição do soma e associação a
neuropilos. Cada modalidade precisa de baseline próprio e auditoria de leakage.

### Experimento C — morfologia

Só abre se skeletons, escalas, cobertura e pré-processamento forem comparáveis.
Compara morfologia apenas, conectividade apenas e combinação. Incompatibilidade
documentada encerra o trilho sem bloquear o paper principal.

## Arquiteturas e baselines em ordem de custo

1. aleatório e maioria;
2. grau e estatísticas artesanais;
3. MLP sobre as mesmas features;
4. Node2Vec/DeepWalk e embeddings espectrais, com a limitação de que espaços
   transdutivos independentes não são comparáveis sem alinhamento permitido;
5. GraphSAGE;
6. GIN;
7. GAT ou GNN relacional apenas se a representação exigir;
8. Transformer de grafo pequeno somente após ganho demonstrado e justificativa.

Nenhum método transdutivo será apresentado como baseline zero-shot direto se
não conseguir embutir o alvo no mesmo espaço sem rótulos ou âncoras proibidas.

## Tarefas auto-supervisionadas prioritárias

- Masked edge/weight prediction com decoder baseado em embeddings, sem tabela de
  parâmetros por node ID e com negativos pareados por grau/distância.
- Reconstrução de estatísticas da vizinhança que não inclua rótulos avaliativos.
- Contrastive learning apenas depois de provar que as augmentations preservam a
  identidade biológica relevante e não criam um atalho.
- Masked node attributes somente no Experimento B; nunca no trilho topologia.

Link prediction no alvo sem fine-tuning é um desfecho secundário, não substitui
a avaliação de tipos.

## Candidatos a auditar

- FlyWire / FAFB;
- hemibrain, incluído como comparador obrigatório mesmo não citado no briefing;
- BANC;
- MANC;
- MAOL;
- MCNS.

Para cada candidato será verificado em fonte oficial: espécime, sexo, estágio,
tecido e cobertura; release; IDs; arestas/pesos; tipos e proveniência desses
rótulos; neurotransmissores; regiões; skeletons; formatos; API/dump; licença;
volume; checksums; crosswalks e correspondências independentes. Não existe “par
escolhido” antes desse inventário.

## Restrições de engenharia

- Hardware-alvo: RTX 4060 Laptop com 8 GB de VRAM, i7-13620H, 32 GB de RAM e
  Linux.
- Faixa preferida: 500 mil a 5 milhões de parâmetros; 10–20 milhões só após uma
  curva de escala justificar.
- Pré-processamento em CPU, formatos colunares/sparse, mmap quando útil,
  neighbor sampling e mixed precision após teste de equivalência.
- Smoke test máximo de 5 minutos; piloto máximo de 30 minutos; execução longa só
  depois de um gate e com orçamento registrado.
- Dados brutos, rótulos selados, checkpoints e runs não entram no Git; manifestos,
  código, configurações e resultados agregados reproduzíveis entram.

## Fora do escopo inicial

- Simular a dinâmica biológica do cérebro inteiro.
- Inferir função neural completa somente de conectividade.
- Treinar modelos gigantes ou chamar o encoder de foundation model sem evidência.
- Ajustar no alvo e ainda nomear o resultado zero-shot.
- Procurar hiperparâmetros após observar as métricas seladas do alvo.
- Fazer alegações entre espécies, estágios ou regiões sem experimento próprio.
