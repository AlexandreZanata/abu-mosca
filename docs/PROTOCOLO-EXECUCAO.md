# Protocolo de execução e reprodutibilidade

## Papéis

- **Planejador:** mantém escopo, dependências, gates e critérios. Não executa
  experimento nesta etapa inicial.
- **Executor:** preferencialmente uma IA econômica; realiza uma única microfase
  objetiva, produz testes e evidência, sem tomar decisões científicas fora dela.
- **Custodiante/avaliador:** mantém rótulos-alvo selados e executa a avaliação
  final a partir de artefatos congelados. Deve usar uma sessão separada do
  executor ou, idealmente, uma pessoa independente.
- **Revisor humano:** decide gates que envolvem equivalência ontológica,
  circularidade de rótulos, novidade, interpretação estatística ou publicação.

Uma pessoa pode acumular papéis, mas deve manter sessões, diretórios e registros
separados. A separação procedural deve ser declarada como limitação; ela não vira
cegamento perfeito apenas por estar documentada.

## Protocolo obrigatório para qualquer IA

1. Leia `README.md`, este protocolo e os arquivos do programa ativo. No programa
   principal, use `docs/ESCOPO-E-HIPOTESES.md` e somente a seção relevante de
   `docs/PLANO-MICROFASES.md`. Depois de G8, no NEXT, use
   `docs/ESCOPO-NEXT-NEUROVERSE.md` e somente o Stage relevante de
   `docs/PLANO-MICROFASES-NEXT.md`.
2. Inspecione `git status --short`, `git log -5 --oneline` quando já houver
   commits e a evidência da fase anterior. Preserve toda alteração preexistente.
3. Escolha somente a primeira microfase `[ ]` do plano ativo cujas dependências
   estejam `[x]`.
4. Antes de editar, copie para a resposta: ID, objetivo, entregas, critérios de
   aceite, proibições, orçamento e dependências. Se algo for objetivamente
   impossível, pare e registre o bloqueio; não improvise outra pergunta.
5. Faça a menor mudança completa. Não antecipe fases, não “aproveite” para trocar
   arquitetura e não execute uma matriz experimental não autorizada.
6. Rode todas as validações da microfase a partir de um comando/script
   versionado. Saída manual não substitui teste automatizado quando este for
   viável.
7. Atualize documentos afetados e acrescente uma linha de evidência sob a
   microfase sem alterar retroativamente seu objetivo.
8. Marque `[x]` somente se todos os critérios forem satisfeitos. Uma fase parcial
   continua `[ ]` e recebe uma nota de bloqueio.
9. Faça um único commit local `fase <ID>: <descrição curta>`, incluindo apenas
   arquivos da fase. Nunca faça push, publique dados ou crie release sem pedido
   explícito do responsável.
10. Encerre a execução. A próxima IA deve começar uma nova sessão na fase
    seguinte.

## Definição global de pronto

- Entregas e critérios da microfase são rastreáveis a arquivos, comandos ou
  decisões assinadas.
- Toda afirmação factual externa tem fonte primária/oficial, URL/DOI, versão ou
  data, data de acesso e trecho/paráfrase verificável.
- Downloads têm release e SHA-256 quando tecnicamente possível; transformações
  têm configuração, seed, versão do código e checksums de entrada/saída.
- Testes usam fixtures pequenas e uma amostra real quando a fase depende de
  formato externo.
- Runs registram commit, estado dirty, ambiente, hardware, tempo, pico de RAM e
  VRAM, parâmetros, seed e métricas.
- Resultados agregados são gerados a partir de arquivos de métricas; números não
  são copiados manualmente para tabelas finais.
- Rótulos do alvo não aparecem em treino, seleção, normalização, debug, logs ou
  nomes de arquivos acessíveis ao executor.
- Documentação descreve limites e falhas, não apenas o caminho feliz.

## Padrão mínimo de evidência externa

Para cada claim de dataset ou literatura, registrar:

- claim atômico;
- fonte primária/oficial e identificador persistente;
- versão/release e data de acesso;
- localização exata na fonte;
- status `confirmado`, `ambíguo`, `conflitante` ou `não encontrado`;
- impacto no desenho;
- segunda fonte independente quando a decisão muda o experimento.

Snippet de buscador, resumo de IA, blog e README de terceiro servem para descobrir
fontes, não para validar um claim central. A IA nunca completa uma célula ausente
por plausibilidade.

## Firewall do connectoma-alvo

O projeto deverá separar quatro zonas:

- `data/raw/source/`: grafo e metadados permitidos da fonte;
- `data/raw/target-public/`: grafo e features do alvo permitidos em inferência;
- `data/sealed/target-labels/`: tipos, crosswalk avaliativo e correspondências;
- `artifacts/frozen/`: encoder, probe, transformações, configuração e hashes
  congelados antes da avaliação.

O executor não lê `data/sealed/`. O avaliador recebe somente os artefatos
congelados e produz um pacote de métricas, sem devolver rótulos por neurônio. O
primeiro unseal exige registro de data, commit, checksums e assinatura do gate.

Se não houver custodiante independente, a avaliação deve ocorrer em uma sessão
nova, depois do congelamento, e essa limitação deve ser relatada. Reabrir tuning
após o unseal transforma o alvo em validação; um novo alvo intocado será exigido
para qualquer alegação confirmatória.

## Normalização e uso permitido do alvo

- Transformações aprendidas são ajustadas somente na fonte e aplicadas ao alvo.
- Estatísticas globais do alvo não são usadas no trilho confirmatório, salvo uma
  análise separada e pré-registrada de adaptação não supervisionada.
- Estrutura do alvo pode ser usada pelo message passing em inferência.
- Ontologia do alvo pode ser usada pelo custodiante para pontuar, nunca para
  selecionar arquitetura, features, classes fáceis ou limiares.
- Classes conhecidas e open-set são definidas no protocolo congelado, não após
  olhar erros individuais.

## Regras estatísticas

- Declarar uma métrica primária e uma diferença mínima relevante antes do
  unseal.
- Separar variação por seed de incerteza biológica. Cinco seeds não criam cinco
  moscas.
- Usar intervalos de confiança e diferenças pareadas; não selecionar apenas a
  melhor seed.
- Respeitar dependência entre neurônios com bootstrap/permutação agrupado por
  tipo e análises de sensibilidade adequadas ao grafo.
- Corrigir ou hierarquizar múltiplas comparações nas ablações confirmatórias.
- Relatar denominadores, classes excluídas e cobertura; não ocultar classes
  pequenas para melhorar score.

## Controle de custo

- Uma sessão de IA por microfase, com contexto limitado aos arquivos indicados.
- Tarefas documentais usam primeiro fontes já registradas e busca por DOI/citação;
  a web ampla só serve para descoberta.
- Toda implementação começa com fixture sintética e amostra mínima; o dataset
  completo só roda depois que invariantes passam.
- Smoke: até 5 minutos e 2 GB de VRAM. Piloto: até 30 minutos e 6 GB. Run
  confirmatório: teto definido no gate, mantendo margem abaixo de 8 GB.
- Busca de hiperparâmetros tem espaço e número máximo de trials pré-registrados;
  sem sweep aberto.
- Arquiteturas mais caras só abrem se a anterior ultrapassar o gate definido.
- Cache é identificado por checksum e nunca reaproveitado quando entrada,
  código ou configuração mudam.

## Decisões que exigem revisão humana

- Aprovar a definição de “mesmo tipo” e o crosswalk entre ontologias.
- Aceitar ou rejeitar rótulos cuja anotação tenha usado conectividade ou
  correspondências que tornem a avaliação circular.
- Escolher o par fonte/alvo e confirmar comparabilidade biológica.
- Assinar pré-registro, unseal, mudança de desfecho e gate de paper.
- Autorizar download sujeito a termos, publicação, upload ou contato externo.

Até a revisão ocorrer, a IA pode preparar evidências e opções, mas não marcar o
gate como aprovado.

## Alterações de protocolo

Antes do unseal, uma mudança exige registro com motivo, impacto, autor e diff do
pré-registro. Depois do unseal, a análise original permanece confirmatória e a
mudança é rotulada exploratória. Nunca sobrescrever configuração ou resultado
antigo.

## Formato de evidência no plano

Ao concluir uma microfase, acrescentar imediatamente abaixo dela:

```text
Evidência (AAAA-MM-DD, executor): arquivos; fontes/versões; comandos e testes;
resultado resumido; recursos medidos; decisão/limitação; commit <hash>.
```

Não preencher evidência futura, não colar logs extensos e não registrar um
comando que não foi realmente executado.
