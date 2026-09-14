#!/usr/bin/env python3
"""Auditoria de qualidade e congelamento do dataset analítico (H09).

Checa os snapshots canônicos de H08 (topologia pública, sem rótulos):
duplicatas, componentes conexas, graus, pesos, self-loops, isolados,
reciprocidade/assimetria, drift de schema, cobertura e reconciliação com H02/H03
e com as contagens publicadas. Modo estritamente exploratório (H07 inconclusiva
por circularidade); nenhum label, score ou crosswalk é consultado.
"""

import argparse
import hashlib
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
from scipy.sparse.csgraph import connected_components

ROOT = Path(__file__).resolve().parent.parent
EXPECTED = {
    "edges": {"source": "string", "target": "string", "weight": "int64"},
    "nodes": {"id": "string", "degree_in": "int64", "degree_out": "int64"},
}
PUBLISHED = {
    "MANC": {"neurons": "~23.000 (LIT-0074)", "nodes": 23188},
    "MCNS": {"neurons": "166.700 (LIT-0023)", "annotated_bodies": 211577},
}


class QualityError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def _schema_report(directory: Path) -> dict:
    report = {}
    for name, expected in EXPECTED.items():
        path = directory / f"{name}.parquet"
        schema = pq.read_schema(path)
        actual = {field.name: str(field.type) for field in schema}
        drift = {key: (actual.get(key), value) for key, value in expected.items() if actual.get(key) != value}
        if set(actual) != set(expected):
            drift["_extra_or_missing"] = sorted(set(actual) ^ set(expected))
        report[name] = {"columns": actual, "drift": drift}
    return report


def audit_snapshot(directory: Path, label: str) -> dict:
    started = time.perf_counter()
    nodes = pq.read_table(directory / "nodes.parquet")
    edges = pq.read_table(directory / "edges.parquet", columns=["source", "target", "weight"])
    node_ids = nodes["id"].combine_chunks()
    weights = edges["weight"].to_numpy(zero_copy_only=False)
    pre = pc.index_in(edges["source"].combine_chunks(), value_set=node_ids).to_numpy(zero_copy_only=False)
    post = pc.index_in(edges["target"].combine_chunks(), value_set=node_ids).to_numpy(zero_copy_only=False)
    if np.any(pre < 0) or np.any(post < 0):
        raise QualityError(f"{label}: aresta com endpoint fora dos nodes")
    n_nodes = len(node_ids)
    keys = pre.astype("int64") * n_nodes + post
    unique_keys = np.unique(keys)
    duplicates = int(len(keys) - len(unique_keys))
    self_loops = int(np.count_nonzero(pre == post))
    reversed_keys = post.astype("int64") * n_nodes + pre
    non_loop = pre != post
    reciprocal = int(np.count_nonzero(np.isin(keys[non_loop], reversed_keys)))
    degree_in = np.bincount(post, weights=weights, minlength=n_nodes).astype("int64")
    degree_out = np.bincount(pre, weights=weights, minlength=n_nodes).astype("int64")
    stored_in = nodes["degree_in"].to_numpy(zero_copy_only=False)
    stored_out = nodes["degree_out"].to_numpy(zero_copy_only=False)
    graph = sp.coo_matrix(
        (np.ones(len(pre), dtype="int8"), (pre, post)), shape=(n_nodes, n_nodes)
    ).tocsr()
    symmetric = graph + graph.T
    n_components, _ = connected_components(symmetric, directed=False)
    isolated = int(np.count_nonzero((stored_in + stored_out) == 0))
    report = {
        "label": label,
        "nodes": int(n_nodes),
        "edges": int(edges.num_rows),
        "weight_sum": int(weights.sum()),
        "weight_min": int(weights.min()) if len(weights) else 0,
        "weight_max": int(weights.max()) if len(weights) else 0,
        "zero_weight_edges": int(np.count_nonzero(weights == 0)),
        "negative_weight_edges": int(np.count_nonzero(weights < 0)),
        "self_loops": self_loops,
        "duplicate_pairs": duplicates,
        "reciprocal_edges": reciprocal,
        "reciprocity_fraction": round(reciprocal / max(1, int(np.count_nonzero(non_loop))), 6),
        "components": int(n_components),
        "isolated_nodes": isolated,
        "degree_in_mean": round(float(degree_in.mean()), 4),
        "degree_out_mean": round(float(degree_out.mean()), 4),
        "degree_mismatch_in": int(np.abs(degree_in - stored_in).max()),
        "degree_mismatch_out": int(np.abs(degree_out - stored_out).max()),
        "schema": _schema_report(directory),
        "seconds": round(time.perf_counter() - started, 3),
    }
    return report


def freeze_manifest(source_dir: Path, target_dir: Path, out: Path) -> dict:
    manifest = {
        "schema_version": "1.0",
        "status": "exploratory-only",
        "labels_used": False,
        "confirmatory_outcome": "nenhum (H07 inconclusiva por circularidade)",
        "source": {
            "kind": "MANC",
            "release": "manc:v1.2.1",
            "snapshot": source_dir.as_posix(),
            "files": {
                name: sha256_file(source_dir / name)
                for name in ("edges.parquet", "nodes.parquet")
            },
        },
        "target_public": {
            "kind": "MCNS",
            "release": "male-cns:v1.0",
            "snapshot": target_dir.as_posix(),
            "files": {
                name: sha256_file(target_dir / name)
                for name in ("edges.parquet", "nodes.parquet")
            },
        },
        "created_at": time.strftime("%Y-%m-%d", time.gmtime()),
    }
    digests = list(manifest["source"]["files"].values()) + list(manifest["target_public"]["files"].values())
    manifest["analytic_sha256"] = hashlib.sha256("".join(sorted(digests)).encode()).hexdigest()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def _load_provenance(directory: Path) -> dict:
    return json.loads((directory / "provenance.json").read_text(encoding="utf-8"))


def audit_pair(source_dir: Path, target_dir: Path, out: Path, manifest_out: Path) -> dict:
    source = audit_snapshot(source_dir, "MANC")
    target = audit_snapshot(target_dir, "MCNS")
    deviations = [
        "MCNS: arquivo público é segmento-a-segmento (151.856.684 arestas); o snapshot usa o nível-neurônio (26.028.386 arestas entre 211.577 bodies anotados) e descarta 125.828.298 arestas com lado não anotado (H08).",
        "MANC: 23.188 nodes medidos contra ~23.000 neurônios publicados (~0,8% acima; segmentos traçados) (LIT-0074).",
        "MCNS: 211.577 bodies anotados incluem além dos 166.700 neurônios curados; o recorte T0 é da custódia e ficou inconclusivo (H07).",
        "Desfecho confirmatório inexistente: H07 inconclusiva por circularidade; dataset congelado apenas para uso exploratório.",
        "Revisor humano único acumulando papéis (segundo indisponível).",
    ]
    report = {
        "schema_version": "1.0",
        "mode": "exploratory-only",
        "source": source,
        "target_public": target,
        "reconciliation": {
            "source_provenance": _load_provenance(source_dir),
            "target_provenance": _load_provenance(target_dir),
            "published": PUBLISHED,
        },
        "missingness": "não se aplica: grafo somente-topologia, sem atributos de nó/aresta no snapshot",
        "deviations": deviations,
    }
    manifest = freeze_manifest(source_dir, target_dir, manifest_out)
    report["analytic_manifest"] = {"path": manifest_out.as_posix(), **manifest}
    report["peak_rss_mib"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    report["seconds_total"] = round(source["seconds"] + target["seconds"], 3)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = audit_pair(args.source, args.target, args.out, args.manifest)
    except (QualityError, FileNotFoundError, KeyError) as error:
        print(f"FALHA: {error}", file=sys.stderr)
        return 1
    summary = {
        "source": {k: report["source"][k] for k in ("nodes", "edges", "weight_sum", "duplicate_pairs", "components", "isolated_nodes", "reciprocity_fraction")},
        "target": {k: report["target_public"][k] for k in ("nodes", "edges", "weight_sum", "duplicate_pairs", "components", "isolated_nodes", "reciprocity_fraction")},
        "analytic_sha256": report["analytic_manifest"]["analytic_sha256"],
        "peak_rss_mib": report["peak_rss_mib"],
        "seconds": report["seconds_total"],
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
