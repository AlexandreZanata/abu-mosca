#!/usr/bin/env python3
"""Firewall do alvo: barreiras de runtime, scanner e inventário selado (R05).

Regras: o executor nunca lê `data/sealed/` (firewall-allow nos literais deste
módulo). O firewall é defensivo: instala uma trilha de auditoria de abertura e
listagem, oferece abertura guardada, filtro de log e inventário que expõe
apenas hashes dos labels — nunca o conteúdo.
"""

import argparse
import hashlib
import json
import logging
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEALED_ROOT = ROOT / "data" / "sealed"  # firewall-allow: raiz vigiada
FORBIDDEN_PATH_TOKENS = (
    "data/sealed",  # firewall-allow
    "data\\sealed",  # firewall-allow
    "target-labels",  # firewall-allow
)
SCAN_SUFFIXES = (".py", ".json", ".yaml", ".yml", ".sh")
_SCAN_ROOTS = (ROOT / "tools", ROOT / "configs", ROOT / "environment")
_SCAN_EXEMPT = {ROOT / "tools" / "firewall.py"}
_ALLOW_MARKER = "firewall-allow"
_ROOTS: tuple[Path, ...] = ()


class FirewallError(RuntimeError):
    pass


def _normalize(path) -> str:
    try:
        return os.path.realpath(os.fspath(path))
    except TypeError:
        return ""


def _under(path: str, root: Path) -> bool:
    if not path:
        return False
    root_str = os.path.realpath(root)
    return path == root_str or path.startswith(root_str + os.sep)


def _audit_hook(event: str, args: tuple) -> None:
    if event in ("open", "os.open", "os.listdir", "os.scandir") and args:
        target = _normalize(args[0])
        for root in _ROOTS:
            if _under(target, root):
                raise FirewallError(f"acesso bloqueado à zona selada: {target}")


def install_audit_firewall(roots: tuple[Path, ...] = (SEALED_ROOT,)) -> None:
    global _ROOTS
    _ROOTS = tuple(roots)
    sys.addaudithook(_audit_hook)


def guarded_open(path, mode: str = "rb", **kwargs):
    for root in (_ROOTS or (SEALED_ROOT,)):
        if _under(_normalize(path), root):
            raise FirewallError(f"abertura bloqueada à zona selada: {path}")
    return open(path, mode, **kwargs)


class FirewallLogFilter(logging.Filter):
    def __init__(self, columns: tuple[str, ...] = ()) -> None:
        super().__init__()
        self.columns = tuple(column.lower() for column in columns)

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        lowered = message.lower()
        for token in FORBIDDEN_PATH_TOKENS:
            if token in lowered:
                raise FirewallError(f"log com caminho proibido: {token}")
        for column in self.columns:
            if column in lowered:
                raise FirewallError(f"log com coluna proibida: {column}")
        return True


def redact_sealed_paths(text: str) -> str:
    for token in FORBIDDEN_PATH_TOKENS:
        text = text.replace(token, "[selado]")
    return text


def sealed_zone_inventory(root: Path = SEALED_ROOT) -> dict:
    files = []
    if Path(root).exists():
        for path in sorted(Path(root).rglob("*")):
            if path.is_file():
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                files.append(
                    {
                        "path": path.relative_to(root).as_posix(),
                        "bytes": path.stat().st_size,
                        "sha256": digest,
                    }
                )
    return {"count": len(files), "total_bytes": sum(f["bytes"] for f in files), "files": files}


def scan_forbidden_references(
    roots: tuple[Path, ...] = _SCAN_ROOTS,
    exempt: set[Path] = _SCAN_EXEMPT,
) -> list[str]:
    violations: list[str] = []
    for base in roots:
        if not Path(base).exists():
            continue
        for path in sorted(Path(base).rglob("*")):
            if not path.is_file() or path.suffix not in SCAN_SUFFIXES or path in exempt:
                continue
            for number, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                if _ALLOW_MARKER in line:
                    continue
                for token in FORBIDDEN_PATH_TOKENS:
                    if token in line:
                        try:
                            label = path.relative_to(ROOT).as_posix()
                        except ValueError:
                            label = path.as_posix()
                        violations.append(f"{label}:{number}: '{token}'")
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("scan", "inventory"))
    args = parser.parse_args()
    if args.command == "scan":
        violations = scan_forbidden_references()
        if violations:
            for violation in violations:
                print(f"FALHA: {violation}")
            return 1
        print("OK: nenhuma referência proibida em código/configs (fora das marcas permitidas)")
        return 0
    inventory = sealed_zone_inventory()
    print(json.dumps(inventory, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
