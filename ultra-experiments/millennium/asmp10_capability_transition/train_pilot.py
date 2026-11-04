"""Hard-capped, resumable ASMP-10 modular-addition pilot trainer."""

from __future__ import annotations

import argparse
import gc
import json
import math
import os
import random
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def append_event(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    enriched = {"ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **event}
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(enriched, sort_keys=True, allow_nan=False) + "\n")
        handle.flush()


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def modular_dataset(modulus: int, train_fraction: float, split_seed: int) -> dict[str, torch.Tensor]:
    pairs = np.asarray([(left, right) for left in range(modulus) for right in range(modulus)], dtype=np.int64)
    labels = (pairs[:, 0] + pairs[:, 1]) % modulus
    generator = np.random.default_rng(split_seed)
    order = generator.permutation(len(pairs))
    train_count = int(round(train_fraction * len(pairs)))
    train_indices = np.sort(order[:train_count])
    test_indices = np.sort(order[train_count:])
    return {
        "all_x": torch.from_numpy(pairs),
        "all_y": torch.from_numpy(labels),
        "train_x": torch.from_numpy(pairs[train_indices]),
        "train_y": torch.from_numpy(labels[train_indices]),
        "test_x": torch.from_numpy(pairs[test_indices]),
        "test_y": torch.from_numpy(labels[test_indices]),
        "train_indices": torch.from_numpy(train_indices),
        "test_indices": torch.from_numpy(test_indices),
    }


class ModularTransformer(nn.Module):
    def __init__(
        self,
        modulus: int,
        d_model: int,
        n_heads: int,
        d_mlp: int,
        n_layers: int,
        dropout: float,
    ) -> None:
        super().__init__()
        self.modulus = modulus
        self.equal_token = modulus
        self.token_embedding = nn.Embedding(modulus + 1, d_model)
        self.position_embedding = nn.Parameter(torch.zeros(3, d_model))
        layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=d_mlp,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=n_layers, enable_nested_tensor=False)
        self.final_norm = nn.LayerNorm(d_model)
        self.output = nn.Linear(d_model, modulus, bias=False)
        nn.init.normal_(self.token_embedding.weight, std=0.02)
        nn.init.normal_(self.position_embedding, std=0.02)

    def forward(self, pairs: torch.Tensor, *, return_hidden: bool = False):
        equal = torch.full((pairs.shape[0], 1), self.equal_token, dtype=pairs.dtype, device=pairs.device)
        tokens = torch.cat((pairs, equal), dim=1)
        hidden = self.token_embedding(tokens) + self.position_embedding.unsqueeze(0)
        hidden = self.encoder(hidden)
        final = self.final_norm(hidden[:, -1, :])
        logits = self.output(final)
        return (logits, final) if return_hidden else logits


@torch.no_grad()
def evaluate(model: nn.Module, x: torch.Tensor, y: torch.Tensor) -> tuple[float, float]:
    model.eval()
    logits = model(x)
    loss = nn.functional.cross_entropy(logits, y)
    accuracy = (logits.argmax(dim=-1) == y).float().mean()
    return float(loss.item()), float(accuracy.item())


def stable_rank(weight: torch.Tensor) -> float:
    matrix = weight.detach().float().cpu()
    singular_values = torch.linalg.svdvals(matrix)
    spectral_squared = float(singular_values[0].item() ** 2)
    frobenius_squared = float(torch.sum(singular_values * singular_values).item())
    return frobenius_squared / spectral_squared if spectral_squared > 0 else 0.0


@torch.no_grad()
def geometry_features(model: ModularTransformer, all_x: torch.Tensor) -> dict[str, float]:
    model.eval()
    _, hidden = model(all_x, return_hidden=True)
    centered = hidden.float() - hidden.float().mean(dim=0, keepdim=True)
    singular_values = torch.linalg.svdvals(centered.cpu())
    energy = singular_values * singular_values
    total = float(torch.sum(energy).item())
    squared_total = float(torch.sum(energy * energy).item())
    effective_rank = total * total / squared_total if squared_total > 0 else 0.0
    parameter_norm_squared = sum(float(torch.sum(parameter.detach().float() ** 2).item()) for parameter in model.parameters())
    return {
        "token_embedding_stable_rank": stable_rank(model.token_embedding.weight),
        "output_weight_stable_rank": stable_rank(model.output.weight),
        "representation_effective_rank": effective_rank,
        "parameter_l2": math.sqrt(parameter_norm_squared),
    }


def gradient_norm(model: nn.Module) -> float:
    total = 0.0
    for parameter in model.parameters():
        if parameter.grad is not None:
            total += float(torch.sum(parameter.grad.detach().float() ** 2).item())
    return math.sqrt(total)


def transition_step(metrics: list[dict[str, Any]], config: dict[str, Any]) -> int | None:
    rule = config["transition"]
    needed = int(rule["consecutive_evaluations"])
    streak = 0
    for index, record in enumerate(metrics):
        qualifies = (
            record["test_accuracy"] >= float(rule["test_accuracy_floor"])
            and record["test_loss"] <= float(rule["test_loss_ceiling"])
        )
        streak = streak + 1 if qualifies else 0
        if streak >= needed:
            return int(metrics[index - needed + 1]["step"])
    return None


def checkpoint_payload(
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    step: int,
    metrics: list[dict[str, Any]],
    geometry: dict[str, float] | None,
) -> dict[str, Any]:
    return {
        "step": step,
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
        "metrics": metrics,
        "geometry": geometry,
        "torch_rng": torch.get_rng_state(),
        "cuda_rng": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None,
        "numpy_rng": np.random.get_state(),
        "python_rng": random.getstate(),
    }


def atomic_torch_save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    torch.save(payload, temporary)
    temporary.replace(path)


def train_chunk(
    config: dict[str, Any],
    run_config: dict[str, Any],
    dataset_cpu: dict[str, torch.Tensor],
    output_dir: Path,
    events_path: Path,
) -> dict[str, Any]:
    run_id = str(run_config["run_id"])
    run_dir = output_dir / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    completed_path = run_dir / "completed.json"
    if completed_path.exists():
        return json.loads(completed_path.read_text(encoding="utf-8"))
    seed = int(run_config["seed"])
    set_seed(seed)
    device = torch.device(config["device"] if torch.cuda.is_available() else "cpu")
    model_config = config["model"]
    model = ModularTransformer(
        modulus=int(config["modulus"]),
        d_model=int(model_config["d_model"]),
        n_heads=int(model_config["n_heads"]),
        d_mlp=int(model_config["d_mlp"]),
        n_layers=int(model_config["n_layers"]),
        dropout=float(model_config["dropout"]),
    ).to(device)
    train_x = dataset_cpu["train_x"].to(device)
    train_y = dataset_cpu["train_y"].to(device)
    test_x = dataset_cpu["test_x"].to(device)
    test_y = dataset_cpu["test_y"].to(device)
    all_x = dataset_cpu["all_x"].to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(config["optimizer"]["learning_rate"]),
        betas=tuple(float(value) for value in config["optimizer"]["betas"]),
        weight_decay=float(run_config["weight_decay"]),
    )
    checkpoint_path = run_dir / "checkpoint.pt"
    metrics: list[dict[str, Any]] = []
    geometry: dict[str, float] | None = None
    start_step = 0
    if checkpoint_path.exists():
        state = torch.load(checkpoint_path, map_location=device, weights_only=False)
        model.load_state_dict(state["model"])
        optimizer.load_state_dict(state["optimizer"])
        metrics = state["metrics"]
        geometry = state["geometry"]
        start_step = int(state["step"])
        torch.set_rng_state(state["torch_rng"])
        if torch.cuda.is_available() and state["cuda_rng"] is not None:
            torch.cuda.set_rng_state_all(state["cuda_rng"])
        np.random.set_state(state["numpy_rng"])
        random.setstate(state["python_rng"])
        append_event(events_path, {"event": "resume", "run_id": run_id, "step": start_step})
    last_checkpoint_time = time.monotonic()
    total_steps = int(config["steps"])
    eval_every = int(config["eval_every_steps"])
    checkpoint_every = int(config["checkpoint_every_steps"])
    checkpoint_seconds = float(config["checkpoint_every_seconds"])
    early_feature_step = int(config["early_feature_step"])
    append_event(events_path, {"event": "chunk_start", "run_id": run_id, "seed": seed, "device": str(device)})
    try:
        for step in range(start_step + 1, total_steps + 1):
            model.train()
            optimizer.zero_grad(set_to_none=True)
            logits = model(train_x)
            loss = nn.functional.cross_entropy(logits, train_y)
            if not torch.isfinite(loss):
                raise FloatingPointError(f"nonfinite loss at step {step}")
            loss.backward()
            current_gradient_norm = gradient_norm(model)
            optimizer.step()
            if geometry is None and step >= early_feature_step:
                geometry = geometry_features(model, all_x)
                geometry["feature_step"] = step
                append_event(events_path, {"event": "geometry", "run_id": run_id, **geometry})
            if step == 1 or step % eval_every == 0 or step == total_steps:
                train_loss, train_accuracy = evaluate(model, train_x, train_y)
                test_loss, test_accuracy = evaluate(model, test_x, test_y)
                record = {
                    "step": step,
                    "train_loss": train_loss,
                    "train_accuracy": train_accuracy,
                    "test_loss": test_loss,
                    "test_accuracy": test_accuracy,
                    "gradient_norm": current_gradient_norm,
                }
                metrics.append(record)
                append_event(events_path, {"event": "evaluation", "run_id": run_id, **record})
                atomic_write(run_dir / "metrics.json", canonical_json(metrics).encode("utf-8"))
            now = time.monotonic()
            if step % checkpoint_every == 0 or now - last_checkpoint_time >= checkpoint_seconds:
                atomic_torch_save(checkpoint_path, checkpoint_payload(model, optimizer, step, metrics, geometry))
                append_event(events_path, {"event": "checkpoint", "run_id": run_id, "step": step, "path": str(checkpoint_path)})
                last_checkpoint_time = now
        result = {
            "run_id": run_id,
            "seed": seed,
            "weight_decay": float(run_config["weight_decay"]),
            "device": str(device),
            "steps_completed": total_steps,
            "transition_step": transition_step(metrics, config),
            "geometry": geometry,
            "final_metrics": metrics[-1],
            "metric_count": len(metrics),
            "status": "completed",
        }
        atomic_write(completed_path, canonical_json(result).encode("utf-8"))
        append_event(events_path, {"event": "chunk_complete", **result})
        return result
    finally:
        del optimizer, model, train_x, train_y, test_x, test_y, all_x
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.synchronize()
            torch.cuda.empty_cache()
            if hasattr(torch.cuda, "ipc_collect"):
                torch.cuda.ipc_collect()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.resolve().read_text(encoding="utf-8"))
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    events_path = output_dir / "events.jsonl"
    summary_path = output_dir / "summary.json"
    started = time.monotonic()
    status = "running"
    error = None
    results: list[dict[str, Any]] = []
    dataset_cpu = modular_dataset(
        int(config["modulus"]), float(config["train_fraction"]), int(config["split_seed"])
    )
    torch.set_num_threads(max(1, (os.cpu_count() or 2) // 2))
    append_event(events_path, {"event": "start", "task_id": config["task_id"], "pid": os.getpid()})
    try:
        for run_config in config["runs"]:
            results.append(train_chunk(config, run_config, dataset_cpu, output_dir, events_path))
        status = "completed"
        return_code = 0
    except Exception as exception:
        status = "aborted"
        error = f"{type(exception).__name__}: {exception}"
        append_event(events_path, {"event": "abort", "reason": error})
        return_code = 2
    finally:
        summary = {
            "schema_version": "asmp10_modular_transition_pilot_summary_v0_1",
            "task_id": config["task_id"],
            "status": status,
            "error": error,
            "chunks_completed": sum(result.get("status") == "completed" for result in results),
            "chunks_registered": len(config["runs"]),
            "elapsed_seconds": time.monotonic() - started,
            "results": results,
            "cuda_available": torch.cuda.is_available(),
            "cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        }
        atomic_write(summary_path, canonical_json(summary).encode("utf-8"))
        append_event(events_path, {"event": status, "summary": str(summary_path)})
        del dataset_cpu
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.synchronize()
            torch.cuda.empty_cache()
            if hasattr(torch.cuda, "ipc_collect"):
                torch.cuda.ipc_collect()
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
