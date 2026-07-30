from __future__ import annotations

import hashlib
import json
from pathlib import Path

from target_interface import classify_target_interface


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "DEVELOPMENT_VERIFICATION_v0_76.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(result) -> dict[str, object]:
    return {
        "status": result.status,
        "target_recoverable": result.target_recoverable,
        "representative_insensitive": result.representative_insensitive,
        "exact_partition_match": result.exact_partition_match,
        "underidentification_witnesses": result.underidentification_witnesses,
        "representative_leakage_witnesses": (
            result.representative_leakage_witnesses
        ),
        "target_decoder": result.target_decoder,
        "representative_insensitive_encoder": (
            result.representative_insensitive_encoder
        ),
    }


def main() -> None:
    target = ("left", "left", "right", "right")
    cases = {
        "exact": classify_target_interface(target, ("a", "a", "b", "b")),
        "leakage_only": classify_target_interface(
            target, ("a", "b", "c", "d")
        ),
        "underidentified_only": classify_target_interface(
            target, ("a", "a", "a", "a")
        ),
        "cross_cut": classify_target_interface(target, ("a", "b", "a", "b")),
    }
    expected = {
        "exact": "exact_target_interface",
        "leakage_only": "recoverable_with_representative_leakage",
        "underidentified_only": "underidentified",
        "cross_cut": "cross_cut_misspecified_interface",
    }
    payload = {
        "status": "development_only_not_preregistered",
        "cases": {name: record(result) for name, result in cases.items()},
        "checks": {
            "all_four_states_realized": (
                {result.status for result in cases.values()} == set(expected.values())
            ),
            "statuses_match": all(
                cases[name].status == status for name, status in expected.items()
            ),
            "leakage_case_has_decoder": (
                cases["leakage_only"].target_decoder is not None
                and cases["leakage_only"].target_recoverable
            ),
            "underidentified_case_has_no_decoder": (
                cases["underidentified_only"].target_decoder is None
                and not cases["underidentified_only"].target_recoverable
            ),
        },
        "claim_boundary": (
            "Finite partition-factorization distinction only; no physical "
            "reward-channel or behavioral validation, and no ASMP-9 resolution."
        ),
        "source_hashes": {
            name: sha256(ROOT / name)
            for name in (
                "target_interface.py",
                "test_target_interface.py",
                "THEOREM_DRAFT_v0_76.md",
                "PRIOR_ART_GATE_v0_76.md",
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
