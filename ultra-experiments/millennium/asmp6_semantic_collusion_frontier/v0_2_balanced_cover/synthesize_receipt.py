"""Emit the final source- and artifact-bound ASMP-6 v0.2 receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

import verify_independent as independent


HERE = Path(__file__).resolve().parent
SOURCE_FILENAMES = (
    "balanced_cover.py",
    "run.py",
    "verify_independent.py",
    "synthesize_receipt.py",
    "test_balanced_cover.py",
    "protocol_v0_2.json",
    "PROTOCOL_v0_2.md",
    "README.md",
)
EXPECTED_CLAIM_SUPPORT = (
    "one_shot_two_equiprobable_messages_uniform_exact_average_cover"
)
FROZEN_PROTOCOL_FIELDS = {
    "alphabet_sizes",
    "claim_boundary",
    "cover_law",
    "independent_extremal_enumeration_maximum",
    "message_count",
    "message_prior",
    "protocol_id",
    "schema_version",
}
FROZEN_CLAIM_BOUNDARY = (
    "one-shot opaque-symbol laws only",
    "exactly two equiprobable messages only",
    "uniform benign cover law only",
    "exact message-averaged cover and exact per-message control only",
    "no learned or linguistic encoder",
    "no multiletter or ASMP-6 resolution claim",
)
EXPECTED_FINAL_LAYERS = {
    "metric_robustness": "five_probe_pack_independently_replayed",
    "task_result": "sharp_uniform_alphabet_parity_frontier",
    "measurement_reliability": (
        "independent_full_grid_continuous_extremal_and_dual_replay_passed"
    ),
    "claim_support": EXPECTED_CLAIM_SUPPORT,
    "operational_decision": "register_multiletter_successor",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _git(args: list[str], *, text: bool) -> str | bytes:
    completed = subprocess.run(
        ["git", *args],
        cwd=HERE,
        check=True,
        capture_output=True,
        text=text,
    )
    return completed.stdout.strip() if text else completed.stdout


def resolve_git_commit(source_commit: str) -> str:
    return str(_git(["rev-parse", "--verify", f"{source_commit}^{{commit}}"], text=True))


def read_git_blob(source_commit: str, repo_relative_path: str) -> bytes:
    repo_root = Path(str(_git(["rev-parse", "--show-toplevel"], text=True))).resolve()
    return subprocess.check_output(
        ["git", "show", f"{source_commit}:{repo_relative_path}"], cwd=repo_root
    )


def default_source_files() -> dict[str, Path]:
    repo_root = Path(str(_git(["rev-parse", "--show-toplevel"], text=True))).resolve()
    relative_directory = HERE.relative_to(repo_root)
    return {
        (relative_directory / filename).as_posix(): HERE / filename
        for filename in SOURCE_FILENAMES
    }


def protocol_binding_checks(protocol: dict[str, Any]) -> dict[str, bool]:
    try:
        prior = tuple(Fraction(value) for value in protocol["message_prior"])
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        prior = ()
    limits = protocol.get("alphabet_sizes", {})
    minimum = limits.get("minimum") if isinstance(limits, dict) else None
    maximum = limits.get("maximum") if isinstance(limits, dict) else None
    boundary = protocol.get("claim_boundary")
    return {
        "protocol_fields_are_exact": set(protocol) == FROZEN_PROTOCOL_FIELDS,
        "protocol_id_is_frozen": (
            protocol.get("protocol_id") == "ASMP6-BALANCED-COVER-v0.2"
        ),
        "protocol_schema_is_frozen": (
            protocol.get("schema_version") == "asmp6_balanced_cover_protocol_v0_2"
        ),
        "cover_law_is_uniform": protocol.get("cover_law") == "uniform",
        "message_count_is_two": (
            type(protocol.get("message_count")) is int
            and protocol.get("message_count") == 2
        ),
        "message_prior_is_equal_half": prior == (Fraction(1, 2), Fraction(1, 2)),
        "registered_alphabet_range_is_2_through_31": (
            type(minimum) is int
            and type(maximum) is int
            and (minimum, maximum) == (2, 31)
        ),
        "enumeration_maximum_is_nine": (
            type(protocol.get("independent_extremal_enumeration_maximum")) is int
            and protocol.get("independent_extremal_enumeration_maximum") == 9
        ),
        "claim_boundary_is_frozen": (
            isinstance(boundary, list) and tuple(boundary) == FROZEN_CLAIM_BOUNDARY
        ),
    }


def build_receipt(
    source_commit: str,
    protocol_path: Path,
    result_path: Path,
    verification_path: Path,
    *,
    source_files: dict[str, Path] | None = None,
    commit_resolver: Callable[[str], str] = resolve_git_commit,
    committed_blob_reader: Callable[[str, str], bytes] = read_git_blob,
) -> dict[str, Any]:
    """Build a receipt and fail every conclusion layer on any binding defect."""

    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    verification = json.loads(verification_path.read_text(encoding="utf-8"))
    fresh_verification = independent.verify(protocol_path, result_path)
    source_files = source_files if source_files is not None else default_source_files()

    commit_format_valid = bool(re.fullmatch(r"[0-9a-f]{40}", source_commit))
    resolved_commit = ""
    commit_resolution_error = ""
    if commit_format_valid:
        try:
            resolved_commit = commit_resolver(source_commit)
        except (OSError, subprocess.SubprocessError, ValueError) as error:
            commit_resolution_error = type(error).__name__
    commit_resolves_exactly = bool(
        commit_format_valid and resolved_commit == source_commit
    )

    current_source_hashes = {
        name: sha256_file(path) for name, path in sorted(source_files.items())
    }
    committed_source_hashes: dict[str, str] = {}
    source_read_errors: dict[str, str] = {}
    if commit_resolves_exactly:
        for name in sorted(source_files):
            try:
                committed_source_hashes[name] = sha256_bytes(
                    committed_blob_reader(source_commit, name)
                )
            except (OSError, subprocess.SubprocessError, ValueError) as error:
                source_read_errors[name] = type(error).__name__
    source_mismatches = [
        name
        for name, current_hash in current_source_hashes.items()
        if committed_source_hashes.get(name) != current_hash
    ]
    source_files_match_commit = bool(source_files) and not (
        source_read_errors or source_mismatches
    )

    artifact_hashes = {
        "protocol_v0_2.json": sha256_file(protocol_path),
        "result_v0_2.json": sha256_file(result_path),
        "verification_v0_2.json": sha256_file(verification_path),
    }
    expected_verification_bindings = {
        key: artifact_hashes[key]
        for key in ("protocol_v0_2.json", "result_v0_2.json")
    }
    binding = protocol_binding_checks(protocol)
    limits = protocol.get("alphabet_sizes", {})
    registered_sizes = (
        list(range(limits["minimum"], limits["maximum"] + 1))
        if binding["registered_alphabet_range_is_2_through_31"]
        else []
    )
    gates = result.get("gates", {})
    independent_gates = verification.get("independent_gates", {})
    final_layers = verification.get("final_conclusion_layers", {})

    checks = {
        "C0_source_commit_resolves_exactly": commit_resolves_exactly,
        "C1_source_files_match_commit": source_files_match_commit,
        "C2_frozen_protocol_binding": all(binding.values()),
        "C3_primary_result_identity_and_preverification_state": bool(
            result.get("schema_version") == "asmp6_balanced_cover_result_v0_2"
            and result.get("protocol_id") == protocol.get("protocol_id")
            and result.get("protocol_binding") == binding
            and result.get("task_result") == "sharp_uniform_alphabet_parity_frontier"
            and result.get("measurement_reliability")
            == "awaiting_independent_verification"
            and result.get("claim_support") == EXPECTED_CLAIM_SUPPORT
            and result.get("operational_decision") == "await_independent_verification"
            and result.get("claim_boundary") == protocol.get("claim_boundary")
            and isinstance(gates, dict)
            and bool(gates)
            and all(value is True for value in gates.values())
        ),
        "C4_verification_pass_and_gates": bool(
            verification.get("schema_version")
            == "asmp6_balanced_cover_verification_v0_2_1"
            and verification.get("pass") is True
            and fresh_verification.get("pass") is True
            and verification == fresh_verification
            and isinstance(independent_gates, dict)
            and bool(independent_gates)
            and all(value is True for value in independent_gates.values())
            and verification.get("registered_alphabet_sizes") == registered_sizes
        ),
        "C5_verification_binds_protocol_and_primary_result": (
            verification.get("bindings") == expected_verification_bindings
        ),
        "C6_final_conclusion_layers_match_verified_scope": (
            final_layers == EXPECTED_FINAL_LAYERS
        ),
        "C7_claim_boundary_matches_protocol": (
            verification.get("claim_support") == EXPECTED_CLAIM_SUPPORT
            and protocol.get("claim_boundary") == result.get("claim_boundary")
        ),
    }
    passed = all(checks.values())
    conclusion_layers = (
        dict(EXPECTED_FINAL_LAYERS)
        if passed
        else {
            "metric_robustness": "not_established",
            "task_result": "not_established",
            "measurement_reliability": "failed",
            "claim_support": "none",
            "operational_decision": "repair",
        }
    )
    return {
        "schema_version": "asmp6_balanced_cover_final_receipt_v0_2_1",
        "pass": passed,
        "source_commit": source_commit,
        "bindings": {
            "resolved_source_commit": resolved_commit,
            "source_files": current_source_hashes,
            "committed_source_files": committed_source_hashes,
            "artifacts": artifact_hashes,
        },
        "binding_diagnostics": {
            "commit_resolution_error": commit_resolution_error,
            "source_read_errors": source_read_errors,
            "source_mismatches": source_mismatches,
            "verification_replay_matches_artifact": (
                verification == fresh_verification
            ),
        },
        "checks": checks,
        "metric_robustness": conclusion_layers["metric_robustness"],
        "task_result": conclusion_layers["task_result"],
        "measurement_reliability": conclusion_layers["measurement_reliability"],
        "claim_support": conclusion_layers["claim_support"],
        "operational_decision": conclusion_layers["operational_decision"],
        "claim_boundary": protocol.get("claim_boundary", []),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-commit", required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "artifacts_v0_2" / "final_receipt_v0_2.json",
    )
    args = parser.parse_args()
    receipt = build_receipt(
        args.source_commit,
        HERE / "protocol_v0_2.json",
        HERE / "artifacts_v0_2" / "result_v0_2.json",
        HERE / "artifacts_v0_2" / "verification_v0_2.json",
    )
    if not receipt["pass"]:
        failed = [name for name, passed in receipt["checks"].items() if not passed]
        raise SystemExit(f"refusing unbound final receipt; failed checks: {failed}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(canonical_json(receipt), encoding="utf-8", newline="\n")
    print(args.output)


if __name__ == "__main__":
    main()
