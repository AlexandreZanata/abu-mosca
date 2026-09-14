#!/usr/bin/env python3
"""Contrato de configuração, RUN-MANIFEST e determinismo (R04).

Executa uma fixture determinística e registra toda opção efetiva, estado do Git,
ambiente, seeds derivadas e recursos em `runs/<run_id>/manifest.json`. O
`run_id` é imutável, deriva de configuração + commit + versão da ferramenta e o
cache nunca é sobrescrito quando as saídas divergem.
"""

import argparse
import hashlib
import json
import os
import platform
import resource
import shutil
import subprocess
import sys
import time
from importlib import metadata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from seeds import derive_seed  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = ROOT / "runs"
CONFIG_SCHEMA = ROOT / "schemas" / "run-config.schema.json"
MANIFEST_SCHEMA = ROOT / "schemas" / "run-manifest.schema.json"
TOOL_VERSION = "1.0"
SCHEMA_VERSION = "1.0"
CONFIG_REQUIRED = ("experiment", "seed", "params")
CONFIG_OPTIONAL = ("notes",)
PARAM_DEFAULTS = {"n_bytes": 4096, "repeats": 2}
PARAM_LIMITS = {"n_bytes": (1, 1_000_000), "repeats": (1, 64)}
SEED_NAMES = ("stream",)
TRACKED_PACKAGES = ("numpy", "scipy", "pandas", "pyarrow", "torch", "pytest")


class RunError(RuntimeError):
    pass


def canonical_json(payload) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def validate_config(payload: dict) -> list[str]:
    failures: list[str] = []
    if not isinstance(payload, dict):
        return ["config: raiz deve ser um objeto JSON"]
    for field in CONFIG_REQUIRED:
        if field not in payload:
            failures.append(f"config: campo obrigatório ausente '{field}'")
    for field in payload:
        if field not in CONFIG_REQUIRED + CONFIG_OPTIONAL:
            failures.append(f"config: campo inesperado '{field}'")
    experiment = payload.get("experiment")
    if not isinstance(experiment, str) or not experiment or any(
        char not in "abcdefghijklmnopqrstuvwxyz0123456789-" for char in experiment
    ):
        failures.append("config: 'experiment' deve usar apenas [a-z0-9-]")
    seed = payload.get("seed")
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0 or seed > 2**63 - 1:
        failures.append("config: 'seed' deve ser inteiro entre 0 e 2^63-1")
    params = payload.get("params")
    if not isinstance(params, dict):
        failures.append("config: 'params' deve ser objeto")
    else:
        for key, value in params.items():
            if key not in PARAM_LIMITS:
                failures.append(f"config: parâmetro inesperado '{key}'")
                continue
            low, high = PARAM_LIMITS[key]
            if not isinstance(value, int) or isinstance(value, bool) or not low <= value <= high:
                failures.append(f"config: '{key}' deve ser inteiro entre {low} e {high}")
    return failures


def resolve_config(payload: dict) -> dict:
    params = dict(PARAM_DEFAULTS)
    params.update(payload.get("params", {}))
    resolved = {
        "experiment": payload["experiment"],
        "seed": payload["seed"],
        "params": dict(sorted(params.items())),
    }
    if "notes" in payload:
        resolved["notes"] = payload["notes"]
    return resolved


def git_state() -> dict:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout
        diff = subprocess.run(
            ["git", "diff"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout
        dirty = bool(status.strip())
        return {
            "git_commit": commit,
            "git_dirty": dirty,
            "dirty_diff_sha256": sha256_bytes(diff.encode("utf-8")) if dirty else None,
        }
    except (subprocess.SubprocessError, FileNotFoundError) as error:
        return {"git_commit": "indisponivel", "git_dirty": True, "dirty_diff_sha256": None, "erro": str(error)}


def environment_state() -> dict:
    packages = {}
    for name in TRACKED_PACKAGES:
        try:
            packages[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            continue
    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "packages": packages,
    }


def compute_run_id(config: dict, code: dict) -> str:
    key = {"config": config, "commit": code["git_commit"], "tool": TOOL_VERSION}
    return sha256_bytes(canonical_json(key).encode("utf-8"))[:16]


def _stream(seed_value: int, size: int) -> bytes:
    output = bytearray()
    counter = 0
    while len(output) < size:
        output += hashlib.sha256(seed_value.to_bytes(8, "big") + counter.to_bytes(8, "big")).digest()
        counter += 1
    return bytes(output[:size])


def fixture_outputs(config: dict, run_id: str, seeds: dict) -> dict[str, bytes]:
    stream = bytearray()
    for repeat in range(config["params"]["repeats"]):
        block_seed = derive_seed(config["seed"], run_id, "stream", str(repeat))
        stream += _stream(block_seed, config["params"]["n_bytes"])
    histogram = [0] * 256
    for value in stream:
        histogram[value] += 1
    summary = {
        "n_bytes": config["params"]["n_bytes"],
        "repeats": config["params"]["repeats"],
        "total_bytes": len(stream),
        "sha256_stream": sha256_bytes(bytes(stream)),
        "byte_histogram": histogram,
        "seed_master": config["seed"],
        "derived_seed_stream": seeds["stream"],
    }
    return {
        "outputs/stream.bin": bytes(stream),
        "outputs/summary.json": (canonical_json(summary) + "\n").encode("utf-8"),
    }


def _output_entries(run_dir: Path) -> list[dict]:
    entries = []
    for path in sorted(run_dir.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            entries.append(
                {
                    "path": path.relative_to(run_dir).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_bytes(path.read_bytes()),
                }
            )
    return entries


def execute(config_path: Path, runs_dir: Path) -> dict:
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    failures = validate_config(payload)
    if failures:
        raise RunError("; ".join(failures))
    config = resolve_config(payload)
    config_sha = sha256_bytes(canonical_json(config).encode("utf-8"))
    code = git_state()
    run_id = compute_run_id(config, code)
    run_dir = runs_dir / run_id
    manifest_path = run_dir / "manifest.json"

    if run_dir.exists():
        if not manifest_path.exists():
            raise RunError(f"run '{run_id}' existe sem manifesto; limpe manualmente antes de repetir")
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        if existing.get("config_sha256") != config_sha or existing.get("code", {}).get("git_commit") != code["git_commit"]:
            raise RunError(f"run '{run_id}' divergente no cache; nada foi sobrescrito")
        for entry in existing.get("outputs", []):
            path = run_dir / entry["path"]
            if not path.exists() or sha256_bytes(path.read_bytes()) != entry["sha256"]:
                raise RunError(f"saída divergente para '{entry['path']}' no cache; nada foi sobrescrito")
        return {"status": "cached", "run_id": run_id, "manifest": manifest_path, "manifest_data": existing}

    seeds = {name: derive_seed(config["seed"], run_id, name) for name in SEED_NAMES}
    temp_dir = runs_dir / f".tmp-{run_id}"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    started = time.perf_counter()
    outputs = fixture_outputs(config, run_id, seeds)
    for rel, content in outputs.items():
        path = temp_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    wall = round(time.perf_counter() - started, 4)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "tool": f"tools/run.py {TOOL_VERSION}",
        "config": config,
        "config_sha256": config_sha,
        "code": code,
        "environment": environment_state(),
        "seeds": {"master": config["seed"], "derived": seeds},
        "resources": {
            "wall_s": wall,
            "peak_rss_mib": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 2),
            "disk_free_gib": round(shutil.disk_usage(runs_dir).free / 2**30, 2),
        },
        "outputs": _output_entries(temp_dir),
        "status": "completed",
    }
    (temp_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    runs_dir.mkdir(parents=True, exist_ok=True)
    if run_dir.exists():
        shutil.rmtree(temp_dir)
        raise RunError(f"run '{run_id}' apareceu durante a execução; nada foi sobrescrito")
    os.replace(temp_dir, run_dir)
    return {"status": "completed", "run_id": run_id, "manifest": manifest_path, "manifest_data": manifest}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--runs-dir", type=Path, default=RUNS_DIR)
    args = parser.parse_args()
    try:
        result = execute(args.config, args.runs_dir)
    except RunError as error:
        print(f"FALHA: {error}", file=sys.stderr)
        return 1
    manifest = result["manifest_data"]
    print(f"{result['status']}: run_id={result['run_id']} em {result['manifest']}")
    for entry in manifest["outputs"]:
        print(f"  {entry['path']} {entry['bytes']} bytes sha256={entry['sha256'][:16]}…")
    return 0


if __name__ == "__main__":
    sys.exit(main())
