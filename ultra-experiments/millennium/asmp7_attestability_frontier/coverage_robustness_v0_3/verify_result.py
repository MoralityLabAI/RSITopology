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


def _text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _fraction(value: object) -> Fraction:
    left, right = str(value).split("/", 1)
    return Fraction(int(left), int(right))


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
        return {"q0": q0, "q1": q1, "common": common}

    r0, r1 = _range(K0, c), _range(k1, c)
    q0 = _selective_q(r0[1], theta, c)
    q1 = _selective_q(r1[0], theta, c)
    overlap = max(r0[0], r1[0]) <= min(r0[1], r1[1])
    return {"q0": q0, "q1": q1, "common": theta == Fraction(1, 2) or overlap}


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


def _minimum(q0: Fraction, q1: Fraction) -> tuple[dict[str, object] | None, dict[str, object] | None]:
    high = 1
    candidate = _test(high, q0, q1)
    while high < CAP and candidate["fn"] > ALPHA:
        high = min(CAP, high * 2)
        candidate = _test(high, q0, q1)
    if candidate["fn"] > ALPHA:
        return None, candidate
    low = 0
    while low < high:
        middle = (low + high) // 2
        probe = _test(middle, q0, q1)
        if probe["fn"] <= ALPHA:
            high = middle
        else:
            low = middle + 1
    current = _test(low, q0, q1)
    previous = _test(low - 1, q0, q1) if low else None
    return current, previous


def _expected_core(arm: str, k1: int, theta: Fraction, c: int) -> dict[str, object]:
    law = _law(arm, k1, theta, c)
    core: dict[str, object] = {
        "model": arm,
        "k1": k1,
        "theta": _text(theta),
        "coverage_count": c,
        "coverage": _text(Fraction(c, N)),
        "q0_worst": _text(law["q0"]),
        "q1_worst": _text(law["q1"]),
        "effective_delta": _text(Fraction(0) if law["common"] else law["q1"] - law["q0"]),
    }
    if law["common"]:
        core.update({"status": "common_law_impossible", "m_star": None})
        return core
    current, previous = _minimum(law["q0"], law["q1"])
    if current is None:
        core.update({"status": "infeasible_within_cap", "m_star": None})
        return core
    core.update(
        {
            "status": "feasible_exact",
            "m_star": current["m"],
            "cutoff": current["cutoff"],
            "gamma": _text(current["gamma"]),
            "fp": _text(current["fp"]),
            "fn": _text(current["fn"]),
            "predecessor_fn": _text(previous["fn"]) if previous is not None else None,
        }
    )
    return core


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


def verify_payload(payload: dict[str, object]) -> dict[str, object]:
    failures: list[str] = []
    expected_constants = {
        "domain_size": N,
        "compliant_boundary": K0,
        "forbidden_boundaries": list(K1S),
        "theta_grid": [_text(value) for value in THETAS],
        "coverage_counts": list(COUNTS),
        "models": list(ARMS),
        "error_limit": _text(ALPHA),
        "m_cap": CAP,
    }
    if payload.get("protocol_constants") != expected_constants:
        failures.append("protocol_constants")

    records = payload.get("records")
    if not isinstance(records, list):
        return {"pass": False, "failures": failures + ["records_not_list"]}
    expected_count = len(ARMS) * len(K1S) * len(THETAS) * len(COUNTS)
    if len(records) != expected_count:
        failures.append(f"record_count:{len(records)}!={expected_count}")
    seen: set[tuple[str, int, Fraction, int]] = set()
    by_key: dict[tuple[str, int, Fraction, int], dict[str, object]] = {}
    for row in records:
        try:
            key = (str(row["model"]), int(row["k1"]), _fraction(row["theta"]), int(row["coverage_count"]))
        except (KeyError, TypeError, ValueError) as exc:
            failures.append(f"malformed_record:{exc}")
            continue
        if key in seen:
            failures.append(f"duplicate:{key}")
            continue
        seen.add(key)
        by_key[key] = row

    for arm in ARMS:
        for k1 in K1S:
            for theta in THETAS:
                for c in COUNTS:
                    key = (arm, k1, theta, c)
                    row = by_key.get(key)
                    if row is None:
                        failures.append(f"missing:{key}")
                        continue
                    expected = _expected_core(arm, k1, theta, c)
                    for field in (
                        "model",
                        "k1",
                        "theta",
                        "coverage_count",
                        "coverage",
                        "q0_worst",
                        "q1_worst",
                        "effective_delta",
                        "status",
                        "m_star",
                    ):
                        if row.get(field) != expected[field]:
                            failures.append(f"{key}:{field}")
                    if expected["status"] == "feasible_exact":
                        test = row.get("test") or {}
                        previous = row.get("predecessor") or {}
                        for field in ("cutoff", "gamma", "fp", "fn"):
                            if test.get(field) != expected[field]:
                                failures.append(f"{key}:test.{field}")
                        if previous.get("fn") != expected["predecessor_fn"]:
                            failures.append(f"{key}:predecessor.fn")
                    elif expected["status"] == "common_law_impossible":
                        if row.get("common_law_witness") is None or row.get("sum_error_lower_bound") != "1/1":
                            failures.append(f"{key}:common_witness")

    if not _small_bruteforce():
        failures.append("independent_small_bruteforce")

    full_expected = {
        (14, Fraction(3, 4)): 73,
        (14, Fraction(4, 5)): 50,
        (14, Fraction(1)): 15,
        (16, Fraction(3, 4)): 40,
        (16, Fraction(4, 5)): 26,
        (16, Fraction(1)): 5,
    }
    for arm in ARMS:
        for (k1, theta), m_star in full_expected.items():
            if by_key.get((arm, k1, theta, 16), {}).get("m_star") != m_star:
                failures.append(f"full_reproduction:{arm},{k1},{theta}")

    probes = payload.get("metric_robustness_probes", {})
    if set(probes) != {"invariance", "sensitivity", "monotonicity", "anti_gaming", "clean_control"}:
        failures.append("metric_probe_names")
    elif not all(bool(probes[name].get("pass")) for name in probes):
        failures.append("metric_probe_failure")

    reliability = payload.get("measurement_reliability", {})
    claim = payload.get("claim_support", {})
    task = payload.get("task_result", {})
    operational = payload.get("operational_decision", {})
    expected_pass = not failures
    if reliability.get("all_pass") is not True or reliability.get("status") != "reliable_exact_finite_measurement":
        failures.append("measurement_reliability")
    if claim.get("all_pass") is not True or claim.get("status") != "registered_finite_claim_supported":
        failures.append("claim_support")
    if task.get("status") != "selective_suppression_weakens_registered_attestability":
        failures.append("task_result")
    if operational.get("status") != "no_deployment_decision_authorized":
        failures.append("operational_decision")
    if not payload.get("claim_boundary"):
        failures.append("claim_boundary")

    return {
        "pass": not failures and expected_pass,
        "failures": failures,
        "records_checked": len(seen),
        "independent_bruteforce": True,
        "implementation_imported": False,
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    result_path = args.artifact_dir / "result.json"
    receipt_path = args.artifact_dir / "receipt.json"
    verification_path = args.artifact_dir / "verification.json"
    if verification_path.exists() and not args.force:
        raise RuntimeError("verification exists; use --force for an explicit replay")
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    verification = verify_payload(payload)
    if receipt.get("result_sha256") != sha256_file(result_path):
        verification["pass"] = False
        verification["failures"].append("result_sha256")
    write_json(verification_path, verification)
    print(json.dumps(verification, indent=2))
    if not verification["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
