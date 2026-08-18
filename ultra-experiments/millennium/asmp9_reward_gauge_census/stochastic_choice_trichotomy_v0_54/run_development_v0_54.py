"""Run the non-claim-eligible ASMP-9 v0.54 development census."""

from __future__ import annotations

import json
import time
import tracemalloc
from collections import Counter
from fractions import Fraction
from pathlib import Path

from stochastic_choice import (
    block_marschak_table,
    canonical_witnesses,
    classify,
    denominator_six_census,
    pair_projection,
)


ROOT = Path(__file__).resolve().parent


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def main() -> None:
    tracemalloc.start()
    started = time.perf_counter()

    counts: Counter[str] = Counter()
    minimum_bm: Counter[str] = Counter()
    certificate_mismatches = 0
    total = 0
    for kernel in denominator_six_census():
        result = classify(kernel)
        counts[result.status] += 1
        total += 1
        table = block_marschak_table(kernel, ("a", "b", "c"))
        minimum_bm[fraction_text(min(table.values()))] += 1
        if result.status == "no_random_utility_representation":
            if result.negative_block_marschak is None:
                certificate_mismatches += 1
        elif result.ranking_mixture is None:
            certificate_mismatches += 1

    witnesses = canonical_witnesses()
    witness_statuses = {
        name: classify(kernel).status for name, kernel in witnesses.items()
    }
    access_pair_match = (
        pair_projection(witnesses["scalar_access"])
        == pair_projection(witnesses["none"])
    )
    none_negative = classify(witnesses["none"]).negative_block_marschak

    elapsed = time.perf_counter() - started
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    payload = {
        "claim_eligible": False,
        "status": "development_only",
        "universe": ["a", "b", "c"],
        "grid_denominator": 6,
        "kernel_count": total,
        "class_counts": dict(sorted(counts.items())),
        "all_tiers_nonempty": all(value > 0 for value in counts.values()),
        "certificate_mismatches": certificate_mismatches,
        "witness_statuses": witness_statuses,
        "binary_access_pair_projection_match": access_pair_match,
        "no_object_negative_bm": {
            "choice": none_negative[0],
            "menu": list(none_negative[1]),
            "value": fraction_text(none_negative[2]),
        },
        "minimum_bm_distribution": dict(sorted(minimum_bm.items())),
        "elapsed_seconds": round(elapsed, 6),
        "peak_traced_bytes": peak,
    }
    (ROOT / "DEVELOPMENT_CENSUS_v0_54.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
