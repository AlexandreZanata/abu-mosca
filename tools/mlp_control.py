#!/usr/bin/env python3
"""MLP de controle sobre as mesmas features artesanais (B05).

Treina MLPs somente na fonte, sobre as 11 features de B04, com o split
determinístico e as seeds iguais aos de B03, normalização z-score ajustada
só no treino e o mesmo avaliador de B01. O objetivo é separar o ganho da
não linearidade do ganho de um futuro encoder. Nenhum outro conjunto além
da fonte entra neste módulo.
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
import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import artisanal_features as af  # noqa: E402
import baselines_source as bs  # noqa: E402
import metrics  # noqa: E402

CONFIGS = {
    "s": {"hidden": (256, 128), "budget": "~100k"},
    "m": {"hidden": (512, 512), "budget": "~500k"},
    "l": {"hidden": (1024, 768), "budget": "pareado-provisorio-1-3M"},
}
EPOCHS_DEFAULT = 50
BATCH_DEFAULT = 1024
LR_DEFAULT = 1e-3
DEVICE = "cpu"


class MlpError(RuntimeError):
    pass


def seed_all(seed: int) -> None:
    seed32 = int(seed) % (2**32)
    random.seed(seed32)
    np.random.seed(seed32)
    torch.manual_seed(seed32)
    torch.use_deterministic_algorithms(True)


class MLP(torch.nn.Module):
    def __init__(self, in_dim: int, hidden: tuple[int, ...], n_classes: int) -> None:
        super().__init__()
        layers: list[torch.nn.Module] = []
        previous = in_dim
        for width in hidden:
            layers.append(torch.nn.Linear(previous, width))
            layers.append(torch.nn.ReLU())
            previous = width
        layers.append(torch.nn.Linear(previous, n_classes))
        self.net = torch.nn.Sequential(*layers)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.net(inputs)


def count_params(model: torch.nn.Module) -> int:
    return int(sum(p.numel() for p in model.parameters()))


def expected_params(in_dim: int, hidden: tuple[int, ...], n_classes: int) -> int:
    total = 0
    previous = in_dim
    for width in hidden:
        total += previous * width + width
        previous = width
    total += previous * n_classes + n_classes
    return total


def fit_stats(matrix: np.ndarray) -> dict:
    mean = matrix.mean(axis=0)
    std = matrix.std(axis=0)
    std[std < 1e-6] = 1e-6
    return {"mean": mean.tolist(), "std": std.tolist()}


def apply_stats(matrix: np.ndarray, stats: dict) -> np.ndarray:
    return (matrix - np.asarray(stats["mean"])) / np.asarray(stats["std"])


def train_mlp(
    train_x: np.ndarray,
    train_y: np.ndarray,
    n_classes: int,
    hidden: tuple[int, ...],
    seed: int,
    epochs: int = EPOCHS_DEFAULT,
    batch: int = BATCH_DEFAULT,
    lr: float = LR_DEFAULT,
) -> tuple[MLP, int]:
    if train_x.shape[0] == 0:
        raise MlpError("treino vazio")
    seed_all(seed)
    previous_threads = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        model = MLP(train_x.shape[1], hidden, n_classes).to(DEVICE)
        model.train()
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        loss_fn = torch.nn.CrossEntropyLoss()
        features = torch.from_numpy(train_x.astype(np.float32))
        labels = torch.from_numpy(train_y.astype(np.int64))
        count = train_x.shape[0]
        rng = np.random.RandomState(int(seed) % (2**32))
        for _ in range(epochs):
            order = rng.permutation(count)
            for start in range(0, count, batch):
                idx = order[start : start + batch]
                optimizer.zero_grad()
                logits = model(features[idx])
                loss = loss_fn(logits, labels[idx])
                loss.backward()
                optimizer.step()
        return model, count_params(model)
    finally:
        torch.set_num_threads(previous_threads)


def predict_mlp(model: MLP, matrix: np.ndarray, batch: int = BATCH_DEFAULT) -> list[int]:
    model.eval()
    outputs: list[int] = []
    with torch.no_grad():
        tensor = torch.from_numpy(matrix.astype(np.float32))
        for start in range(0, len(tensor), batch):
            logits = model(tensor[start : start + batch])
            outputs.extend(int(v) for v in logits.argmax(dim=1).tolist())
    return outputs


def run(
    snapshot: Path,
    properties: Path,
    out_dir: Path,
    report_path: Path,
    configs: tuple[str, ...] = ("s", "m", "l"),
    seeds: tuple[int, ...] = bs.SELECTION_SEEDS,
    epochs: int = EPOCHS_DEFAULT,
    batch: int = BATCH_DEFAULT,
    lr: float = LR_DEFAULT,
) -> dict:
    started = time.perf_counter()
    for name in configs:
        if name not in CONFIGS:
            raise MlpError(f"configuração desconhecida: {name}")
    ids, features = af.extract_features(snapshot)
    labels, label_meta = bs.load_source_labels(properties)
    order = {node: index for index, node in enumerate(ids)}
    labels = {node: name for node, name in labels.items() if node in order}
    counts = Counter(labels.values())
    labels = {node: name for node, name in labels.items() if counts[name] >= bs.K_MIN}
    if not labels:
        raise MlpError("nenhum rótulo utilizável após mapear para o snapshot")
    train, val = bs.split_deterministic(labels)
    train_nodes, val_nodes = list(train), list(val)
    classes = sorted(set(train.values()))
    class_index = {name: position for position, name in enumerate(classes)}
    full = np.column_stack([features[name] for name in af.FEATURE_ORDER])
    train_matrix = full[[order[node] for node in train_nodes]]
    val_matrix = full[[order[node] for node in val_nodes]]
    stats = fit_stats(train_matrix)
    train_scaled = apply_stats(train_matrix, stats)
    val_scaled = apply_stats(val_matrix, stats)
    train_y = np.asarray([class_index[train[node]] for node in train_nodes], dtype=np.int64)
    out_dir.mkdir(parents=True, exist_ok=True)
    results: dict = {}
    predictions_refs = []
    for name in configs:
        hidden = tuple(CONFIGS[name]["hidden"])
        in_dim = len(af.FEATURE_ORDER)
        per_seed = []
        for seed_index, seed in enumerate(seeds):
            model, n_params = train_mlp(train_scaled, train_y, len(classes), hidden, int(seed), epochs, batch, lr)
            assert n_params == expected_params(in_dim, hidden, len(classes))
            pred_idx = predict_mlp(model, val_scaled, batch)
            pred_names = {node: classes[pred_idx[i]] for i, node in enumerate(val_nodes)}
            ranked = {node: [pred_names[node]] for node in val_nodes}
            evaluation = metrics.evaluate(ranked, val, k_values=(1, 5))
            path = out_dir / f"predictions-mlp-{name}-seed{seed_index}.json"
            path.write_text(json.dumps(pred_names, sort_keys=True) + "\n", encoding="utf-8")
            predictions_refs.append(
                {"config": name, "seed_index": seed_index, "path": path.as_posix(), "sha256": bs.sha256_file(path)}
            )
            per_seed.append(
                {
                    "seed_index": seed_index,
                    "macro_recall@1": evaluation["recall"]["@1"]["macro"],
                    "micro_recall@1": evaluation["recall"]["@1"]["micro"],
                }
            )
        macros = sorted(item["macro_recall@1"] for item in per_seed)
        results[name] = {
            "hidden": list(hidden),
            "budget": CONFIGS[name]["budget"],
            "n_params": expected_params(in_dim, hidden, len(classes)),
            "per_seed": per_seed,
            "median_macro_recall@1": macros[len(macros) // 2],
        }
    report = {
        "schema": "b05-mlp-control",
        "features": list(af.FEATURE_ORDER),
        "feature_version": af.FEATURE_VERSION,
        "configs": {name: {"hidden": list(CONFIGS[name]["hidden"]), "budget": CONFIGS[name]["budget"]} for name in configs},
        "seeds": list(seeds),
        "hyperparameters": {"epochs": epochs, "batch": batch, "lr": lr, "device": DEVICE},
        "label_meta": label_meta,
        "nodes_used": len(labels),
        "split": {"train": len(train), "val": len(val), "classes": len(classes)},
        "stats_source_fit": stats,
        "results": results,
        "predictions": predictions_refs,
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
    parser.add_argument("--configs", nargs="+", default=["s", "m", "l"], choices=sorted(CONFIGS))
    parser.add_argument("--epochs", type=int, default=EPOCHS_DEFAULT)
    parser.add_argument("--batch", type=int, default=BATCH_DEFAULT)
    parser.add_argument("--lr", type=float, default=LR_DEFAULT)
    args = parser.parse_args()
    try:
        report = run(args.snapshot, args.properties, args.out_dir, args.report, tuple(args.configs), bs.SELECTION_SEEDS, args.epochs, args.batch, args.lr)
    except (MlpError, FileNotFoundError) as error:
        print(f"FALHA: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"results": report["results"], "seconds": report["seconds"], "peak_rss_mib": report["peak_rss_mib"]}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
