# Relatório de dry run do protocolo em dados sintéticos (R08)

Executado em 2026-09-14 pelo executor. Fixture **sintética** com três tipos
conhecidos (`alpha`, `beta`, `gamma`) e um tipo unknown (`omega`); nenhum dado
real de fonte ou alvo foi usado e a zona selada real não foi tocada. As métricas
abaixo são do dry run e **não são evidência científica**.

## 1. Estágios executados

| Estágio | Resultado medido |
|---|---|
| Geração da fixture | 70 nós (60 fonte + 10 unknown), arestas dirigidas ponderadas |
| Download local (HTTP + `tools/download.py`) | `downloaded`, 1.076 bytes, SHA-256 `f09fee7b…`; segunda chamada `skipped` (idempotente) |
| Pré-processamento | 60 linhas, 3 classes, features de grau source-fit |
| Treino trivial (MLP torch, CPU) | 3 classes, pesos `6c20ffb6…`, seed 20260914 |
| Congelamento | estado, normalizador e hashes registrados |
| Inferência opaca | 70 consultas (`q<hex>`), 13 rejeitadas (10 unknown + 3 outliers) |
| Avaliação selada (fixture sintética) | `metrics.json` válido no schema R06 (macro-recall@1, open-set, calibração) |
| Relatório | `artifacts/reports/DRY-RUN-R08.{md,json}` |

Tag interna do protocolo: **`dryrun-1.0-f90a4927`**. Hashes:
predictions `9f1ad2cf…`, metrics `bbbf9e82…`.

## 2. Critérios de aceite

- Fluxo completo (download → preprocessamento → treino trivial → freeze →
  inferência → avaliação → relatório) passou ponta a ponta.
- Todos os schemas validaram: predições e métricas aceitas por
  `tools/evaluator_contract.py`.
- Teste proposital de leakage **falhou como esperado**: abrir o selado sintético
  com a auditoria armada levanta `FirewallError`; predição com campo de label é
  recusada; scanner de referências limpo (`firewall_scanner_clean = true`).
- Download idempotente: a segunda chamada retorna `skipped` sem nova requisição.
- Determinismo: duas execuções produzem o mesmo `dryrun_tag` e o mesmo hash de
  predições.

## 3. Recursos medidos

- CPU apenas; nenhuma GPU; suíte de testes completa em ~11,6 s (5 testes novos
  de dry run); fixture de poucos KB em `runs/dryrun-r08/` (ignorado pelo Git).

## 4. Falhas e correções

- A primeira versão da fixture não era detectável como unknown (rejeição 0);
  ajustada para dar ao tipo `omega` um regime de graus distinto, com rejeição
  por distância source-fit, passando a 13 rejeições.
- O contrato de predições não marcava a chave `type` como proibida; a chave foi
  adicionada à lista de rótulos proibidos.

## 5. Limitações

- Fixture linearmente separável e trivial; o dry run valida **operacionalidade**,
  não desempenho nem viabilidade científica.
- A avaliação selada usou um "selado" sintético sob firewall; o selado real e o
  custodiante independente continuam pendentes (H04/H07/M08).
- Números do dry run não entram em nenhuma claim; a conclusão real depende do
  pré-registro assinado (R07) e do gate G3.
