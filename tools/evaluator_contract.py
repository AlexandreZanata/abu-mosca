#!/usr/bin/env python3
"""Contrato do avaliador selado: valida predições e métricas (R06).

Implementa em Python as mesmas regras de `schemas/predictions.schema.json` e
`schemas/metrics.schema.json`, sem dependências externas, e falha se o pacote
contiver rótulos, IDs crus ou resultados por neurônio.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREDICTIONS_SCHEMA = ROOT / "schemas" / "predictions.schema.json"
METRICS_SCHEMA = ROOT / "schemas" / "metrics.schema.json"

PREDICTIONS_REQUIRED = ("schema_version", "run_id", "seed", "gallery", "queries")
METRICS_REQUIRED = (
    "schema_version",
    "run_id",
    "evaluated_at",
    "inputs",
    "counts",
    "primary",
    "comparisons",
    "open_set",
    "calibration",
    "within_cross",
    "secondary",
    "nulls",
)
RUN_ID_RE = re.compile(r"^[0-9a-f]{16}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
QUERY_RE = re.compile(r"^q[0-9a-f]{16}$")
GALLERY_RE = re.compile(r"^g[0-9a-f]{16}$")
RAW_ID_RE = re.compile(r"\b\d{9,}\b")
FORBIDDEN_KEYS = {
    "label", "labels", "type", "true_type", "target_type", "cell_type", "celltype",
    "bodyid", "body_id", "root_id", "neuron_id", "id_map", "qid_map",
}
FORBIDDEN_SUBSTRINGS = ("per_query", "per_node", "example", "true_type", "target_type")


def _forbidden_key(key: str) -> bool:
    lowered = str(key).lower()
    return lowered in FORBIDDEN_KEYS or any(token in lowered for token in FORBIDDEN_SUBSTRINGS)


def _scan_labels_and_ids(node, path: str, failures: list[str]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if _forbidden_key(key):
                failures.append(f"{path}: chave proibida no pacote '{key}'")
            _scan_labels_and_ids(value, f"{path}.{key}", failures)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            _scan_labels_and_ids(value, f"{path}[{index}]", failures)
    elif isinstance(node, str):
        match = RAW_ID_RE.search(node)
        if match:
            failures.append(f"{path}: possível ID cru de neurônio ('{match.group(0)}')")


def _check_interval(value, label: str, failures: list[str], low=0.0, high=1.0) -> None:
    if (
        not isinstance(value, list)
        or len(value) != 2
        or not all(isinstance(item, (int, float)) and low <= item <= high for item in value)
    ):
        failures.append(f"{label}: esperado intervalo [baixo, alto] entre {low} e {high}")


def validate_predictions(payload: dict, label: str = "predictions") -> list[str]:
    failures: list[str] = []
    if not isinstance(payload, dict):
        return [f"{label}: raiz deve ser um objeto JSON"]
    for field in PREDICTIONS_REQUIRED:
        if field not in payload:
            failures.append(f"{label}: campo obrigatório ausente '{field}'")
    for field in payload:
        if field not in PREDICTIONS_REQUIRED:
            failures.append(f"{label}: campo inesperado '{field}'")
    if payload.get("schema_version") != "1.0":
        failures.append(f"{label}: schema_version deve ser '1.0'")
    if not isinstance(payload.get("run_id"), str) or not RUN_ID_RE.match(payload["run_id"]):
        failures.append(f"{label}: run_id deve ter 16 hexadecimais minúsculos")
    seed = payload.get("seed")
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
        failures.append(f"{label}: seed deve ser inteiro não negativo")
    gallery = payload.get("gallery")
    if not isinstance(gallery, dict) or not all(
        isinstance(gallery.get(key), int) and gallery[key] >= 1 for key in ("nodes", "types")
    ):
        failures.append(f"{label}: gallery deve ter 'nodes' e 'types' inteiros positivos")
    queries = payload.get("queries")
    if not isinstance(queries, list) or not queries:
        failures.append(f"{label}: 'queries' deve ser lista não vazia")
        return failures
    for index, query in enumerate(queries):
        item = f"{label}.queries[{index}]"
        if not isinstance(query, dict):
            failures.append(f"{item}: consulta deve ser objeto")
            continue
        for field in query:
            if field not in ("id", "ranked", "rejected"):
                failures.append(f"{item}: campo inesperado '{field}'")
        if not isinstance(query.get("id"), str) or not QUERY_RE.match(query["id"]):
            failures.append(f"{item}: id opaco deve casar q<16 hex>")
        ranked = query.get("ranked")
        if not isinstance(ranked, list) or not 1 <= len(ranked) <= 10:
            failures.append(f"{item}: 'ranked' deve ter entre 1 e 10 itens")
        else:
            for position, entry in enumerate(ranked):
                if not isinstance(entry, dict) or "id" not in entry or "score" not in entry:
                    failures.append(f"{item}.ranked[{position}]: esperado id e score")
                    continue
                if not isinstance(entry["id"], str) or not GALLERY_RE.match(entry["id"]):
                    failures.append(f"{item}.ranked[{position}]: id de galeria deve casar g<16 hex>")
                if not isinstance(entry["score"], (int, float)) or isinstance(entry["score"], bool):
                    failures.append(f"{item}.ranked[{position}]: score deve ser número")
        if "rejected" in query and not isinstance(query["rejected"], bool):
            failures.append(f"{item}: 'rejected' deve ser booleano")
    _scan_labels_and_ids(payload, label, failures)
    return failures


def validate_metrics(payload: dict, label: str = "metrics") -> list[str]:
    failures: list[str] = []
    if not isinstance(payload, dict):
        return [f"{label}: raiz deve ser um objeto JSON"]
    for field in METRICS_REQUIRED:
        if field not in payload:
            failures.append(f"{label}: campo obrigatório ausente '{field}'")
    for field in payload:
        if field not in METRICS_REQUIRED + ("sensitivity_circular_labels", "notes"):
            failures.append(f"{label}: campo inesperado '{field}'")
    if payload.get("schema_version") != "1.0":
        failures.append(f"{label}: schema_version deve ser '1.0'")
    if not isinstance(payload.get("run_id"), str) or not RUN_ID_RE.match(payload["run_id"]):
        failures.append(f"{label}: run_id deve ter 16 hexadecimais minúsculos")
    inputs = payload.get("inputs")
    if not isinstance(inputs, dict) or any(
        not isinstance(inputs.get(key), str) or not SHA256_RE.match(inputs[key])
        for key in ("predictions_sha256", "label_set_sha256")
    ):
        failures.append(f"{label}: inputs deve conter predictions_sha256 e label_set_sha256")
    counts = payload.get("counts")
    if not isinstance(counts, dict) or any(
        not isinstance(counts.get(key), int) or counts[key] < 0 for key in (
            "queries_total", "known", "unknown", "excluded_missing",
            "excluded_ambiguous", "excluded_conflicting", "classes_known", "classes_small",
        )
    ):
        failures.append(f"{label}: counts incompletos ou negativos")
    primary = payload.get("primary")
    if not isinstance(primary, dict):
        failures.append(f"{label}: 'primary' deve ser objeto")
    else:
        if primary.get("name") != "macro-recall@1-t0":
            failures.append(f"{label}: métrica primária deve ser 'macro-recall@1-t0'")
        for key in ("value", "median_across_seeds"):
            if not isinstance(primary.get(key), (int, float)) or isinstance(primary.get(key), bool) or not 0 <= primary[key] <= 1:
                failures.append(f"{label}.primary: '{key}' deve estar em [0,1]")
        _check_interval(primary.get("ci95"), f"{label}.primary.ci95", failures)
        _check_interval(primary.get("seed_range"), f"{label}.primary.seed_range", failures)
        if not isinstance(primary.get("n_classes"), int) or primary["n_classes"] < 1:
            failures.append(f"{label}.primary: 'n_classes' deve ser inteiro positivo")
        if not isinstance(primary.get("denominator"), int) or primary["denominator"] < 1:
            failures.append(f"{label}.primary: 'denominator' deve ser inteiro positivo")
    comparisons = payload.get("comparisons")
    if not isinstance(comparisons, dict):
        failures.append(f"{label}: 'comparisons' deve ser objeto")
    else:
        if comparisons.get("sesoi_pp") != 5:
            failures.append(f"{label}.comparisons: SESOI deve ser 5 pontos percentuais")
        if comparisons.get("holm_family_size") != 3:
            failures.append(f"{label}.comparisons: família Holm deve ter tamanho 3")
        for key in ("delta", "delta_ci95"):
            if key not in comparisons:
                failures.append(f"{label}.comparisons: campo ausente '{key}'")
        _check_interval(comparisons.get("delta_ci95"), f"{label}.comparisons.delta_ci95", failures, -1.0, 1.0)
        for block, key_ci in (("degree_matched", "ci95"), ("balanced_sensitivity", "ci95")):
            sub = comparisons.get(block)
            if not isinstance(sub, dict):
                failures.append(f"{label}.comparisons: bloco ausente '{block}'")
                continue
            _check_interval(sub.get(key_ci), f"{label}.comparisons.{block}.{key_ci}", failures, -1.0, 1.0)
            if block == "balanced_sensitivity" and not isinstance(sub.get("k_min"), int):
                failures.append(f"{label}.comparisons.balanced_sensitivity: 'k_min' deve ser inteiro")
        if not isinstance(comparisons.get("sesoi_met"), bool):
            failures.append(f"{label}.comparisons: 'sesoi_met' deve ser booleano")
    open_set = payload.get("open_set")
    if not isinstance(open_set, dict) or open_set.get("tpr_target") != 0.95:
        failures.append(f"{label}: open_set deve fixar TPR = 0,95")
    calibration = payload.get("calibration")
    if not isinstance(calibration, dict) or calibration.get("bins") != 15:
        failures.append(f"{label}: calibração deve usar 15 bins fixos")
    _scan_labels_and_ids(payload, label, failures)
    return failures


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate",))
    parser.add_argument("kind", choices=("predictions", "metrics"))
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    payload = load(args.path)
    failures = (
        validate_predictions(payload, args.path.name)
        if args.kind == "predictions"
        else validate_metrics(payload, args.path.name)
    )
    if failures:
        for failure in failures:
            print(f"FALHA: {failure}")
        return 1
    print(f"OK: {args.kind} válido e sem rótulos/IDs crus ({args.path})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
