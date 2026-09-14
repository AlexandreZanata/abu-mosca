# Decisão do gate G4 — dados analíticos (modo exploratório)

Pacote preparado pela IA executora em 2026-09-14 14:01 -04; **nenhum critério
científico foi aprovado pela IA**. A decisão `GO`, `NO-GO` ou `REFORMULAR`
pertence ao responsável científico, ao custodiante e ao revisor de método. O
dataset analítico é público, sem rótulos, e está congelado em modo
**estritamente exploratório** porque o desfecho confirmatório ficou
**inconclusivo por circularidade** (H07; changelog 2.3).

- Data/hora e fuso: 2026-09-14 14:01 -04
- Commit e estado dirty: preparação sobre HEAD `0c8ade2`; modificações não
  relacionadas do workstream NEXT preservadas fora do commit
- Revisores: a preencher (científico, custodiante e método/estatística)
- Decisão: AGUARDAR (pacote preparado; nenhuma decisão tomada pela IA)

## Pacote de revisão

- Congelamento: `data/manifests/analitico-v1.json` — status `exploratory-only`,
  `labels_used: false`, desfecho confirmatório inexistente, hash analítico
  `5c7b96bd4939e285e5fd41d80a1012d686b69c608d627f47a1ee17dd746f9737`.
- Snapshots canônicos: fonte MANC (23.188 nodes, 5.243.574 arestas, peso
  30.698.527) e alvo público MCNS nível-neurônio (211.577 nodes, 26.028.386
  arestas, peso 125.365.933), em `runs/h08/` (fora do Git).
- Qualidade: `artifacts/reports/DATA-QUALITY.md` e `.json` — duplicatas 0,
  graus conferidos (divergência 0), pesos não negativos, drift de schema 0,
  componentes, isolados, self-loops e reciprocidade medidos.
- Desvios aceitos/documentados: nível do alvo (segmento→neurônio; 125.828.298
  arestas descartadas), 22.799 bodies anotados isolados no subgrafo, contagens
  publicadas reconciliadas, sem desfecho confirmatório, revisor único.
- Segurança: firewall R05 ativo; nenhum label, crosswalk ou arquivo selado foi
  lido; snapshots contêm apenas topologia pública.
- Perguntas a decidir: aprovar o dataset analítico em modo exploratório?
  confirmar separação (custodiante) e cobertura/validade (científico)? aceitar
  os desvios listados? liberar B01–B09 apenas como exploração, sem claims
  confirmatórios?

## Artefatos e hashes

- SHA-256 `d4175fe78a0b895accf7400b54203ec90880287ff4b935d0a5c32bae2603732f` — `data/manifests/analitico-v1.json`
- SHA-256 `5c14e132a3c691ee27fa439a2853dd64c6543a1966b01ce21116d3ac867fa33e` — `artifacts/reports/DATA-QUALITY.md`
- SHA-256 `367f01446e312ba80da445f86ed9abe0554caba33587aac96d9c613c47fd1b2a` — `artifacts/reports/DATA-QUALITY.json`
- SHA-256 `7bbd3f36bb4fda1348f14397490063c8c15118064452a9b186771824d6f439b6` — `artifacts/reports/H08-SNAPSHOTS.md`
- SHA-256 `73e0d507cbd7ad4e5f6143a34c276169bbe167e5da5b8767568471bbc7867bdf` — `artifacts/reports/H08-SNAPSHOTS.json`
- SHA-256 `c649a5a5763ac93de3e0ab83bcc32efd31ac5e5990d78cb12f58317e922253f7` — `preregistration/REGISTRY.md`
- SHA-256 `6a7d0c8f9c6ae27bd85241b00f3f361ea258caf1708d42d9600cf896e575fce7` — `preregistration/CHANGELOG.md`
- SHA-256 `8357d449c718a2ee2fb50b8fdda9eefcf664d4416dba19d31bec862e7c265cfb` — `docs/research/FIREWALL.md`

## Critérios

- Snapshot íntegro com checksums conferidos: `PASS` — quatro arquivos Parquet com hashes estáveis e hash analítico `5c7b96bd4939e285…`.
- Qualidade estrutural: `PASS` — duplicatas 0, pesos negativos 0, divergência de grau 0 e drift de schema 0 nos dois lados (H09).
- Isolamento de labels e selado: `PASS` — nenhum rótulo, crosswalk ou acesso a `data/sealed/`; manifesto com `labels_used: false`.
- Cobertura e reconciliação: `PASS` — contagens reconciliadas com H02/H03 e cards, com desvios listados e corrigidos quando técnicos (grau, determinismo).
- Desfecho confirmatório inexistente: `PASS` — T0 e hemilinhagem inconclusivos por circularidade (H07, changelog 2.3); dataset só exploratório.
- Pré-registro atualizado para alterações materiais: `PASS` — changelog 2.2/2.3 e H1′ corrigida antes de qualquer baseline.
- Custodiante confirma separação e integridade do selado: `NÃO VERIFICADO` — assinatura humana pendente.
- Responsável científico confirma cobertura/validade para uso exploratório: `NÃO VERIFICADO` — assinatura humana pendente.

## Riscos e divergências

- Sem desfecho confirmatório: qualquer baseline futuro é exploratório e não
  sustenta claim de transferência.
- 22.799 bodies isolados e 125,8M arestas descartadas exigem cuidado em
  estatísticas de grau e cobertura.
- Revisor único acumulando papéis (limitação declarada); segundo revisor
  indisponível.
- BANC/FlyWire não processados; nenhuma réplica biológica independente.

## Condições do G4

- Com `GO`: liberar B01–B09 apenas em modo exploratório, sobre o dataset
  congelado, sem unseal, sem rótulos-alvo e sem claims confirmatórios.
- Qualquer alteração material no dataset exige nova versão de manifesto e
  atualização do pré-registro antes de resultados.
- Dataset reprovado não pode ser “limpo” manualmente sem nova proveniência.

## Escopo liberado

- Próximas microfases autorizadas com `GO`: B01 e seguintes, na ordem do plano,
  como exploração.
- Trilhos não autorizados: unseal, leitura de `data/sealed/`, tuning no alvo,
  alegação confirmatória e publicação.
- Orçamento aprovado: IA baixa por microfase; CPU; sem GPU nesta etapa.

## Assinaturas

- Responsável científico: a preencher
- Custodiante dos dados: a preencher
- Revisor de método/estatística: a preencher
