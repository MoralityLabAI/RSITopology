from __future__ import annotations

import hashlib
import json
from pathlib import Path

from history_stabilization import (
    delayed_prefix_census,
    machine_census,
    pair_equivalence_census_two_state,
)


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "DEVELOPMENT_VERIFICATION_v0_73.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    two_state = machine_census(2)
    three_state = machine_census(3)
    pair_census = pair_equivalence_census_two_state()
    delayed = delayed_prefix_census(12)
    payload = {
        "status": "development_only_not_preregistered",
        "two_state_machine_census": two_state,
        "three_state_machine_census": three_state,
        "two_state_pair_census": pair_census,
        "delayed_prefix_census": delayed,
        "checks": {
            "all_256_two_state_machines_checked": (
                two_state["machine_count"] == 256
            ),
            "all_46656_three_state_machines_checked": (
                three_state["machine_count"] == 46_656
            ),
            "k_minus_one_bound_holds": (
                two_state["maximum_depth"] <= 1
                and three_state["maximum_depth"] <= 2
            ),
            "all_32896_two_state_pairs_checked": (
                pair_census["unordered_pairs_with_repetition"] == 32_896
            ),
            "product_bound_holds": (
                pair_census["maximum_word_length"]
                <= pair_census["product_bound"]
            ),
            "all_13_finite_prefixes_have_delayed_witness": (
                len(delayed["records"]) == 13
                and delayed["all_prefixes_indistinguishable"]
                and delayed["all_delayed_witnesses_nonstationary"]
            ),
        },
        "claim_boundary": (
            "Classical deterministic reward-machine equivalence and finite-"
            "prefix impossibility. No empirical human/model memory bound, "
            "stochastic process theorem, moral-value claim, or ASMP-9 "
            "resolution."
        ),
        "source_hashes": {
            name: sha256(ROOT / name)
            for name in (
                "history_stabilization.py",
                "test_history_stabilization.py",
                "THEOREM_DRAFT_v0_73.md",
                "PRIOR_ART_GATE_v0_73.md",
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
