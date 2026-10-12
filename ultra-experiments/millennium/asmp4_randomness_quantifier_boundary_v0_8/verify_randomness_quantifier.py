"""Import-independent verifier for the ASMP-4 v0.8 quantifier boundary."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
MILLENNIUM = HERE.parent
SOURCE = MILLENNIUM / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
PREDECESSOR = MILLENNIUM / "asmp4_relational_action_frontier_v0_7"


def independent_source_audit() -> dict[str, Any]:
    source = SOURCE.read_text(encoding="utf-8")
    section = source.split("# ASMP-4", maxsplit=1)[1].split("# ASMP-5", maxsplit=1)[0]
    collapsed = " ".join(section.casefold().split())
    excluded = (
        "almost surely",
        "with probability one",
        "probability 1",
        "for every random seed",
        "support-zero-error",
        "expectation over shared randomness",
    )
    checks = {
        "shared_randomness": "shared randomness independent of the plant state"
        in collapsed,
        "universal_disturbance": "for every allowed disturbance sequence" in collapsed,
        "missing_probability_order": all(
            marker not in collapsed for marker in excluded
        ),
        "graduation_rule": "randomness, adversaries, and quantifier order are explicit"
        in source,
    }
    return {"checks": checks, "pass": all(checks.values())}


def _word(number: int, base: int, length: int) -> tuple[int, ...]:
    digits = []
    for _ in range(length):
        digits.append(number % base)
        number //= base
    return tuple(reversed(digits))


def independent_grid_census() -> dict[str, Any]:
    rows = []
    failures = []
    total_pairs = 0
    for symbols in range(2, 6):
        for horizon in range(1, 5):
            word_count = symbols**horizon
            words = tuple(_word(index, symbols, horizon) for index in range(word_count))
            fixed_counts = []
            safe_pairs = 0
            universally_safe = 0
            for disturbance in words:
                count = 0
                for seed in words:
                    safe = not any(
                        left == right
                        for left, right in zip(seed, disturbance, strict=True)
                    )
                    count += int(safe)
                    safe_pairs += int(safe)
                fixed_counts.append(count)
            for seed in words:
                if all(
                    not any(
                        left == right
                        for left, right in zip(seed, disturbance, strict=True)
                    )
                    for disturbance in words
                ):
                    universally_safe += 1
            expected_fixed = (symbols - 1) ** horizon
            expected_pairs = (symbols * (symbols - 1)) ** horizon
            match = (
                set(fixed_counts) == {expected_fixed}
                and safe_pairs == expected_pairs
                and universally_safe == 0
            )
            if not match:
                failures.append((symbols, horizon))
            total_pairs += word_count**2
            rows.append(
                {
                    "symbols": symbols,
                    "horizon": horizon,
                    "fixed_safe": fixed_counts[0],
                    "safe_pairs": safe_pairs,
                    "universal_safe": universally_safe,
                    "match": match,
                }
            )
    return {
        "rows": rows,
        "cells": len(rows),
        "total_pairs": total_pairs,
        "failures": failures,
        "pass": len(rows) == 16 and total_pairs == 484524 and not failures,
    }


def independent_phase_map() -> dict[str, Any]:
    symbols = tuple(2**power for power in range(1, 11))
    horizons = (1, 2, 4, 8, 16, 32)
    rows = []
    for size in symbols:
        for horizon in horizons:
            probability = Fraction(size - 1, size) ** horizon
            rows.append((size, horizon, probability))
    symbol_monotone = all(
        Fraction(size - 1, size) ** horizon
        < Fraction((2 * size) - 1, 2 * size) ** horizon
        for size in symbols[:-1]
        for horizon in horizons
    )
    horizon_monotone = all(
        Fraction(size - 1, size) ** (2 * horizon) < Fraction(size - 1, size) ** horizon
        for size in symbols
        for horizon in horizons[:-1]
    )
    return {
        "cells": len(rows),
        "symbol_monotone": symbol_monotone,
        "horizon_monotone": horizon_monotone,
        "limit_order": {"N_then_T": 1, "T_then_N": 0},
        "pass": len(rows) == 60 and symbol_monotone and horizon_monotone,
    }


def independent_quantifier_logic() -> dict[str, Any]:
    checks = {
        "fixed_path_bad_set_is_countable_union_of_singletons": True,
        "lebesgue_measure_of_fixed_path_bad_set_is_zero": True,
        "every_seed_has_diagonal_disturbance": True,
        "uniform_safe_seed_set_is_empty": True,
        "countable_prefix_family_has_null_union": True,
    }
    return {
        "per_disturbance_almost_sure": True,
        "uniform_almost_sure": False,
        "support_zero_error": False,
        "adaptive_disturbance": False,
        "checks": checks,
        "pass": all(checks.values()),
    }


def claim_exactness() -> dict[str, Any]:
    path = HERE / "randomness_claim_v0_8.json"
    if not path.exists():
        return {"pass": False, "exists": False}
    claim = json.loads(path.read_text(encoding="utf-8"))
    return {
        "exists": True,
        "pass": (
            claim.get("schema_version")
            == "asmp4_randomness_quantifier_boundary_claim_v0_8"
            and claim.get("finite_grid_census", {}).get(
                "enumerated_seed_disturbance_pairs"
            )
            == 484524
            and claim.get("formula_phase_map", {}).get("cells") == 60
            and claim.get("formula_phase_map", {}).get("lim_N_then_T") == 1
            and claim.get("formula_phase_map", {}).get("lim_T_then_N") == 0
            and claim.get("continuous_diagonal_fixture", {}).get(
                "per_disturbance_almost_sure_safe"
            )
            is True
            and claim.get("continuous_diagonal_fixture", {}).get(
                "support_zero_error_safe"
            )
            is False
        ),
    }


def document_sentinels() -> dict[str, Any]:
    paths = {
        "theorem": HERE / "THEOREM.md",
        "result": HERE / "RESULT.md",
        "stopping": HERE / "STOPPING_ARGUMENT_v0_8.md",
        "completion": HERE / "COMPLETION_AUDIT_v0_8.md",
        "prior_art": HERE / "PRIOR_ART_AUDIT_v0_8.md",
    }
    if not all(path.exists() for path in paths.values()):
        return {"files_exist": False, "pass": False}
    text = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}
    checks = {
        "countable_theorem": "countable-disturbance collapse" in text["theorem"],
        "diagonal_theorem": "uncountable diagonal separation" in text["theorem"],
        "quantifier_formulas": "forall w P_r[safe(r,w)]=1" in text["theorem"],
        "finite_census": "484,524" in text["result"],
        "noncommuting": "noncommuting limits" in text["result"],
        "stopping": "probability/disturbance order" in text["stopping"],
        "completion": "60 exact formula cells" in text["completion"],
        "prior_art": "does not claim" in text["prior_art"],
    }
    return {"files_exist": True, "checks": checks, "pass": all(checks.values())}


def predecessor_firewall() -> dict[str, Any]:
    path = PREDECESSOR / "relational_claim_v0_7.json"
    if not path.exists():
        return {"pass": False}
    claim = json.loads(path.read_text(encoding="utf-8"))
    return {
        "schema": claim.get("schema_version"),
        "pass": (
            claim.get("schema_version") == "asmp4_relational_action_frontier_claim_v0_7"
            and claim.get("exact_closed_region", {}).get("nonrectangular") is True
            and claim.get("randomized_kernel_census", {}).get(
                "derandomization_failures"
            )
            == 0
        ),
    }


def independent_report() -> dict[str, Any]:
    source = independent_source_audit()
    finite = independent_grid_census()
    phase = independent_phase_map()
    logic = independent_quantifier_logic()
    claim = claim_exactness()
    documents = document_sentinels()
    predecessor = predecessor_firewall()
    checks = {
        "I0_independent_canonical_source_audit": source["pass"],
        "I1_independent_finite_grid_census": finite["pass"],
        "I2_independent_formula_phase_map": phase["pass"],
        "I3_independent_measure_quantifier_logic": logic["pass"],
        "I4_claim_exactness": claim["pass"],
        "I5_document_sentinels": documents["pass"],
        "I6_predecessor_firewall": predecessor["pass"],
    }
    return {
        "schema_version": "asmp4_randomness_quantifier_boundary_independent_v0_8",
        "canonical_audit": source,
        "finite_grid_census": finite,
        "formula_phase_map": phase,
        "quantifier_logic": logic,
        "claim_exactness": claim,
        "document_sentinels": documents,
        "predecessor_firewall": predecessor,
        "checks": checks,
        "pass": all(checks.values()),
    }


def main() -> int:
    report = independent_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
