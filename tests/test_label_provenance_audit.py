import json
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.feather as feather
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import label_provenance_audit as audit  # noqa: E402


def write_annotations(tmp_path: Path, rows: list[dict]) -> Path:
    columns = {name: [] for name in ("type", "fruDsx", "trumanHl", "itoleeHl", "flywireType", "hemibrainType", "vfbId", "mancType")}
    for row in rows:
        for name in columns:
            columns[name].append(row.get(name))
    path = tmp_path / "annotations.feather"
    feather.write_feather(pa.table(columns), path)
    return path


def test_canais_e_conclusao(tmp_path):
    rows = [
        {"type": "T1", "fruDsx": "fru_high"},                      # genético
        {"type": "T1", "fruDsx": "fru_high"},
        {"type": "T2", "trumanHl": "03B"},                          # linhagem
        {"type": "T2", "trumanHl": "03B"},
        {"type": "T3", "flywireType": "X"},                         # correspondência
        {"type": "T4", "mancType": "M1"},                           # manual apenas
    ]
    report = audit.audit(write_annotations(tmp_path, rows))
    assert report["types_seen"] == 4
    assert report["channels_by_type"] == {"genetic": 1, "lineage": 1, "cross_dataset": 1, "manual_only": 1}
    assert report["conclusion"]["non_circular_subset_for_t0_types"] is False
    assert report["conclusion"]["primary_benchmark"] == "inconclusivo por circularidade"
    assert report["conclusion"]["reformulation_options"]


def test_cobertura_k_min(tmp_path):
    rows = []
    for index in range(12):
        rows.append({"type": f"T{index}", "fruDsx": "fru_high"})
    rows.append({"type": "Tsmall", "fruDsx": "dsx_low"})
    report = audit.audit(write_annotations(tmp_path, rows))
    coverage = report["genetic_label_coverage"]
    assert coverage["classes_total"] == 2
    assert coverage["classes_with_k_min"] == 1
    assert coverage["smallest_covered_class"] == 12
    assert coverage["neurons_in_covered_classes"] == 12


def test_tbd_nao_conta_como_evidencia(tmp_path):
    rows = [{"type": "T1", "trumanHl": "TBD", "flywireType": "X"}]
    report = audit.audit(write_annotations(tmp_path, rows))
    assert report["channels_by_type"].get("lineage") is None
    assert report["lineage_label_coverage"]["classes_total"] == 0


def test_relatorio_nao_tem_ids_de_neuronio(tmp_path):
    path = write_annotations(tmp_path, [{"type": "T1", "fruDsx": "fru_low"}])
    report = audit.audit(path)
    serialized = json.dumps(report)
    for token in ("bodyId", "root_id", "123456789"):
        assert token not in serialized
