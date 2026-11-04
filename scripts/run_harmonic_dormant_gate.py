#!/usr/bin/env python3
"""Replay exact 16-state dormant-gate experiment and export JSON receipt."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from HarmonicConsciousness.dormant_gate import run_adversary  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20261027)
    parser.add_argument("--trials", type=int, default=24)
    parser.add_argument("--length", type=int, default=256)
    parser.add_argument("--delay", type=int, default=12)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    receipt = run_adversary(seed=args.seed, trials=args.trials,
                            length=args.length, delay=args.delay)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"seed": args.seed, "trials": args.trials,
                      "diagnostics": receipt["diagnostics"]}, sort_keys=True))


if __name__ == "__main__":
    main()
