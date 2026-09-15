import copy
import json
import re
import sys
from pathlib import Path

import numpy as np
import pytest
import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import gnn_graphsage as gg  # noqa: E402
import resource_smoke as rs  # noqa: E402

REPORT = ROOT / "artifacts" / "reports" / "M04-RECURSOS.json"


def synthetic_graph(n: int = 40, seed: int = 5) -> dict:
    rng = np.random.RandomState(seed)
    edges = []
    for node in range(n):
        edges.append((node, (node + 1) % n, 1.0 + rng.rand()))
        edges.append(((node + 2) % n, node, 1.0 + rng.rand()))
    for _ in range(n):
        source, destination = rng.randint(0, n, size=2)
        if source != destination:
            edges.append((int(source), int(destination), 1.0))
    source = np.asarray([edge[0] for edge in edges], dtype=np.int64)
    destination = np.asarray([edge[1] for edge in edges], dtype=np.int64)
    weight = np.asarray([edge[2] for edge in edges], dtype=np.float64)
    features = rng.randn(n, len(gg.FEATURE_NAMES)).astype(np.float32)
    return {
        "n_nodes": n,
        "train_edges": int(len(source)),
        "in_csr": gg.build_direction_csr(source, destination, weight, n, "in"),
        "out_csr": gg.build_direction_csr(source, destination, weight, n, "out"),
        "features": features,
        "weight": weight,
    }


def synthetic_row(config: dict, peak: float, reserved: float, steps: int = 8) -> dict:
    return {
        "name": config["name"],
        "group": config["group"],
        "dim": config["dim"],
        "layers": config["layers"],
        "fanout": list(config["fanout"]),
        "batch": config["batch"],
        "precision": config["precision"],
        "checkpoint": bool(config.get("checkpoint", False)),
        "variant_of": config["variant_of"],
        "steps": steps,
        "skipped_steps": 0,
        "seconds_per_step_mean": 0.5,
        "sample_seconds_mean": 0.4,
        "compute_seconds_mean": 0.1,
        "step_seconds": [0.5] * steps,
        "total_seconds": 0.5 * steps,
        "steps_per_second": 2.0,
        "loss_first": 10.0,
        "loss_last": 1.0,
        "peak_vram_mib": peak,
        "peak_reserved_mib": reserved,
        "vram_margin": round(1.0 - peak / rs.VRAM_CAP_MIB, 4),
        "vram_margin_reserved": round(1.0 - reserved / rs.VRAM_CAP_MIB, 4),
        "free_before_mib": 7600.0,
        "free_after_mib": 6000.0,
        "peak_rss_mib": 2000.0,
        "oom": False,
    }


def synthetic_rows() -> list[dict]:
    rows = []
    for config in rs.grid_rows():
        layers = config["layers"]
        batch = config["batch"]
        base = 90.0 * layers + batch * 0.02 + (500.0 if config["dim"] == 576 else 300.0)
        checkpoint = bool(config.get("checkpoint", False))
        precision = config["precision"]
        heavy = layers == 3 and batch == 1024
        peak = base * (7.5 if heavy else 1.0) * (0.55 if precision == "amp" else 1.0) * (0.62 if checkpoint else 1.0)
        rows.append(synthetic_row(config, round(peak, 1), round(peak * 1.35, 1)))
    return rows


def synthetic_report() -> dict:
    rows = synthetic_rows()
    probe = next(row for row in rows if row["name"] == "mvp576_2l_f10_b512")
    return {
        "schema": rs.SCHEMA,
        "status": "exploratory-only; somente fonte; sem nenhum dado do alvo",
        "device": "cuda",
        "cuda_name": "fixture",
        "vram_cap_mib": round(rs.VRAM_CAP_MIB, 1),
        "margin_min": rs.MARGIN_MIN,
        "grid": rows,
        "choice": rs.choose_config(rows),
        "envelope": rs.envelope(rows),
        "epoch_projection": {
            "definition": "fixture",
            "n_nodes": 23188,
            "name": probe["name"],
            "batch": probe["batch"],
            "precision": "fp32",
            "checkpoint": False,
            "steps_per_epoch": 46,
            "probe_steps": 10,
            "estimator": "mediana",
            "seconds_per_step_probe": 0.5,
            "projected_epoch_seconds": 23.0,
            "measured_epoch_seconds": 23.2,
            "seconds_per_step_epoch_mean": 0.504,
            "relative_error": 0.0086,
            "within_tolerance": True,
            "probe_block_seconds_mean": 0.5,
            "epoch_block_seconds_mean": 0.505,
            "step_seconds": [0.5] * 46,
            "sample_seconds_mean": 0.4,
            "compute_seconds_mean": 0.1,
            "peak_vram_mib": probe["peak_vram_mib"],
            "peak_reserved_mib": probe["peak_reserved_mib"],
            "vram_margin": probe["vram_margin"],
            "vram_margin_reserved": probe["vram_margin_reserved"],
            "oom": False,
        },
        "worker_reproducibility": {
            "items": 4,
            "batch": 512,
            "fanout": [10, 10],
            "workers": [0, 2],
            "hashes_by_worker_count": {"0": ["a"], "2": ["a"]},
            "identical": True,
            "cpu_count": 8,
        },
        "precision_equivalence": {
            "applicable": True,
            "dtype": "bfloat16",
            "base_config": probe["name"],
            "losses": {"amp": 70.9, "fp32": 71.2},
            "relative_difference": 0.0045,
            "within_tolerance": True,
        },
        "checkpoint_equivalence": {
            "applicable": True,
            "base_config": probe["name"],
            "dropout": 0.0,
            "losses": {"plain": 71.2, "checkpoint": 71.2},
            "relative_difference": 0.0,
            "within_tolerance": True,
        },
        "declared": {
            "short_steps": rs.SHORT_STEPS,
            "epoch_probe_steps": 10,
            "epoch_tolerance": rs.EPOCH_TOLERANCE,
            "precision_tolerance": rs.PRECISION_TOLERANCE,
            "checkpoint_tolerance": rs.CHECKPOINT_TOLERANCE,
            "combination_order": [list(combination) for combination in rs.COMBINATION_ORDER],
            "grid_predeclared": [config["name"] for config in rs.grid_rows()],
            "protocol_trials": [list(trial) for trial in rs.PROTOCOL_TRIALS],
            "no_target_selection": "apenas recursos; nenhuma métrica do alvo",
        },
        "resources": {"seconds": 100.0, "peak_rss_mib": 2500.0},
    }


def write_report(tmp_path: Path, report: dict) -> Path:
    path = tmp_path / "report.json"
    path.write_text(json.dumps(report), encoding="utf-8")
    return path


def test_grid_predeclarado_completo_e_coerente():
    rows = rs.grid_rows()
    names = [row["name"] for row in rows]
    assert len(names) == len(set(names)) == 16
    assert {"s64_2l_f10_b512", "s128_3l_f15_b512", "mvp576_2l_f10_b512", "mvp408_3l_f1510_b1024_ckpt_amp"} <= set(names)
    for row in rows:
        assert len(row["fanout"]) == row["layers"]
        assert row["batch"] in (512, 1024)
    assert {row["dim"] for row in rows if row["group"] == "sampling"} == {64, 128}
    assert {row["dim"] for row in rows if row["group"] == "mvp"} == {408, 576}
    amp_rows = [row for row in rows if row["precision"] == "amp"]
    assert amp_rows and all(row["variant_of"] for row in amp_rows)
    checkpoint_rows = [row for row in rows if row.get("checkpoint")]
    assert checkpoint_rows and all(row["layers"] == 3 and row["batch"] == 1024 for row in checkpoint_rows)


def test_protocol_trials_espelham_a_tabela_congelada():
    text = (ROOT / "preregistration" / "PROTOCOL.md").read_text(encoding="utf-8")
    parsed = {}
    for line in text.splitlines():
        if not re.match(r"\| T\d\d ", line):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        trial, dim, layers, fanout, _lr, batch = cells[:6]
        values = tuple(int(value) for value in fanout.split(","))
        parsed[trial] = (int(dim), int(layers), gg.pad_fanout(int(layers), values), int(batch))
    assert set(parsed) == {trial[0] for trial in rs.PROTOCOL_TRIALS}
    for name, dim, layers, fanout, batch in rs.PROTOCOL_TRIALS:
        assert parsed[name] == (dim, layers, tuple(fanout), batch)
    assert {dim for dim, _, _, _ in parsed.values()} == {408, 576}


def test_epoch_metrics_projecao_e_drift():
    stable = rs.epoch_metrics([0.5] * 46, 46, 10)
    assert stable["within_tolerance"] and stable["relative_error"] < 1e-9
    drift = rs.epoch_metrics([0.5] * 10 + [1.0] * 36, 46, 10)
    assert drift["relative_error"] > rs.EPOCH_TOLERANCE and not drift["within_tolerance"]
    assert len(drift["step_seconds"]) == 46


def test_choose_config_usa_margem_dupla():
    rows = synthetic_rows()
    chosen = rs.choose_config(rows)
    eligible = [
        row
        for row in rows
        if row["group"] == "mvp" and row["precision"] == "fp32" and rs._eligible(row)
    ]
    best = max(eligible, key=lambda row: min(row["vram_margin"], row["vram_margin_reserved"]))
    assert chosen["chosen"] == best["name"]
    assert chosen["vram_margin_reserved"] >= rs.MARGIN_MIN and chosen["checkpoint"] in (True, False)
    tight = copy.deepcopy(rows)
    for row in tight:
        if row["name"] == chosen["chosen"]:
            row["peak_reserved_mib"] = rs.VRAM_CAP_MIB * 0.9
            row["vram_margin_reserved"] = 0.1
    assert rs.choose_config(tight)["chosen"] != chosen["chosen"]
    for row in tight:
        row["oom"] = True
    assert rs.choose_config(tight)["chosen"] is None


def test_dominancia_e_envelope():
    rows = synthetic_rows()
    by_name = {row["name"]: row for row in rows}
    assert rs._dominates(by_name["mvp576_2l_f1510_b1024"], 576, 2, (10, 10), 512)
    assert not rs._dominates(by_name["mvp576_2l_f10_b512"], 576, 2, (15, 10), 512)
    assert not rs._dominates(by_name["mvp576_2l_f10_b512"], 408, 2, (10, 10), 512)
    envelope = rs.envelope(rows)
    trials = {trial["trial"]: trial for trial in envelope["trials"]}
    assert list(trials) == [trial[0] for trial in rs.PROTOCOL_TRIALS]
    assert envelope["all_within_cap"]
    assert trials["T03"]["recommended_checkpoint"] is True
    assert trials["T03"]["bound_row"] == "mvp408_3l_f1510_b1024_ckpt"
    assert trials["T01"]["recommended_checkpoint"] is False
    assert trials["T01"]["bound_row"] == "mvp576_2l_f10_b512"
    assert trials["T12"]["recommended_precision"] == "fp32"
    assert all(trial["bound_peak_reserved_mib"] is not None for trial in envelope["trials"])


def test_check_report_valido_e_tamperado(tmp_path):
    report = synthetic_report()
    assert rs.check_report(write_report(tmp_path, report)) == []
    cases = {
        "teto alocado": lambda r: r["grid"][0].update(peak_vram_mib=rs.VRAM_CAP_MIB + 1),
        "teto reservado": lambda r: r["grid"][0].update(peak_reserved_mib=rs.VRAM_CAP_MIB + 1),
        "margem escolhida": lambda r: [
            row.update(vram_margin_reserved=0.1) for row in r["grid"] if row["name"] == r["choice"]["chosen"]
        ],
        "worker": lambda r: r["worker_reproducibility"].update(identical=False),
        "epoca": lambda r: r["epoch_projection"].update(within_tolerance=False),
        "amostragem": lambda r: r["epoch_projection"].update(sample_seconds_mean=None),
        "precisao": lambda r: r["precision_equivalence"].update(within_tolerance=False),
        "checkpoint": lambda r: r["checkpoint_equivalence"].update(within_tolerance=False),
        "status": lambda r: r.update(status="resultado final"),
        "envelope": lambda r: r["envelope"].update(all_within_cap=False),
        "trial": lambda r: r["envelope"]["trials"][0].update(bound_row=None),
        "checkpoint do trial": lambda r: r["envelope"]["trials"][0].update(recommended_checkpoint=None),
    }
    for label, mutate in cases.items():
        tampered = synthetic_report()
        mutate(tampered)
        failures = rs.check_report(write_report(tmp_path, tampered))
        assert failures, f"caso '{label}' deveria falhar"
    assert rs.check_report(tmp_path / "ausente.json")


def test_worker_reproducibility_entre_contagens():
    graph = synthetic_graph()
    config = {"fanout": (3, 2), "batch": 8, "name": "fixture"}
    result = rs.worker_reproducibility(graph, config, rs.MASTER_SEED, workers=(0, 2), items=2)
    assert result["identical"]
    assert result["hashes_by_worker_count"]["0"] == result["hashes_by_worker_count"]["2"]
    assert result["cpu_count"] > 0


def test_checkpoint_preserva_a_matematica():
    graph = synthetic_graph()
    fans = (3, 2)
    encoder = gg.build_encoder(gg.EncoderConfig(dim=16, layers=2, fanout=fans, dropout=0.0))
    encoder.eval()
    targets = rs.batch_targets(graph, 8, 0, rs.MASTER_SEED)
    subgraph = gg.sample_subgraph(targets, graph["in_csr"], graph["out_csr"], fans, 7)
    plain = gg.forward_sampled(encoder, graph["features"], subgraph, training=False, aggregation="mean", device="cpu")
    checkpointed = gg.forward_sampled(encoder, graph["features"], subgraph, training=False, aggregation="mean", device="cpu", checkpoint=True)
    assert torch.allclose(plain, checkpointed, atol=1e-6)


@pytest.mark.skipif(not torch.cuda.is_available(), reason="equivalência de precisão/checkpoint exige CUDA")
def test_equivalencias_em_cuda():
    graph = synthetic_graph()
    encoder_config = gg.EncoderConfig(dim=32, layers=2, fanout=(3, 2), dropout=0.1)
    base = {"name": "fixture", "dim": 32, "layers": 2, "fanout": (3, 2), "batch": 8}
    precision = rs.precision_equivalence(graph, base, rs.MASTER_SEED, "cuda", steps=2)
    assert precision["applicable"] and precision["within_tolerance"]
    checkpoint = rs.checkpoint_equivalence(graph, base, rs.MASTER_SEED, "cuda", steps=2)
    assert checkpoint["applicable"] and checkpoint["within_tolerance"]
    assert gg.encoder_parameter_count(gg.build_encoder(encoder_config)) > 0


def test_fontes_sem_referencia_ao_alvo():
    source = (ROOT / "tools" / "resource_smoke.py").read_text(encoding="utf-8")
    for token in ("male-cns", "data/sealed", "target_labels", "crosswalk"):
        assert token not in source
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert "exploratory-only" in report["status"]
    assert "sem nenhum dado do alvo" in report["status"]
