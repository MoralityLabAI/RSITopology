"""Import-independent exhaustive replay for ASMP-8 v0.6.

The verifier freezes the protocol independently, reconstructs the complete
pointwise and adaptive summaries with scaled integer arithmetic, derives every
gate and conclusion layer, and binds the protocol, primary result, run receipt,
source files, and verification artifact.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
N = 6
ERROR_ALPHABET = (-1, 0, 1)
ERROR_CAP = 1
PROTOCOL_ID = "ASMP8-ADAPTIVE-REUSE-v0.6"
PROTOCOL_SCHEMA = "asmp8_adaptive_reuse_protocol_v0_6"
RESULT_SCHEMA = "asmp8_adaptive_reuse_result_v0_6"
POLICY_MASS_MOVE = "1/6"
CLAIM_BOUNDARY = (
    "deterministic bounded errors on enumerable atoms only",
    "no stochastic optional-stopping or learned-policy claim",
    "no ASMP-8 resolution claim",
)
PROTOCOL_KEYS = frozenset(
    {
        "alphabet_size",
        "claim_boundary",
        "error_alphabet",
        "error_cap",
        "policy_mass_move",
        "protocol_id",
        "schema_version",
    }
)
SOURCE_FILES = (
    "adaptive_reuse.py",
    "protocol_v0_6.json",
    "PROTOCOL_v0_6.md",
    "README.md",
    "run.py",
    "verify_independent.py",
    "test_adaptive_reuse.py",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def expected_protocol() -> dict[str, Any]:
    return {
        "alphabet_size": N,
        "claim_boundary": list(CLAIM_BOUNDARY),
        "error_alphabet": list(ERROR_ALPHABET),
        "error_cap": ERROR_CAP,
        "policy_mass_move": POLICY_MASS_MOVE,
        "protocol_id": PROTOCOL_ID,
        "schema_version": PROTOCOL_SCHEMA,
    }


def protocol_binding_checks(protocol: dict[str, Any]) -> dict[str, bool]:
    expected = expected_protocol()
    return {
        "exact_field_set": set(protocol) == PROTOCOL_KEYS,
        **{
            f"field_{name}": protocol.get(name) == expected[name]
            for name in sorted(PROTOCOL_KEYS)
        },
    }


def policies() -> tuple[tuple[str, int, int], ...]:
    return tuple(
        (f"move_{source}_to_{target}", source, target)
        for source in range(N)
        for target in range(N)
        if source != target
    )


def score_numerators(
    policy: tuple[str, int, int],
    errors: tuple[int, ...],
    mask: int,
    cap: int = ERROR_CAP,
    proxy_numerator: int | None = None,
) -> tuple[int, int, int]:
    """Return observed, lower, and exact gains on the common denominator 30."""

    _name, source, target = policy
    proxy = target - source if proxy_numerator is None else proxy_numerator
    observed = proxy
    if mask & (1 << target):
        observed += 5 * errors[target]
    if mask & (1 << source):
        observed -= 5 * errors[source]
    unseen_penalty = 5 * cap * (
        int(not mask & (1 << source)) + int(not mask & (1 << target))
    )
    lower = observed - unseen_penalty
    exact = proxy + 5 * (errors[target] - errors[source])
    return observed, lower, exact


def _fraction30(numerator: int) -> Fraction:
    return Fraction(numerator, 30)


def policy_probability_failures() -> int:
    failures = 0
    for _name, source, target in policies():
        distribution = [Fraction(1, N)] * N
        distribution[source] -= Fraction(1, N)
        distribution[target] += Fraction(1, N)
        failures += int(min(distribution) < 0 or sum(distribution) != 1)
    return failures


def pointwise_replay() -> dict[str, Any]:
    total = robust_failures = full_failures = naive_false = robust_positive = 0
    first_naive_witness = None
    full_mask = (1 << N) - 1
    digest = hashlib.sha256()
    for errors in itertools.product(ERROR_ALPHABET, repeat=N):
        for mask in range(1 << N):
            for policy in policies():
                observed, lower, exact = score_numerators(policy, errors, mask)
                total += 1
                robust_failures += int(lower > exact)
                full_failures += int(mask == full_mask and lower != exact)
                robust_positive += int(lower > 0)
                if observed > 0 and exact <= 0:
                    naive_false += 1
                    if first_naive_witness is None:
                        first_naive_witness = {
                            "errors": [fraction_text(Fraction(value)) for value in errors],
                            "mask": mask,
                            "policy_id": policy[0],
                            "naive_score": fraction_text(_fraction30(observed)),
                            "robust_lower_bound": fraction_text(_fraction30(lower)),
                            "true_gain": fraction_text(_fraction30(exact)),
                        }
                digest.update(
                    (
                        f"{','.join(map(str, errors))}|{mask}|{policy[0]}|"
                        f"{_fraction30(lower)}|{_fraction30(exact)}\n"
                    ).encode()
                )
    return {
        "pointwise_cells": total,
        "robust_soundness_failures": robust_failures,
        "full_census_failures": full_failures,
        "naive_false_declarations": naive_false,
        "robust_positive_cells": robust_positive,
        "first_naive_false_witness": first_naive_witness,
        "pointwise_digest_sha256": digest.hexdigest(),
    }


def select_policy(
    errors: tuple[int, ...], mask: int
) -> tuple[str, int, int]:
    return max(
        policies(),
        key=lambda policy: (score_numerators(policy, errors, mask)[0], policy[0]),
    )


def reveal_next(policy: tuple[str, int, int], mask: int) -> int:
    _name, source, target = policy
    unseen = [index for index in range(N) if not mask & (1 << index)]
    return max(
        unseen,
        key=lambda index: (int(index in (source, target)), -index),
    )


def adaptive_replay() -> dict[str, Any]:
    robust_false = naive_false = traces_with_naive_false = trace_count = 0
    first_witness = None
    for errors in itertools.product(ERROR_ALPHABET, repeat=N):
        mask = 0
        trace_has_naive_false = False
        for audits in range(N + 1):
            policy = select_policy(errors, mask)
            observed, lower, exact = score_numerators(policy, errors, mask)
            robust_false += int(lower > 0 and exact <= 0)
            if observed > 0 and exact <= 0:
                naive_false += 1
                trace_has_naive_false = True
                if first_witness is None:
                    first_witness = {
                        "audits": audits,
                        "errors": [fraction_text(Fraction(value)) for value in errors],
                        "mask": mask,
                        "policy_id": policy[0],
                        "naive_score": fraction_text(_fraction30(observed)),
                        "robust_lower_bound": fraction_text(_fraction30(lower)),
                        "true_gain": fraction_text(_fraction30(exact)),
                    }
            if audits < N:
                mask |= 1 << reveal_next(policy, mask)
        trace_count += 1
        traces_with_naive_false += int(trace_has_naive_false)
    return {
        "adaptive_traces": trace_count,
        "adaptive_robust_false_declarations": robust_false,
        "adaptive_naive_false_declarations": naive_false,
        "traces_with_naive_false_declaration": traces_with_naive_false,
        "first_adaptive_naive_false_witness": first_witness,
    }


def local_monotonicity_failures() -> int:
    return sum(
        1
        for coefficient in (-1, 0, 1)
        for error in ERROR_ALPHABET
        if coefficient * error + abs(coefficient) * ERROR_CAP < 0
    )


def robustness_probes(summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    # Reconstruct the registered relabeling/sensitivity fixture independently.
    policy = policies()[3]
    errors = (-1, 0, 1, -1, 1, 0)
    mask = 0b101011
    permutation = (4, 0, 5, 2, 1, 3)
    inverse = {old: new for new, old in enumerate(permutation)}
    _name, source, target = policy
    transformed_errors = tuple(errors[old] for old in permutation)
    transformed_source = inverse[source]
    transformed_target = inverse[target]
    transformed_policy = (policy[0], transformed_source, transformed_target)
    transformed_mask = sum(
        1 << inverse[index] for index in range(N) if mask & (1 << index)
    )
    original_bound = score_numerators(policy, errors, mask)[1]
    permuted_bound = score_numerators(
        transformed_policy,
        transformed_errors,
        transformed_mask,
        proxy_numerator=target - source,
    )[1]
    stricter_bound = score_numerators(policy, errors, mask, cap=2)[1]
    return {
        "invariance": {
            "pass": original_bound == permuted_bound,
            "probe": "joint_atom_relabeling",
        },
        "sensitivity": {
            "pass": stricter_bound <= original_bound and stricter_bound != original_bound,
            "probe": "double_error_cap",
        },
        "monotonicity": {
            "pass": summary["local_monotonicity_failures"] == 0,
            "probe": "one_more_revealed_atom_fixed_policy",
        },
        "anti_gaming": {
            "pass": summary["adaptive"]["adaptive_naive_false_declarations"] > 0
            and summary["adaptive"]["adaptive_robust_false_declarations"] == 0,
            "probe": "adaptive_plugin_selection",
        },
        "clean_control": {
            "pass": summary["pointwise"]["full_census_failures"] == 0,
            "probe": "full_census_equals_true_gain",
        },
    }


@lru_cache(maxsize=1)
def expected_result() -> dict[str, Any]:
    pointwise = pointwise_replay()
    adaptive = adaptive_replay()
    summary = {
        "policy_count": len(policies()),
        "policy_probability_failures": policy_probability_failures(),
        "pointwise": pointwise,
        "adaptive": adaptive,
        "local_monotonicity_failures": local_monotonicity_failures(),
    }
    probes = robustness_probes(summary)
    gates = {
        "G0_policy_feasibility": summary["policy_count"] == N * (N - 1)
        and summary["policy_probability_failures"] == 0,
        "G1_pointwise_soundness": pointwise["pointwise_cells"]
        == len(ERROR_ALPHABET) ** N * 2**N * N * (N - 1)
        and pointwise["robust_soundness_failures"] == 0,
        "G2_reveal_monotonicity": summary["local_monotonicity_failures"] == 0,
        "G3_full_census_exactness": pointwise["full_census_failures"] == 0,
        "G4_adaptive_soundness": adaptive["adaptive_robust_false_declarations"] == 0,
        "G5_plugin_negative_control": adaptive["adaptive_naive_false_declarations"] > 0,
        "G6_metric_robustness": all(record["pass"] for record in probes.values()),
    }
    passed = all(gates.values())
    binding = protocol_binding_checks(expected_protocol())
    return {
        "schema_version": RESULT_SCHEMA,
        "protocol_id": PROTOCOL_ID,
        "protocol_binding": binding,
        "protocol_constants": {
            "alphabet_size": N,
            "error_alphabet": list(ERROR_ALPHABET),
            "error_cap": ERROR_CAP,
            "policy_mass_move": POLICY_MASS_MOVE,
        },
        "metric_robustness": probes,
        "task_result": "adaptive_pointwise_certificate_sound" if passed else "not_established",
        "measurement_reliability": "pending_independent_complete_replay" if passed else "failed",
        "claim_support": "deterministic_finite_adaptive_audit_reuse" if passed else "none",
        "operational_decision": "retain_bound_require_new_noisy_label_protocol" if passed else "repair",
        "gates": gates,
        "summary": summary,
        "claim_boundary": list(CLAIM_BOUNDARY),
    }


def diff_paths(expected: object, reported: object, prefix: str = "") -> list[str]:
    if isinstance(expected, dict):
        if not isinstance(reported, dict):
            return [prefix or "$"]
        failures: list[str] = []
        for key in sorted(set(expected) | set(reported)):
            path = f"{prefix}.{key}" if prefix else str(key)
            if key not in expected or key not in reported:
                failures.append(path)
            else:
                failures.extend(diff_paths(expected[key], reported[key], path))
        return failures
    if isinstance(expected, list):
        if not isinstance(reported, list) or len(expected) != len(reported):
            return [prefix or "$"]
        failures: list[str] = []
        for index, (left, right) in enumerate(zip(expected, reported)):
            failures.extend(diff_paths(left, right, f"{prefix}[{index}]"))
        return failures
    return [] if expected == reported else [prefix or "$"]


def verify_payload(protocol: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    binding = protocol_binding_checks(protocol)
    expected = expected_result()
    mismatches = diff_paths(expected, result)
    gates = {
        "V0_exact_registered_protocol": all(binding.values()),
        "V1_exact_result_schema_and_key_universe": bool(
            set(result) == set(expected)
            and result.get("schema_version") == RESULT_SCHEMA
            and result.get("protocol_id") == PROTOCOL_ID
            and result.get("protocol_binding") == expected["protocol_binding"]
            and result.get("protocol_constants") == expected["protocol_constants"]
        ),
        "V2_pointwise_census_replayed": not any(
            path.startswith("summary.pointwise") for path in mismatches
        ),
        "V3_adaptive_policy_and_audit_replayed": not any(
            path.startswith("summary.adaptive") for path in mismatches
        ),
        "V4_policy_and_monotonicity_replayed": not any(
            path.startswith("summary.policy")
            or path == "summary.local_monotonicity_failures"
            for path in mismatches
        ),
        "V5_metric_probes_and_primary_gates_derived": not any(
            path.startswith("metric_robustness") or path.startswith("gates")
            for path in mismatches
        ),
        "V6_conclusion_layers_and_boundary_derived": not any(
            path in {
                "task_result",
                "measurement_reliability",
                "claim_support",
                "operational_decision",
                "claim_boundary",
            }
            or path.startswith("claim_boundary[")
            for path in mismatches
        ),
        "V7_complete_payload_matches": not mismatches,
    }
    passed = all(gates.values())
    final_layers = {
        "task_result": expected["task_result"] if passed else "not_established",
        "measurement_reliability": (
            "independent_complete_pointwise_and_adaptive_replay_passed"
            if passed
            else "failed"
        ),
        "claim_support": expected["claim_support"] if passed else "none",
        "operational_decision": expected["operational_decision"] if passed else "repair",
        "claim_boundary": expected["claim_boundary"],
    }
    return {
        "schema_version": "asmp8_adaptive_reuse_verification_v0_6_1",
        "pass": passed,
        "implementation_imported": False,
        "protocol_binding": binding,
        "independent_gates": gates,
        "mismatch_paths": mismatches,
        "replayed_pointwise_cells": expected["summary"]["pointwise"]["pointwise_cells"],
        "replayed_adaptive_traces": expected["summary"]["adaptive"]["adaptive_traces"],
        "derived_primary_gates": expected["gates"],
        "derived_conclusion_layers": final_layers,
        # Compatibility fields are derived, never copied from the primary result.
        "measurement_reliability": final_layers["measurement_reliability"],
        "claim_support": final_layers["claim_support"],
        "operational_decision": final_layers["operational_decision"],
    }


def verify_artifact_bundle(
    artifact_dir: Path, source_root: Path | None = None
) -> dict[str, Any]:
    source_root = source_root or HERE
    protocol_path = source_root / "protocol_v0_6.json"
    result_path = artifact_dir / "result_v0_6.json"
    receipt_path = artifact_dir / "run_receipt_v0_6.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    verification = verify_payload(protocol, result)
    current_source_hashes = {
        name: sha256_file(source_root / name) for name in SOURCE_FILES
    }
    expected_receipt_keys = {
        "schema_version",
        "protocol_id",
        "executed_utc",
        "protocol_sha256",
        "result_sha256",
        "source_hashes",
        "protocol_binding",
        "environment",
    }
    environment = receipt.get("environment")
    binding_gates = {
        "B0_run_receipt_schema_exact": bool(
            set(receipt) == expected_receipt_keys
            and receipt.get("schema_version")
            == "asmp8_adaptive_reuse_run_receipt_v0_6_1"
            and receipt.get("protocol_id") == PROTOCOL_ID
            and isinstance(receipt.get("executed_utc"), str)
            and bool(receipt.get("executed_utc"))
            and isinstance(environment, dict)
            and set(environment) == {"python", "implementation", "arithmetic", "gpu"}
            and environment.get("arithmetic") == "fractions.Fraction"
            and environment.get("gpu") == "not used"
        ),
        "B1_protocol_hash_bound": receipt.get("protocol_sha256")
        == sha256_file(protocol_path),
        "B2_result_hash_bound": receipt.get("result_sha256")
        == sha256_file(result_path),
        "B3_exact_source_set_and_hashes_bound": receipt.get("source_hashes")
        == current_source_hashes,
        "B4_protocol_binding_report_bound": receipt.get("protocol_binding")
        == protocol_binding_checks(protocol),
    }
    verification["binding_gates"] = binding_gates
    verification["pass"] = verification["pass"] and all(binding_gates.values())
    if not verification["pass"]:
        verification["measurement_reliability"] = "failed"
        verification["claim_support"] = "none"
        verification["operational_decision"] = "repair"
        verification["derived_conclusion_layers"] = {
            **verification["derived_conclusion_layers"],
            "measurement_reliability": "failed",
            "claim_support": "none",
            "operational_decision": "repair",
        }
    verification["bindings"] = {
        "protocol_v0_6.json": sha256_file(protocol_path),
        "result_v0_6.json": sha256_file(result_path),
        "run_receipt_v0_6.json": sha256_file(receipt_path),
        "source_files": current_source_hashes,
    }
    return verification


def main() -> None:
    artifact_dir = HERE / "artifacts_v0_6"
    verification = verify_artifact_bundle(artifact_dir)
    output = artifact_dir / "verification_v0_6.json"
    output.write_text(canonical_json(verification), encoding="utf-8", newline="\n")
    bundle_receipt = {
        "schema_version": "asmp8_adaptive_reuse_bundle_receipt_v0_6_1",
        "pass": verification["pass"],
        "bindings": {
            **verification["bindings"],
            "verification_v0_6.json": sha256_file(output),
        },
        "derived_conclusion_layers": verification["derived_conclusion_layers"],
    }
    bundle_path = artifact_dir / "bundle_receipt_v0_6.json"
    bundle_path.write_text(canonical_json(bundle_receipt), encoding="utf-8", newline="\n")
    print(json.dumps(verification, indent=2))
    if not verification["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
