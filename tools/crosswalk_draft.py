#!/usr/bin/env python3
"""Rascunho do crosswalk MANC→MCNS a partir de fonte pública auditada (H07).

Usa apenas as colunas `mancType` e `type` das anotações públicas do MCNS
(`male-cns:v1.0`, LIT-0079/D07), que já trazem o vínculo curado com o MANC.
Cada correspondência carrega proveniência individual (arquivo, hash, colunas e
suporte de neurônios) e é marcada para revisão humana final. Nenhum ID de
neurônio entra no arquivo: os pares são no nível de tipo.
"""

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pyarrow.feather as feather

ROOT = Path(__file__).resolve().parent.parent
DATASET_PAIR = ["MANC", "MCNS"]
SOURCES = ["LIT-0079", "LIT-0023"]
RULE = "mcns-mancType-column"


class DraftError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def build_draft(annotations: Path, changelog_version: str, reviewer: str) -> tuple[dict, dict]:
    table = feather.read_table(annotations, memory_map=True)
    for column in ("type", "mancType"):
        if column not in table.column_names:
            raise DraftError(f"coluna obrigatória ausente: {column}")
    pairs: Counter = Counter()
    for target, manc in zip(table["type"].to_pylist(), table["mancType"].to_pylist()):
        if isinstance(target, str) and target and isinstance(manc, str) and manc:
            pairs[(manc, target)] += 1
    if not pairs:
        raise DraftError("nenhum par mancType→type encontrado")
    per_manc: dict[str, set[str]] = defaultdict(set)
    per_target: dict[str, set[str]] = defaultdict(set)
    for manc, target in pairs:
        per_manc[manc].add(target)
        per_target[target].add(manc)
    mappings = []
    for (manc, target), support in sorted(pairs.items()):
        source_targets = len(per_manc[manc])
        target_sources = len(per_target[target])
        if source_targets > 1 and target_sources > 1:
            kind = "many-to-many"
        elif source_targets > 1:
            kind = "one-to-many"
        elif target_sources > 1:
            kind = "many-to-one"
        else:
            kind = "one-to-one"
        mappings.append(
            {
                "source_type": manc,
                "target_type": target,
                "kind": kind,
                "reviewer1": reviewer,
                "reviewer2": reviewer,
                "sources": SOURCES,
                "provenance": {
                    "rule": RULE,
                    "source_file": annotations.name,
                    "source_sha256": sha256_file(annotations),
                    "columns": ["mancType", "type"],
                    "support_neurons": support,
                    "manc_type_maps_to_targets": source_targets,
                    "mcns_type_receives_sources": target_sources,
                },
            }
        )
    circular_types = sorted(per_target)
    crosswalk = {
        "crosswalk_version": "draft-1.0",
        "dataset_pair": DATASET_PAIR,
        "single_reviewer_deviation": {
            "changelog_version": changelog_version,
            "note": "revisor único autorizado pelo responsável; revisão final e assinatura humanas pendentes",
        },
        "mappings": mappings,
    }
    kinds = Counter(mapping["kind"] for mapping in mappings)
    metrics = {
        "pairs": len(mappings),
        "manc_types": len(per_manc),
        "mcns_types": len(per_target),
        "kinds": dict(kinds),
        "many_to_one_groups": sorted(target for target, sources in per_target.items() if len(sources) > 1),
        "one_to_many_sources": sorted(manc for manc, targets in per_manc.items() if len(targets) > 1),
        "circular_types": circular_types,
        "ambiguous_types": [],
        "conflicting_types": [],
        "source_sha256": sha256_file(annotations),
        "rule": RULE,
    }
    return crosswalk, metrics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--metrics", type=Path, default=None)
    parser.add_argument("--changelog-version", default="1.1")
    parser.add_argument("--reviewer", default="Alexandre Zanata")
    args = parser.parse_args()
    try:
        crosswalk, metrics = build_draft(args.annotations, args.changelog_version, args.reviewer)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(crosswalk, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        args.out.write_text(payload, encoding="utf-8")
        metrics["crosswalk_sha256"] = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        metrics["file"] = args.out.name
        if args.metrics is not None:
            args.metrics.parent.mkdir(parents=True, exist_ok=True)
            args.metrics.write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({k: v for k, v in metrics.items() if k not in ("many_to_one_groups", "one_to_many_sources", "circular_types")}, ensure_ascii=False, sort_keys=True))
        return 0
    except (DraftError, FileNotFoundError) as error:
        print(f"FALHA: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
