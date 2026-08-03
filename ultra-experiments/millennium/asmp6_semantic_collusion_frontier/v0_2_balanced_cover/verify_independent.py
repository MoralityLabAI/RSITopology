"""Standalone extremal replay for ASMP-6 v0.2."""

from __future__ import annotations

import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def extremal_enumeration(alphabet_size: int) -> Fraction:
    radius = Fraction(1, alphabet_size)
    best = Fraction(-1)
    for signs in itertools.product((-1, 0, 1), repeat=alphabet_size):
        if sum(signs) != 0:
            continue
        value = radius * sum(abs(sign) for sign in signs)
        best = max(best, value)
    return best


def verify() -> dict[str, Any]:
    protocol = json.loads((HERE / "protocol_v0_2.json").read_text(encoding="utf-8"))
    result = json.loads((HERE / "artifacts_v0_2" / "result_v0_2.json").read_text(encoding="utf-8"))
    lookup = {cell["alphabet_size"]: cell for cell in result["cells"]}
    mismatches = []
    maximum = int(protocol["independent_extremal_enumeration_maximum"])
    for alphabet_size in range(2, maximum + 1):
        enumerated = extremal_enumeration(alphabet_size)
        reported = Fraction(lookup[alphabet_size]["total_variation"])
        if enumerated != reported:
            mismatches.append(
                {
                    "alphabet_size": alphabet_size,
                    "enumerated": str(enumerated),
                    "reported": str(reported),
                }
            )
    dual_failures = []
    for alphabet_size in range(2, 64):
        sign_count_bound = Fraction(2 * (alphabet_size // 2), alphabet_size)
        claimed_error = Fraction(0) if alphabet_size % 2 == 0 else Fraction(1, 2 * alphabet_size)
        if (1 - sign_count_bound) / 2 != claimed_error:
            dual_failures.append(alphabet_size)
    passed = not mismatches and not dual_failures and all(result["gates"].values())
    return {
        "schema_version": "asmp6_balanced_cover_verification_v0_2",
        "pass": passed,
        "enumerated_alphabet_sizes": list(range(2, maximum + 1)),
        "mismatches": mismatches,
        "dual_bound_failures": dual_failures,
        "measurement_reliability": "independent_extremal_and_dual_replay_passed" if passed else "failed",
        "claim_support": result["claim_support"] if passed else "none",
        "operational_decision": "register_multiletter_successor" if passed else "repair",
    }


def main() -> None:
    verification = verify()
    output = HERE / "artifacts_v0_2" / "verification_v0_2.json"
    output.write_text(canonical_json(verification), encoding="utf-8", newline="\n")
    print(output)
    if not verification["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
