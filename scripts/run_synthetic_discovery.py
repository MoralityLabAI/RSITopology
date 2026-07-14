from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.discovery import (
    DiscoveryConfig,
    discover_consensus_bands,
    evaluate_discovery,
    write_result,
)
from rsi_topology.synthetic import build_fixture


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run planted and null spectral-bundle controls.")
    parser.add_argument("--out-dir", type=Path, default=Path("artifacts/synthetic_discovery"))
    parser.add_argument("--seed", type=int, default=20260711)
    parser.add_argument("--contexts", type=int, default=10)
    parser.add_argument("--candidates-per-context", type=int, default=96)
    parser.add_argument("--dimension", type=int, default=48)
    parser.add_argument("--planted-rank", type=int, default=12)
    parser.add_argument("--checkpoint-interval", default="one_fixture_phase")
    parser.add_argument("--chunk-rows", type=int, default=64)
    return parser.parse_args()


def canonical_hash(payload: object) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def array_hash(value: np.ndarray) -> str:
    array = np.ascontiguousarray(value, dtype="<f8")
    return hashlib.sha256(array.tobytes()).hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def geometry_receipt(fixture, config: DiscoveryConfig) -> dict:
    bands = discover_consensus_bands(fixture.laplacians, config)
    return {
        "phase": "sealed_geometry_before_outcomes",
        "laplacian_hashes": {
            key: array_hash(value) for key, value in fixture.laplacians.items()
        },
        "candidate_vector_sha256": array_hash(fixture.vectors),
        "baseline_covariate_sha256": array_hash(fixture.baseline_covariates),
        "outcome_hash_present": False,
        "bands": {
            key: {
                "rank": band.rank,
                "basis_sha256": array_hash(band.basis),
                "occupancies": band.occupancies.tolist(),
                "context_ranks": list(band.context_ranks),
            }
            for key, band in bands.items()
        },
        "config_sha256": canonical_hash(asdict(config)),
    }


def report(signal: dict, null: dict, receipt: dict) -> str:
    return "\n".join(
        [
            "# Spectral-Bundle Discovery Control",
            "",
            "## Claim boundary",
            "",
            signal["claim_boundary"],
            "",
            "This run changes no model weights and performs no reinforcement learning. "
            "It tests the mathematical instrument on planted and outcome-null controls.",
            "",
            "## Mathematical object",
            "",
            "For each frozen Laplacian spectral band, average its prompt-specific "
            "projectors implicitly, then retain directions whose projector occupancy is "
            "at least 0.75. This is a Grassmannian consensus subspace: a high-dimensional "
            "structure stable across contexts, rather than a coordinate tuple at one site.",
            "",
            "## Geometry seal",
            "",
            "```json",
            json.dumps(receipt, indent=2, sort_keys=True),
            "```",
            "",
            "## Planted control",
            "",
            "```json",
            json.dumps(
                {
                    "geometry": signal["geometry"],
                    "policy": {k: v for k, v in signal["policy"].items() if k != "folds"},
                    "direct_edit": {
                        k: v
                        for k, v in signal["direct_edit"].items()
                        if k != "proposal_direction"
                    },
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Outcome-null control",
            "",
            "```json",
            json.dumps(
                {
                    "geometry": null["geometry"],
                    "policy": {k: v for k, v in null["policy"].items() if k != "folds"},
                    "direct_edit": {
                        k: v
                        for k, v in null["direct_edit"].items()
                        if k != "proposal_direction"
                    },
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "The geometry gate is expected to pass in both fixtures because outcomes do "
            "not define geometry. The policy and edit gates should pass only when held-out "
            "causal utility is planted; otherwise the instrument is leaking or overfitting.",
            "",
        ]
    )


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    config = DiscoveryConfig(chunk_rows=args.chunk_rows)
    signal_fixture = build_fixture(
        seed=args.seed,
        contexts=args.contexts,
        candidates_per_context=args.candidates_per_context,
        dimension=args.dimension,
        planted_rank=args.planted_rank,
        outcome_signal=True,
    )
    receipt = geometry_receipt(signal_fixture, config)
    receipt.update(
        {
            "exact_argv": [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]],
            "python": sys.version,
            "platform": platform.platform(),
            "checkpoint_interval": args.checkpoint_interval,
            "chunk_strategy": f"candidate rows in blocks of {args.chunk_rows}; mean projector is matrix-free",
        }
    )
    write_json(args.out_dir / "geometry_pre_reveal_receipt.json", receipt)
    signal = evaluate_discovery(
        laplacians=signal_fixture.laplacians,
        vectors=signal_fixture.vectors,
        baseline_covariates=signal_fixture.baseline_covariates,
        outcomes=signal_fixture.outcomes,
        groups=signal_fixture.groups,
        config=config,
    )
    write_result(args.out_dir / "planted_result.json", signal, config)

    null_fixture = build_fixture(
        seed=args.seed,
        contexts=args.contexts,
        candidates_per_context=args.candidates_per_context,
        dimension=args.dimension,
        planted_rank=args.planted_rank,
        outcome_signal=False,
    )
    null = evaluate_discovery(
        laplacians=null_fixture.laplacians,
        vectors=null_fixture.vectors,
        baseline_covariates=null_fixture.baseline_covariates,
        outcomes=null_fixture.outcomes,
        groups=null_fixture.groups,
        config=config,
    )
    write_result(args.out_dir / "null_result.json", null, config)
    report_path = Path("reports/spectral_bundle_discovery_control.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        report(asdict(signal), asdict(null), receipt), encoding="utf-8"
    )
    summary = {
        "status": "completed_synthetic_control",
        "steps_completed": 2,
        "checkpoints": [
            str(args.out_dir / "geometry_pre_reveal_receipt.json"),
            str(args.out_dir / "planted_result.json"),
            str(args.out_dir / "null_result.json"),
        ],
        "geometry_passed": signal.geometry["passed"],
        "policy_passed": signal.policy["passed"],
        "direct_edit_passed": signal.direct_edit["passed"],
        "null_policy_passed": null.policy["passed"],
        "null_direct_edit_passed": null.direct_edit["passed"],
        "peak_ram_mb": None,
        "avg_ram_mb": None,
        "peak_io_mb_s": None,
        "cpu_pct": None,
        "resource_note": "populate from capped wrapper for any model-bearing run",
        "report": str(report_path),
    }
    write_json(args.out_dir / "run_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

