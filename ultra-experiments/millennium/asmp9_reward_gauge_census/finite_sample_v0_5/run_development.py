from __future__ import annotations

import json
from dataclasses import asdict

from finite_sample import (
    fano_fixed_budget_lower_bound,
    logical_query_bound,
    nonadaptive_farey_lower_bound,
    repetitions_required,
    theorem_width,
)
from information_design import (
    mle_union_bound_samples,
    solve_information_design,
)


def main() -> None:
    cells = []
    for bound in range(3, 7):
        critical = theorem_width(bound)
        # Keep the LP in the finite-information interior. At eta=0, strict
        # opposite responses have disjoint support and infinite
        # Bhattacharyya information.
        for eta in (0.01, 0.1, 0.25, 0.4):
            for width in (critical - 1, critical):
                result = solve_information_design(
                    dimension=2,
                    bound=bound,
                    width=width,
                    eta=eta,
                )
                record = asdict(result)
                record["mle_union_bound_samples"] = (
                    mle_union_bound_samples(
                        result.hypothesis_count,
                        result.minimum_information,
                        0.05,
                    )
                )
                record["fano_lower_bound"] = (
                    fano_fixed_budget_lower_bound(
                        dimension=2,
                        bound=bound,
                        eta=eta,
                        alpha=0.05,
                    )
                )
                record["nonadaptive_farey_lower_bound"] = (
                    nonadaptive_farey_lower_bound(
                        bound=bound,
                        eta=eta,
                        alpha=0.05,
                    )
                )
                logical = logical_query_bound(2, bound)
                record["constructive_repetition_upper"] = (
                    logical
                    * repetitions_required(
                        eta=eta,
                        alpha=0.05,
                        logical_queries=logical,
                    )
                )
                cells.append(record)
    print(json.dumps(cells, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
