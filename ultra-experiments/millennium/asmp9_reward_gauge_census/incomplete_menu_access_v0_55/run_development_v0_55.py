"""Run the non-claim-eligible ASMP-9 v0.55 domain-lattice census."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import time

import psutil

from incomplete_menu import (
    ALL_MENUS,
    compatible_tiers,
    domain_name,
    full_grid,
    full_status,
    menu_domains,
    nonluce_rum_completion,
    nonrum_completion,
    project,
    projection_key,
    rum_completion,
    scalar_completion,
)


HERE = Path(__file__).resolve().parent


def main() -> None:
    started = time.perf_counter()
    process = psutil.Process()
    full_kernels = tuple(full_grid())
    rows = []
    construction_failures = 0

    for domain in menu_domains():
        unique = {}
        for full in full_kernels:
            partial = project(full, domain)
            unique.setdefault(projection_key(partial), partial)

        tier_counts = Counter()
        scalar_compatible = 0
        rum_compatible = 0
        for partial in unique.values():
            tiers = compatible_tiers(partial, domain)
            tier_counts["|".join(tiers)] += 1
            weights = scalar_completion(partial, domain)
            rum = rum_completion(partial, domain)
            scalar_compatible += weights is not None
            rum_compatible += rum is not None

            if set(domain) != set(ALL_MENUS):
                try:
                    none = nonrum_completion(partial, domain)
                    construction_failures += full_status(none) != (
                        "no_random_utility_representation"
                    )
                    if weights is not None:
                        middle = nonluce_rum_completion(
                            partial, domain, weights
                        )
                        construction_failures += full_status(middle) != (
                            "random_utility_non_luce"
                        )
                except (AssertionError, ValueError):
                    construction_failures += 1

        rows.append(
            {
                "domain": domain_name(domain),
                "menu_count": len(domain),
                "observed_dimension": sum(len(menu) - 1 for menu in domain),
                "complete": set(domain) == set(ALL_MENUS),
                "unique_projection_count": len(unique),
                "scalar_compatible_count": scalar_compatible,
                "rum_compatible_count": rum_compatible,
                "tier_set_counts": dict(sorted(tier_counts.items())),
            }
        )

    elapsed = time.perf_counter() - started
    payload = {
        "claim_eligible": False,
        "status": "development_only",
        "full_grid_kernel_count": len(full_kernels),
        "domain_count": len(rows),
        "proper_domain_count": sum(not row["complete"] for row in rows),
        "construction_failures": construction_failures,
        "domains": rows,
        "elapsed_seconds": round(elapsed, 6),
        "resident_bytes": process.memory_info().rss,
    }
    (HERE / "DEVELOPMENT_CENSUS_v0_55.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
