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


def product(values: Iterable[Fraction]) -> Fraction:
    result = Fraction(1)
    for value in values:
        result *= value
    return result


def independent_availability(
    trials: tuple[int, ...], probabilities: tuple[Fraction, ...]
) -> Fraction:
    probability_no_zero = product(
        1 - (1 - probability) ** count
        for count, probability in zip(
            trials, probabilities, strict=True
        )
    )
    probability_no_full = product(
        1 - probability**count
        for count, probability in zip(
            trials, probabilities, strict=True
        )
    )
    probability_all_interior = product(
        1 - probability**count - (1 - probability) ** count
        for count, probability in zip(
            trials, probabilities, strict=True
        )
    )
    return (
        probability_no_zero
        + probability_no_full
        - probability_all_interior
    )


def independent_sharp(
    k: int, n: int, epsilon: Fraction
) -> Fraction:
    a = (1 - epsilon) ** n
    b = epsilon**n
    x = 1 - a
    y = 1 - b
    z = 1 - a - b
    m = k // 2
    h = k - m
    return x**m * y**h + y**m * x**h - z**k


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


def independent_worst(
    trials: tuple[int, ...], epsilon: Fraction
) -> Fraction:
    values = []
    for bits in itertools.product((0, 1), repeat=len(trials)):
        probabilities = tuple(
            epsilon if bit == 0 else 1 - epsilon for bit in bits
        )
        values.append(independent_availability(trials, probabilities))
    return min(values)


def independent_allocation_optimum(
    total: int, k: int, epsilon: Fraction
) -> tuple[Fraction, Fraction]:
    values = [
        independent_worst(candidate, epsilon)
        for candidate in allocations(total, k)
    ]
    quotient, remainder = divmod(total, k)
    balanced = (
        (quotient,) * (k - remainder)
        + (quotient + 1,) * remainder
    )
    return max(values), independent_worst(balanced, epsilon)


def verify(
    *,
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
    checks["gate_universe"] = (
        list(result["gates"]) == protocol["gate_ids"]
    )
    checks["reported_pass"] = (
        result["verdict"] == "registered_exact_result_passed"
        and receipt["verdict"] == result["verdict"]
        and all(result["gates"].values())
    )

    theorem_ok = True
    for row in result["theorem_records"]:
        k = row["cycle_length"]
        n = row["trials_per_edge"]
        epsilon = parse(row["epsilon"]["fraction"])
        reported = parse(row["sharp_minimum"]["fraction"])
        closed = independent_sharp(k, n, epsilon)
        vertex_values = [
            independent_availability(
                (n,) * k,
                (epsilon,) * low
                + (1 - epsilon,) * (k - low),
            )
            for low in range(k + 1)
        ]
        witnesses = [
            index
            for index, value in enumerate(vertex_values)
            if value == min(vertex_values)
        ]
        theorem_ok = theorem_ok and (
            reported == closed == min(vertex_values)
            and witnesses == sorted({k // 2, k - k // 2})
        )
    checks["independent_theorem_replay"] = theorem_ok

    threshold_ok = True
    for row in result["threshold_records"]:
        k = row["cycle_length"]
        n = row["minimum_trials_per_edge"]
        epsilon = parse(row["epsilon"]["fraction"])
        target = parse(row["target"]["fraction"])
        current = independent_sharp(k, n, epsilon)
        predecessor = (
            Fraction(0)
            if n == 1
            else independent_sharp(k, n - 1, epsilon)
        )
        threshold_ok = threshold_ok and (
            predecessor < target <= current
            and current
            == parse(row["threshold_availability"]["fraction"])
            and predecessor
            == parse(row["predecessor_availability"]["fraction"])
        )
    checks["independent_threshold_replay"] = threshold_ok

    zero_ok = all(
        independent_sharp(
            row["cycle_length"],
            row["trials_per_edge"],
            Fraction(0),
        )
        == 0
        == parse(row["minimum_availability"]["fraction"])
        for row in result["zero_interior_records"]
    )
    checks["independent_zero_interior_replay"] = zero_ok

    allocation_ok = True
    for row in result["allocation_records"]:
        epsilon = parse(row["epsilon"]["fraction"])
        optimum, balanced = independent_allocation_optimum(
            row["total_trials"], row["cycle_length"], epsilon
        )
        allocation_ok = allocation_ok and (
            optimum == parse(row["optimum"]["fraction"])
            and balanced
            == parse(row["balanced_worst_availability"]["fraction"])
            and balanced == optimum
        )
    checks["independent_allocation_replay"] = allocation_ok

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
        "verified_artifacts": {
            "registration": registration_path.name,
            "result": result_path.name,
            "report": report_path.name,
            "receipt": receipt_path.name,
        },
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
        registration_path=args.registration.resolve(),
        result_path=args.result.resolve(),
        report_path=args.report.resolve(),
        receipt_path=args.receipt.resolve(),
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
