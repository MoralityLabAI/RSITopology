from __future__ import annotations

import argparse
import json
import sys
import types
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rsi_topology.discovery import DiscoveryConfig, discover_consensus_bands
from rsi_topology.jspace_bridge import load_operator_bundle, sha256_file, write_operator_bundle


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Exercise the JSpace sparse-operator bridge.")
    parser.add_argument("--jspace-root", type=Path, default=Path(r"C:\projects\VPD\JSpace"))
    parser.add_argument("--out-dir", type=Path, default=Path("artifacts/jspace_operator_bridge"))
    parser.add_argument("--dimension", type=int, default=32)
    parser.add_argument("--layers", type=int, default=6)
    parser.add_argument("--contexts", type=int, default=5)
    return parser.parse_args()


def band_summary(bands) -> dict:
    return {
        key: {
            "rank": value.rank,
            "minimum_occupancy": value.minimum_occupancy,
            "context_ranks": list(value.context_ranks),
        }
        for key, value in bands.items()
    }


def main() -> int:
    args = parse_args()
    jspace_package = args.jspace_root.resolve() / "vpd_jspace"
    # JSpace's public package initializer imports optional Qwen/Torch backends.
    # This bridge needs only the sealed sheaf/prereveal modules, so register a
    # minimal namespace package and avoid loading unrelated model runtimes.
    package = types.ModuleType("vpd_jspace")
    package.__path__ = [str(jspace_package)]
    sys.modules["vpd_jspace"] = package
    from vpd_jspace.prereveal import (
        PromptOperatorInput,
        build_weighted_prompt_operator,
        identity_naturality_squares,
    )
    from vpd_jspace.sheaf import build_residual_linear_sheaf

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20260711)
    weights = [
        0.04 * rng.normal(size=(args.dimension, args.dimension))
        / np.sqrt(args.dimension)
        for _ in range(args.layers)
    ]
    fixture = build_residual_linear_sheaf(weights)
    operators = []
    for context in range(args.contexts):
        edge_defects = {
            edge.edge_id: 0.04 + 0.01 * rng.random() for edge in fixture.sheaf.edges
        }
        item = PromptOperatorInput(
            prompt_id=f"bridge-context-{context:02d}",
            norm=0.5,
            sheaf=fixture.sheaf,
            edge_defects=edge_defects,
            naturality_squares=identity_naturality_squares(fixture.sheaf),
        )
        operators.append(
            build_weighted_prompt_operator(
                item,
                sigma=0.25,
                lanczos_seed=20260711 + context,
                lanczos_tolerance=1e-6,
            )
        )
    bundle_path = args.out_dir / "jspace_operator_bundle.npz"
    candidate_sites = list(fixture.hidden_vertex_ids[1:-1])
    if not candidate_sites:
        candidate_sites = [fixture.output_vertex_id]
    manifest = write_operator_bundle(
        bundle_path,
        operators,
        candidate_sites=candidate_sites,
        source_protocol_path=args.jspace_root
        / "protocols"
        / "real_model_sheaf_diagnostic_v1.json",
    )
    _, laplacians = load_operator_bundle(
        bundle_path, expected_sha256=sha256_file(bundle_path)
    )
    config = DiscoveryConfig(
        minimum_consensus_rank=min(8, args.dimension),
        maximum_consensus_rank=max(8, min(32, args.dimension)),
    )
    stable = discover_consensus_bands(laplacians, config)
    shuffled = {}
    for index, (key, matrix) in enumerate(laplacians.items()):
        permutation = np.random.default_rng(1000 + index).permutation(matrix.shape[0])
        shuffled[key] = matrix[permutation][:, permutation]
    shuffled_bands = discover_consensus_bands(shuffled, config)
    summary = {
        "status": "completed_outcome_free_bridge_control",
        "bundle_sha256": sha256_file(bundle_path),
        "manifest": manifest,
        "stable_bands": band_summary(stable),
        "shuffled_transport_bands": band_summary(shuffled_bands),
        "stable_geometry_passed": stable["low"].rank >= config.minimum_consensus_rank,
        "shuffled_geometry_passed": shuffled_bands["low"].rank
        >= config.minimum_consensus_rank,
        "outcomes_accessed": False,
        "claim_boundary": "JSpace serialization and common-space control only; no real-model or self-improvement claim.",
        "steps_completed": 2,
        "checkpoints": [str(bundle_path)],
    }
    (args.out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
