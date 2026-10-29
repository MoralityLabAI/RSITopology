from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from .asmp9_native_fixture import load_native_sources
    from .semantic_coupling import (
        factorized_probe_design,
        rational_rank,
    )
except ImportError:
    from asmp9_native_fixture import (  # type: ignore[no-redef]
        load_native_sources,
    )
    from semantic_coupling import (  # type: ignore[no-redef]
        factorized_probe_design,
        rational_rank,
    )


def build_report() -> dict[str, object]:
    sources = load_native_sources()
    design = factorized_probe_design(
        sources.v031_analysis_map,
        sources.v031_policies,
        sources.v032_semantic_operator,
    )
    probes = [
        {
            "behavioral_cell_index": cell,
            "policy_contrast_index": policy,
            "canonical_row_index": canonical,
        }
        for canonical, (cell, policy) in zip(
            design.canonical_row_indices,
            (
                (cell, policy)
                for cell in design.cell_basis_indices
                for policy in design.policy_contrast_basis_indices
            ),
            strict=True,
        )
    ]
    return {
        "claim_status": "development_only_unregistered",
        "source_hashes": sources.source_hashes,
        "candidate_composite_probe_grammar": {
            "scalar_form": (
                "selected_policy_contrast_row * K * "
                "selected_semantic_cell_column"
            ),
            "policy_contrast_basis_indices": list(
                design.policy_contrast_basis_indices
            ),
            "behavioral_cell_basis_indices": list(
                design.cell_basis_indices
            ),
            "probes": probes,
            "probe_operator_rank": rational_rank(design.probe_operator),
        },
        "access_comparison": {
            "entrywise_coupling_coordinates": 48,
            "entrywise_active_coordinates": list(
                design.active_entrywise_coordinates
            ),
            "minimum_entrywise_queries": (
                design.raw_entrywise_query_count
            ),
            "minimum_factorized_composite_queries": (
                design.scalar_composite_query_count
            ),
            "entrywise_to_composite_ratio": "8/3",
        },
        "decision_claim": {
            "composite_rows_span_full_decision_quotient": True,
            "decision_quotient_dimension": (
                design.scalar_composite_query_count
            ),
        },
        "claim_boundary": {
            "physical_interventions_implemented": False,
            "local_linearity_validated": False,
            "finite_sample_bound_proved": False,
            "registered_or_claim_eligible": False,
            "resolves_asmp9": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Construct the exact factorized v0.33 probe basis."
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    encoded = json.dumps(build_report(), indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        output = args.output.resolve()
        if output.exists():
            raise FileExistsError(f"refusing to overwrite {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8", newline="\n")
        print(f"wrote {output}")
        print(f"sha256 {hashlib.sha256(output.read_bytes()).hexdigest()}")
    print(encoded, end="")


if __name__ == "__main__":
    main()
