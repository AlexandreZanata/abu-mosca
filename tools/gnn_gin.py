#!/usr/bin/env python3
"""Encoder GIN comparável ao GraphSAGE do MVP (M03).

Implementa o candidato alternativo sob o **mesmo harness** de M01/M02: mesmas
features de H05, mesmo neighbor sampling, mesmo decoder/loss e mesmas
verificações, trocando apenas a agregação (soma ponderada sem normalização por
grau, com MLP e epsilon por camada, em vez de média ponderada com projeções
lineares). As configurações são pareadas em contagem exata de parâmetros com o
grid emendado do R07 (2 e 3 camadas) e as diferenças inevitáveis entre as
arquiteturas ficam registradas. Somente fonte, sem dado do alvo.
"""

import argparse
import dataclasses
import json
import resource
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import gnn_graphsage as gg  # noqa: E402

MASTER_SEED = 20260914
SCHEMA = "m03-gin"
MVP_RANGE = gg.MVP_RANGE
PAIRING_TRIALS = {2: "T01", 3: "T03"}
PARAMETER_TOLERANCE = 0.05
FIXTURE_TRAINING = {"lr": 1e-3, "steps": 4000, "note": "taxa do grid; GIN com soma não normalizada precisa de mais passos que a média ponderada para estabilizar no fixture"}
GIN_DIFFERENCES = (
    "agregação por soma ponderada, sem normalização por grau (GraphSAGE usa média ponderada): "
    "embeddings podem crescer com o grau/prevalência e a escala não é invariante à densidade "
    "(no fixture, a loss inicial fica na casa de 10³ e o overfit exige ~4× mais passos que a média)",
    "MLP interno (Linear→ReLU→Linear) por camada em vez de três projeções lineares (self/in/out), "
    "o que muda a forma funcional e exige dims diferentes para parear parâmetros",
    "epsilon aprendível por camada (mais 1 parâmetro por camada), ausente no GraphSAGE implementado",
    "direção tratada por duas somas separadas (entrada/saída) com os mesmos pesos, como em M02; "
    "GIN original não define direção, então a adaptação é explícita e não uma equivalência",
    "soma ponderada com peso **bruto** divergiu numericamente no grafo denso (loss inicial ~1e23, run "
    "descartada e registrada); pela incompatibilidade documentada em L06/M-10 (soma pressupõe arestas sem "
    "peso), a tarefa do GIN usa a variante **binária pré-registrada de H06** como peso de mensagem, "
    "mantendo o mesmo objetivo (alvo de existência + log1p do peso bruto) e o mesmo decoder",
    "com peso binário, mensagens ainda crescem com o número de vizinhos (sem normalização por grau): "
    "no fixture o overfit exige ~4× mais passos que a média ponderada do GraphSAGE",
)


class GinError(RuntimeError):
    pass


@dataclasses.dataclass(frozen=True)
class GINConfig:
    dim: int
    layers: int
    fanout: tuple[int, ...]
    dropout: float = 0.0
    input_dim: int = len(gg.FEATURE_NAMES)

    def validate(self) -> None:
        if self.dim <= 0 or self.layers <= 0:
            raise GinError("dim/layers devem ser positivos")
        if len(self.fanout) != self.layers:
            raise GinError("fanout deve ter um valor por camada")
        if not 0.0 <= self.dropout < 1.0:
            raise GinError("dropout deve ficar em [0,1)")

    def to_dict(self) -> dict:
        payload = dataclasses.asdict(self)
        payload["fanout"] = list(self.fanout)
        payload["aggregation"] = "sum"
        return payload


def gin_parameter_formula(config: GINConfig) -> int:
    """MLP(in, dim, dim) + epsilon por camada; contagem fechada."""
    config.validate()
    total = 0
    previous = config.input_dim
    for _ in range(config.layers):
        total += (previous * config.dim + config.dim) + (config.dim * config.dim + config.dim) + 1
        previous = config.dim
    return total


def paired_gin_dim(layers: int, target_parameters: int, low: int = 64, high: int = 1536) -> dict:
    best = None
    for dim in range(low, high + 1):
        config = GINConfig(dim=dim, layers=layers, fanout=(10,) * layers)
        count = gin_parameter_formula(config)
        delta = abs(count - target_parameters)
        if best is None or delta < best["delta_parameters"]:
            best = {"dim": dim, "parameters": count, "delta_parameters": delta, "relative_delta": delta / target_parameters}
    return best


def pairing_table() -> list[dict]:
    rows = []
    grid = {row["trial"]: row for row in gg.grid_parameter_counts()}
    for layers, trial in PAIRING_TRIALS.items():
        reference = grid[trial]
        paired = paired_gin_dim(layers, reference["parameters"])
        config = GINConfig(dim=paired["dim"], layers=layers, fanout=gg.pad_fanout(layers, reference["fanout"]), dropout=0.1)
        rows.append(
            {
                "layers": layers,
                "graphsage": {"trial": trial, "dim": reference["dim"], "parameters": reference["parameters"], "fanout": reference["fanout"]},
                "gin": {"dim": config.dim, "parameters": paired["parameters"], "fanout": list(config.fanout), "dropout": config.dropout},
                "delta_parameters": paired["delta_parameters"],
                "relative_delta": round(paired["relative_delta"], 6),
                "within_tolerance": paired["relative_delta"] <= PARAMETER_TOLERANCE,
                "both_in_mvp_range": bool(MVP_RANGE[0] <= reference["parameters"] <= MVP_RANGE[1] and MVP_RANGE[0] <= paired["parameters"] <= MVP_RANGE[1]),
            }
        )
    return rows


def _gin_classes():
    import torch

    cached = getattr(_gin_classes, "cached", None)
    if cached is not None:
        return cached

    class GINLayer(torch.nn.Module):
        def __init__(self, in_dim: int, out_dim: int):
            super().__init__()
            self.mlp = torch.nn.Sequential(
                torch.nn.Linear(in_dim, out_dim),
                torch.nn.ReLU(),
                torch.nn.Linear(out_dim, out_dim),
            )
            self.epsilon = torch.nn.Parameter(torch.zeros(1))

        def forward(self, hidden, in_agg, out_agg):
            return self.mlp((1.0 + self.epsilon) * hidden + in_agg + out_agg)

    class GINEncoder(torch.nn.Module):
        def __init__(self, config: GINConfig):
            super().__init__()
            config.validate()
            self.config = config
            layers = []
            previous = config.input_dim
            for _ in range(config.layers):
                layers.append(GINLayer(previous, config.dim))
                previous = config.dim
            self.layers = torch.nn.ModuleList(layers)
            self.dropout = torch.nn.Dropout(config.dropout)

    _gin_classes.cached = (GINLayer, GINEncoder)
    return _gin_classes.cached


def build_gin(config: GINConfig):
    _, encoder_class = _gin_classes()
    config.validate()
    return encoder_class(config)


def gin_parameter_count(encoder) -> int:
    return int(sum(parameter.numel() for parameter in encoder.parameters()))


def save_gin(path: Path, encoder, config: GINConfig) -> dict:
    import torch

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"config": config.to_dict(), "state_dict": encoder.state_dict()}, path)
    return {"path": str(path), "bytes": path.stat().st_size}


def load_gin(path: Path):
    import torch

    payload = torch.load(Path(path), map_location="cpu", weights_only=False)
    raw = payload["config"]
    config = GINConfig(dim=int(raw["dim"]), layers=int(raw["layers"]), fanout=tuple(int(value) for value in raw["fanout"]), dropout=float(raw.get("dropout", 0.0)))
    encoder = build_gin(config)
    encoder.load_state_dict(payload["state_dict"])
    return encoder, config


def fixture_smoke(seed: int = MASTER_SEED) -> dict:
    import torch

    import ssl_decoder as sd

    def train_once() -> dict:
        torch.manual_seed(seed % (2**32))
        src, dst, weight, features, adjacency = gg._fixture_graph(seed=seed)
        n_nodes = features.shape[0]
        rng = np.random.RandomState((seed + 1) % (2**32))
        edge_order = rng.permutation(len(src))
        val_index = edge_order[: max(4, len(src) // 5)]
        train_index = edge_order[max(4, len(src) // 5) :]
        binary = np.ones_like(weight)
        in_edges = gg.csr_edges(gg.build_direction_csr(src, dst, binary, n_nodes, "in"))
        out_edges = gg.csr_edges(gg.build_direction_csr(src, dst, binary, n_nodes, "out"))
        config = GINConfig(dim=16, layers=2, fanout=(n_nodes, n_nodes), dropout=0.0)
        encoder = build_gin(config)
        decoder = sd.BilinearDecoder(config.dim)
        optimizer = torch.optim.Adam(list(encoder.parameters()) + list(decoder.parameters()), lr=FIXTURE_TRAINING["lr"])
        losses = []
        for _ in range(FIXTURE_TRAINING["steps"]):
            embeddings = gg.forward_full(encoder, features, in_edges, out_edges, training=True, aggregation="sum")
            negative_target = gg._draw_true_negatives(adjacency, rng, src[train_index])
            parts = sd.masked_edge_weight_loss(
                decoder,
                embeddings[src[train_index]],
                embeddings[dst[train_index]],
                torch.from_numpy(weight[train_index].astype(np.float32)),
                embeddings[src[train_index]],
                embeddings[negative_target],
            )
            optimizer.zero_grad()
            parts["loss"].backward()
            optimizer.step()
            losses.append(float(parts["loss"].detach()))
        def pair_auc(edge_index):
            with torch.no_grad():
                encoder.eval()
                decoder.eval()
                embeddings = gg.forward_full(encoder, features, in_edges, out_edges, aggregation="sum")
                scores = decoder(embeddings[src[edge_index]], embeddings[dst[edge_index]])[0].numpy()
                negatives = gg._draw_true_negatives(adjacency, rng, src[edge_index])
                negative_scores = decoder(embeddings[src[edge_index]], embeddings[negatives])[0].numpy()
            ranked = np.concatenate([scores, negative_scores])
            labels = np.concatenate([np.ones(len(scores)), np.zeros(len(negative_scores))])
            import scipy.stats as stats

            ranks = stats.rankdata(ranked)
            positives, negatives_count = int(labels.sum()), int(len(labels) - labels.sum())
            return float((ranks[labels == 1].sum() - positives * (positives + 1) / 2) / (positives * negatives_count))
        gradients_finite = all(bool(torch.isfinite(p.grad).all()) for p in encoder.parameters() if p.grad is not None)
        return {
            "encoder": encoder,
            "config": config,
            "embeddings": gg.forward_full(encoder, features, in_edges, out_edges, aggregation="sum").detach().numpy(),
            "auc_train": pair_auc(train_index),
            "auc_validation": pair_auc(val_index),
            "loss_first": losses[0],
            "loss_last": losses[-1],
            "gradients_finite": gradients_finite,
            "encoder_parameters": gin_parameter_count(encoder),
            "parameters_formula": gin_parameter_formula(config),
            "graph_edges": int(len(src)),
            "validation_edges": int(len(val_index)),
            "features": features,
            "edges": (in_edges, out_edges),
        }

    first = train_once()
    second = train_once()
    buffer = Path("/tmp") / f"m03-gin-fixture-{seed % 100000}.pt"
    save_info = save_gin(buffer, first["encoder"], first["config"])
    reloaded, reloaded_config = load_gin(buffer)
    original = gg.forward_full(first["encoder"], first["features"], first["edges"][0], first["edges"][1], aggregation="sum")
    restored = gg.forward_full(reloaded, first["features"], first["edges"][0], first["edges"][1], aggregation="sum")
    return {
        "nodes": int(first["embeddings"].shape[0]),
        "graph_edges": first["graph_edges"],
        "validation_edges": first["validation_edges"],
        "encoder_parameters": first["encoder_parameters"],
        "parameters_formula": first["parameters_formula"],
        "overfit_train_auc": round(float(first["auc_train"]), 6),
        "validation_auc": round(float(first["auc_validation"]), 6),
        "loss_first": round(float(first["loss_first"]), 6),
        "loss_last": round(float(first["loss_last"]), 6),
        "gradients_finite": bool(first["gradients_finite"]),
        "deterministic_same_seed": bool(np.array_equal(first["embeddings"], second["embeddings"])),
        "serialization_max_abs_diff": float((original - restored).abs().max()),
        "serialization_bytes": save_info["bytes"],
        "reloaded_config_matches": reloaded_config == first["config"],
        "fixture_training": FIXTURE_TRAINING,
    }


def real_graph_smoke(snapshot: Path = gg.SOURCE_SNAPSHOT, seed: int = MASTER_SEED, batch: int = 64, steps: int = 10, device: str | None = None, edge_weight_mode: str = "binary") -> dict:
    import torch

    import ssl_decoder as sd
    import ssl_task as st

    use_cuda = bool(torch.cuda.is_available()) if device is None else device == "cuda"
    device = "cuda" if use_cuda else "cpu"
    torch.manual_seed(seed % (2**32))
    ids, src, dst, weight = st.load_source_edges(snapshot)
    n_nodes = len(ids)
    mask_info = st.build_mask(src, dst, n_nodes, st.seedlib.derive_seed(seed, "m01", "mask"))
    mask = mask_info["mask"]
    train_src, train_dst, train_wgt = st.training_view(src, dst, weight, mask)
    message_weights = np.ones_like(train_wgt) if edge_weight_mode == "binary" else train_wgt.astype(np.float64)
    in_csr = gg.build_direction_csr(train_src, train_dst, message_weights, n_nodes, "in")
    out_csr = gg.build_direction_csr(train_src, train_dst, message_weights, n_nodes, "out")
    in_csr_raw = gg.build_direction_csr(train_src, train_dst, train_wgt, n_nodes, "in")
    _, raw_features = gg.snapshot_features(snapshot)
    _, features = gg.fit_transform_stats(raw_features)
    layers = 3
    reference = next(row for row in pairing_table() if row["layers"] == layers)
    config = GINConfig(dim=int(reference["gin"]["dim"]), layers=layers, fanout=tuple(reference["gin"]["fanout"]), dropout=0.1)
    encoder = build_gin(config).to(device)
    decoder = sd.BilinearDecoder(config.dim).to(device)
    optimizer = torch.optim.Adam(list(encoder.parameters()) + list(decoder.parameters()), lr=1e-3)
    rng = np.random.RandomState((seed + 7) % (2**32))
    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()
    started = time.perf_counter()
    losses = []
    subgraph = None
    for step in range(steps):
        targets = np.sort(rng.choice(n_nodes, size=batch, replace=False))
        subgraph = gg.sample_subgraph(targets, in_csr, out_csr, config.fanout, (seed + step) % (2**32))
        embeddings = gg.forward_sampled(encoder, features, subgraph, training=True, aggregation="sum", device=device)
        adjacency = np.zeros((batch, batch), dtype=bool)
        edge_weight = np.zeros((batch, batch), dtype=np.float64)
        for position, node in enumerate(targets):
            start, finish = in_csr_raw.indptr[node], in_csr_raw.indptr[node + 1]
            neighbors, weights = in_csr_raw.indices[start:finish], in_csr_raw.data[start:finish]
            slots = np.searchsorted(targets, neighbors)
            valid = (slots < batch) & (targets[np.clip(slots, 0, batch - 1)] == neighbors)
            adjacency[position, slots[valid]] = True
            edge_weight[position, slots[valid]] = weights[valid]
        upper = np.triu_indices(batch, k=1)
        positive_slots = np.nonzero(adjacency[upper])[0]
        negative_slots = np.nonzero(~adjacency[upper])[0]
        count = int(min(64, len(positive_slots)))
        if count == 0:
            continue
        picked = rng.choice(len(positive_slots), size=count, replace=False)
        chosen_negatives = rng.choice(len(negative_slots), size=count, replace=False)
        positive_rows = positive_slots[picked]
        negative_rows = negative_slots[chosen_negatives]
        parts = sd.masked_edge_weight_loss(
            decoder,
            embeddings[upper[0][positive_rows]],
            embeddings[upper[1][positive_rows]],
            gg._weight_tensor(edge_weight[upper[0][positive_rows], upper[1][positive_rows]]).to(device),
            embeddings[upper[0][negative_rows]],
            embeddings[upper[1][negative_rows]],
        )
        optimizer.zero_grad()
        parts["loss"].backward()
        optimizer.step()
        losses.append(float(parts["loss"].detach()))
    seconds = time.perf_counter() - started
    finite = all(np.isfinite(value) for value in losses)
    diverged = (not finite) or (len(losses) >= 2 and losses[-1] > 10.0 * losses[0]) or (losses and abs(losses[0]) > 1e6)
    sparse_bytes = int(in_csr_raw.data.nbytes + in_csr_raw.indices.nbytes + in_csr_raw.indptr.nbytes + out_csr.data.nbytes + out_csr.indices.nbytes + out_csr.indptr.nbytes)
    dense_bytes = int(2 * n_nodes * n_nodes * 8)
    return {
        "device": device,
        "cuda_available": bool(torch.cuda.is_available()),
        "vram_peak_mib": round(torch.cuda.max_memory_allocated() / 1024 / 1024, 1) if device == "cuda" else None,
        "steps": steps,
        "batch": batch,
        "fanout": list(config.fanout),
        "dim": config.dim,
        "encoder_parameters": gin_parameter_count(encoder),
        "loss_first": float(losses[0]) if losses else None,
        "loss_last": float(losses[-1]) if losses else None,
        "seconds": round(seconds, 3),
        "sampled_nodes": int(subgraph["sampled_nodes"]) if subgraph else 0,
        "edges_per_layer": subgraph["edges_per_layer"] if subgraph else [],
        "train_edges": int(len(train_src)),
        "edge_weight_mode": edge_weight_mode,
        "diverged": bool(diverged),
        "sparse_bytes": sparse_bytes,
        "dense_equivalent_bytes": dense_bytes,
        "sparse_ratio": round(sparse_bytes / dense_bytes, 6),
    }


def run(workdir: Path, report_path: Path, seed: int = MASTER_SEED, device: str | None = None) -> dict:
    started = time.perf_counter()
    workdir = Path(workdir).resolve()
    report_path = Path(report_path).resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    pairing = pairing_table()
    report = {
        "schema": SCHEMA,
        "status": "exploratory-only; somente fonte; sem nenhum dado do alvo",
        "config": {
            "aggregation": "sum",
            "edge_weight_mode": "binary (H06)",
            "activation": "relu",
            "epsilon": "aprendível por camada",
            "features": list(gg.FEATURE_NAMES),
            "per_node_parameters": 0,
            "max_source_nodes": None,
        },
        "pairing": {
            "rule": "menor dim de GIN cuja contagem de parâmetros minimiza a diferença para o trial do grid emendado com o mesmo número de camadas; fanout e dropout do trial pareado",
            "tolerance": PARAMETER_TOLERANCE,
            "rows": pairing,
            "all_within_tolerance": all(row["within_tolerance"] and row["both_in_mvp_range"] for row in pairing),
        },
        "inevitable_differences": list(GIN_DIFFERENCES),
        "fixture_smoke": fixture_smoke(seed=seed),
        "real_graph_smoke": real_graph_smoke(seed=seed, device=device, edge_weight_mode="binary"),
        "resources": {"seconds": round(time.perf_counter() - started, 3), "peak_rss_mib": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)},
    }
    raw_smoke = real_graph_smoke(seed=seed, device=device, edge_weight_mode="raw")
    report["discarded_runs"] = [
        {
            "edge_weight_mode": "raw",
            "reason": "divergência numérica por soma não normalizada no grafo denso (magnitude explosiva)",
            "diverged": bool(raw_smoke["diverged"]),
            "loss_first": raw_smoke["loss_first"],
            "loss_last": raw_smoke["loss_last"],
            "device": raw_smoke["device"],
            "steps": raw_smoke["steps"],
        }
    ]
    primary = report["real_graph_smoke"]
    report["candidate_status"] = {
        "usable_in_m05_as_implemented": not bool(primary["diverged"]),
        "summary": (
            "GIN com soma não normalizada é incompatível com o grafo denso como implementado (divergência "
            "numérica); R07 §4 prevê relatar a incompatibilidade, não silenciá-la"
            if primary["diverged"]
            else "GIN pareado estável no smoke; apto como candidato comparável"
        ),
        "decision_needed_from": "revisor humano (G5, condição 6) se uma variante normalizada for desejada",
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
    config = report.get("config", {})
    if int(config.get("per_node_parameters", -1)) != 0 or config.get("max_source_nodes") is not None:
        failures.append("GIN não pode ter parâmetros por node nem depender do número de nós")
    if config.get("aggregation") != "sum":
        failures.append("agregação do GIN deve ser soma ponderada")
    if "binary" not in str(config.get("edge_weight_mode", "")):
        failures.append("GIN deve declarar a variante binária de peso como incompatibilidade de H06")
    if "binary" not in str(report.get("real_graph_smoke", {}).get("edge_weight_mode", "")):
        failures.append("smoke do GIN deve registrar o modo de peso binário")
    pairing = report.get("pairing", {})
    rows = pairing.get("rows", [])
    if {row.get("layers") for row in rows} != {2, 3}:
        failures.append("pareamento deve cobrir 2 e 3 camadas")
    for row in rows:
        config_gin = GINConfig(dim=int(row["gin"]["dim"]), layers=int(row["layers"]), fanout=tuple(int(value) for value in row["gin"]["fanout"]), dropout=float(row["gin"]["dropout"]))
        expected = gin_parameter_formula(config_gin)
        if int(row["gin"]["parameters"]) != expected:
            failures.append(f"contagem de parâmetros do GIN divergente em {row['layers']} camadas")
        graphsage_config = gg.EncoderConfig(dim=int(row["graphsage"]["dim"]), layers=int(row["layers"]), fanout=gg.pad_fanout(int(row["layers"]), row["graphsage"]["fanout"]))
        if int(row["graphsage"]["parameters"]) != gg.parameter_count_formula(graphsage_config):
            failures.append(f"contagem de parâmetros do GraphSAGE divergente em {row['layers']} camadas")
        if float(row.get("relative_delta", 1.0)) > PARAMETER_TOLERANCE:
            failures.append(f"pareamento fora da tolerância em {row['layers']} camadas")
        if not row.get("both_in_mvp_range"):
            failures.append(f"pareamento fora do intervalo do MVP em {row['layers']} camadas")
        if list(gg.pad_fanout(int(row["layers"]), row["graphsage"]["fanout"])) != list(row["gin"]["fanout"]):
            failures.append(f"fanout divergente no pareamento de {row['layers']} camadas")
    if not pairing.get("all_within_tolerance"):
        failures.append("nem todo pareamento está na tolerância")
    if len(report.get("inevitable_differences", [])) < 4:
        failures.append("diferenças inevitáveis insuficientes")
    fixture = report.get("fixture_smoke", {})
    if float(fixture.get("overfit_train_auc", -1)) < 0.95:
        failures.append("overfit controlado de fixture abaixo do esperado")
    if not fixture.get("gradients_finite") or not fixture.get("deterministic_same_seed"):
        failures.append("fixture sem gradientes finitos/determinismo")
    if not fixture.get("reloaded_config_matches") or float(fixture.get("serialization_max_abs_diff", 1.0)) > 1e-6:
        failures.append("serialização divergente")
    if int(fixture.get("encoder_parameters", -1)) != int(fixture.get("parameters_formula", -2)):
        failures.append("contagem exata difere da fórmula na fixture")
    smoke = report.get("real_graph_smoke", {})
    if int(smoke.get("encoder_parameters", -1)) <= 0:
        failures.append("smoke sem contagem de parâmetros")
    if smoke.get("diverged"):
        status = report.get("candidate_status", {})
        if status.get("usable_in_m05_as_implemented") is not False:
            failures.append("smoke divergente exige status de candidato incompatível")
        if not report.get("discarded_runs") or not report["discarded_runs"][0].get("diverged"):
            failures.append("incompatibilidade exige run descartada registrada")
        if "R07" not in str(status.get("summary", "")):
            failures.append("incompatibilidade deve referenciar a provisão de R07 §4")
    elif smoke.get("loss_first") is None or float(smoke.get("loss_last", 1.0)) > float(smoke.get("loss_first", 0.0)):
        failures.append("smoke não reduziu a loss")
    if int(smoke.get("sparse_bytes", 0)) >= int(smoke.get("dense_equivalent_bytes", 1)):
        failures.append("representação deveria permanecer esparsa")
    if int(smoke.get("sampled_nodes", 0)) <= 0 or len(smoke.get("fanout", [])) <= 0:
        failures.append("smoke sem sampling")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("run", "check"))
    parser.add_argument("--workdir", type=Path, default=ROOT / "runs" / "m03")
    parser.add_argument("--report", type=Path, default=ROOT / "artifacts" / "reports" / "M03-GIN.json")
    parser.add_argument("--device", choices=("cpu", "cuda"), default=None)
    args = parser.parse_args()
    try:
        if args.command == "run":
            report = run(args.workdir, args.report, device=args.device)
            print(json.dumps({
                "pairing": report["pairing"]["rows"],
                "fixture_smoke": report["fixture_smoke"],
                "real_graph_smoke": report["real_graph_smoke"],
                "resources": report["resources"],
            }, ensure_ascii=False, sort_keys=True))
        else:
            failures = check_report(args.report)
            if failures:
                for failure in failures:
                    print(f"FALHA: {failure}")
                return 1
            print("OK: GIN M03 validado (pareamento, fixture, serialização, sampling e esparsidade)")
    except (GinError, FileNotFoundError, json.JSONDecodeError) as error:
        print(f"FALHA: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
