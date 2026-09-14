# Contrato canônico do grafo e fixture sintética (H01)

Especificado em 2026-09-14. Define como todos os connectomas entram no projeto
sem apagar diferenças relevantes: tipos, unidades, constraints, multiedges,
self-loops, zero/NaN, threshold, agregação, proveniência e missingness. O
contrato versionado está em `schemas/graph.schema.json`; o validador e o
round-trip ficam em `tools/graph_contract.py`; a fixture dirigida/ponderada em
`tests/fixtures/graph-fixture.json`.

## 1. Princípios

- Um grafo canônico descreve **um** dataset/release; nada é fundido entre
  datasets neste contrato.
- Diferenças relevantes (direção, peso, atributos existentes, missingness,
  threshold aplicado) são explicitamente declaradas; nenhum campo “comum” é
  inventado para dataset que não o possui.
- IDs no contrato são opacos (`n<16 hex>`); o mapeamento para IDs reais do
  dataset é responsabilidade do adapter e nunca aparece como feature.

## 2. Nodes

- `id`: opaco, único, `^n[0-9a-f]{16}$`.
- `attributes`: objeto de atributos tipados permitidos (ex.: graus calculados);
  ausente de dados ⇒ a chave entra em `missing`, nunca vira 0 ou sentinela.
- `missing`: lista explícita de chaves sem valor; `null` só é válido se a chave
  estiver em `missing`.

## 3. Edges

- `source` e `target`: IDs de node existentes; a direção é sempre
  `source → target` e o grafo declara `directed`.
- `weight`: inteiro ≥ 0 (unidade declarada em `graph.weight_units`, por padrão
  contagem de sinapses); `NaN`/`Inf` são proibidos pelo schema; peso zero é
  válido e **preservado** (não é descartado silenciosamente).
- `attributes`/`missing`: mesma regra dos nodes para atributos de aresta.
- Multiedges: permitidas; a agregação é declarada em `graph.aggregation`:
  - `none`: multiedges permanecem separadas;
  - `sum`: a soma por par `(source,target)` é aplicada pelo adapter e a
    conservação do total de peso é verificável (o round-trip não agrega).
- Self-loops: permitidos apenas quando `allow_self_loops = true`; caso
  contrário o grafo é inválido (nunca removidos em silêncio).

## 4. Grafo e agregados

- `directed`: os datasets atuais são dirigidos; datasets não dirigidos exigem
  flag `false` e não podem ser simetrizados sem decisão explícita.
- `weighted`: quando `false`, `weight` é `null` e `weight_units` é `null`.
- `threshold`: `{weight_min, rule}` registra o corte aplicado pelo adapter
  (`keep` = nenhum; `drop_below` = remove arestas com peso < `weight_min`);
  o contrato não aplica threshold por conta própria e o corte usado fica na
  proveniência.
- Agregação e threshold **não** alteram a identidade dos nodes.

## 5. Proveniência

Obrigatória: `dataset`, `release`, `license`, `source_files` (path + SHA-256),
`adapter` (nome, versão, `config_sha256`) e `created_at`. Sem isso o grafo não é
considerado canônico.

## 6. Missingness

- Sem sentinelas: `-1`, `NaN`, `""` ou `0` não representam ausência.
- Ausência é explícita via `missing`; o consumidor decide a imputação fora do
  contrato, com máscara.
- `missing` é preservado no round-trip e não pode ser preenchido por padrão.

## 7. Round-trip

`python3 tools/graph_contract.py roundtrip tests/fixtures/graph-fixture.json`
valida a fixture, serializa em JSON canônico (chaves ordenadas) e verifica que
recarregar produce exatamente o mesmo conteúdo; qualquer perda de campo,
reordenação instável ou colapso de multiedge falha o teste.

## 8. Constraints e validação

- IDs únicos; arestas referenciam nodes existentes.
- Tipos e unidades conferidos; peso inteiro; JSON rejeita `NaN`.
- `missing` não pode conter chave existente em `attributes`.
- `sum` com multiedges preserva o total; `none` mantém cardinalidade.
- Fixture cobre: multiedge, self-loop permitido, peso zero, atributo ausente e
  proveniência completa.

## 9. Limitações

- O contrato cobre o Nível 1 (topologia dirigida e ponderada); atributos de
  região/neurotransmissor entram no Experimento B como chaves opcionais, sem
  alterar o núcleo.
- A conversão de cada dataset é responsabilidade dos adapters H02/H03, que
  devem registrar `adapter.config_sha256` e conferir contagens oficiais.
- Validação: `python3 tools/validate_research.py`.
