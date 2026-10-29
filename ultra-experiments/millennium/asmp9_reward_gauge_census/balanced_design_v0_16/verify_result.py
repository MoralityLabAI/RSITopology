from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> Fraction:
    numerator, denominator = value.split("/")
    return Fraction(int(numerator), int(denominator))


def prod(values: Iterable[Fraction]) -> Fraction:
    result = Fraction(1)
    for value in values:
        result *= value
    return result


def xyz(count: int, epsilon: Fraction) -> tuple[Fraction, Fraction, Fraction]:
    r = 1 - epsilon
    s = epsilon
    return 1 - r**count, 1 - s**count, 1 - r**count - s**count


def availability(
    counts: tuple[int, ...],
    epsilon: Fraction,
    labels: tuple[int, ...],
) -> Fraction:
    first = []
    second = []
    interior = []
    for count, label in zip(counts, labels, strict=True):
        x, y, z = xyz(count, epsilon)
        first.append(x if label == 0 else y)
        second.append(y if label == 0 else x)
        interior.append(z)
    return prod(first) + prod(second) - prod(interior)


def worst(
    counts: tuple[int, ...], epsilon: Fraction
) -> Fraction:
    return min(
        availability(counts, epsilon, labels)
        for labels in itertools.product((0, 1), repeat=len(counts))
    )


def allocations(
    total: int, length: int, minimum: int = 1
) -> Iterable[tuple[int, ...]]:
    if length == 1:
        if total >= minimum:
            yield (total,)
        return
    for first in range(minimum, total // length + 1):
        for rest in allocations(total - first, length - 1, first):
            yield (first, *rest)


def balanced(total: int, length: int) -> tuple[int, ...]:
    quotient, remainder = divmod(total, length)
    return (
        (quotient,) * (length - remainder)
        + (quotient + 1,) * remainder
    )


def compact_value(
    total: int, length: int, epsilon: Fraction
) -> Fraction:
    counts = balanced(total, length)
    lower = counts[0]
    upper = counts[-1]
    upper_count = total - lower * length
    lower_count = length - upper_count
    xl, yl, zl = xyz(lower, epsilon)
    xu, yu, zu = xyz(upper, epsilon)
    values = []
    for j in range(lower_count + 1):
        for ell in range(upper_count + 1):
            values.append(
                xl**j
                * yl ** (lower_count - j)
                * xu**ell
                * yu ** (upper_count - ell)
                + yl**j
                * xl ** (lower_count - j)
                * yu**ell
                * xu ** (upper_count - ell)
                - zl**lower_count * zu**upper_count
            )
    return min(values)


def local_values(
    a: int,
    b: int,
    epsilon: Fraction,
    U: Fraction,
    V: Fraction,
    W: Fraction,
) -> tuple[Fraction, Fraction, Fraction]:
    xa, ya, za = xyz(a, epsilon)
    xb, yb, zb = xyz(b, epsilon)
    M = max(U, V)
    m = min(U, V)
    same = M * xa * xb + m * ya * yb - W * za * zb
    opposite = M * xa * yb + m * ya * xb - W * za * zb
    direct = min(
        U * (xa if left == 0 else ya) * (xb if right == 0 else yb)
        + V * (ya if left == 0 else xa) * (yb if right == 0 else xb)
        - W * za * zb
        for left, right in itertools.product((0, 1), repeat=2)
    )
    return same, opposite, direct


def verify(
    registration_path: Path,
    result_path: Path,
    report_path: Path,
    receipt_path: Path,
) -> dict[str, Any]:
    registration = json.loads(
        registration_path.read_text(encoding="utf-8")
    )
    protocol = json.loads(
        (REPO / registration["protocol_path"]).read_text(encoding="utf-8")
    )
    result = json.loads(result_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}

    for relative, expected in registration["sealed_files"].items():
        checks[f"sealed:{relative}"] = sha256(REPO / relative) == expected
    checks["receipt_result_hash"] = (
        receipt["output_hashes"][result_path.name] == sha256(result_path)
    )
    checks["receipt_report_hash"] = (
        receipt["output_hashes"][report_path.name] == sha256(report_path)
    )
    checks["registration_hash"] = (
        result["registration_sha256"]
        == receipt["registration_sha256"]
        == sha256(registration_path)
    )
    checks["protocol_id"] = (
        result["protocol_id"]
        == receipt["protocol_id"]
        == protocol["protocol_id"]
    )
    checks["reported_pass"] = (
        result["verdict"] == "registered_exact_result_passed"
        and receipt["verdict"] == result["verdict"]
        and all(result["gates"].values())
    )

    pair_ok = True
    for row in result["pair_records"]:
        a = row["a"]
        b = row["b"]
        epsilon = parse(row["epsilon"]["fraction"])
        U = parse(row["U"]["fraction"])
        V = parse(row["V"]["fraction"])
        W = parse(row["W"]["fraction"])
        same_before, opposite_before, direct_before = local_values(
            a, b, epsilon, U, V, W
        )
        same_after, opposite_after, direct_after = local_values(
            a + 1, b - 1, epsilon, U, V, W
        )
        pair_ok = pair_ok and (
            min(same_before, opposite_before) == direct_before
            and min(same_after, opposite_after) == direct_after
            and same_after > same_before
            and opposite_after > opposite_before
            and direct_after > direct_before
        )
    checks["independent_pair_replay"] = pair_ok

    global_ok = True
    for row in result["global_records"]:
        k = row["cycle_length"]
        total = row["total_trials"]
        epsilon = parse(row["epsilon"]["fraction"])
        values = [
            (worst(candidate, epsilon), candidate)
            for candidate in allocations(total, k)
        ]
        optimum = max(value for value, _ in values)
        optimizers = [
            candidate for value, candidate in values if value == optimum
        ]
        global_ok = global_ok and (
            optimizers == [balanced(total, k)]
            and optimum == parse(row["optimum"]["fraction"])
        )
    checks["independent_global_replay"] = global_ok

    compact_ok = all(
        compact_value(
            row["total_trials"],
            row["cycle_length"],
            parse(row["epsilon"]["fraction"]),
        )
        == worst(
            balanced(row["total_trials"], row["cycle_length"]),
            parse(row["epsilon"]["fraction"]),
        )
        == parse(row["closed"]["fraction"])
        == parse(row["exhaustive"]["fraction"])
        for row in result["compact_records"]
    )
    checks["independent_compact_replay"] = compact_ok

    threshold_ok = True
    for row in result["threshold_records"]:
        k = row["cycle_length"]
        epsilon = parse(row["epsilon"]["fraction"])
        target = parse(row["target"]["fraction"])
        selected = row["minimum_total_trials"]
        current = compact_value(selected, k, epsilon)
        predecessor = (
            Fraction(0)
            if selected == k
            else compact_value(selected - 1, k, epsilon)
        )
        threshold_ok = threshold_ok and (
            predecessor < target <= current
            and predecessor == parse(row["predecessor"]["fraction"])
            and current == parse(row["current"]["fraction"])
        )
    checks["independent_threshold_replay"] = threshold_ok

    zero_ok = all(
        worst(tuple(row["allocation"]), Fraction(0)) == 0
        for row in result["boundary_records"]["epsilon_zero"]
    )
    k_two_ok = True
    for row in result["boundary_records"]["k_two"]:
        epsilon = parse(row["epsilon"]["fraction"])
        values = [
            worst(candidate, epsilon)
            for candidate in allocations(row["total_trials"], 2)
        ]
        k_two_ok = k_two_ok and len(set(values)) == 1
    checks["independent_boundary_replay"] = zero_ok and k_two_ok

    checks["gate_universe"] = (
        list(result["gates"]) == protocol["gate_ids"]
    )
    checks["resource_caps"] = (
        result["resources"]["gpu_used"] is False
        and result["resources"]["elapsed_seconds"]
        <= protocol["resource_caps"]["wall_seconds"]
        and result["resources"]["peak_resident_bytes"]
        <= protocol["resource_caps"]["peak_resident_bytes"]
    )
    checks["claim_boundary_exact"] = (
        result["claim_boundary"] == protocol["claim_boundary"]
    )
    return {
        "status": "pass" if all(checks.values()) else "fail",
        "check_count": len(checks),
        "checks": checks,
        "failed_checks": [
            name for name, passed in checks.items() if not passed
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    verification = verify(
        args.registration.resolve(),
        args.result.resolve(),
        args.report.resolve(),
        args.receipt.resolve(),
    )
    rendered = json.dumps(verification, indent=2, sort_keys=True) + "\n"
    if args.output:
        if args.output.exists():
            raise FileExistsError(
                f"refusing to overwrite output: {args.output}"
            )
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    raise SystemExit(0 if verification["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
