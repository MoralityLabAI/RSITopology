#!/usr/bin/env python3
"""Reproducible, harmless successor-inheritance benchmark runner."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rsi_topology.successor_inheritance import run_sweep  # noqa: E402


def parse_grid(value: str) -> tuple[int, ...]:
    result = tuple(int(piece.strip()) for piece in value.split(","))
    if not result or any(x < 1 for x in result):
        raise argparse.ArgumentTypeError("expected positive comma-separated integers")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path,
                        default=ROOT / "protocols/successor_inheritance_v1.json")
    parser.add_argument("--bits", type=parse_grid)
    parser.add_argument("--depths", type=parse_grid)
    parser.add_argument("--trials", type=int)
    parser.add_argument("--budget", type=int)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--semantic", action="store_true",
                        help="Add paired artifact-reading checks without changing probes or repairs")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--summary-out", type=Path)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    if (protocol["historical_contexts"] != [0, 1, 2, 3]
            or protocol["successor_generations"] != 3
            or protocol["status"] != "synthetic_model_free"):
        parser.error("v1 requires history [0,1,2,3], three generations, and synthetic_model_free")
    rows, report = run_sweep(
        args.bits if args.bits is not None else tuple(protocol["context_bits"]),
        args.depths if args.depths is not None else tuple(protocol["adaptive_depths"]),
        args.trials if args.trials is not None else protocol["trials_per_cell"],
        args.budget if args.budget is not None else protocol["random_probe_budget"],
        args.seed if args.seed is not None else protocol["seed"],
        include_semantic=args.semantic,
    )
    prefix = "semantic_v1" if args.semantic else "v1"
    out = args.out or Path(f"artifacts/successor_inheritance/{prefix}_trials.jsonl")
    summary_out = args.summary_out or Path(f"artifacts/successor_inheritance/{prefix}_summary.json")
    if out.resolve() == summary_out.resolve():
        parser.error("trial and summary outputs must differ")
    payloads = [(out, "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)),
                (summary_out, json.dumps(report, indent=2, sort_keys=True) + "\n")]
    for path, payload in payloads:
        if path.exists() and path.read_bytes() != payload.encode("utf-8"):
            raise FileExistsError(f"refusing to overwrite a different receipt: {path}")
    for path, payload in payloads:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload.encode("utf-8"))
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
