# Decisão do gate G0 — Contrato científico provisório

Pacote preparado pela IA executora; **nenhum critério científico foi aprovado
pela IA**. A decisão exige revisão humana de método.

- Data/hora e fuso: 2026-09-14 08:39 -04
- Commit e estado dirty: HEAD `3f6934f`; árvore com modificações não relacionadas
  do programa NEXT (README, ESCOPO, MATRIZ, PROTOCOLO e templates/README)
  preservadas; nenhum arquivo deste gate commitado no momento da preparação
- Revisores: a preencher pela revisão humana (nenhum assinado pela IA)
- Decisão: AGUARDAR (pacote preparado; aprovação pendente de revisão humana)

## Pacote de revisão

- H0/H1 e estimando: `docs/ESCOPO-E-HIPOTESES.md` e
  `docs/research/PERGUNTA-E-ESTIMANDO.md` (C02).
- Equivalência e crosswalk: `docs/research/EQUIVALENCIA.md` (C03; decisões
  DEC-EQ-01 a DEC-EQ-09 já aprovadas pelo revisor humano em 2026-09-14).
- Desfechos e falsificação: `docs/research/DESFECHOS-E-FALSIFICACAO.md` (C04).
- Ameaças e leakage: `docs/research/AMEACAS-A-VALIDADE.md` (C05).
- Escada de claims e saídas negativas: `docs/research/ESCADA-DE-CLAIMS.md` e
  `docs/research/RELATORIO-INVIABILIDADE-ESQUELETO.md` (C06).
- Registros de apoio: `docs/research/GLOSSARIO.md`, `CLAIMS.md` e `RISCOS.md`
  (C01).
- Perguntas a decidir: H0/H1 são testáveis? a equivalência aprovada é aceita
  como contrato do gate? os desfechos e a falsificação são adequados? a escada
  de claims limita corretamente a linguagem? há divergência a registrar?

## Critérios

- C01 registros auditáveis (glossário, claims, riscos): `PASS` — validador
  `tools/validate_research.py` confirma 14 termos, 15 claims e 16 riscos.
- C02 pergunta, estimando e unidade de análise: `NÃO VERIFICADO` — aguarda
  revisão humana da separação entre datasets observados e população de moscas.
- C03 equivalência e hierarquia: `PASS` — DEC-EQ-01 a DEC-EQ-09 aprovadas pelo
  revisor humano em 2026-09-14 (`EQUIVALENCIA.md` § 9).
- C04 desfechos, sucesso e falsificação: `NÃO VERIFICADO` — aguarda revisão
  humana de métricas, SESOI provisório e árvore de decisão.
- C05 ameaças à validade e leakage: `NÃO VERIFICADO` — aguarda revisão humana de
  severidades, testes de detecção e riscos residuais.
- C06 escada de claims e saídas negativas: `NÃO VERIFICADO` — aguarda revisão
  humana dos níveis e da linguagem permitida.
- Integridade estrutural das entregas: `PASS` — validador com 9 grupos de
  checagens, 46 caminhos citados e 65 referências de fase resolvidas.
- Firewall do alvo e uso permitido: `NÃO VERIFICADO` — depende de leitura humana
  do protocolo e da futura execução de R05.
- Nenhum dado externo ou rótulo do alvo consultado: `PASS` — evidências de
  C01–C06 registram apenas documentos internos e nenhum unseal.

## Riscos e divergências

- Evidência conflitante: nenhuma até o momento; literatura e datasets ainda não
  auditados (L01+ e D01+ bloqueados até este gate).
- Leakage/circularidade: modelados em C05; nenhum teste executado, todos os
  riscos seguem `aberto`/`não verificado`.
- Limites biológicos/estatísticos: um fonte e um alvo no MVP; nenhuma
  generalização populacional; SESOI de 5 pp é provisório e será revisado em R07.
- Limites de hardware/licença: nenhum download ou licença avaliada; teto de
  VRAM/RAM documentado apenas como restrição de engenharia.
- Pendências declaradas: crosswalk concreto (D08), par fonte/alvo (G2), números
  finais de SESOI/K/seeds (R07) e revisão de severidades (D01–D10).

## Escopo liberado

- Próximas microfases autorizadas: nenhuma enquanto a decisão for `AGUARDAR`.
  Com `GO`, a primeira autorizada é L01 (revisão de literatura).
- Trilhos explicitamente não autorizados: L01+, D01+, R01+, qualquer download,
  treino, unseal ou leitura de `data/sealed/`.
- Orçamento aprovado: nenhum; a IA executora encerra após entregar o pacote.

## Assinaturas

- Responsável científico: A preencher pela revisão humana
- Custodiante do alvo, quando aplicável: A preencher pela revisão humana
- Revisor de método/estatística: A preencher pela revisão humana
