"""Shared command-line entry for the six thin experiment scripts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .common import jsonable
from .runner import run_config


def main(experiment: str, default_config: str) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=default_config)
    parser.add_argument("--output-root", default="artifacts/confinement")
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    receipt = run_config(
        Path(args.config), output_root=Path(args.output_root), workers=args.workers
    )
    if receipt["experiment"] != experiment:
        raise ValueError(
            f"entry point {experiment} cannot run config for {receipt['experiment']}"
        )
    print(json.dumps(jsonable(receipt), indent=2, sort_keys=True))
