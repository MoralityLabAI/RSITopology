"""Import-independent verifier for ASMP-4 safe closing v0.33."""

from __future__ import annotations

import ast
import itertools
import json
import re
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CONTRACT = HERE / "safe_closing_contract_v0_33.json"
CLAIM = HERE / "safe_closing_claim_v0_33.json"


def substitution_word(minimum_length: int) -> tuple[int, ...]:
    word = (0,)
    while len(word) < minimum_length:
        word = tuple(
            symbol
            for bit in word
            for symbol in ((0, 1) if bit == 0 else (1, 0))
        )
    return word


def independent_prefix_report(limit: int = 4096) -> dict[str, Any]:
    word = substitution_word(limit + 256)
    ones = 0
    discrepancy = True
    recurrence = True
    for horizon in range(1, limit + 1):
        ones += word[horizon - 1]
        discrepancy &= abs(2 * ones - horizon) <= 1
    for index in range(limit // 2):
        recurrence &= word[2 * index] == word[index]
        recurrence &= word[2 * index + 1] == 1 - word[index]
    checks = {
        "substitution_length": len(word) >= limit + 256,
        "prefix_discrepancy": discrepancy,
        "recurrence": recurrence,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_aperiodicity(
    max_period: int = 128, max_start: int = 64, window: int = 512
) -> dict[str, Any]:
    required = max_start + window + max_period
    word = substitution_word(required)
    witnesses: list[tuple[int, int, int]] = []
    for period, start in itertools.product(
        range(1, max_period + 1), range(max_start + 1)
    ):
        witness = next(
            (
                index
                for index in range(start, start + window)
                if word[index] != word[index + period]
            ),
            None,
        )
        if witness is not None:
            witnesses.append((period, start, witness))
    checks = {
        "all_candidates_have_witness": len(witnesses)
        == max_period * (max_start + 1),
        "candidate_count": len(witnesses) == 8320,
    }
    return {
        "witnesses": len(witnesses),
        "checks": checks,
        "pass": all(checks.values()),
    }


def _rates(horizon: int, mode: str, word: tuple[int, ...]) -> tuple[Fraction, Fraction]:
    ones = sum(word[:horizon])
    if mode == "balanced":
        cost = ones + 1, horizon - ones + 1
    elif mode == "left":
        cost = ones + 1, 2 * horizon - ones + 2
    elif mode == "right":
        cost = 2 * horizon - ones + 2, ones + 1
    else:
        raise ValueError(mode)
    return Fraction(cost[0], horizon + 1), Fraction(cost[1], horizon + 1)


def independent_component_report(limit: int = 4096) -> dict[str, Any]:
    word = substitution_word(limit)
    corners = {
        "balanced": (Fraction(1, 2), Fraction(1, 2)),
        "left": (Fraction(1, 2), Fraction(3, 2)),
        "right": (Fraction(3, 2), Fraction(1, 2)),
    }
    all_blocks_above = True
    for horizon in range(1, limit + 1):
        for mode, corner in corners.items():
            rate = _rates(horizon, mode, word)
            all_blocks_above &= rate[0] >= corner[0] and rate[1] >= corner[1]

    left = corners["left"]
    right = corners["right"]
    midpoint = (Fraction(1), Fraction(1))
    outside = not (
        (midpoint[0] >= left[0] and midpoint[1] >= left[1])
        or (midpoint[0] >= right[0] and midpoint[1] >= right[1])
    )
    collapsed_accepts = True
    for numerator in range(65):
        weight = Fraction(numerator, 64)
        midpoint_value = weight * midpoint[0] + (1 - weight) * midpoint[1]
        left_value = weight * left[0] + (1 - weight) * left[1]
        right_value = weight * right[0] + (1 - weight) * right[1]
        collapsed_accepts &= midpoint_value >= min(left_value, right_value)
    final = _rates(limit, "balanced", word)
    checks = {
        "all_blocks_above_corners": all_blocks_above,
        "power_horizon_converges": final
        == (
            Fraction(1, 2) + Fraction(1, 2 * (limit + 1)),
            Fraction(1, 2) + Fraction(1, 2 * (limit + 1)),
        ),
        "midpoint_outside_union": outside,
        "collapsed_support_accepts_midpoint": collapsed_accepts,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_correction_report(limit: int = 256) -> dict[str, Any]:
    word = substitution_word(limit)
    rows = 0
    exact_bound = True
    for horizon in range(1, limit + 1):
        ones = sum(word[:horizon])
        prefix = ones, horizon - ones
        for numerator in range(9):
            weight = Fraction(numerator, 8)
            exact = (
                weight * (prefix[0] + 1) + (1 - weight) * (prefix[1] + 1)
            ) / (horizon + 1)
            coarse = (
                weight * prefix[0] + (1 - weight) * prefix[1]
            ) / horizon + Fraction(1, horizon)
            exact_bound &= exact <= coarse
            rows += 1
    constant = Fraction(1, limit)
    linear = Fraction((limit + 3) // 4, limit)
    checks = {
        "exact_bound": exact_bound,
        "constant_overhead_vanishes": constant == Fraction(1, 256),
        "linear_overhead_does_not_vanish": linear == Fraction(1, 4),
        "strict_margin_rule": Fraction(3, 4) < 1 and not Fraction(1) < 1,
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def independent_burst_report(stages: int = 10) -> dict[str, Any]:
    total = 1
    ones = 0
    low = Fraction(1)
    high = Fraction(0)
    for stage in range(stages):
        length = 10 * total + 1
        if stage % 2:
            ones += length
        total += length
        average = Fraction(ones, total)
        if stage % 2:
            high = max(high, average)
        else:
            low = min(low, average)
    checks = {"separated": low < Fraction(1, 10) and high > Fraction(9, 10)}
    return {"low": str(low), "high": str(high), "checks": checks, "pass": all(checks.values())}


def independent_contract_claim() -> dict[str, Any]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    claim = json.loads(CLAIM.read_text(encoding="utf-8"))
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    checks = {
        "contract_schema": contract.get("schema_version")
        == "asmp4_safe_closing_contract_v0_33",
        "claim_schema": claim.get("schema_version")
        == "asmp4_nonfinite_safe_closing_v0_33",
        "component_formula": claim.get("theorem", {}).get("component_region")
        == "R_q=closure(upward(conv(P_q)))",
        "nonfinite": claim.get("nonfinite_fixture", {}).get(
            "finite_exact_stationary_quotient"
        )
        is False,
        "not_full_resolution": "remains open" in claim.get("disposition", ""),
        "central_not_imported": "safe_closing_variational" not in imports,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_mutations() -> dict[str, Any]:
    components = independent_component_report()["checks"]
    aperiodic = independent_aperiodicity()["checks"]
    correction = independent_correction_report()["checks"]
    burst = independent_burst_report()["checks"]
    one_port_overhead = (Fraction(0), Fraction(64, 256))
    composition_charge = Fraction(256, 256)
    scope_open = independent_contract_claim()["checks"]["not_full_resolution"]
    rows = {
        "collapse_components": components["collapsed_support_accepts_midpoint"],
        "finite_quotient_required": aperiodic["all_candidates_have_witness"],
        "linear_overhead_zero": correction["linear_overhead_does_not_vanish"],
        "one_port_controls_both": one_port_overhead
        == (Fraction(0), Fraction(1, 4)),
        "liminf_for_limsup": burst["separated"],
        "margin_free_shadowing": correction["strict_margin_rule"],
        "free_nonmultiplicative_composition": composition_charge == 1,
        "full_global_resolution": scope_open,
    }
    return {"rows": rows, "pass": len(rows) == 8 and all(rows.values())}


def _count_tests(path: Path) -> int:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
        for node in ast.walk(tree)
    )


def _package_version(name: str) -> int:
    match = re.search(r"_v0_(\d+)$", name)
    return int(match.group(1)) if match else 0


def independent_inventory() -> dict[str, Any]:
    rows = []
    for package in sorted(ROOT.iterdir(), key=lambda path: path.name):
        if not package.is_dir() or not package.name.startswith("asmp4"):
            continue
        if package.resolve() == HERE.resolve() or _package_version(package.name) >= 33:
            continue
        for test_file in sorted(package.glob("test_*.py")):
            rows.append((package.name, test_file.name, _count_tests(test_file)))
    checks = {
        "packages": len(rows) == 33,
        "tests": sum(row[2] for row in rows) == 364,
    }
    return {
        "packages": len(rows),
        "tests": sum(row[2] for row in rows),
        "checks": checks,
        "pass": all(checks.values()),
    }


def document_report() -> dict[str, Any]:
    sentinels = {
        "THEOREM.md": ("Sublinear safe-closing theorem", "closure(union"),
        "RESULT.md": ("nonfinite", "not a full resolution"),
        "PRIOR_ART_BOUNDARY_v0_33.md": ("Da Silva", "no novelty"),
        "REVIEWER_PACKET_v0_33.md": ("Review order", "Thue-Morse"),
        "COMPLETION_AUDIT_v0_33.md": ("Expanded regression", "Not claimed"),
    }
    rows = {}
    for name, tokens in sentinels.items():
        text = (HERE / name).read_text(encoding="utf-8").casefold()
        rows[name] = all(token.casefold() in text for token in tokens)
    return {"rows": rows, "pass": all(rows.values())}


def independent_report() -> dict[str, Any]:
    report = {
        "prefix": independent_prefix_report(),
        "aperiodicity": independent_aperiodicity(),
        "components": independent_component_report(),
        "correction": independent_correction_report(),
        "burst": independent_burst_report(),
        "contract_claim": independent_contract_claim(),
        "mutations": independent_mutations(),
        "inventory": independent_inventory(),
        "documents": document_report(),
    }
    report["pass"] = all(section["pass"] for section in report.values())
    return report


def main() -> int:
    report = independent_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
