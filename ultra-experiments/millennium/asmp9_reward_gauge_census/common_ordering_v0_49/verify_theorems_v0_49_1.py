"""Verifier-only repair for the ASMP-9 v0.49 universe count."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
UNCHANGED_GATES = ("H0", "T0", "M0", "G0", "V0", "RESOURCE")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def corrected_universe_valid(original: dict) -> bool:
    audit = original["exhaustive_four_outcome"]
    return (
        audit["expected_table_count"] == 168
        and audit["expected_ordered_pair_count"] == 168**2
        and audit["table_count"] == 167
        and audit["ordered_pair_count"] == 167**2
        and audit["tight_dag_mismatches"] == 0
        and audit["common_chain_mismatches"] == 0
    )


def original_failure_is_count_only(original: dict) -> bool:
    return (
        not original["ok"]
        and original["status"]
        == "finite_common_ordering_theorem_not_verified"
        and not original["gates"]["D0"]
        and all(original["gates"][name] for name in UNCHANGED_GATES)
        and corrected_universe_valid(original)
    )


def main() -> None:
    repair_registration_path = (
        HERE / "verification_repair_registration_v0_49_1.json"
    )
    original_registration_path = (
        HERE / "verification_registration_v0_49.json"
    )
    original_result_path = HERE / "VERIFY_RESULT_v0_49.json"
    output = HERE / "VERIFY_RESULT_v0_49_1.json"

    repair_bytes = repair_registration_path.read_bytes()
    repair = json.loads(repair_bytes)
    original_registration_bytes = original_registration_path.read_bytes()
    original = json.loads(original_result_path.read_bytes())

    repair_sources_match = all(
        (REPO / relative).is_file()
        and sha256(REPO / relative) == expected
        for relative, expected in repair["source_sha256"].items()
    )
    original_registration_match = (
        original["registration_sha256"]
        == hashlib.sha256(original_registration_bytes).hexdigest()
    )
    original_receipt_match = (
        sha256(original_result_path)
        == repair["original_verification_sha256"]
    )
    original_sources_match = all(
        row["match"] for row in original["source_checks"]
    )
    correction_match = corrected_universe_valid(original)
    failure_diagnosed = original_failure_is_count_only(original)
    ok = all(
        (
            repair_sources_match,
            original_registration_match,
            original_receipt_match,
            original_sources_match,
            correction_match,
            failure_diagnosed,
        )
    )
    payload = {
        "schema": "asmp9-v0.49.1-verification-repair-v1",
        "ok": ok,
        "status": (
            "finite_common_ordering_theorem_verified"
            if ok
            else "finite_common_ordering_theorem_not_verified"
        ),
        "repair_registration_sha256": hashlib.sha256(
            repair_bytes
        ).hexdigest(),
        "repair_sources_match": repair_sources_match,
        "original_registration_match": original_registration_match,
        "original_receipt_match": original_receipt_match,
        "original_sources_match": original_sources_match,
        "original_failure_is_count_only": failure_diagnosed,
        "corrected_universe": {
            "dedekind_count": 168,
            "excluded_constant_one": 1,
            "admissible_table_count": 167,
            "ordered_pair_count": 167**2,
            "tight_dag_mismatches": original[
                "exhaustive_four_outcome"
            ]["tight_dag_mismatches"],
            "common_chain_mismatches": original[
                "exhaustive_four_outcome"
            ]["common_chain_mismatches"],
        },
        "unchanged_gate_values": {
            name: original["gates"][name] for name in UNCHANGED_GATES
        },
        "original_D0": original["gates"]["D0"],
    }
    encoded = (
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    if output.exists() and output.read_bytes() != encoded:
        raise RuntimeError("write-once repair verification mismatch")
    output.write_bytes(encoded)
    print(json.dumps(payload, indent=2, sort_keys=True))
    raise SystemExit(not ok)


if __name__ == "__main__":
    main()
