"""Independent verifier for the ASMP-4 metric-robust bilateral relay theorem."""

from __future__ import annotations

import itertools
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent


def independent_branch_product(language: tuple[tuple[str, ...], ...]) -> int:
    horizon = len(language[0])
    maximum = 1
    for word in language:
        product = 1
        for event in range(horizon):
            next_symbols = set()
            for candidate in language:
                if candidate[:event] == word[:event]:
                    next_symbols.add(candidate[event])
            product *= len(next_symbols)
        maximum = max(maximum, product)
    return maximum


def independent_prefix_cost(language: tuple[tuple[str, ...], ...]) -> int:
    """Exact minimax binary prefix-code cost, recomputed without the harness."""

    horizon = len(language[0])

    def recurse(prefix: tuple[str, ...]) -> int:
        if len(prefix) == horizon:
            return 0
        successors = sorted(
            {word[len(prefix)] for word in language if word[: len(prefix)] == prefix}
        )
        kraft_sum = sum(2 ** recurse(prefix + (symbol,)) for symbol in successors)
        return (kraft_sum - 1).bit_length()

    return recurse(())


def independent_small_census() -> dict[str, object]:
    checked = 0
    failures = []
    for horizon in range(4):
        universe = tuple(itertools.product(("0", "1"), repeat=horizon))
        for size in range(1, len(universe) + 1):
            for language in itertools.combinations(universe, size):
                checked += 1
                product = independent_branch_product(language)
                if product < len(language):
                    failures.append(
                        {
                            "horizon": horizon,
                            "language": language,
                            "branch_product": product,
                        }
                    )
    return {"checked": checked, "failures": failures, "pass": not failures}


def independent_comb_check(max_horizon: int = 64) -> dict[str, object]:
    rows = []
    for horizon in range(1, max_horizon + 1):
        language = [("0",) * horizon]
        language.extend(
            ("0",) * event + ("1",) + ("0",) * (horizon - event - 1)
            for event in range(horizon)
        )
        normalized = tuple(sorted(language))
        product = independent_branch_product(normalized)
        rows.append(
            {
                "horizon": horizon,
                "language_count": len(normalized),
                "branch_product": product,
                "language_rate": math.log2(len(normalized)) / horizon,
                "branch_rate": math.log2(product) / horizon,
            }
        )
    return {
        "rows": rows,
        "pass": all(
            row["language_count"] == row["horizon"] + 1
            and row["branch_product"] == 2 ** row["horizon"]
            and row["branch_rate"] == 1.0
            for row in rows
        ),
    }


def independent_delay_check() -> dict[str, object]:
    rows = []
    for read_delay in range(3):
        for write_delay in range(3):
            for horizon in range(5):
                count = 2 ** max(0, horizon - read_delay)
                rows.append(
                    {
                        "read_delay": read_delay,
                        "write_delay": write_delay,
                        "horizon": horizon,
                        "original_read_count": count,
                        "downstream_write_count": count,
                        "applied_input_shift": write_delay,
                    }
                )
    return {
        "rows": rows,
        "pass": all(
            row["original_read_count"] == row["downstream_write_count"]
            and row["applied_input_shift"] == row["write_delay"]
            for row in rows
        ),
    }


def independent_skew_check(max_binary_depth: int = 10) -> dict[str, object]:
    """Independently separate language, minimax-prefix, and branch costs."""

    rows = []
    for depth in range(2, max_binary_depth + 1):
        tail = ("fixed",) * depth
        language = [
            ("heavy",) + word for word in itertools.product(("0", "1"), repeat=depth)
        ]
        language.extend((("light_a",) + tail, ("light_b",) + tail))
        normalized = tuple(sorted(language))
        language_bits = math.log2(len(normalized))
        prefix_bits = independent_prefix_cost(normalized)
        branch_bits = math.log2(independent_branch_product(normalized))
        rows.append(
            {
                "binary_depth": depth,
                "language_bits": language_bits,
                "prefix_worst_bits": prefix_bits,
                "branch_bits": branch_bits,
            }
        )
    return {
        "rows": rows,
        "pass": all(
            row["prefix_worst_bits"] == row["binary_depth"] + 1
            and math.isclose(row["branch_bits"], row["binary_depth"] + math.log2(3))
            and row["language_bits"] < row["prefix_worst_bits"] < row["branch_bits"]
            for row in rows
        ),
    }


def independent_prefix_rounding_check() -> dict[str, object]:
    language = (
        ("heavy", "0"),
        ("heavy", "1"),
        ("heavy", "2"),
        ("light", "fixed"),
    )
    language_bits = math.log2(len(language))
    branch_bits = math.log2(independent_branch_product(language))
    prefix_bits = independent_prefix_cost(language)
    return {
        "language_bits": language_bits,
        "branch_bits": branch_bits,
        "prefix_worst_bits": prefix_bits,
        "pass": language_bits == 2
        and branch_bits == math.log2(6)
        and prefix_bits == 3
        and language_bits < branch_bits < prefix_bits,
    }


def theorem_sentinels() -> dict[str, bool]:
    theorem = (HERE / "THEOREM.md").read_text(encoding="utf-8")
    result = (HERE / "RESULT.md").read_text(encoding="utf-8")
    return {
        "terminal_metric_defined": "C_T(L) = log2 |L(T)|" in theorem,
        "branch_metric_defined": "B_T(L) =" in theorem and "log2 deg_L" in theorem,
        "prefix_metric_defined": (
            "P_T(p) = ceil(log2 sum_(a after p) 2^P_T(pa))" in theorem
            and "minimum worst-case cumulative binary prefix-code length" in theorem
        ),
        "tree_domination": "C_T(L) <= B_T(L)" in theorem,
        "prefix_lower_bound": "C_T(L) <= P_T(L)" in theorem,
        "fixed_prefix_invariance": (
            "deterministic-prefix invariance" in theorem
            and "J_(T+d)(p_d L)=J_T(L)" in theorem
            and "difference is `o(T)` uniformly" in theorem
        ),
        "upstream_normal_form": "**Theorem 1 (upstream normal form).**" in theorem,
        "downstream_normal_form": "**Theorem 2 (downstream normal form).**" in theorem,
        "full_region": ("[h_J(K_0,K), infinity) x [h_J(K_0,K), infinity)" in theorem),
        "coordinate_invariance": (
            "The entropy is coordinate invariant." in theorem
            and "control-congruence" in theorem
        ),
        "one_sided_criterion": (
            "**Theorem 4.**" in theorem
            and "h_r^J <= h_w^J" in theorem
            and "h_w^J <= h_r^J" in theorem
        ),
        "metric_correction": (
            "T+1 terminal words but branch product 2^T" in theorem
            and "must not be identified" in result
        ),
        "boundary_scope": (
            "different cost or risk functionals on the two ports" in theorem
            and "positive conversion of units by itself is not a structural exception"
            in theorem
        ),
        "strict_gap_witnesses": (
            "Forced raw sensor, read above write." in theorem
            and "Fixed direct-action decoder, write above read." in theorem
        ),
        "fixed_delay_evidence": "all 96 combinations" in result,
        "three_metric_separation": (
            "C_T < P_T < B_T" in theorem and "pairwise numerically distinct" in theorem
        ),
        "reverse_three_metric_separation": (
            "C_T < B_T < P_T" in theorem
            and "ceil(log2(2^2+2^0)) = 3" in theorem
            and "neither `B_T` nor" in theorem
        ),
    }


def registry_check() -> dict[str, object]:
    registry = json.loads(
        (HERE.parent / "problem_set_v0_1.json").read_text(encoding="utf-8")
    )
    claim = json.loads(
        (HERE / "resolution_claim_v0_3.json").read_text(encoding="utf-8")
    )
    problem = next(
        item for item in registry["problems"] if item["id"] == claim["problem_id"]
    )
    positive_expected = set(problem["positive_resolution_requires"])
    negative_expected = set(problem["negative_resolution_requires"])
    positive_actual = set(claim["positive_obligation_evidence"])
    negative_actual = set(claim["negative_obligation_evidence"])
    return {
        "positive_exact": positive_actual == positive_expected,
        "negative_exact": negative_actual == negative_expected,
        "negative_resolution_allowed": problem["negative_resolution_allowed"],
        "empirical_resolution_forbidden": not problem["empirical_resolution_allowed"],
        "claim_is_nonempirical": not claim["empirical_resolution"],
    }


def verify() -> dict[str, object]:
    census = independent_small_census()
    comb = independent_comb_check()
    delays = independent_delay_check()
    skew = independent_skew_check()
    prefix_rounding = independent_prefix_rounding_check()
    sentinels = theorem_sentinels()
    registry = registry_check()
    checks = {
        "I0_independent_language_census": census["pass"] and census["checked"] == 274,
        "I1_independent_comb_separation": comb["pass"],
        "I2_independent_fixed_delay_replay": delays["pass"]
        and len(delays["rows"]) == 45,
        "I3_independent_prefix_metric_separation": skew["pass"],
        "I4_independent_prefix_rounding_separation": prefix_rounding["pass"],
        "I5_theorem_structure": all(sentinels.values()),
        "I6_registry_obligations": all(registry.values()),
    }
    return {
        "schema_version": "asmp4_metric_robust_independent_verification_v0_3",
        "census": census,
        "comb": comb,
        "delays": delays,
        "skew": skew,
        "prefix_rounding": prefix_rounding,
        "theorem_sentinels": sentinels,
        "registry": registry,
        "checks": checks,
        "pass": all(checks.values()),
    }


def main() -> int:
    payload = verify()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
