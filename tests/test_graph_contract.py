import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import graph_contract as gc  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "graph-fixture.json"


def payload() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_fixture_valida_e_roundtrip_preserva():
    data = payload()
    assert gc.validate_graph(data) == []
    failures, ok = gc.roundtrip(FIXTURE)
    assert failures == [] and ok is True
    assert gc.canonical_json(json.loads(gc.canonical_json(data))) == gc.canonical_json(data)


def test_multiedge_conserva_soma():
    data = payload()
    n1, n2 = data["nodes"][0]["id"], data["nodes"][1]["id"]
    pair = [edge for edge in data["edges"] if edge["source"] == n1 and edge["target"] == n2]
    assert len(pair) == 2
    assert sum(edge["weight"] for edge in pair) == 8
    assert data["graph"]["aggregation"] == "sum"


@pytest.mark.parametrize(
    "mutacao, esperado",
    [
        (lambda d: d["edges"][0].update(weight=-1), "weight"),
        (lambda d: d["edges"][0].update(weight=5.0), "weight"),
        (lambda d: d["edges"][0].update(weight=None), None),
        (lambda d: d["graph"].update(allow_self_loops=False), "self-loop"),
        (lambda d: d["edges"][0].update(target="n" + "0" * 16), "inexistente"),
        (lambda d: d["nodes"].append(dict(d["nodes"][0])), "duplicado"),
        (lambda d: d["nodes"][0]["missing"].append("degree_in"), "attributes e em missing"),
        (lambda d: d["graph"].update(aggregation="media"), "aggregation"),
        (lambda d: d.update(extra=1), "inesperado"),
        (lambda d: d["provenance"].pop("license"), "license"),
        (lambda d: d["provenance"]["adapter"].update(config_sha256="x"), "config_sha256"),
    ],
)
def test_grafos_invalidos(mutacao, esperado):
    data = payload()
    mutacao(data)
    failures = gc.validate_graph(data)
    assert failures, "mutação deveria falhar"
    if esperado:
        assert any(esperado in failure for failure in failures), failures


def test_null_sem_missing_falha():
    data = payload()
    data["nodes"][0]["attributes"]["degree_in"] = None
    failures = gc.validate_graph(data)
    assert any("null exige" in failure for failure in failures), failures


def test_schema_e_validador_em_sincronia():
    schema = json.loads((ROOT / "schemas" / "graph.schema.json").read_text(encoding="utf-8"))
    assert tuple(schema["required"]) == gc.TOP_REQUIRED
    assert tuple(schema["properties"]["provenance"]["required"]) == gc.PROVENANCE_REQUIRED
    assert tuple(schema["properties"]["graph"]["required"]) == gc.GRAPH_REQUIRED
    assert tuple(schema["properties"]["nodes"]["items"]["required"]) == gc.NODE_REQUIRED
    assert tuple(schema["properties"]["edges"]["items"]["required"]) == gc.EDGE_REQUIRED
    assert schema["properties"]["nodes"]["items"]["properties"]["id"]["pattern"] == gc.NODE_RE.pattern


def test_cli_validate(tmp_path):
    import subprocess

    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "graph_contract.py"), "roundtrip", str(FIXTURE)],
        capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert "round-trip preserva" in result.stdout
