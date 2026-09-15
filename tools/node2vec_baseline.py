#!/usr/bin/env python3
"""Baselines transdutivos Node2Vec/DeepWalk dentro da fonte (B06).

Implementa caminhadas aleatórias de segunda ordem (Grover–Leskovec, LIT-0049)
e de primeira ordem (DeepWalk como caso p=q=1, LIT-0050) sobre o grafo dirigido
e ponderado da fonte, mais Skip-gram com negativos por CPU determinística. A
avaliação usa o mesmo split, as mesmas seeds e o mesmo avaliador de B01/B03,
com probe por centroide sobre os embeddings.

Limite central, já esperado em L06/M-05/M-06: embeddings transdutivos vivem em
espaços arbitrários por grafo; sem um mecanismo de alinhamento não
supervisionado permitido e pré-registrado, não há uso entre grafos. Esta fase
executa somente dentro da fonte e marca o método como não comparável
zero-shot. Nenhum outro conjunto além da fonte entra neste módulo.
"""

import argparse
import json
import random
import resource
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import baselines_source as bs  # noqa: E402
import metrics  # noqa: E402

CONFIGS = {
    "deepwalk": {"p": 1.0, "q": 1.0},
    "node2vec": {"p": 1.0, "q": 0.5},
}
WALKS_PER_NODE = 4
WALK_LENGTH = 25
WINDOW = 5
DIM = 64
EPOCHS = 2
NEGATIVES = 5
BATCH = 16384
LR = 1e-3
UNIGRAM_TABLE = 1_000_000
DEVICE = "cpu"


class TransductiveError(RuntimeError):
    pass


def seed_all(seed: int) -> None:
    seed32 = int(seed) % (2**32)
    random.seed(seed32)
    np.random.seed(seed32)
    torch.manual_seed(seed32)
    torch.use_deterministic_algorithms(True)


def load_directed_graph(snapshot: Path) -> tuple[list[str], np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Grafo dirigido ponderado com ordem canônica de nós (invariante à ordem da tabela).

    Retorna ids, limites por nó, vizinhos, pesos float64, cumulativas por nó e totais.
    """
    nodes = pq.read_table(snapshot / "nodes.parquet")
    edges = pq.read_table(snapshot / "edges.parquet", columns=["source", "target", "weight"])
    ids = sorted(nodes["id"].combine_chunks().to_pylist())
    index = {node: position for position, node in enumerate(ids)}
    src = np.asarray([index[node] for node in edges["source"].combine_chunks().to_pylist()], dtype=np.int64)
    dst = np.asarray([index[node] for node in edges["target"].combine_chunks().to_pylist()], dtype=np.int64)
    wgt = np.asarray(edges["weight"].combine_chunks().to_pylist(), dtype=np.float64)
    if np.any(wgt < 0):
        raise TransductiveError("peso negativo no snapshot")
    order = np.argsort(src, kind="stable")
    src, dst, wgt = src[order], dst[order], wgt[order]
    bounds = np.searchsorted(src, np.arange(len(ids) + 1))
    cum = np.empty_like(wgt)
    total = np.zeros(len(ids))
    for node in range(len(ids)):
        lo, hi = int(bounds[node]), int(bounds[node + 1])
        if hi > lo:
            cum[lo:hi] = np.cumsum(wgt[lo:hi])
            total[node] = cum[hi - 1]
    return ids, bounds, dst.astype(np.int32), wgt, cum, total


def biased_weights(
    cand: np.ndarray,
    wgt: np.ndarray,
    prev: int,
    prev_nbr: np.ndarray,
    p: float,
    q: float,
) -> np.ndarray:
    """Pesos de transição não normalizados de segunda ordem (retorno 1/p, vizinho 1, externo 1/q)."""
    if p == 1.0 and q == 1.0:
        return np.asanyarray(wgt, dtype=np.float64)
    alpha = np.full(len(cand), 1.0 / q)
    alpha[cand == prev] = 1.0 / p
    if len(prev_nbr):
        alpha[np.isin(cand, prev_nbr) & (cand != prev)] = 1.0
    return np.asanyarray(wgt, dtype=np.float64) * alpha


def random_walks(
    bounds: np.ndarray,
    nbr: np.ndarray,
    wgt: np.ndarray,
    cum: np.ndarray,
    total: np.ndarray,
    n_nodes: int,
    walks_per_node: int,
    walk_length: int,
    p: float,
    q: float,
    rng: np.random.RandomState,
) -> list[np.ndarray]:
    walks: list[np.ndarray] = []
    first_order = p == 1.0 and q == 1.0
    for start in range(n_nodes):
        for _ in range(walks_per_node):
            walk = [start]
            while len(walk) < walk_length:
                cur = walk[-1]
                lo, hi = int(bounds[cur]), int(bounds[cur + 1])
                if hi <= lo or total[cur] <= 0:
                    break
                cand = nbr[lo:hi]
                if first_order:
                    nxt = cand[int(np.searchsorted(cum[lo:hi], rng.random() * total[cur]))]
                else:
                    if len(walk) >= 2:
                        prev = walk[-2]
                        plo, phi = int(bounds[prev]), int(bounds[prev + 1])
                        weights = biased_weights(cand, wgt[lo:hi], prev, nbr[plo:phi], p, q)
                    else:
                        weights = wgt[lo:hi]
                    mass = weights.sum()
                    if mass <= 0:
                        break
                    nxt = cand[int(np.searchsorted(np.cumsum(weights), rng.random() * mass))]
                walk.append(int(nxt))
            walks.append(np.asarray(walk, dtype=np.int32))
    if not walks:
        raise TransductiveError("nenhuma caminhada gerada")
    return walks


def build_pairs(walks: list[np.ndarray], window: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    centers: list[np.ndarray] = []
    contexts: list[np.ndarray] = []
    tokens: list[np.ndarray] = []
    for walk in walks:
        tokens.append(walk)
        last = len(walk)
        for k in range(1, window + 1):
            if k >= last:
                break
            centers.append(walk[:-k])
            contexts.append(walk[k:])
            centers.append(walk[k:])
            contexts.append(walk[:-k])
    return (
        np.concatenate(centers).astype(np.int32),
        np.concatenate(contexts).astype(np.int32),
        np.concatenate(tokens).astype(np.int32),
    )


def unigram_table(tokens: np.ndarray, n_nodes: int, size: int, seed: int) -> np.ndarray:
    freq = np.bincount(tokens, minlength=n_nodes).astype(np.float64) ** 0.75
    if freq.sum() <= 0:
        raise TransductiveError("frequência de tokens vazia")
    prob = freq / freq.sum()
    rng = np.random.RandomState(seed)
    return rng.choice(n_nodes, size=size, p=prob).astype(np.int32)


def train_skipgram(
    centers: np.ndarray,
    contexts: np.ndarray,
    tokens: np.ndarray,
    n_nodes: int,
    dim: int,
    seed: int,
    epochs: int,
    batch: int,
    negatives: int,
    lr: float,
) -> np.ndarray:
    if len(centers) == 0:
        raise TransductiveError("pares vazios")
    seed_all(seed)
    previous_threads = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        table = unigram_table(tokens, n_nodes, UNIGRAM_TABLE, (int(seed) + 1) % (2**32))
        target = torch.nn.Embedding(n_nodes, dim, sparse=True)
        context = torch.nn.Embedding(n_nodes, dim, sparse=True)
        torch.nn.init.xavier_uniform_(target.weight)
        torch.nn.init.zeros_(context.weight)
        model = torch.nn.Sequential()
        optimizer = torch.optim.SparseAdam(list(target.parameters()) + list(context.parameters()), lr=lr)
        loss_fn = torch.nn.BCEWithLogitsLoss()
        center_t = torch.from_numpy(centers.astype(np.int64))
        context_t = torch.from_numpy(contexts.astype(np.int64))
        table_t = torch.from_numpy(table.astype(np.int64))
        count = len(centers)
        ones = torch.ones((), dtype=torch.float32)
        zeros = torch.zeros((), dtype=torch.float32)
        rng = np.random.RandomState((int(seed) + 2) % (2**32))
        for _ in range(epochs):
            order = rng.permutation(count)
            neg_draws = rng.randint(0, UNIGRAM_TABLE, size=(count, negatives)).astype(np.int32)
            for start in range(0, count, batch):
                idx = order[start : start + batch]
                batch_c = center_t[idx]
                batch_x = context_t[idx]
                neg = table_t[torch.from_numpy(neg_draws[idx].astype(np.int64))]
                pos_score = (target(batch_c) * context(batch_x)).sum(dim=1)
                neg_score = (target(batch_c).unsqueeze(1) * context(neg)).sum(dim=2)
                loss = loss_fn(pos_score, ones.expand_as(pos_score)) + loss_fn(neg_score, zeros.expand_as(neg_score))
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            del neg_draws
        return target.weight.detach().cpu().numpy().astype(np.float32)
    finally:
        torch.set_num_threads(previous_threads)


def probe_embeddings(
    embeddings: np.ndarray,
    order: dict[str, int],
    train: dict[str, str],
    val: dict[str, str],
    classes: list[str],
) -> dict[str, str]:
    train_matrix = np.asarray([embeddings[order[node]] for node in train])
    val_matrix = np.asarray([embeddings[order[node]] for node in val])
    stats = bs.fit_stats(train_matrix)
    train_scaled = bs.transform(train_matrix, stats)
    val_scaled = bs.transform(val_matrix, stats)
    centroids = {}
    for name in classes:
        rows = [train_scaled[index] for index, node in enumerate(train) if train[node] == name]
        if rows:
            centroids[name] = np.mean(rows, axis=0)
    predictions = {}
    for index, node in enumerate(val):
        distances = {name: float(np.linalg.norm(val_scaled[index] - centroid)) for name, centroid in centroids.items()}
        predictions[node] = min(distances, key=lambda name: (distances[name], name))
    return predictions


def random_orthogonal(dim: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(int(seed) % (2**32))
    mat, upper = np.linalg.qr(rng.randn(dim, dim))
    mat = mat * np.sign(np.diag(upper))
    return mat.astype(np.float64)


def mean_cosine(first: np.ndarray, second: np.ndarray) -> float:
    denom = np.linalg.norm(first, axis=1) * np.linalg.norm(second, axis=1)
    denom[denom < 1e-12] = 1e-12
    return float(((first * second).sum(axis=1) / denom).mean())


def run(
    snapshot: Path,
    properties: Path,
    out_dir: Path,
    report_path: Path,
    configs: tuple[str, ...] = ("deepwalk", "node2vec"),
    seeds: tuple[int, ...] = bs.SELECTION_SEEDS,
    walks_per_node: int = WALKS_PER_NODE,
    walk_length: int = WALK_LENGTH,
    window: int = WINDOW,
    dim: int = DIM,
    epochs: int = EPOCHS,
    negatives: int = NEGATIVES,
    batch: int = BATCH,
    lr: float = LR,
) -> dict:
    started = time.perf_counter()
    for name in configs:
        if name not in CONFIGS:
            raise TransductiveError(f"configuração desconhecida: {name}")
    ids, bounds, nbr, wgt, cum, total = load_directed_graph(snapshot)
    order = {node: position for position, node in enumerate(ids)}
    labels, label_meta = bs.load_source_labels(properties)
    labels = {node: name for node, name in labels.items() if node in order}
    counts = Counter(labels.values())
    labels = {node: name for node, name in labels.items() if counts[name] >= bs.K_MIN}
    if not labels:
        raise TransductiveError("nenhum rótulo utilizável após mapear para o snapshot")
    train, val = bs.split_deterministic(labels)
    train_nodes, val_nodes = list(train), list(val)
    classes = sorted(set(train.values()))
    out_dir.mkdir(parents=True, exist_ok=True)
    results: dict = {}
    predictions_refs = []
    embeddings_refs = []
    for name in configs:
        params = CONFIGS[name]
        per_seed = []
        seed_embeddings: dict[int, np.ndarray] = {}
        for seed_index, seed in enumerate(seeds):
            rng = np.random.RandomState(int(seed) % (2**32))
            mark = time.perf_counter()
            walks = random_walks(bounds, nbr, wgt, cum, total, len(ids), walks_per_node, walk_length, params["p"], params["q"], rng)
            walk_seconds = time.perf_counter() - mark
            mark = time.perf_counter()
            centers, contexts, tokens = build_pairs(walks, window)
            pair_seconds = time.perf_counter() - mark
            mark = time.perf_counter()
            embeddings = train_skipgram(centers, contexts, tokens, len(ids), dim, int(seed), epochs, batch, negatives, lr)
            train_seconds = time.perf_counter() - mark
            seed_embeddings[seed_index] = embeddings
            predictions = probe_embeddings(embeddings, order, train, val, classes)
            evaluation = bs.evaluate_predictions(val, predictions)
            pred_path = out_dir / f"predictions-{name}-seed{seed_index}.json"
            pred_path.write_text(json.dumps(predictions, sort_keys=True) + "\n", encoding="utf-8")
            emb_path = out_dir / f"embeddings-{name}-seed{seed_index}.npy"
            np.save(emb_path, embeddings)
            predictions_refs.append(
                {"config": name, "seed_index": seed_index, "path": pred_path.as_posix(), "sha256": bs.sha256_file(pred_path)}
            )
            embeddings_refs.append(
                {"config": name, "seed_index": seed_index, "path": emb_path.as_posix(), "sha256": bs.sha256_file(emb_path)}
            )
            per_seed.append(
                {
                    "seed_index": seed_index,
                    "macro_recall@1": evaluation["recall"]["@1"]["macro"],
                    "micro_recall@1": evaluation["recall"]["@1"]["micro"],
                    "walk_tokens": int(sum(len(w) for w in walks)),
                    "pairs": int(len(centers)),
                    "walk_seconds": round(walk_seconds, 1),
                    "pair_seconds": round(pair_seconds, 1),
                    "train_seconds": round(train_seconds, 1),
                }
            )
            del walks, centers, contexts, tokens
        macros = sorted(item["macro_recall@1"] for item in per_seed)
        rotation = random_orthogonal(dim, 20260914)
        base_predictions = probe_embeddings(seed_embeddings[0], order, train, val, classes)
        rotated_predictions = probe_embeddings(seed_embeddings[0] @ rotation, order, train, val, classes)
        agreement = sum(1 for node in val_nodes if base_predictions[node] == rotated_predictions[node]) / len(val_nodes)
        seed_keys = sorted(seed_embeddings)
        cosine_pairs = {}
        for pos, first_key in enumerate(seed_keys):
            for second_key in seed_keys[pos + 1 :]:
                cosine_pairs[f"{first_key}x{second_key}"] = mean_cosine(seed_embeddings[first_key], seed_embeddings[second_key])
        results[name] = {
            "p": params["p"],
            "q": params["q"],
            "per_seed": per_seed,
            "median_macro_recall@1": macros[len(macros) // 2],
            "rotation_agreement": agreement,
            "seed_cosine": cosine_pairs,
        }
        del seed_embeddings
    report = {
        "schema": "b06-node2vec",
        "verdict": "não comparável zero-shot",
        "configs": {name: dict(CONFIGS[name]) for name in configs},
        "seeds": list(seeds),
        "hyperparameters": {
            "walks_per_node": walks_per_node,
            "walk_length": walk_length,
            "window": window,
            "dim": dim,
            "epochs": epochs,
            "negatives": negatives,
            "batch": batch,
            "lr": lr,
            "device": DEVICE,
        },
        "label_meta": label_meta,
        "nodes_used": len(labels),
        "nodes_total": len(ids),
        "split": {"train": len(train), "val": len(val), "classes": len(classes)},
        "results": results,
        "predictions": predictions_refs,
        "embeddings": embeddings_refs,
        "torch_version": torch.__version__,
        "seconds": round(time.perf_counter() - started, 3),
        "peak_rss_mib": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--properties", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--configs", nargs="+", default=["deepwalk", "node2vec"], choices=sorted(CONFIGS))
    parser.add_argument("--seed-idx", default="0,1,2")
    parser.add_argument("--walks", type=int, default=WALKS_PER_NODE)
    parser.add_argument("--length", type=int, default=WALK_LENGTH)
    parser.add_argument("--window", type=int, default=WINDOW)
    parser.add_argument("--dim", type=int, default=DIM)
    parser.add_argument("--epochs", type=int, default=EPOCHS)
    parser.add_argument("--negatives", type=int, default=NEGATIVES)
    parser.add_argument("--batch", type=int, default=BATCH)
    parser.add_argument("--lr", type=float, default=LR)
    args = parser.parse_args()
    try:
        idx = [int(part) for part in args.seed_idx.split(",")]
        seeds = tuple(bs.SELECTION_SEEDS[i] for i in idx)
    except (ValueError, IndexError) as error:
        print(f"FALHA: seed-idx inválido: {error}", file=sys.stderr)
        return 1
    try:
        report = run(
            args.snapshot, args.properties, args.out_dir, args.report, tuple(args.configs), seeds,
            args.walks, args.length, args.window, args.dim, args.epochs, args.negatives, args.batch, args.lr,
        )
    except (TransductiveError, FileNotFoundError) as error:
        print(f"FALHA: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"results": report["results"], "seconds": report["seconds"], "peak_rss_mib": report["peak_rss_mib"]}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
