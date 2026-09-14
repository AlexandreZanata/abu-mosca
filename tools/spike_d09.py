#!/usr/bin/env python3
"""Sondas mínimas de escala (D09): inspeção, custo Parquet/Arrow e COO/CSR."""

import argparse
import json
import pathlib
import resource
import time


def peak_rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def read_table(p: pathlib.Path):
    import pandas as pd

    if p.suffix == ".feather":
        return pd.read_feather(p)
    if p.suffix == ".csv":
        return pd.read_csv(p)
    if p.suffix == ".parquet":
        return pd.read_parquet(p)
    raise SystemExit(f"formato não suportado: {p.suffix}")


def inspect(path: str) -> dict:
    p = pathlib.Path(path)
    out = {"path": str(p), "bytes": p.stat().st_size}
    started = time.perf_counter()
    if p.suffix == ".npy":
        import numpy as np

        arr = np.load(p, mmap_mode="r")
        out.update(
            format="npy",
            dtype=str(arr.dtype),
            shape=list(arr.shape),
            nbytes=int(arr.nbytes),
        )
    else:
        df = read_table(p)
        out.update(
            format=p.suffix.lstrip("."),
            rows=int(len(df)),
            cols=int(len(df.columns)),
            mem_bytes=int(df.memory_usage(deep=False).sum()),
            dtypes={c: str(df[c].dtype) for c in df.columns[:14]},
        )
    out["load_s"] = round(time.perf_counter() - started, 3)
    out["peak_rss_mb"] = round(peak_rss_mb(), 1)
    return out


def parquet(path: str, out_dir: str) -> dict:
    p = pathlib.Path(path)
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    result = {"path": str(p), "bytes_in": p.stat().st_size}
    started = time.perf_counter()
    df = read_table(p)
    result["load_s"] = round(time.perf_counter() - started, 3)
    target = out_dir / (p.stem + ".zstd.parquet")
    started = time.perf_counter()
    df.to_parquet(target, engine="pyarrow", compression="zstd", index=False)
    result["write_s"] = round(time.perf_counter() - started, 3)
    result["bytes_parquet_zstd"] = target.stat().st_size
    del df
    started = time.perf_counter()
    import pandas as pd

    back = pd.read_parquet(target, engine="pyarrow", memory_map=True)
    result["mmap_read_s"] = round(time.perf_counter() - started, 3)
    result["rows"] = int(len(back))
    result["mem_bytes"] = int(back.memory_usage(deep=False).sum())
    result["peak_rss_mb"] = round(peak_rss_mb(), 1)
    return result


def csr(path: str, pre: str, post: str, weight: str | None = None) -> dict:
    import numpy as np
    import pandas as pd
    import scipy.sparse as sp

    p = pathlib.Path(path)
    cols = [pre, post] + ([weight] if weight else [])
    started = time.perf_counter()
    dtype = {weight: "float32"} if weight else None
    df = pd.read_csv(p, usecols=cols, dtype=dtype)
    load_s = time.perf_counter() - started
    rows = len(df)
    pre_ids = df[pre].to_numpy()
    post_ids = df[post].to_numpy()
    uniq = np.unique(np.concatenate([pre_ids, post_ids]))
    index_of = pd.Series(np.arange(len(uniq), dtype=np.int64), index=uniq)
    r = index_of.loc[pre_ids].to_numpy()
    c = index_of.loc[post_ids].to_numpy()
    del index_of, pre_ids, post_ids, uniq
    coo_bytes = int(r.nbytes + c.nbytes)
    if weight:
        data = df[weight].to_numpy()
        coo_bytes += int(data.nbytes)
    mat = sp.csr_matrix(
        (data if weight else np.ones(rows, dtype=np.float32), (r, c)),
        shape=(int(r.max()) + 1, int(c.max()) + 1),
    )
    csr_bytes = int(mat.data.nbytes + mat.indices.nbytes + mat.indptr.nbytes)
    result = {
        "path": str(p),
        "rows": int(rows),
        "nodes_indexados": int(mat.shape[0]),
        "nnz": int(mat.nnz),
        "weighted": bool(weight),
        "load_s": round(load_s, 3),
        "build_s": round(time.perf_counter() - started - load_s, 3),
        "coo_bytes": coo_bytes,
        "csr_bytes": csr_bytes,
        "coo_bytes_per_row": round(coo_bytes / rows, 2),
        "csr_bytes_per_nnz": round(csr_bytes / max(mat.nnz, 1), 2),
        "dtypes": {"index": "int64" if r.dtype == np.int64 else str(r.dtype)},
        "peak_rss_mb": round(peak_rss_mb(), 1),
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("inspect")
    p1.add_argument("path")
    p2 = sub.add_parser("parquet")
    p2.add_argument("path")
    p2.add_argument("--out-dir", default="data/raw/spikes/tmp")
    p3 = sub.add_parser("csr")
    p3.add_argument("path")
    p3.add_argument("--pre", required=True)
    p3.add_argument("--post", required=True)
    p3.add_argument("--weight", default=None)
    args = parser.parse_args()
    if args.cmd == "inspect":
        out = inspect(args.path)
    elif args.cmd == "parquet":
        out = parquet(args.path, args.out_dir)
    else:
        out = csr(args.path, args.pre, args.post, args.weight)
    print(json.dumps(out, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
