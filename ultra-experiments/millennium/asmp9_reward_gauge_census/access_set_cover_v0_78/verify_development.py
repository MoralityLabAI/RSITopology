from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

from access_set_cover import (
    build_access_instance,
    minimum_access_family,
    minimum_set_cover,
    query_family_separates,
)


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "DEVELOPMENT_VERIFICATION_v0_78.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    universe = (0, 1, 2, 3)
    sets = ({0, 1}, {2, 3}, {0, 2}, {1, 3})
    cover = minimum_set_cover(universe, sets)
    instance = build_access_instance(universe, sets)
    access = minimum_access_family(instance)

    generator = random.Random(7801)
    registry_records = []
    for registry_index in range(48):
        local_universe = tuple(range(5))
        local_sets = tuple(
            frozenset(
                element
                for element in local_universe
                if generator.random() < 0.45
            )
            for _ in range(6)
        )
        local_cover = minimum_set_cover(local_universe, local_sets)
        local_access = minimum_access_family(
            build_access_instance(local_universe, local_sets)
        )
        registry_records.append(
            {
                "registry_index": registry_index,
                "cover_optimum": local_cover,
                "access_optimum": local_access,
                "shift_holds": (
                    local_cover is None and local_access is None
                )
                or (
                    local_cover is not None
                    and local_access is not None
                    and local_access[0] == 0
                    and len(local_access) == len(local_cover) + 1
                ),
            }
        )

    payload = {
        "status": "development_only_not_preregistered",
        "frozen_fixture": {
            "universe": universe,
            "sets": [sorted(item) for item in sets],
            "cover_optimum": cover,
            "access_optimum": access,
            "anchor_query_index": instance.anchor_query_index,
            "access_separates": query_family_separates(
                instance.target_labels,
                instance.queries,
                access,
            ),
        },
        "seeded_registry": registry_records,
        "checks": {
            "frozen_cover_optimum_two": len(cover) == 2,
            "frozen_access_optimum_three": len(access) == 3,
            "anchor_is_in_every_reported_optimum": access[0] == 0,
            "all_48_shift_checks_hold": all(
                record["shift_holds"] for record in registry_records
            ),
        },
        "claim_boundary": (
            "Polynomial reduction from finite Set Cover to deterministic exact "
            "target-access design; classical NP-hardness consequence only, "
            "not behavioral acquisition or ASMP-9 resolution."
        ),
        "source_hashes": {
            name: sha256(ROOT / name)
            for name in (
                "access_set_cover.py",
                "test_access_set_cover.py",
                "THEOREM_DRAFT_v0_78.md",
                "PRIOR_ART_GATE_v0_78.md",
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
