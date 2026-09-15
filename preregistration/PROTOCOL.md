# Pré-registro confirmatório (minuta) — CrossConnectome-µ

**Status: MINUTA — assinatura humana pendente.** Preparada pela IA executora em
2026-09-14 (R07). Sem assinatura do responsável científico, este documento não
autoriza nenhuma análise confirmatória. Nenhum resultado do alvo foi observado
nem existe; nenhum rótulo selado foi lido.

- Versão: `1.0-draft` (será `1.0` na assinatura, com hash no `REGISTRY.md`).
- Base: R03–R06, G2 `GO`, C02–C05, D08 (crosswalk aprovado), D09/D10.
- Alterações pós-assinatura: somente via `CHANGELOG.md`, com motivo, diff e
  hash; depois do unseal, qualquer mudança é rotulada exploratória.

## 1. Fonte, alvo e versões fixados

| Papel | Dataset | Release fixada | Licença | Evidência |
|---|---|---|---|---|
| Fonte | MANC | `manc:v1.2.1` (bucket flat v1.0) | CC BY 4.0 | D05/D09/G2 |
| Alvo-piloto | MCNS | `male-cns:v1.0` | CC BY 4.0 | D07/D09/G2 |
| Alvo confirmatório reservado | BANC | `v888` | CC BY 4.0 (arquivos restritos) | D04/G2 |
| Reserva alternativa de alvo | FlyWire/FAFB | `v783` | grafo CC BY 4.0 | D02/G2 |
| Comparador | hemibrain | `v1.2.1` | CC BY 4.0 | D03 |

Trocar release, par ou papel invalida este pré-registro e exige novo G2. Os
arquivos usados têm manifesto e SHA-256 (R03); o MCNS não publica checksum e o
SHA-256 local é registrado no download.

## 2. População, unidade e independência

- Unidade de consulta: um neurônio do alvo; galeria: protótipos por tipo
  harmonizado da fonte, congelados.
- Grupos de inferência: tipos (bootstrap/permutação agrupados por tipo).
- Declaração canônica: **neurônios do mesmo grafo e seeds de treino não são
  réplicas biológicas independentes**; a conclusão é um estudo de transferência
  entre os datasets observados (um indivíduo por papel).

## 3. Features permitidas (trilho A — topologia)

- Permitido: direção, peso de sinapse (contagem), graus in/out e padrões de
  vizinhança computados sem rótulo.
- Proibido: ID numérico como feature, posição, região/neuropilo,
  neurotransmissor, morfologia, tipo, crosswalk ou qualquer campo derivado do
  alvo avaliativo. Normalizadores ajustados somente na fonte.

## 4. Modelo, baselines e capacidade

- Primário: GraphSAGE indutivo, 1–3M de parâmetros, com neighbor sampling.
- Comparável: GIN sob o mesmo orçamento; se incompatível com direção/peso, a
  incompatibilidade é relatada, não silenciada.
- Controle: MLP sobre as mesmas features (≈100k, ≈500k e pareado quando possível).
- Baselines obrigatórios: aleatório estratificado, maioria, degree-only,
  estatísticas artesanais; baselines transdutivos ficam fora do zero-shot.

## 5. Espaço de hiperparâmetros e budget de trials

- Seleção **somente na fonte**, com 3 seeds de seleção distintas das finais
  (297979363399525401, 1699981902186354598, 3729859090210297070).
- Budget fixo: **12 trials**; nenhum trial extra, nenhum sweep aberto.

| Trial | Dim | Camadas | Fanout | LR | Batch | Dropout |
|---|---|---|---|---|---|---|
| T01 | 576 | 2 | 10,10 | 1e-3 | 512 | 0,1 |
| T02 | 576 | 2 | 10,10 | 3e-4 | 512 | 0,2 |
| T03 | 408 | 3 | 15,10 | 1e-3 | 1024 | 0,1 |
| T04 | 408 | 3 | 15,10 | 3e-4 | 1024 | 0,2 |
| T05 | 576 | 2 | 10,10 | 1e-3 | 1024 | 0,2 |
| T06 | 576 | 2 | 10,10 | 3e-4 | 512 | 0,1 |
| T07 | 408 | 3 | 15,10 | 1e-3 | 512 | 0,1 |
| T08 | 408 | 3 | 15,10 | 3e-4 | 1024 | 0,2 |
| T09 | 576 | 2 | 15,10 | 1e-3 | 1024 | 0,1 |
| T10 | 408 | 3 | 10,10 | 3e-4 | 512 | 0,2 |
| T11 | 576 | 2 | 15,10 | 1e-3 | 512 | 0,2 |
| T12 | 408 | 3 | 10,10 | 3e-4 | 1024 | 0,1 |

- Critério de seleção: Macro Recall@1 de validação congruente na fonte,
  mediana das 3 seeds de seleção; empate → menor capacidade e menor tempo.
- Trials falhos permanecem no ledger; o melhor da fonte é congelado antes do
  alvo (M05/M06).

## 6. Seeds finais

Cinco seeds, derivadas de `derive_seed(20260914, "prereg-r07", "final-seed-i")`
com `tools/seeds.py`, fixadas aqui:

1. 1342714389145479246
2. 8142193368363737116
3. 495739693416096352
4. 8602629889984631926
5. 7682391451267186339

Bootstrap: `2130364506833354634`; permutação: `8300351966476733168`. A melhor
seed nunca é a estimativa; reportar mediana e intervalo entre seeds.

## 7. Stopping e early stop

- Máximo de 200 épocas por trial; early stop na métrica de validação da fonte
  com paciência de 20 épocas; sem qualquer sinal do alvo.
- Runs interrompidos são retomados ou descartados com registro; nada é
  sobrescrito (RUN-CONTRACT).
- Teto de recursos: pico ≤ 6,5 GB de VRAM no pré-registro (M04) e ≤ 28 GB de
  RAM no processamento (H08).

## 8. Métricas, SESOI e exclusões

- Primária: Macro Recall@1 no T0 (`macro-recall@1-t0`), IC 95% por bootstrap
  agrupado por tipo (10.000), mediana de Δ entre as 5 seeds; SAP/R06 fixa o
  cálculo.
- SESOI = **5 pontos percentuais** sobre o melhor baseline simples; sucesso
  exige Δ ≥ SESOI, IC 95% excluindo zero, sensibilidade balanceada e
  degree-matched preservados (família Holm de 3 testes, α = 0,05).
- K = **10** (cobertura mínima por classe); classes menores participam do macro
  com n reportado; sensibilidade balanceada restrita a n ≥ 10.
- Exclusões: missing, ambíguo e conflitante saem do T0 com contagens;
  singleton permanece com n = 1; regras decididas no congelamento (H07), nunca
  após scores. Circularidade: análise com e sem tipos derivados de
  conectividade (DEC-CW-03).
- Open-set: AUROC, AUPR e FPR@TPR95 com limiar congelado na fonte; calibração
  Brier/ECE (15 bins) com temperatura ajustada só na fonte.

## 9. Análise confirmatória

Ordem fixa: (1) métrica primária e IC; (2) Δ pareado e Holm; (3) gap
within-vs-cross; (4) open-set; (5) calibração; (6) secundárias; (7)
sensibilidades. Gap: within ≥ 2× o acaso macro e IC do cross cruzando o acaso →
refutação por overajuste; gap > 0,15 é registrado como diagnóstico.

## 10. Decisões condicionais do Nível 2

| Resultado em G6 | Ramos autorizados |
|---|---|
| `sucesso` | S01, S03, S06, S07, S08 e S11 conforme orçamento; S02 só se S01 mostrar ganho ≥ 2 p.p.; S04/S09 só com compatibilidade aprovada em D10; S05 se a curva não saturar; S10 só com ≥ 3 datasets; S12 após S11 |
| `parcial` | apenas S06, S07 e S08 como diagnósticos; sem escalada de arquitetura e sem novo treino caro |
| `refutado` | encerrar o Nível 2 neste alvo; hipótese nova exige alvo reservado intocado e novo pré-registro |
| `inconclusivo` | corrigir cobertura/circularidade sem tocar no alvo ou encerrar com relatório |

## 11. Exploratório versus confirmatório

- Confirmatório: tudo neste documento, executado antes do unseal e avaliado
  pelo pacote congelado.
- Exploratório: qualquer análise nova, subgrupo pós-hoc, feature ou métrica
  fora daqui; rotulada como exploratória, sem retreino confirmatório e sem
  substituir o resultado primário.

## 12. Avaliação selada e unseal

- Executor entrega predições por ID opaco (R06); o custodiante roda o avaliador
  uma única vez (M08) em sessão separada, com firewall armado, e devolve apenas
  métricas agregadas com hashes de entrada.
- Reexecução exige incidente documentado; reabrir tuning no alvo o transforma
  em validação e exige novo alvo para alegação confirmatória.

## 13. Alterações

- Somente via `CHANGELOG.md` com motivo, impacto, diff e hash; nenhuma
  sobrescrita de configuração ou resultado (PROTOCOLO e RUN-CONTRACT).
- Correções de forma (typo, link) ainda exigem entrada no changelog.

## 14. Assinatura

- Responsável científico: a preencher
- Revisor de estatística: a preencher
- Custodiante designado: a preencher
- Data e hash de assinatura: a preencher

## 15. Rastreabilidade e limitações

- Fases: R03–R06, G2, H04/H07, M01–M09, S01–S12, G3/G6.
- Limitações: números de K/gap/seed são propostas técnicas desta minuta e
  tornam-se válidos com a assinatura; contagens reais de classes virão de H07;
  um indivíduo por papel impede generalização populacional.
- Validação: `python3 tools/validate_research.py`.
