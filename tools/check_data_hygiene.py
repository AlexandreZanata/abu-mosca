#!/usr/bin/env python3
"""Teste de sentinelas: dados, runs, selados e segredos devem ficar fora do Git."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

IGNORED_SENTINELS = (
    "data/raw/source/sentinela_fonte.feather",
    "data/raw/target-public/sentinela_alvo.parquet",
    "data/raw/spikes/sentinela_spike.npy",
    "data/sealed/target-labels/sentinela_selado.csv",  # firewall-allow
    "runs/sentinela_run/manifest.json",
    "checkpoints/sentinela.ckpt",
    "outputs/sentinela.out",
    "artifacts/frozen/sentinela.pt",
    ".env.sentinela",
    "tokens/sentinela.token",
    "segredo.token",
)
TRACKABLE_SENTINELS = (
    "data/manifests/sentinela_manifest.json",
    "artifacts/reports/sentinela_report.md",
)
TRACKABLE_EXISTING = ("data/README.md",)
LAYOUT_DIRS = (
    "data/raw/source",
    "data/raw/target-public",
    "data/raw/spikes",
    "data/manifests",
    "data/sealed/target-labels",  # firewall-allow
    "artifacts/reports",
    "artifacts/frozen",
    "runs",
    "checkpoints",
    "outputs",
)


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False
    )


def is_ignored(rel: str) -> bool:
    return git("check-ignore", "-q", rel).returncode == 0


def main() -> int:
    for rel in LAYOUT_DIRS:
        (ROOT / rel).mkdir(parents=True, exist_ok=True)
    failures: list[str] = []
    created = [ROOT / rel for rel in (*IGNORED_SENTINELS, *TRACKABLE_SENTINELS)]
    for path in created:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"sentinela de higiene de dados")
    try:
        status = git("status", "--porcelain").stdout
        for rel in IGNORED_SENTINELS:
            if not is_ignored(rel):
                failures.append(f"não ignorado pelo Git: {rel}")
            if rel in status:
                failures.append(f"apareceu em git status: {rel}")
        for rel in TRACKABLE_SENTINELS:
            if is_ignored(rel):
                failures.append(f"arquivo permitido está ignorado: {rel}")
        for rel in TRACKABLE_EXISTING:
            if not (ROOT / rel).exists():
                failures.append(f"arquivo permitido ausente: {rel}")
            elif is_ignored(rel):
                failures.append(f"arquivo permitido está ignorado: {rel}")
        for rel in LAYOUT_DIRS:
            if not (ROOT / rel).is_dir():
                failures.append(f"diretório obrigatório ausente: {rel}")
    finally:
        for path in created:
            if path.exists():
                path.unlink()
        parents = {path.parent for path in created if path.parent != ROOT}
        for directory in sorted(parents, key=lambda d: len(d.parts), reverse=True):
            rel = directory.relative_to(ROOT).as_posix()
            if rel in LAYOUT_DIRS:
                continue
            if directory.is_dir() and not any(directory.iterdir()):
                directory.rmdir()
    if failures:
        for failure in failures:
            print(f"FALHA: {failure}")
        return 1
    print(
        f"OK: {len(IGNORED_SENTINELS)} sentinelas sensíveis ignoradas, "
        f"{len(TRACKABLE_SENTINELS) + len(TRACKABLE_EXISTING)} arquivos permitidos "
        f"rastreáveis, {len(LAYOUT_DIRS)} diretórios de layout presentes, "
        f"resíduos removidos"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
