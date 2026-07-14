from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.discovery import DiscoveryConfig, evaluate_discovery, write_result
from rsi_topology.synthetic import build_sparse_fixture


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a larger sparse spectral-bundle control.")
    parser.add_argument("--out-dir", type=Path, default=Path("artifacts/sparse_bundle_control"))
    parser.add_argument("--dimension", type=int, default=384)
    parser.add_argument("--planted-rank", type=int, default=32)
    parser.add_argument("--contexts", type=int, default=8)
    parser.add_argument("--candidates-per-context", type=int, default=96)
    parser.add_argument("--chunk-rows", type=int, default=64)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    config = DiscoveryConfig(
        minimum_consensus_rank=min(8, args.planted_rank),
        maximum_consensus_rank=max(32, args.planted_rank + 8),
        chunk_rows=args.chunk_rows,
    )
    stable = build_sparse_fixture(
        dimension=args.dimension,
        planted_rank=args.planted_rank,
        contexts=args.contexts,
        candidates_per_context=args.candidates_per_context,
    )
    stable_result = evaluate_discovery(
        laplacians=stable.laplacians,
        vectors=stable.vectors,
        baseline_covariates=stable.baseline_covariates,
        outcomes=stable.outcomes,
        groups=stable.groups,
        config=config,
    )
    write_result(args.out_dir / "stable_result.json", stable_result, config)
    shuffled = build_sparse_fixture(
        dimension=args.dimension,
        planted_rank=args.planted_rank,
        contexts=args.contexts,
        candidates_per_context=args.candidates_per_context,
        shuffle_low_space=True,
    )
    shuffled_result = evaluate_discovery(
        laplacians=shuffled.laplacians,
        vectors=shuffled.vectors,
        baseline_covariates=shuffled.baseline_covariates,
        outcomes=shuffled.outcomes,
        groups=shuffled.groups,
        config=config,
    )
    write_result(args.out_dir / "shuffled_transport_result.json", shuffled_result, config)
    summary = {
        "status": "completed_sparse_control",
        "configuration": {
            "dimension": args.dimension,
            "planted_rank": args.planted_rank,
            "contexts": args.contexts,
            "candidates_per_context": args.candidates_per_context,
            "chunk_rows": args.chunk_rows,
        },
        "stable": {
            "geometry": stable_result.geometry,
            "policy_passed": stable_result.policy["passed"],
            "direct_edit_passed": stable_result.direct_edit["passed"],
        },
        "shuffled_transport": {
            "geometry": shuffled_result.geometry,
            "policy_status": shuffled_result.policy.get("status"),
            "direct_edit_status": shuffled_result.direct_edit.get("status"),
        },
        "steps_completed": 2,
        "checkpoints": ["stable_result.json", "shuffled_transport_result.json"],
        "claim_boundary": stable_result.claim_boundary,
    }
    (args.out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

