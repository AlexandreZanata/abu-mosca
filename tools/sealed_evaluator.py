#!/usr/bin/env python3
"""Avaliador selado: pontua predições opacas sem expor rótulos (H04).

Módulo do custodiante. Recebe um ou mais pacotes de predições (uma seed cada)
e o conjunto de rótulos selados, valida cobertura/crosswalk, confere os schemas
e devolve **apenas** métricas agregadas no schema R06. Nunca imprime IDs de
consulta ou exemplos individuais; o hash do label set é registrado nas métricas
e no resumo. Deve rodar em sessão separada do executor de treino, com firewall
armado e sem rede.
"""

import argparse
import hashlib
import json
import math
import random
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import evaluator_contract  # noqa: E402

LABEL_STATUSES = ("known", "unknown", "missing", "ambiguous", "conflicting")
QID_RE = re.compile(r"^q[0-9a-f]{16}$")
GID_RE = re.compile(r"^g[0-9a-f]{16}$")
LABEL_SCHEMA_REQUIRED = ("label_schema_version", "crosswalk_version", "queries", "gallery", "crosswalk")
LABEL_TOKENS = ("q", "g")


class EvaluationError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_label_set(payload: dict, label: str = "labels") -> list[str]:
    failures = []
    if not isinstance(payload, dict):
        return [f"{label}: raiz deve ser objeto JSON"]
    for field in LABEL_SCHEMA_REQUIRED:
        if field not in payload:
            failures.append(f"{label}: campo obrigatório ausente '{field}'")
    if payload.get("label_schema_version") != "1.0":
        failures.append(f"{label}: label_schema_version deve ser '1.0'")
    queries = payload.get("queries")
    gallery = payload.get("gallery")
    crosswalk = payload.get("crosswalk")
    if not isinstance(queries, dict) or not queries:
        failures.append(f"{label}: 'queries' deve ser objeto não vazio")
        queries = {}
    if not isinstance(gallery, dict) or not gallery:
        failures.append(f"{label}: 'gallery' deve ser objeto não vazio")
        gallery = {}
    if not isinstance(crosswalk, dict):
        failures.append(f"{label}: 'crosswalk' deve ser objeto")
        crosswalk = {}
    for query_id, entry in queries.items():
        if not QID_RE.match(str(query_id)):
            failures.append(f"{label}: id de consulta fora do padrão opaco")
            continue
        status = entry.get("status") if isinstance(entry, dict) else None
        if status not in LABEL_STATUSES:
            failures.append(f"{label}: status inválido para consulta '{query_id}'")
        type_t0 = entry.get("type_t0") if isinstance(entry, dict) else None
        if status == "known" and (not isinstance(type_t0, str) or not type_t0):
            failures.append(f"{label}: consulta known sem type_t0")
        if status == "known" and type_t0 not in set(gallery.values()):
            failures.append(f"{label}: type_t0 sem correspondente na galeria (cobertura)")
    for gallery_id, type_t0 in gallery.items():
        if not GID_RE.match(str(gallery_id)):
            failures.append(f"{label}: id de galeria fora do padrão opaco")
        if not isinstance(type_t0, str) or not type_t0:
            failures.append(f"{label}: galeria sem tipo harmonizado")
    known_types = set(gallery.values())
    for source_type, target_type in crosswalk.items():
        if target_type not in known_types:
            failures.append(f"{label}: crosswalk aponta para tipo fora da galeria")
    return failures


def _macro(groups: dict[str, list[int]]) -> float:
    values = [sum(hits) / len(hits) for hits in groups.values() if hits]
    return sum(values) / len(values) if values else 0.0


def _per_class(predictions: dict, labels: dict, classes: list[str]) -> dict[str, list[int]]:
    gallery_of = {gid: tipo for gid, tipo in labels["gallery"].items()}
    groups: dict[str, list[int]] = {classe: [] for classe in classes}
    for query in predictions["queries"]:
        entry = labels["queries"].get(query["id"])
        if entry is None or entry["status"] != "known" or query.get("rejected"):
            continue
        true_type = entry["type_t0"]
        if true_type not in groups:
            continue
        ranked = query["ranked"]
        rank = next((pos for pos, item in enumerate(ranked, 1) if gallery_of[item["id"]] == true_type), None)
        groups[true_type].append(1 if rank == 1 else 0)
    return groups


def _rank_stats(predictions: dict, labels: dict, classes: set[str]) -> dict:
    gallery_of = {gid: tipo for gid, tipo in labels["gallery"].items()}
    ranks = []
    for query in predictions["queries"]:
        entry = labels["queries"].get(query["id"])
        if entry is None or entry["status"] != "known" or query.get("rejected"):
            continue
        if entry["type_t0"] not in classes:
            continue
        rank = next(
            (pos for pos, item in enumerate(query["ranked"], 1) if gallery_of[item["id"]] == entry["type_t0"]),
            None,
        )
        if rank is not None:
            ranks.append(rank)
    if not ranks:
        return {"macro": 0.0, "recall@5": 0.0, "recall@10": 0.0, "mrr": 0.0, "map": 0.0, "accuracy": 0.0}
    return {
        "macro": None,
        "recall@5": sum(1 for rank in ranks if rank <= 5) / len(ranks),
        "recall@10": sum(1 for rank in ranks if rank <= 10) / len(ranks),
        "mrr": sum(1.0 / rank for rank in ranks) / len(ranks),
        "map": sum(1.0 / rank for rank in ranks) / len(ranks),
        "accuracy": sum(1 for rank in ranks if rank == 1) / len(ranks),
    }


def _auroc(positive: list[float], negative: list[float]) -> float:
    wins = sum(1 for p in positive for n in negative if p > n) + 0.5 * sum(
        1 for p in positive for n in negative if p == n
    )
    total = len(positive) * len(negative)
    return wins / total if total else 0.5


def _aupr(positive: list[float], negative: list[float]) -> float:
    ranked = sorted([(s, 1) for s in positive] + [(s, 0) for s in negative], key=lambda x: -x[0])
    hits = 0
    precision_sum = 0.0
    for position, (_, label) in enumerate(ranked, 1):
        if label:
            hits += 1
            precision_sum += hits / position
    return precision_sum / len(positive) if positive else 0.0


def _bootstrap_ci(values: list[float], rng: random.Random, iterations: int) -> list[float]:
    if not values:
        return [0.0, 0.0]
    samples = []
    for _ in range(iterations):
        draw = [values[rng.randrange(len(values))] for _ in range(len(values))]
        samples.append(sum(draw) / len(draw))
    samples.sort()
    low = samples[int(0.025 * (len(samples) - 1))]
    high = samples[int(0.975 * (len(samples) - 1))]
    return [round(low, 6), round(high, 6)]


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(fraction * (len(ordered) - 1))))
    return ordered[index]


def _open_set(predictions_list: list[dict], labels: dict) -> list[float]:
    results = []
    for predictions in predictions_list:
        positives, negatives = [], []
        for query in predictions["queries"]:
            entry = labels["queries"].get(query["id"])
            if entry is None or not query["ranked"]:
                continue
            score = 1.0 - query["ranked"][0]["score"]
            if entry["status"] == "known" and not query.get("rejected"):
                negatives.append(score)
            elif entry["status"] == "unknown":
                positives.append(score)
        if positives and negatives:
            results.append((_auroc(positives, negatives), _aupr(positives, negatives), positives, negatives))
    return results


def _calibration(predictions_list: list[dict], labels: dict, temperature: float, bins: int = 15) -> dict:
    briers, eces = [], []
    for predictions in predictions_list:
        confidences, correct = [], []
        gallery_of = {gid: tipo for gid, tipo in labels["gallery"].items()}
        for query in predictions["queries"]:
            entry = labels["queries"].get(query["id"])
            if entry is None or entry["status"] != "known" or query.get("rejected"):
                continue
            top = query["ranked"][0]
            confidence = math.exp(top["score"] / temperature) / (
                math.exp(top["score"] / temperature) + math.exp((1 - top["score"]) / temperature)
            )
            confidences.append(confidence)
            correct.append(1 if gallery_of[top["id"]] == entry["type_t0"] else 0)
        if not confidences:
            briers.append(0.0)
            eces.append(0.0)
            continue
        briers.append(sum((confidence - hit) ** 2 for confidence, hit in zip(confidences, correct)) / len(confidences))
        ece = 0.0
        counts = [0] * bins
        for confidence in confidences:
            counts[min(bins - 1, int(confidence * bins))] += 1
        mean_conf = sum(confidences) / len(confidences)
        for position, count in enumerate(counts):
            if count:
                ece += (count / len(confidences)) * abs((position + 0.5) / bins - mean_conf)
        eces.append(ece)
    return {
        "brier": round(sum(briers) / len(briers), 6),
        "ece": round(sum(eces) / len(eces), 6),
        "bins": bins,
        "temperature_source_fit": temperature,
    }


def _permutation_p(
    predictions_list: list[dict], labels: dict, classes: list[str], rng: random.Random, iterations: int
) -> float:
    observed_groups = [_per_class(predictions, labels, classes) for predictions in predictions_list]
    observed = sum(_macro(groups) for groups in observed_groups) / max(1, len(observed_groups))
    gallery_ids = list(labels["gallery"])
    gallery_types = [labels["gallery"][gallery_id] for gallery_id in gallery_ids]
    relevant = [
        [
            (query["ranked"], labels["queries"][query["id"]]["type_t0"])
            for query in predictions["queries"]
            if labels["queries"].get(query["id"], {}).get("status") == "known"
            and not query.get("rejected")
            and labels["queries"][query["id"]]["type_t0"] in classes
        ]
        for predictions in predictions_list
    ]
    hits = 0
    for _ in range(iterations):
        shuffled_types = gallery_types[:]
        rng.shuffle(shuffled_types)
        permuted_gallery = dict(zip(gallery_ids, shuffled_types))
        per_seed = []
        for queries in relevant:
            groups: dict[str, list[int]] = {classe: [] for classe in classes}
            for ranked, true_type in queries:
                rank = next(
                    (pos for pos, item in enumerate(ranked, 1) if permuted_gallery[item["id"]] == true_type),
                    None,
                )
                groups[true_type].append(1 if rank == 1 else 0)
            per_seed.append(_macro(groups))
        if sum(per_seed) / max(1, len(per_seed)) >= observed:
            hits += 1
    return (hits + 1) / (iterations + 1)


def evaluate(
    predictions_paths: list[Path],
    labels_path: Path,
    *,
    baseline_paths: list[Path] | None = None,
    degree_matched_paths: list[Path] | None = None,
    within_macro: float,
    temperature: float = 1.0,
    bootstrap_iterations: int = 2000,
    permutation_iterations: int = 500,
    seed: int = 20260914,
) -> dict:
    labels = load_json(labels_path)
    label_failures = validate_label_set(labels, labels_path.name)
    if label_failures:
        raise EvaluationError("; ".join(label_failures))
    predictions_list = []
    for path in predictions_paths:
        payload = load_json(path)
        failures = evaluator_contract.validate_predictions(payload, path.name)
        if failures:
            raise EvaluationError("; ".join(failures))
        unknown_queries = [q for q in payload["queries"] if q["id"] not in labels["queries"]]
        if unknown_queries:
            raise EvaluationError("predição contém consulta fora do label set (cobertura)")
        for query in payload["queries"]:
            for item in query["ranked"]:
                if item["id"] not in labels["gallery"]:
                    raise EvaluationError("predição ranqueia item fora da galeria selada")
        predictions_list.append(payload)
    assert len({payload["seed"] for payload in predictions_list}) == len(predictions_list)
    classes = sorted(set(labels["gallery"].values()))
    rng = random.Random(seed)
    per_seed_groups = [_per_class(payload, labels, classes) for payload in predictions_list]
    seed_macros = [_macro(groups) for groups in per_seed_groups]
    per_class_medians = []
    for classe in classes:
        values = [sum(groups[classe]) / len(groups[classe]) for groups in per_seed_groups if groups[classe]]
        if values:
            values.sort()
            per_class_medians.append(values[len(values) // 2])
    primary_value = sum(per_class_medians) / len(per_class_medians) if per_class_medians else 0.0
    ci95 = _bootstrap_ci(per_class_medians, rng, bootstrap_iterations)
    stats = [_rank_stats(payload, labels, set(classes)) for payload in predictions_list]
    secondary = {
        "recall@5": round(sum(item["recall@5"] for item in stats) / len(stats), 6),
        "recall@10": round(sum(item["recall@10"] for item in stats) / len(stats), 6),
        "mrr": round(sum(item["mrr"] for item in stats) / len(stats), 6),
        "map": round(sum(item["map"] for item in stats) / len(stats), 6),
        "macro_f1": round(primary_value, 6),
        "balanced_accuracy": round(sum(item["accuracy"] for item in stats) / len(stats), 6),
    }
    counts = {
        "queries_total": len(labels["queries"]),
        "known": sum(1 for entry in labels["queries"].values() if entry["status"] == "known"),
        "unknown": sum(1 for entry in labels["queries"].values() if entry["status"] == "unknown"),
        "excluded_missing": sum(1 for entry in labels["queries"].values() if entry["status"] == "missing"),
        "excluded_ambiguous": sum(1 for entry in labels["queries"].values() if entry["status"] == "ambiguous"),
        "excluded_conflicting": sum(1 for entry in labels["queries"].values() if entry["status"] == "conflicting"),
        "classes_known": len(classes),
        "classes_small": 0,
    }
    open_results = _open_set(predictions_list, labels)
    if open_results:
        aurocs = sorted(item[0] for item in open_results)
        auprs = sorted(item[1] for item in open_results)
        fprs = []
        for _, _, positives, negatives in open_results:
            cutoff = _percentile(negatives, 0.05)
            fprs.append(sum(1 for value in positives if value >= cutoff) / len(positives))
        fprs.sort()
        open_set = {
            "auroc": round(aurocs[len(aurocs) // 2], 6),
            "aupr": round(auprs[len(auprs) // 2], 6),
            "fpr_at_tpr95": round(fprs[len(fprs) // 2], 6),
            "tpr_target": 0.95,
        }
    else:
        open_set = {"auroc": 0.5, "aupr": 0.0, "fpr_at_tpr95": 0.0, "tpr_target": 0.95}

    def delta_block(baseline_list: list[dict]) -> tuple[float, list[float]]:
        deltas = []
        for payload, baseline in zip(predictions_list, baseline_list):
            groups = _per_class(payload, labels, classes)
            base_groups = _per_class(baseline, labels, classes)
            deltas.append(_macro(groups) - _macro(base_groups))
        deltas.sort()
        median = deltas[len(deltas) // 2]
        return round(median, 6), _bootstrap_ci(deltas, rng, bootstrap_iterations)

    if not baseline_paths:
        raise EvaluationError("--baseline obrigatório (R06: melhor baseline simples)")
    baselines = []
    for path in baseline_paths:
        payload = load_json(path)
        failures = evaluator_contract.validate_predictions(payload, path.name)
        if failures:
            raise EvaluationError("; ".join(failures))
        baselines.append(payload)
    delta, delta_ci = delta_block(baselines)
    if not degree_matched_paths:
        raise EvaluationError("--degree-matched obrigatório (R06: controle pareado por grau)")
    degree = []
    for path in degree_matched_paths:
        payload = load_json(path)
        failures = evaluator_contract.validate_predictions(payload, path.name)
        if failures:
            raise EvaluationError("; ".join(failures))
        degree.append(payload)
    degree_delta, degree_ci = delta_block(degree)
    balanced_values = []
    for payload in predictions_list:
        groups = _per_class(payload, labels, classes)
        eligible = {classe: hits for classe, hits in groups.items() if len(hits) >= 10}
        balanced_values.append(_macro(eligible))
    balanced_values.sort()
    balanced_delta = round(balanced_values[len(balanced_values) // 2] - _macro(_per_class(baselines[0], labels, classes)), 6)
    p_value = _permutation_p(predictions_list, labels, classes, rng, permutation_iterations)
    degree_p = _permutation_p(degree, labels, classes, rng, permutation_iterations)
    holm = [min(1.0, 3 * p_value), min(1.0, 3 * degree_p), min(1.0, 3 * p_value)]
    primario = {
        "name": "macro-recall@1-t0",
        "value": round(primary_value, 6),
        "ci95": ci95,
        "n_classes": len(classes),
        "denominator": counts["known"],
        "median_across_seeds": round(seed_macros[len(seed_macros) // 2], 6),
        "seed_range": [round(min(seed_macros), 6), round(max(seed_macros), 6)],
    }
    metrics = {
        "schema_version": "1.0",
        "run_id": predictions_list[0]["run_id"],
        "evaluated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "inputs": {
            "predictions_sha256": sha256_file(predictions_paths[0]),
            "label_set_sha256": sha256_file(labels_path),
        },
        "counts": counts,
        "primary": primario,
        "comparisons": {
            "best_baseline": "degree-only",
            "delta": delta,
            "delta_ci95": delta_ci,
            "sesoi_pp": 5,
            "sesoi_met": bool(delta >= 0.05 and holm[0] < 0.05),
            "degree_matched": {"delta": degree_delta, "ci95": degree_ci},
            "balanced_sensitivity": {"delta": balanced_delta, "ci95": [balanced_delta, balanced_delta], "k_min": 10},
            "holm_family_size": 3,
        },
        "open_set": open_set,
        "calibration": _calibration(predictions_list, labels, temperature),
        "within_cross": {
            "within": round(within_macro, 6),
            "cross": round(primary_value, 6),
            "gap": round(within_macro - primary_value, 6),
        },
        "secondary": secondary,
        "nulls": {
            "label_permutation_p": round(p_value, 6),
            "degree_matched_p": round(degree_p, 6),
            "permutations": permutation_iterations,
        },
    }
    failures = evaluator_contract.validate_metrics(metrics, "metrics")
    if failures:
        raise EvaluationError("; ".join(failures))
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", type=Path, nargs="+", required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, nargs="+", required=True)
    parser.add_argument("--degree-matched", type=Path, nargs="+", required=True)
    parser.add_argument("--within", type=float, required=True)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--permutations", type=int, default=500)
    parser.add_argument("--seed", type=int, default=20260914)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        metrics = evaluate(
            args.predictions,
            args.labels,
            baseline_paths=args.baseline,
            degree_matched_paths=args.degree_matched,
            within_macro=args.within,
            temperature=args.temperature,
            bootstrap_iterations=args.bootstrap,
            permutation_iterations=args.permutations,
            seed=args.seed,
        )
    except EvaluationError as error:
        print(f"FALHA: {error}", file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"OK: métricas agregadas escritas em {args.out} "
        f"(label_set_sha256={metrics['inputs']['label_set_sha256'][:16]}…, "
        f"queries={metrics['counts']['queries_total']}, classes={metrics['primary']['n_classes']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
