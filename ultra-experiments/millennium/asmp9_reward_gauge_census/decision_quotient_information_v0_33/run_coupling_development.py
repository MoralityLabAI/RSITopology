from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Sequence

try:
    from .asmp9_native_fixture import load_native_sources
    from .semantic_coupling import (
        Matrix,
        coupling_quotient,
        decision_effect,
        independent_row_indices,
        matmul,
        nullspace_basis,
        outer,
        policy_difference_matrix,
        zeros,
    )
except ImportError:
    from asmp9_native_fixture import (  # type: ignore[no-redef]
        load_native_sources,
    )
    from semantic_coupling import (  # type: ignore[no-redef]
        Matrix,
        coupling_quotient,
        decision_effect,
        independent_row_indices,
        matmul,
        nullspace_basis,
        outer,
        policy_difference_matrix,
        zeros,
    )


HERE = Path(__file__).resolve().parent


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def shape(values: Sequence[Sequence]) -> list[int]:
    return [len(values), len(values[0])]


def nonzero_entries(values: Sequence[Sequence]) -> list[dict[str, object]]:
    return [
        {
            "row": row,
            "column": column,
            "value": fraction_text(value),
        }
        for row, values_row in enumerate(values)
        for column, value in enumerate(values_row)
        if value
    ]


def first_decision_changing_coordinate(
    analysis_map: Matrix,
    policies: Matrix,
    semantic_operator: Matrix,
) -> tuple[Matrix, Matrix]:
    rows = len(analysis_map[0])
    columns = len(semantic_operator)
    for row in range(rows):
        for column in range(columns):
            candidate = [
                [Fraction(0) for _ in range(columns)]
                for _ in range(rows)
            ]
            candidate[row][column] = 1
            effect = decision_effect(
                analysis_map,
                policies,
                candidate,
                semantic_operator,
            )
            if any(value for effect_row in effect for value in effect_row):
                return tuple(tuple(item for item in line) for line in candidate), effect
    raise RuntimeError("actual coupling operator has no decision-changing coordinate")


def build_report() -> dict[str, object]:
    sources = load_native_sources()
    quotient = coupling_quotient(
        sources.v031_analysis_map,
        sources.v031_policies,
        sources.v032_semantic_operator,
    )
    restricted = coupling_quotient(
        sources.v031_analysis_map,
        sources.v031_policies[:2],
        sources.v032_semantic_operator,
    )
    policy_analysis = matmul(
        policy_difference_matrix(sources.v031_policies),
        sources.v031_analysis_map,
    )
    policy_analysis_null = nullspace_basis(policy_analysis)
    null_coupling = outer(
        policy_analysis_null[0],
        (Fraction(1), 0, 0, 0, 0, 0),
    )
    null_effect = decision_effect(
        sources.v031_analysis_map,
        sources.v031_policies,
        null_coupling,
        sources.v032_semantic_operator,
    )
    changing_coupling, changing_effect = first_decision_changing_coordinate(
        sources.v031_analysis_map,
        sources.v031_policies,
        sources.v032_semantic_operator,
    )
    independent_rows = independent_row_indices(quotient.canonical_operator)
    if any(value for row in null_effect for value in row):
        raise RuntimeError("declared gauge witness changes a policy margin")
    if len(independent_rows) != quotient.decision_rank:
        raise RuntimeError("canonical row basis does not attain decision rank")

    return {
        "claim_status": "development_only_unregistered",
        "formula": {
            "decision_effect": "Q L K C",
            "column_major_operator": "transpose(C) kron (Q L)",
            "rank_identity": "rank(C) * rank(Q L)",
        },
        "source_hashes": sources.source_hashes,
        "actual_objects": {
            "analysis_map_shape": shape(sources.v031_analysis_map),
            "policy_matrix_shape": shape(sources.v031_policies),
            "semantic_operator_shape": shape(
                sources.v032_semantic_operator
            ),
            "coupling_shape": [
                quotient.coupling_rows,
                quotient.coupling_columns,
            ],
        },
        "full_policy_family": {
            "policy_difference_rank": quotient.policy_difference_rank,
            "policy_analysis_rank": quotient.policy_analysis_rank,
            "semantic_rank": quotient.semantic_rank,
            "raw_coupling_dimension": quotient.coupling_dimension,
            "decision_relevant_dimension": quotient.decision_rank,
            "decision_null_gauge_dimension": quotient.gauge_dimension,
            "minimum_arbitrary_scalar_linear_queries": (
                quotient.decision_rank
            ),
            "independent_canonical_row_indices": list(independent_rows),
        },
        "restricted_two_policy_control": {
            "policy_difference_rank": restricted.policy_difference_rank,
            "policy_analysis_rank": restricted.policy_analysis_rank,
            "semantic_rank": restricted.semantic_rank,
            "raw_coupling_dimension": restricted.coupling_dimension,
            "decision_relevant_dimension": restricted.decision_rank,
            "decision_null_gauge_dimension": restricted.gauge_dimension,
        },
        "witnesses": {
            "nonzero_decision_null_coupling": {
                "coupling_entries": nonzero_entries(null_coupling),
                "effect_entries": nonzero_entries(null_effect),
            },
            "decision_changing_coordinate_coupling": {
                "coupling_entries": nonzero_entries(changing_coupling),
                "effect_entries": nonzero_entries(changing_effect),
            },
        },
        "claim_boundary": {
            "identifies_physical_coupling": False,
            "proves_access_to_arbitrary_linear_queries": False,
            "registered_or_claim_eligible": False,
            "resolves_asmp9": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute the exact v0.31-v0.32 coupling quotient."
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON output path; stdout is always emitted.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = build_report()
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        output = args.output.resolve()
        if output.exists():
            raise FileExistsError(f"refusing to overwrite {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8", newline="\n")
        digest = hashlib.sha256(output.read_bytes()).hexdigest()
        print(f"wrote {output}")
        print(f"sha256 {digest}")
    print(encoded, end="")


if __name__ == "__main__":
    main()
