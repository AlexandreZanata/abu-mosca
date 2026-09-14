# Neuron matching e graph alignment (revisão)

Aberto em 2026-09-14 (L03). Revisão de métodos e baselines publicados para
correspondência de neurônios e alinhamento de grafos, com foco no que cada um
exige e por que não serve diretamente como zero-shot cross-connectome. Fontes
primárias registradas em `research/literature/` (LEDGER.tsv); nenhum dataset
card é preenchido aqui.

## 1. Estado e escopo

- Métodos recebem IDs `ALN-nn`; a supervisão é classificada explicitamente e um
  método supervisionado nunca será chamado de não supervisionado (proibição L03).
- Cobertura: morfologia (NBLAST e NeuronBridge) e conectividade/grafo (bisected
  graph matching, SGM, REGAL e FINAL).
- Nenhuma métrica foi reproduzida; a reprodução de um baseline publicado cabe a
  B08.

## 2. Métodos

### ALN-01 — NBLAST
- Referência: LIT-0026 (Costa et al. 2016, Neuron; DOI 10.1016/j.neuron.2016.06.012).
- Input: esqueletos de neurônios (nuvem de pontos com direção local), comparados em espaço comum após registro.
- Âncoras/rótulos: nenhuma; a pontuação vem de estatística de matches e não-matches.
- Supervisão: não supervisionado.
- Caráter: transdutivo.
- Datasets: FlyCircuit (16.129 neurônios de LM) e aplicações FAFB-luz.
- Código/licença: pacote R `nat.nblast` público (natverse); licença não verificada nesta busca; artigo CC BY.
- Métrica: similaridade NBLAST; acurácia de recuperação e de clusterização.
- Inadequações ao zero-shot: usa morfologia, não conectividade; exige registro espacial comum; não gera embedding indutivo por nó; pertence ao Experimento C, não ao trilho topologia.
- Status: documentado

### ALN-02 — NeuronBridge (CDM Search e PPPM)
- Referência: LIT-0027 (Clements et al. 2024, BMC Bioinformatics; DOI 10.1186/s12859-024-05732-7).
- Input: imagens de morfologia EM e LM alinhadas a um template comum.
- Âncoras/rótulos: nenhuma; matches putativos pré-computados.
- Supervisão: não supervisionado.
- Caráter: transdutivo.
- Datasets: hemibrain, MANC e bibliotecas FlyLight; FANC e FlyWire previstos no artigo.
- Código/licença: código arquivado em Zenodo 10.5281/zenodo.10541060; imagens sujeitas a acordo de licença.
- Métrica: ranking de matches putativos, validado por correspondências conhecidas.
- Inadequações ao zero-shot: modalidade imagética/morfológica; não usa conectividade; não embute um alvo novo sem registro; depende de serviço pré-computado.
- Status: documentado

### ALN-03 — Bisected graph matching
- Referência: LIT-0028 (Pedigo et al. 2022, Network Neuroscience; DOI 10.1162/netn_a_00287).
- Input: matrizes de adjacência de um mesmo sistema dividido em duas partes (hemisférios), dirigidas e ponderadas.
- Âncoras/rótulos: nenhuma no núcleo; extensões opcionais usam pareamentos previamente conhecidos como sementes.
- Supervisão: não supervisionado (núcleo); usos com sementes são híbridos.
- Caráter: transdutivo.
- Datasets: C. elegans (hermafrodita e macho), P. pacificus e subconjunto larval de Drosophila.
- Código/licença: implementado em bibliotecas de graph matching; licença não verificada nesta busca.
- Métrica: acurácia de pareamento contra pares conhecidos.
- Inadequações ao zero-shot: pareia hemisférios do mesmo indivíduo; a correspondência bilateral é referência, não alvo; não classifica tipo nem generaliza para um alvo novo.
- Status: documentado

### ALN-04 — Seeded graph matching (SGM/FAQ)
- Referência: LIT-0029 (Fishkind et al. 2019, Pattern Recognition; DOI 10.1016/j.patcog.2018.09.014).
- Input: dois grafos e, na variante SGM, um alinhamento parcial conhecido.
- Âncoras/rótulos: sementes obrigatórias em SGM; a variante FAQ não é semeada.
- Supervisão: supervisionado (SGM, por sementes); FAQ é não supervisionado.
- Caráter: transdutivo.
- Datasets: simulações e experimentos reais; sem connectoma de Drosophila específico.
- Código/licença: implementações públicas (por exemplo graspologic e Gunrock HIVE); licença não verificada nesta busca.
- Métrica: discordância de adjacência e taxa de acerto.
- Inadequações ao zero-shot: exigiria sementes, que são correspondências proibidas no nosso desenho; não lida com nós sem par sem extensão; não produz representação transferível.
- Status: documentado

### ALN-05 — REGAL (xNetMF)
- Referência: LIT-0030 (Heimann et al. 2018, CIKM; DOI 10.1145/3269206.3271788).
- Input: dois grafos; atributos de nó são opcionais.
- Âncoras/rótulos: nenhuma; atributos são features, não rótulos.
- Supervisão: não supervisionado.
- Caráter: transdutivo.
- Datasets: redes sociais e biológicas gerais, não connectomas.
- Código/licença: github.com/GemsLab/REGAL, licença MIT.
- Métrica: acurácia de alinhamento.
- Inadequações ao zero-shot: alinha identidades de nós entre dois grafos; não classifica tipo; atributos podem vazar no trilho topologia; não transfere para um alvo não visto sem nova execução conjunta.
- Status: documentado

### ALN-06 — FINAL
- Referência: LIT-0031 (Zhang e Tong 2016, KDD; DOI 10.1145/2939672.2939766).
- Input: duas redes atribuídas, com topologia e atributos de nó ou aresta; preferência prévia opcional.
- Âncoras/rótulos: nenhuma por padrão; a preferência prévia é opcional.
- Supervisão: não supervisionado.
- Caráter: transdutivo.
- Datasets: redes atribuídas gerais, não connectomas.
- Código/licença: código hospedado em asu.edu; licença não verificada nesta busca.
- Métrica: acurácia de alinhamento.
- Inadequações ao zero-shot: exige atributos, incompatível com o trilho somente topologia; não induz embedding para nós novos.
- Status: documentado

## 3. Síntese para o zero-shot

- Nenhum método revisado é zero-shot cross-connectome no sentido do projeto:
  todos são transdutivos (resolvem o par na hora) e/ou exigem morfologia,
  registro espacial ou atributos.
- SGM usa sementes e bisected graph matching tem extensões com pareamentos
  conhecidos; esses usos não podem ser apresentados como baselines não
  supervisionados (proibição L03).
- NBLAST, CDM Search e PPPM são referências morfológicas do Experimento C, não
  do trilho topologia.
- Existe base publicada de matching (CLM-008); a reprodução de um baseline
  publicado fica em B08, com rótulo explícito de transdutivo quando for o caso.
- Consequência para o desenho: baselines transdutivos serão rotulados como tais
  (B06 e B07) e nunca apresentados como zero-shot; o encoder indutivo treinado
  na fonte continua sendo a proposta a testar.

## 4. Limitações

- Busca limitada às consultas Q1 e Q2 do protocolo; licenças de código foram
  registradas como não verificadas quando a fonte consultada não as declarava.
- Nenhum dataset foi acessado e nenhuma métrica foi reproduzida nesta fase.
- Aplicação de matching multi-dataset em Drosophila aparece em LIT-0032 como
  contexto; não foi classificada como método novo.
- Validação: `python3 tools/validate_research.py`.
