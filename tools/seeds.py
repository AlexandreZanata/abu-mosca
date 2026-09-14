#!/usr/bin/env python3
"""Seeds centralizadas: toda seed deriva do mestre + contexto (R04).

Nenhuma seed literal pode existir espalhada pelo código; qualquer componente
deve chamar `derive_seed(master, context...)`, que é determinística e
independente da máquina e do relógio.
"""

import hashlib
import struct

MAX_SEED = 2**63 - 1


def derive_seed(master: int, *context: str) -> int:
    if not isinstance(master, int) or master < 0 or master > MAX_SEED:
        raise ValueError("seed mestre deve ser inteiro entre 0 e 2^63-1")
    payload = "|".join(str(part) for part in context)
    digest = hashlib.sha256(f"{master}|{payload}".encode("utf-8")).digest()
    return struct.unpack(">Q", digest[:8])[0] % (MAX_SEED + 1)


def resolve_seeds(master: int, run_id: str, names: tuple[str, ...]) -> dict:
    return {name: derive_seed(master, run_id, name) for name in names}
