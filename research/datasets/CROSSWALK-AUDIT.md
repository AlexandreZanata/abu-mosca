# Auditoria de ontologias, crosswalks e independência de rótulos (pacote para dupla revisão humana)

Preparado em 2026-09-14 (D08) pela IA executora. **Nenhuma regra foi aprovada**:
todas as decisões aguardam dupla revisão humana. Este documento é público e
contém apenas método, proveniência e agregados; qualquer mapping exato
necessário fica somente na zona selada `data/sealed/target-labels/`, sob
custódia. O executor de treino não recebe mapping exato nem associação por
neurônio do alvo.

## 1. Estado e escopo

- Objetivo: saber se “mesmo tipo” pode ser pontuado sem circularidade indevida.
- Entradas: cards auditados em D02–D07 e decisões de equivalência aprovadas em
  C03 (`docs/research/EQUIVALENCIA.md`).
- Regra geral: toda regra de mapeamento aponta para fonte primária; mapeamento
  manual exige dois revisores; rótulos derivados de conectividade ou do próprio
  matching ficam sinalizados para análise de sensibilidade ou exclusão.
- Nenhum dataset foi baixado e nenhum mapping foi gerado nesta fase.

## 2. Método de auditoria

1. Inventariar a ontologia de cada release com a fonte já registrada no card.
2. Classificar a proveniência do rótulo: literatura, morfologia, conectividade,
   multimodal ou matching.
3. Verificar se o rótulo depende do mesmo sinal que o modelo avalia; se
   depender, sinalizar para sensibilidade ou exclusão (GLO-10 e RSK-005).
4. Propor interseção (tipos presentes nos dois lados), conjunto conhecido
   (classes pontuáveis) e open-set (tipos exclusivos de um lado).
5. Exigir dois revisores humanos para qualquer correspondência manual;
   divergências vão para o gate G2/G4.
6. Registrar decisões, riscos e limitações sem expor IDs ou neurônios do alvo.

## 3. Proposta por par (somente agregados)

### PAIR-01 — FlyWire/FAFB ↔ hemibrain
- Par: conectomas de cérebro central sobrepostos; mesmo indivíduo? não.
- Interseção proposta: tipos do hemibrain reidentificados no FlyWire via
  NBLAST/co-conectividade, já computados na literatura (LIT-0002).
- Known/open-set: known = tipos consensuais; open-set = tipos exclusivos de cada
  cérebro e tipos não reprodutíveis entre indivíduos.
- Independência do rótulo: parcial — a tipagem do hemibrain usou morfologia e
  conectividade (LIT-0002), sinalizando circularidade parcial.
- Fontes: LIT-0002, LIT-0006, LIT-0038.
- Risco de circularidade: alto para tipos definidos por conectividade; mitigar
  com análise de sensibilidade ou exclusão de tipos derivados.
- Status: aguardando dupla revisão humana

### PAIR-02 — FlyWire/FAFB ↔ MCNS
- Par: cérebro de fêmea (FlyWire) e de macho (MCNS); indivíduos distintos.
- Interseção proposta: tipos isomórficos e dimórficos já anotados nas anotações
  FlyWire v3.0.0/v3.1.0 com o MaleCNS (LIT-0038).
- Known/open-set: known = tipos isomórficos e dimórficos; open-set = tipos
  específicos de sexo de cada lado.
- Independência do rótulo: parcial — rótulos de dimorfismo derivam de matching
  e expressão gênica (LIT-0023, LIT-0038).
- Fontes: LIT-0023, LIT-0038.
- Risco de circularidade: médio; sinalizar classes cujo rótulo dependa do
  próprio matching.
- Status: aguardando dupla revisão humana

### PAIR-03 — MCNS ↔ MAOL
- Par: mesmo espécime; MAOL é a região do lobo óptico direito do volume MCNS.
- Interseção proposta: todos os tipos do MAOL existem no MCNS; a relação é de
  subconjunto anatômico, não de correspondência entre indivíduos (LIT-0019,
  LIT-0023).
- Known/open-set: known = tipos do MAOL dentro do MCNS; open-set = classes do
  MCNS fora do lobo óptico.
- Independência do rótulo: não aplicável a transferência entre indivíduos; usar
  apenas para checagem interna.
- Fontes: LIT-0019, LIT-0023, LIT-0078.
- Risco de circularidade: baixo para anatomia, alto se o par for tratado como
  cross-individual; proibido no MVP.
- Status: aguardando dupla revisão humana

### PAIR-04 — MCNS ↔ MANC
- Par: VNC do MCNS e VNC do MANC; indivíduos distintos e sexo masculino em
  ambos.
- Interseção proposta: comparação por tipos correspondentes documentada nas
  anotações FlyWire v3.x (campo `supertype` ligado ao male-cns) e no depósito
  BANC (NBLAST), com fontes a confirmar em revisão (LIT-0038, LIT-0010).
- Known/open-set: known = tipos correspondentes; open-set = tipos exclusivos de
  cada espécime.
- Independência do rótulo: média; rótulos vêm de anotação manual com
  conectividade e morfologia.
- Fontes: LIT-0038, LIT-0015, LIT-0079.
- Risco de circularidade: médio; exigir dois revisores para o mapeamento manual.
- Status: aguardando dupla revisão humana

### PAIR-05 — MANC ↔ BANC
- Par: VNC de macho (MANC) e VNC de fêmea (BANC); indivíduos e sexos distintos.
- Interseção proposta: alinhamento topológico BANC–MANC já publicado como
  preprint (LIT-0060) e matrizes NBLAST no depósito BANC (LIT-0010).
- Known/open-set: known = tipos isomórficos/dimórficos segundo o preprint;
  open-set = tipos específicos de sexo.
- Independência do rótulo: parcial — o alinhamento usa a própria conectividade;
  sinalizar para sensibilidade.
- Fontes: LIT-0060, LIT-0010, LIT-0015.
- Risco de circularidade: alto se o matching for usado como feature; proibido
  no input.
- Status: aguardando dupla revisão humana

### PAIR-06 — BANC ↔ FlyWire/FAFB
- Par: CNS feminino completo (BANC) e cérebro feminino (FlyWire); indivíduos
  distintos.
- Interseção proposta: matrizes NBLAST BANC–FAFB no depósito BANC (LIT-0010);
  correspondência exata não verificada nesta auditoria.
- Known/open-set: known = tipos correspondentes que a revisão aceitar; open-set
  = tipos exclusivos de cada volume (VNC vs cérebro).
- Independência do rótulo: parcial; depende do matching morfológico.
- Fontes: LIT-0010, LIT-0002.
- Risco de circularidade: médio; exigir dois revisores e sensibilidade.
- Status: aguardando dupla revisão humana

### PAIR-07 — BANC ↔ MCNS
- Par: CNSs completos de fêmea e de macho; indivíduos distintos.
- Interseção proposta: tipos isomórficos/dimórficos conforme anotações
  cruzadas BANC–maleCNS descritas no depósito BANC (LIT-0010) e no MCNS
  (LIT-0078).
- Known/open-set: known = isomórficos; open-set = específicos de sexo.
- Independência do rótulo: média; anotação manual com conectividade.
- Fontes: LIT-0010, LIT-0078.
- Risco de circularidade: médio; sensibilidade para tipos derivados.
- Status: aguardando dupla revisão humana

## 4. Sinalização de rótulos derivados

- Tipos do hemibrain e do FlyWire foram construídos com morfologia e
  conectividade (LIT-0002): sinalizados para sensibilidade/exclusão.
- Tipos do BANC, MANC e MCNS combinam curadoria manual com conectividade e
  morfologia (LIT-0015, LIT-0023): sinalizados.
- Neurotransmissor é predição (LIT-0034) e entra apenas como atributo do
  Experimento B, nunca como rótulo avaliativo.
- Rótulos obtidos do próprio matching (NBLAST, alinhamento topológico) não
  podem entrar como feature nem como rótulo de treino.

## 5. Regras de selagem e acesso

- Mapping exato, quando necessário, fica somente na zona selada
  `data/sealed/target-labels/`, acessível apenas ao custodiante/avaliador.
- O documento público expõe apenas contagens agregadas por par; nenhuma
  associação por neurônio do alvo é publicada ou entregue ao executor.
- Mapeamentos manuais exigem dois revisores; discordâncias são registradas e
  escaladas para decisão humana.

## 6. Decisões pendentes

### DEC-CW-01 — Aprovar o método de auditoria
- Decisão: aceitar os seis passos da seção 2?
- Opções: (a) aceitar; (b) reformular.
- Recomendação: (a).
- Status: aguardando dupla revisão humana

### DEC-CW-02 — Aprovar as propostas por par
- Decisão: aceitar as interseções/known/open-set propostas para PAIR-01 a
  PAIR-07?
- Opções: (a) aceitar; (b) ajustar pares.
- Recomendação: (a), com confirmação de fontes por dois revisores.
- Status: aguardando dupla revisão humana

### DEC-CW-03 — Regra de rótulos derivados
- Decisão: aceitar a sinalização e as regras de sensibilidade/exclusão da
  seção 4?
- Opções: (a) aceitar; (b) endurecer exclusões.
- Recomendação: (a), com registro por tipo.
- Status: aguardando dupla revisão humana

### DEC-CW-04 — Selagem e acesso
- Decisão: confirmar que o mapping exato permanece apenas na zona selada e
  fora do alcance do executor?
- Opções: (a) confirmar; (b) ajustar fluxo.
- Recomendação: (a), conforme C03 e PROTOCOLO.
- Status: aguardando dupla revisão humana

## 7. Limitações

- Propostas baseadas apenas em fontes públicas já registradas; nenhum dado foi
  baixado e nenhum mapping exato foi criado.
- A interseção real depende de releases concretas e de harmonização aprovada;
  números por classe entram em D09/D10 após a revisão.
- Sem dupla revisão humana, a fase permanece `[ ]` e nenhuma correspondência
  pode ser usada em treino ou avaliação.
- Validação: `python3 tools/validate_research.py`.
