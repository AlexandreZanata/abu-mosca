#!/usr/bin/env python3
"""Decoder de pares de embeddings e loss masked-edge/weight (M01).

Duas cabeças bilineares sobre pares de embeddings — existência e peso — sem
nenhum parâmetro indexado por node ID. A transformação de peso é log1p e a
loss combina BCE de existência com MSE de log1p(peso). Módulo separado porque
depende de torch, que não é necessário para validar o restante da tarefa.
"""

import numpy as np
import torch

LAMBDA_WEIGHT = 1.0
DECODER_DIM = 16
PER_NODE_PARAMETERS = 0


class BilinearDecoder(torch.nn.Module):
    """Duas cabeças bilineares sobre pares de embeddings; nenhum parâmetro por node ID."""

    def __init__(self, dim: int):
        super().__init__()
        self.existence = torch.nn.Parameter(torch.empty(dim, dim))
        self.weight = torch.nn.Parameter(torch.empty(dim, dim))
        self.bias_existence = torch.nn.Parameter(torch.zeros(1))
        self.bias_weight = torch.nn.Parameter(torch.zeros(1))
        torch.nn.init.xavier_uniform_(self.existence)
        torch.nn.init.xavier_uniform_(self.weight)

    def forward(self, left: torch.Tensor, right: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        existence_logit = (left @ self.existence * right).sum(dim=1) + self.bias_existence
        weight_prediction = (left @ self.weight * right).sum(dim=1) + self.bias_weight
        return existence_logit, weight_prediction


def masked_edge_weight_loss(
    decoder: BilinearDecoder,
    positive_left: torch.Tensor,
    positive_right: torch.Tensor,
    positive_weight: torch.Tensor,
    negative_left: torch.Tensor,
    negative_right: torch.Tensor,
    lambda_weight: float = LAMBDA_WEIGHT,
) -> dict:
    pos_logit, pos_weight_pred = decoder(positive_left, positive_right)
    neg_logit, _ = decoder(negative_left, negative_right)
    existence = torch.nn.functional.binary_cross_entropy_with_logits(
        torch.cat([pos_logit, neg_logit]), torch.cat([torch.ones_like(pos_logit), torch.zeros_like(neg_logit)])
    )
    weight_loss = torch.nn.functional.mse_loss(pos_weight_pred, torch.log1p(positive_weight))
    total = existence + lambda_weight * weight_loss
    return {"loss": total, "existence": existence, "weight": weight_loss}


def decoder_smoke(dim: int = DECODER_DIM, steps: int = 60, seed: int = 0) -> dict:
    torch.manual_seed(seed)
    torch.set_num_threads(1)
    decoder = BilinearDecoder(dim)
    rng = np.random.RandomState(seed % (2**32))
    positive_left = torch.from_numpy(rng.randn(16, dim).astype(np.float32))
    positive_right = torch.from_numpy(rng.randn(16, dim).astype(np.float32))
    positive_weight = torch.from_numpy(np.abs(rng.randn(16)).astype(np.float32))
    negative_left = torch.from_numpy(rng.randn(16, dim).astype(np.float32))
    negative_right = torch.from_numpy(rng.randn(16, dim).astype(np.float32))
    optimizer = torch.optim.Adam(decoder.parameters(), lr=5e-2)
    first = None
    last = None
    for _ in range(steps):
        optimizer.zero_grad()
        parts = masked_edge_weight_loss(decoder, positive_left, positive_right, positive_weight, negative_left, negative_right)
        parts["loss"].backward()
        optimizer.step()
        value = float(parts["loss"].detach())
        first = value if first is None else first
        last = value
    gradients_finite = all(bool(torch.isfinite(p.grad).all().item()) for p in decoder.parameters() if p.grad is not None)
    return {
        "parameters": int(sum(p.numel() for p in decoder.parameters())),
        "per_node_parameters": PER_NODE_PARAMETERS,
        "gradients_finite": gradients_finite,
        "loss_first": round(float(first), 6),
        "loss_last": round(float(last), 6),
        "loss_decreased": bool(last < first),
        "steps": steps,
    }
