"""Import-independent exhaustive replay for ASMP-8 v0.6."""

from __future__ import annotations

import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def build_policies(size: int):
    proxy = [Fraction(i, size - 1) for i in range(size)]
    move = Fraction(1, size)
    rows = []
    for source in range(size):
        for target in range(size):
            if source == target:
                continue
            d = [Fraction()] * size
            d[source], d[target] = -move, move
            rows.append((f"move_{source}_to_{target}", tuple(d), sum((d[i] * proxy[i] for i in range(size)), Fraction())))
    return rows


def verify() -> dict[str, Any]:
    protocol = json.loads((HERE / "protocol_v0_6.json").read_text(encoding="utf-8"))
    result = json.loads((HERE / "artifacts_v0_6" / "result_v0_6.json").read_text(encoding="utf-8"))
    size = int(protocol["alphabet_size"])
    cap = Fraction(int(protocol["error_cap"]))
    policies = build_policies(size)
    total = robust_failures = full_failures = naive_false = 0
    full_mask = (1 << size) - 1
    for raw_errors in itertools.product((-1, 0, 1), repeat=size):
        errors = tuple(Fraction(value) for value in raw_errors)
        for mask in range(1 << size):
            for _name, displacement, proxy_gain in policies:
                observed = proxy_gain + sum(
                    (displacement[i] * errors[i] for i in range(size) if mask & (1 << i)), Fraction()
                )
                lower = observed - sum(
                    (abs(displacement[i]) * cap for i in range(size) if not mask & (1 << i)), Fraction()
                )
                exact = proxy_gain + sum((displacement[i] * errors[i] for i in range(size)), Fraction())
                total += 1
                robust_failures += int(lower > exact)
                full_failures += int(mask == full_mask and lower != exact)
                naive_false += int(observed > 0 and exact <= 0)
    reported = result["summary"]["pointwise"]
    agreements = {
        "pointwise_cells": total == reported["pointwise_cells"],
        "robust_soundness_failures": robust_failures == reported["robust_soundness_failures"],
        "full_census_failures": full_failures == reported["full_census_failures"],
        "naive_false_declarations": naive_false == reported["naive_false_declarations"],
    }
    passed = all(agreements.values()) and robust_failures == 0 and full_failures == 0 and all(result["gates"].values())
    return {
        "schema_version": "asmp8_adaptive_reuse_verification_v0_6",
        "pass": passed,
        "implementation_imported": False,
        "agreements": agreements,
        "replayed_pointwise_cells": total,
        "measurement_reliability": "independent_complete_replay_passed" if passed else "failed",
        "claim_support": result["claim_support"] if passed else "none",
        "operational_decision": result["operational_decision"] if passed else "repair",
    }


def main() -> None:
    verification = verify()
    output = HERE / "artifacts_v0_6" / "verification_v0_6.json"
    output.write_text(canonical_json(verification), encoding="utf-8", newline="\n")
    print(output)
    if not verification["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
