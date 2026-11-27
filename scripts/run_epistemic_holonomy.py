"""Deterministic, CPU-only EH-01 synthetic study. Outputs JSON receipts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.epistemic_holonomy.model import echo_metrics, fresh_metrics, paired_trial, corrected_echo_graph, hodge_receipt  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reliability", type=float, default=0.6)
    parser.add_argument("--counts", type=int, nargs="+", default=[1, 2, 4, 8, 10, 16, 32])
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument("--trials", type=int, default=20000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if any(n < 1 for n in args.counts):
        parser.error("counts must be positive")
    report = {
        "study": "EH-01: provenance-marked epistemic holonomy",
        "status": "synthetic_only",
        "hypothesis_model": "uniform binary H; one noisy binary X; echoed replicas share source X",
        "reliability": args.reliability,
        "rows": [
            {
                "total_signals": n,
                "echo": echo_metrics(n, args.reliability),
                "corrected_echo_hodge": hodge_receipt(*corrected_echo_graph(n, args.reliability)),
                "independent": fresh_metrics(n, args.reliability),
            }
            for n in args.counts
        ],
        "paired_trials": paired_trial(max(args.counts), args.reliability, seed=args.seed, trials=args.trials),
        "claims": {
            "holonomy": "cycle inconsistencies relative to a provenance-marked graph; not truth",
            "mutual_information": "unchanged by copied observations via data processing",
            "indistinguishability": "identical transcript distributions cannot reveal differing external labels",
        },
    }
    rendered = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(args.output)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
