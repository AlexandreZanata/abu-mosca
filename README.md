# CrossConnectome-µ

Planejamento operacional de uma pesquisa sobre transferência de representações
neuronais entre connectomas de *Drosophila*. A pergunta provisória é se um
encoder pequeno, treinado sem rótulos em conectividade de um connectoma-fonte,
consegue recuperar tipos neuronais em um connectoma-alvo nunca usado no treino.

Este repositório contém **somente o plano**. Ainda não há conclusão sobre
viabilidade, melhor par de datasets, arquitetura ou novidade. Essas respostas
serão produzidas com evidência nas microfases e não devem ser presumidas.

## Ordem obrigatória de leitura

1. [Escopo e hipóteses](docs/ESCOPO-E-HIPOTESES.md)
2. [Protocolo de execução e reprodutibilidade](docs/PROTOCOLO-EXECUCAO.md)
3. [Plano de microfases](docs/PLANO-MICROFASES.md)
4. [Matriz de rastreabilidade](docs/MATRIZ-RASTREABILIDADE.md)
5. [Modelos de artefatos](docs/templates/README.md)

O prompt operacional para retomar o projeto ficará em
`.local/PROMPT-CONTINUAR.md`. A pasta `.local/` é ignorada pelo Git de propósito.

O caminho máximo tem 81 microfases e 9 gates, mas não é uma obrigação executar
todas: ramos caros e multimodais só abrem se os gates anteriores justificarem.
O Nível 0 usa 27 passos sem treino; o Nível 1 leva o MVP ao gate em mais 40; os
13 passos do Nível 2 e os 10 do Nível 3 são condicionais.

## Regra de execução

- Executar exatamente uma microfase aberta por vez.
- Não começar treinamento antes dos gates de literatura, dados, leakage e
  pré-registro.
- Não consultar rótulos do connectoma-alvo fora do avaliador selado.
- Não promover uma hipótese com base apenas em visualização ou em uma seed.
- Registrar fontes, comandos, hashes, testes, métricas e decisões suficientes
  para outra pessoa repetir o resultado.
- Encerrar ou reformular cedo quando um gate reprovar; resultado negativo é um
  resultado científico válido.

## Níveis de entrega

- **Nível 1 — MVP:** um connectoma-fonte, um alvo, conectividade apenas,
  baselines simples e um encoder indutivo de aproximadamente 1–3 milhões de
  parâmetros.
- **Nível 2 — experimento sério:** repetições, incerteza, ablações, open-set,
  controles de atalhos, direção inversa e análise de domain shift.
- **Nível 3 — projeto de paper:** múltiplos connectomas quando defensável,
  reprodução independente, artefatos congelados e redação proporcional à
  evidência.

## Estado inicial

- [x] Briefing consolidado em um contrato de pesquisa provisório.
- [x] Protocolo e roadmap de microfases preparados.
- [ ] Nenhuma pesquisa bibliográfica foi validada ainda.
- [ ] Nenhum dataset foi aprovado ou baixado ainda.
- [ ] Nenhum código ou experimento foi executado ainda.
