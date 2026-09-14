#!/usr/bin/env python3
"""Diagnóstico do ambiente: versões, hardware, licenças e operação CUDA mínima."""

import argparse
import importlib.metadata as md
import json
import platform
import resource
import shutil
import subprocess
import sys
import time
from pathlib import Path

TOP_LEVEL = ("numpy", "scipy", "pandas", "pyarrow", "torch", "pytest")


def license_of(name: str) -> str:
    meta = md.metadata(name)
    expression = meta.get("License-Expression")
    if expression:
        return expression
    classifier = next(
        (c.removeprefix("License :: ").strip() for c in meta.get_all("Classifier") or []
         if c.startswith("License ::")),
        "",
    )
    raw = (meta.get("License") or "").strip().splitlines()
    short = raw[0].strip() if raw else ""
    return expression or classifier or short or "não declarada no metadado"


def nvidia_smi() -> dict:
    fields = "name,driver_version,memory.total,compute_cap"
    try:
        out = subprocess.run(
            ["nvidia-smi", f"--query-gpu={fields}", "--format=csv,noheader"],
            capture_output=True, text=True, check=True, timeout=30,
        ).stdout.strip()
    except (FileNotFoundError, subprocess.SubprocessError) as error:
        return {"disponivel": False, "erro": str(error)}
    name, driver, memory, compute = (part.strip() for part in out.split(","))
    return {
        "disponivel": True,
        "nome": name,
        "driver": driver,
        "vram_mib": int(memory.split()[0]),
        "compute_cap": compute,
    }


def cuda_op() -> dict:
    import torch

    result = {
        "torch": torch.__version__,
        "torch_cuda_runtime": torch.version.cuda,
        "cuda_available": bool(torch.cuda.is_available()),
    }
    if not result["cuda_available"]:
        return result
    result["dispositivo"] = torch.cuda.get_device_name(0)
    started = time.perf_counter()
    a = torch.rand(1024, 1024, device="cuda")
    b = torch.rand(1024, 1024, device="cuda")
    c = (a @ b).sum()
    torch.cuda.synchronize()
    result["matmul_1024_s"] = round(time.perf_counter() - started, 4)
    result["matmul_finito"] = bool(torch.isfinite(c).item())
    result["vram_alocada_mib"] = round(torch.cuda.memory_allocated(0) / 2**20, 1)
    result["vram_reservada_mib"] = round(torch.cuda.memory_reserved(0) / 2**20, 1)
    return result


def relativo(path: str) -> str:
    try:
        return Path(path).relative_to(Path.cwd()).as_posix()
    except ValueError:
        return Path(path).name


def collect() -> dict:
    os_release = {}
    for line in Path("/etc/os-release").read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            os_release[key] = value.strip('"')
    disk = shutil.disk_usage(Path.home())
    data = {
        "sistema": {
            "distro": os_release.get("PRETTY_NAME", platform.platform()),
            "kernel": platform.release(),
            "arquitetura": platform.machine(),
        },
        "python": {
            "versao": platform.python_version(),
            "implementacao": platform.python_implementation(),
            "executavel": relativo(sys.executable),
            "venv": sys.prefix != sys.base_prefix,
        },
        "pacotes": {
            name: {"versao": md.version(name), "licenca": license_of(name)}
            for name in TOP_LEVEL
        },
        "cpu": {
            "modelo": next(
                (line.split(":", 1)[1].strip() for line in Path("/proc/cpuinfo").read_text().splitlines()
                 if line.startswith("model name")),
                platform.processor(),
            ),
            "logicos": str(len(Path("/proc/cpuinfo").read_text().split("processor\t")) - 1),
        },
        "disco_gib": {
            "total": round(disk.total / 2**30, 1),
            "livre": round(disk.free / 2**30, 1),
        },
        "gpu": nvidia_smi(),
        "pico_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    meminfo = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        key, value = line.split(":", 1)
        meminfo[key] = int(value.split()[0])
    data["memoria_gib"] = {
        "total": round(meminfo["MemTotal"] / 2**20, 1),
        "disponivel": round(meminfo["MemAvailable"] / 2**20, 1),
    }
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", default=None)
    args = parser.parse_args()
    started = time.perf_counter()
    data = collect()
    data["cuda_op"] = cuda_op()
    data["tempo_s"] = round(time.perf_counter() - started, 2)
    data["pico_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    payload = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
    if args.json_out:
        Path(args.json_out).write_text(payload + "\n", encoding="utf-8")
    print(payload)
    if not data["cuda_op"].get("cuda_available") or not data["cuda_op"].get("matmul_finito"):
        print("FALHA: operação CUDA mínima não passou", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
