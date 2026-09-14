# Pacote de handoff ao custodiante (R08)

Preparado em 2026-09-14. Descreve o que o custodiante recebe do executor e como
conduz a avaliação selada sem expor rótulos por neurônio. Vale para o dry run
(R08) e é o molde operacional de H04/H07/M08.

## 1. O que o executor entrega

- `predictions.json` no schema `schemas/predictions.schema.json`: IDs opacos
  (`q<hex>` para consultas, `g<hex>` para galeria), top-10 com scores e flag
  `rejected`; nenhum label, nome de tipo ou ID cru.
- `RUN-MANIFEST` do congelamento (R04) com hashes do encoder, probe e
  transformações em `artifacts/frozen/`.
- Manifesto de proveniência de cada arquivo usado (R03) com release, licença,
  URL pública, data, bytes e SHA-256.
- Relatório de dry run (R08) quando aplicável.

## 2. O que o custodiante guarda

- `data/sealed/target-labels/` com o crosswalk avaliativo, tipos harmonizados e
  conjuntos known/unknown/ambíguo/excluído (H07), com hashes registrados.
- A chave opaca que liga `q<hex>`/`g<hex>` aos IDs reais; ela nunca volta ao
  executor.

## 3. Procedimento de avaliação (H04/M08)

1. Conferir os hashes do pacote de predições e do label set.
2. Rodar o avaliador no ambiente do custodiante, com firewall armado e sem
   rede: `python3 tools/evaluator_contract.py validate predictions <arquivo>`
   antes de pontuar.
3. Executar o avaliador uma única vez por chave lógica; registrar data, commit,
   hashes e assinatura do gate (G3/M08).
4. Devolver apenas `metrics.json` no schema `schemas/metrics.schema.json`:
   agregados, contagens, CIs e p-valores; nunca listas de acertos, exemplos ou
   IDs por neurônio.
5. Registrar qualquer incidente (reexecução divergente, acesso indevido) com
   horário, comando, arquivo e impacto; invalidar a análise correspondente.

## 4. Invariantes de segurança

- O executor nunca monta `data/sealed/`; o hook de auditoria barra `open`,
  `os.open`, `os.listdir` e `os.scandir` sob a raiz selada.
- Logs passam pelo filtro do firewall; caminho ou coluna proibidos falham.
- Reabrir tuning após o unseal transforma o alvo em validação; nova alegação
  confirmatória exige alvo reservado intocado.
- O pacote público contém apenas hashes dos labels, nunca seu conteúdo.

## 5. Validação

- `python3 tools/firewall.py scan` e `inventory` para conferir a zona.
- `python3 tools/validate_research.py` valida este pacote e o firewall.
