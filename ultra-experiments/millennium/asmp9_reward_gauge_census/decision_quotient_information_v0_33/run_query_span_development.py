from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Sequence

try:
    from .asmp9_native_fixture import load_native_sources
    from .query_span import identity_rows, query_span_certificate
    from .robust_probe_design import (
        minimum_linf_factorized_probe_design,
    )
    from .semantic_coupling import (
        coupling_quotient,
        factorized_probe_design,
    )
except ImportError:
    from asmp9_native_fixture import (  # type: ignore[no-redef]
        load_native_sources,
    )
    from query_span import (  # type: ignore[no-redef]
        identity_rows,
        query_span_certificate,
    )
    from robust_probe_design import (  # type: ignore[no-redef]
        minimum_linf_factorized_probe_design,
    )
    from semantic_coupling import (  # type: ignore[no-redef]
        coupling_quotient,
        factorized_probe_design,
    )


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def nonzero_vector_entries(values: Sequence[Fraction]) -> list[dict]:
    return [
        {"index": index, "value": fraction_text(value)}
        for index, value in enumerate(values)
        if value
    ]


def failure_record(certificate) -> dict[str, object]:
    if certificate.spans_decision_quotient:
        raise ValueError("failure record requires a failing certificate")
    return {
        "query_rank": certificate.query_rank,
        "accessible_decision_dimensions": (
            certificate.accessible_decision_dimensions
        ),
        "missing_decision_dimensions": (
            certificate.missing_decision_dimensions
        ),
        "invisible_witness_nonzero_entries": nonzero_vector_entries(
            certificate.invisible_witness
        ),
        "query_effect_is_zero": not any(
            certificate.witness_query_effect
        ),
        "decision_effect_nonzero_entries": nonzero_vector_entries(
            certificate.witness_decision_effect
        ),
    }


def build_report() -> dict[str, object]:
    sources = load_native_sources()
    quotient = coupling_quotient(
        sources.v031_analysis_map,
        sources.v031_policies,
        sources.v032_semantic_operator,
    )
    greedy = factorized_probe_design(
        sources.v031_analysis_map,
        sources.v031_policies,
        sources.v032_semantic_operator,
    )
    greedy_certificate = query_span_certificate(
        quotient.canonical_operator,
        greedy.probe_operator,
    )
    robust = minimum_linf_factorized_probe_design(
        sources.v031_analysis_map,
        sources.v031_policies,
        sources.v032_semantic_operator,
    )
    robust_certificate = query_span_certificate(
        quotient.canonical_operator,
        robust.probe_operator,
    )

    leave_one_out = []
    for omitted in range(len(robust.probe_operator)):
        reduced = tuple(
            row
            for index, row in enumerate(robust.probe_operator)
            if index != omitted
        )
        leave_one_out.append(
            query_span_certificate(
                quotient.canonical_operator,
                reduced,
            )
        )

    entrywise_leave_one_out = []
    for omitted in range(quotient.coupling_dimension):
        retained = tuple(
            index
            for index in range(quotient.coupling_dimension)
            if index != omitted
        )
        entrywise_leave_one_out.append(
            query_span_certificate(
                quotient.canonical_operator,
                identity_rows(quotient.coupling_dimension, retained),
            )
        )

    diagonal = tuple(
        robust.probe_operator[index]
        for index in (0, 4, 8, 9, 13, 17)
    )
    diagonal_certificate = query_span_certificate(
        quotient.canonical_operator,
        diagonal,
    )

    if not all(
        not certificate.spans_decision_quotient
        and certificate.missing_decision_dimensions == 1
        for certificate in leave_one_out
    ):
        raise RuntimeError("factorized leave-one-out control failed")
    if not all(
        not certificate.spans_decision_quotient
        and certificate.missing_decision_dimensions == 1
        for certificate in entrywise_leave_one_out
    ):
        raise RuntimeError("entrywise leave-one-out control failed")

    robust_rows = [
        cell * 5 + policy
        for cell in robust.cell_basis_indices
        for policy in robust.policy_contrast_basis_indices
    ]
    return {
        "claim_status": "development_only_unregistered",
        "source_hashes": sources.source_hashes,
        "target": {
            "coupling_dimension": quotient.coupling_dimension,
            "decision_quotient_dimension": quotient.decision_rank,
        },
        "passing_grammars": {
            "greedy_factorized": {
                "query_count": len(greedy.probe_operator),
                "query_rank": greedy_certificate.query_rank,
                "spans": greedy_certificate.spans_decision_quotient,
                "worst_case_linf_amplification": fraction_text(
                    greedy_certificate.worst_case_linf_amplification
                ),
            },
            "minimum_linf_factorized": {
                "query_count": len(robust.probe_operator),
                "query_rank": robust_certificate.query_rank,
                "spans": robust_certificate.spans_decision_quotient,
                "policy_basis_candidates": (
                    robust.policy_basis_candidates
                ),
                "cell_basis_candidates": robust.cell_basis_candidates,
                "policy_contrast_basis_indices": list(
                    robust.policy_contrast_basis_indices
                ),
                "behavioral_cell_basis_indices": list(
                    robust.cell_basis_indices
                ),
                "canonical_row_indices": robust_rows,
                "policy_linf_amplification": fraction_text(
                    robust.policy_amplification
                ),
                "cell_linf_amplification": fraction_text(
                    robust.cell_amplification
                ),
                "worst_case_linf_amplification": fraction_text(
                    robust.combined_amplification
                ),
            },
        },
        "failing_controls": {
            "factorized_leave_one_out": {
                "failures": len(leave_one_out),
                "attempts": len(leave_one_out),
                "missing_dimensions_each": 1,
                "representative": failure_record(leave_one_out[0]),
            },
            "entrywise_leave_one_out": {
                "failures": len(entrywise_leave_one_out),
                "attempts": len(entrywise_leave_one_out),
                "missing_dimensions_each": 1,
                "representative": failure_record(
                    entrywise_leave_one_out[0]
                ),
            },
            "six_diagonal_composites": failure_record(
                diagonal_certificate
            ),
        },
        "deterministic_error_bound": (
            "if every selected probe error is at most epsilon in absolute "
            "value, every reconstructed decision-effect error is at most "
            "8*epsilon"
        ),
        "claim_boundary": {
            "physical_probe_implementation_validated": False,
            "measurement_error_bound_estimated": False,
            "registered_or_claim_eligible": False,
            "resolves_asmp9": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the exact ASMP-9 query-span certificate."
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
