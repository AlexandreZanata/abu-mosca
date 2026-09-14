# Gestão de dados, retenção e material selado (R01)

Política preparada em 2026-09-14 (R01), após o `GO` do G2. Ela separa código,
manifestos, dados, runs, documentos e material selado antes de qualquer download
integral. Dados brutos, rótulos do alvo, tokens e checkpoints **nunca entram no
Git**; o teste `python3 tools/check_data_hygiene.py` prova isso com sentinelas.
Nenhum dado selado foi lido para escrever este documento.

## 1. Princípios e fonte de verdade

- O Git contém código, documentação, configurações, manifestos e resultados
  agregados reproduzíveis; não contém dados brutos nem material restrito.
- Fonte de verdade de cada dataset é o **raw imutável** identificado por
  release, URL e checksum (`data/raw/source/`, `data/raw/target-public/`).
- Snapshots canônicos são **derivados regeneráveis**: recalculados a partir do
  raw por código + configuração + seed, nunca editados à mão.
- Material selado (`data/sealed/target-labels/`) é fonte de verdade do alvo
  apenas para o custodiante; o executor não o lê em nenhuma fase.
- Artefatos congelados (`artifacts/frozen/`) são somente leitura depois do
  congelamento; rewrites exigem novo identificador e registro de incidente.

## 2. Layout de zonas e diretórios

- `data/raw/source/` — grafo e metadados permitidos da fonte (MANC `v1.2.1`);
  retido até o fim do projeto ou limpeza registrada.
- `data/raw/target-public/` — grafo e features públicos do alvo (MCNS
  `v1.0`); usado somente em inferência conforme o pré-registro.
- `data/raw/spikes/` — amostras mínimas medidas em D09 (226 MB, regeneráveis);
  podem ser removidas após H08 e registro de hashes.
- `data/sealed/target-labels/` — tipos, rótulos e crosswalk avaliativo; custódia
  separada do executor; nunca versionado.
- `data/manifests/` — manifestos versionados (URL, release, licença, data,
  bytes, MD5 oficial e SHA-256 calculado), sem tokens ou URL assinada.
- `artifacts/reports/` — relatórios agregados versionados, sem IDs por neurônio.
- `artifacts/frozen/` — encoder, probe, transformações e hashes congelados;
  ignorado pelo Git.
- `runs/`, `checkpoints/`, `outputs/` — execuções e saídas regeneráveis;
  ignorados pelo Git e nunca usados como fonte de verdade.

## 3. Releases, checksums e manifestos

- Toda entrada registra: dataset, release/materialização, URL primária, data de
  acesso, licença, bytes e checksum.
- Usar MD5 oficial quando a fonte publicar; sempre calcular SHA-256 local e
  registrá-lo (D09 fez isso para 6 amostras; o MCNS não publica checksum).
- O schema de manifestos e o download idempotente serão formalizados em R03;
  até lá, os registros vivem em `research/datasets/RECURSOS.md` e nos cards.
- Divergência de tamanho, checksum ou contagem bloqueia o uso do arquivo e
  abre incidente registrado; nunca "corrigir" dado bruto in-place.

## 4. Retenção, backup e limpeza

- Raw e snapshots: retidos enquanto o experimento estiver ativo; decisão final
  de retenção no encerramento (G8).
- Backup: documentação e manifestos pelo Git; dados grandes e material selado
  exigem armazenamento externo, ainda **não designado** (limitação registrada
  no G2 e a resolver antes de H08).
- Procedimento de limpeza: (1) identificar o alvo; (2) registrar origem, bytes
  e hash; (3) confirmar que é regenerável ou obter aprovação do custodiante
  quando for dado selado ou único; (4) remover; (5) rodar o teste de higiene e
  conferir `git status` limpo.
- Amostras de D09 podem ser removidas após o registro de hashes; `data/sealed`
  nunca é limpo sem o custodiante.

## 5. Licenças e redistribuição

| Dataset | Licença declarada | Regra de uso/redistribuição |
|---|---|---|
| MANC `v1.2.1` | CC BY 4.0 (LIT-0074) | uso e derivados com atribuição; brutos fora do Git |
| MCNS `v1.0` | CC BY 4.0 (LIT-0078, LIT-0079) | uso e derivados com atribuição; sem checksum oficial |
| BANC `v888` | CC BY 4.0 no depósito, 277/379 arquivos restritos (LIT-0010) | apenas arquivos liberados; restritos exigem pedido |
| FlyWire `v783` | grafo CC BY 4.0; anotações sem licença declarada (LIT-0001) | grafo público; anotações com redistribuição não confirmada |
| hemibrain `v1.2.1` | CC BY 4.0 (LIT-0070) | comparador; export sem checksum oficial |
| MAOL `optic-lobe:v1.1` | CC BY 4.0 (LIT-0076) | uso interno; proibido como par cross-individual do MCNS |

- Nenhum dado bruto é redistribuído pelo repositório; derivados publicáveis
  exigem atribuição e revisão de licença em P07.
- Anotações com licença não confirmada não são redistribuídas; permanecem no
  ambiente local ou seladas.

## 6. Dados regeneráveis e não regeneráveis

- Regeneráveis: snapshots canônicos, amostras de spike, embeddings derivados de
  pesos congelados, relatórios agregados.
- Não regeneráveis: rótulos selados, crosswalk avaliativo e decisões de
  curadoria; por isso têm hash registrado e backup custodiado fora do Git.
- Regenerar um snapshot exige o mesmo raw + configuração; cache só é reusado
  quando o checksum de entrada, o código e a configuração coincidem.

## 7. Dados selados e firewall do alvo

- Zonas do PROTOCOLO: fonte, alvo-público, selado e congelado; o executor nunca
  lê `data/sealed/` nem recebe rótulos por neurônio.
- O primeiro unseal exige registro de data, commit, checksums e assinatura do
  gate (G3); avaliação roda em sessão separada do executor.
- Logs, nomes de arquivo e mensagens de erro nunca contêm tipo, label ou
  associação do alvo; IDs do alvo são opacos no material público.
- Reabrir tuning após o unseal transforma o alvo em validação e exige novo
  alvo para qualquer alegação confirmatória.

## 8. Segredos e credenciais

- Tokens ficam apenas em `.env` local (ignorado pelo Git) ou variável de
  ambiente; `*.token` e `tokens/` também são ignorados.
- Manifestos registram URL pública, nunca URL assinada, token ou credencial.
- Nenhum cadastro, compra ou contato externo é feito por IA sem autorização
  humana explícita.

## 9. Teste automatizado de higiene

- `python3 tools/check_data_hygiene.py` cria 11 sentinelas sensíveis (dados,
  selados, runs, checkpoints, frozen, `.env`, tokens), confirma que o Git as
  ignora, confirma que `data/README.md`, `data/manifests/` e
  `artifacts/reports/` continuam rastreáveis, verifica os 10 diretórios de
  layout e remove os resíduos.
- O teste deve rodar antes de commits que toquem dados, e sempre que o
  `.gitignore` mudar.

## 10. Limitações

- Armazenamento externo e backup ainda não designados; o disco local tem 34 GB
  livres e não comporta BANC (17,15 GB) mais MCNS (31,32 GB) completos.
- R03 formalizará schema de manifestos e download idempotente; até lá os
  registros são manuais e verificáveis.
- A política cobre o Nível 1; retenção e destinação final serão reconciliadas
  no G8.
- Validação: `python3 tools/validate_research.py`.
