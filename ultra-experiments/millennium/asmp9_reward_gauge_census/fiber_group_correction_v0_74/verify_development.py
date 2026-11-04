from __future__ import annotations

import hashlib
import json
from pathlib import Path

from fiber_group import (
    diagnose_access,
    full_fiber_group_size,
    generated_group,
    minimum_exact_query_family,
)


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "DEVELOPMENT_VERIFICATION_v0_74.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    cyclic = ((1, 2, 0),)
    constant = ("same", "same", "same")
    exact = diagnose_access([constant], cyclic)
    under = diagnose_access(
        [("same",) * 4],
        ((1, 0, 2, 3), (0, 1, 3, 2)),
    )
    over = diagnose_access([("left", "right", "other")], ((1, 0, 2),))
    minimum = minimum_exact_query_family(
        ((0, 0, 1, 1), (0, 1, 0, 1), (0, 0, 0, 0)),
        tuple(),
    )
    payload = {
        "status": "development_only_not_preregistered",
        "checks": {
            "cyclic_group_order": len(generated_group(3, cyclic)),
            "full_fiber_group_order": full_fiber_group_size(constant),
            "same_orbits_despite_different_group_orders": (
                exact.status == "exact_quotient_identification"
                and len(generated_group(3, cyclic)) == 3
                and full_fiber_group_size(constant) == 6
            ),
            "underidentification_detected": under.status == "underidentified",
            "gauge_split_detected": (
                over.status == "overdiscriminates_licensed_gauge"
            ),
            "minimum_exact_query_family": minimum,
            "minimum_family_has_two_queries": minimum == (0, 1),
        },
        "claim_boundary": (
            "Finite set-theoretic orbit/fiber and set-cover correction only; "
            "no behavioral reward identification or ASMP-9 resolution."
        ),
        "source_hashes": {
            name: sha256(ROOT / name)
            for name in (
                "fiber_group.py",
                "test_fiber_group.py",
                "THEOREM_DRAFT_v0_74.md",
                "PRIOR_ART_GATE_v0_74.md",
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
