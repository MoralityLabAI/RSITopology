from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

from stochastic_target import (
    analyze_stochastic_interface,
    exact_binary_bayes_error,
    hellinger_mle_union_bound,
    iid_tv_misspecification_penalty,
    law,
    minimum_exact_binary_bayes_samples,
    minimum_hellinger_bound_samples,
    robustified_error_bound,
)


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "DEVELOPMENT_VERIFICATION_v0_77.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text(value) -> str:
    return str(sp.simplify(value))


def main() -> None:
    left = law(("9/10", "1/10"))
    right = law(("1/10", "9/10"))
    interface = analyze_stochastic_interface(("left", "right"), (left, right))
    alpha = sp.Rational(1, 20)
    hellinger_n = minimum_hellinger_bound_samples(
        ("left", "right"), (left, right), alpha
    )
    exact_n = minimum_exact_binary_bayes_samples(left, right, alpha)
    registered = hellinger_mle_union_bound(
        ("left", "right"), (left, right), hellinger_n
    )
    epsilon = sp.Rational(1, 1000)
    penalty = iid_tv_misspecification_penalty(epsilon, hellinger_n)
    robust = robustified_error_bound(registered, epsilon, hellinger_n)
    payload = {
        "status": "development_only_not_preregistered",
        "fixture": {
            "left": [text(value) for value in left],
            "right": [text(value) for value in right],
            "alpha": text(alpha),
            "population_status": interface.status,
            "minimum_cross_target_h2": text(
                interface.minimum_cross_target_hellinger_squared
            ),
            "hellinger_bound_minimum_samples": hellinger_n,
            "hellinger_bound_at_minimum": text(registered),
            "exact_bayes_minimum_samples": exact_n,
            "exact_bayes_error_at_minimum": text(
                exact_binary_bayes_error(left, right, exact_n)
            ),
            "per_sample_tv_stress": text(epsilon),
            "iid_tv_penalty": text(penalty),
            "robustified_bound": text(robust),
        },
        "checks": {
            "population_recoverable": bool(
                interface.population_target_recoverable
            ),
            "h2_is_two_fifths": bool(
                interface.minimum_cross_target_hellinger_squared
                == sp.Rational(2, 5)
            ),
            "hellinger_bound_threshold_is_six": bool(hellinger_n == 6),
            "exact_bayes_threshold_is_three": bool(exact_n == 3),
            "registered_bound_passes": bool(registered < alpha),
            "tv_stress_breaks_bound": bool(robust > alpha),
        },
        "claim_boundary": (
            "Finite known iid laws, a conservative Hellinger union bound, one "
            "exact binary Bayes control, and a worst-case TV stress only; no "
            "behavioral law validation or ASMP-9 resolution."
        ),
        "source_hashes": {
            name: sha256(ROOT / name)
            for name in (
                "stochastic_target.py",
                "test_stochastic_target.py",
                "THEOREM_DRAFT_v0_77.md",
                "PRIOR_ART_GATE_v0_77.md",
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
