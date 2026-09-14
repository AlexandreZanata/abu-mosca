import json
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.feather as feather
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import hemilineage_crosswalk as hc  # noqa: E402


def write_tables(tmp_path: Path, manc_values: list, mcns_values: list) -> tuple[Path, Path]:
    manc = tmp_path / "manc.feather"
    mcns = tmp_path / "mcns.feather"
    feather.write_feather(pa.table({"hemilineage": pa.array(manc_values, type=pa.string())}), manc)
    feather.write_feather(pa.table({"trumanHl": pa.array(mcns_values, type=pa.string())}), mcns)
    return manc, mcns


def test_normalizacao_e_intersecao_k_min(tmp_path):
    manc_values = ["03B"] * 12 + ["07B"] * 12 + ["01A"] * 9 + ["TBD", None]
    mcns_values = ["03B"] * 10 + ["07B"] * 12 + ["01A"] * 12 + ["09B"]
    manc, mcns = write_tables(tmp_path, manc_values, mcns_values)
    crosswalk, metrics = hc.build(manc, mcns, "Alexandre Zanata", "2.0-draft")
    labels = [mapping["source_type"] for mapping in crosswalk["mappings"]]
    assert "03B" in labels and "07B" in labels
    assert "01A" not in labels  # K<10 no MANC
    assert metrics["shared_labels"] == 3
    assert metrics["classes_k_min_both"] == 2
    assert all(mapping["provenance"]["manc_neurons"] >= 10 for mapping in crosswalk["mappings"])
    assert crosswalk["single_reviewer_deviation"]["changelog_version"] == "2.0-draft"


def test_rotulos_incertos_marcados(tmp_path):
    manc = ["20A.22A"] * 10 + ["26X"] * 10 + ["05B"] * 10
    mcns = ["20A.22A"] * 10 + ["26X"] * 10 + ["05B"] * 10
    manc_path, mcns_path = write_tables(tmp_path, manc, mcns)
    crosswalk, metrics = hc.build(manc_path, mcns_path, "A", "2.0-draft")
    assert set(metrics["uncertain_labels"]) == {"20A.22A", "26X"}
    assert all(
        mapping["provenance"]["uncertain_label"] is True
        for mapping in crosswalk["mappings"]
        if mapping["source_type"] in metrics["uncertain_labels"]
    )


def test_sem_ids_de_neuronio(tmp_path):
    manc_path, mcns_path = write_tables(tmp_path, ["05B"] * 10, ["05B"] * 10)
    crosswalk, metrics = hc.build(manc_path, mcns_path, "A", "2.0-draft")
    serialized = json.dumps(crosswalk) + json.dumps(metrics)
    for token in ("bodyId", "root_id", "123456789"):
        assert token not in serialized


def test_tbd_excluido(tmp_path):
    manc_path, mcns_path = write_tables(tmp_path, ["TBD"] * 20, ["TBD"] * 20)
    with pytest.raises(hc.CrosswalkError):
        hc.build(manc_path, mcns_path, "A", "2.0-draft")
