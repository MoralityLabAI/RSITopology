"""Independent exact verifier for ASMP-9 risk-polytope access v0.40."""

from __future__ import annotations

from fractions import Fraction as Q
import json
from pathlib import Path

from execute_confirmation import (
    canonical_bytes,
    sha256_bytes,
    sha256_file,
    validate_registration,
)
from confirmation import (
    CONFIRMATION_QUERIES,
    S0_FN,
    S0_FP,
    S0_LABELS,
    S1_FN,
    S1_FP,
    S1_LABELS,
    run_confirmation,
)
from risk_polytope_access import (
    binary_group_partition_deficiency,
    classification_partition_deficiency,
    is_test_cover,
)


BASE = Path(__file__).resolve().parent


def parseq(value: str) -> Q:
    return Q(value)


def verify(registration_path: Path, result_path: Path) -> dict:
    registration = validate_registration(registration_path)
    result = json.loads(result_path.read_text(encoding="utf-8"))
    content_hash = result["result_content_sha256"]
    unhashed = {
        key: value
        for key, value in result.items()
        if key != "result_content_sha256"
    }
    if sha256_bytes(canonical_bytes(unhashed)) != content_hash:
        raise ValueError("result content hash does not reproduce")
    if result["registration_file_sha256"] != sha256_file(registration_path):
        raise ValueError("result is not bound to this registration")

    replay = run_confirmation()
    for key in (
        "classification_rows",
        "compiled_rows",
        "solver_spotchecks",
        "zero_tolerance_minimal_access",
        "persistence_curves",
    ):
        if result[key] != replay[key]:
            raise ValueError(f"exact replay mismatch in {key}")
    for gate, state in replay["gates"].items():
        if result["gates"].get(gate) != state:
            raise ValueError(f"exact replay mismatch in gate {gate}")

    for row in result["classification_rows"]:
        subset = tuple(row["subset"])
        expected = classification_partition_deficiency(
            CONFIRMATION_QUERIES, subset
        )
        if parseq(row["epsilon"]) != expected:
            raise ValueError("classification partition formula failed")
        if row["is_test_cover"] != is_test_cover(
            CONFIRMATION_QUERIES, subset
        ):
            raise ValueError("test-cover decision failed")
        if (expected == 0) != row["is_test_cover"]:
            raise ValueError("zero deficiency and Test Cover diverged")

    compiled = {
        name: {
            tuple(row["subset"]): parseq(row["epsilon"])
            for row in rows
        }
        for name, rows in result["compiled_rows"].items()
    }
    for subset in compiled["s0_asymmetric"]:
        expected_s0 = binary_group_partition_deficiency(
            CONFIRMATION_QUERIES,
            subset,
            S0_LABELS,
            S0_FP,
            S0_FN,
        )
        expected_s1 = binary_group_partition_deficiency(
            CONFIRMATION_QUERIES,
            subset,
            S1_LABELS,
            S1_FP,
            S1_FN,
        )
        if compiled["s0_asymmetric"][subset] != expected_s0:
            raise ValueError("s0 group formula failed")
        if compiled["s1_asymmetric"][subset] != expected_s1:
            raise ValueError("s1 group formula failed")
        if compiled["combined_groups"][subset] != max(
            expected_s0, expected_s1
        ):
            raise ValueError("combined decision-type formula failed")

    if result["status"] != (
        "finite_risk_polytope_access_characterization_established"
    ):
        raise ValueError("unexpected result status")
    if not all(result["gates"].values()):
        raise ValueError("a registered gate did not pass")

    return {
        "status": "independent_exact_replay_passed",
        "registration_file_sha256": sha256_file(registration_path),
        "result_file_sha256": sha256_file(result_path),
        "result_content_sha256": content_hash,
        "sealed_files_revalidated": len(registration["sealed_files"]),
        "classification_rows_replayed": len(
            result["classification_rows"]
        ),
        "compiled_rows_replayed": sum(
            len(rows) for rows in result["compiled_rows"].values()
        ),
        "solver_spotchecks_replayed": len(result["solver_spotchecks"]),
        "all_registered_gates_pass": True,
    }


def main() -> None:
    registration = BASE / "registration_v0_40.json"
    result = BASE / "artifacts_v0_40" / "RESULT_v0_40.json"
    output = BASE / "artifacts_v0_40" / "VERIFY_v0_40.json"
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    payload = verify(registration, result)
    output.write_bytes(canonical_bytes(payload))
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
