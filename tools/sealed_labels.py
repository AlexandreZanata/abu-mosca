#!/usr/bin/env python3
"""Construtor selado do crosswalk e dos conjuntos avaliativos (H07).

Ferramenta do custodiante: transforma mapeamentos ontológicos revisados
manualmente em um label set imutável no schema de H04. Exige **dois revisores
distintos** por mapeamento, com fonte registrada; aplica a regra explícita de
muitos-para-um; sinaliza tipos circulares para sensibilidade; e escreve o
relatório de cobertura apenas com agregados — nenhuma lista por node ID sai da
zona selada.
"""

import argparse
import csv
import hashlib
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import sealed_evaluator  # noqa: E402

LABEL_SCHEMA_VERSION = "1.0"
MAPPING_KINDS = ("one-to-one", "one-to-many", "many-to-one", "many-to-many")
CROSSWALK_REQUIRED = ("crosswalk_version", "dataset_pair", "mappings")
MAPPING_REQUIRED = ("source_type", "target_type", "kind", "reviewer1", "reviewer2", "sources")


class SealedError(RuntimeError):
    pass


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _qid(body) -> str:
    return "q" + sha256_bytes(f"query|{body}".encode())[:16]


def _gid(target_type: str) -> str:
    return "g" + sha256_bytes(f"gallery|{target_type}".encode())[:16]


def validate_crosswalk(payload: dict, label: str = "crosswalk") -> list[str]:
    failures: list[str] = []
    if not isinstance(payload, dict):
        return [f"{label}: deve ser objeto JSON"]
    for field in CROSSWALK_REQUIRED:
        if field not in payload:
            failures.append(f"{label}: campo obrigatório ausente '{field}'")
    mappings = payload.get("mappings")
    if not isinstance(mappings, list) or not mappings:
        failures.append(f"{label}: 'mappings' deve ser lista não vazia")
        return failures
    seen: set[tuple[str, str]] = set()
    for index, mapping in enumerate(mappings):
        item = f"{label}.mappings[{index}]"
        if not isinstance(mapping, dict):
            failures.append(f"{item}: deve ser objeto")
            continue
        for field in MAPPING_REQUIRED:
            if field not in mapping:
                failures.append(f"{item}: campo obrigatório ausente '{field}'")
        if mapping.get("kind") not in MAPPING_KINDS:
            failures.append(f"{item}: 'kind' inválido '{mapping.get('kind')}'")
        reviewer1 = str(mapping.get("reviewer1", "")).strip()
        reviewer2 = str(mapping.get("reviewer2", "")).strip()
        if not reviewer1 or not reviewer2:
            failures.append(f"{item}: dois revisores são obrigatórios")
        elif reviewer1.lower() == reviewer2.lower():
            deviation = payload.get("single_reviewer_deviation") if isinstance(payload, dict) else None
            if not isinstance(deviation, dict) or not deviation.get("changelog_version") or not deviation.get("note"):
                failures.append(f"{item}: revisores devem ser distintos (dupla revisão)")
        sources = mapping.get("sources")
        if not isinstance(sources, list) or not sources:
            failures.append(f"{item}: fonte/proveniência obrigatória em 'sources'")
        key = (str(mapping.get("source_type")), str(mapping.get("target_type")))
        if key in seen:
            failures.append(f"{item}: mapeamento duplicado {key}")
        seen.add(key)
    return failures


def load_annotations(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    bodies = payload.get("bodies")
    if not isinstance(bodies, dict) or not bodies:
        raise SealedError(f"{path.name}: 'bodies' deve ser objeto não vazio")
    return {str(body): str(tipo) for body, tipo in bodies.items()}


def build_label_set(
    crosswalk: dict,
    target_annotations: dict,
    *,
    circular_types: tuple[str, ...] = (),
    ambiguous_types: tuple[str, ...] = (),
    conflicting_types: tuple[str, ...] = (),
) -> tuple[dict, dict]:
    failures = validate_crosswalk(crosswalk)
    if failures:
        raise SealedError("; ".join(failures))
    crosswalk_targets = {str(mapping["target_type"]): str(mapping["source_type"]) for mapping in crosswalk["mappings"]}
    crosswalk_public = {str(mapping["source_type"]): str(mapping["target_type"]) for mapping in crosswalk["mappings"]}
    queries = {}
    status_counts = {"known": 0, "unknown": 0, "missing": 0, "ambiguous": 0, "conflicting": 0}
    type_counts: dict[str, int] = {}
    for body, target_type in target_annotations.items():
        if not target_type or target_type in ("", "nan", "None"):
            status, type_t0 = "missing", None
        elif target_type in ambiguous_types:
            status, type_t0 = "ambiguous", None
        elif target_type in conflicting_types:
            status, type_t0 = "conflicting", None
        elif target_type in crosswalk_targets:
            status, type_t0 = "known", target_type
        else:
            status, type_t0 = "unknown", None
        queries[_qid(body)] = {"status": status, "type_t0": type_t0}
        status_counts[status] += 1
        if status == "known":
            type_counts[target_type] = type_counts.get(target_type, 0) + 1
    gallery = {_gid(target_type): target_type for target_type in sorted(crosswalk_targets)}
    mapping_kinds: dict[str, int] = {}
    for mapping in crosswalk["mappings"]:
        mapping_kinds[mapping["kind"]] = mapping_kinds.get(mapping["kind"], 0) + 1
    deviation = crosswalk.get("single_reviewer_deviation")
    many_to_one = sorted(
        target_type for target_type in crosswalk_targets
        if sum(1 for mapping in crosswalk["mappings"] if mapping["target_type"] == target_type) > 1
    )
    label_set = {
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "crosswalk_version": crosswalk["crosswalk_version"],
        "queries": queries,
        "gallery": gallery,
        "crosswalk": crosswalk_public,
    }
    report = {
        "crosswalk_version": crosswalk["crosswalk_version"],
        "single_reviewer_deviation": deviation,
        "dataset_pair": crosswalk.get("dataset_pair"),
        "mappings": len(crosswalk["mappings"]),
        "mapping_kinds": mapping_kinds,
        "many_to_one_groups": many_to_one,
        "status_counts": status_counts,
        "classes_known": len(gallery),
        "types_with_coverage": {tipo: count for tipo, count in sorted(type_counts.items())},
        "circular_types_flagged": sorted(circular_types),
        "reviewers": sorted({str(m["reviewer1"]) for m in crosswalk["mappings"]} | {str(m["reviewer2"]) for m in crosswalk["mappings"]}),
        "sources_used": sorted({str(source) for m in crosswalk["mappings"] for source in m["sources"]}),
    }
    return label_set, report


def _csv_to_annotations(text: str) -> dict:
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames != ["body", "type"]:
        raise SealedError("CSV de anotações deve ter cabeçalho 'body,type'")
    return {row["body"]: row["type"] for row in reader}


def require_sealed_dir(out_path: Path, sealed_dir: Path) -> None:
    sealed_root = sealed_dir.resolve()
    target = out_path.resolve()
    if sealed_root not in target.parents:
        raise SealedError(f"saída deve ficar dentro de {sealed_root.name}/ (zona selada)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--crosswalk", type=Path, required=True)
    parser.add_argument("--target-annotations", type=Path, required=True)
    parser.add_argument("--sealed-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--circular-types", nargs="*", default=[])
    parser.add_argument("--ambiguous-types", nargs="*", default=[])
    parser.add_argument("--conflicting-types", nargs="*", default=[])
    args = parser.parse_args()
    try:
        crosswalk = json.loads(args.crosswalk.read_text(encoding="utf-8"))
        if args.target_annotations.suffix == ".csv":
            annotations = _csv_to_annotations(args.target_annotations.read_text(encoding="utf-8"))
        else:
            annotations = load_annotations(args.target_annotations)
        require_sealed_dir(args.out, args.sealed_dir)
        require_sealed_dir(args.report, args.sealed_dir)
        label_set, report = build_label_set(
            crosswalk,
            annotations,
            circular_types=tuple(args.circular_types),
            ambiguous_types=tuple(args.ambiguous_types),
            conflicting_types=tuple(args.conflicting_types),
        )
        failures = sealed_evaluator.validate_label_set(label_set, args.out.name)
        if failures:
            raise SealedError("; ".join(failures))
        sealed_bytes = (json.dumps(label_set, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
        args.sealed_dir.mkdir(parents=True, exist_ok=True)
        args.out.write_bytes(sealed_bytes)
        report["label_set_sha256"] = sha256_bytes(sealed_bytes)
        report["crosswalk_sha256"] = sha256_bytes(args.crosswalk.read_bytes())
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({k: v for k, v in report.items() if k != "types_with_coverage"}, ensure_ascii=False, sort_keys=True))
        return 0
    except (SealedError, json.JSONDecodeError) as error:
        print(f"FALHA: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
