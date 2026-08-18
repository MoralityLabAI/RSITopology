from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from itertools import combinations, product
from math import comb
from pathlib import Path


# This verifier intentionally repeats the frozen model. It must not import the
# implementation under review.
N = 16
K0 = 8
K1S = (14, 16)
ALPHA = Fraction(1, 20)
THETAS = (Fraction(1, 2), Fraction(3, 4), Fraction(4, 5), Fraction(1))
COUNTS = (0, 8, 10, 12, 14, 16)
ARMS = ("policy_independent", "adversarial_selective")
CAP = 8192
PROTOCOL_ID = "ASMP-7-METER-COVERAGE-ROBUSTNESS-v0.3"
PROTOCOL_SCHEMA = "asmp7_coverage_robustness_protocol_v0_3"
INDEPENDENT_SEMANTICS = "fresh_per_challenge_event_with_probability_c_over_16"
SELECTIVE_SEMANTICS = "execution_dependent_exact_c_point_mask_fixed_across_challenges"
FIXED_MASK_COUNTERFACTUAL = "out_of_scope_sensitivity_only"
CLAIM_BOUNDARY = (
    "This result concerns a 16-point Boolean registry, fresh per-challenge "
    "policy-independent coverage events, an execution-dependent exact-c-point selective "
    "mask fixed across challenges, fresh fair fallback bits, and independent challenges. "
    "It does not cover an execution-fixed random independent mask, establish real meter "
    "coverage, identify a deployment threshold, characterize adaptive history-dependent "
    "suppression, prove transformation-universal attestability, or resolve ASMP-7."
)
PROTOCOL_KEYS = frozenset(
    {
        "schema_version",
        "protocol_id",
        "domain_size",
        "compliant_boundary",
        "forbidden_boundaries",
        "theta_grid",
        "coverage_counts",
        "models",
        "error_limit",
        "m_cap",
        "independent_coverage_semantics",
        "selective_coverage_semantics",
        "fixed_independent_mask_counterfactual",
        "claim_boundary",
    }
)
SOURCE_FILES = (
    "protocol_v0_3.json",
    "PROTOCOL_v0_3.md",
    "README.md",
    "coverage_robustness.py",
    "run.py",
    "verify_result.py",
    "test_coverage_robustness.py",
)


def _text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _fraction(value: object) -> Fraction:
    left, right = str(value).split("/", 1)
    return Fraction(int(left), int(right))


def _expected_protocol() -> dict[str, object]:
    return {
        "schema_version": PROTOCOL_SCHEMA,
        "protocol_id": PROTOCOL_ID,
        "domain_size": N,
        "compliant_boundary": K0,
        "forbidden_boundaries": list(K1S),
        "theta_grid": [_text(value) for value in THETAS],
        "coverage_counts": list(COUNTS),
        "models": list(ARMS),
        "error_limit": _text(ALPHA),
        "m_cap": CAP,
        "independent_coverage_semantics": INDEPENDENT_SEMANTICS,
        "selective_coverage_semantics": SELECTIVE_SEMANTICS,
        "fixed_independent_mask_counterfactual": FIXED_MASK_COUNTERFACTUAL,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def protocol_binding_checks(protocol: dict[str, object]) -> dict[str, bool]:
    expected = _expected_protocol()
    return {
        "exact_field_set": set(protocol) == PROTOCOL_KEYS,
        **{
            f"field_{name}": protocol.get(name) == expected[name]
            for name in sorted(PROTOCOL_KEYS)
        },
    }


def _diff_paths(expected: object, reported: object, prefix: str = "") -> list[str]:
    if isinstance(expected, dict):
        if not isinstance(reported, dict):
            return [prefix or "$"]
        failures: list[str] = []
        for key in sorted(set(expected) | set(reported)):
            path = f"{prefix}.{key}" if prefix else str(key)
            if key not in expected or key not in reported:
                failures.append(path)
            else:
                failures.extend(_diff_paths(expected[key], reported[key], path))
        return failures
    if isinstance(expected, list):
        if not isinstance(reported, list) or len(expected) != len(reported):
            return [prefix or "$"]
        failures = []
        for index, (left, right) in enumerate(zip(expected, reported)):
            failures.extend(_diff_paths(left, right, f"{prefix}[{index}]"))
        return failures
    return [] if expected == reported else [prefix or "$"]


def _range(k: int, c: int, n: int = N) -> tuple[int, int]:
    return max(0, k + c - n), min(k, c)


def _selective_q(a: int, theta: Fraction, c: int, n: int = N) -> Fraction:
    return Fraction(1, 2) + (2 * theta - 1) * Fraction(2 * a - c, 2 * n)


def _independent_q(k: int, theta: Fraction, c: int) -> Fraction:
    full = (1 - theta) + (2 * theta - 1) * Fraction(k, N)
    return Fraction(1, 2) + Fraction(c, N) * (full - Fraction(1, 2))


def _law(arm: str, k1: int, theta: Fraction, c: int) -> dict[str, object]:
    if arm == "policy_independent":
        q0, q1 = _independent_q(K0, theta, c), _independent_q(k1, theta, c)
        common = q0 == q1
        witness = None
        if common:
            witness = {
                "kind": "identical_bernoulli_law",
                "q": _text(q0),
                "reason": "zero_coverage" if c == 0 else "privacy_channel_kill",
            }
        return {"q0": q0, "q1": q1, "common": common, "witness": witness}

    r0, r1 = _range(K0, c), _range(k1, c)
    q0 = _selective_q(r0[1], theta, c)
    q1 = _selective_q(r1[0], theta, c)
    overlap = max(r0[0], r1[0]) <= min(r0[1], r1[1])
    common = theta == Fraction(1, 2) or overlap
    witness = None
    if theta == Fraction(1, 2):
        witness = {
            "kind": "identical_bernoulli_law",
            "q": "1/2",
            "compliant_covered_agreements": r0[0],
            "forbidden_covered_agreements": r1[0],
            "reason": "privacy_channel_kill",
        }
    elif overlap:
        common_a = max(r0[0], r1[0])
        witness = {
            "kind": "selective_mask_common_law",
            "q": _text(_selective_q(common_a, theta, c)),
            "covered_agreements": common_a,
            "compliant_range": list(r0),
            "forbidden_range": list(r1),
            "reason": "coverage_alignment_overlap",
        }
    return {
        "q0": q0,
        "q1": q1,
        "common": common,
        "witness": witness,
    }


def _masses(m: int, q: Fraction) -> tuple[list[int], int]:
    a, b = q.numerator, q.denominator
    denominator = b**m
    if a == 0:
        return [denominator] + [0] * m, denominator
    if a == b:
        return [0] * m + [denominator], denominator
    complement = b - a
    values = [complement**m]
    for j in range(m):
        values.append(values[-1] * (m - j) * a // ((j + 1) * complement))
    if sum(values) != denominator:
        raise ArithmeticError("verifier binomial recurrence failed")
    return values, denominator


def _test(m: int, q0: Fraction, q1: Fraction) -> dict[str, object]:
    null, null_den = _masses(m, q0)
    cutoff, upper = m, 0
    while Fraction(upper + null[cutoff], null_den) < ALPHA:
        upper += null[cutoff]
        cutoff -= 1
    gamma = (ALPHA - Fraction(upper, null_den)) / Fraction(null[cutoff], null_den)
    alternative, alt_den = _masses(m, q1)
    fn = Fraction(sum(alternative[:cutoff]), alt_den) + (1 - gamma) * Fraction(
        alternative[cutoff], alt_den
    )
    return {"m": m, "cutoff": cutoff, "gamma": gamma, "fp": ALPHA, "fn": fn}


def _minimum(
    q0: Fraction, q1: Fraction
) -> tuple[dict[str, object] | None, dict[str, object] | None, dict[str, object] | None, int]:
    evaluations = 0
    high = 1
    candidate = _test(high, q0, q1)
    evaluations += 1
    while high < CAP and candidate["fn"] > ALPHA:
        high = min(CAP, high * 2)
        candidate = _test(high, q0, q1)
        evaluations += 1
    if candidate["fn"] > ALPHA:
        return None, None, candidate, evaluations
    low = 0
    while low < high:
        middle = (low + high) // 2
        probe = _test(middle, q0, q1)
        evaluations += 1
        if probe["fn"] <= ALPHA:
            high = middle
        else:
            low = middle + 1
    current = _test(low, q0, q1)
    evaluations += 1
    previous = _test(low - 1, q0, q1) if low else None
    if previous is not None:
        evaluations += 1
    return current, previous, None, evaluations


def _test_record(test: dict[str, object]) -> dict[str, object]:
    return {
        "m": test["m"],
        "cutoff": test["cutoff"],
        "gamma": _text(test["gamma"]),
        "fp": _text(test["fp"]),
        "fn": _text(test["fn"]),
    }


def _expected_record(arm: str, k1: int, theta: Fraction, c: int) -> dict[str, object]:
    law = _law(arm, k1, theta, c)
    record: dict[str, object] = {
        "model": arm,
        "k1": k1,
        "theta": _text(theta),
        "coverage_count": c,
        "coverage": _text(Fraction(c, N)),
        "q0_worst": _text(law["q0"]),
        "q1_worst": _text(law["q1"]),
        "effective_delta": _text(Fraction(0) if law["common"] else law["q1"] - law["q0"]),
        "common_law_witness": law["witness"],
    }
    if law["common"]:
        record.update(
            {
                "status": "common_law_impossible",
                "m_star": None,
                "sum_error_lower_bound": "1/1",
                "exact_evaluations": 0,
            }
        )
        return record
    current, previous, cap_test, evaluations = _minimum(law["q0"], law["q1"])
    if current is None:
        assert cap_test is not None
        record.update(
            {
                "status": "infeasible_within_cap",
                "m_star": None,
                "cap": cap_test["m"],
                "cap_test": _test_record(cap_test),
                "exact_evaluations": evaluations,
            }
        )
        return record
    record.update(
        {
            "status": "feasible_exact",
            "m_star": current["m"],
            "test": _test_record(current),
            "predecessor": _test_record(previous) if previous is not None else None,
            "exact_evaluations": evaluations,
        }
    )
    return record


def _small_bruteforce() -> bool:
    universe = range(4)
    for k in range(5):
        for agreement_tuple in combinations(universe, k):
            agreements = set(agreement_tuple)
            for c in range(5):
                attained = {
                    len(agreements.intersection(coverage))
                    for coverage in combinations(universe, c)
                }
                low, high = _range(k, c, 4)
                if attained != set(range(low, high + 1)):
                    return False
    for q in (Fraction(1, 2), Fraction(9, 16), Fraction(3, 4)):
        for m in range(6):
            direct = [Fraction(0) for _ in range(m + 1)]
            for reports in product((0, 1), repeat=m):
                count = sum(reports)
                direct[count] += q**count * (1 - q) ** (m - count)
            formula = [
                Fraction(comb(m, count)) * q**count * (1 - q) ** (m - count)
                for count in range(m + 1)
            ]
            if direct != formula:
                return False
    return True


def _record_index(
    records: list[dict[str, object]],
) -> dict[tuple[str, int, Fraction, int], dict[str, object]]:
    return {
        (str(row["model"]), int(row["k1"]), _fraction(row["theta"]), int(row["coverage_count"])): row
        for row in records
    }


def _derive_gates(records: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    index = _record_index(records)
    adjacency_failures: list[str] = []
    for row in records:
        if row["status"] != "feasible_exact":
            continue
        label = (
            f"{row['model']},k1={row['k1']},theta={row['theta']},"
            f"c={row['coverage_count']}"
        )
        if _fraction(row["test"]["fp"]) != ALPHA or _fraction(row["test"]["fn"]) > ALPHA:
            adjacency_failures.append(f"{label}:test")
        predecessor = row["predecessor"]
        if predecessor is not None and _fraction(predecessor["fn"]) <= ALPHA:
            adjacency_failures.append(f"{label}:predecessor")

    full_expected = {
        (14, Fraction(3, 4)): 73,
        (14, Fraction(4, 5)): 50,
        (14, Fraction(1)): 15,
        (16, Fraction(3, 4)): 40,
        (16, Fraction(4, 5)): 26,
        (16, Fraction(1)): 5,
    }
    reproduction_failures: list[str] = []
    for arm in ARMS:
        for (k1, theta), m_star in full_expected.items():
            row = index[(arm, k1, theta, 16)]
            if row["status"] != "feasible_exact" or row["m_star"] != m_star:
                reproduction_failures.append(
                    f"{arm},k1={k1},theta={_text(theta)}"
                )

    monotonicity_failures: list[str] = []
    for arm in ARMS:
        for k1 in K1S:
            for theta in THETAS:
                previous_m: int | None = None
                previous_live = False
                previous_delta = Fraction(-1)
                for coverage_count in COUNTS:
                    row = index[(arm, k1, theta, coverage_count)]
                    delta = _fraction(row["effective_delta"])
                    label = f"{arm},k1={k1},theta={_text(theta)},c={coverage_count}"
                    if delta < previous_delta:
                        monotonicity_failures.append(f"delta:{label}")
                    previous_delta = delta
                    live = row["status"] == "feasible_exact"
                    if previous_live and not live:
                        monotonicity_failures.append(f"status:{label}")
                    if live and previous_m is not None and int(row["m_star"]) > previous_m:
                        monotonicity_failures.append(f"m:{label}")
                    if live:
                        previous_m = int(row["m_star"])
                        previous_live = True

    common_failures: list[str] = []
    for row in records:
        zero_information = row["theta"] == "1/2" or row["coverage_count"] == 0
        if zero_information and row["status"] != "common_law_impossible":
            common_failures.append(
                f"zero:{row['model']},k1={row['k1']},theta={row['theta']},c={row['coverage_count']}"
            )
        if row["status"] == "common_law_impossible" and (
            row["common_law_witness"] is None
            or row["sum_error_lower_bound"] != "1/1"
        ):
            common_failures.append(
                f"witness:{row['model']},k1={row['k1']},theta={row['theta']},c={row['coverage_count']}"
            )
    for theta in THETAS[1:]:
        if index[("adversarial_selective", 14, theta, 10)]["status"] != "common_law_impossible":
            common_failures.append(f"selective_overlap:k1=14,theta={_text(theta)},c=10")

    cross_model_failures: list[str] = []
    for k1 in K1S:
        for theta in THETAS:
            for coverage_count in COUNTS:
                independent = index[("policy_independent", k1, theta, coverage_count)]
                selective = index[("adversarial_selective", k1, theta, coverage_count)]
                label = f"k1={k1},theta={_text(theta)},c={coverage_count}"
                if _fraction(selective["effective_delta"]) > _fraction(independent["effective_delta"]):
                    cross_model_failures.append(f"delta:{label}")
                if independent["status"] == "common_law_impossible":
                    if selective["status"] != "common_law_impossible":
                        cross_model_failures.append(f"common_law:{label}")
                elif selective["status"] == "common_law_impossible":
                    continue
                elif independent["status"] == "feasible_exact":
                    if selective["status"] == "feasible_exact":
                        if int(selective["m_star"]) < int(independent["m_star"]):
                            cross_model_failures.append(f"burden:{label}")
                    elif selective["status"] != "infeasible_within_cap":
                        cross_model_failures.append(f"status:{label}")
                elif independent["status"] == "infeasible_within_cap" and selective["status"] == "feasible_exact":
                    cross_model_failures.append(f"cap_order:{label}")

    brute_force_pass = _small_bruteforce()
    return {
        "E0_exact_adjacency": {"pass": not adjacency_failures, "failures": adjacency_failures},
        "R0_full_coverage_reproduction": {
            "pass": not reproduction_failures,
            "failures": reproduction_failures,
            "expected_cells": len(full_expected) * len(ARMS),
        },
        "M0_coverage_monotonicity": {
            "pass": not monotonicity_failures,
            "failures": monotonicity_failures,
        },
        "Z0_common_law_zero_information": {
            "pass": not common_failures,
            "failures": common_failures,
        },
        "C0_cross_model_weakening": {
            "pass": not cross_model_failures,
            "failures": cross_model_failures,
        },
        "B0_bruteforce_small_cases": {
            "pass": brute_force_pass,
            "range_failures": [],
            "invariance_failures": [],
            "distribution_failures": [],
            "domain_size": 4,
            "report_lengths": list(range(6)),
        },
    }


def _derive_probes(
    records: list[dict[str, object]], gates: dict[str, dict[str, object]]
) -> dict[str, dict[str, object]]:
    index = _record_index(records)
    ind_half = index[("policy_independent", 14, Fraction(3, 4), 8)]
    ind_full = index[("policy_independent", 14, Fraction(3, 4), 16)]
    ind_three_quarters = index[("policy_independent", 14, Fraction(3, 4), 12)]
    adv_three_quarters = index[("adversarial_selective", 14, Fraction(3, 4), 12)]
    anti_failures = [
        f"theta={_text(theta)}"
        for theta in THETAS[1:]
        if index[("policy_independent", 14, theta, 10)]["status"] != "feasible_exact"
        or index[("adversarial_selective", 14, theta, 10)]["status"]
        != "common_law_impossible"
    ]
    clean_failures = [
        f"k1={k1},theta={_text(theta)}"
        for k1 in K1S
        for theta in THETAS[1:]
        if any(
            (
                index[("policy_independent", k1, theta, 16)]["status"]
                != "feasible_exact",
                index[("adversarial_selective", k1, theta, 16)]["status"]
                != "feasible_exact",
                index[("policy_independent", k1, theta, 16)]["m_star"]
                != index[("adversarial_selective", k1, theta, 16)]["m_star"],
                index[("policy_independent", k1, theta, 16)]["q0_worst"]
                != index[("adversarial_selective", k1, theta, 16)]["q0_worst"],
                index[("policy_independent", k1, theta, 16)]["q1_worst"]
                != index[("adversarial_selective", k1, theta, 16)]["q1_worst"],
            )
        )
    ]
    sensitivity = bool(
        ind_half["status"] == ind_full["status"] == "feasible_exact"
        and int(ind_half["m_star"]) > int(ind_full["m_star"])
        and adv_three_quarters["status"] == ind_three_quarters["status"] == "feasible_exact"
        and int(adv_three_quarters["m_star"]) > int(ind_three_quarters["m_star"])
    )
    return {
        "invariance": {
            "pass": bool(gates["B0_bruteforce_small_cases"]["pass"]),
            "probe": "all n=4 input relabelings preserve attainable covered-agreement sets",
        },
        "sensitivity": {
            "pass": sensitivity,
            "probe": "sample burden responds to coverage loss and selective suppression",
            "independent_m_c8": ind_half["m_star"],
            "independent_m_c16": ind_full["m_star"],
            "independent_m_c12": ind_three_quarters["m_star"],
            "adversarial_m_c12": adv_three_quarters["m_star"],
        },
        "monotonicity": {
            "pass": gates["M0_coverage_monotonicity"]["pass"],
            "probe": "more exact coverage never increases certified burden on the frozen grid",
        },
        "anti_gaming": {
            "pass": not anti_failures,
            "probe": "nominal independent coverage cannot substitute for selective worst-case coverage",
            "failures": anti_failures,
        },
        "clean_control": {
            "pass": not clean_failures and gates["R0_full_coverage_reproduction"]["pass"],
            "probe": "both models collapse to the v0.2.1 full-coverage experiment",
            "failures": clean_failures,
        },
    }


def _expected_payload() -> dict[str, object]:
    records = [
        _expected_record(arm, k1, theta, coverage_count)
        for arm in ARMS
        for k1 in K1S
        for theta in THETAS
        for coverage_count in COUNTS
    ]
    gates = _derive_gates(records)
    probes = _derive_probes(records, gates)
    reliability_gate_names = (
        "E0_exact_adjacency",
        "R0_full_coverage_reproduction",
        "B0_bruteforce_small_cases",
    )
    measurement_reliable = all(gates[name]["pass"] for name in reliability_gate_names)
    claim_gate_names = (
        "M0_coverage_monotonicity",
        "Z0_common_law_zero_information",
        "C0_cross_model_weakening",
    )
    claim_supported = bool(
        measurement_reliable
        and all(gates[name]["pass"] for name in claim_gate_names)
        and all(probe["pass"] for probe in probes.values())
    )
    task_status = (
        "not_evaluated_invalid_measurement"
        if not measurement_reliable
        else "selective_suppression_weakens_registered_attestability"
        if probes["sensitivity"]["pass"] and probes["anti_gaming"]["pass"]
        else "registered_coverage_contrast_not_established"
    )
    return {
        "experiment_id": PROTOCOL_ID,
        "protocol_schema": PROTOCOL_SCHEMA,
        "coverage_semantics": {
            "policy_independent": INDEPENDENT_SEMANTICS,
            "adversarial_selective": SELECTIVE_SEMANTICS,
            "fixed_independent_mask_counterfactual": FIXED_MASK_COUNTERFACTUAL,
        },
        "evidence_class": "exact_finite_rational_composite_testing",
        "protocol_constants": {
            "domain_size": N,
            "compliant_boundary": K0,
            "forbidden_boundaries": list(K1S),
            "theta_grid": [_text(value) for value in THETAS],
            "coverage_counts": list(COUNTS),
            "models": list(ARMS),
            "error_limit": _text(ALPHA),
            "m_cap": CAP,
        },
        "task_result": {
            "status": task_status,
            "basis": "exact comparison of policy-independent coverage and adversarial selective suppression",
        },
        "measurement_reliability": {
            "status": "reliable_exact_finite_measurement"
            if measurement_reliable
            else "unreliable_measurement",
            "gate_names": list(reliability_gate_names),
            "all_pass": measurement_reliable,
        },
        "claim_support": {
            "status": "registered_finite_claim_supported"
            if claim_supported
            else "claim_not_supported",
            "claim": (
                "On the frozen Boolean grid, selective suppression can create an exact common-law "
                "region and otherwise weakly increases audit burden relative to policy-independent coverage."
            ),
            "all_pass": claim_supported,
        },
        "operational_decision": {
            "status": "no_deployment_decision_authorized",
            "reason": "synthetic finite registry with no validated real-meter or deployment bridge",
        },
        "gates": gates,
        "metric_robustness_probes": probes,
        "records": records,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def verify_payload(payload: dict[str, object]) -> dict[str, object]:
    expected = _expected_payload()
    failures = _diff_paths(expected, payload)
    return {
        "pass": not failures,
        "failures": failures,
        "records_checked": len(expected["records"]),
        "independent_bruteforce": bool(
            expected["gates"]["B0_bruteforce_small_cases"]["pass"]
        ),
        "implementation_imported": False,
        "derived_conclusion_layers": {
            "task_result": expected["task_result"],
            "measurement_reliability": expected["measurement_reliability"],
            "claim_support": expected["claim_support"],
            "operational_decision": expected["operational_decision"],
            "claim_boundary": expected["claim_boundary"],
        },
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def verify_artifact_bundle(
    artifact_dir: Path, source_root: Path | None = None
) -> dict[str, object]:
    source_root = source_root or Path(__file__).resolve().parent
    protocol_path = source_root / "protocol_v0_3.json"
    result_path = artifact_dir / "result.json"
    receipt_path = artifact_dir / "receipt.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    verification = verify_payload(payload)
    protocol_binding = protocol_binding_checks(protocol)
    current_source_hashes = {
        name: sha256_file(source_root / name) for name in SOURCE_FILES
    }
    expected_receipt_keys = {
        "schema_version",
        "experiment_id",
        "executed_utc",
        "protocol_sha256",
        "result_sha256",
        "source_hashes",
        "protocol_binding",
        "environment",
    }
    environment = receipt.get("environment")
    binding_gates = {
        "V0_exact_registered_protocol": all(protocol_binding.values()),
        "V1_result_recomputed_exactly": verification["pass"],
        "V2_run_receipt_schema_exact": bool(
            set(receipt) == expected_receipt_keys
            and receipt.get("schema_version")
            == "asmp7_coverage_robustness_run_receipt_v0_3_1"
            and receipt.get("experiment_id") == PROTOCOL_ID
            and isinstance(receipt.get("executed_utc"), str)
            and bool(receipt.get("executed_utc"))
            and isinstance(environment, dict)
            and set(environment) == {"python", "implementation", "arithmetic", "gpu"}
            and environment.get("arithmetic")
            == "integer binomial masses and fractions.Fraction"
            and environment.get("gpu") == "not used"
        ),
        "V3_protocol_hash_bound": receipt.get("protocol_sha256")
        == sha256_file(protocol_path),
        "V4_result_hash_bound": receipt.get("result_sha256")
        == sha256_file(result_path),
        "V5_exact_source_set_and_hashes_bound": receipt.get("source_hashes")
        == current_source_hashes,
        "V6_protocol_binding_report_bound": receipt.get("protocol_binding")
        == protocol_binding,
    }
    verification["binding_gates"] = binding_gates
    verification["pass"] = verification["pass"] and all(binding_gates.values())
    verification["bindings"] = {
        "protocol_v0_3.json": sha256_file(protocol_path),
        "result.json": sha256_file(result_path),
        "receipt.json": sha256_file(receipt_path),
        "source_files": current_source_hashes,
    }
    return verification


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    verification_path = args.artifact_dir / "verification.json"
    bundle_receipt_path = args.artifact_dir / "bundle_receipt.json"
    if (verification_path.exists() or bundle_receipt_path.exists()) and not args.force:
        raise RuntimeError("verification output exists; use --force for an explicit replay")
    verification = verify_artifact_bundle(args.artifact_dir)
    write_json(verification_path, verification)
    bundle_receipt = {
        "schema_version": "asmp7_coverage_robustness_bundle_receipt_v0_3_1",
        "pass": verification["pass"],
        "bindings": {
            **verification["bindings"],
            "verification.json": sha256_file(verification_path),
        },
        "derived_conclusion_layers": verification["derived_conclusion_layers"],
    }
    write_json(bundle_receipt_path, bundle_receipt)
    print(json.dumps(verification, indent=2))
    if not verification["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
