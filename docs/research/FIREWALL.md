# Firewall do alvo e antileakage (R05)

Implementado em 2026-09-14. Impede acesso acidental do executor aos labels do
alvo e ao crosswalk avaliativo: zonas separadas, permissões restritas, scanner
de referências, barreiras de runtime (auditoria de abertura e filtro de log),
inventário que só expõe hashes e testes que falham em qualquer tentativa
sentinela. O pipeline público roda com o firewall armado e sem montar o selado.

## 1. Zonas e princípios

- `data/raw/source/` e `data/raw/target-public/`: dados permitidos da fonte e do
  alvo público (grafo/features em inferência).
- `data/sealed/target-labels/`: rótulos do alvo, crosswalk avaliativo e
  correspondências; o executor **nunca** lê nem lista.
- `artifacts/frozen/`: encoder, probe e transformações congelados antes do
  unseal; somente leitura após o congelamento.
- Princípio: o executor de treino não recebe rótulo por neurônio; o avaliador
  (custodiante) recebe apenas o pacote congelado e devolve métricas agregadas.

## 2. Permissões e custódia

- `data/sealed/` e `data/sealed/target-labels/` estão com modo `700` (medido);
  qualquer conteúdo novo mantém essa restrição.
- Custódia: uma pessoa (custodiante) mantém a zona; em ambiente de usuário
  único, a separação é procedural e declarada como limitação — não é cegamento
  perfeito.
- O executor nunca cria, copia ou limpa arquivos no selado; limpeza exige
  aprovação do custodiante e registro de hash (R01).

## 3. Scanner de referências e dependências

- `python3 tools/firewall.py scan` percorre `tools/`, `configs/` e
  `environment/` procurando referências a caminhos proibidos
  (`data/sealed`, `target-labels`).
- Linhas legítimas (constantes e testes do próprio firewall ou validadores de
  contrato) usam a marca `firewall-allow`; sem a marca, a ocorrência é falha.
- O valor correspondente ao label real nunca entra em nomes de classe, cache ou
  dependência; colunas proibidas são definidas pelo schema selado em H07 e
  passadas ao filtro de log no momento da avaliação.

## 4. Barreiras de runtime

- `install_audit_firewall()` instala uma trilha de auditoria que bloqueia
  eventos `open`, `os.open`, `os.listdir` e `os.scandir` sob a raiz selada.
- `guarded_open(path)` é a abertura defensiva para qualquer leitura de dados;
  falha com `FirewallError` antes de tocar o arquivo.
- `FirewallLogFilter` falha se uma mensagem de log contiver caminho proibido ou
  coluna configurada como sensível; `redact_sealed_paths()` existe para
  mensagens que precisem ser normalizadas; logs de treino também passam pelo filtro.
- As barreiras são instaladas em subprocessos/avaliador; o hook de auditoria é
  permanente por processo, então não é instalado na sessão do executor.

## 5. Inventário selado: apenas hashes

- `python3 tools/firewall.py inventory` devolve `count`, `total_bytes`, `path`,
  `bytes` e `sha256` de cada arquivo selado — nunca o conteúdo.
- O pacote congelado compartilhável contém somente esses hashes; a leitura dos
  rótulos acontece apenas no ambiente do custodiante.
- Hoje o selado está vazio (`count = 0`); o inventário passará a ter conteúdo
  quando H07 materializar o crosswalk sob custódia.

## 6. Testes antileakage

- `tests/test_firewall.py` (7 casos) cobre: abertura guardada bloqueando o
  selado e liberando o público; filtro de log para caminho e coluna;
  inventário sem conteúdo; scanner detectando violação e respeitando a marca;
  repositório limpo; auditoria bloqueando abertura em subprocesso; e o
  **pipeline público rodando com o firewall armado** (`tools/run.py` completa a
  fixture sem tocar o selado).
- Suíte completa: 49 testes.

## 7. Procedimento de unseal e invalidação

1. Congelar encoder/probe/transformações em `artifacts/frozen/` com hashes
   (M06) e entregar o pacote por ID opaco.
2. O custodiante registra data, commit, checksums e a assinatura do gate (G3)
   antes do primeiro unseal; a avaliação roda em sessão separada do executor.
3. Após o unseal, qualquer tuning novo sobre o mesmo alvo torna o resultado
   exploratório; alegação confirmatória nova exige alvo reservado e intocado.
4. Incidente de acesso indevido: registrar horário, comando, arquivo e impacto;
   invalidar a análise correspondente e repetir com firewall reforçado.

## 8. Limitações

- Usuário único: permissões `700` e separação de sessões são procedurais, não
  isolamento de sistema operacional; revisão de segurança metodológica fica
  pendente para G3.
- O scanner cobre código e configuração versionados, não notebooks externos nem
  caches de terceiros; a auditoria de runtime cobre o que é executado.
- A lista de colunas proibidas depende do schema selado de H07; por ora o
  filtro recebe a lista explicitamente.
- Validação: `python3 tools/validate_research.py`.
