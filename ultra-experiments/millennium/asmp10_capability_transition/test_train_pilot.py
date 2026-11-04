from __future__ import annotations

import json
from pathlib import Path

import torch

import train_pilot
import train_pilot_gpu_guard_v0_2 as gpu_guard


HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "pilot_config_v0_1.json").read_text(encoding="utf-8"))


def test_dataset_is_complete_disjoint_and_correct() -> None:
    data = train_pilot.modular_dataset(31, 0.4, 20260720)
    assert len(data["all_x"]) == 31 * 31
    assert set(data["train_indices"].tolist()).isdisjoint(data["test_indices"].tolist())
    assert len(data["train_indices"]) + len(data["test_indices"]) == 31 * 31
    assert torch.equal(data["all_y"], (data["all_x"][:, 0] + data["all_x"][:, 1]) % 31)


def test_model_forward_and_geometry_cpu() -> None:
    model = train_pilot.ModularTransformer(11, 16, 4, 32, 1, 0.0)
    pairs = torch.tensor([[0, 0], [3, 7], [10, 10]], dtype=torch.long)
    logits = model(pairs)
    assert logits.shape == (3, 11)
    features = train_pilot.geometry_features(model, pairs)
    assert features["token_embedding_stable_rank"] > 0
    assert features["output_weight_stable_rank"] > 0
    assert features["representation_effective_rank"] > 0


def test_transition_requires_consecutive_joint_thresholds() -> None:
    config = {"transition": {"test_accuracy_floor": 0.9, "test_loss_ceiling": 0.5, "consecutive_evaluations": 3}}
    metrics = [
        {"step": 10, "test_accuracy": 0.91, "test_loss": 0.49},
        {"step": 20, "test_accuracy": 0.92, "test_loss": 0.48},
        {"step": 30, "test_accuracy": 0.89, "test_loss": 0.47},
        {"step": 40, "test_accuracy": 0.93, "test_loss": 0.46},
        {"step": 50, "test_accuracy": 0.94, "test_loss": 0.45},
        {"step": 60, "test_accuracy": 0.95, "test_loss": 0.44},
    ]
    assert train_pilot.transition_step(metrics, config) == 40


def test_two_cpu_steps_are_finite() -> None:
    train_pilot.set_seed(0)
    data = train_pilot.modular_dataset(7, 0.5, 3)
    model = train_pilot.ModularTransformer(7, 16, 4, 32, 1, 0.0)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.1)
    for _ in range(2):
        optimizer.zero_grad(set_to_none=True)
        loss = torch.nn.functional.cross_entropy(model(data["train_x"]), data["train_y"])
        assert torch.isfinite(loss)
        loss.backward()
        optimizer.step()


def test_gpu_guard_argument_parser(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    output_path = tmp_path / "output"
    config_path.write_text(json.dumps({"resource_intent": {"gpu_allowance_mb": 1000}}), encoding="utf-8")
    config, output = gpu_guard.parse_config_and_output(
        ["--config", str(config_path), "--output-dir", str(output_path)]
    )
    assert config["resource_intent"]["gpu_allowance_mb"] == 1000
    assert output == output_path.resolve()
