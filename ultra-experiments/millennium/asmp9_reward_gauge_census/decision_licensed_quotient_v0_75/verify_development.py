from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

from decision_licensed_quotient import analyze_decision_licensed_quotient, matrix


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "DEVELOPMENT_VERIFICATION_v0_75.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    occupancies = matrix(((1, 0), (0, 1)))
    exact = analyze_decision_licensed_quotient(
        occupancies,
        matrix(((-1, 1),)),
        sp.zeros(1, 0),
    )
    nuisance_exact = analyze_decision_licensed_quotient(
        occupancies,
        sp.eye(2),
        matrix(((1,), (1,))),
    )
    confounded = analyze_decision_licensed_quotient(
        occupancies,
        matrix(((1, 1),)),
        sp.zeros(1, 0),
    )
    payload = {
        "status": "development_only_not_preregistered",
        "exact_contrast": exact.to_jsonable(),
        "exact_with_output_nuisance": nuisance_exact.to_jsonable(),
        "gauge_only_confounded": confounded.to_jsonable(),
        "checks": {
            "gauge_derived_as_common_mode": (
                exact.gauge_basis == matrix(((1,), (1,)))
            ),
            "contrast_exact": exact.exactly_identifies_decision_quotient,
            "output_nuisance_exact": (
                nuisance_exact.exactly_identifies_decision_quotient
            ),
            "gauge_only_channel_rejected": (
                not confounded.exactly_identifies_decision_quotient
            ),
            "non_gauge_witness_emitted": (
                confounded.non_gauge_witness is not None
                and not (
                    confounded.decision_matrix * confounded.non_gauge_witness
                ).is_zero_matrix
            ),
        },
        "claim_boundary": (
            "Finite linear policy-margin license and access composition only; "
            "no claim that the policy family or reward is morally adequate, "
            "and no ASMP-9 resolution."
        ),
        "source_hashes": {
            name: sha256(ROOT / name)
            for name in (
                "decision_licensed_quotient.py",
                "test_decision_licensed_quotient.py",
                "THEOREM_DRAFT_v0_75.md",
                "PRIOR_ART_GATE_v0_75.md",
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
