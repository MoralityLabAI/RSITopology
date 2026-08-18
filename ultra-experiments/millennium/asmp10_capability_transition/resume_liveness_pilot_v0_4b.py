"""Refresh the existing event-file heartbeat, then run the sealed v0.4 pilot."""

from __future__ import annotations

import sys
from pathlib import Path


def output_dir_from_argv(argv: list[str]) -> Path:
    return Path(argv[argv.index("--output-dir") + 1]).resolve()


def main() -> int:
    output_dir = output_dir_from_argv(sys.argv[1:])
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "events.jsonl").touch(exist_ok=True)
    import train_liveness_pilot_v0_4

    return train_liveness_pilot_v0_4.main()


if __name__ == "__main__":
    raise SystemExit(main())
