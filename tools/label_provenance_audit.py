#!/usr/bin/env python3
"""Auditoria de proveniência dos rótulos tipo a tipo (reformulação H07).

Verifica, por tipo do alvo, quais canais de evidência existem nas anotações
públicas auditadas do MCNS (`male-cns:v1.0`, LIT-0079/D07): genético
(`fruDsx`), linhagem (`trumanHl`/`itoleeHl`), correspondência entre datasets
(`flywireType`/`hemibrainType`/`vfbId`) ou apenas curadoria manual — esta última
usa conectividade/morfologia e é circular para o desfecho primário. Também
calcula a cobertura (K=10, sem scores) de rótulos alternativos com canal
independente (genético e linhagem) para eventual reformulação do desfecho.
"""

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pyarrow.feather as feather

ROOT = Path(__file__).resolve().parent.parent
K_MIN = 10
CHANNELS = ("genetic", "lineage", "cross_dataset", "manual_only")


class AuditError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def _filled(value) -> bool:
    return value not in (None, "", "nan", "TBD")


def audit(annotations: Path) -> dict:
    table = feather.read_table(annotations, memory_map=True)
    required = ("type", "fruDsx", "trumanHl", "itoleeHl", "flywireType", "hemibrainType", "vfbId", "mancType")
    for column in required:
        if column not in table.column_names:
            raise AuditError(f"coluna obrigatória ausente: {column}")
    columns = {name: table[name].to_pylist() for name in required}
    channel_by_type: dict[str, Counter] = defaultdict(Counter)
    genes_by_type: dict[str, Counter] = defaultdict(Counter)
    lineage_counts: Counter = Counter()
    genetic_counts: Counter = Counter()
    types_seen: set[str] = set()
    for index, tipo in enumerate(columns["type"]):
        if not _filled(tipo):
            continue
        types_seen.add(tipo)
        genetic = _filled(columns["fruDsx"][index])
        lineage = _filled(columns["trumanHl"][index]) or _filled(columns["itoleeHl"][index])
        cross = (
            _filled(columns["flywireType"][index])
            or _filled(columns["hemibrainType"][index])
            or _filled(columns["vfbId"][index])
        )
        if genetic:
            channel_by_type[tipo]["genetic"] += 1
            genetic_counts[columns["fruDsx"][index]] += 1
        if lineage:
            channel_by_type[tipo]["lineage"] += 1
            if _filled(columns["trumanHl"][index]):
                lineage_counts[columns["trumanHl"][index]] += 1
        if cross:
            channel_by_type[tipo]["cross_dataset"] += 1
        if not (genetic or lineage or cross):
            channel_by_type[tipo]["manual_only"] += 1
    type_channels = Counter()
    for tipo, channels in channel_by_type.items():
        for name in CHANNELS:
            if channels.get(name):
                type_channels[name] += 1
    independent_types = sorted(
        tipo for tipo, channels in channel_by_type.items()
        if channels.get("genetic") and channels.get("manual_only", 0) == 0
    )
    independent_genetic = sorted(
        tipo for tipo, channels in channel_by_type.items()
        if channels.get("genetic") and channels.get("manual_only", 0) == 0 and channels.get("cross_dataset", 0) == 0
    )

    def coverage(counts: Counter) -> dict:
        classes = {name: total for name, total in counts.items() if total >= K_MIN}
        return {
            "classes_total": len(counts),
            "classes_with_k_min": len(classes),
            "neurons_in_covered_classes": sum(classes.values()),
            "smallest_covered_class": min(classes.values()) if classes else 0,
            "largest_covered_class": max(classes.values()) if classes else 0,
        }

    return {
        "annotations_sha256": sha256_file(annotations),
        "types_seen": len(types_seen),
        "k_min": K_MIN,
        "channels_by_type": dict(type_channels),
        "types_with_genetic_and_no_manual_only": len(independent_types),
        "types_with_genetic_only": len(independent_genetic),
        "genetic_label_coverage": coverage(genetic_counts),
        "lineage_label_coverage": coverage(lineage_counts),
        "genetic_classes": dict(sorted(genetic_counts.items())),
        "lineage_classes_with_k_min": sorted(name for name, total in lineage_counts.items() if total >= K_MIN),
        "conclusion": {
            "non_circular_subset_for_t0_types": False,
            "reason": (
                "todos os tipos do alvo foram curados com conectividade/morfologia (LIT-0023/D07); "
                "nenhuma evidência pública documenta tipos atribuídos sem esses canais"
            ),
            "primary_benchmark": "inconclusivo por circularidade",
            "reformulation_options": [
                "trocar o desfecho primário para rótulo genético (fruDsx) com K=10 e novo pré-registro",
                "trocar para linhagem de desenvolvimento (trumanHl) com K=10 e novo pré-registro",
                "manter T0 apenas exploratório e declarar o benchmark primário inconclusivo",
                "buscar outro par de datasets com proveniência de rótulo independente",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = audit(args.annotations)
    except (AuditError, FileNotFoundError) as error:
        print(f"FALHA: {error}", file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("types_seen", "channels_by_type", "genetic_label_coverage", "lineage_label_coverage", "conclusion")}, ensure_ascii=False, sort_keys=True)[:800])
    return 0


if __name__ == "__main__":
    sys.exit(main())
