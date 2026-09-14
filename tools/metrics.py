#!/usr/bin/env python3
"""Implementação única de métricas de retrieval/classificação (B01).

Funções puras, sem I/O e sem qualquer acesso a labels reais do alvo: recebem
predições e rótulos **sintéticos ou da fonte** e devolvem métricas em Python
puro. Orientação de score é explícita (`higher_is_better`); empates são
desfeitos de forma determinística pelo rótulo em ordem alfabética.

Métricas: Recall@1/5/10 (macro por classe e micro), MRR, MAP, top-k accuracy,
macro-F1 e balanced accuracy, com contagens de queries sem match e classes
ausentes.
"""

from __future__ import annotations

from typing import Iterable, Mapping, Sequence


class MetricsError(RuntimeError):
    pass


def rank_from_scores(
    scores: Mapping[str, Mapping[str, float]],
    higher_is_better: bool = True,
) -> dict[str, list[str]]:
    """Ordena rótulos por score; empates desfeitos por rótulo alfabético."""
    ranked: dict[str, list[str]] = {}
    for query, label_scores in scores.items():
        if higher_is_better:
            ranked[query] = sorted(label_scores, key=lambda label: (-label_scores[label], label))
        else:
            ranked[query] = sorted(label_scores, key=lambda label: (label_scores[label], label))
    return ranked


def _normalize_gold(gold: Mapping[str, object]) -> dict[str, list[str] | None]:
    normalized: dict[str, list[str] | None] = {}
    for query, value in gold.items():
        if value is None:
            normalized[query] = None
        elif isinstance(value, str):
            normalized[query] = [value]
        elif isinstance(value, Iterable):
            items = [str(item) for item in value]
            normalized[query] = items or None
        else:
            raise MetricsError(f"gold inválido para '{query}'")
    return normalized


def recall_at_k(ranked: Mapping[str, Sequence[str]], gold: Mapping[str, object], k: int) -> dict[str, float | int]:
    """Recall@k macro (por classe) e micro (por query), com contagens."""
    gold_norm = _normalize_gold(gold)
    per_class_hits: dict[str, int] = {}
    per_class_total: dict[str, int] = {}
    micro_hits = 0
    micro_total = 0
    unmatched = 0
    for query, labels in gold_norm.items():
        predictions = list(ranked.get(query, []))[:k]
        if not labels:
            unmatched += 1
            continue
        micro_total += 1
        if any(label in predictions for label in labels):
            micro_hits += 1
        for label in labels:
            per_class_total[label] = per_class_total.get(label, 0) + 1
            if label in predictions:
                per_class_hits[label] = per_class_hits.get(label, 0) + 1
    classes = sorted(per_class_total)
    macro = (
        sum(per_class_hits.get(label, 0) / per_class_total[label] for label in classes) / len(classes)
        if classes
        else 0.0
    )
    return {
        "macro": round(macro, 6),
        "micro": round(micro_hits / micro_total, 6) if micro_total else 0.0,
        "classes": classes,
        "queries_scored": micro_total,
        "queries_unmatched": unmatched,
        "per_class": {
            label: round(per_class_hits.get(label, 0) / per_class_total[label], 6) for label in classes
        },
    }


def mean_reciprocal_rank(ranked: Mapping[str, Sequence[str]], gold: Mapping[str, object]) -> float:
    gold_norm = _normalize_gold(gold)
    values = []
    for query, labels in gold_norm.items():
        if not labels:
            continue
        predictions = list(ranked.get(query, []))
        rank = next((position for position, label in enumerate(predictions, 1) if label in labels), None)
        values.append(1.0 / rank if rank else 0.0)
    return round(sum(values) / len(values), 6) if values else 0.0


def average_precision(ranked: Mapping[str, Sequence[str]], gold: Mapping[str, object]) -> float:
    """MAP com relevantes múltiplos (média das precisões nos acertos)."""
    gold_norm = _normalize_gold(gold)
    values = []
    for query, labels in gold_norm.items():
        if not labels:
            continue
        predictions = list(ranked.get(query, []))
        relevant = set(labels)
        hits = 0
        precision_sum = 0.0
        for position, label in enumerate(predictions, 1):
            if label in relevant:
                hits += 1
                precision_sum += hits / position
        values.append(precision_sum / len(relevant))
    return round(sum(values) / len(values), 6) if values else 0.0


def top_k_accuracy(ranked: Mapping[str, Sequence[str]], gold: Mapping[str, object], k: int) -> float:
    gold_norm = _normalize_gold(gold)
    values = []
    for query, labels in gold_norm.items():
        if not labels:
            continue
        predictions = list(ranked.get(query, []))[:k]
        values.append(1.0 if any(label in predictions for label in labels) else 0.0)
    return round(sum(values) / len(values), 6) if values else 0.0


def macro_f1(ranked: Mapping[str, Sequence[str]], gold: Mapping[str, object]) -> float:
    """F1 macro em top-1 (multi-instance conta acerto se qualquer gold acerta)."""
    gold_norm = _normalize_gold(gold)
    per_class = {label: {"tp": 0, "pred": 0, "gold": 0} for label in _all_labels(gold_norm, ranked)}
    for query, labels in gold_norm.items():
        if not labels:
            continue
        top = list(ranked.get(query, []))[:1]
        predicted = top[0] if top else None
        if predicted is not None:
            per_class[predicted]["pred"] += 1
        for label in labels:
            per_class[label]["gold"] += 1
        if predicted is not None and predicted in labels:
            per_class[predicted]["tp"] += 1
    scores = []
    for label, counts in per_class.items():
        if counts["gold"] == 0:
            continue
        precision = counts["tp"] / counts["pred"] if counts["pred"] else 0.0
        recall = counts["tp"] / counts["gold"]
        scores.append(2 * precision * recall / (precision + recall) if (precision + recall) else 0.0)
    return round(sum(scores) / len(scores), 6) if scores else 0.0


def balanced_accuracy(ranked: Mapping[str, Sequence[str]], gold: Mapping[str, object]) -> float:
    """Acurácia balanceada top-1, igual à macro Recall@1 por classe."""
    return float(recall_at_k(ranked, gold, 1)["macro"])


def _all_labels(gold_norm: Mapping[str, list[str] | None], ranked: Mapping[str, Sequence[str]]) -> set[str]:
    labels: set[str] = set()
    for value in gold_norm.values():
        for label in value or []:
            labels.add(label)
    for predictions in ranked.values():
        labels.update(predictions[:1])
    return labels


def evaluate(
    ranked: Mapping[str, Sequence[str]],
    gold: Mapping[str, object],
    k_values: Sequence[int] = (1, 5, 10),
) -> dict:
    """Pacote completo de métricas para uma lista ordenada por query."""
    report = {
        "recall": {f"@{k}": recall_at_k(ranked, gold, k) for k in k_values},
        "mrr": mean_reciprocal_rank(ranked, gold),
        "map": average_precision(ranked, gold),
        "top_k_accuracy": {f"@{k}": top_k_accuracy(ranked, gold, k) for k in k_values},
        "macro_f1": macro_f1(ranked, gold),
        "balanced_accuracy": balanced_accuracy(ranked, gold),
    }
    first = report["recall"][f"@{k_values[0]}"]
    report["counts"] = {
        "queries_scored": first["queries_scored"],
        "queries_unmatched": first["queries_unmatched"],
        "classes": len(first["classes"]),
    }
    return report
