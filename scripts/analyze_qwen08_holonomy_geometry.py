"""Replay the preregistered Qwen3.5-0.8B pairwise identity geometry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.qwen_geometry_analysis import analyze_registered_pairs


ROOT = Path(__file__).resolve().parents[1]


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    value.add_argument(
        "--registration",
        type=Path,
        default=ROOT / "protocols" / "qwen08_holonomy_geometry_analysis_v0_1.json",
    )
    value.add_argument("--output-dir", type=Path, required=True)
    value.add_argument("--seed", type=int, default=2026071605)
    value.add_argument("--pair", nargs=2, metavar=("SOURCE", "TARGET"))
    return value


def main() -> None:
    args = parser().parse_args()
    result = analyze_registered_pairs(
        registration_path=args.registration,
        repository_root=ROOT,
        output_dir=args.output_dir,
        seed=args.seed,
        selected_pair=args.pair,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
