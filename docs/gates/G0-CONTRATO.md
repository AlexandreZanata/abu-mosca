# Decisão do gate G0 — Contrato científico provisório

Pacote preparado pela IA executora; **nenhum critério científico foi aprovado
pela IA**. A decisão foi tomada pela revisão humana de método; o executor apenas
registrou o parecer.

- Data/hora e fuso: 2026-09-14 08:39 -04 (preparação); GO registrado em
  2026-09-14 08:42 -04
- Commit e estado dirty: preparação em HEAD `3f6934f`; registro em HEAD
  `859849e`, com modificações não relacionadas do programa NEXT (README,
  ESCOPO, MATRIZ, PROTOCOLO e templates/README) e arquivos NEXT não rastreados,
  todos preservados; o commit de registro do GO consta da evidência de G0 no
  plano
- Revisores: revisor humano / responsável científico — GO registrado em
  2026-09-14; nome não informado na mensagem de aprovação
- Decisão: GO (aprovada pela revisão humana em 2026-09-14; executor apenas
  registrou a decisão)

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
- Perguntas decididas em 2026-09-14: H0/H1, estimando e unidade de análise
  testáveis; equivalência aceita; desfechos e falsificação adequados; escada de
  claims conservadora aprovada; nenhuma divergência metodológica bloqueante
  identificada.

## Critérios

- C01 registros auditáveis (glossário, claims, riscos): `PASS` — validador
  `tools/validate_research.py` confirma 14 termos, 15 claims e 16 riscos.
- C02 pergunta, estimando e unidade de análise: `PASS` — aprovado pela revisão
  humana em 2026-09-14; separação entre datasets observados e população de
  moscas aceita.
- C03 equivalência e hierarquia: `PASS` — DEC-EQ-01 a DEC-EQ-09 aprovadas pelo
  revisor humano em 2026-09-14 (`EQUIVALENCIA.md` § 9).
- C04 desfechos, sucesso e falsificação: `PASS` — aprovado pela revisão humana
  em 2026-09-14.
- C05 ameaças à validade e leakage: `PASS` — tratamento aprovado em 2026-09-14;
  riscos seguem abertos e não mitigados sem testes e artefatos.
- C06 escada de claims e saídas negativas: `PASS` — aprovado pela revisão humana
  em 2026-09-14.
- Integridade estrutural das entregas: `PASS` — validador cobre registros,
  documentos e gate; 55 caminhos citados e 65 referências de fase resolvidas.
- Firewall do alvo e uso permitido: `PASS` — firewall aprovado em 2026-09-14;
  implementação e testes antileakage permanecem obrigatórios em R05.
- Nenhum dado externo ou rótulo do alvo consultado: `PASS` — evidências de
  C01–C06 registram apenas documentos internos e nenhum unseal.

## Riscos e divergências

- Divergência metodológica: nenhuma bloqueante; o revisor humano não identificou
  divergência que impeça o avanço para L01.
- Evidência conflitante: nenhuma até o momento; literatura e datasets ainda não
  auditados (L01–L07 e D01–D10 dependem de G1 e G2).
- Leakage/circularidade: modelados em C05; nenhum teste executado, todos os
  riscos seguem `aberto`/`não verificado`.
- Limites biológicos/estatísticos: um fonte e um alvo no MVP; nenhuma
  generalização populacional; SESOI de 5 pp é provisório e será revisado em R07.
- Limites de hardware/licença: nenhum download ou licença avaliada; teto de
  VRAM/RAM documentado apenas como restrição de engenharia.
- Pendências declaradas: crosswalk concreto (D08), par fonte/alvo (G2), números
  finais de SESOI/K/seeds (R07) e revisão de severidades (D01–D10).

## Condições do GO

- Auditar literatura, datasets, licenças, cobertura e comparabilidade antes de
  qualquer uso confirmatório.
- Definir em R07 os valores finais de SESOI, K, número de seeds, exclusões e
  análises.
- Implementar e testar o firewall e os controles antileakage em R05.
- Aprovar o pré-registro e o firewall em G3.
- Manter métricas, limiares, crosswalk e artefatos congelados antes do unseal.
- Classificar como `inconclusivo`, `parcial` ou `refutado` todo resultado que não
  satisfaça integralmente as condições pré-fixadas, sem trocar o desfecho depois
  de observar o alvo.

## Escopo liberado

- Próximas microfases autorizadas: L01 e demais microfases do Nível 0 conforme
  suas dependências (L01–L07, D01–D10), sempre respeitando G1 e G2.
- Trilhos explicitamente não autorizados pelo GO: qualquer download, treinamento,
  acesso a `data/sealed/` ou unseal; R01+ só após G1–G3 conforme dependências.
- Orçamento aprovado: IA baixa por microfase; sem GPU; nenhum download ou serviço
  autorizado por este gate.

## Assinaturas

- Responsável científico: GO registrado em 2026-09-14; nome do responsável não
  informado na aprovação (preencher quando disponível)
- Custodiante do alvo, quando aplicável: não designado; designação aplicável
  apenas antes do unseal (R05 e G3)
- Revisor de método/estatística: revisão registrada em 2026-09-14 pelo mesmo
  revisor humano
