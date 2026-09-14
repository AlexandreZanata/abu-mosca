# Predição de tipo por conectividade e morfologia (revisão)

Aberto em 2026-09-14 (L04). Revisão de evidência a favor, contra e condições de
validade para tipagem celular a partir de conectividade e morfologia, e registro
de como os rótulos foram originalmente produzidos. Fontes primárias no ledger;
nenhum dataset card é preenchido aqui.

## 1. Estado e escopo

- Modalidades recebem IDs `CT-Mn`; proveniência de rótulos recebe `CT-Pn`.
- Proibição central: correlação dentro de um indivíduo não prova transferência
  entre indivíduos ou connectomas.
- Rotas de leitura por modalidade: conectividade (Experimento A), morfologia e
  atributos (Experimentos B e C); a decisão de trilhos é de C03.
- Nenhuma métrica foi reproduzida nesta fase.

## 2. Modalidades

### CT-M1 — Connectivity-only
- Referência: LIT-0002, LIT-0006, LIT-0033, LIT-0036.
- Evidência a favor: CBLAST agrupa neurônios por padrões de conexão sináptica e separa tipos com morfologia quase idêntica (LIT-0006, LIT-0036); classes derivadas exclusivamente de conectividade potencial recuperam estrutura de circuito e revelam aspectos não capturados por esquemas tradicionais (LIT-0033); a comparação entre cérebros usa conectividade co-clusterizada para definir tipos consensuais (LIT-0002).
- Evidência contra: apenas 14% dos tipos de conectividade do hemibrain foram reidentificados no FlyWire, enquanto os tipos morfológicos serviram de base reprodutível (LIT-0002); conectividade potencial por sobreposição espacial não é sinapse EM (LIT-0033); parte dos rótulos do hemibrain foi produzida com base em conectividade, gerando risco de circularidade (LIT-0002).
- Condições de validade: usar conectividade como sinal sob controles pareados por grau; nunca avaliar contra rótulos cuja produção usou a mesma conectividade sem auditoria (C05 e D08).
- Status: documentado

### CT-M2 — Morphology-only
- Referência: LIT-0026, LIT-0027, LIT-0002.
- Evidência a favor: NBLAST distingue tipos finos sem informação a priori e é rápido (LIT-0026); NeuronBridge recupera morfologias entre EM e LM em escala (LIT-0027); quase todos os neurônios do hemibrain têm parceiro morfologicamente muito similar no FlyWire, e a tipagem morfológica foi a base reprodutível na comparação entre cérebros (LIT-0002).
- Evidência contra: morfologia não determina conectividade; neurônios com forma semelhante podem ter entradas distintas (LIT-0006); exige registro espacial comum e template (LIT-0026, LIT-0027); pertence ao Experimento C, não ao trilho topologia.
- Condições de validade: usar apenas quando escalas, cobertura e pré-processamento forem comparáveis (ESCOPO, Experimento C); reportar cobertura e registrar o template.
- Status: documentado

### CT-M3 — Posição
- Referência: LIT-0035, LIT-0036, LIT-0038.
- Evidência a favor: posição e localização de soma entram na definição operacional de tipos em anotações de conectoma e em features iniciais de clustering por conectividade (LIT-0035, LIT-0036); a anotação oficial do FlyWire carrega o campo `side` (LIT-0038).
- Evidência contra: posição sozinha é fraca; o próprio CBLAST usa região/posição apenas para gerar tipos putativos iniciais, refinados por conectividade (LIT-0036); posição é justamente o atalho que o trilho A proíbe (RISCOS RSK-003).
- Condições de validade: permitida apenas como estratificação, diagnóstico ou inicialização interna, nunca como feature do trilho topologia nem como classe (C03).
- Status: documentado

### CT-M4 — Região
- Referência: LIT-0037, LIT-0032, LIT-0036.
- Evidência a favor: populações de neurônios são frequentemente agrupadas pela innervação de neuropilas, e a nomenclatura hierárquica de 2014 torna regiões comparáveis entre estudos (LIT-0037, LIT-0032).
- Evidência contra: fronteiras dependem de marcadores e podem variar; mudanças de nomenclatura quebram comparações (LIT-0037); a mesma região contém tipos distintos e o mesmo tipo pode ocupar regiões diferentes (LIT-0002).
- Condições de validade: mesmo uso de posição — estratificação e diagnóstico; nunca como rótulo avaliativo de tipo (C03).
- Status: documentado

### CT-M5 — Neurotransmissor
- Referência: LIT-0034.
- Evidência a favor: o transmissor pode ser predito de imagens EM com 87% por sinapse, 94% por neurônio e 91% por tipo conhecido, habilitando sinal excitatório/inibitório sem rótulos moleculares no alvo (LIT-0034).
- Evidência contra: é predição, não medida; assume um único transmissor de baixo peso molecular por neurônio e exclui co-transmissão; o ground truth cobre 356 tipos de 21 estudos, com cobertura limitada (LIT-0034).
- Condições de validade: usar só no Experimento B, quando disponível e harmonizável, com baseline próprio e incerteza da predição declarada (ESCOPO).
- Status: documentado

### CT-M6 — Função
- Referência: LIT-0002, LIT-0010, LIT-0019.
- Evidência a favor: anotações de fluxo/superclasse ajudam a navegar e a gerar hipóteses, e depósitos de dados trazem campos de função de célula (LIT-0002, LIT-0010, LIT-0019).
- Evidência contra: EM não mede função; rótulos funcionais são atribuídos por curadoria a partir de literatura, morfologia e conectividade, com risco de circularidade; o projeto declara função fora do escopo como desfecho (GLO-07).
- Condições de validade: usar apenas como contexto de hipótese; nunca como desfecho, classe de tipo ou evidência de transferência.
- Status: documentado

## 3. Proveniência dos rótulos

### CT-P1 — hemibrain
- Como o rótulo foi produzido: NBLAST produziu 5.235 tipos morfológicos; rodadas de CBLAST dividiram alguns tipos, gerando 640 tipos de conectividade; revisão manual extensa; 7% dos tipos vinham da literatura e 90% eram novos, derivados de um hemisfério de um único animal; a filosofia era dividir em caso de dúvida (LIT-0006, LIT-0002).
- Fonte: LIT-0002, LIT-0006, LIT-0036.
- Status: documentado

### CT-P2 — FlyWire/FAFB
- Como o rótulo foi produzido: hierarquia de classes, tipos e hemilinagens, combinando NBLAST, CBLAST, co-clustering entre datasets e revisão manual; versão 2.1.0 reportada em Schlegel 2024 e versão 3.0.0 com comparação ao MaleCNS (LIT-0002, LIT-0038).
- Fonte: LIT-0002, LIT-0038.
- Status: documentado

### CT-P3 — conectomas masculinos e BANC/MANC
- Como o rótulo foi produzido: reconstruções prova de leitura com anotação manual e curadoria, tipagem por morfologia e conectividade, matching entre datasets e uso de marcadores de dimorfismo (fruitless/doublesex); BANC inclui anotações de função celular curadas (LIT-0019, LIT-0023, LIT-0014, LIT-0015, LIT-0010).
- Fonte: LIT-0010, LIT-0014, LIT-0015, LIT-0019, LIT-0023.
- Status: documentado

### CT-P4 — regiões e nomenclatura
- Como o rótulo foi produzido: consórcio de nomenclatura definiu hierarquia de neuropilas com fronteiras baseadas em marcadores sinápticos (anti-Bruchpilot, anti-Synapsin) e mapas 3D de referência (LIT-0037).
- Fonte: LIT-0037.
- Status: documentado

## 4. Síntese e validade

- Evidência a favor: conectividade isolada carrega sinal de tipo dentro de um
  indivíduo (LIT-0006, LIT-0033, LIT-0036); morfologia também carrega sinal
  (LIT-0026, LIT-0027); as duas modalidades se complementam em ablações
  supervisionadas no hemibrain (queda de 36% sem esqueleto e 6% sem conectoma,
  LIT-0035); neurotransmissor é previsível de EM (LIT-0034).
- Evidência contra: 32% dos tipos do hemibrain não foram reidentificados no
  FlyWire e apenas 14% dos tipos de conectividade o foram (LIT-0002); parte dos
  rótulos foi construída a partir de conectividade e morfologia, o que exige
  auditoria de circularidade (LIT-0002, RSK-004); informações mútuas baixas entre
  conectividade e outras classificações indicam que uma modalidade não substitui
  a outra (LIT-0033).
- Condições de validade para o projeto: (i) rótulos só valem após harmonização e
  aprovação humana (C03); (ii) cada modalidade tem trilho e baseline próprios
  (ESCOPO); (iii) correlação dentro de um indivíduo não prova transferência; (iv)
  cobertura, denominadores e tipos excluídos são reportados; (v) rótulos
  derivados de conectividade entram na auditoria de circularidade (C05 e D08).

## 5. Limitações

- Revisão documental; nenhum dado foi baixado nem métrica reproduzida.
- Busca limitada às consultas Q3 e Q6 do protocolo, complementada por
  referências cruzadas das fontes primárias.
- Classificações de função e região são anotações de contexto, não desfechos do
  projeto (GLO-07 e C03).
- Validação: `python3 tools/validate_research.py`.
