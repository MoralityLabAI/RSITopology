"""Independent exact verifier for the registered ASMP-9 v0.39 result."""

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
from confirmation import run_confirmation


BASE = Path(__file__).resolve().parent


def parseq(value: str) -> Q:
    return Q(value)


def verify(
    registration_path: Path,
    result_path: Path,
) -> dict:
    registration = validate_registration(registration_path)
    result = json.loads(result_path.read_text(encoding="utf-8"))

    recorded_content_hash = result["result_content_sha256"]
    unhashed = {
        key: value
        for key, value in result.items()
        if key != "result_content_sha256"
    }
    recomputed_content_hash = sha256_bytes(canonical_bytes(unhashed))
    if recomputed_content_hash != recorded_content_hash:
        raise ValueError("result content hash does not reproduce")
    if result["registration_file_sha256"] != sha256_file(registration_path):
        raise ValueError("result is not bound to this registration")
    if result["registration_implementation_commit"] != registration[
        "implementation_commit"
    ]:
        raise ValueError("implementation commit link does not match")

    replay = run_confirmation()
    for key in ("leakage_rows", "intervention_rows", "alignment_rows"):
        if result[key] != replay[key]:
            raise ValueError(f"exact replay mismatch in {key}")
    for gate, state in replay["gates"].items():
        if result["gates"].get(gate) != state:
            raise ValueError(f"exact replay mismatch in gate {gate}")

    for row in result["leakage_rows"]:
        probabilities = tuple(parseq(value) for value in row["probabilities"])
        expected = (max(probabilities) - min(probabilities)) / 2
        if not (
            parseq(row["analytic_radius"])
            == parseq(row["decision_relative_radius"])
            == parseq(row["ordinary_radius"])
            == expected
        ):
            raise ValueError("half-range leakage identity failed")
        if (
            parseq(row["reverse_decision_relative"]) != 0
            or parseq(row["reverse_ordinary"]) != 0
        ):
            raise ValueError("reverse deficiency is nonzero")

    blocks: dict[tuple[Q, Q], dict[str, dict]] = {}
    for row in result["alignment_rows"]:
        high, low = parseq(row["high"]), parseq(row["low"])
        gap = high - low
        expected = {
            "q0": Q(0),
            "q0_complement": Q(0),
            "q1": gap / 2,
            "q2": high * low * gap,
            "constant": gap / 2,
        }[row["gauge_assignment"]]
        if not (
            parseq(row["registered_expected_deficiency"])
            == parseq(row["relative_substitution_deficiency"])
            == parseq(row["ordinary_substitution_deficiency"])
            == expected
        ):
            raise ValueError("alignment identity failed")
        blocks.setdefault((high, low), {})[row["gauge_assignment"]] = row

    for block in blocks.values():
        radii = {
            parseq(block[name]["leakage_radius"])
            for name in ("q0", "q1", "q2")
        }
        values = {
            parseq(block[name]["relative_substitution_deficiency"])
            for name in ("q0", "q1", "q2")
        }
        if len(radii) != 1 or len(values) != 3:
            raise ValueError("equal-radius value separation failed")

    if result["status"] != "correlated_gauge_access_alignment_established":
        raise ValueError("registered status is not the passing status")
    if not all(result["gates"].values()):
        raise ValueError("at least one registered gate did not pass")

    return {
        "status": "independent_exact_replay_passed",
        "registration_file_sha256": sha256_file(registration_path),
        "result_file_sha256": sha256_file(result_path),
        "result_content_sha256": recorded_content_hash,
        "sealed_files_revalidated": len(registration["sealed_files"]),
        "alignment_rows_replayed": len(result["alignment_rows"]),
        "leakage_rows_replayed": len(result["leakage_rows"]),
        "intervention_rows_replayed": len(result["intervention_rows"]),
        "all_registered_gates_pass": True,
    }


def main() -> None:
    registration_path = BASE / "registration_v0_39.json"
    result_path = BASE / "artifacts_v0_39" / "RESULT_v0_39.json"
    output_path = BASE / "artifacts_v0_39" / "VERIFY_v0_39.json"
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite {output_path}")
    payload = verify(registration_path, result_path)
    output_path.write_bytes(canonical_bytes(payload))
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
