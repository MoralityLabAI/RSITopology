from __future__ import annotations

import json

try:
    from .asmp9_native_fixture import (
        native_laws_and_answers,
        query_families,
    )
    from .decision_information import (
        characteristic_design,
        decision_identifiable,
        fixed_confidence_lower_bound,
        restrict_queries,
    )
    from .semantic_coupling import coupling_quotient
except ImportError:
    from asmp9_native_fixture import (  # type: ignore[no-redef]
        native_laws_and_answers,
        query_families,
    )
    from decision_information import (  # type: ignore[no-redef]
        characteristic_design,
        decision_identifiable,
        fixed_confidence_lower_bound,
        restrict_queries,
    )
    from semantic_coupling import (  # type: ignore[no-redef]
        coupling_quotient,
    )


def main() -> None:
    laws, answers, sources = native_laws_and_answers()
    coupling = coupling_quotient(
        sources.v031_analysis_map,
        sources.v031_policies,
        sources.v032_semantic_operator,
    )
    design = characteristic_design(laws, answers, "base")
    full = characteristic_design(
        laws,
        answers,
        "base",
        distinguish_full_hypothesis=True,
    )
    families = query_families()
    family_allocations = {
        family: sum(design.allocation[query] for query in queries)
        for family, queries in families.items()
    }
    ablations = {}
    all_queries = tuple(next(iter(laws.values())))
    for family, removed in families.items():
        retained = tuple(query for query in all_queries if query not in removed)
        restricted = restrict_queries(laws, retained)
        ablated = characteristic_design(restricted, answers, "base")
        ablations[family] = {
            "decision_identifiable": decision_identifiable(
                restricted,
                answers,
            ),
            "rate": ablated.rate,
            "retained_queries": retained,
        }
    report = {
        "answers": answers,
        "channel_ablations": ablations,
        "claim_status": "development_only_unregistered",
        "decision_identifiable": decision_identifiable(laws, answers),
        "delta": 0.05,
        "family_allocations": family_allocations,
        "full_parameter_rate_with_gauge_alias": full.rate,
        "joint_allocation": design.allocation,
        "joint_allocation_unit": design.allocation_unit,
        "joint_rate": design.rate,
        "joint_sample_fraction": design.sample_fraction,
        "lower_bound_expected_queries": fixed_confidence_lower_bound(
            design,
            0.05,
        ),
        "source_hashes": sources.source_hashes,
        "semantic_coupling": {
            "v031_measurement_rows": sources.v031_measurement_rows,
            "v032_semantic_residual_rows": (
                sources.v032_semantic_residual_rows
            ),
            "raw_coupling_dimension": coupling.coupling_dimension,
            "decision_relevant_dimension": coupling.decision_rank,
            "decision_null_gauge_dimension": coupling.gauge_dimension,
            "physical_coupling_estimated": False,
            "quotient_characterized": True,
            "registered_coupling_acquisition_grammar_present": False,
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
