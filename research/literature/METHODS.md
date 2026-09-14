# Matriz de métodos, baselines e implementações auditáveis

Aberto em 2026-09-14 (L06). Transforma a literatura revisada em opções
executáveis com parâmetros, complexidade, dependências, licença, manutenção,
suporte sparse/sampling e estimativa conservadora para 8 GB. Nenhum pacote foi
instalado ou executado nesta fase; nenhuma estimativa foi medida.

## 1. Estado e escopo

- Entradas recebem ID `M-nn`, na ordem de custo do ESCOPO.
- Estimativas de 8 GB são julgamentos conservadores de projeto, não medições;
  serão verificadas em smoke e piloto (M04).
- Incompatibilidades são registradas como tais; nenhuma adaptação é fabricada.
- Métodos transdutivos aparecem rotulados e nunca como zero-shot direto (L03).

## 2. Matriz de métodos

### M-01 — Random
- Referência: —
- Parâmetros: seed fixa.
- Complexidade: O(1) por consulta.
- Dependências: Python (stdlib).
- Licença: não aplicável.
- Manutenção: não aplicável.
- Suporte sparse/sampling: não aplicável.
- Estimativa 8 GB: < 0,5 GB (CPU).
- Incompatibilidades: nenhuma; serve como piso absoluto.
- Status: planejado

### M-02 — Majority
- Referência: —
- Parâmetros: tipo mais frequente da fonte.
- Complexidade: O(N) para contagem.
- Dependências: Python (stdlib).
- Licença: não aplicável.
- Manutenção: não aplicável.
- Suporte sparse/sampling: não aplicável.
- Estimativa 8 GB: < 0,5 GB (CPU).
- Incompatibilidades: ignora estrutura e atributos; piso absoluto.
- Status: planejado

### M-03 — Degree-only
- Referência: —
- Parâmetros: grau in/out, normalizações; classificador linear.
- Complexidade: O(N + E) para features; treino linear barato.
- Dependências: Python (stdlib) e opcionalmente scikit-learn.
- Licença: não aplicável para o cálculo; scikit-learn tem licença própria a auditar.
- Manutenção: não aplicável.
- Suporte sparse/sampling: usa representação esparsa.
- Estimativa 8 GB: < 0,5 GB (CPU).
- Incompatibilidades: é o atalho que o controle pareado por grau precisa vencer (B03).
- Status: planejado

### M-04 — Handcrafted
- Referência: LIT-0057; LIT-0006 para motivos de vizinhança.
- Parâmetros: graus, coeficiente de clustering, caminhos curtos, motivos; janela de vizinhança.
- Complexidade: O(N·k) a O(N·E) dependendo do motivo.
- Dependências: NetworkX (BSD-3-Clause) e NumPy.
- Licença: BSD-3-Clause (NetworkX) verificada.
- Manutenção: ativa (NetworkX 3.6.1).
- Suporte sparse/sampling: suporta sparse; custo de CPU cresce com motivos.
- Estimativa 8 GB: 1 a 2 GB (CPU) para o grafo da fonte.
- Incompatibilidades: motivos caros no grafo inteiro; calcular em subset ou amostragem.
- Status: planejado

### M-05 — Node2Vec
- Referência: LIT-0049.
- Parâmetros: dimensão, comprimento e número de caminhadas, p, q, janela, épocas.
- Complexidade: linear no número de nós para grafos esparsos (relatado).
- Dependências: implementação do autor ou fork em Python; NumPy.
- Licença: repositório original com licença não verificada nesta busca.
- Manutenção: não verificada nesta busca.
- Suporte sparse/sampling: caminhadas esparsas; amostragem por alias.
- Estimativa 8 GB: cerca de 2 GB (embeddings de 140 mil nós x 128 dimensões ≈ 72 MB mais estruturas de treino).
- Incompatibilidades: transdutivo; espaços independentes não são comparáveis sem alinhamento (proibição L03/L05).
- Status: planejado

### M-06 — DeepWalk
- Referência: LIT-0050.
- Parâmetros: dimensão, comprimento e número de caminhadas, janela, épocas.
- Complexidade: linear e paralelizável (relatado).
- Dependências: implementação original em Python; NumPy.
- Licença: repositório original com licença não verificada nesta busca.
- Manutenção: não verificada nesta busca.
- Suporte sparse/sampling: caminhadas truncadas.
- Estimativa 8 GB: cerca de 2 GB.
- Incompatibilidades: transdutivo, igual a M-05.
- Status: planejado

### M-07 — Espectral
- Referência: LIT-0033 (adjacency spectral embedding aplicada a neurônios), LIT-0028 (graph matching espectral).
- Parâmetros: dimensão de embedding, número de componentes, clustering (GMM).
- Complexidade: SVD truncada, aproximadamente O(E·d) por iteração; custo de memória sensível.
- Dependências: SciPy/NumPy e opcionalmente scikit-learn.
- Licença: bibliotecas com licenças próprias a auditar.
- Manutenção: ativa (SciPy/NumPy).
- Suporte sparse/sampling: exige matriz esparsa e SVD aleatorizada.
- Estimativa 8 GB: 4 a 6 GB para o grafo da fonte; risco de estouro sem SVD aleatorizada.
- Incompatibilidades: transdutivo; autovetores podem não ser estáveis entre grafos.
- Status: planejado

### M-08 — MLP
- Referência: —
- Parâmetros: camadas, largura, dropout, épocas, taxa de aprendizado.
- Complexidade: O(N·d) por época.
- Dependências: PyTorch (licença própria a auditar).
- Licença: PyTorch BSD-3-Clause (a confirmar na instalação).
- Manutenção: ativa.
- Suporte sparse/sampling: opera sobre features densas derivadas; lote completo em RAM.
- Estimativa 8 GB: 1 a 2 GB.
- Incompatibilidades: ignora estrutura além das features fornecidas; controle obrigatório (B05).
- Status: planejado

### M-09 — GraphSAGE
- Referência: LIT-0043.
- Parâmetros: agregação, número de camadas, tamanhos de vizinhança, dimensão, lote.
- Complexidade: O(batch · fanout^camadas) por passo.
- Dependências: PyTorch + PyG (MIT) ou DGL (Apache-2.0).
- Licença: MIT (PyG) e Apache-2.0 (DGL) verificadas.
- Manutenção: ativas; PyG com release 2.8.0 e último push verificado em 2026-07-06.
- Suporte sparse/sampling: samplers de vizinhança nativos.
- Estimativa 8 GB: 3 a 5 GB com amostragem; grafo inteiro não cabe.
- Incompatibilidades: agregação padrão ignora peso/direção; pesos entram como features de aresta.
- Status: planejado

### M-10 — GIN
- Referência: LIT-0051.
- Parâmetros: MLP interno, epsilon, número de camadas, lote.
- Complexidade: O(batch · fanout^camadas) por passo.
- Dependências: PyTorch + PyG ou DGL.
- Licença: MIT (PyG) e Apache-2.0 (DGL) verificadas.
- Manutenção: ativas.
- Suporte sparse/sampling: samplers de vizinhança.
- Estimativa 8 GB: 3 a 5 GB com amostragem.
- Incompatibilidades: somatório assume arestas sem peso; pesos exigem features de aresta; direção precisa de tratamento explícito.
- Status: planejado

### M-11 — GAT
- Referência: LIT-0052.
- Parâmetros: cabeças de atenção, dimensão por cabeça, camadas, dropout, lote.
- Complexidade: O(batch · arestas amostradas · cabeças).
- Dependências: PyTorch + PyG ou DGL.
- Licença: MIT (PyG) e Apache-2.0 (DGL) verificadas.
- Manutenção: ativas.
- Suporte sparse/sampling: samplers de vizinhança; atenção só nas arestas amostradas.
- Estimativa 8 GB: 4 a 6 GB com amostragem.
- Incompatibilidades: atenção não é invariante a direção por padrão; pesos entram como features.
- Status: condicional (apenas se a representação exigir)

### M-12 — Relacional (R-GCN)
- Referência: LIT-0053.
- Parâmetros: número de tipos de relação, dimensão, camadas, regularização.
- Complexidade: O(batch · arestas · tipos de relação).
- Dependências: PyTorch + PyG (camada RGCNConv) ou reimplementação.
- Licença: MIT (PyG) verificada.
- Manutenção: ativa.
- Suporte sparse/sampling: convolução esparsa por tipo de relação.
- Estimativa 8 GB: 4 a 6 GB com amostragem; um peso por tipo de relação.
- Incompatibilidades: modela tipos discretos de aresta; peso contínuo precisa ser discretizado ou virar feature.
- Status: condicional

### M-13 — Transformer pequeno
- Referência: LIT-0054 (Graphormer).
- Parâmetros: camadas, cabeças, dimensão, codificações de centralidade, distância e aresta.
- Complexidade: O(N^2) na atenção densa.
- Dependências: PyTorch (e implementação própria pequena).
- Licença: PyTorch BSD-3-Clause (a confirmar); código do Graphormer com licença não verificada.
- Manutenção: não verificada.
- Suporte sparse/sampling: não usa sparse; exigiria subgrafos ou pooling.
- Estimativa 8 GB: incompatível com o grafo inteiro (mais de 8 GB por N^2); apenas subgrafos pequenos.
- Incompatibilidades: não abre antes de ganho demonstrado (ESCOPO) e não é assumido superior (L05).
- Status: fora de escopo por ora

### M-14 — NBLAST (matching publicado)
- Referência: LIT-0026.
- Parâmetros: parâmetros de score estatísticos; KNN para busca.
- Complexidade: cerca de 2 ms por comparação par a par (relatado); busca KNN.
- Dependências: R (natverse) ou reimplementação consagrada.
- Licença: repositório nat.nblast com licença não verificada nesta busca; artigo CC BY.
- Manutenção: ativa no ecossistema natverse (a confirmar).
- Suporte sparse/sampling: não usa grafo; usa esqueletos.
- Estimativa 8 GB: 2 a 4 GB (CPU) em subconjuntos; 140 mil x 140 mil pares é inviável.
- Incompatibilidades: morfologia, não conectividade; pertence ao Experimento C.
- Status: condicional

### M-15 — NeuronBridge (matching publicado)
- Referência: LIT-0027.
- Parâmetros: nenhum treino local; consulta a matches pré-computados.
- Complexidade: consulta indexada; busca customizada depende do serviço.
- Dependências: serviço web e APIs oficiais; dados sujeitos a acordo de licença.
- Licença: código arquivado em Zenodo; imagens sujeitas a acordo.
- Manutenção: ativa (serviço Janelia).
- Suporte sparse/sampling: não aplicável.
- Estimativa 8 GB: não consome GPU local; uso via serviço.
- Incompatibilidades: imagem/morfologia; não é baseline treinável no trilho topologia.
- Status: contextual

## 3. Notas de execução e licenças

- Ordem de execução: M-01 a M-08 primeiro, depois M-09 a M-12; M-13 só após
  ganho demonstrado; M-14 e M-15 apenas no Experimento C.
- Nenhum pacote foi instalado ou executado nesta fase; a instalação ocorrerá em
  fase própria com registro de versão e licença.
- PyG (MIT) e DGL (Apache-2.0) estão auditados; PyTorch terá licença confirmada
  no ambiente.
- Métodos transdutivos (M-05, M-06, M-07) só entram rotulados, com a limitação
  de que espaços independentes não são comparáveis sem alinhamento permitido.

## 4. Limitações

- Estimativas de memória não medidas; podem ser revisadas para baixo ou para
  cima após smoke (M04).
- Manutenção e licenças marcadas como não verificadas precisam ser confirmadas
  antes da instalação.
- A matriz não decide o par fonte/alvo, que segue em G2.
- Validação: `python3 tools/validate_research.py`.
