from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

from gaussian_quotient import (
    canonical_fixture,
    exact_allocation_optimum,
    information_matrix,
    parameter_minimax_risk,
    rational_matrix,
    two_policy_plugin_error,
    worst_vertex_bias_mse,
)


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "DEVELOPMENT_VERIFICATION_v0_70.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    rows, variances = canonical_fixture()
    parameter = exact_allocation_optimum(rows, variances, 12)
    policy = exact_allocation_optimum(
        rows,
        variances,
        12,
        functional=rational_matrix([[1], [0]]),
    )
    singular = information_matrix(rows, variances, (12, 0, 0))
    parameter_information = information_matrix(
        rows, variances, parameter.allocations[0]
    )
    policy_tail = two_policy_plugin_error(
        1.0, float(policy.objective)
    )
    bias_audit = worst_vertex_bias_mse(
        rows,
        variances,
        parameter.allocations[0],
        (sp.Rational(1, 20),) * 3,
    )

    payload = {
        "status": "development_only_not_preregistered",
        "theorem_object": "finite Gaussian representative-insensitive quotient",
        "query_rows": [list(map(int, rows.row(i))) for i in range(rows.rows)],
        "variances": [str(value) for value in variances],
        "total_samples": 12,
        "parameter_optimum": parameter.to_jsonable(),
        "policy_functional": ["1", "0"],
        "policy_optimum": policy.to_jsonable(),
        "singular_control": {
            "allocation": [12, 0, 0],
            "information_rank": singular.rank(),
            "parameter_minimax_risk": str(
                parameter_minimax_risk(singular)
            ),
        },
        "parameter_information": [
            [str(parameter_information[i, j]) for j in range(2)]
            for i in range(2)
        ],
        "policy_tail_at_unit_margin": policy_tail,
        "rectangular_bias_audit": bias_audit,
        "checks": {
            "parameter_optimum_is_5_5_2": (
                parameter.allocations == ((5, 5, 2),)
            ),
            "parameter_minimax_risk_is_14_over_45": (
                parameter.objective == sp.Rational(14, 45)
            ),
            "policy_optima_are_decision_directed": (
                set(policy.allocations) == {(11, 0, 1), (11, 1, 0)}
            ),
            "policy_variance_is_1_over_11": (
                policy.objective == sp.Rational(1, 11)
            ),
            "singular_control_is_unidentified": singular.rank() < rows.cols,
            "all_91_integer_allocations_enumerated": (
                parameter.evaluated_allocations == 91
            ),
            "all_8_bias_vertices_enumerated": (
                bias_audit["vertex_count"] == 8
            ),
        },
        "claim_boundary": (
            "Classical exact Gaussian linear-model specialization after the "
            "v0.69 quotient. No physical channel validation, adaptive minimax "
            "theorem, strategic robustness, human value claim, or ASMP-9 "
            "resolution is established."
        ),
        "source_hashes": {
            name: sha256(ROOT / name)
            for name in (
                "gaussian_quotient.py",
                "test_gaussian_quotient.py",
                "THEOREM_DRAFT_v0_70.md",
                "PRIOR_ART_GATE_v0_70.md",
            )
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload["checks"], sort_keys=True))


if __name__ == "__main__":
    main()
