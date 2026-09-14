import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import sealed_evaluator as se  # noqa: E402
import sealed_labels as sl  # noqa: E402


def crosswalk(reviewer2: str = "Revisor B") -> dict:
    return {
        "crosswalk_version": "sintetico-1.0",
        "dataset_pair": ["FONTE", "ALVO"],
        "mappings": [
            {
                "source_type": "S1",
                "target_type": "T1",
                "kind": "one-to-one",
                "reviewer1": "Revisor A",
                "reviewer2": reviewer2,
                "sources": ["LIT-9999"],
            },
            {
                "source_type": "S2",
                "target_type": "T1",
                "kind": "many-to-one",
                "reviewer1": "Revisor A",
                "reviewer2": reviewer2,
                "sources": ["LIT-9999"],
            },
            {
                "source_type": "S3",
                "target_type": "T2",
                "kind": "one-to-one",
                "reviewer1": "Revisor A",
                "reviewer2": reviewer2,
                "sources": ["LIT-9999"],
            },
        ],
    }


def annotations() -> dict:
    return {"b": "T1", "b2": "T2", "b3": "T9", "b4": "", "b5": "T2"}


def test_constroi_label_set_valido_e_cobertura():
    label_set, report = sl.build_label_set(crosswalk(), annotations())
    assert se.validate_label_set(label_set) == []
    counts = report["status_counts"]
    assert counts == {"known": 3, "unknown": 1, "missing": 1, "ambiguous": 0, "conflicting": 0}
    assert report["many_to_one_groups"] == ["T1"]
    assert report["classes_known"] == 2
    assert report["types_with_coverage"]["T1"] == 1


def test_dupla_revisao_obrigatoria():
    with pytest.raises(sl.SealedError, match="distintos"):
        sl.build_label_set(crosswalk(reviewer2="Revisor A"), annotations())
    payload = crosswalk()
    payload["mappings"][0]["reviewer2"] = " "
    with pytest.raises(sl.SealedError, match="dois revisores"):
        sl.build_label_set(payload, annotations())


def test_ambiguos_e_conflitantes_excluidos():
    label_set, report = sl.build_label_set(
        crosswalk(), annotations(), ambiguous_types=("T2",), conflicting_types=("T1",)
    )
    statuses = [entry["status"] for entry in label_set["queries"].values()]
    assert statuses.count("ambiguous") == 2
    assert statuses.count("conflicting") == 1
    assert report["status_counts"]["known"] == 0


def test_relatorio_nao_vaza_ids():
    _, report = sl.build_label_set(crosswalk(), annotations(), circular_types=("T2",))
    serialized = json.dumps(report)
    assert not re.search(r"[qg][0-9a-f]{16}", serialized)
    assert "b3" not in serialized and "b4" not in serialized
    assert report["circular_types_flagged"] == ["T2"]


def test_exige_saida_dentro_da_zona_selada(tmp_path):
    out = tmp_path / "fora" / "labels.json"
    sealed = tmp_path / "sealed"
    with pytest.raises(sl.SealedError, match="selada"):
        sl.require_sealed_dir(out, sealed)
    inside = sealed / "target-labels" / "labels.json"
    sl.require_sealed_dir(inside, sealed)


def test_cli_ponta_a_ponta_em_zona_selada(tmp_path):
    sealed = tmp_path / "data" / "sealed"
    crosswalk_path = tmp_path / "crosswalk.json"
    crosswalk_path.write_text(json.dumps(crosswalk()), encoding="utf-8")
    annotations_path = tmp_path / "annotations.json"
    annotations_path.write_text(json.dumps({"bodies": annotations()}), encoding="utf-8")
    out = sealed / "labels.json"
    report_path = sealed / "coverage.json"
    import subprocess

    result = subprocess.run(
        [
            sys.executable, str(ROOT / "tools" / "sealed_labels.py"),
            "--crosswalk", str(crosswalk_path),
            "--target-annotations", str(annotations_path),
            "--sealed-dir", str(sealed),
            "--out", str(out),
            "--report", str(report_path),
            "--circular-types", "T2",
        ],
        capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, result.stderr
    label_set = json.loads(out.read_text(encoding="utf-8"))
    assert se.validate_label_set(label_set) == []
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["label_set_sha256"] == sl.sha256_bytes(out.read_bytes())
    assert "T2" in report["circular_types_flagged"]
