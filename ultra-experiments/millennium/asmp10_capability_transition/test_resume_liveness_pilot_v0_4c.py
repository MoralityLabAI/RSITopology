from __future__ import annotations

from pathlib import Path

import torch

import resume_liveness_pilot_v0_4c as resume


def test_output_dir_parser_is_exact(tmp_path: Path) -> None:
    output = tmp_path / "artifacts"
    assert resume.output_dir_from_argv(["--output-dir", str(output)]) == output.resolve()


def test_rng_state_bytes_are_preserved_on_cpu() -> None:
    state = torch.get_rng_state()
    repaired = resume.cpu_rng_state(state)
    assert repaired.device.type == "cpu"
    assert torch.equal(repaired, state)
