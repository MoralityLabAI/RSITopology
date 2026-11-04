"""Independent checker for the exact binary safety-deficiency artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_fraction(text: str) -> Fraction:
    numerator, denominator = text.split("/")
    return Fraction(int(numerator), int(denominator))


def independent_success(sample_size: int, signal: Fraction) -> Fraction:
    if sample_size == 0:
        return Fraction(1, 2)
    p = Fraction(1, 2) + signal
    q = 1 - p
    total = Fraction(0)
    for count in range(sample_size + 1):
        mass = (
            Fraction(math.comb(sample_size, count))
            * p**count
            * q ** (sample_size - count)
        )
        if 2 * count > sample_size:
            total += mass
        elif 2 * count == sample_size:
            total += mass / 2
    return total


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = json.loads(args.result.read_text(encoding="utf-8"))
    theorem = HERE / "DECISION_DEFICIENCY_REDUCTION_v0_3.md"
    table_matches = True
    for signal_text in result["signals"]:
        signal = parse_fraction(signal_text)
        for sample_size in result["sample_sizes"]:
            success = independent_success(sample_size, signal)
            row = result["exact_table"][signal_text][str(sample_size)]
            table_matches &= parse_fraction(row["success"]) == success
            table_matches &= parse_fraction(row["deficiency"]) == 1 - success

    checks = {
        "identity": result["schema_version"] == "asmp2_safety_deficiency_v0_3",
        "theorem_hash": result["theorem_sha256"] == sha256(theorem),
        "exact_table": table_matches,
        "zero_signal_infinite_complexity": (
            result["sample_complexities"]["0/1"] == "infinity"
        ),
        "active_choice": result["active_choice_index"] == 1,
        "reported_gates": result["all_gates_passed"] is True
        and all(result["gates"].values()),
    }
    payload = {
        "schema_version": "asmp2_safety_deficiency_verification_v0_3",
        "result_sha256": sha256(args.result),
        "checks": checks,
        "passed_count": sum(checks.values()),
        "check_count": len(checks),
        "passed": all(checks.values()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"verification_passed={str(payload['passed']).lower()}")
    print(f"checks={payload['passed_count']}/{payload['check_count']}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
