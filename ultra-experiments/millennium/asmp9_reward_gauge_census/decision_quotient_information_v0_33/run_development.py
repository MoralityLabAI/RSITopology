from __future__ import annotations

import json

try:
    from .decision_information import (
        characteristic_design,
        decision_identifiable,
        fixed_confidence_lower_bound,
        restrict_queries,
        xor_channel_fixture,
    )
except ImportError:
    from decision_information import (  # type: ignore[no-redef]
        characteristic_design,
        decision_identifiable,
        fixed_confidence_lower_bound,
        restrict_queries,
        xor_channel_fixture,
    )


def main() -> None:
    laws, answers = xor_channel_fixture()
    joint = characteristic_design(laws, answers, "h00")
    full = characteristic_design(
        laws,
        answers,
        "h00",
        distinguish_full_hypothesis=True,
    )
    ablations = {}
    for query in ("behavior", "mechanics"):
        restricted = restrict_queries(laws, [query])
        design = characteristic_design(restricted, answers, "h00")
        ablations[query] = {
            "decision_identifiable": decision_identifiable(
                restricted,
                answers,
            ),
            "rate": design.rate,
        }
    result = {
        "claim_status": "development_only_unregistered",
        "decision_identifiable": decision_identifiable(laws, answers),
        "delta": 0.05,
        "full_parameter_rate_with_gauge_alias": full.rate,
        "joint_allocation": joint.allocation,
        "joint_rate": joint.rate,
        "lower_bound_expected_queries": fixed_confidence_lower_bound(
            joint,
            0.05,
        ),
        "single_channel_ablations": ablations,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
