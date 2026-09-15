#!/usr/bin/env python3
"""Encoder GraphSAGE indutivo dirigido/ponderado (M02).

Implementa o candidato primário do MVP (R07 §4): agregação por média ponderada
separada para vizinhos de entrada e de saída, sem nenhuma tabela de parâmetros
por node ID e sem camada dependente do número de nós. O módulo cobre o encoder,
o neighbor sampling determinístico (numpy), a serialização, a contagem exata de
parâmetros e o smoke em fixture e no grafo da fonte, além de registrar o
conflito entre o grid congelado do pré-registro (dim 64/128) e o intervalo de
1–3M parâmetros declarado para o MVP. Somente fonte, sem dado do alvo.
"""

import argparse
import dataclasses
import json
import resource
import sys
import time
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import scipy.sparse as sp
import scipy.stats as stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import topology_features as tf  # noqa: E402

MASTER_SEED = 20260914
SOURCE_SNAPSHOT = ROOT / "runs" / "h08" / "source"
SCHEMA = "m02-graphsage"
MVP_RANGE = (1_000_000, 3_000_000)
GRID_AMENDMENT = (
    "R07 §5 emendado em 2026-09-15 (changelog 3.0; decisão humana opção (a) da nota de bloqueio da M02): "
    "dim 576 para trials de 2 camadas e dim 408 para trials de 3 camadas"
)
FEATURE_NAMES = tf.FEATURE_NAMES
AGGREGATOR = "mean"
ACTIVATION = "relu"
WEIGHT_MODE = "raw"
GRID_TRIALS = (
    ("T01", 576, 2, (10, 10)),
    ("T02", 576, 2, (10, 10)),
    ("T03", 408, 3, (15, 10)),
    ("T04", 408, 3, (15, 10)),
    ("T05", 576, 2, (10, 10)),
    ("T06", 576, 2, (10, 10)),
    ("T07", 408, 3, (15, 10)),
    ("T08", 408, 3, (15, 10)),
    ("T09", 576, 2, (15, 10)),
    ("T10", 408, 3, (10, 10)),
    ("T11", 576, 2, (15, 10)),
    ("T12", 408, 3, (10, 10)),
)
CAPACITY_DIMS = (384, 408, 512, 576, 768, 1024)


class GraphSageError(RuntimeError):
    pass


FANOUT_CONVENTION = (
    "o grid do R07 lista dois fanouts para trials de três camadas; a convenção adotada repete o "
    "último valor nas camadas mais profundas (não altera o número de parâmetros)"
)


def pad_fanout(layers: int, fanout) -> tuple[int, ...]:
    values = [int(value) for value in fanout]
    if not values:
        raise GraphSageError("fanout vazio")
    while len(values) < layers:
        values.append(values[-1])
    return tuple(values)


@dataclasses.dataclass(frozen=True)
class EncoderConfig:
    dim: int
    layers: int
    fanout: tuple[int, ...]
    dropout: float = 0.0
    input_dim: int = len(FEATURE_NAMES)

    def validate(self) -> None:
        if self.dim <= 0:
            raise GraphSageError("dim deve ser positivo")
        if self.layers <= 0:
            raise GraphSageError("layers deve ser positivo")
        if len(self.fanout) != self.layers:
            raise GraphSageError("fanout deve ter um valor por camada")
        if not 0.0 <= self.dropout < 1.0:
            raise GraphSageError("dropout deve ficar em [0,1)")
        if self.input_dim <= 0:
            raise GraphSageError("input_dim deve ser positivo")

    def to_dict(self) -> dict:
        payload = dataclasses.asdict(self)
        payload["fanout"] = list(self.fanout)
        payload["aggregator"] = AGGREGATOR
        payload["activation"] = ACTIVATION
        payload["weight_mode"] = WEIGHT_MODE
        return payload


def parameter_count_formula(config: EncoderConfig) -> int:
    """Contagem fechada: 3 projeções por camada (self, entrada, saída), com viés."""
    config.validate()
    total = 0
    previous = config.input_dim
    for _ in range(config.layers):
        total += 3 * (previous * config.dim + config.dim)
        previous = config.dim
    return total


def parameter_count_two_projections(config: EncoderConfig) -> int:
    """Variante conservadora (self + uma projeção de vizinhos compartilhada)."""
    config.validate()
    total = 0
    previous = config.input_dim
    for _ in range(config.layers):
        total += 2 * (previous * config.dim + config.dim)
        previous = config.dim
    return total


def grid_parameter_counts() -> list[dict]:
    rows = []
    for name, dim, layers, fanout in GRID_TRIALS:
        config = EncoderConfig(dim=dim, layers=layers, fanout=pad_fanout(layers, fanout))
        rows.append(
            {
                "trial": name,
                "dim": dim,
                "layers": layers,
                "fanout": list(fanout),
                "parameters": parameter_count_formula(config),
                "parameters_two_projections": parameter_count_two_projections(config),
            }
        )
    return rows


def capacity_table() -> list[dict]:
    rows = []
    for dim in CAPACITY_DIMS:
        for layers in (2, 3):
            config = EncoderConfig(dim=dim, layers=layers, fanout=(10,) * layers)
            count = parameter_count_formula(config)
            rows.append({"dim": dim, "layers": layers, "parameters": count, "meets_mvp_range": MVP_RANGE[0] <= count <= MVP_RANGE[1]})
    return rows


def smallest_dims_for_range() -> list[dict]:
    rows = []
    for layers in (2, 3):
        for dim in range(64, 1537, 8):
            config = EncoderConfig(dim=dim, layers=layers, fanout=(10,) * layers)
            count = parameter_count_formula(config)
            if count >= MVP_RANGE[0]:
                rows.append({"layers": layers, "dim": dim, "parameters": count})
                break
    return rows


def _model_classes():
    import torch

    cached = getattr(_model_classes, "cached", None)
    if cached is not None:
        return cached

    class GraphSAGELayer(torch.nn.Module):
        def __init__(self, in_dim: int, out_dim: int):
            super().__init__()
            self.self_proj = torch.nn.Linear(in_dim, out_dim)
            self.in_proj = torch.nn.Linear(in_dim, out_dim)
            self.out_proj = torch.nn.Linear(in_dim, out_dim)

        def forward(self, hidden, in_agg, out_agg):
            return torch.relu(self.self_proj(hidden) + self.in_proj(in_agg) + self.out_proj(out_agg))

    class GraphSAGEEncoder(torch.nn.Module):
        def __init__(self, config: EncoderConfig):
            super().__init__()
            config.validate()
            self.config = config
            layers = []
            previous = config.input_dim
            for _ in range(config.layers):
                layers.append(GraphSAGELayer(previous, config.dim))
                previous = config.dim
            self.layers = torch.nn.ModuleList(layers)
            self.dropout = torch.nn.Dropout(config.dropout)

    _model_classes.cached = (GraphSAGELayer, GraphSAGEEncoder)
    return _model_classes.cached


def build_encoder(config: EncoderConfig):
    _, encoder_class = _model_classes()
    config.validate()
    return encoder_class(config)


def encoder_parameter_count(encoder) -> int:
    return int(sum(parameter.numel() for parameter in encoder.parameters()))


def _index_tensor(array):
    import torch

    return torch.as_tensor(np.asarray(array), dtype=torch.long)


def _weight_tensor(array):
    import torch

    return torch.as_tensor(np.asarray(array), dtype=torch.float32)


def weighted_mean(hidden, source_index, destination_index, edge_weight, n_rows: int):
    import torch

    if len(source_index) == 0:
        return torch.zeros(n_rows, hidden.shape[1], dtype=hidden.dtype, device=hidden.device)
    messages = hidden[source_index] * edge_weight.unsqueeze(1)
    aggregated = torch.zeros(n_rows, hidden.shape[1], dtype=hidden.dtype, device=hidden.device).index_add_(0, destination_index, messages)
    denominator = torch.zeros(n_rows, dtype=hidden.dtype, device=hidden.device).index_add_(0, destination_index, edge_weight)
    return aggregated / denominator.clamp(min=1e-6).unsqueeze(1)


AGGREGATION_MODES = ("mean", "sum")


def aggregate(hidden, source_index, destination_index, edge_weight, n_rows: int, mode: str = "mean"):
    import torch

    if mode not in AGGREGATION_MODES:
        raise GraphSageError(f"agregação desconhecida: {mode}")
    source_index = source_index.to(hidden.device)
    destination_index = destination_index.to(hidden.device)
    edge_weight = edge_weight.to(hidden.device)
    if len(source_index) == 0:
        return torch.zeros(n_rows, hidden.shape[1], dtype=hidden.dtype, device=hidden.device)
    messages = hidden[source_index] * edge_weight.unsqueeze(1)
    aggregated = torch.zeros(n_rows, hidden.shape[1], dtype=hidden.dtype, device=hidden.device).index_add_(0, destination_index, messages)
    if mode == "sum":
        return aggregated
    denominator = torch.zeros(n_rows, dtype=hidden.dtype, device=hidden.device).index_add_(0, destination_index, edge_weight)
    return aggregated / denominator.clamp(min=1e-6).unsqueeze(1)


def forward_full(encoder, features: np.ndarray, in_edges, out_edges, training: bool = False, aggregation: str = "mean", device: str = "cpu"):
    """Passagem completa (sem sampling); edges = (origem visualizada, destino, peso)."""
    import torch

    encoder.train(training)
    hidden = torch.as_tensor(np.asarray(features), dtype=torch.float32, device=device)
    n_rows = features.shape[0]
    for layer in encoder.layers:
        in_agg = aggregate(hidden, _index_tensor(in_edges[0]), _index_tensor(in_edges[1]), _weight_tensor(in_edges[2]), n_rows, aggregation)
        out_agg = aggregate(hidden, _index_tensor(out_edges[0]), _index_tensor(out_edges[1]), _weight_tensor(out_edges[2]), n_rows, aggregation)
        hidden = encoder.dropout(layer(hidden, in_agg, out_agg))
    return hidden


def save_encoder(path: Path, encoder, config: EncoderConfig) -> dict:
    import torch

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"config": config.to_dict(), "state_dict": encoder.state_dict()}, path)
    return {"path": str(path), "bytes": path.stat().st_size}


def load_encoder(path: Path):
    import torch

    payload = torch.load(Path(path), map_location="cpu", weights_only=False)
    config = EncoderConfig(
        dim=int(payload["config"]["dim"]),
        layers=int(payload["config"]["layers"]),
        fanout=tuple(int(value) for value in payload["config"]["fanout"]),
        dropout=float(payload["config"].get("dropout", 0.0)),
    )
    encoder = build_encoder(config)
    encoder.load_state_dict(payload["state_dict"])
    return encoder, config


def build_direction_csr(src: np.ndarray, dst: np.ndarray, weight: np.ndarray, n_nodes: int, direction: str) -> sp.csr_matrix:
    if direction == "in":
        return sp.csr_matrix((weight.astype(np.float64), (dst, src)), shape=(n_nodes, n_nodes))
    if direction == "out":
        return sp.csr_matrix((weight.astype(np.float64), (src, dst)), shape=(n_nodes, n_nodes))
    raise GraphSageError("direção deve ser 'in' ou 'out'")


def csr_edges(csr: sp.csr_matrix) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    incoming = np.diff(csr.indptr)
    destination = np.repeat(np.arange(csr.shape[0], dtype=np.int64), incoming)
    return csr.indices.astype(np.int64), destination, csr.data.astype(np.float64)


def sample_direction(csr: sp.csr_matrix, frontier: np.ndarray, fanout: int, rng: np.random.RandomState) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    sources: list[np.ndarray] = []
    destinations: list[np.ndarray] = []
    weights: list[np.ndarray] = []
    for node in frontier:
        start, end = csr.indptr[node], csr.indptr[node + 1]
        candidates = csr.indices[start:end]
        candidate_weights = csr.data[start:end]
        if len(candidates) == 0:
            continue
        if len(candidates) > fanout:
            picks = np.sort(rng.choice(len(candidates), size=fanout, replace=False))
            candidates = candidates[picks]
            candidate_weights = candidate_weights[picks]
        sources.append(candidates.astype(np.int64))
        destinations.append(np.full(len(candidates), int(node), dtype=np.int64))
        weights.append(candidate_weights.astype(np.float64))
    if not sources:
        empty = np.zeros(0, dtype=np.int64)
        return empty, empty, np.zeros(0, dtype=np.float64)
    return np.concatenate(sources), np.concatenate(destinations), np.concatenate(weights)


def sample_subgraph(targets: np.ndarray, in_csr: sp.csr_matrix, out_csr: sp.csr_matrix, fanout: tuple[int, ...], seed: int) -> dict:
    """Expande vizinhanças por camada e devolve subgrafo induzido (arestas separadas por direção)."""
    rng = np.random.RandomState(int(seed) % (2**32))
    depths = [np.unique(np.asarray(targets, dtype=np.int64))]
    in_lists: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []
    out_lists: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []
    edges_per_layer = []
    frontier_sizes = []
    for depth in range(len(fanout)):
        frontier = depths[depth]
        frontier_sizes.append(int(len(frontier)))
        in_edges = sample_direction(in_csr, frontier, fanout[depth], rng)
        out_edges = sample_direction(out_csr, frontier, fanout[depth], rng)
        in_lists.append(in_edges)
        out_lists.append(out_edges)
        edges_per_layer.append(int(len(in_edges[0]) + len(out_edges[0])))
        neighbors = np.unique(np.concatenate([in_edges[0], out_edges[0]])) if (len(in_edges[0]) or len(out_edges[0])) else np.zeros(0, dtype=np.int64)
        depths.append(neighbors)
    union = np.unique(np.concatenate(depths)) if depths else np.zeros(0, dtype=np.int64)
    local_of = {int(node): index for index, node in enumerate(union)}
    depth_rows = [np.asarray([local_of[int(node)] for node in depth], dtype=np.int64) for depth in depths]

    def localized(edge_lists):
        sources = np.concatenate([edges[0] for edges in edge_lists]) if edge_lists else np.zeros(0, dtype=np.int64)
        destinations = np.concatenate([edges[1] for edges in edge_lists]) if edge_lists else np.zeros(0, dtype=np.int64)
        weights = np.concatenate([edges[2] for edges in edge_lists]) if edge_lists else np.zeros(0, dtype=np.float64)
        if not len(sources):
            return np.zeros(0, dtype=np.int64), np.zeros(0, dtype=np.int64), np.zeros(0, dtype=np.float64)
        local_sources = np.asarray([local_of[int(node)] for node in sources], dtype=np.int64)
        local_destinations = np.asarray([local_of[int(node)] for node in destinations], dtype=np.int64)
        keys = local_sources * len(union) + local_destinations
        _, unique_index = np.unique(keys, return_index=True)
        return local_sources[unique_index], local_destinations[unique_index], weights[unique_index]

    in_edges = localized(in_lists)
    out_edges = localized(out_lists)
    return {
        "nodes": union,
        "depth_rows": depth_rows,
        "in_edges": in_edges,
        "out_edges": out_edges,
        "targets_local": depth_rows[0],
        "sampled_nodes": int(len(union)),
        "edges_per_layer": edges_per_layer,
        "frontier_sizes": frontier_sizes,
        "sampled_edges": int(len(in_edges[0]) + len(out_edges[0])),
    }


def forward_sampled(encoder, features: np.ndarray, subgraph: dict, training: bool = False, aggregation: str = "mean", device: str = "cpu"):
    import torch

    encoder.train(training)
    hidden = torch.as_tensor(np.asarray(features[subgraph["nodes"]]), dtype=torch.float32, device=device)
    n_rows = hidden.shape[0]
    in_source, in_destination, in_weight = subgraph["in_edges"]
    out_source, out_destination, out_weight = subgraph["out_edges"]
    for layer in encoder.layers:
        in_agg = aggregate(hidden, _index_tensor(in_source), _index_tensor(in_destination), _weight_tensor(in_weight), n_rows, aggregation)
        out_agg = aggregate(hidden, _index_tensor(out_source), _index_tensor(out_destination), _weight_tensor(out_weight), n_rows, aggregation)
        hidden = encoder.dropout(layer(hidden, in_agg, out_agg))
    return hidden[subgraph["targets_local"]]


def snapshot_features(snapshot: Path) -> tuple[list[str], np.ndarray]:
    """Espelha H05 raw_features: graus sem self-loop, reciprocidade min(1, ·) vetorizada."""
    nodes = pq.read_table(snapshot / "nodes.parquet")
    edges = pq.read_table(snapshot / "edges.parquet", columns=["source", "target", "weight"])
    ids = sorted(nodes["id"].combine_chunks().to_pylist())
    value_set = pa.array(ids, type=pa.string())
    src = pc.index_in(edges["source"].combine_chunks(), value_set=value_set).to_numpy(zero_copy_only=False).astype(np.int64)
    dst = pc.index_in(edges["target"].combine_chunks(), value_set=value_set).to_numpy(zero_copy_only=False).astype(np.int64)
    weight = np.asarray(edges["weight"].combine_chunks().to_pylist(), dtype=np.float64)
    n_nodes = len(ids)
    self_loop = src == dst
    pair_src, pair_dst, pair_weight = src[~self_loop], dst[~self_loop], weight[~self_loop]
    keys = pair_src * n_nodes + pair_dst
    if len(np.unique(keys)) != len(keys):
        raise GraphSageError("pares (src,dst) duplicados no snapshot")
    order = np.argsort(keys)
    sorted_keys = keys[order]
    reverse_keys = pair_dst * n_nodes + pair_src
    position = np.clip(np.searchsorted(sorted_keys, reverse_keys), 0, max(len(sorted_keys) - 1, 0))
    matched = sorted_keys[position] == reverse_keys if len(sorted_keys) else np.zeros(len(keys), dtype=bool)
    reverse_weight = np.where(matched, pair_weight[order][position], 0.0)
    reciprocity = np.bincount(pair_src, weights=np.minimum(pair_weight, reverse_weight), minlength=n_nodes)
    in_degree = np.bincount(pair_dst, minlength=n_nodes).astype(np.float64)
    out_degree = np.bincount(pair_src, minlength=n_nodes).astype(np.float64)
    weighted_in = np.bincount(pair_dst, weights=pair_weight, minlength=n_nodes)
    weighted_out = np.bincount(pair_src, weights=pair_weight, minlength=n_nodes)
    self_loop_weight = np.bincount(src[self_loop], weights=weight[self_loop], minlength=n_nodes)
    ratio = np.divide(reciprocity, weighted_out, out=np.zeros(n_nodes), where=weighted_out > 0)
    matrix = np.column_stack([in_degree, out_degree, weighted_in, weighted_out, np.minimum(1.0, ratio), self_loop_weight])
    return ids, matrix


def fit_transform_stats(matrix: np.ndarray) -> tuple[dict, np.ndarray]:
    mean = matrix.mean(axis=0)
    std = matrix.std(axis=0)
    std[std < 1e-6] = 1e-6
    transformed = (matrix - mean) / std
    transformed = np.clip(np.nan_to_num(transformed, nan=0.0, posinf=0.0, neginf=0.0), -8.0, 8.0)
    return {"mean": mean.tolist(), "std": std.tolist()}, transformed


def _fixture_graph(seed: int = 0):
    rng = np.random.RandomState(seed)
    n_nodes = 40
    labels = np.zeros(n_nodes, dtype=np.int64)
    labels[n_nodes // 2 :] = 1
    edges = []
    adjacency = np.zeros((n_nodes, n_nodes), dtype=bool)
    for i in range(n_nodes):
        for j in range(i + 1, n_nodes):
            probability = 0.15 if labels[i] == labels[j] else 0.01
            if rng.rand() < probability:
                edges.append((i, j, 1.0 + rng.rand()))
                edges.append((j, i, 1.0 + rng.rand()))
                adjacency[i, j] = True
                adjacency[j, i] = True
    src = np.asarray([edge[0] for edge in edges], dtype=np.int64)
    dst = np.asarray([edge[1] for edge in edges], dtype=np.int64)
    weight = np.asarray([edge[2] for edge in edges], dtype=np.float64)
    features = rng.randn(n_nodes, len(FEATURE_NAMES)).astype(np.float32)
    return src, dst, weight, features, adjacency


def _draw_true_negatives(adjacency: np.ndarray, rng: np.random.RandomState, rows: np.ndarray) -> np.ndarray:
    n_nodes = adjacency.shape[0]
    picked = np.zeros(len(rows), dtype=np.int64)
    for index, row in enumerate(rows.tolist()):
        for _ in range(64):
            candidate = int(rng.randint(0, n_nodes))
            if candidate != row and not adjacency[row, candidate]:
                picked[index] = candidate
                break
        else:
            picked[index] = int((row + 1) % n_nodes)
    return picked


def _train_fixture(seed: int = MASTER_SEED) -> np.ndarray:
    import torch

    import ssl_decoder as sd

    torch.manual_seed(seed % (2**32))
    src, dst, weight, features, adjacency = _fixture_graph(seed=seed)
    n_nodes = features.shape[0]
    rng = np.random.RandomState((seed + 1) % (2**32))
    edge_order = rng.permutation(len(src))
    val_index = edge_order[: max(4, len(src) // 5)]
    train_index = edge_order[max(4, len(src) // 5) :]
    in_csr = build_direction_csr(src, dst, weight, n_nodes, "in")
    out_csr = build_direction_csr(src, dst, weight, n_nodes, "out")
    in_edges, out_edges = csr_edges(in_csr), csr_edges(out_csr)
    config = EncoderConfig(dim=16, layers=2, fanout=(n_nodes, n_nodes), dropout=0.0)
    encoder = build_encoder(config)
    decoder = sd.BilinearDecoder(config.dim)
    optimizer = torch.optim.Adam(list(encoder.parameters()) + list(decoder.parameters()), lr=1e-3)
    losses = []
    for _ in range(1000):
        embeddings = forward_full(encoder, features, in_edges, out_edges, training=True)
        positive_left = embeddings[src[train_index]]
        positive_right = embeddings[dst[train_index]]
        positive_weight = torch.from_numpy(weight[train_index].astype(np.float32))
        negative_target = _draw_true_negatives(adjacency, rng, src[train_index])
        parts = sd.masked_edge_weight_loss(
            decoder,
            positive_left,
            positive_right,
            positive_weight,
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
            embeddings = forward_full(encoder, features, in_edges, out_edges)
            scores = decoder(embeddings[src[edge_index]], embeddings[dst[edge_index]])[0].numpy()
            negatives = _draw_true_negatives(adjacency, rng, src[edge_index])
            negative_scores = decoder(embeddings[src[edge_index]], embeddings[negatives])[0].numpy()
        ranked = np.concatenate([scores, negative_scores])
        labels = np.concatenate([np.ones(len(scores)), np.zeros(len(negative_scores))])
        ranks = stats.rankdata(ranked)
        positives, negatives = int(labels.sum()), int(len(labels) - labels.sum())
        return float((ranks[labels == 1].sum() - positives * (positives + 1) / 2) / (positives * negatives))
    auc_train = pair_auc(train_index)
    auc_validation = pair_auc(val_index)
    with torch.no_grad():
        encoder.eval()
        embeddings = forward_full(encoder, features, in_edges, out_edges)
    gradients_finite = all(bool(torch.isfinite(p.grad).all()) for p in encoder.parameters() if p.grad is not None)
    return {
        "encoder": encoder,
        "decoder": decoder,
        "config": config,
        "features": features,
        "edges": (csr_edges(in_csr), csr_edges(out_csr)),
        "embeddings": embeddings.detach().numpy(),
        "auc_train": auc_train,
        "auc_validation": auc_validation,
        "loss_first": losses[0],
        "loss_last": losses[-1],
        "gradients_finite": gradients_finite,
        "encoder_parameters": encoder_parameter_count(encoder),
        "parameters_formula": parameter_count_formula(config),
        "graph_edges": int(len(src)),
        "validation_edges": int(len(val_index)),
    }


def fixture_smoke(seed: int = MASTER_SEED) -> dict:
    first = _train_fixture(seed)
    second = _train_fixture(seed)
    config = first["config"]
    encoder = first["encoder"]
    in_edges, out_edges = first["edges"]
    buffer = Path("/tmp") / f"m02-fixture-{seed % 100000}.pt"
    save_info = save_encoder(buffer, encoder, config)
    reloaded, reloaded_config = load_encoder(buffer)
    original = forward_full(encoder, first["features"], in_edges, out_edges)
    restored = forward_full(reloaded, first["features"], in_edges, out_edges)
    serialization_diff = float((original - restored).abs().max())
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
        "serialization_max_abs_diff": serialization_diff,
        "serialization_bytes": save_info["bytes"],
        "reloaded_config_matches": reloaded_config == config,
    }


def real_graph_smoke(snapshot: Path = SOURCE_SNAPSHOT, seed: int = MASTER_SEED, batch: int = 64, steps: int = 20) -> dict:
    import torch

    import ssl_decoder as sd
    import ssl_task as st

    torch.manual_seed(seed % (2**32))
    ids, src, dst, weight = st.load_source_edges(snapshot)
    n_nodes = len(ids)
    mask_info = st.build_mask(src, dst, n_nodes, st.seedlib.derive_seed(seed, "m01", "mask"))
    mask = mask_info["mask"]
    train_src, train_dst, train_wgt = st.training_view(src, dst, weight, mask)
    in_csr = build_direction_csr(train_src, train_dst, train_wgt, n_nodes, "in")
    out_csr = build_direction_csr(train_src, train_dst, train_wgt, n_nodes, "out")
    _, raw_features = snapshot_features(snapshot)
    _, features = fit_transform_stats(raw_features)
    config = EncoderConfig(dim=128, layers=3, fanout=(15, 10, 10), dropout=0.1)
    encoder = build_encoder(config)
    decoder = sd.BilinearDecoder(config.dim)
    optimizer = torch.optim.Adam(list(encoder.parameters()) + list(decoder.parameters()), lr=1e-3)
    rng = np.random.RandomState((seed + 7) % (2**32))
    started = time.perf_counter()
    losses = []
    subgraph = None
    for step in range(steps):
        targets = np.sort(rng.choice(n_nodes, size=batch, replace=False))
        subgraph = sample_subgraph(targets, in_csr, out_csr, config.fanout, (seed + step) % (2**32))
        embeddings = forward_sampled(encoder, features, subgraph, training=True)
        adjacency = np.zeros((batch, batch), dtype=bool)
        edge_weight = np.zeros((batch, batch), dtype=np.float64)
        for position, node in enumerate(targets):
            start, finish = in_csr.indptr[node], in_csr.indptr[node + 1]
            neighbors, weights = in_csr.indices[start:finish], in_csr.data[start:finish]
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
            _weight_tensor(edge_weight[upper[0][positive_rows], upper[1][positive_rows]]),
            embeddings[upper[0][negative_rows]],
            embeddings[upper[1][negative_rows]],
        )
        optimizer.zero_grad()
        parts["loss"].backward()
        optimizer.step()
        losses.append(float(parts["loss"].detach()))
    seconds = time.perf_counter() - started
    sparse_bytes = int(in_csr.data.nbytes + in_csr.indices.nbytes + in_csr.indptr.nbytes + out_csr.data.nbytes + out_csr.indices.nbytes + out_csr.indptr.nbytes)
    dense_bytes = int(2 * n_nodes * n_nodes * 8)
    return {
        "device": "cpu",
        "cuda_available": bool(torch.cuda.is_available()),
        "vram_peak_mib": None,
        "steps": steps,
        "batch": batch,
        "fanout": list(config.fanout),
        "encoder_parameters": encoder_parameter_count(encoder),
        "loss_first": round(float(losses[0]), 6),
        "loss_last": round(float(losses[-1]), 6),
        "seconds": round(seconds, 3),
        "sampled_nodes": int(subgraph["sampled_nodes"]),
        "edges_per_layer": subgraph["edges_per_layer"],
        "train_edges": int(len(train_src)),
        "sparse_bytes": sparse_bytes,
        "dense_equivalent_bytes": dense_bytes,
        "sparse_ratio": round(sparse_bytes / dense_bytes, 6),
    }


def cuda_probe(config: EncoderConfig | None = None) -> dict | None:
    import torch

    if not torch.cuda.is_available():
        return None
    config = config or EncoderConfig(dim=576, layers=2, fanout=(10, 10), dropout=0.0)
    encoder = build_encoder(config).cuda()
    optimizer = torch.optim.Adam(encoder.parameters(), lr=1e-3)
    features = torch.randn(512, len(FEATURE_NAMES), device="cuda")
    source = torch.randint(0, 512, (4096,), device="cuda")
    destination = torch.randint(0, 512, (4096,), device="cuda")
    weight = torch.rand(4096, device="cuda") + 0.5
    torch.cuda.reset_peak_memory_stats()
    for _ in range(3):
        hidden = features
        for layer in encoder.layers:
            in_agg = weighted_mean(hidden, source, destination, weight, 512)
            out_agg = weighted_mean(hidden, destination, source, weight, 512)
            hidden = layer(hidden, in_agg, out_agg)
        loss = hidden.square().mean()
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    return {
        "device": torch.cuda.get_device_name(0),
        "parameters": encoder_parameter_count(encoder),
        "peak_vram_mib": round(torch.cuda.max_memory_allocated() / 1024 / 1024, 1),
        "dtype": "float32",
    }


def run(workdir: Path, report_path: Path, seed: int = MASTER_SEED) -> dict:
    started = time.perf_counter()
    workdir = Path(workdir).resolve()
    report_path = Path(report_path).resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    grid = grid_parameter_counts()
    grid_values = [row["parameters"] for row in grid]
    capacity = capacity_table()
    grid_meets = bool(MVP_RANGE[0] <= min(grid_values) and max(grid_values) <= MVP_RANGE[1])
    report = {
        "schema": SCHEMA,
        "status": "exploratory-only; somente fonte; sem nenhum dado do alvo",
        "fanout_convention": FANOUT_CONVENTION,
        "config": {
            "aggregator": AGGREGATOR,
            "activation": ACTIVATION,
            "weight_mode": WEIGHT_MODE,
            "features": list(FEATURE_NAMES),
            "input_dim": len(FEATURE_NAMES),
            "per_node_parameters": 0,
            "max_source_nodes": None,
        },
        "parameter_budget": {
            "mvp_range": list(MVP_RANGE),
            "grid_source": GRID_AMENDMENT,
            "grid_min": int(min(grid_values)),
            "grid_max": int(max(grid_values)),
            "grid_rows": grid,
            "capacity_rows": capacity,
            "smallest_in_range": smallest_dims_for_range(),
            "grid_meets_mvp_range": bool(MVP_RANGE[0] <= min(grid_values) and max(grid_values) <= MVP_RANGE[1]),
            "meets_mvp_range": bool(any(row["meets_mvp_range"] for row in capacity)),
        },
        "fixture_smoke": fixture_smoke(seed=seed),
        "real_graph_smoke": real_graph_smoke(snapshot=SOURCE_SNAPSHOT, seed=seed),
        "cuda_probe": cuda_probe(),
        "blocking_issue": (
            {"present": False}
            if grid_meets
            else {
                "present": True,
                "summary": "o grid vigente do R07 produz no máximo "
                f"{max(grid_values)} parâmetros, abaixo do intervalo de {MVP_RANGE[0]}–{MVP_RANGE[1]} declarado para o MVP",
                "evidence": {"grid_min": int(min(grid_values)), "grid_max": int(max(grid_values)), "smallest_in_range": smallest_dims_for_range()},
                "options": [
                    "emendar o grid do pré-registro (changelog + nova revisão do G5, condição 6)",
                    "aceitar encoder abaixo do intervalo e registrar o desvio",
                    "outra decisão humana documentada",
                ],
                "decision_required_from": "revisor humano do G5 (condição 6)",
            }
        ),
        "resolution": (
            {
                "summary": f"grid emendado produz {min(grid_values)}–{max(grid_values)} parâmetros, dentro de {MVP_RANGE[0]}–{MVP_RANGE[1]}",
                "amendment": GRID_AMENDMENT,
                "decision": "opção (a) da nota de bloqueio da M02 (2026-09-15)",
            }
            if grid_meets
            else None
        ),
        "resources": {"seconds": round(time.perf_counter() - started, 3), "peak_rss_mib": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)},
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
    if int(config.get("per_node_parameters", -1)) != 0:
        failures.append("encoder não pode ter parâmetros por node")
    if config.get("max_source_nodes") is not None:
        failures.append("encoder não pode depender do número fixo de nós da fonte")
    if list(config.get("features", [])) != list(FEATURE_NAMES):
        failures.append("features do encoder divergentes de H05")
    budget = report.get("parameter_budget", {})
    rows = budget.get("grid_rows", [])
    if len(rows) != len(GRID_TRIALS):
        failures.append("tabela do grid incompleta")
    for row in rows:
        expected = parameter_count_formula(EncoderConfig(dim=int(row["dim"]), layers=int(row["layers"]), fanout=pad_fanout(int(row["layers"]), row["fanout"])))
        if int(row.get("parameters", -1)) != expected:
            failures.append(f"contagem de parâmetros divergente no trial {row.get('trial')}")
    if not budget.get("capacity_rows"):
        failures.append("tabela de capacidade ausente")
    if bool(budget.get("grid_meets_mvp_range")) != bool(MVP_RANGE[0] <= int(budget.get("grid_max", 0)) <= MVP_RANGE[1]):
        failures.append("conclusão do orçamento do grid incoerente")
    blocking = report.get("blocking_issue", {})
    if blocking.get("present"):
        if not blocking.get("options") or not blocking.get("decision_required_from"):
            failures.append("bloqueio de orçamento sem opções/decisor")
        if "grid" not in str(blocking.get("summary", "")):
            failures.append("bloqueio sem resumo do grid")
    else:
        resolution = report.get("resolution") or {}
        if "R07" not in str(resolution.get("amendment", "")):
            failures.append("sem bloqueio, a emenda do grid precisa estar registrada na resolução")
        if "2026-" not in str(resolution.get("amendment", "")):
            failures.append("resolução sem data da emenda")
    fixture = report.get("fixture_smoke", {})
    if float(fixture.get("overfit_train_auc", -1)) < 0.95:
        failures.append("overfit controlado de fixture abaixo do esperado")
    if not fixture.get("gradients_finite") or not fixture.get("deterministic_same_seed"):
        failures.append("fixture sem gradientes finitos/determinismo")
    if not fixture.get("reloaded_config_matches"):
        failures.append("serialização sem round-trip de configuração")
    if int(fixture.get("encoder_parameters", -1)) != int(fixture.get("parameters_formula", -2)):
        failures.append("contagem exata difere da fórmula na fixture")
    smoke = report.get("real_graph_smoke", {})
    if int(smoke.get("encoder_parameters", -1)) <= 0:
        failures.append("smoke sem contagem de parâmetros")
    if float(smoke.get("loss_last", 1.0)) > float(smoke.get("loss_first", 0.0)):
        failures.append("smoke não reduziu a loss")
    if int(smoke.get("sparse_bytes", 0)) >= int(smoke.get("dense_equivalent_bytes", 1)):
        failures.append("representação deveria permanecer esparsa")
    if len(smoke.get("fanout", [])) <= 0 or int(smoke.get("sampled_nodes", 0)) <= 0:
        failures.append("smoke sem sampling")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("run", "check"))
    parser.add_argument("--workdir", type=Path, default=ROOT / "runs" / "m02")
    parser.add_argument("--report", type=Path, default=ROOT / "artifacts" / "reports" / "M02-GRAPHSAGE.json")
    args = parser.parse_args()
    try:
        if args.command == "run":
            report = run(args.workdir, args.report)
            print(json.dumps({
                "parameter_budget": {key: report["parameter_budget"][key] for key in ("mvp_range", "grid_min", "grid_max", "meets_mvp_range", "smallest_in_range")},
                "blocking_issue": report["blocking_issue"]["present"],
                "fixture_smoke": report["fixture_smoke"],
                "real_graph_smoke": report["real_graph_smoke"],
                "cuda_probe": report["cuda_probe"],
                "resources": report["resources"],
            }, ensure_ascii=False, sort_keys=True))
        else:
            failures = check_report(args.report)
            if failures:
                for failure in failures:
                    print(f"FALHA: {failure}")
                return 1
            print("OK: encoder M02 validado (parâmetros, fixture, serialização, sampling e esparsidade)")
    except (GraphSageError, FileNotFoundError, json.JSONDecodeError) as error:
        print(f"FALHA: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
