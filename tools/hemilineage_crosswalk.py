#!/usr/bin/env python3
"""Crosswalk reformulado por hemilinhagem de desenvolvimento (reformulação H07).

Casa `hemilineage` do MANC com `trumanHl` do MCNS por normalização conservadora
(maiúsculas, remoção de sufixos `_putN`, exclusão de `TBD`/ausentes) e calcula a
interseção com K≥10 **nos dois lados**, sem consultar scores. Gera o rascunho do
crosswalk (nível de classe, sem IDs de neurônio), métricas de cobertura e lista
de rótulos incertos (juntas/X) para revisão humana.
"""

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import pyarrow.feather as feather

ROOT = Path(__file__).resolve().parent.parent
K_MIN = 10
EXCLUDED_LABELS = ("20A.22A", "20B.21B.22B", "24B.25B", "26X", "27X")
MANC_DATASET, MANC_RELEASE = "MANC", "manc:v1.2.1"
MCNS_DATASET, MCNS_RELEASE = "MCNS", "male-cns:v1.0"
MANC_SHA = "data/raw/spikes/manc_neuron_properties.feather"
MCNS_SHA = "data/raw/spikes/mcns_body_annotations.feather"


class CrosswalkError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def normalize(value) -> str | None:
    if value in (None, "", "nan"):
        return None
    text = str(value).strip().upper()
    if text in ("TBD", "NONE"):
        return None
    text = text.split("_")[0].strip()
    return text or None


def is_uncertain(label: str) -> bool:
    return label.endswith("X") or "." in label


def build(manc_path: Path, mcns_path: Path, reviewer: str, changelog_version: str) -> tuple[dict, dict]:
    manc = feather.read_table(manc_path, memory_map=True)
    mcns = feather.read_table(mcns_path, memory_map=True)
    for table, column in ((manc, "hemilineage"), (mcns, "trumanHl")):
        if column not in table.column_names:
            raise CrosswalkError(f"coluna obrigatória ausente: {column}")
    manc_counts: Counter = Counter(filter(None, (normalize(v) for v in manc["hemilineage"].to_pylist())))
    mcns_counts: Counter = Counter(filter(None, (normalize(v) for v in mcns["trumanHl"].to_pylist())))
    shared = sorted(set(manc_counts) & set(mcns_counts))
    both = [
        label for label in shared
        if manc_counts[label] >= K_MIN and mcns_counts[label] >= K_MIN and label not in EXCLUDED_LABELS
    ]
    if not both:
        raise CrosswalkError("nenhuma hemilinhagem com K≥10 nos dois lados")
    uncertain = [label for label in both if is_uncertain(label)]
    mappings = []
    for label in both:
        mappings.append(
            {
                "source_type": label,
                "target_type": label,
                "kind": "one-to-one",
                "reviewer1": reviewer,
                "reviewer2": reviewer,
                "sources": ["LIT-0015", "LIT-0023"],
                "provenance": {
                    "rule": "normalized-hemilineage==trumanHl",
                    "source_file": manc_path.name,
                    "source_sha256": sha256_file(manc_path),
                    "target_file": mcns_path.name,
                    "target_sha256": sha256_file(mcns_path),
                    "columns": ["hemilineage", "trumanHl"],
                    "manc_neurons": manc_counts[label],
                    "mcns_neurons": mcns_counts[label],
                    "uncertain_label": is_uncertain(label),
                },
            }
        )
    crosswalk = {
        "crosswalk_version": "hemilineage-2.0-draft",
        "dataset_pair": [MANC_DATASET, MCNS_DATASET],
        "single_reviewer_deviation": {
            "changelog_version": changelog_version,
            "note": "revisão única autorizada; revisão final e assinatura humanas pendentes",
        },
        "mappings": mappings,
    }
    metrics = {
        "shared_labels": len(shared),
        "classes_k_min_both": len(both),
        "uncertain_labels": uncertain,
        "excluded_uncertain_labels": list(EXCLUDED_LABELS),
        "excluded_labels": sorted(set(shared) - set(both)) + ["TBD", "ausentes"],
        "classes": [
            {
                "label": label,
                "manc_neurons": manc_counts[label],
                "mcns_neurons": mcns_counts[label],
                "uncertain": is_uncertain(label),
            }
            for label in both
        ],
        "k_min": K_MIN,
        "source_sha256": sha256_file(manc_path),
        "target_sha256": sha256_file(mcns_path),
    }
    return crosswalk, metrics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manc", type=Path, default=ROOT / MANC_SHA)
    parser.add_argument("--mcns", type=Path, default=ROOT / MCNS_SHA)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--metrics", type=Path, default=None)
    parser.add_argument("--reviewer", default="Alexandre Zanata")
    parser.add_argument("--changelog-version", default="2.0-draft")
    args = parser.parse_args()
    try:
        crosswalk, metrics = build(args.manc, args.mcns, args.reviewer, args.changelog_version)
    except (CrosswalkError, FileNotFoundError) as error:
        print(f"FALHA: {error}", file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(crosswalk, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    args.out.write_text(payload, encoding="utf-8")
    metrics["crosswalk_sha256"] = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    metrics["file"] = args.out.name
    if args.metrics is not None:
        args.metrics.parent.mkdir(parents=True, exist_ok=True)
        args.metrics.write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in metrics.items() if k != "classes"}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
