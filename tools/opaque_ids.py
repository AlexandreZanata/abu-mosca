#!/usr/bin/env python3
"""Mapeamento canônico de IDs opacos (H05).

Fonte única para todos os adapters: o corpo/ID real vira `n<16 hex>` derivado de
SHA-256 de `dataset|release|body`. O ID nunca entra como número, categoria ou
índice treinável; o mapa body→opaco existe apenas no adapter/custodiante.
"""

import hashlib

PREFIX = "n"
ID_LENGTH = 16


def opaque_node_id(dataset: str, release: str, body) -> str:
    digest = hashlib.sha256(f"{dataset}|{release}|{body}".encode()).hexdigest()
    return PREFIX + digest[:ID_LENGTH]


def body_map(dataset: str, release: str, bodies) -> dict:
    return {body: opaque_node_id(dataset, release, body) for body in bodies}
