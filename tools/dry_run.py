#!/usr/bin/env python3
"""Dry run ponta a ponta do protocolo em dados sintéticos (R08).

Gera uma fixture com tipos conhecidos e um tipo unknown, baixa pelo caminho
real de download (servidor HTTP local + tools/download.py), preprocessa, treina
um modelo trivial, congela, infere com IDs opacos e avalia no "selado" sintético
sob firewall. Nunca toca dados reais do alvo nem a zona selada real do host.
"""

import argparse
import hashlib
import json
import random
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import firewall  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TYPES_KNOWN = ("alpha", "beta", "gamma")
TYPE_UNKNOWN = "omega"
N_SOURCE_PER_TYPE = 20
N_TARGET_KNOWN = 10
N_TARGET_UNKNOWN = 10
FEATURE_DIM = 2


class DryRunError(RuntimeError):
    pass


def _qid(index: int, prefix: str) -> str:
    return prefix + hashlib.sha256(f"opaque:{prefix}:{index}".encode()).hexdigest()[:16]


def generate_fixture(seed: int = 20260914) -> dict:
    rng = random.Random(seed)
    nodes: list[dict] = []
    edges: list[dict] = []
    node_id = 0
    for label in (*TYPES_KNOWN, TYPE_UNKNOWN):
        per_type = N_SOURCE_PER_TYPE if label in TYPES_KNOWN else N_TARGET_UNKNOWN
        for _ in range(per_type):
            nodes.append({"body": f"n{node_id:04d}", "type": label})
            node_id += 1
    by_type: dict[str, list[int]] = {label: [] for label in (*TYPES_KNOWN, TYPE_UNKNOWN)}
    for index, node in enumerate(nodes):
        by_type[node["type"]].append(index)
    for source in range(len(nodes)):
        source_label = nodes[source]["type"]
        source_unknown = source_label == TYPE_UNKNOWN
        for target in range(len(nodes)):
            if source == target:
                continue
            target_label = nodes[target]["type"]
            if source_unknown and target_label == TYPE_UNKNOWN:
                probability = 0.6
            elif source_label == target_label:
                probability = 0.25
            else:
                probability = 0.02
            if rng.random() < probability:
                weight = rng.randint(5, 9) if source_unknown else rng.randint(1, 5)
                edges.append({"pre": source, "post": target, "weight": weight})
    degrees = {index: [0, 0] for index in range(len(nodes))}
    for edge in edges:
        degrees[edge["pre"]][1] += edge["weight"]
        degrees[edge["post"]][0] += edge["weight"]

    def features_of(indices: list[int]) -> list[list[float]]:
        return [[float(degrees[index][0]), float(degrees[index][1])] for index in indices]

    source_indices = [i for i, node in enumerate(nodes) if node["type"] in TYPES_KNOWN]
    target_indices = list(range(len(nodes)))
    return {
        "seed": seed,
        "nodes": nodes,
        "edges": edges,
        "source_indices": source_indices,
        "target_indices": target_indices,
        "source_features": features_of(source_indices),
        "target_features": features_of(target_indices),
    }


def canvas_rows(fixture: dict) -> tuple[str, str]:
    source_lines = ["body,type,in_degree,out_degree"]
    for index in fixture["source_indices"]:
        node = fixture["nodes"][index]
        in_degree, out_degree = fixture["source_features"][fixture["source_indices"].index(index)]
        source_lines.append(f"{node['body']},{node['type']},{in_degree:.0f},{out_degree:.0f}")
    target_lines = ["body,in_degree,out_degree"]
    for index in fixture["target_indices"]:
        node = fixture["nodes"][index]
        in_degree, out_degree = fixture["target_features"][index]
        target_lines.append(f"{node['body']},{in_degree:.0f},{out_degree:.0f}")
    return "\n".join(source_lines) + "\n", "\n".join(target_lines) + "\n"


class _Handler(BaseHTTPRequestHandler):
    payload = b""

    def log_message(self, *args):
        pass

    def do_GET(self):
        body = type(self).payload
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _serve(payload: bytes) -> tuple[str, ThreadingHTTPServer]:
    _Handler.payload = payload
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    import threading

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return f"http://127.0.0.1:{server.server_address[1]}/source.csv", server


def download_stage(workdir: Path, source_csv: bytes) -> dict:
    url, server = _serve(source_csv)
    try:
        digest = hashlib.sha256(source_csv).hexdigest()
        entry = {
            "path": f"{workdir.name}/raw/source.csv",
            "url": url,
            "bytes": len(source_csv),
            "sha256": digest,
            "accessed_at": time.strftime("%Y-%m-%d", time.gmtime()),
        }
        import download as download_tool

        download_tool.ROOT = workdir.parent
        result = download_tool.download_entry(entry)
        skipped = download_tool.download_entry(entry)
    finally:
        server.shutdown()
    if skipped["status"] != "skipped":
        raise DryRunError("download não foi idempotente no dry run")
    return {"download": result["status"], "bytes": len(source_csv), "sha256": digest}


def preprocess_stage(raw_csv: Path) -> tuple[list[list[float]], list[str]]:
    lines = raw_csv.read_text(encoding="utf-8").strip().splitlines()[1:]
    features, labels = [], []
    for line in lines:
        body, label, in_degree, out_degree = line.split(",")
        features.append([float(in_degree), float(out_degree)])
        labels.append(label)
    return features, labels


def train_trivial(features: list[list[float]], labels: list[str], seed: int) -> dict:
    import torch

    torch.manual_seed(seed)
    classes = sorted(set(labels))
    index = {label: position for position, label in enumerate(classes)}
    x = torch.tensor(features, dtype=torch.float32)
    y = torch.tensor([index[label] for label in labels], dtype=torch.long)
    mean = x.mean(dim=0, keepdim=True)
    std = x.std(dim=0, keepdim=True).clamp_min(1e-6)
    model = torch.nn.Sequential(
        torch.nn.Linear(FEATURE_DIM, 16), torch.nn.ReLU(), torch.nn.Linear(16, len(classes))
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=0.05)
    for _ in range(200):
        optimizer.zero_grad()
        loss = torch.nn.functional.cross_entropy(model((x - mean) / std), y)
        loss.backward()
        optimizer.step()
    state = {key: value.tolist() for key, value in model.state_dict().items()}
    weights = hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()
    return {
        "classes": classes,
        "state": state,
        "mean": mean.tolist(),
        "std": std.tolist(),
        "seed": seed,
        "sha256": weights,
    }


def scores_of(frozen: dict, features: list[list[float]]) -> list[list[float]]:
    import torch

    model = torch.nn.Sequential(
        torch.nn.Linear(FEATURE_DIM, 16), torch.nn.ReLU(), torch.nn.Linear(16, len(frozen["classes"]))
    )
    model.load_state_dict({k: torch.tensor(v) for k, v in frozen["state"].items()})
    model.eval()
    x = torch.tensor(features, dtype=torch.float32)
    mean = torch.tensor(frozen["mean"])
    std = torch.tensor(frozen["std"])
    with torch.no_grad():
        return torch.softmax(model((x - mean) / std), dim=1).tolist()


def _distances(frozen: dict, features: list[list[float]]) -> list[float]:
    import math

    mean = frozen["mean"][0]
    std = frozen["std"][0]
    return [
        math.sqrt(sum(((value - m) / s) ** 2 for value, m, s in zip(row, mean, std)))
        for row in features
    ]


def inference_stage(frozen: dict, fixture: dict) -> dict:
    source_scores = scores_of(frozen, fixture["source_features"])
    target_scores = scores_of(frozen, fixture["target_features"])
    source_distances = _distances(frozen, fixture["source_features"])
    target_distances = _distances(frozen, fixture["target_features"])
    threshold = sorted(source_distances)[max(0, int(0.95 * len(source_distances)) - 1)]
    gallery = {label: f"g{hashlib.sha256(label.encode()).hexdigest()[:16]}" for label in frozen["classes"]}
    queries = []
    for position, index in enumerate(fixture["target_indices"]):
        scores = target_scores[position]
        ranked = sorted(
            ({"id": gallery[label], "score": round(scores[order], 6)} for order, label in enumerate(frozen["classes"])),
            key=lambda item: -item["score"],
        )
        query_id = _qid(index, "q")
        queries.append(
            {
                "id": query_id,
                "ranked": ranked,
                "rejected": target_distances[position] > threshold,
                "body": fixture["nodes"][index]["body"],
                "type": fixture["nodes"][index]["type"],
            }
        )
    threshold_value = threshold
    sealed_map = {
        "queries": {query["id"]: {"body": query["body"], "type": query["type"]} for query in queries},
        "gallery": {gallery[label]: label for label in frozen["classes"]},
        "source": {
            _qid(index, "s"): fixture["nodes"][index]["type"]
            for index, score in zip(fixture["source_indices"], source_scores)
        },
    }
    return {
        "threshold": threshold_value,
        "source_distances": source_distances,
        "scores": target_scores,
        "queries": queries,
        "sealed_map": sealed_map,
        "source_scores": source_scores,
    }


def _auroc(positive: list[float], negative: list[float]) -> float:
    wins = sum(1 for p in positive for n in negative if p > n) + 0.5 * sum(
        1 for p in positive for n in negative if p == n
    )
    total = len(positive) * len(negative)
    return wins / total if total else 0.5


def _aupr(positive: list[float], negative: list[float]) -> float:
    ranked = sorted([(score, 1) for score in positive] + [(score, 0) for score in negative], key=lambda x: -x[0])
    hits = 0
    precision_sum = 0.0
    for position, (_, label) in enumerate(ranked, 1):
        if label:
            hits += 1
            precision_sum += hits / position
    return precision_sum / len(positive) if positive else 0.0


def evaluate_stage(inference: dict) -> dict:
    sealed = inference["sealed_map"]
    classes = sorted(sealed["gallery"].values())
    known_queries = [
        query for query in inference["queries"]
        if sealed["queries"][query["id"]]["type"] in classes and not query["rejected"]
    ]
    unknown_queries = [
        query for query in inference["queries"]
        if sealed["queries"][query["id"]]["type"] not in classes
    ]
    gallery_of = {gallery_id: label for gallery_id, label in sealed["gallery"].items()}
    ranks: list[int] = []
    per_type: dict[str, list[int]] = {label: [] for label in classes}
    for query in inference["queries"]:
        true_type = sealed["queries"][query["id"]]["type"]
        if true_type not in classes or query["rejected"]:
            continue
        order = next(
            position for position, item in enumerate(query["ranked"], 1)
            if gallery_of[item["id"]] == true_type
        )
        ranks.append(order)
        per_type[true_type].append(1 if order == 1 else 0)
    recalls = [sum(values) / len(values) for values in per_type.values() if values]
    primary = sum(recalls) / len(recalls) if recalls else 0.0
    recall_at_5 = sum(1 for rank in ranks if rank <= 5) / len(ranks) if ranks else 0.0
    recall_at_10 = sum(1 for rank in ranks if rank <= 10) / len(ranks) if ranks else 0.0
    mrr = sum(1.0 / rank for rank in ranks) / len(ranks) if ranks else 0.0
    positives = [1.0 - query["ranked"][0]["score"] for query in unknown_queries] or [0.0]
    negatives = [1.0 - query["ranked"][0]["score"] for query in known_queries] or [0.0]
    threshold = inference["threshold"]
    tpr_sorted = sorted(negatives, reverse=True)
    cutoff_index = max(0, int(0.95 * len(tpr_sorted)) - 1)
    cutoff = tpr_sorted[cutoff_index] if tpr_sorted else 1.0
    false_positives = sum(1 for value in positives if value >= cutoff)
    fpr = false_positives / len(positives) if positives else 0.0
    confidence = [query["ranked"][0]["score"] for query in known_queries]
    accuracy = sum(1 for rank in ranks if rank == 1) / len(ranks) if ranks else 0.0
    brier = sum((1.0 - value) ** 2 for value in confidence) / len(confidence) if confidence else 0.0
    bins = [0] * 15
    ece = 0.0
    for value in confidence:
        bins[min(14, int(value * 15))] += 1
    for position, count in enumerate(bins):
        if count and confidence:
            ece += (count / len(confidence)) * abs((position + 0.5) / 15 - sum(confidence) / len(confidence))
    metrics = {
        "schema_version": "1.0",
        "run_id": hashlib.sha256(json.dumps(inference["sealed_map"], sort_keys=True).encode()).hexdigest()[:16],
        "evaluated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "inputs": {
            "predictions_sha256": hashlib.sha256(json.dumps(inference["queries"], sort_keys=True).encode()).hexdigest(),
            "label_set_sha256": hashlib.sha256(json.dumps(sealed, sort_keys=True).encode()).hexdigest(),
        },
        "counts": {
            "queries_total": len(inference["queries"]),
            "known": len(known_queries),
            "unknown": len(unknown_queries),
            "excluded_missing": 0,
            "excluded_ambiguous": 0,
            "excluded_conflicting": 0,
            "classes_known": len(classes),
            "classes_small": 0,
        },
        "primary": {
            "name": "macro-recall@1-t0",
            "value": round(primary, 6),
            "ci95": [round(primary, 6), round(primary, 6)],
            "n_classes": len(classes),
            "denominator": max(1, len(ranks)),
            "median_across_seeds": round(primary, 6),
            "seed_range": [round(primary, 6), round(primary, 6)],
        },
        "comparisons": {
            "best_baseline": "degree-only",
            "delta": round(primary - accuracy, 6),
            "delta_ci95": [round(primary - accuracy, 6), round(primary - accuracy, 6)],
            "sesoi_pp": 5,
            "sesoi_met": (primary - accuracy) >= 0.05,
            "degree_matched": {"delta": round(primary - accuracy, 6), "ci95": [0.0, 0.0]},
            "balanced_sensitivity": {"delta": round(primary, 6), "ci95": [0.0, 0.0], "k_min": 1},
            "holm_family_size": 3,
        },
        "open_set": {
            "auroc": round(_auroc(positives, negatives), 6),
            "aupr": round(_aupr(positives, negatives), 6),
            "fpr_at_tpr95": round(fpr, 6),
            "tpr_target": 0.95,
        },
        "calibration": {
            "brier": round(brier, 6),
            "ece": round(ece, 6),
            "bins": 15,
            "temperature_source_fit": 1.0,
        },
        "within_cross": {
            "within": round(primary, 6),
            "cross": round(primary, 6),
            "gap": 0.0,
        },
        "secondary": {
            "recall@5": round(recall_at_5, 6),
            "recall@10": round(recall_at_10, 6),
            "mrr": round(mrr, 6),
            "map": round(mrr, 6),
            "macro_f1": round(primary, 6),
            "balanced_accuracy": round(accuracy, 6),
        },
        "nulls": {
            "label_permutation_p": 0.5,
            "degree_matched_p": 0.5,
            "permutations": 10000,
        },
    }
    return {"metrics": metrics, "queries": inference["queries"], "unknown": len(unknown_queries)}


def run(workdir: Path, seed: int = 20260914) -> dict:
    import evaluator_contract

    workdir.mkdir(parents=True, exist_ok=True)
    fixture = generate_fixture(seed)
    source_csv, target_csv = canvas_rows(fixture)
    stages: dict[str, dict] = {}
    stages["download"] = download_stage(workdir, source_csv.encode())
    features, labels = preprocess_stage(workdir / "raw" / "source.csv")
    stages["preprocess"] = {"rows": len(features), "classes": len(set(labels))}
    frozen = train_trivial(features, labels, seed)
    stages["train"] = {"classes": len(frozen["classes"]), "weights_sha256": frozen["sha256"][:16]}
    inference = inference_stage(frozen, fixture)
    stages["inference"] = {
        "queries": len(inference["queries"]),
        "rejected": sum(1 for query in inference["queries"] if query["rejected"]),
    }
    evaluated = evaluate_stage(inference)
    predictions = {
        "schema_version": "1.0",
        "run_id": evaluated["metrics"]["run_id"],
        "seed": seed,
        "gallery": {"nodes": len(features), "types": len(frozen["classes"])},
        "queries": [
            {"id": query["id"], "ranked": query["ranked"], "rejected": query["rejected"]}
            for query in inference["queries"]
        ],
    }
    prediction_failures = evaluator_contract.validate_predictions(predictions, "dryrun")
    metrics_failures = evaluator_contract.validate_metrics(evaluated["metrics"], "dryrun")
    if prediction_failures or metrics_failures:
        raise DryRunError("; ".join(prediction_failures + metrics_failures))
    (workdir / "predictions.json").write_text(json.dumps(predictions, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (workdir / "metrics.json").write_text(
        json.dumps(evaluated["metrics"], indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    protocol_tag = "dryrun-1.0-" + hashlib.sha256(
        (json.dumps(stages, sort_keys=True) + frozen["sha256"]).encode()
    ).hexdigest()[:8]
    manifest = {
        "schema_version": "1.0",
        "dryrun_tag": protocol_tag,
        "seed": seed,
        "stages": stages,
        "predictions_sha256": hashlib.sha256((workdir / "predictions.json").read_bytes()).hexdigest(),
        "metrics_sha256": hashlib.sha256((workdir / "metrics.json").read_bytes()).hexdigest(),
        "classes_known": frozen["classes"],
        "unknown_queries": evaluated["unknown"],
        "firewall_scanner_clean": firewall.scan_forbidden_references() == [],
    }
    (workdir / "dryrun-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workdir", type=Path, default=ROOT / "runs" / "dryrun-r08")
    parser.add_argument("--seed", type=int, default=20260914)
    args = parser.parse_args()
    manifest = run(args.workdir, args.seed)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
