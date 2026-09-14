# Protocolo de revisão de literatura (pré-especificado)

Aberto em 2026-09-14 (L01) e liberado por G0 (`GO`). Este documento pré-especifica
bases, strings, período, idiomas, critérios de inclusão/exclusão, deduplicação,
esquema do ledger e fluxo de triagem. A execução ocorre em L02–L07; mudanças no
protocolo exigem versão, motivo e diff, sem reescrever buscas antigas.

## 1. Objetivo e perguntas

Tornar a busca repetível e menos suscetível a cherry-picking. Claims e questões a
decidir: CLM-007 (conectividade já recuperou tipos dentro de um connectoma) e
CLM-008 (baseline publicado de neuron matching reproduzível) em
`docs/research/CLAIMS.md`. Resultado final: mapa de lacuna e veredito provisório
de novidade (L07) e pacote do gate G1.

## 2. Bases e ferramentas

- Europe PMC (inclui registros MEDLINE/PubMed e preprints depositados).
- PubMed (NCBI), para conferência de vocabulário MeSH.
- arXiv (pré-prints de computação e métodos).
- bioRxiv (pré-prints de biologia; versões publicadas conferidas por DOI).
- Semantic Scholar (API, para citações e trabalhos relacionados).
- OpenAlex (metadados e descoberta por DOI/citação).
- Crossref (verificação de DOI e versão de registro).
- DBLP (ciência da computação; aprendizado de representação de grafos).
- Google Scholar apenas como descoberta complementar; todo achado precisa de
  verificação na fonte primária e registro no ledger.

Nenhum resultado de base é evidência por si só: snippet de buscador, blog e
resumo de IA servem apenas para descoberta (`docs/PROTOCOLO-EXECUCAO.md` §
Padrão mínimo de evidência externa).

## 3. Strings de busca

Sintaxe booleana genérica; cada base adapta campos e operadores, e a string
exata usada é registrada no log de consultas. Os sete blocos cobrem o aceite.

### Q1 — Neuron matching
- Objetivo: métodos de correspondência de neurônios entre reconstruções.
- String: `("neuron matching" OR "neuron correspondence" OR "cell matching" OR "neuron alignment") AND (connectome OR "electron microscopy" OR "neuronal reconstruction")`
- Bases: Europe PMC, PubMed, arXiv, Semantic Scholar, OpenAlex.
- Janela: W1.

### Q2 — Connectome alignment
- Objetivo: alinhamento/registro de connectomas e grafos neurais.
- String: `("connectome alignment" OR "connectome registration" OR "cross-connectome" OR ("graph alignment" AND neuron))`
- Bases: Europe PMC, arXiv, Semantic Scholar, OpenAlex, DBLP.
- Janela: W1.

### Q3 — Cell type por conectividade
- Objetivo: predição/classificação de tipo celular a partir de conectividade.
- String: `("cell type" OR "neuron type" OR "cell classification") AND (connectivity OR connectome OR "synaptic connectivity" OR wiring)`
- Bases: Europe PMC, PubMed, bioRxiv, Semantic Scholar.
- Janela: W1.

### Q4 — Graph representation learning
- Objetivo: aprendizado auto-supervisionado e embeddings de grafos aplicáveis.
- String: `("graph representation learning" OR "graph neural network" OR "node embedding" OR "graph embedding") AND ("self-supervised" OR unsupervised OR pretraining)`
- Bases: arXiv, DBLP, Semantic Scholar, OpenAlex.
- Janela: W2.

### Q5 — Cross-animal
- Objetivo: generalização entre animais, espécimes ou indivíduos.
- String: `(cross-animal OR cross-specimen OR "individual differences" OR "between animals") AND (connectome OR "neuron type" OR "cell type") AND (transfer OR generalization)`
- Bases: Europe PMC, PubMed, bioRxiv, Semantic Scholar.
- Janela: W2.

### Q6 — Morfologia
- Objetivo: morfologia celular associada a tipo neuronal.
- String: `(morphology OR neurite OR skeleton) AND ("neuron type" OR "cell type" OR "cell classification")`
- Bases: Europe PMC, PubMed, bioRxiv, Semantic Scholar.
- Janela: W2.

### Q7 — Embeddings de connectomas
- Objetivo: representações latentes de connectomas e wiring diagrams.
- String: `(connectome OR "wiring diagram") AND (embedding OR "latent representation" OR "representation learning")`
- Bases: Europe PMC, arXiv, Semantic Scholar, OpenAlex.
- Janela: W2.

## 4. Período e idiomas

- W1 (Q1–Q3): 1980-01-01 até a data de execução da busca, para alcançar
  métodos clássicos de matching e alinhamento.
- W2 (Q4–Q7): 2013-01-01 até a data de execução, cobrindo a literatura moderna
  de representação de grafos e aprendizado profundo.
- Idiomas: inglês. Trabalhos em outro idioma só entram com abstract em inglês e
  nota no ledger.
- A data/hora exata de cada busca é registrada no log de consultas.

## 5. Inclusão e exclusão

Incluir: artigos revisados por pares; pré-prints com DOI e versão (marcados como
`preprint`); métodos de matching/alinhamento de neurônios; classificação de tipo
por conectividade ou morfologia; aprendizado de representação de grafos
aplicável; estudos cross-animal com avaliação de generalização.

Excluir: retratações; registros sem método suficiente; duplicatas; evidência
baseada apenas em snippet, blog ou resumo de IA; textos inacessíveis (marcar
`pendente_fulltext`, não silenciar).

Exclusões nunca são usadas para esconder resultado negativo: o motivo fica no
ledger e os totais são reportados.

## 6. Deduplicação

- Normalizar DOI (minúsculas, sem prefixo de URL), arXiv ID e título
  (casefold, sem pontuação nem espaços múltiplos).
- Chave primária de deduplicação: DOI normalizado; na ausência, arXiv ID; na
  ausência, título normalizado + primeiro autor + ano.
- Versões preprint e publicada do mesmo trabalho são vinculadas
  (`versao_de`), mantendo o registro mais completo como principal; a contagem
  final conta o trabalho uma vez.

## 7. Esquema do ledger

Arquivo versionado em `research/literature/` (LEDGER.tsv, TSV, uma linha por
registro), com colunas:

`lit_id` (LIT-0001), `run_date`, `base`, `query_id` (Q1–Q7), `titulo`, `autores`,
`ano`, `venue`, `tipo` (`journal | conference | preprint | thesis | outro`),
`doi`, `url`, `versao`, `status_triagem`
(`triagem | incluido | excluido | pendente_fulltext`), `motivo_exclusao`,
`claims_relacionados` (IDs CLM e/ou GLO), `fase` (L02–L07), `nota`.

Log de consultas em `research/literature/` (QUERY-LOG.tsv):
`run_date`, `query_id`, `base`, `string_exata`, `filtros`, `periodo`, `idioma`,
`n_resultados`, `export_formato`, `hash_export` (SHA-256 do arquivo bruto),
`operador`, `observacoes`.

Exports brutos não entram no Git quando a licença não permitir; nesse caso
guardam-se apenas o hash e o log, e o motivo é registrado.

## 8. Triagem e extração

1. Executar as strings por base e exportar o resultado bruto; calcular o hash.
2. Deduplicar conforme a seção 6.
3. Triagem por título/abstract; cada exclusão recebe motivo no ledger.
4. Extração em texto completo: claim atômico, localização exata (seção/página),
   versão e data de acesso.
5. Segundo triador (ou revisor humano) confere uma amostra definida no início da
   execução; divergências são resolvidas por decisão humana registrada.
6. Contagens de triagem (incluídos, excluídos, pendentes) são reportadas no
   ledger consolidado.

## 9. Reprodutibilidade e atualização

- Um segundo executor repete a busca a partir do commit do protocolo, rodando
  Q1–Q7 nas bases listadas, com as janelas da seção 4, e compara o número de
  resultados e os hashes de export.
- Toda busca nova gera `run_date` novo; exports antigos não são sobrescritos.
- Mudança de string, base, janela ou critério exige nova versão deste protocolo
  com motivo, autor e diff, antes de valer para buscas futuras.
- A revisão é atualizável: L07 e S11 podem exigir nova passada; o veredito de
  novidade é sempre provisório.

## 10. Regras de evidência

- Fonte primária/oficial com DOI ou URL persistente, versão/release e data de
  acesso.
- Status por claim: `confirmado`, `ambíguo`, `conflitante` ou `não encontrado`.
- Localização exata do trecho que sustenta o claim.
- Segunda fonte independente quando o claim muda decisão experimental.
- A ausência de resultado em uma busca não prova novidade (L07).
- Validação estrutural desta entrega: `python3 tools/validate_research.py`.
