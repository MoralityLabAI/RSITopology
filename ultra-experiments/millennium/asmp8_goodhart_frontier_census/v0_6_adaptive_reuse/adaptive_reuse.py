"""Exact adaptive partial-census certificate for ASMP-8 v0.6."""

from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


FROZEN_PROTOCOL_ID = "ASMP8-ADAPTIVE-REUSE-v0.6"
FROZEN_PROTOCOL_SCHEMA = "asmp8_adaptive_reuse_protocol_v0_6"
FROZEN_ALPHABET_SIZE = 6
FROZEN_ERROR_ALPHABET = (-1, 0, 1)
FROZEN_ERROR_CAP = 1
FROZEN_POLICY_MASS_MOVE = "1/6"
FROZEN_CLAIM_BOUNDARY = (
    "deterministic bounded errors on enumerable atoms only",
    "no stochastic optional-stopping or learned-policy claim",
    "no ASMP-8 resolution claim",
)
FROZEN_PROTOCOL_KEYS = frozenset(
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


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def frozen_protocol() -> dict[str, Any]:
    return {
        "alphabet_size": FROZEN_ALPHABET_SIZE,
        "claim_boundary": list(FROZEN_CLAIM_BOUNDARY),
        "error_alphabet": list(FROZEN_ERROR_ALPHABET),
        "error_cap": FROZEN_ERROR_CAP,
        "policy_mass_move": FROZEN_POLICY_MASS_MOVE,
        "protocol_id": FROZEN_PROTOCOL_ID,
        "schema_version": FROZEN_PROTOCOL_SCHEMA,
    }


def protocol_binding_checks(protocol: dict[str, Any]) -> dict[str, bool]:
    expected = frozen_protocol()
    return {
        "exact_field_set": set(protocol) == FROZEN_PROTOCOL_KEYS,
        **{
            f"field_{name}": protocol.get(name) == expected[name]
            for name in sorted(FROZEN_PROTOCOL_KEYS)
        },
    }


def validate_protocol(protocol: dict[str, Any]) -> dict[str, bool]:
    checks = protocol_binding_checks(protocol)
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise ValueError(f"protocol binding failed: {failures}")
    return checks


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def dot(left: Iterable[Fraction], right: Iterable[Fraction]) -> Fraction:
    return sum((a * b for a, b in zip(left, right)), Fraction())


def policy_registry(size: int) -> list[dict[str, Any]]:
    if size < 2:
        raise ValueError("size must be at least two")
    proxy = tuple(Fraction(index, size - 1) for index in range(size))
    move = Fraction(1, size)
    policies = []
    for source in range(size):
        for target in range(size):
            if source == target:
                continue
            displacement = [Fraction()] * size
            displacement[source] = -move
            displacement[target] = move
            distribution = [move + value for value in displacement]
            policies.append(
                {
                    "policy_id": f"move_{source}_to_{target}",
                    "source": source,
                    "target": target,
                    "displacement": tuple(displacement),
                    "distribution": tuple(distribution),
                    "proxy_gain": dot(displacement, proxy),
                }
            )
    return policies


def observed_score(policy: dict[str, Any], errors: tuple[Fraction, ...], mask: int) -> Fraction:
    return policy["proxy_gain"] + sum(
        (value * errors[index] for index, value in enumerate(policy["displacement"]) if mask & (1 << index)),
        Fraction(),
    )


def robust_lower_bound(
    policy: dict[str, Any], errors: tuple[Fraction, ...], mask: int, cap: Fraction
) -> Fraction:
    observed = observed_score(policy, errors, mask)
    unseen = sum(
        (abs(value) * cap for index, value in enumerate(policy["displacement"]) if not mask & (1 << index)),
        Fraction(),
    )
    return observed - unseen


def true_gain(policy: dict[str, Any], errors: tuple[Fraction, ...]) -> Fraction:
    return policy["proxy_gain"] + dot(policy["displacement"], errors)


def select_policy(policies: list[dict[str, Any]], errors: tuple[Fraction, ...], mask: int):
    return max(policies, key=lambda policy: (observed_score(policy, errors, mask), policy["policy_id"]))


def reveal_next(policy: dict[str, Any], mask: int, size: int) -> int:
    unseen = [index for index in range(size) if not mask & (1 << index)]
    if not unseen:
        raise ValueError("full census has no next atom")
    return max(unseen, key=lambda index: (abs(policy["displacement"][index]), -index))


def error_vectors(size: int, alphabet: tuple[int, ...] = (-1, 0, 1)):
    for row in itertools.product(alphabet, repeat=size):
        yield tuple(Fraction(value) for value in row)


def pointwise_census(size: int, cap: Fraction) -> dict[str, Any]:
    policies = policy_registry(size)
    full_mask = (1 << size) - 1
    total = robust_failures = full_failures = naive_false = robust_positive = 0
    first_naive_witness = None
    digest = hashlib.sha256()
    for errors in error_vectors(size):
        for mask in range(1 << size):
            for policy in policies:
                lower = robust_lower_bound(policy, errors, mask, cap)
                exact = true_gain(policy, errors)
                naive = observed_score(policy, errors, mask)
                total += 1
                robust_failures += int(lower > exact)
                full_failures += int(mask == full_mask and lower != exact)
                robust_positive += int(lower > 0)
                if naive > 0 and exact <= 0:
                    naive_false += 1
                    if first_naive_witness is None:
                        first_naive_witness = {
                            "errors": [fraction_text(value) for value in errors],
                            "mask": mask,
                            "policy_id": policy["policy_id"],
                            "naive_score": fraction_text(naive),
                            "robust_lower_bound": fraction_text(lower),
                            "true_gain": fraction_text(exact),
                        }
                digest.update(
                    f"{','.join(map(str, errors))}|{mask}|{policy['policy_id']}|{lower}|{exact}\n".encode()
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


def adaptive_census(size: int, cap: Fraction) -> dict[str, Any]:
    policies = policy_registry(size)
    robust_false = naive_false = traces_with_naive_false = 0
    first_witness = None
    trace_count = 0
    for errors in error_vectors(size):
        mask = 0
        trace_has_naive_false = False
        for audits in range(size + 1):
            policy = select_policy(policies, errors, mask)
            naive = observed_score(policy, errors, mask)
            lower = robust_lower_bound(policy, errors, mask, cap)
            exact = true_gain(policy, errors)
            robust_false += int(lower > 0 and exact <= 0)
            if naive > 0 and exact <= 0:
                naive_false += 1
                trace_has_naive_false = True
                if first_witness is None:
                    first_witness = {
                        "audits": audits,
                        "errors": [fraction_text(value) for value in errors],
                        "mask": mask,
                        "policy_id": policy["policy_id"],
                        "naive_score": fraction_text(naive),
                        "robust_lower_bound": fraction_text(lower),
                        "true_gain": fraction_text(exact),
                    }
            if audits < size:
                mask |= 1 << reveal_next(policy, mask, size)
        trace_count += 1
        traces_with_naive_false += int(trace_has_naive_false)
    return {
        "adaptive_traces": trace_count,
        "adaptive_robust_false_declarations": robust_false,
        "adaptive_naive_false_declarations": naive_false,
        "traces_with_naive_false_declaration": traces_with_naive_false,
        "first_adaptive_naive_false_witness": first_witness,
    }


def local_monotonicity_failures(size: int, cap: Fraction) -> int:
    """Check the one-coordinate reveal increment for every local value."""

    coefficients = (Fraction(-1, size), Fraction(), Fraction(1, size))
    return sum(
        1
        for coefficient in coefficients
        for error in (Fraction(-1), Fraction(), Fraction(1))
        if coefficient * error + abs(coefficient) * cap < 0
    )


def robustness_probes(summary: dict[str, Any], size: int, cap: Fraction) -> dict[str, dict[str, Any]]:
    policies = policy_registry(size)
    policy = policies[3]
    errors = tuple(Fraction(value) for value in (-1, 0, 1, -1, 1, 0))
    mask = 0b101011
    permutation = (4, 0, 5, 2, 1, 3)
    inverse = {old: new for new, old in enumerate(permutation)}
    transformed = {
        **policy,
        "displacement": tuple(policy["displacement"][old] for old in permutation),
    }
    transformed_errors = tuple(errors[old] for old in permutation)
    transformed_mask = sum(1 << inverse[index] for index in range(size) if mask & (1 << index))
    original_bound = robust_lower_bound(policy, errors, mask, cap)
    permuted_bound = robust_lower_bound(transformed, transformed_errors, transformed_mask, cap)
    stricter_cap = robust_lower_bound(policy, errors, mask, cap * 2)
    return {
        "invariance": {
            "pass": original_bound == permuted_bound,
            "probe": "joint_atom_relabeling",
        },
        "sensitivity": {
            "pass": stricter_cap <= original_bound and stricter_cap != original_bound,
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


def compile_result(protocol: dict[str, Any]) -> dict[str, Any]:
    protocol_binding = validate_protocol(protocol)
    size = int(protocol["alphabet_size"])
    cap = Fraction(int(protocol["error_cap"]))
    policies = policy_registry(size)
    pointwise = pointwise_census(size, cap)
    adaptive = adaptive_census(size, cap)
    summary = {
        "policy_count": len(policies),
        "policy_probability_failures": sum(
            int(min(policy["distribution"]) < 0 or sum(policy["distribution"]) != 1)
            for policy in policies
        ),
        "pointwise": pointwise,
        "adaptive": adaptive,
        "local_monotonicity_failures": local_monotonicity_failures(size, cap),
    }
    probes = robustness_probes(summary, size, cap)
    gates = {
        "G0_policy_feasibility": summary["policy_count"] == size * (size - 1)
        and summary["policy_probability_failures"] == 0,
        "G1_pointwise_soundness": pointwise["pointwise_cells"] == 729 * 64 * 30
        and pointwise["robust_soundness_failures"] == 0,
        "G2_reveal_monotonicity": summary["local_monotonicity_failures"] == 0,
        "G3_full_census_exactness": pointwise["full_census_failures"] == 0,
        "G4_adaptive_soundness": adaptive["adaptive_robust_false_declarations"] == 0,
        "G5_plugin_negative_control": adaptive["adaptive_naive_false_declarations"] > 0,
        "G6_metric_robustness": all(record["pass"] for record in probes.values()),
    }
    passed = all(gates.values())
    return {
        "schema_version": "asmp8_adaptive_reuse_result_v0_6",
        "protocol_id": protocol["protocol_id"],
        "protocol_binding": protocol_binding,
        "protocol_constants": {
            "alphabet_size": size,
            "error_alphabet": list(FROZEN_ERROR_ALPHABET),
            "error_cap": int(protocol["error_cap"]),
            "policy_mass_move": protocol["policy_mass_move"],
        },
        "metric_robustness": probes,
        "task_result": "adaptive_pointwise_certificate_sound" if passed else "not_established",
        "measurement_reliability": "pending_independent_complete_replay" if passed else "failed",
        "claim_support": "deterministic_finite_adaptive_audit_reuse" if passed else "none",
        "operational_decision": "retain_bound_require_new_noisy_label_protocol" if passed else "repair",
        "gates": gates,
        "summary": summary,
        "claim_boundary": protocol["claim_boundary"],
    }


def load_protocol(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
