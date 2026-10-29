"""Independent verifier for the ASMP-2 crossed-shift result."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent


def F(value: str | int) -> Fraction:
    return Fraction(str(value))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def write_once(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"refusing to replace non-identical artifact: {path}")
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def verify(result_path: Path, receipt_path: Path) -> dict[str, Any]:
    result = json.loads(result_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}

    checks["result_hash_matches_receipt"] = sha256_file(result_path) == receipt.get("result_sha256")
    checks["verifier_hash_matches_receipt"] = sha256_file(Path(__file__).resolve()) == receipt.get("verifier_sha256")
    checks["protocol_hash_matches_local"] = sha256_file(HERE / "protocol_v0_1.json") == receipt.get("protocol_sha256")
    checks["claim_hash_matches_local"] = sha256_file(HERE / "CLAIM_PACKET.md") == receipt.get("claim_packet_sha256")
    checks["schema_matches"] = result.get("schema_version") == "asmp2_crossed_shift_result_v0_1"
    checks["forced_label_preserved"] = result.get("evidence_label") == "instrument_valid_forced_construction"
    checks["runner_status_valid"] = result.get("instrument_status") == "valid" and result.get("runner_gate_pass") is True

    gates = result.get("gates", {})
    expected_gate_ids = {f"G{index}_{name}" for index, name in (
        (0, "registration_binding"),
        (1, "source_indistinguishability"),
        (2, "exact_fisher_conditioning"),
        (3, "local_global_identities"),
        (4, "liveness_and_controls"),
        (5, "coordinate_invariance"),
    )}
    checks["exact_gate_universe"] = set(gates) == expected_gate_ids
    checks["all_runner_gates_pass"] = bool(gates) and all(record.get("pass") is True for record in gates.values())

    fisher = gates.get("G2_exact_fisher_conditioning", {})
    checks["fisher_exact"] = fisher.get("matrix") == [["5/64", "1/64"], ["1/64", "5/64"]]
    checks["fisher_eigenpairs_exact"] = fisher.get("eigenpair_checks") == [True, True]
    checks["kappa_exact"] = F(fisher.get("kappa_squared", "0")) == F("1/16") and fisher.get("kappa") == "1/4"

    ambiguity = gates.get("G3_local_global_identities", {})
    records = ambiguity.get("ambiguity_records", [])
    expected = {
        F("1/4"): (F("1/64"), F("1/16")),
        F("1/2"): (F("1/16"), F("1/8")),
        F("1"): (F("1/4"), F("1/4")),
    }
    observed: dict[Fraction, tuple[Fraction, Fraction]] = {}
    for record in records:
        observed[F(record["radius"])] = (
            F(record["crossed_observed"]),
            F(record["unspanned_observed"]),
        )
    checks["ambiguity_table_exact"] = observed == expected
    checks["global_ambiguity_exact"] = F(ambiguity.get("global_ambiguity", "0")) == F("1/4")

    controls = gates.get("G4_liveness_and_controls", {})
    checks["affine_control_exact"] = F(controls.get("affine_ambiguity", "1")) == 0
    checks["risk_null_control_exact"] = controls.get("risk_null", {}).get("raw_design_rank") == 2 and controls.get("risk_null", {}).get("quotient_design_rank") == 2
    checks["count_matched_control_exact"] = controls.get("count_matched", {}).get("axis_count") == controls.get("count_matched", {}).get("diagonal_design_count") == 5 and F(controls.get("count_matched", {}).get("world_gap_at_diagonal", "0")) == F("1/16")
    checks["safety_control_exact"] = controls.get("safety") == {
        "minus_at_1_1": "1/2",
        "opposite_sides": True,
        "plus_at_1_1": "3/4",
        "threshold": "3/5",
    }
    coordinate_records = gates.get("G5_coordinate_invariance", {}).get("records", [])
    checks["eight_coordinate_reframes"] = len(coordinate_records) == 8 and all(record.get("pass") is True for record in coordinate_records)
    checks["resource_ceiling_pass"] = result.get("resource_receipt", {}).get("pass") is True
    checks["registration_commit_agrees"] = result.get("registration", {}).get("commit") == receipt.get("git_commit_at_run")

    passed = all(checks.values())
    return {
        "schema_version": "asmp2_crossed_shift_verification_v0_1",
        "instrument_status": "valid" if passed else "invalid",
        "evidence_label": "instrument_valid_forced_construction" if passed else "not_established",
        "G6_independent_verification": {"pass": passed, "checks": checks},
        "stage_decision": "pass" if passed else "invalid_stop_sequence",
        "next_stage": "ASMP-4" if passed else None,
        "claim_boundary": "Exact verification of one analytically forced finite construction; no general ASMP-2 inference.",
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    result_path = args.result.resolve()
    receipt_path = args.receipt.resolve()
    output_path = args.output.resolve()
    if not result_path.is_file() or not receipt_path.is_file():
        raise FileNotFoundError("result and receipt are required")
    if output_path in {result_path, receipt_path}:
        raise ValueError("verification output aliases an input")
    verification = verify(result_path, receipt_path)
    write_once(output_path, canonical_json(verification).encode("utf-8"))
    print(canonical_json(verification), end="")
    return 0 if verification["stage_decision"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
