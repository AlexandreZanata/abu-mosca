#!/usr/bin/env python3
"""Calibração, open-set e incerteza com regras fixas (B02).

Funções puras, sem I/O e sem labels reais: Brier multiclasse, ECE com bins
fixos e tabela de confiabilidade, AUROC/AUPR, FPR@TPR pré-fixada, bootstrap
agrupado e permutação por troca de sinal com seed registrada. O limiar de
rejeição é aprendido **somente na fonte** (`fit_threshold_source`) e aplicado
depois sem refit.

Empates: bin de confiança usa `int(conf * bins)` limitado a `bins-1`; empates
em scores contam 0,5 no AUROC e entram em ordem estável no AUPR.
"""

from __future__ import annotations

import random
from typing import Mapping, Sequence


class CalibrationError(RuntimeError):
    pass


def brier_multiclass(probabilities: Mapping[str, Mapping[str, float]], gold: Mapping[str, str | None]) -> float:
    """Brier multiclasse médio: média de sum_c (p_c - y_c)^2 por consulta."""
    if not probabilities:
        return 0.0
    values = []
    for query, distribution in probabilities.items():
        label = gold.get(query)
        if label is None:
            continue
        total = sum(distribution.values())
        if total <= 0:
            raise CalibrationError(f"distribuição degenerada em '{query}'")
        values.append(sum((probability / total - (1.0 if name == label else 0.0)) ** 2 for name, probability in distribution.items()))
    return round(sum(values) / len(values), 6) if values else 0.0


def reliability_table(confidences: Sequence[float], correct: Sequence[bool], bins: int = 15) -> list[dict]:
    if bins < 1:
        raise CalibrationError("bins deve ser ≥ 1")
    if len(confidences) != len(correct):
        raise CalibrationError("confidences e correct com tamanhos diferentes")
    rows = [{"bin": index, "count": 0, "mean_confidence": 0.0, "accuracy": 0.0} for index in range(bins)]
    for confidence, hit in zip(confidences, correct):
        if not 0.0 <= confidence <= 1.0:
            raise CalibrationError(f"confiança fora de [0,1]: {confidence}")
        slot = min(bins - 1, int(confidence * bins))
        rows[slot]["count"] += 1
        rows[slot]["mean_confidence"] += confidence
        rows[slot]["accuracy"] += 1.0 if hit else 0.0
    for row in rows:
        if row["count"]:
            row["mean_confidence"] = round(row["mean_confidence"] / row["count"], 6)
            row["accuracy"] = round(row["accuracy"] / row["count"], 6)
    return rows


def expected_calibration_error(confidences: Sequence[float], correct: Sequence[bool], bins: int = 15) -> float:
    rows = reliability_table(confidences, correct, bins)
    total = sum(row["count"] for row in rows)
    if total == 0:
        return 0.0
    return round(sum(row["count"] / total * abs(row["accuracy"] - row["mean_confidence"]) for row in rows), 6)


def auroc(positive_scores: Sequence[float], negative_scores: Sequence[float]) -> float:
    if not positive_scores or not negative_scores:
        return 0.5
    wins = sum(1 for p in positive_scores for n in negative_scores if p > n) + 0.5 * sum(
        1 for p in positive_scores for n in negative_scores if p == n
    )
    return round(wins / (len(positive_scores) * len(negative_scores)), 6)


def aupr(positive_scores: Sequence[float], negative_scores: Sequence[float]) -> float:
    if not positive_scores:
        return 0.0
    ranked = sorted(
        [(score, 1) for score in positive_scores] + [(score, 0) for score in negative_scores],
        key=lambda item: (-item[0], item[1]),
    )
    hits = 0
    precision_sum = 0.0
    for position, (_, label) in enumerate(ranked, 1):
        if label:
            hits += 1
            precision_sum += hits / position
    return round(precision_sum / len(positive_scores), 6)


def fpr_at_tpr(positive_scores: Sequence[float], negative_scores: Sequence[float], tpr: float = 0.95) -> dict:
    """FPR na TPR pré-fixada; limiar é o k-ésimo maior score positivo."""
    if not positive_scores:
        raise CalibrationError("sem scores positivos para fixar a TPR")
    if not 0.0 < tpr <= 1.0:
        raise CalibrationError("tpr deve estar em (0,1]")
    ordered = sorted(positive_scores, reverse=True)
    index = max(0, min(len(ordered) - 1, int(round(tpr * len(ordered))) - 1))
    threshold = ordered[index]
    achieved_tpr = sum(1 for score in positive_scores if score >= threshold) / len(positive_scores)
    false_positives = sum(1 for score in negative_scores if score >= threshold)
    fpr = false_positives / len(negative_scores) if negative_scores else 0.0
    return {
        "threshold": round(threshold, 6),
        "tpr_target": tpr,
        "tpr_achieved": round(achieved_tpr, 6),
        "fpr": round(fpr, 6),
        "negatives": len(negative_scores),
    }


def open_set_metrics(
    known_scores: Sequence[float],
    unknown_scores: Sequence[float],
    tpr: float = 0.95,
) -> dict:
    """Scores = confiança de ser conhecido (maior = mais conhecido).

    AUROC/AUPR tratam known como positivos e unknown como negativos; a FPR é a
    fração de unknown aceitos no limiar que garante a TPR pedida em known.
    """
    return {
        "auroc": auroc(known_scores, unknown_scores),
        "aupr": aupr(known_scores, unknown_scores),
        "fpr_at_tpr": fpr_at_tpr(known_scores, unknown_scores, tpr),
        "tpr_target": tpr,
    }


def bootstrap_ci_grouped(
    groups: Mapping[str, Sequence[float]],
    iterations: int = 2000,
    seed: int = 20260914,
) -> dict:
    """IC 95% do macro por bootstrap agrupado por grupo (classe). Reamostra grupos."""
    names = sorted(groups)
    if not names or iterations < 1:
        raise CalibrationError("grupos vazios ou iterations < 1")
    rng = random.Random(seed)
    samples = []
    for _ in range(iterations):
        draw = [rng.choice(names) for _ in range(len(names))]
        values = [sum(groups[name]) / len(groups[name]) for name in draw if groups[name]]
        samples.append(sum(values) / len(values) if values else 0.0)
    samples.sort()
    low = samples[int(0.025 * (len(samples) - 1))]
    high = samples[int(0.975 * (len(samples) - 1))]
    point = sum(sum(groups[name]) / len(groups[name]) for name in names if groups[name]) / len([name for name in names if groups[name]])
    return {"point": round(point, 6), "ci95": [round(low, 6), round(high, 6)], "iterations": iterations, "seed": seed}


def permutation_p_sign_flip(values: Sequence[float], iterations: int = 5000, seed: int = 20260914) -> float:
    """Permutação por troca de sinal para a média (nulo de simetria em torno de zero)."""
    if not values:
        return 1.0
    rng = random.Random(seed)
    observed = abs(sum(values) / len(values))
    hits = 0
    for _ in range(iterations):
        flipped = sum(value if rng.random() < 0.5 else -value for value in values)
        if abs(flipped / len(values)) >= observed:
            hits += 1
    return round((hits + 1) / (iterations + 1), 6)


def fit_threshold_source(
    source_known_scores: Sequence[float],
    source_unknown_scores: Sequence[float],
    tpr: float = 0.95,
) -> dict:
    """Ajusta o limiar de rejeição APENAS com dados de fonte/desenvolvimento."""
    result = fpr_at_tpr(source_known_scores, source_unknown_scores, tpr)
    return {
        "threshold": result["threshold"],
        "tpr_target": tpr,
        "source_tpr": result["tpr_achieved"],
        "source_fpr": result["fpr"],
        "fitted_on": "source",
    }


def apply_threshold(scores: Sequence[float], threshold: float) -> list[bool]:
    """Rejeita (True) scores abaixo do limiar congelado; nunca reajusta."""
    return [score < threshold for score in scores]
