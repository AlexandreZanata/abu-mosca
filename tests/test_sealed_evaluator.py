import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import evaluator_contract as ec  # noqa: E402
import sealed_evaluator as se  # noqa: E402


def qid(index: int) -> str:
    return "q" + f"{index:016x}"


def gid(index: int) -> str:
    return "g" + f"{index:016x}"


CLASSES = tuple(f"t{i}" for i in range(8))
GALLERY = [gid(i) for i in range(8)]
GALLERY_OF = {f"t{i}": gid(i) for i in range(8)}
N_PER_CLASS = 4


def labels_payload() -> dict:
    queries = {}
    known = len(CLASSES) * N_PER_CLASS
    for index in range(known):
        queries[qid(index)] = {"status": "known", "type_t0": CLASSES[index % len(CLASSES)]}
    queries[qid(known)] = {"status": "unknown", "type_t0": None}
    queries[qid(known + 1)] = {"status": "unknown", "type_t0": None}
    queries[qid(known + 2)] = {"status": "missing", "type_t0": None}
    return {
        "label_schema_version": "1.0",
        "crosswalk_version": "sintetico-v1",
        "queries": queries,
        "gallery": {GALLERY_OF[tipo]: tipo for tipo in CLASSES},
        "crosswalk": {f"src{i}": tipo for i, tipo in enumerate(CLASSES)},
    }


def predictions_payload(seed: int, quality: str, run_id: str = "a" * 16) -> dict:
    queries = []
    known = len(CLASSES) * N_PER_CLASS
    for index in range(known):
        true_type = CLASSES[index % len(CLASSES)]
        scores = {tipo: 0.05 for tipo in CLASSES}
        if quality == "forte":
            scores[true_type] = 0.9
        elif quality == "baseline":
            scores[true_type] = 0.4
            scores[CLASSES[(index + 1) % len(CLASSES)]] = 0.6
        else:
            scores[true_type] = 0.55
            scores[CLASSES[(index + 2) % len(CLASSES)]] = 0.45
        ranked = sorted(
            ({"id": GALLERY_OF[tipo], "score": value} for tipo, value in scores.items()),
            key=lambda item: -item["score"],
        )
        queries.append({"id": qid(index), "ranked": ranked, "rejected": False})
    queries.append({"id": qid(known), "ranked": [{"id": GALLERY_OF["t0"], "score": 0.2}], "rejected": True})
    queries.append({"id": qid(known + 1), "ranked": [{"id": GALLERY_OF["t1"], "score": 0.15}], "rejected": True})
    queries.append({"id": qid(known + 2), "ranked": [{"id": GALLERY_OF["t2"], "score": 0.1}], "rejected": True})
    return {
        "schema_version": "1.0",
        "run_id": run_id,
        "seed": seed,
        "gallery": {"nodes": 64, "types": len(CLASSES)},
        "queries": queries,
    }


@pytest.fixture()
def files(tmp_path):
    labels_path = tmp_path / "labels.json"
    labels_path.write_text(json.dumps(labels_payload()), encoding="utf-8")
    encoders = []
    baselines = []
    degree = []
    for seed in (1, 2):
        encoder_path = tmp_path / f"pred-{seed}.json"
        encoder_path.write_text(json.dumps(predictions_payload(seed, "forte")), encoding="utf-8")
        baseline_path = tmp_path / f"base-{seed}.json"
        baseline_path.write_text(json.dumps(predictions_payload(seed, "baseline")), encoding="utf-8")
        degree_path = tmp_path / f"degree-{seed}.json"
        degree_path.write_text(json.dumps(predictions_payload(seed, "degree")), encoding="utf-8")
        encoders.append(encoder_path)
        baselines.append(baseline_path)
        degree.append(degree_path)
    return labels_path, encoders, baselines, degree


def test_avaliacao_produz_metricas_validas(files):
    labels_path, encoders, baselines, degree = files
    metrics = se.evaluate(
        encoders,
        labels_path,
        baseline_paths=baselines,
        degree_matched_paths=degree,
        within_macro=0.85,
        bootstrap_iterations=200,
        permutation_iterations=100,
    )
    assert ec.validate_metrics(metrics) == []
    assert metrics["primary"]["name"] == "macro-recall@1-t0"
    assert metrics["primary"]["value"] == 1.0
    assert metrics["counts"]["known"] == len(CLASSES) * N_PER_CLASS
    assert metrics["counts"]["unknown"] == 2
    assert metrics["comparisons"]["sesoi_met"] is True
    assert metrics["within_cross"]["gap"] == pytest.approx(-0.15)
    assert metrics["nulls"]["permutations"] == 100


def test_hash_do_label_set_registrado(files):
    labels_path, encoders, baselines, degree = files
    metrics = se.evaluate(
        encoders, labels_path, baseline_paths=baselines, degree_matched_paths=degree,
        within_macro=0.8, bootstrap_iterations=50, permutation_iterations=20,
    )
    assert metrics["inputs"]["label_set_sha256"] == se.sha256_file(labels_path)


def test_cobertura_incompleta_falha(tmp_path, files):
    labels_path, encoders, baselines, degree = files
    payload = predictions_payload(1, "forte")
    payload["queries"].append({"id": "q" + "f" * 16, "ranked": [{"id": GALLERY[0], "score": 0.3}], "rejected": False})
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(se.EvaluationError, match="cobertura"):
        se.evaluate([bad], labels_path, baseline_paths=baselines, degree_matched_paths=degree, within_macro=0.8)


def test_label_schema_invalido_falha(tmp_path, files):
    labels_path, encoders, baselines, degree = files
    payload = json.loads(labels_path.read_text(encoding="utf-8"))
    payload["queries"][qid(0)]["status"] = "talvez"
    bad = tmp_path / "labels-bad.json"
    bad.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(se.EvaluationError, match="status"):
        se.evaluate(encoders, bad, baseline_paths=baselines, degree_matched_paths=degree, within_macro=0.8)


def test_cli_nao_vaza_ids_em_log(files, tmp_path):
    labels_path, encoders, baselines, degree = files
    out = tmp_path / "metrics.json"
    command = [
        sys.executable, str(ROOT / "tools" / "sealed_evaluator.py"),
        "--labels", str(labels_path),
        "--within", "0.8",
        "--bootstrap", "50", "--permutations", "20",
        "--out", str(out),
    ]
    for flag, paths in (("--predictions", encoders), ("--baseline", baselines), ("--degree-matched", degree)):
        command.append(flag)
        command.extend(str(path) for path in paths)
    result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stderr
    assert not re.search(r"q[0-9a-f]{16}", result.stdout + result.stderr)
    assert out.exists()
    assert ec.validate_metrics(json.loads(out.read_text(encoding="utf-8"))) == []
