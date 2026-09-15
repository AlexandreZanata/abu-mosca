#!/usr/bin/env python3
"""Fatoração espectral esparsa dentro da fonte (B07).

Compara a estrutura global linear de baixo custo contra os demais baselines:
SVD truncada da matriz de adjacência dirigida e ponderada (A ≈ U S Vᵀ) e
decomposição própria da matriz simetrizada ((A + Aᵀ)/2), ambas com operadores
esparsos (scipy.sparse.linalg, ARPACK) e sem densificar a matriz completa.

Ambiguidade de sinal e rotação: cada vetor é canonicalizado por convenção fixa
(maior carga em módulo positiva; empate pelo menor índice) e a sensibilidade do
probe é medida com rotação ortogonal aleatória e troca de sinal. O subespaço
líder pode girar sob valores degenerados, então o método fica restrito ao
diagnóstico within-source e não é comparável zero-shot, como os demais
transdutivos de L06/M-07. Nenhum alinhamento entre grafos é executado.

Avaliação com o mesmo split, seeds e avaliador de B01/B03–B06: probe por
centroide com normalização source-fit ajustada só no treino. Nenhum dado além
da fonte entra neste módulo.
"""

import argparse
import json
import resource
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import scipy
import scipy.sparse as sp
import scipy.sparse.linalg as spla

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import baselines_source as bs  # noqa: E402
import metrics  # noqa: E402

CONFIGS = {
    "svd_dirigido": {"k": 32, "dims": 64, "modo": "svd_dirigida"},
    "ase_simetrizado": {"k": 32, "dims": 32, "modo": "ase_simetrizada"},
}
VERDICT = "restrito ao diagnóstico within-source (não comparável zero-shot)"
SIGN_CONVENTION = "maior carga em módulo positiva, empate pelo menor índice"
ALIGNMENT_NOTE = "nenhum alinhamento entre grafos; matching com pares conhecidos é proibido"
AMBIGUITY_NOTE = (
    "sinal neutralizado por convenção canônica (probe exato); rotação demonstrada com probe "
    "equívariante (linha L2); o probe padrão de z-score por coluna não é equívariante e não "
    "autoriza girar a base"
)
DEVICE = "cpu"


class SpectralError(RuntimeError):
    pass


def load_directed_edges(snapshot: Path) -> tuple[list[str], np.ndarray, np.ndarray, np.ndarray]:
    """Arestas dirigidas em ordem canônica de nós (invariante à ordem da tabela)."""
    nodes = pq.read_table(snapshot / "nodes.parquet")
    edges = pq.read_table(snapshot / "edges.parquet", columns=["source", "target", "weight"])
    ids = sorted(nodes["id"].combine_chunks().to_pylist())
    if not ids:
        raise SpectralError("snapshot sem nodes")
    value_set = pa.array(ids, type=pa.string())
    src = pc.index_in(edges["source"].combine_chunks(), value_set=value_set).fill_null(-1).to_numpy(zero_copy_only=False).astype(np.int64)
    dst = pc.index_in(edges["target"].combine_chunks(), value_set=value_set).fill_null(-1).to_numpy(zero_copy_only=False).astype(np.int64)
    wgt = np.asarray(edges["weight"].combine_chunks().to_pylist(), dtype=np.float64)
    if np.any(src < 0) or np.any(dst < 0):
        raise SpectralError("aresta com endpoint fora dos nodes")
    if np.any(wgt < 0):
        raise SpectralError("peso negativo no snapshot")
    return ids, src, dst, wgt


def build_directed_matrix(n_nodes: int, src: np.ndarray, dst: np.ndarray, wgt: np.ndarray) -> sp.csr_matrix:
    """Adjacência dirigida e ponderada; pares repetidos somam, zero preservado."""
    order = np.lexsort((wgt, dst, src))
    matrix = sp.coo_matrix(
        (wgt[order], (src[order], dst[order])), shape=(n_nodes, n_nodes)
    ).tocsr()
    return matrix


def starting_vector(n_nodes: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(int(seed) % (2**32))
    vector = rng.standard_normal(n_nodes)
    vector /= np.linalg.norm(vector)
    return vector


def canonical_signs(matrix: np.ndarray) -> np.ndarray:
    out = np.array(matrix, dtype=np.float64, copy=True)
    for column in range(out.shape[1]):
        values = out[:, column]
        pivot = int(np.argmax(np.abs(values)))
        if values[pivot] < 0:
            out[:, column] = -values
    return out


def fit_directed_svd(matrix: sp.csr_matrix, n_components: int, seed: int) -> tuple[np.ndarray, np.ndarray, float]:
    started = time.perf_counter()
    n_nodes = matrix.shape[0]
    u, s, vt = spla.svds(matrix, k=n_components, v0=starting_vector(n_nodes, seed))
    order = np.argsort(-s)
    s = np.asarray(s[order], dtype=np.float64)
    u = canonical_signs(np.asarray(u[:, order], dtype=np.float64))
    v = canonical_signs(np.asarray(vt[order].T, dtype=np.float64))
    embeddings = np.hstack([u * np.sqrt(s), v * np.sqrt(s)])
    return embeddings, s, time.perf_counter() - started


def fit_symmetric_ase(matrix: sp.csr_matrix, n_components: int, seed: int) -> tuple[np.ndarray, np.ndarray, float]:
    started = time.perf_counter()
    symmetric = ((matrix + matrix.T) * 0.5).tocsr()
    values, vectors = spla.eigsh(symmetric, k=n_components, which="LA", v0=starting_vector(matrix.shape[0], seed))
    order = np.argsort(-values)
    values = np.asarray(values[order], dtype=np.float64)
    vectors = canonical_signs(np.asarray(vectors[:, order], dtype=np.float64))
    scale = np.sign(values) * np.sqrt(np.abs(values))
    embeddings = vectors * scale
    return embeddings, values, time.perf_counter() - started


def scaled_matrices(embeddings: np.ndarray, order: dict[str, int], train: dict[str, str], val: dict[str, str]):
    train_matrix = np.asarray([embeddings[order[node]] for node in train])
    val_matrix = np.asarray([embeddings[order[node]] for node in val])
    stats = bs.fit_stats(train_matrix)
    return bs.transform(train_matrix, stats), bs.transform(val_matrix, stats)


def centroids_from(train_scaled: np.ndarray, train: dict[str, str], classes: list[str]) -> dict[str, np.ndarray]:
    centroids = {}
    for name in classes:
        rows = [train_scaled[index] for index, node in enumerate(train) if train[node] == name]
        if rows:
            centroids[name] = np.mean(rows, axis=0)
    return centroids


def probe_embeddings(
    embeddings: np.ndarray,
    order: dict[str, int],
    train: dict[str, str],
    val: dict[str, str],
    classes: list[str],
) -> dict[str, str]:
    train_scaled, val_scaled = scaled_matrices(embeddings, order, train, val)
    centroids = centroids_from(train_scaled, train, classes)
    predictions = {}
    for index, node in enumerate(val):
        distances = {name: float(np.linalg.norm(val_scaled[index] - centroid)) for name, centroid in centroids.items()}
        predictions[node] = min(distances, key=lambda name: (distances[name], name))
    return predictions


def probe_embeddings_equivariant(
    embeddings: np.ndarray,
    order: dict[str, int],
    train: dict[str, str],
    val: dict[str, str],
    classes: list[str],
) -> dict[str, str]:
    """Probe diagnóstico invariante a rotação: normalização L2 por linha, sem z-score por coluna."""

    def row_normalized(matrix: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms < 1e-12] = 1e-12
        return matrix / norms

    train_matrix = row_normalized(np.asarray([embeddings[order[node]] for node in train]))
    val_matrix = row_normalized(np.asarray([embeddings[order[node]] for node in val]))
    centroids = centroids_from(train_matrix, train, classes)
    predictions = {}
    for index, node in enumerate(val):
        distances = {name: float(np.linalg.norm(val_matrix[index] - centroid)) for name, centroid in centroids.items()}
        predictions[node] = min(distances, key=lambda name: (distances[name], name))
    return predictions


def random_orthogonal(dim: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(int(seed) % (2**32))
    mat, upper = np.linalg.qr(rng.randn(dim, dim))
    mat = mat * np.sign(np.diag(upper))
    return mat.astype(np.float64)


def agreement(first: dict[str, str], second: dict[str, str]) -> float:
    if not first:
        raise SpectralError("predições vazias")
    return sum(1 for node in first if first[node] == second[node]) / len(first)


def subspace_cosines(first: np.ndarray, second: np.ndarray) -> dict:
    """Cossenos dos ângulos principais entre os subespaços (bases ortonormalizadas)."""
    q_first, _ = np.linalg.qr(np.asarray(first, dtype=np.float64))
    q_second, _ = np.linalg.qr(np.asarray(second, dtype=np.float64))
    cosines = np.linalg.svd(q_first.T @ q_second, compute_uv=False)
    return {"min_cos": float(np.min(cosines)), "mean_cos": float(np.mean(cosines))}


def distance_margins(
    embeddings: np.ndarray,
    order: dict[str, int],
    train: dict[str, str],
    val: dict[str, str],
    classes: list[str],
    train_matrix: np.ndarray,
    val_matrix: np.ndarray,
) -> list[float]:
    """Margem (melhor vs segundo melhor) da distância ao centroide, por consulta."""
    centroids = {}
    for name in classes:
        rows = [train_matrix[index] for index, node in enumerate(train) if train[node] == name]
        if rows:
            centroids[name] = np.mean(rows, axis=0)
    margins = []
    for index, node in enumerate(val):
        distances = sorted(
            float(np.linalg.norm(val_matrix[index] - centroid)) for centroid in centroids.values()
        )
        margins.append(float(distances[1] - distances[0]) if len(distances) > 1 else float("inf"))
    return margins


def run(
    snapshot: Path,
    properties: Path,
    out_dir: Path,
    report_path: Path,
    configs: tuple[str, ...] = ("svd_dirigido", "ase_simetrizado"),
    seeds: tuple[int, ...] = bs.SELECTION_SEEDS,
    n_components: int = 32,
) -> dict:
    started = time.perf_counter()
    for name in configs:
        if name not in CONFIGS:
            raise SpectralError(f"configuração desconhecida: {name}")
    ids, src, dst, wgt = load_directed_edges(snapshot)
    n_nodes = len(ids)
    order = {node: position for position, node in enumerate(ids)}
    labels, label_meta = bs.load_source_labels(properties)
    labels = {node: name for node, name in labels.items() if node in order}
    counts = Counter(labels.values())
    labels = {node: name for node, name in labels.items() if counts[name] >= bs.K_MIN}
    if not labels:
        raise SpectralError("nenhum rótulo utilizável após mapear para o snapshot")
    train, val = bs.split_deterministic(labels)
    val_nodes = list(val)
    classes = sorted(set(train.values()))
    out_dir.mkdir(parents=True, exist_ok=True)

    build_started = time.perf_counter()
    matrix = build_directed_matrix(n_nodes, src, dst, wgt)
    build_seconds = time.perf_counter() - build_started
    matrix_bytes = int(matrix.data.nbytes + matrix.indices.nbytes + matrix.indptr.nbytes)
    dense_equivalent_bytes = int(n_nodes * n_nodes * 8)
    resources = {
        "nodes": n_nodes,
        "edge_rows": int(len(src)),
        "directed_nnz": int(matrix.nnz),
        "duplicate_rows": int(len(src) - matrix.nnz),
        "zero_entries": int((matrix.data == 0).sum()),
        "directed_matrix_bytes": matrix_bytes,
        "directed_dense_equivalent_bytes": dense_equivalent_bytes,
        "directed_sparse_ratio": round(matrix_bytes / dense_equivalent_bytes, 6),
        "build_seconds": round(build_seconds, 3),
        "ram_cap_gib": 24,
        "device": DEVICE,
    }

    results: dict = {}
    predictions_refs = []
    embeddings_refs = []
    for name in configs:
        mode = CONFIGS[name]["modo"]
        per_seed = []
        seed_embeddings: dict[int, np.ndarray] = {}
        seed_predictions: dict[int, dict[str, str]] = {}
        spectra: dict[int, list[float]] = {}
        for seed_index, seed in enumerate(seeds):
            if mode == "svd_dirigida":
                embeddings, spectrum, fit_seconds = fit_directed_svd(matrix, n_components, int(seed))
            else:
                embeddings, spectrum, fit_seconds = fit_symmetric_ase(matrix, n_components, int(seed))
            probe_started = time.perf_counter()
            predictions = probe_embeddings(embeddings, order, train, val, classes)
            probe_seconds = time.perf_counter() - probe_started
            evaluation = bs.evaluate_predictions(val, predictions)
            seed_embeddings[seed_index] = embeddings
            seed_predictions[seed_index] = predictions
            spectra[seed_index] = [float(value) for value in spectrum]
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
                    "fit_seconds": round(fit_seconds, 3),
                    "probe_seconds": round(probe_seconds, 3),
                    "spectrum_top": spectra[seed_index][0],
                    "spectrum_min": spectra[seed_index][-1],
                    "dims": int(embeddings.shape[1]),
                }
            )
        dims = int(seed_embeddings[0].shape[1])
        rotation = random_orthogonal(dims, 20260914)
        sign_pattern = np.where(np.arange(dims) % 2 == 0, -1.0, 1.0)
        base = seed_predictions[0]
        rotated = probe_embeddings(seed_embeddings[0] @ rotation, order, train, val, classes)
        rotated_equivariant = probe_embeddings_equivariant(seed_embeddings[0] @ rotation, order, train, val, classes)
        base_equivariant = probe_embeddings_equivariant(seed_embeddings[0], order, train, val, classes)
        flipped = probe_embeddings(seed_embeddings[0] * sign_pattern, order, train, val, classes)
        pair_cosines = {}
        spans = (lambda emb: emb[:, :n_components]) if mode == "svd_dirigida" else (lambda emb: emb)
        seed_keys = sorted(seed_embeddings)
        for pos, first_key in enumerate(seed_keys):
            for second_key in seed_keys[pos + 1 :]:
                pair_cosines[f"{first_key}x{second_key}"] = subspace_cosines(
                    spans(seed_embeddings[first_key]), spans(seed_embeddings[second_key])
                )
        macro_values = sorted(item["macro_recall@1"] for item in per_seed)
        results[name] = {
            "k_components": n_components,
            "dims": dims,
            "per_seed": per_seed,
            "median_macro_recall@1": macro_values[len(macro_values) // 2],
            "rotation_agreement_standard_probe": agreement(base, rotated),
            "rotation_agreement_equivariant_probe": agreement(base_equivariant, rotated_equivariant),
            "sign_agreement": agreement(base, flipped),
            "prediction_agreement_seed0": {
                f"0x{key}": agreement(base, seed_predictions[key]) for key in seed_keys if key != 0
            },
            "subspace_cosines": pair_cosines,
        }
        del seed_embeddings, seed_predictions
    report = {
        "schema": "b07-spectral",
        "verdict": VERDICT,
        "configs": {name: dict(CONFIGS[name]) for name in configs},
        "seeds": list(seeds),
        "hyperparameters": {
            "components": n_components,
            "directed_dims": 2 * n_components,
            "symmetric_dims": n_components,
            "solver": "scipy.sparse.linalg svds/eigsh (ARPACK) com v0 determinístico por seed",
            "sign_convention": SIGN_CONVENTION,
            "alignment": ALIGNMENT_NOTE,
            "ambiguity_control": AMBIGUITY_NOTE,
            "scipy_version": scipy.__version__,
            "numpy_version": np.__version__,
        },
        "resources": resources,
        "label_meta": label_meta,
        "nodes_used": len(labels),
        "split": {"train": len(train), "val": len(val), "classes": len(classes)},
        "results": results,
        "predictions": predictions_refs,
        "embeddings": embeddings_refs,
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
    parser.add_argument("--configs", nargs="+", default=["svd_dirigido", "ase_simetrizado"], choices=sorted(CONFIGS))
    parser.add_argument("--seed-idx", default="0,1,2")
    parser.add_argument("--components", type=int, default=32)
    args = parser.parse_args()
    try:
        idx = [int(part) for part in args.seed_idx.split(",")]
        seeds = tuple(bs.SELECTION_SEEDS[i] for i in idx)
    except (ValueError, IndexError) as error:
        print(f"FALHA: seed-idx inválido: {error}", file=sys.stderr)
        return 1
    try:
        report = run(args.snapshot, args.properties, args.out_dir, args.report, tuple(args.configs), seeds, args.components)
    except (SpectralError, FileNotFoundError) as error:
        print(f"FALHA: {error}", file=sys.stderr)
        return 1
    summary = {
        "verdict": report["verdict"],
        "median_macro": {name: data["median_macro_recall@1"] for name, data in report["results"].items()},
        "resources": report["resources"],
        "seconds": report["seconds"],
        "peak_rss_mib": report["peak_rss_mib"],
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
