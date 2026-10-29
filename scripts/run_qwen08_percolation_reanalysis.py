"""Run the frozen retrospective Qwen0.8B percolation analysis."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

for name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(name, "1")
os.environ["CUDA_VISIBLE_DEVICES"] = ""
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.confinement_experiments.common import (
    canonical_json_bytes,
    write_bytes_compare_or_fail,
)
from rsi_topology.qwen_percolation_reanalysis import run_reanalysis


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--protocol",
        type=Path,
        default=ROOT / "protocols" / "qwen08_percolation_reanalysis_v0_1.json",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_reanalysis(args.protocol)
    write_bytes_compare_or_fail(args.output, canonical_json_bytes(result))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
