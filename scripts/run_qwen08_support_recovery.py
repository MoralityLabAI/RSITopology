"""Run the frozen target-blind between-class sample-support diagnostic."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.qwen_support_recovery import run_support_recovery


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--protocol",
        type=Path,
        default=ROOT / "protocols" / "qwen08_between_class_support_recovery_v0_1.json",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=2026071606)
    args = parser.parse_args()
    result = run_support_recovery(
        protocol_path=args.protocol,
        repository_root=ROOT,
        output_dir=args.output_dir,
        seed=args.seed,
    )
    print(
        json.dumps(
            {
                "branch_decision": result["branch_decision"],
                "pair_decisions": result["pair_decisions"],
                "row_count": len(result["rows"]),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
