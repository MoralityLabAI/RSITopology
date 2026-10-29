from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

from coordinate_metric import (
    canonical_fixture,
    exact_metric_optimum,
    functional_risk,
    quadratic_risk,
    rational_matrix,
    reframe_functional,
    reframe_information,
    reframe_loss_metric,
)


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "DEVELOPMENT_VERIFICATION_v0_70_1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    rows, information = canonical_fixture()
    transform = rational_matrix([[2, 1], [0, 1]])
    metric = rational_matrix([[2, 0], [0, 3]])
    functional = rational_matrix([[1], [-1]])

    metric_original = quadratic_risk(information, metric)
    metric_reframed = quadratic_risk(
        reframe_information(information, transform),
        reframe_loss_metric(metric, transform),
    )
    functional_original = functional_risk(information, functional)
    functional_reframed = functional_risk(
        reframe_information(information, transform),
        reframe_functional(functional, transform),
    )
    silent_reset_original = quadratic_risk(information, sp.eye(2))
    silent_reset_reframed = quadratic_risk(
        reframe_information(information, transform), sp.eye(2)
    )

    isotropic = exact_metric_optimum(rows, 12, sp.eye(2))
    first_heavy = exact_metric_optimum(
        rows, 12, rational_matrix([[100, 0], [0, 1]])
    )
    second_heavy = exact_metric_optimum(
        rows, 12, rational_matrix([[1, 0], [0, 100]])
    )

    payload = {
        "status": "development_only_additive_scope_correction",
        "coordinate_map": [["2", "1"], ["0", "1"]],
        "metric_risk": {
            "original": str(metric_original),
            "reframed_with_transported_metric": str(metric_reframed),
        },
        "functional_risk": {
            "original": str(functional_original),
            "reframed_with_transported_covector": str(functional_reframed),
        },
        "silent_identity_reset": {
            "original": str(silent_reset_original),
            "reframed": str(silent_reset_reframed),
        },
        "allocation_controls": {
            "identity_metric": {
                "risk": str(isotropic.risk),
                "allocations": [list(row) for row in isotropic.allocations],
            },
            "first_coordinate_weight_100": {
                "risk": str(first_heavy.risk),
                "allocations": [list(row) for row in first_heavy.allocations],
            },
            "second_coordinate_weight_100": {
                "risk": str(second_heavy.risk),
                "allocations": [list(row) for row in second_heavy.allocations],
            },
        },
        "checks": {
            "transported_metric_risk_is_invariant": (
                metric_original == metric_reframed
            ),
            "transported_functional_risk_is_invariant": (
                functional_original == functional_reframed
            ),
            "silent_identity_reset_changes_loss": (
                silent_reset_original != silent_reset_reframed
            ),
            "metric_changes_allocation": (
                isotropic.allocations != first_heavy.allocations
                and isotropic.allocations != second_heavy.allocations
            ),
        },
        "claim_boundary": (
            "Additive coordinate-fidelity correction to development-only "
            "v0.70. It does not validate a quotient metric, physical channel, "
            "value object, or ASMP-9 resolution."
        ),
        "source_hashes": {
            name: sha256(ROOT / name)
            for name in (
                "coordinate_metric.py",
                "test_coordinate_metric.py",
                "AMENDMENT_v0_70_1.md",
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
