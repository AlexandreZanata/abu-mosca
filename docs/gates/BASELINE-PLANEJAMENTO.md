# Decisão do gate C00 — Baseline de planejamento

Registro de congelamento do baseline pedido por C00. Não é um gate científico
`G*`: não aprova hipótese, dataset, par fonte/alvo nem qualquer fase posterior.
Gates científicos só existem em `docs/gates/G*` e exigem revisão humana.

- Data/hora e fuso: 2026-09-14 08:13 -04
- Commit e estado dirty: commit H1 =
  `3e9863464078d80b588a55366a8ee3d8183bc13e`; árvore rastreável limpa antes e
  depois do congelamento
- Revisores: executor IA (opencode, modelo deepseek-v4.1-flash) — C00 tem
  orçamento "IA baixa", sem revisão humana obrigatória
- Decisão: `BASELINE CONGELADO` (registro de baseline; não é `GO`/`NO-GO`)

## Critérios

- 81 microfases e 9 gates: `PASS` — `python3 tools/validate_plan.py` conta 90
  itens (81 fases `C/L/D/R/H/B/M/S/P` + gates `G0`–`G8`).
- Seis campos por item: `PASS` — `Objetivo`, `Entregas`, `Aceite`, `Proibições`,
  `Dependências` e `Orçamento` presentes nos 90 itens.
- IDs e dependências resolvem: `PASS` — 331 referências expandidas apontam para
  IDs existentes no plano.
- Links atuais resolvem: `PASS` — 5 links Markdown, todos relativos, resolvidos
  em 12 arquivos; não há URLs externas no repositório.
- `.local/` fora do Git: `PASS` — `git check-ignore -v
  .local/PROMPT-CONTINUAR.md` aponta `.gitignore:2:.local/`; o arquivo existe.
- Dados e runs ignorados: `PASS` — `git check-ignore -v data/raw/x runs/y
  artifacts/z` aponta `/data/*`, `/runs/` e `/artifacts/*`.
- `git diff --check`: `PASS` após normalizar a linha em branco final de 6
  documentos preexistentes (correção apenas de whitespace).
- Status rastreável limpo após o commit: `PASS` — `git status --porcelain`
  vazio, com `.local/` ignorado.

## Riscos e divergências

- Evidência conflitante: nenhuma; o baseline não contém claim científico.
- Leakage/circularidade: não aplicável nesta fase; nenhum dado foi lido.
- Limites biológicos/estatísticos: nenhum teste empírico foi executado.
- Limites de hardware/licença: sem GPU, sem download, sem licença consultada.
- Limitação: a validação é estrutural (contagem, campos, links internos,
  ignore e whitespace) e não julga o conteúdo científico de cada microfase.
- Limitação do registro: como o hash de um commit não pode constar do próprio
  conteúdo, a evidência C00 e este documento registram H1, o commit que criou o
  congelamento; o amend que inseriu esses hashes é o commit de topo
  (`git log -1`), reportado na mensagem final da sessão.

## Escopo liberado

- Próximas microfases autorizadas: C01 (dependência C00 satisfeita).
- Trilhos explicitamente não autorizados: L01+, D01+, R01+, qualquer treino,
  download, unseal ou leitura de `data/sealed/`.
- Orçamento aprovado: IA baixa; sem GPU; sessão curta.

## Assinaturas

- Responsável científico: pendente — nenhum gate científico foi avaliado.
- Custodiante do alvo, quando aplicável: não designado.
- Revisor de método/estatística: não aplicável.
