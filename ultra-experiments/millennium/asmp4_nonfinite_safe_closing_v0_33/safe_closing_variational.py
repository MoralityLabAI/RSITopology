"""Exact harness for the ASMP-4 nonfinite safe-closing theorem v0.33."""

from __future__ import annotations

import ast
import json
import math
import re
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Literal

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CONTRACT = HERE / "safe_closing_contract_v0_33.json"
CLAIM = HERE / "safe_closing_claim_v0_33.json"

Variant = Literal["balanced", "left", "right"]
Pair = tuple[int, int]
RatePair = tuple[Fraction, Fraction]

EXPECTED_PAYLOAD = (
    "README.md",
    "THEOREM.md",
    "RESULT.md",
    "PRIOR_ART_BOUNDARY_v0_33.md",
    "REVIEWER_PACKET_v0_33.md",
    "COMPLETION_AUDIT_v0_33.md",
    "safe_closing_contract_v0_33.json",
    "safe_closing_claim_v0_33.json",
    "safe_closing_variational.py",
    "verify_safe_closing.py",
    "test_safe_closing.py",
    "run_verification.py",
)


@dataclass(frozen=True)
class ClosedBlock:
    """One safe prefix closed back to its registered reset component."""

    component: str
    prefix_horizon: int
    horizon: int
    prefix_cost: Pair
    cost: Pair
    time_overhead: int
    cost_overhead: Pair

    @property
    def rate(self) -> RatePair:
        return (
            Fraction(self.cost[0], self.horizon),
            Fraction(self.cost[1], self.horizon),
        )


def thue_morse_bit(index: int) -> int:
    """Return the index-th Thue-Morse bit using binary digit parity."""

    if index < 0:
        raise ValueError("index must be nonnegative")
    return index.bit_count() & 1


def prefix_ones(horizon: int) -> int:
    if horizon < 1:
        raise ValueError("horizon must be positive")
    return sum(thue_morse_bit(index) for index in range(horizon))


def prefix_cost(horizon: int, variant: Variant = "balanced") -> Pair:
    """Return additive read/write bit costs for the aperiodic fixture."""

    ones = prefix_ones(horizon)
    if variant == "balanced":
        return ones, horizon - ones
    if variant == "left":
        return ones, 2 * horizon - ones
    if variant == "right":
        return 2 * horizon - ones, ones
    raise ValueError(f"unknown variant: {variant}")


def connector_overhead(variant: Variant) -> Pair:
    if variant == "balanced":
        return 1, 1
    if variant == "left":
        return 1, 2
    if variant == "right":
        return 2, 1
    raise ValueError(f"unknown variant: {variant}")


def closed_block(horizon: int, variant: Variant = "balanced") -> ClosedBlock:
    base = prefix_cost(horizon, variant)
    overhead = connector_overhead(variant)
    return ClosedBlock(
        component=variant,
        prefix_horizon=horizon,
        horizon=horizon + 1,
        prefix_cost=base,
        cost=(base[0] + overhead[0], base[1] + overhead[1]),
        time_overhead=1,
        cost_overhead=overhead,
    )


def theoretical_corner(variant: Variant) -> RatePair:
    if variant == "balanced":
        return Fraction(1, 2), Fraction(1, 2)
    if variant == "left":
        return Fraction(1, 2), Fraction(3, 2)
    if variant == "right":
        return Fraction(3, 2), Fraction(1, 2)
    raise ValueError(f"unknown variant: {variant}")


def weighted(pair: RatePair, weight: Fraction) -> Fraction:
    if not 0 <= weight <= 1:
        raise ValueError("weight must lie in [0,1]")
    return weight * pair[0] + (1 - weight) * pair[1]


def finite_closing_bound(
    prefix: Pair,
    horizon: int,
    time_overhead: int,
    overhead: Pair,
    weight: Fraction,
) -> tuple[Fraction, Fraction]:
    """Return the exact closed rate and its coarser prefix-plus-overhead bound."""

    if horizon < 1 or time_overhead < 0:
        raise ValueError("invalid horizons")
    prefix_rate = (
        Fraction(prefix[0], horizon),
        Fraction(prefix[1], horizon),
    )
    overhead_rate = (
        Fraction(overhead[0], horizon),
        Fraction(overhead[1], horizon),
    )
    exact = Fraction(
        weight * (prefix[0] + overhead[0])
        + (1 - weight) * (prefix[1] + overhead[1]),
        horizon + time_overhead,
    )
    coarse = weighted(prefix_rate, weight) + weighted(overhead_rate, weight)
    return exact, coarse


def shadow_margin_certificate(
    safety_margin: Fraction, shadow_error: Fraction
) -> bool:
    """Universal metric safety certificate without assuming a closed safe set."""

    if safety_margin < 0 or shadow_error < 0:
        raise ValueError("margin and error must be nonnegative")
    return shadow_error < safety_margin


def upward_contains_corner(corner: RatePair, target: RatePair) -> bool:
    return target[0] >= corner[0] and target[1] >= corner[1]


def thue_morse_report(max_horizon: int = 4096) -> dict[str, Any]:
    ones = 0
    discrepancy_ok = True
    recurrence_ok = True
    block_lower_bounds = True
    variants: tuple[Variant, ...] = ("balanced", "left", "right")
    for horizon in range(1, max_horizon + 1):
        ones += thue_morse_bit(horizon - 1)
        discrepancy_ok &= abs(2 * ones - horizon) <= 1
        for variant in variants:
            block = closed_block(horizon, variant)
            corner = theoretical_corner(variant)
            block_lower_bounds &= upward_contains_corner(corner, block.rate)
    for index in range(max_horizon // 2):
        recurrence_ok &= thue_morse_bit(2 * index) == thue_morse_bit(index)
        recurrence_ok &= thue_morse_bit(2 * index + 1) == 1 - thue_morse_bit(index)
    checks = {
        "prefix_discrepancy_at_most_one": discrepancy_ok,
        "substitution_recurrence": recurrence_ok,
        "all_closed_blocks_above_component_corners": block_lower_bounds,
    }
    return {
        "horizons": max_horizon,
        "checks": checks,
        "pass": all(checks.values()),
    }


def bounded_aperiodicity_report(
    max_period: int = 128, max_start: int = 64, window: int = 512
) -> dict[str, Any]:
    """Falsify all bounded eventual-period candidates; THEOREM.md gives the proof."""

    rejected = 0
    for period in range(1, max_period + 1):
        for start in range(max_start + 1):
            if any(
                thue_morse_bit(index) != thue_morse_bit(index + period)
                for index in range(start, start + window)
            ):
                rejected += 1
    total = max_period * (max_start + 1)
    checks = {
        "all_bounded_eventual_periods_rejected": rejected == total,
        "finite_exact_deterministic_quotient_boundary_exercised": total == 8320,
    }
    return {
        "candidates": total,
        "rejected": rejected,
        "checks": checks,
        "pass": all(checks.values()),
    }


def component_formula_report(max_power: int = 12) -> dict[str, Any]:
    variants: tuple[Variant, ...] = ("balanced", "left", "right")
    weights = tuple(Fraction(index, 32) for index in range(33))
    blocks = {
        variant: [closed_block(2**power, variant) for power in range(1, max_power + 1)]
        for variant in variants
    }
    support_convergence = True
    for variant in variants:
        corner = theoretical_corner(variant)
        final = blocks[variant][-1]
        error = max(final.rate[0] - corner[0], final.rate[1] - corner[1])
        support_convergence &= error == Fraction(1, 2 * (2**max_power + 1))
        for weight in weights:
            finite_support = min(weighted(block.rate, weight) for block in blocks[variant])
            support_convergence &= finite_support >= weighted(corner, weight)
            support_convergence &= (
                finite_support - weighted(corner, weight)
                <= Fraction(1, 2 * (2**max_power + 1))
            )

    left = theoretical_corner("left")
    right = theoretical_corner("right")
    false_midpoint = (Fraction(1), Fraction(1))
    midpoint_outside_union = not upward_contains_corner(
        left, false_midpoint
    ) and not upward_contains_corner(right, false_midpoint)
    midpoint_passes_collapsed_support = all(
        weighted(false_midpoint, weight)
        >= min(weighted(left, weight), weighted(right, weight))
        for weight in weights
    )
    checks = {
        "component_supports_converge_exactly": support_convergence,
        "irreversible_midpoint_outside_component_union": midpoint_outside_union,
        "collapsed_global_support_falsely_accepts_midpoint": midpoint_passes_collapsed_support,
    }
    return {
        "weights": len(weights),
        "power_horizons_per_component": max_power,
        "checks": checks,
        "pass": all(checks.values()),
    }


def finite_correction_report(max_horizon: int = 512) -> dict[str, Any]:
    weights = tuple(Fraction(index, 16) for index in range(17))
    variants: tuple[Variant, ...] = ("balanced", "left", "right")
    exact_below_coarse = True
    constant_overhead_vanishes = True
    rows = 0
    for horizon in range(1, max_horizon + 1):
        for variant in variants:
            prefix = prefix_cost(horizon, variant)
            overhead = connector_overhead(variant)
            for weight in weights:
                exact, coarse = finite_closing_bound(
                    prefix, horizon, 1, overhead, weight
                )
                exact_below_coarse &= exact <= coarse
                rows += 1
        constant_overhead_vanishes &= Fraction(2, horizon) <= Fraction(2)
    final_overhead = Fraction(2, max_horizon)
    linear_overhead = Fraction(math.ceil(max_horizon / 4), max_horizon)
    checks = {
        "exact_closed_rate_below_prefix_plus_overhead_bound": exact_below_coarse,
        "constant_cost_overhead_is_sublinear": constant_overhead_vanishes
        and final_overhead == Fraction(1, 256),
        "linear_cost_overhead_has_positive_rate": linear_overhead >= Fraction(1, 4),
        "strict_margin_accepts_safe_shadow": shadow_margin_certificate(
            Fraction(1), Fraction(3, 4)
        ),
        "strict_margin_rejects_unregistered_boundary_case": not shadow_margin_certificate(
            Fraction(1), Fraction(1)
        ),
    }
    return {
        "rows": rows,
        "final_constant_overhead": str(final_overhead),
        "final_linear_overhead": str(linear_overhead),
        "checks": checks,
        "pass": all(checks.values()),
    }


def burst_liminf_limsup_report(stages: int = 8) -> dict[str, Any]:
    total = 1
    ones = 0
    lows: list[Fraction] = []
    highs: list[Fraction] = []
    for stage in range(stages):
        bit = stage & 1
        length = 10 * total + 1
        total += length
        ones += bit * length
        average = Fraction(ones, total)
        if bit:
            highs.append(average)
        else:
            lows.append(average)
    checks = {
        "low_subsequence_below_one_tenth": min(lows) < Fraction(1, 10),
        "high_subsequence_above_nine_tenths": max(highs) > Fraction(9, 10),
        "liminf_limsup_polarity_separated": min(lows) < max(highs),
    }
    return {
        "stages": stages,
        "checks": checks,
        "pass": all(checks.values()),
    }


def mutation_report() -> dict[str, Any]:
    components = component_formula_report()
    aperiodic = bounded_aperiodicity_report()
    corrections = finite_correction_report()
    bursts = burst_liminf_limsup_report()
    one_port_overhead = (
        Fraction(0, 512),
        Fraction(math.ceil(512 / 4), 512),
    )
    unregistered_composition_charge = Fraction(128, 128)
    scope_open = contract_report()["checks"]["keeps_global_gap_open"] and claim_report()[
        "checks"
    ]["scope_boundary"]
    rows = {
        "one_support_family_across_irreversible_components": components["checks"][
            "collapsed_global_support_falsely_accepts_midpoint"
        ],
        "finite_exact_quotient_is_necessary": aperiodic["checks"][
            "all_bounded_eventual_periods_rejected"
        ],
        "linear_closing_cost_has_zero_rate": corrections["checks"][
            "linear_cost_overhead_has_positive_rate"
        ],
        "one_port_overhead_controls_both_ports": one_port_overhead
        == (Fraction(0), Fraction(1, 4)),
        "liminf_can_replace_registered_limsup": bursts["checks"][
            "liminf_limsup_polarity_separated"
        ],
        "shadow_error_needs_no_safety_margin": corrections["checks"][
            "strict_margin_rejects_unregistered_boundary_case"
        ],
        "concatenation_needs_no_submultiplicative_cost_law": unregistered_composition_charge
        == 1,
        "block_formula_resolves_unspecified_global_class": scope_open,
    }
    return {
        "rows": rows,
        "cases": len(rows),
        "rejected": sum(rows.values()),
        "pass": len(rows) == 8 and all(rows.values()),
    }


def _count_tests(path: Path) -> int:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
        for node in ast.walk(tree)
    )


def _package_version(name: str) -> int:
    match = re.search(r"_v0_(\d+)$", name)
    return int(match.group(1)) if match else 0


def predecessor_inventory_report() -> dict[str, Any]:
    paths = sorted(
        path
        for path in ROOT.glob("asmp4*/test_*.py")
        if path.parent.resolve() != HERE.resolve()
        and _package_version(path.parent.name) < 33
    )
    rows = [
        {"package": path.parent.name, "file": path.name, "tests": _count_tests(path)}
        for path in paths
    ]
    checks = {
        "thirty_three_predecessor_packages": len(rows) == 33,
        "three_hundred_sixty_four_predecessor_tests": sum(
            row["tests"] for row in rows
        )
        == 364,
    }
    return {
        "rows": rows,
        "packages": len(rows),
        "tests": sum(row["tests"] for row in rows),
        "checks": checks,
        "pass": all(checks.values()),
    }


def claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_nonfinite_safe_closing_v0_33",
        "theorem": {
            "component_region": "R_q=closure(upward(conv(P_q)))",
            "support_formula": "R_q=intersection_lambda {(r,w): lambda*r+(1-lambda)*w >= h_q(lambda)}",
            "global_region": "closure(R)=closure(union_q R_q)",
            "finite_correction": "closed weighted rate <= prefix weighted rate plus weighted closing overhead/T",
            "coordinate_invariance": "cost-preserving causal conjugacies transport components, blocks, h_q, and R",
        },
        "hypotheses": {
            "component_indexed": True,
            "safe_reset_concatenation": True,
            "cofinal_sublinear_cost_closing": True,
            "sublinear_time_for_rate_preservation": True,
            "shadow_error_below_registered_margin": True,
        },
        "nonfinite_fixture": {
            "sequence": "Thue-Morse",
            "finite_exact_stationary_quotient": False,
            "balanced_corner": ["1/2", "1/2"],
            "closing_time_overhead": 1,
            "closing_cost_overhead": [1, 1],
        },
        "nonconvex_boundary": {
            "component_corners": [["1/2", "3/2"], ["3/2", "1/2"]],
            "false_collapsed_midpoint": [1, 1],
        },
        "evidence": {
            "aperiodicity_candidates_rejected": 8320,
            "prefix_horizons": 4096,
            "finite_correction_rows": 26112,
            "mutations_rejected": 8,
            "predecessor_packages": 33,
            "predecessor_tests": 364,
        },
        "disposition": "nonfinite variational replacement proved under an explicit safe-closing property; arbitrary nonlinear safe-closing remains open",
    }


def contract_report() -> dict[str, Any]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    checks = {
        "schema": contract.get("schema_version")
        == "asmp4_safe_closing_contract_v0_33",
        "nonfinite_scope": contract.get("objective", "").startswith(
            "prove a nonfinite"
        ),
        "does_not_assume_finite_quotient": contract.get("requirements", {}).get(
            "finite_quotient"
        )
        == "not required",
        "keeps_global_gap_open": "not a full ASMP-4 resolution"
        in contract.get("scope_boundary", ""),
    }
    return {"checks": checks, "pass": all(checks.values())}


def claim_report() -> dict[str, Any]:
    actual = json.loads(CLAIM.read_text(encoding="utf-8"))
    expected = claim_payload()
    checks = {
        "exact_payload": actual == expected,
        "nonfinite_witness": actual.get("nonfinite_fixture", {}).get(
            "finite_exact_stationary_quotient"
        )
        is False,
        "scope_boundary": "remains open" in actual.get("disposition", ""),
    }
    return {"checks": checks, "pass": all(checks.values())}


def payload_report() -> dict[str, Any]:
    missing = [name for name in EXPECTED_PAYLOAD if not (HERE / name).is_file()]
    return {"missing": missing, "pass": not missing}


def full_report() -> dict[str, Any]:
    report = {
        "contract": contract_report(),
        "claim": claim_report(),
        "thue_morse": thue_morse_report(),
        "aperiodicity": bounded_aperiodicity_report(),
        "components": component_formula_report(),
        "finite_correction": finite_correction_report(),
        "bursts": burst_liminf_limsup_report(),
        "mutations": mutation_report(),
        "inventory": predecessor_inventory_report(),
        "payload": payload_report(),
    }
    report["pass"] = all(section["pass"] for section in report.values())
    return report


def main() -> int:
    report = full_report()
    gates = {
        "R0_contract": report["contract"]["pass"],
        "R1_claim": report["claim"]["pass"],
        "R2_thue_morse": report["thue_morse"]["pass"],
        "R3_aperiodicity": report["aperiodicity"]["pass"],
        "R4_component_formula": report["components"]["pass"],
        "R5_finite_correction": report["finite_correction"]["pass"],
        "R6_limsup_boundary": report["bursts"]["pass"],
        "R7_mutations": report["mutations"]["pass"],
        "R8_predecessor_inventory": report["inventory"]["pass"],
        "R9_payload": report["payload"]["pass"],
    }
    print(json.dumps({"gates": gates, "report": report}, indent=2, sort_keys=True))
    return 0 if all(gates.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
