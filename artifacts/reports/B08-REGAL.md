# Reprodução de baseline publicado — REGAL/xNetMF (B08)

Executado em 2026-09-15, somente com o benchmark público do próprio método e
sem nenhum dado do alvo. Esta fase reproduz o baseline publicado mais
compatível identificado em L03: **REGAL (ALN-05, LIT-0030; Heimann et al.,
CIKM 2018, DOI 10.1145/3269206.3271788)** — alinhamento de grafos não
supervisionado, baseado em conectividade e com licença permissiva.

## 1. Escolha do método e trilhos

| Candidato L03 | Situação nesta fase |
|---|---|
| REGAL (ALN-05) | escolhido: conectividade, não supervisionado, MIT, código oficial |
| NBLAST / NeuronBridge (ALN-01/02) | morfologia/imagens, exigem Experimento C e termos próprios |
| Bisected GM (ALN-03) | depende de referência bilateral conhecida; outro desenho |
| SGM/FAQ (ALN-04) | variante semeada exigiria correspondências proibidas |
| FINAL (ALN-06) | atributos obrigatórios: informação extra, trilho separado |

Supervisão declarada: o mapa verdadeiro do benchmark é usado **somente para
pontuar**; o núcleo xNetMF/REGAL é não supervisionado. A variante com
atributos não foi executada (trilho separado). REGAL é **transdutivo** e
**não comparável zero-shot**, como já registrado em B06/B07.

## 2. Versão, licença e ambiente

- Repositório oficial `github.com/GemsLab/REGAL`, commit fixado
  `42ed9083f51ad481dc7d7acfb488b390e2013050` (2021-03-30); licença **MIT**
  verificada em `license.txt` (Copyright (c) 2018, Mark Heimann).
- Cópia congelada e ignorada pelo Git em `data/raw/vendor/regal-42ed9083/`
  (tar.gz de `codeload.github.com`, SHA-256
  `99443be72f3b0517b9763d3c45453af30ba9e90373068d699d9118ffedecd718`);
  SHA-256 por arquivo no `B08-REGAL.json`.
- Código oficial executado **sem nenhuma modificação**. Como `alignments.py`
  importa `sklearn` (ausente do lock do projeto), a reprodução usa um ambiente
  separado e pinado em `.local/regal-venv/`: numpy 2.5.3, scipy 1.18.1,
  networkx 3.6.1, scikit-learn 1.9.1 (licenças BSD-3-Clause/agregada; SHA-256
  dos wheels no JSON). O lock do projeto não foi alterado.
- Fontes da publicação baixadas e conferidas por SHA-256: arXiv v3
  (`f0057edc…`) e arXiv v1 (`5146b029…`).

## 3. Comandos

```text
.local/regal-venv/bin/python regal.py --input data/arenas_combined_edges.txt \
  --output <runs/b08/regal-shipped.npy>          # cwd: cópia congelada do repo
python3 tools/regal_repro.py run --report artifacts/reports/B08-REGAL.json
python3 tools/regal_repro.py check --report artifacts/reports/B08-REGAL.json
```

## 4. Resultado da reprodução

- Benchmark embarcado `arenas990-1` (par de 1.135 nós, 1% de ruído):
  **score top1 = 0,905727 (1.028/1.135)**.
- Duas execuções independentes produzem o mesmo SHA-256 de embedding
  (`87b7fea2…`): determinístico no ambiente fixado.
- **Paridade de artefato público:** o repositório oficial embarca
  `emb/arenas990-1.emb.npy` (saída de referência dos autores). Repontuado com
  o **próprio código oficial de avaliação**, esse artefato dá a mesma acurácia
  (Δ = 0,0). Nosso embedding difere do artefato em máximo 1,86e-2 e média
  3,9e-6 (diferenças numéricas de versão de biblioteca, não do método). Com as
  tolerâncias declaradas antes da execução (acurácia ≤ 0,002; média ≤ 1e-4), a
  paridade é **reproduzida**.
- **Achado de repositório:** o outro artefato embarcado,
  `emb/arenas990-1.emb` (pickle), pontua 0,000881 (1/1.135) sob o avaliador
  oficial — não é referência válida e fica sinalizado como inconsistente.

## 5. Paridade com a publicação: não verificável numericamente

A publicação (CIKM 2018 / arXiv v3) reporta acurácia **apenas graficamente**
(Figura 4); a Tabela 4 contém tempos de execução e a Tabela 5 lista os
datasets, sem valor numérico de acurácia por dataset. O único valor numérico
de acurácia nos manuscritos públicos dos autores está no arXiv v1 (§6.1,
case study do mirrored Karate: 79,4% para REGAL-xNetMF), mas a instância
exata (permutação e par conectado) não é publicada; reconstruí-la exigiria
adivinhar o grafo, o que o protocolo proíbe. Portanto o teste de paridade
numérica contra a publicação fica registrado como **não verificável
numericamente** — e não é substituído por um número inventado.

## 6. Recursos e limites

- Execução: 4,2 s, pico de RSS dos processos filhos 208 MiB, CPU apenas, sem
  GPU. Download externo: tarball MIT (~6 MB) e dois PDFs públicos.
- Limites: um único trial do benchmark; a paridade é de artefato do
  repositório, não da figura da publicação; o ambiente difere do original
  apenas em versões de biblioteca; resultados não sustentam claim de
  transferência nem uso zero-shot.
