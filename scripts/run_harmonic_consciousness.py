"""Run the preregistered CPU-only toy comparison and save an exact JSON receipt."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from HarmonicConsciousness.benchmark import (  # noqa: E402
    DEFAULT_DELAY, DEFAULT_LENGTH, DEFAULT_SEED, DEFAULT_TRIALS, run_benchmark,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--trials", type=int, default=DEFAULT_TRIALS)
    parser.add_argument("--length", type=int, default=DEFAULT_LENGTH)
    parser.add_argument("--delay", type=int, default=DEFAULT_DELAY)
    parser.add_argument("--out", type=Path, default=Path("harmonic_consciousness_v0_1.json"))
    args = parser.parse_args()
    result = run_benchmark(seed=args.seed, trials=args.trials,
                           length=args.length, delay=args.delay)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
                        encoding="utf-8")
    print(json.dumps({"out": str(args.out), "flags": result["protocol_flags"],
                      "summary": result["summary"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
