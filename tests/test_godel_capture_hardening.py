from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str, relative: str):
    specification = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


RUNNER = load_script("run_godel_globes_v0_1", "scripts/run_godel_globes_v0_1.py")
CAPTURE = load_script("capture_godel_globes_qwen", "scripts/capture_godel_globes_qwen.py")


REQUIRED_CHECKS = {
    "success_path": True,
    "memory_cap_configured": True,
    "memory_probe_terminated": True,
    "memory_probe_stayed_at_cap": True,
    "cpu_cap_configured": True,
    "cpu_probe_completed": True,
    "cpu_observed_below_margin": True,
    "io_monitor_aborted": True,
    "timeout_aborted": True,
    "all_cleanup_passed": True,
}


def validation_receipt(wrapper: Path, cleanup: Path) -> dict:
    return {
        "schema_version": "qwen_holonomy_hard_cap_validation_v0_1",
        "hard_cap_validation_status": "passed",
        "wrapper": {
            "path": str(wrapper.resolve()),
            "sha256": RUNNER.sha256_file(wrapper),
        },
        "cleanup": {
            "path": str(cleanup.resolve()),
            "sha256": RUNNER.sha256_file(cleanup),
        },
        "checks": REQUIRED_CHECKS,
    }


def test_validation_receipt_binds_exact_wrapper_and_cleanup(tmp_path: Path):
    wrapper = tmp_path / "wrapper.ps1"
    cleanup = tmp_path / "cleanup.ps1"
    wrapper.write_text("wrapper-v1", encoding="utf-8")
    cleanup.write_text("cleanup-v1", encoding="utf-8")
    receipt = validation_receipt(wrapper, cleanup)

    RUNNER._validate_hard_cap_receipt(
        receipt, wrapper_path=wrapper, cleanup_path=cleanup
    )
    wrapper.write_text("wrapper-v2", encoding="utf-8")
    with pytest.raises(ValueError, match="wrapper hash mismatch"):
        RUNNER._validate_hard_cap_receipt(
            receipt, wrapper_path=wrapper, cleanup_path=cleanup
        )


def test_prepare_authorization_emits_wrapper_contract_and_ram_preflight(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    wrapper = tmp_path / "wrapper.ps1"
    cleanup = tmp_path / "cleanup.ps1"
    wrapper.write_text("wrapper", encoding="utf-8")
    cleanup.write_text("cleanup", encoding="utf-8")
    receipt_path = tmp_path / "validation.json"
    receipt_path.write_text(
        json.dumps(validation_receipt(wrapper, cleanup)), encoding="utf-8"
    )

    original_run = RUNNER.subprocess.run

    def fake_run(command, **kwargs):
        if command[1:3] == ["rev-parse", "HEAD"]:
            return SimpleNamespace(stdout="a" * 40 + "\n")
        if command[1:3] == ["status", "--porcelain"]:
            return SimpleNamespace(stdout="")
        if command[1:4] == ["branch", "-r", "--contains"]:
            return SimpleNamespace(stdout="origin/test\n")
        return original_run(command, **kwargs)

    monkeypatch.setattr(RUNNER.subprocess, "run", fake_run)
    output = tmp_path / "authorization.json"
    capture_output = tmp_path / "capture"
    args = argparse.Namespace(
        protocol=ROOT / "protocols" / "godel_globes_falsification_v0_1.json",
        prompt_manifest=ROOT / "protocols" / "godel_globes_prompt_manifest_v0_1.json",
        confirm_caps=True,
        batch_size=1,
        hard_cap_validation_receipt=receipt_path,
        hard_cap_wrapper=wrapper,
        cleanup_script=cleanup,
        memory_mb=14000,
        host_reserve_mb=2048,
        cpu_percent=50,
        io_mb_s=50,
        timeout_seconds=43200,
        gpu_allowance_mb=1,
        checkpoint_every_seconds=300,
        swap_bytes=0,
        run_id="test-godel-capture",
        capture_output_dir=capture_output,
        device="cpu",
        output=output,
    )
    RUNNER.prepare_authorization(args)
    value = json.loads(output.read_text(encoding="utf-8"))

    assert value["schema_version"] == "godel_capture_authorization_v0_1"
    assert value["resource_caps"]["minimum_free_memory_mb"] == 16048
    assert value["wrapper_output_dir"] == str((capture_output / "_wrapper").resolve())
    assert "durable_partial_group" in value["checkpoint_strategy"]
    assert value["capture_contract"]["model_surface"] == (
        "base_transformer_without_lm_head"
    )
    assert value["capture_contract"]["checkpoint_loader"] == (
        "tensorwise_safetensors_into_meta_base_model"
    )
    assert value["capture_contract"]["logits_materialized"] is False
    assert value["capture_contract"]["float32_load_strategy"] == (
        "native_tensorwise_bfloat16_then_incremental_float32_promotion"
    )
    assert value["hard_cap_validation_receipt"]["sha256"] == RUNNER.sha256_file(
        receipt_path
    )


def test_base_transformer_resolves_frozen_causallm_site_namespace():
    leaf = object()
    base_model = SimpleNamespace(
        layers=[SimpleNamespace(self_attn=SimpleNamespace(v_proj=leaf))]
    )
    assert CAPTURE._resolve_module(
        base_model, "model.layers.0.self_attn.v_proj"
    ) is leaf

    source = (ROOT / "scripts" / "capture_godel_globes_qwen.py").read_text(
        encoding="utf-8"
    )
    assert "AutoModelForCausalLM.from_pretrained" not in source
    assert "runtime_tensorwise_load_completed" in source


def test_checkpoint_key_projection_excludes_only_lm_head():
    assert CAPTURE._base_parameter_name("lm_head.weight") is None
    assert CAPTURE._base_parameter_name("model.layers.0.input_layernorm.weight") == (
        "layers.0.input_layernorm.weight"
    )
    with pytest.raises(ValueError, match="outside base model"):
        CAPTURE._base_parameter_name("unexpected.weight")


def test_installed_native_state_promotes_without_touching_integer_buffers():
    import torch

    model = torch.nn.Linear(2, 2, bias=False, dtype=torch.bfloat16)
    model.register_buffer("indices", torch.tensor([1, 2], dtype=torch.int64))
    CAPTURE._promote_floating_state_to_float32(model, torch)
    assert model.weight.dtype == torch.float32
    assert model.indices.dtype == torch.int64


def test_partial_group_checkpoint_roundtrip_and_prefix_guard(tmp_path: Path):
    sites = ["site.a", "site.b"]
    captured = {
        "site.a": [np.ones((1, 3)), np.full((1, 3), 2.0)],
        "site.b": [np.full((2, 4), 3.0)],
    }
    CAPTURE._write_partial_group(
        tmp_path,
        runtime="full_float32",
        shard="shard-00",
        half="construction",
        sites=sites,
        prompt_ids=["p0", "p1"],
        captured=captured,
    )
    count, restored = CAPTURE._load_partial_group(
        tmp_path,
        runtime="full_float32",
        shard="shard-00",
        half="construction",
        sites=sites,
        expected_prompt_ids=["p0", "p1", "p2"],
    )
    assert count == 2
    assert np.array_equal(restored["site.a"], np.array([[1, 1, 1], [2, 2, 2]]))
    assert np.array_equal(restored["site.b"], np.full((2, 4), 3.0))

    _, metadata_path = CAPTURE._partial_group_paths(
        tmp_path,
        runtime="full_float32",
        shard="shard-00",
        half="construction",
    )
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["prompt_ids"] = ["wrong", "p1"]
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    with pytest.raises(ValueError, match="prompt prefix mismatch"):
        CAPTURE._load_partial_group(
            tmp_path,
            runtime="full_float32",
            shard="shard-00",
            half="construction",
            sites=sites,
            expected_prompt_ids=["p0", "p1", "p2"],
        )


def test_wrapper_declares_godel_schema_ram_preflight_and_checkpoint_watchdog():
    wrapper = (ROOT / "scripts" / "run_qwen_holonomy_jobobject.ps1").read_text(
        encoding="utf-8"
    )
    assert '"godel_capture_authorization_v0_1"' in wrapper
    assert "minimum_free_memory_mb" in wrapper
    assert '"checkpoint_stale"' in wrapper
    assert "does not bind the executing wrapper" in wrapper
