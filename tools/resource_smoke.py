#!/usr/bin/env python3
"""Smoke e calibração de sampling/recursos (M04).

Mede o envelope seguro de fanout, batch e precisão para o encoder GraphSAGE do
MVP (grid emendado do R07) no hardware-alvo, com um grid **pré-definido** e sem
usar qualquer métrica do alvo: o critério de escolha é puramente de recursos
(pico abaixo de 6,5 GB de VRAM com margem, sem OOM). Confirma neighbor sampling,
reprodutibilidade entre contagens de CPU workers, equivalência de mixed precision
e compara a projeção de tempo por época com a medição. Cobre os 12 trials
congelados do R07 por dominância declarada (fanout e batch maiores) e mapeia
cada trial ao pico medido que o limita. Somente fonte.
"""

import argparse
import contextlib
import hashlib
import json
import os
import resource
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import gnn_graphsage as gg  # noqa: E402

MASTER_SEED = 20260914
SCHEMA = "m04-resource-smoke"
VRAM_CAP_MIB = 6.5 * 1024
MARGIN_MIN = 0.25
EPOCH_TOLERANCE = 0.25
PRECISION_TOLERANCE = 1e-2
SHORT_STEPS = 8
SAMPLING_GRID = (
    {"name": "s64_2l_f10_b512", "dim": 64, "layers": 2, "fanout": (10, 10), "batch": 512},
    {"name": "s64_2l_f15_b512", "dim": 64, "layers": 2, "fanout": (15, 10), "batch": 512},
    {"name": "s64_2l_f10_b1024", "dim": 64, "layers": 2, "fanout": (10, 10), "batch": 1024},
    {"name": "s128_2l_f10_b512", "dim": 128, "layers": 2, "fanout": (10, 10), "batch": 512},
    {"name": "s128_2l_f15_b1024", "dim": 128, "layers": 2, "fanout": (15, 10), "batch": 1024},
    {"name": "s128_3l_f15_b512", "dim": 128, "layers": 3, "fanout": (15, 10, 10), "batch": 512},
)
MVP_GRID = (
    {"name": "mvp576_2l_f10_b512", "dim": 576, "layers": 2, "fanout": (10, 10), "batch": 512},
    {"name": "mvp408_3l_f1510_b512", "dim": 408, "layers": 3, "fanout": (15, 10, 10), "batch": 512},
    {"name": "mvp576_2l_f1510_b1024", "dim": 576, "layers": 2, "fanout": (15, 10), "batch": 1024},
    {"name": "mvp408_3l_f1510_b1024", "dim": 408, "layers": 3, "fanout": (15, 10, 10), "batch": 1024},
)
CHECKPOINT_GRID = (
    {"name": "mvp408_3l_f1510_b1024_ckpt", "dim": 408, "layers": 3, "fanout": (15, 10, 10), "batch": 1024, "checkpoint": True},
)
PRECISION_VARIANTS = tuple(
    {"name": f"{config['name']}_amp", "base": config["name"], "precision": "amp"}
    for config in MVP_GRID + CHECKPOINT_GRID
)
CHECKPOINT_TOLERANCE = 1e-4
COMBINATION_ORDER = (("fp32", False), ("fp32", True), ("amp", False), ("amp", True))
PROTOCOL_TRIALS = (
    ("T01", 576, 2, (10, 10), 512),
    ("T02", 576, 2, (10, 10), 512),
    ("T03", 408, 3, (15, 10, 10), 1024),
    ("T04", 408, 3, (15, 10, 10), 1024),
    ("T05", 576, 2, (10, 10), 1024),
    ("T06", 576, 2, (10, 10), 512),
    ("T07", 408, 3, (15, 10, 10), 512),
    ("T08", 408, 3, (15, 10, 10), 1024),
    ("T09", 576, 2, (15, 10), 1024),
    ("T10", 408, 3, (10, 10, 10), 512),
    ("T11", 576, 2, (15, 10), 512),
    ("T12", 408, 3, (10, 10, 10), 1024),
)
_WORKER_CONTEXT: dict = {}


def grid_rows() -> list[dict]:
    rows = []
    for group, configs in (("sampling", SAMPLING_GRID), ("mvp", MVP_GRID), ("mvp", CHECKPOINT_GRID)):
        for config in configs:
            rows.append({**config, "group": group, "precision": "fp32", "variant_of": None})
    for variant in PRECISION_VARIANTS:
        base = next(config for config in MVP_GRID + CHECKPOINT_GRID if config["name"] == variant["base"])
        rows.append({**base, "name": variant["name"], "group": "mvp", "precision": "amp", "variant_of": variant["base"]})
    return rows


def load_graph(snapshot: Path = gg.SOURCE_SNAPSHOT, seed: int = MASTER_SEED) -> dict:
    import ssl_task as st

    ids, src, dst, weight = st.load_source_edges(snapshot)
    n_nodes = len(ids)
    mask = st.build_mask(src, dst, n_nodes, st.seedlib.derive_seed(seed, "m01", "mask"))["mask"]
    train_src, train_dst, train_wgt = st.training_view(src, dst, weight, mask)
    _, raw_features = gg.snapshot_features(snapshot)
    _, features = gg.fit_transform_stats(raw_features)
    return {
        "n_nodes": n_nodes,
        "train_edges": int(len(train_src)),
        "in_csr": gg.build_direction_csr(train_src, train_dst, train_wgt, n_nodes, "in"),
        "out_csr": gg.build_direction_csr(train_src, train_dst, train_wgt, n_nodes, "out"),
        "features": features,
        "weight": train_wgt,
    }


def batch_targets(graph: dict, batch: int, step: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState((seed + step) % (2**32))
    return np.sort(rng.choice(graph["n_nodes"], size=batch, replace=False))


def batch_loss(encoder, decoder, graph: dict, targets: np.ndarray, step: int, seed: int, device: str, precision: str, timings: dict | None = None, config_checkpoint: bool = False):
    import torch

    started = time.perf_counter()
    subgraph = gg.sample_subgraph(targets, graph["in_csr"], graph["out_csr"], encoder.config.fanout, (seed + step) % (2**32))
    batch = len(targets)
    adjacency = np.zeros((batch, batch), dtype=bool)
    for position, node in enumerate(targets):
        start, finish = graph["in_csr"].indptr[node], graph["in_csr"].indptr[node + 1]
        neighbors = graph["in_csr"].indices[start:finish]
        slots = np.searchsorted(targets, neighbors)
        valid = (slots < batch) & (targets[np.clip(slots, 0, batch - 1)] == neighbors)
        adjacency[position, slots[valid]] = True
    upper = np.triu_indices(batch, k=1)
    positive_slots = np.nonzero(adjacency[upper])[0]
    negative_slots = np.nonzero(~adjacency[upper])[0]
    rng = np.random.RandomState((seed + step + 1) % (2**32))
    count = int(min(64, len(positive_slots)))
    if count == 0:
        return None
    positive_rows = positive_slots[rng.choice(len(positive_slots), size=count, replace=False)]
    negative_rows = negative_slots[rng.choice(len(negative_slots), size=count, replace=False)]
    weight = torch.from_numpy(np.ones(count, dtype=np.float32)).to(device)
    if timings is not None:
        timings["sample"] = timings.get("sample", 0.0) + time.perf_counter() - started
    use_amp = precision == "amp" and device == "cuda"
    autocast = torch.autocast(device_type="cuda", dtype=torch.bfloat16) if use_amp else contextlib.nullcontext()
    with autocast:
        embeddings = gg.forward_sampled(
            encoder,
            graph["features"],
            subgraph,
            training=True,
            aggregation="mean",
            device=device,
            checkpoint=bool(config_checkpoint),
        )
        parts = sd_masked_edge_weight_loss(
            decoder,
            embeddings[upper[0][positive_rows]],
            embeddings[upper[1][positive_rows]],
            weight,
            embeddings[upper[0][negative_rows]],
            embeddings[upper[1][negative_rows]],
        )
    return parts["loss"]


def sd_masked_edge_weight_loss(decoder, source, destination, weight, negative_source, negative_destination):
    import ssl_decoder as sd

    return sd.masked_edge_weight_loss(decoder, source, destination, weight, negative_source, negative_destination)


def build_models(config: dict, seed: int, device: str):
    import torch

    import ssl_decoder as sd

    torch.manual_seed(seed % (2**32))
    encoder_config = gg.EncoderConfig(dim=config["dim"], layers=config["layers"], fanout=tuple(config["fanout"]), dropout=0.1)
    encoder = gg.build_encoder(encoder_config).to(device)
    decoder = sd.BilinearDecoder(encoder_config.dim).to(device)
    optimizer = torch.optim.Adam(list(encoder.parameters()) + list(decoder.parameters()), lr=1e-3)
    return encoder, decoder, optimizer


def run_config(graph: dict, config: dict, seed: int, device: str, steps: int) -> dict:
    import torch

    if device == "cuda":
        free_before = float(torch.cuda.mem_get_info()[0] / 1024 / 1024)
    encoder, decoder, optimizer = build_models(config, seed, device)
    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()
    times: list[float] = []
    losses: list[float] = []
    sample_times: list[float] = []
    skipped = 0
    warmup = 2
    for step in range(warmup + steps):
        targets = batch_targets(graph, config["batch"], step, seed)
        if device == "cuda":
            torch.cuda.synchronize()
        started = time.perf_counter()
        timings: dict = {}
        loss = batch_loss(encoder, decoder, graph, targets, step, seed, device, config["precision"], timings, bool(config.get("checkpoint", False)))
        if loss is None:
            skipped += 1
            continue
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        if device == "cuda":
            torch.cuda.synchronize()
        elapsed = time.perf_counter() - started
        if step >= warmup:
            times.append(elapsed)
            sample_times.append(timings.get("sample", 0.0))
            losses.append(float(loss.detach()))
    peak_vram = float(torch.cuda.max_memory_allocated() / 1024 / 1024) if device == "cuda" else None
    peak_reserved = float(torch.cuda.max_memory_reserved() / 1024 / 1024) if device == "cuda" else None
    free_after = float(torch.cuda.mem_get_info()[0] / 1024 / 1024) if device == "cuda" else None
    peak_rss = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    mean_seconds = float(np.mean(times)) if times else None
    mean_sample = float(np.mean(sample_times)) if sample_times else None
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
        "steps": len(times),
        "skipped_steps": skipped,
        "seconds_per_step_mean": round(mean_seconds, 6) if mean_seconds else None,
        "sample_seconds_mean": round(mean_sample, 6) if mean_sample is not None else None,
        "compute_seconds_mean": round(mean_seconds - mean_sample, 6) if mean_seconds and mean_sample is not None else None,
        "step_seconds": [round(value, 4) for value in times],
        "total_seconds": round(float(np.sum(times)), 6) if times else None,
        "steps_per_second": round(1.0 / mean_seconds, 4) if mean_seconds else None,
        "loss_first": losses[0] if losses else None,
        "loss_last": losses[-1] if losses else None,
        "peak_vram_mib": round(peak_vram, 1) if peak_vram is not None else None,
        "peak_reserved_mib": round(peak_reserved, 1) if peak_reserved is not None else None,
        "vram_margin": round(1.0 - peak_vram / VRAM_CAP_MIB, 4) if peak_vram is not None else None,
        "vram_margin_reserved": round(1.0 - peak_reserved / VRAM_CAP_MIB, 4) if peak_reserved is not None else None,
        "free_before_mib": round(free_before, 1) if device == "cuda" else None,
        "free_after_mib": round(free_after, 1) if device == "cuda" else None,
        "peak_rss_mib": peak_rss,
        "oom": False,
    }


def epoch_metrics(times: list[float], steps_per_epoch: int, probe_steps: int) -> dict:
    probe = int(min(probe_steps, len(times)))
    estimated_step = float(np.median(times[:probe]))
    measured_epoch = float(np.sum(times))
    projected = estimated_step * steps_per_epoch
    relative = abs(measured_epoch - projected) / measured_epoch if measured_epoch else None
    return {
        "definition": "epoch = uma passagem por todos os nós da fonte como alvos (ceil(n_nodes/batch) passos)",
        "steps_per_epoch": steps_per_epoch,
        "probe_steps": probe,
        "estimator": "mediana do tempo/passo nos primeiros probe_steps da própria época (bloco curto declarado)",
        "seconds_per_step_probe": round(estimated_step, 6),
        "projected_epoch_seconds": round(projected, 3),
        "measured_epoch_seconds": round(measured_epoch, 3),
        "seconds_per_step_epoch_mean": round(float(np.mean(times)), 6),
        "relative_error": round(relative, 4) if relative is not None else None,
        "within_tolerance": bool(relative is not None and relative <= EPOCH_TOLERANCE),
        "probe_block_seconds_mean": round(float(np.mean(times[:probe])), 6),
        "epoch_block_seconds_mean": round(float(np.mean(times[probe:])), 6) if len(times) > probe else None,
        "step_seconds": [round(value, 4) for value in times],
    }


def epoch_probe(graph: dict, config: dict, seed: int, device: str, probe_steps: int = 10, warmup: int = 2) -> dict:
    import torch

    free_before = float(torch.cuda.mem_get_info()[0] / 1024 / 1024) if device == "cuda" else None
    encoder, decoder, optimizer = build_models(config, seed, device)
    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()
    steps_per_epoch = int(np.ceil(graph["n_nodes"] / config["batch"]))
    times: list[float] = []
    sample_times: list[float] = []
    for step in range(warmup + steps_per_epoch):
        targets = batch_targets(graph, config["batch"], step, seed)
        if device == "cuda":
            torch.cuda.synchronize()
        started = time.perf_counter()
        timings: dict = {}
        loss = batch_loss(encoder, decoder, graph, targets, step, seed, device, config["precision"], timings, bool(config.get("checkpoint", False)))
        if loss is None:
            continue
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        if device == "cuda":
            torch.cuda.synchronize()
        if step >= warmup:
            times.append(time.perf_counter() - started)
            sample_times.append(timings.get("sample", 0.0))
    metrics = {
        "n_nodes": graph["n_nodes"],
        "name": config["name"],
        "batch": config["batch"],
        "precision": config["precision"],
        "checkpoint": bool(config.get("checkpoint", False)),
        **epoch_metrics(times, steps_per_epoch, probe_steps),
    }
    peak_vram = float(torch.cuda.max_memory_allocated() / 1024 / 1024) if device == "cuda" else None
    peak_reserved = float(torch.cuda.max_memory_reserved() / 1024 / 1024) if device == "cuda" else None
    metrics["sample_seconds_mean"] = round(float(np.mean(sample_times)), 6) if sample_times else None
    metrics["compute_seconds_mean"] = round(float(np.mean(times) - np.mean(sample_times)), 6) if sample_times and times else None
    metrics["peak_vram_mib"] = round(peak_vram, 1) if peak_vram is not None else None
    metrics["peak_reserved_mib"] = round(peak_reserved, 1) if peak_reserved is not None else None
    metrics["vram_margin"] = round(1.0 - peak_vram / VRAM_CAP_MIB, 4) if peak_vram is not None else None
    metrics["vram_margin_reserved"] = round(1.0 - peak_reserved / VRAM_CAP_MIB, 4) if peak_reserved is not None else None
    metrics["free_before_mib"] = round(free_before, 1) if free_before is not None else None
    metrics["free_after_mib"] = round(float(torch.cuda.mem_get_info()[0] / 1024 / 1024), 1) if device == "cuda" else None
    metrics["oom"] = False
    return metrics


class WorkerDataset:
    def __init__(self, n_items: int, batch: int, seed: int):
        self.n_items = n_items
        self.batch = batch
        self.seed = seed

    def __len__(self) -> int:
        return self.n_items

    def __getitem__(self, index: int):
        targets = batch_targets(_WORKER_CONTEXT["graph"], self.batch, index, self.seed)
        subgraph = gg.sample_subgraph(
            targets,
            _WORKER_CONTEXT["graph"]["in_csr"],
            _WORKER_CONTEXT["graph"]["out_csr"],
            _WORKER_CONTEXT["fanout"],
            (self.seed + index) % (2**32),
        )
        digest = hashlib.sha256(subgraph["nodes"].tobytes() + subgraph["in_edges"][2].tobytes()).hexdigest()
        return targets.tolist(), digest


def worker_reproducibility(graph: dict, config: dict, seed: int, workers: tuple[int, ...] = (0, 2), items: int = 4) -> dict:
    from torch.utils.data import DataLoader

    _WORKER_CONTEXT["graph"] = graph
    _WORKER_CONTEXT["fanout"] = tuple(config["fanout"])
    results = {}
    for worker_count in workers:
        loader = DataLoader(WorkerDataset(items, config["batch"], seed), batch_size=None, num_workers=worker_count)
        results[str(worker_count)] = [digest for _, digest in loader]
    baseline = results[str(workers[0])]
    return {
        "items": items,
        "batch": config["batch"],
        "fanout": list(config["fanout"]),
        "workers": list(workers),
        "hashes_by_worker_count": results,
        "identical": all(value == baseline for value in results.values()),
        "cpu_count": os.cpu_count(),
    }


def precision_equivalence(graph: dict, base_config: dict, seed: int, device: str, steps: int = 4) -> dict:
    import torch

    if device != "cuda":
        return {"applicable": False, "reason": "CUDA indisponível"}
    torch.manual_seed(seed % (2**32))
    encoder_config = gg.EncoderConfig(dim=base_config["dim"], layers=base_config["layers"], fanout=tuple(base_config["fanout"]), dropout=0.0)
    encoder = gg.build_encoder(encoder_config).to(device)
    encoder.eval()
    import ssl_decoder as sd

    decoder = sd.BilinearDecoder(encoder_config.dim).to(device).eval()
    losses = {}
    for precision in ("fp32", "amp"):
        values = []
        for step in range(steps):
            targets = batch_targets(graph, base_config["batch"], step, seed)
            with torch.no_grad():
                loss = batch_loss(encoder, decoder, graph, targets, step, seed, device, precision)
            values.append(float(loss.detach()))
        losses[precision] = float(np.mean(values))
    relative = abs(losses["amp"] - losses["fp32"]) / abs(losses["fp32"]) if losses["fp32"] else None
    return {
        "applicable": True,
        "dtype": "bfloat16",
        "base_config": base_config["name"],
        "losses": {key: round(value, 6) for key, value in losses.items()},
        "relative_difference": round(relative, 6) if relative is not None else None,
        "within_tolerance": bool(relative is not None and relative <= PRECISION_TOLERANCE),
    }


def checkpoint_equivalence(graph: dict, base_config: dict, seed: int, device: str, steps: int = 4) -> dict:
    import torch

    import ssl_decoder as sd

    if device != "cuda":
        return {"applicable": False, "reason": "CUDA indisponível"}
    torch.manual_seed(seed % (2**32))
    encoder_config = gg.EncoderConfig(dim=base_config["dim"], layers=base_config["layers"], fanout=tuple(base_config["fanout"]), dropout=0.0)
    encoder = gg.build_encoder(encoder_config).to(device).eval()
    decoder = sd.BilinearDecoder(encoder_config.dim).to(device).eval()
    losses = {}
    for checked in (False, True):
        values = []
        for step in range(steps):
            targets = batch_targets(graph, base_config["batch"], step, seed)
            with torch.no_grad():
                loss = batch_loss(encoder, decoder, graph, targets, step, seed, device, "fp32", None, checked)
            values.append(float(loss.detach()))
        losses["checkpoint" if checked else "plain"] = float(np.mean(values))
    relative = abs(losses["checkpoint"] - losses["plain"]) / abs(losses["plain"]) if losses["plain"] else None
    return {
        "applicable": True,
        "base_config": base_config["name"],
        "dropout": 0.0,
        "losses": {key: round(value, 6) for key, value in losses.items()},
        "relative_difference": round(relative, 6) if relative is not None else None,
        "within_tolerance": bool(relative is not None and relative <= CHECKPOINT_TOLERANCE),
    }


def _eligible(row: dict) -> bool:
    return (
        not row.get("oom")
        and row.get("peak_vram_mib") is not None
        and row.get("peak_reserved_mib") is not None
        and row["vram_margin"] >= MARGIN_MIN
        and row["vram_margin_reserved"] >= MARGIN_MIN
    )


def _margin_min(row: dict) -> float:
    return min(row["vram_margin"], row["vram_margin_reserved"])


def choose_config(rows: list[dict]) -> dict:
    candidates = [row for row in rows if row["group"] == "mvp" and row["precision"] == "fp32"]
    eligible = [row for row in candidates if _eligible(row)]
    if not eligible:
        return {"chosen": None, "reason": "nenhuma configuração do MVP com margem suficiente"}
    chosen = max(eligible, key=lambda row: (_margin_min(row), -(row["seconds_per_step_mean"] or 0.0)))
    return {
        "chosen": chosen["name"],
        "batch": chosen["batch"],
        "fanout": chosen["fanout"],
        "dim": chosen["dim"],
        "layers": chosen["layers"],
        "checkpoint": bool(chosen.get("checkpoint")),
        "peak_vram_mib": chosen["peak_vram_mib"],
        "peak_reserved_mib": chosen["peak_reserved_mib"],
        "vram_margin": chosen["vram_margin"],
        "vram_margin_reserved": chosen["vram_margin_reserved"],
        "rule": "entre as configurações do MVP sem OOM e com margem >= 25% sob o teto de 6,5 GB tanto no pico alocado quanto no reservado pelo allocator, escolhe a de maior margem mínima; desempate por menor tempo/passo (critério apenas de recursos, nunca de métrica)",
    }


def _dominates(row: dict, dim: int, layers: int, fanout: tuple[int, ...], batch: int) -> bool:
    return (
        row["group"] == "mvp"
        and row["dim"] == dim
        and row["layers"] == layers
        and len(row["fanout"]) == len(fanout)
        and all(row["fanout"][index] >= fanout[index] for index in range(len(fanout)))
        and row["batch"] >= batch
    )


def envelope(rows: list[dict]) -> dict:
    trials = []
    for name, dim, layers, fanout, batch in PROTOCOL_TRIALS:
        bounds = [row for row in rows if _dominates(row, dim, layers, fanout, batch)]
        chosen_row = None
        precision = None
        checkpoint = None
        for candidate_precision, candidate_checkpoint in COMBINATION_ORDER:
            for row in bounds:
                if row["precision"] != candidate_precision or bool(row.get("checkpoint")) != candidate_checkpoint:
                    continue
                if not _eligible(row):
                    continue
                if chosen_row is None or row["peak_reserved_mib"] < chosen_row["peak_reserved_mib"]:
                    chosen_row = row
                    precision = candidate_precision
                    checkpoint = candidate_checkpoint
            if chosen_row is not None:
                break
        trials.append({
            "trial": name,
            "dim": dim,
            "layers": layers,
            "fanout": list(fanout),
            "batch": batch,
            "bound_row": chosen_row["name"] if chosen_row else None,
            "bound_peak_vram_mib": chosen_row["peak_vram_mib"] if chosen_row else None,
            "bound_peak_reserved_mib": chosen_row["peak_reserved_mib"] if chosen_row else None,
            "bound_vram_margin": chosen_row["vram_margin"] if chosen_row else None,
            "bound_vram_margin_reserved": chosen_row["vram_margin_reserved"] if chosen_row else None,
            "bound_margin_min": round(_margin_min(chosen_row), 4) if chosen_row else None,
            "recommended_precision": precision,
            "recommended_checkpoint": checkpoint,
            "within_cap": bool(chosen_row is not None and _margin_min(chosen_row) >= MARGIN_MIN),
        })
    return {
        "rule": "cada trial congelado do R07 é limitado por dominância (mesmo dim/camadas, fanout e batch maiores ou iguais) pelo pico medido; a precisão/checkpoint vem da primeira combinação viável na ordem declarada (fp32, fp32+checkpoint, amp, amp+checkpoint), sempre com margem >= 25% sob o teto de 6,5 GB no pico alocado e no reservado",
        "trials": trials,
        "all_within_cap": all(trial["within_cap"] for trial in trials),
        "precisions": sorted({trial["recommended_precision"] for trial in trials if trial["recommended_precision"]}),
        "precisions_with_checkpoint": sorted({f"{trial['recommended_precision']}+checkpoint" for trial in trials if trial["recommended_checkpoint"]}),
    }


def run(workdir: Path, report_path: Path, seed: int = MASTER_SEED, device: str | None = None, probe_name: str | None = None) -> dict:
    import torch

    started = time.perf_counter()
    workdir = Path(workdir).resolve()
    report_path = Path(report_path).resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    graph = load_graph()
    rows = []
    for config in grid_rows():
        try:
            row = run_config(graph, config, seed, device, SHORT_STEPS)
        except RuntimeError as error:
            row = {
                "name": config["name"],
                "group": config["group"],
                "dim": config["dim"],
                "layers": config["layers"],
                "fanout": list(config["fanout"]),
                "batch": config["batch"],
                "precision": config["precision"],
                "variant_of": config["variant_of"],
                "steps": 0,
                "oom": "out of memory" in str(error).lower(),
                "error": str(error)[:200],
                "peak_vram_mib": None,
                "vram_margin": None,
            }
            if device == "cuda":
                torch.cuda.empty_cache()
        rows.append(row)
        if device == "cuda":
            torch.cuda.empty_cache()
    chosen = choose_config(rows)
    epoch = None
    target_name = probe_name or chosen["chosen"]
    probe = next((config for config in grid_rows() if config["name"] == target_name), None)
    if probe is not None:
        try:
            epoch = epoch_probe(graph, probe, seed, device)
        except RuntimeError as error:
            epoch = {"name": probe["name"], "oom": "out of memory" in str(error).lower(), "error": str(error)[:200], "within_tolerance": False}
    worker_config = probe or next(config for config in grid_rows() if config["group"] == "sampling")
    workers = worker_reproducibility(graph, worker_config, seed)
    precision = precision_equivalence(graph, worker_config, seed, device)
    checkpoint_equiv = checkpoint_equivalence(graph, worker_config, seed, device)
    report = {
        "schema": SCHEMA,
        "status": "exploratory-only; somente fonte; sem nenhum dado do alvo",
        "device": device,
        "cuda_name": torch.cuda.get_device_name(0) if device == "cuda" else None,
        "vram_cap_mib": round(VRAM_CAP_MIB, 1),
        "margin_min": MARGIN_MIN,
        "grid": rows,
        "choice": chosen,
        "envelope": envelope(rows),
        "epoch_projection": epoch,
        "worker_reproducibility": workers,
        "precision_equivalence": precision,
        "checkpoint_equivalence": checkpoint_equiv,
        "declared": {
            "short_steps": SHORT_STEPS,
            "epoch_probe_steps": 10,
            "epoch_tolerance": EPOCH_TOLERANCE,
            "precision_tolerance": PRECISION_TOLERANCE,
            "checkpoint_tolerance": CHECKPOINT_TOLERANCE,
            "combination_order": [list(combination) for combination in COMBINATION_ORDER],
            "grid_predeclared": [config["name"] for config in grid_rows()],
            "protocol_trials": [list(trial) for trial in PROTOCOL_TRIALS],
            "no_target_selection": "o critério de escolha usa apenas VRAM/tempo; nenhuma métrica do alvo existe ou foi aberta",
        },
        "resources": {
            "seconds": round(time.perf_counter() - started, 3),
            "peak_rss_mib": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1),
        },
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def check_report(path: Path) -> list[str]:
    failures: list[str] = []
    path = Path(path).resolve()
    if not path.exists():
        return [f"relatório ausente: {path}"]
    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("schema") != SCHEMA:
        failures.append("schema divergente")
    status = str(report.get("status", ""))
    if "exploratory-only" not in status or "sem nenhum dado do alvo" not in status:
        failures.append("status deve declarar modo exploratório e ausência de dados do alvo")
    grid = report.get("grid", [])
    if not set(report["declared"]["grid_predeclared"]) <= {row["name"] for row in grid}:
        failures.append("grid medido diverge do pré-definido")
    if len(grid) < 16:
        failures.append("grid pequeno demais para a calibração (esperado >= 16 configurações)")
    for row in grid:
        if row.get("oom") and row.get("vram_margin") is None:
            continue
        if row.get("peak_vram_mib") is not None and row["peak_vram_mib"] > VRAM_CAP_MIB:
            failures.append(f"config '{row['name']}' acima do teto de VRAM")
        if row.get("peak_reserved_mib") is not None and row["peak_reserved_mib"] > VRAM_CAP_MIB:
            failures.append(f"config '{row['name']}' acima do teto de VRAM reservada")
        if row.get("steps", 0) <= 0 and not row.get("oom"):
            failures.append(f"config '{row['name']}' sem passos medidos")
        if row.get("peak_vram_mib") is not None and row.get("vram_margin_reserved") is None:
            failures.append(f"config '{row['name']}' sem margem reservada medida")
    choice = report.get("choice", {})
    if not choice.get("chosen"):
        failures.append("nenhuma configuração escolhida com margem")
    else:
        chosen_row = next(row for row in grid if row["name"] == choice["chosen"])
        if chosen_row.get("oom"):
            failures.append("configuração escolhida com OOM")
        if float(chosen_row.get("vram_margin", -1)) < MARGIN_MIN:
            failures.append("configuração escolhida sem margem mínima")
        if float(chosen_row.get("vram_margin_reserved", -1)) < MARGIN_MIN:
            failures.append("configuração escolhida sem margem mínima no pico reservado")
        if "recursos" not in str(choice.get("rule", "")):
            failures.append("regra de escolha deve ser apenas de recursos")
    envelope_block = report.get("envelope") or {}
    trials = envelope_block.get("trials", [])
    if [trial.get("trial") for trial in trials] != [trial[0] for trial in PROTOCOL_TRIALS]:
        failures.append("envelope não cobre exatamente os 12 trials congelados do R07")
    if not envelope_block.get("all_within_cap"):
        failures.append("nem todo trial do R07 cabe no teto com margem")
    for trial in trials:
        if not trial.get("bound_row"):
            failures.append(f"trial {trial.get('trial')} sem configuração limitante medida")
        if trial.get("bound_row") and trial.get("bound_peak_reserved_mib") is None:
            failures.append(f"trial {trial.get('trial')} sem pico reservado medido")
        if not trial.get("within_cap"):
            failures.append(f"trial {trial.get('trial')} fora do teto de VRAM com margem")
        if trial.get("recommended_precision") not in ("fp32", "amp"):
            failures.append(f"trial {trial.get('trial')} sem precisão recomendada")
        if not isinstance(trial.get("recommended_checkpoint"), bool):
            failures.append(f"trial {trial.get('trial')} sem decisão de checkpoint")
    epoch = report.get("epoch_projection") or {}
    if not epoch:
        failures.append("projeção de época ausente")
    else:
        if epoch.get("steps_per_epoch", 0) <= 0 or (epoch.get("measured_epoch_seconds") or 0) <= 0:
            failures.append("medição de época inválida")
        if not epoch.get("within_tolerance"):
            failures.append("projeção de época fora da tolerância da medição")
        if epoch.get("sample_seconds_mean") is None:
            failures.append("fração de sampling CPU por passo não medida")
    workers = report.get("worker_reproducibility", {})
    if not workers.get("identical"):
        failures.append("sampling não é reproduzível entre CPU workers")
    if workers.get("cpu_count", 0) <= 0:
        failures.append("contagem de CPUs ausente")
    precision = report.get("precision_equivalence", {})
    if precision.get("applicable") and not precision.get("within_tolerance"):
        failures.append("mixed precision fora da tolerância de equivalência")
    if not precision.get("applicable"):
        failures.append("equivalência de mixed precision deve ser medida em CUDA")
    checkpoint_equiv = report.get("checkpoint_equivalence", {})
    if checkpoint_equiv.get("applicable") and not checkpoint_equiv.get("within_tolerance"):
        failures.append("modo com checkpoint fora da tolerância de equivalência")
    if not checkpoint_equiv.get("applicable"):
        failures.append("equivalência do mode com checkpoint deve ser medida em CUDA")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("run", "check"))
    parser.add_argument("--workdir", type=Path, default=ROOT / "runs" / "m04")
    parser.add_argument("--report", type=Path, default=ROOT / "artifacts" / "reports" / "M04-RECURSOS.json")
    parser.add_argument("--device", choices=("cpu", "cuda"), default=None)
    args = parser.parse_args()
    try:
        if args.command == "run":
            report = run(args.workdir, args.report, device=args.device)
            print(json.dumps({
                "device": report["device"],
                "choice": report["choice"],
                "envelope": {key: report["envelope"][key] for key in ("all_within_cap", "precisions")},
                "epoch_projection": {key: report["epoch_projection"][key] for key in ("relative_error", "within_tolerance", "sample_seconds_mean", "compute_seconds_mean")},
                "worker_reproducibility": {key: report["worker_reproducibility"][key] for key in ("identical", "cpu_count")},
                "precision_equivalence": report["precision_equivalence"],
                "checkpoint_equivalence": {key: report["checkpoint_equivalence"][key] for key in ("relative_difference", "within_tolerance")},
                "resources": report["resources"],
            }, ensure_ascii=False, sort_keys=True))
        else:
            failures = check_report(args.report)
            if failures:
                for failure in failures:
                    print(f"FALHA: {failure}")
                return 1
            print("OK: calibração M04 validada (VRAM, OOM, envelope, workers, precisão e época)")
    except (FileNotFoundError, json.JSONDecodeError) as error:
        print(f"FALHA: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
