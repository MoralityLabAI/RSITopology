"""Resume v0.4 after heartbeat refresh and exact RNG-state device repair."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


def output_dir_from_argv(argv: list[str]) -> Path:
    return Path(argv[argv.index("--output-dir") + 1]).resolve()


def cpu_rng_state(state: Any) -> Any:
    """Return the same RNG bytes on CPU, as required by PyTorch setters."""
    return state.cpu()


def main() -> int:
    output_dir = output_dir_from_argv(sys.argv[1:])
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "events.jsonl").touch(exist_ok=True)

    import torch
    import train_liveness_pilot_v0_4

    original_set_rng_state = torch.set_rng_state
    original_set_cuda_rng_state_all = torch.cuda.set_rng_state_all

    def set_cpu_rng_state(state: Any) -> None:
        original_set_rng_state(cpu_rng_state(state))

    def set_cuda_rng_states(states: Any) -> None:
        original_set_cuda_rng_state_all([cpu_rng_state(state) for state in states])

    torch.set_rng_state = set_cpu_rng_state
    torch.cuda.set_rng_state_all = set_cuda_rng_states
    try:
        return train_liveness_pilot_v0_4.main()
    finally:
        torch.set_rng_state = original_set_rng_state
        torch.cuda.set_rng_state_all = original_set_cuda_rng_state_all


if __name__ == "__main__":
    raise SystemExit(main())
