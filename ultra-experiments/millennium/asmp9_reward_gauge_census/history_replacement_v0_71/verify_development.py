from __future__ import annotations

import hashlib
import json
from pathlib import Path

from history_replacement import (
    binary_valuation_census,
    canonical_fixtures,
    canonical_history_replacement,
    factor_markov_reward,
    replay_replacement,
)


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "DEVELOPMENT_VERIFICATION_v0_71.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    records: dict[str, object] = {}
    for name, system in canonical_fixtures().items():
        factorization = factor_markov_reward(system)
        replacement = canonical_history_replacement(system)
        records[name] = {
            "factorization": factorization.to_jsonable(),
            "replacement": replacement.to_jsonable(),
            "replay_passed": replay_replacement(system, replacement),
        }

    positive = records["markov_additive"]
    negative = records["history_interaction"]
    census = binary_valuation_census()
    payload = {
        "status": "development_only_not_preregistered",
        "fixtures": records,
        "binary_valuation_census": census,
        "checks": {
            "markov_fixture_factorizes": positive["factorization"]["factorizes"],
            "markov_fixture_has_no_history_split": not positive["replacement"][
                "needs_history_augmentation"
            ],
            "interaction_fixture_does_not_factorize": not negative[
                "factorization"
            ]["factorizes"],
            "interaction_fixture_has_exact_obstruction": negative[
                "factorization"
            ]["obstruction_value"]
            is not None,
            "interaction_fixture_splits_history": negative["replacement"][
                "needs_history_augmentation"
            ],
            "both_replacements_replay": all(
                record["replay_passed"] for record in records.values()
            ),
            "all_16_binary_valuations_classified": census["total"] == 16,
            "binary_census_replays_without_failure": (
                census["replay_failures"] == 0
            ),
        },
        "claim_boundary": (
            "Exact bounded finite path-language factorization and minimal "
            "future-increment quotient. Classical linear algebra and "
            "Myhill-Nerode-style machinery; no human/model value claim or "
            "ASMP-9 resolution."
        ),
        "source_hashes": {
            name: sha256(ROOT / name)
            for name in (
                "history_replacement.py",
                "test_history_replacement.py",
                "THEOREM_DRAFT_v0_71.md",
                "PRIOR_ART_GATE_v0_71.md",
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
