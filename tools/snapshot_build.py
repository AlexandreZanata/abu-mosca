#!/usr/bin/env python3
"""Snapshots canônicos colunares completos (H08).

Materializa o grafo canônico (H01) em Parquet — `edges.parquet`
(`source`, `target`, `weight`) e `nodes.parquet` (`id`, `degree_in`,
`degree_out`) — com IDs opacos, `provenance.json` e `SHA256SUMS`. Processa as
releases completas da fonte (MANC `traced-connections.csv`) e do alvo público
(MCNS `connectome-weights`), em fatias para limitar RAM, verifica conservação de
peso, confronta o sha256 de entrada com o manifesto R03 e nunca sobrescreve
snapshot divergente (idempotente por hash).
"""

import argparse
import csv
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

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import opaque_ids  # noqa: E402

EDGE_COLUMNS = ("source", "target", "weight")
NODE_COLUMNS = ("id", "degree_in", "degree_out")
SLICE_ROWS = 8_000_000
MANC_DATASET, MANC_RELEASE = "MANC", "manc:v1.2.1"
MCNS_DATASET, MCNS_RELEASE = "MCNS", "male-cns:v1.0"


class SnapshotError(RuntimeError):
    pass


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(chunk):
            digest.update(block)
    return digest.hexdigest()


def manifest_sha256(manifest: Path, suffix: str) -> str | None:
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    entry = next((item for item in payload["files"] if item["path"].endswith(suffix)), None)
    return entry["sha256"] if entry else None


def _opaque_array(bodies: np.ndarray, dataset: str, release: str) -> pa.Array:
    values = [opaque_ids.opaque_node_id(dataset, release, body) for body in bodies.tolist()]
    return pa.array(values, type=pa.string())


def _write_parquet(path: Path, table: pa.Table, row_group_size: int = SLICE_ROWS) -> None:
    pq.write_table(table, path, compression="zstd", row_group_size=row_group_size)


def _check_idempotent(out_dir: Path, input_sha: str) -> bool:
    provenance_path = out_dir / "provenance.json"
    if not provenance_path.exists():
        return False
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    if provenance.get("input_sha256") != input_sha:
        raise SnapshotError("snapshot existente com entrada divergente; nada foi sobrescrito")
    for name, expected in provenance.get("files", {}).items():
        path = out_dir / name
        if not path.exists() or sha256_file(path) != expected:
            raise SnapshotError(f"snapshot existente com '{name}' divergente; nada foi sobrescrito")
    return True


def _finish(out_dir: Path, provenance: dict) -> dict:
    files = {
        name: sha256_file(out_dir / name)
        for name in ("edges.parquet", "nodes.parquet")
    }
    provenance["files"] = files
    provenance["peak_rss_mib"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    provenance["snapshot_set_sha256"] = hashlib.sha256(
        "".join(sorted(files.values())).encode()
    ).hexdigest()
    (out_dir / "provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out_dir / "SHA256SUMS").write_text(
        "".join(f"{digest}  {name}\n" for name, digest in sorted(files.items())), encoding="utf-8"
    )
    provenance["provenance_sha256"] = sha256_file(out_dir / "provenance.json")
    return provenance


def _verify_edges(out_dir: Path, expected_rows: int, expected_weight: int) -> dict:
    edges = pq.read_table(out_dir / "edges.parquet", columns=list(EDGE_COLUMNS))
    rows = edges.num_rows
    total = int(pc.sum(edges["weight"]).as_py())
    if rows != expected_rows or total != expected_weight:
        raise SnapshotError(f"snapshot divergente: {rows}/{total} != {expected_rows}/{expected_weight}")
    if any(not column.startswith(("source", "target", "weight")) for column in edges.column_names):
        raise SnapshotError("coluna inesperada no snapshot de arestas")
    return {"rows": rows, "weight_sum": total}


def build_manc(connections: Path, manifest: Path, out_dir: Path) -> dict:
    started = time.perf_counter()
    input_sha = sha256_file(connections)
    official = manifest_sha256(manifest, "manc_traced_connections.csv")
    if official and input_sha != official:
        raise SnapshotError("sha256 da fonte não confere com o manifesto R03")
    if _check_idempotent(out_dir, input_sha):
        return {**json.loads((out_dir / "provenance.json").read_text(encoding="utf-8")), "status": "cached"}
    index: dict[str, int] = {}
    sources: list[int] = []
    targets: list[int] = []
    weights: list[int] = []
    rows = 0
    weight_sum = 0
    with connections.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header = tuple(next(reader))
        if header != ("bodyId_pre", "bodyId_post", "weight"):
            raise SnapshotError(f"cabeçalho inesperado: {header!r}")
        for row in reader:
            pre, post, weight = row[0].strip(), row[1].strip(), int(row[2])
            if weight < 0:
                raise SnapshotError("peso negativo na fonte")
            sources.append(index.setdefault(pre, len(index)))
            targets.append(index.setdefault(post, len(index)))
            weights.append(weight)
            rows += 1
            weight_sum += weight
    order = {position: body for body, position in index.items()}
    bodies = np.array([order[position] for position in range(len(order))])
    node_ids = _opaque_array(bodies, MANC_DATASET, MANC_RELEASE)
    source_array = pc.take(node_ids, pa.array(sources, type=pa.int64()))
    target_array = pc.take(node_ids, pa.array(targets, type=pa.int64()))
    weight_array = pa.array(weights, type=pa.int64())
    edges = pa.table(
        {
            "source": source_array,
            "target": target_array,
            "weight": weight_array,
        }
    )
    weights_np = np.asarray(weights, dtype="int64")
    degree_in = np.bincount(np.asarray(targets), weights=weights_np, minlength=len(order)).astype("int64")
    degree_out = np.bincount(np.asarray(sources), weights=weights_np, minlength=len(order)).astype("int64")
    nodes = pa.table(
        {
            "id": node_ids,
            "degree_in": pa.array(degree_in.tolist(), type=pa.int64()),
            "degree_out": pa.array(degree_out.tolist(), type=pa.int64()),
        }
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_parquet(out_dir / "edges.parquet", edges)
    _write_parquet(out_dir / "nodes.parquet", nodes)
    verified = _verify_edges(out_dir, rows, weight_sum)
    provenance = {
        "dataset": MANC_DATASET,
        "release": MANC_RELEASE,
        "license": "CC-BY-4.0",
        "kind": "source",
        "input": connections.as_posix(),
        "input_sha256": input_sha,
        "rows": rows,
        "nodes": len(order),
        "weight_sum": weight_sum,
        "self_loops": sum(1 for source, target in zip(sources, targets) if source == target),
        "id_scheme": "opaque n<16 hex> via sha256(dataset|release|body)",
        "columns": {"edges": list(EDGE_COLUMNS), "nodes": list(NODE_COLUMNS)},
        "degree_semantics": "weighted_sum",
        "seconds": round(time.perf_counter() - started, 3),
        "verified": verified,
    }
    return _finish(out_dir, provenance)


def _build_mcns_neuron_level(table: pa.Table, bodies: pa.Array, node_ids: pa.Array, annotations: Path, manifest: Path) -> tuple[dict, dict]:
    input_sha = sha256_file(annotations)
    official = manifest_sha256(manifest, "body-annotations-male-cns")
    if official and input_sha != official:
        raise SnapshotError("sha256 das anotações não confere com o manifesto R03")
    pre = table["body_pre"].combine_chunks()
    post = table["body_post"].combine_chunks()
    mask = pc.and_(pc.is_in(pre, value_set=bodies), pc.is_in(post, value_set=bodies))
    kept = int(pc.sum(pc.cast(mask, "int64")).as_py())
    pre_f = pc.filter(pre, mask)
    post_f = pc.filter(post, mask)
    weight_f = pc.filter(table["weight"].combine_chunks(), mask)
    grouped = pa.table(
        {
            "pre": pc.index_in(pre_f, value_set=bodies),
            "post": pc.index_in(post_f, value_set=bodies),
            "weight": weight_f,
        }
    ).group_by(["pre", "post"]).aggregate([("weight", "sum")])
    grouped = grouped.rename_columns(["pre", "post", "weight"]).sort_by(
        [("pre", "ascending"), ("post", "ascending")]
    )
    pre_idx = grouped["pre"].to_numpy(zero_copy_only=False)
    post_idx = grouped["post"].to_numpy(zero_copy_only=False)
    weights_np = grouped["weight"].to_numpy(zero_copy_only=False)
    degree_in = np.bincount(post_idx, weights=weights_np, minlength=len(bodies)).astype("int64")
    degree_out = np.bincount(pre_idx, weights=weights_np, minlength=len(bodies)).astype("int64")
    edges = pa.table(
        {
            "source": pc.take(node_ids, grouped["pre"]),
            "target": pc.take(node_ids, grouped["post"]),
            "weight": grouped["weight"],
        }
    )
    nodes = pa.table(
        {
            "id": node_ids,
            "degree_in": pa.array(degree_in.tolist(), type=pa.int64()),
            "degree_out": pa.array(degree_out.tolist(), type=pa.int64()),
        }
    )
    weight_sum = int(weights_np.sum())
    metrics = {"edges": edges, "nodes": nodes, "rows": grouped.num_rows, "weight_sum": weight_sum}
    provenance_extra = {
        "level": "neuron-level",
        "annotations": annotations.as_posix(),
        "annotations_sha256": input_sha,
        "annotations_columns_used": ["bodyId"],
        "segment_edges_total": table.num_rows,
        "segment_edges_kept_both_annotated": kept,
        "segment_edges_dropped": table.num_rows - kept,
        "self_loops": int(np.count_nonzero(pre_idx == post_idx)),
    }
    return metrics, provenance_extra


def build_mcns(weights: Path, manifest: Path, out_dir: Path, annotations: Path | None = None) -> dict:
    started = time.perf_counter()
    input_sha = sha256_file(weights)
    official = manifest_sha256(manifest, "mcns_connectome_weights.feather")
    if official and input_sha != official:
        raise SnapshotError("sha256 do alvo não confere com o manifesto R03")
    if _check_idempotent(out_dir, input_sha):
        return {**json.loads((out_dir / "provenance.json").read_text(encoding="utf-8")), "status": "cached"}
    table = pq.read_table(weights) if weights.suffix == ".parquet" else __import__("pyarrow.feather", fromlist=["feather"]).read_table(weights, memory_map=True)
    if tuple(table.column_names) != ("body_pre", "body_post", "weight"):
        raise SnapshotError(f"colunas inesperadas: {tuple(table.column_names)}")
    if annotations is not None:
        annotations_table = __import__("pyarrow.feather", fromlist=["feather"]).read_table(annotations, memory_map=True)
        if "bodyId" not in annotations_table.column_names:
            raise SnapshotError("anotações sem coluna 'bodyId'")
        bodies = annotations_table["bodyId"].combine_chunks()
        bodies_np = bodies.to_numpy(zero_copy_only=False)
        node_ids = _opaque_array(bodies_np, MCNS_DATASET, MCNS_RELEASE)
        metrics, extra = _build_mcns_neuron_level(table, bodies, node_ids, annotations, manifest)
        out_dir.mkdir(parents=True, exist_ok=True)
        _write_parquet(out_dir / "edges.parquet", metrics["edges"])
        _write_parquet(out_dir / "nodes.parquet", metrics["nodes"])
        verified = _verify_edges(out_dir, metrics["rows"], metrics["weight_sum"])
        provenance = {
            "dataset": MCNS_DATASET,
            "release": MCNS_RELEASE,
            "license": "CC-BY-4.0",
            "kind": "target-public",
            "input": weights.as_posix(),
            "input_sha256": input_sha,
            "rows": metrics["rows"],
            "nodes": len(bodies_np),
            "weight_sum": metrics["weight_sum"],
            "id_scheme": "opaque n<16 hex> via sha256(dataset|release|body)",
            "columns": {"edges": list(EDGE_COLUMNS), "nodes": list(NODE_COLUMNS)},
            "degree_semantics": "weighted_sum",
            "no_labels": True,
            "seconds": round(time.perf_counter() - started, 3),
            "verified": verified,
            **extra,
        }
        return _finish(out_dir, provenance)
    bodies = pc.unique(pa.concat_arrays([table["body_pre"].combine_chunks(), table["body_post"].combine_chunks()]))
    bodies_np = bodies.to_numpy(zero_copy_only=False)
    node_ids = _opaque_array(bodies_np, MCNS_DATASET, MCNS_RELEASE)
    degree_in = np.zeros(len(bodies_np), dtype="int64")
    degree_out = np.zeros(len(bodies_np), dtype="int64")
    rows = 0
    weight_sum = 0
    self_loops = 0
    out_dir.mkdir(parents=True, exist_ok=True)
    writer = pq.ParquetWriter(out_dir / "edges.parquet", pa.schema(
        [("source", pa.string()), ("target", pa.string()), ("weight", pa.int64())]
    ), compression="zstd")
    try:
        for start in range(0, table.num_rows, SLICE_ROWS):
            stop = min(start + SLICE_ROWS, table.num_rows)
            sl = table.slice(start, stop - start)
            pre_idx = pc.index_in(sl["body_pre"], value_set=bodies)
            post_idx = pc.index_in(sl["body_post"], value_set=bodies)
            pre_idx_np = pre_idx.to_numpy(zero_copy_only=False)
            post_idx_np = post_idx.to_numpy(zero_copy_only=False)
            weight_np = sl["weight"].to_numpy(zero_copy_only=False)
            np.add.at(degree_out, pre_idx_np, weight_np)
            np.add.at(degree_in, post_idx_np, weight_np)
            rows += sl.num_rows
            weight_sum += int(weight_np.sum())
            if np.any(pre_idx_np == post_idx_np):
                self_loops += int(np.count_nonzero(pre_idx_np == post_idx_np))
            writer.write_table(
                pa.table(
                    {
                        "source": pc.take(node_ids, pre_idx),
                        "target": pc.take(node_ids, post_idx),
                        "weight": sl["weight"],
                    }
                ),
                row_group_size=SLICE_ROWS,
            )
    finally:
        writer.close()
    nodes = pa.table(
        {
            "id": node_ids,
            "degree_in": pa.array(degree_in.tolist(), type=pa.int64()),
            "degree_out": pa.array(degree_out.tolist(), type=pa.int64()),
        }
    )
    _write_parquet(out_dir / "nodes.parquet", nodes)
    verified = _verify_edges(out_dir, rows, weight_sum)
    provenance = {
        "dataset": MCNS_DATASET,
        "release": MCNS_RELEASE,
        "license": "CC-BY-4.0",
        "kind": "target-public",
        "input": weights.as_posix(),
        "input_sha256": input_sha,
        "rows": rows,
        "nodes": len(bodies_np),
        "weight_sum": weight_sum,
        "self_loops": self_loops,
        "id_scheme": "opaque n<16 hex> via sha256(dataset|release|body)",
        "columns": {"edges": list(EDGE_COLUMNS), "nodes": list(NODE_COLUMNS)},
        "no_labels": True,
        "seconds": round(time.perf_counter() - started, 3),
        "verified": verified,
    }
    return _finish(out_dir, provenance)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    manc = sub.add_parser("manc")
    manc.add_argument("--connections", type=Path, required=True)
    manc.add_argument("--manifest", type=Path, required=True)
    manc.add_argument("--out", type=Path, required=True)
    mcns = sub.add_parser("mcns")
    mcns.add_argument("--weights", type=Path, required=True)
    mcns.add_argument("--manifest", type=Path, required=True)
    mcns.add_argument("--out", type=Path, required=True)
    mcns.add_argument("--annotations", type=Path, default=None)
    args = parser.parse_args()
    try:
        result = (
            build_manc(args.connections, args.manifest, args.out)
            if args.command == "manc"
            else build_mcns(args.weights, args.manifest, args.out, args.annotations)
        )
    except SnapshotError as error:
        print(f"FALHA: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
