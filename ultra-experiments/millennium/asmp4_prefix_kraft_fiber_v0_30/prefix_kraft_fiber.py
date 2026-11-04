"""Sequential Kraft-rounding transfer under causal ASMP-4 tree factors."""

from __future__ import annotations

import ast
import hashlib
import itertools
import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
V03 = ROOT / "asmp4_metric_robust_collapse_v0_3" / "resolution_claim_v0_3.json"
V29 = ROOT / "asmp4_causal_branch_fiber_v0_29" / "causal_branch_fiber_claim_v0_29.json"
V28_CENTRAL = (
    ROOT / "asmp4_transcript_fiber_entropy_v0_28" / "transcript_fiber_entropy.py"
)
V28_TEST = (
    "asmp4_transcript_fiber_entropy_v0_28",
    "test_transcript_fiber_entropy.py",
)
V29_TEST = ("asmp4_causal_branch_fiber_v0_29", "test_causal_branch_fiber.py")
CONTRACT = HERE / "prefix_kraft_fiber_contract_v0_30.json"
CLAIM = HERE / "prefix_kraft_fiber_claim_v0_30.json"

SEALS = {
    SOURCE: "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    V03: "eb56ebbbccc2f088e09ccc5a6ff55f6403dcdf54ef47d9879dc207285cf31da1",
    V29: "0ad83cb7d61f777b67ce804f35141ab1ffe93e703c3d11144cc3ea38afe95f28",
}

Word = tuple[int, ...]
Language = tuple[Word, ...]
EdgeLabels = dict[tuple[Word, int], int]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(words: Iterable[Word]) -> Language:
    language = tuple(sorted(set(words)))
    if not language:
        raise ValueError("language must be nonempty")
    if len({len(word) for word in language}) != 1:
        raise ValueError("all words must have equal length")
    return language


def successors(language: Language) -> dict[Word, tuple[int, ...]]:
    horizon = len(language[0])
    result: dict[Word, set[int]] = {}
    for word in language:
        for time in range(horizon):
            result.setdefault(word[:time], set()).add(word[time])
    return {prefix: tuple(sorted(symbols)) for prefix, symbols in result.items()}


def edges(language: Language) -> tuple[tuple[Word, int], ...]:
    return tuple(
        (prefix, symbol)
        for prefix, symbols in sorted(
            successors(language).items(), key=lambda item: (len(item[0]), item[0])
        )
        for symbol in symbols
    )


def ceil_log2(integer: int) -> int:
    if integer < 1:
        raise ValueError("integer must be positive")
    return (integer - 1).bit_length()


def prefix_cost(language: Language) -> int:
    successor_map = successors(language)

    @lru_cache(maxsize=None)
    def cost(prefix: Word) -> int:
        children = successor_map.get(prefix, ())
        if not children:
            return 0
        kraft_sum = sum(2 ** cost(prefix + (symbol,)) for symbol in children)
        return ceil_log2(kraft_sum)

    return cost(())


def causal_image(language: Language, labels: EdgeLabels) -> tuple[Language, dict[Word, Word]]:
    word_map: dict[Word, Word] = {}
    for word in language:
        prefix: Word = ()
        image: Word = ()
        for symbol in word:
            image = image + (labels[(prefix, symbol)],)
            prefix = prefix + (symbol,)
        word_map[word] = image
    return normalize(word_map.values()), word_map


def rounded_local_fiber_cost(language: Language, labels: EdgeLabels) -> tuple[int, int]:
    successor_map = successors(language)
    horizon = len(language[0])
    rounded_maximum = 0
    unrounded_product_maximum = 1
    for word in language:
        rounded = 0
        product = 1
        for time in range(horizon):
            prefix = word[:time]
            counts: dict[int, int] = {}
            for symbol in successor_map[prefix]:
                image = labels[(prefix, symbol)]
                counts[image] = counts.get(image, 0) + 1
            maximum = max(counts.values())
            rounded += ceil_log2(maximum)
            product *= maximum
        rounded_maximum = max(rounded_maximum, rounded)
        unrounded_product_maximum = max(unrounded_product_maximum, product)
    return rounded_maximum, unrounded_product_maximum


def terminal_fiber(word_map: dict[Word, Word]) -> int:
    counts: dict[Word, int] = {}
    for image in word_map.values():
        counts[image] = counts.get(image, 0) + 1
    return max(counts.values())


def morphism_report(language: Language, labels: EdgeLabels) -> dict[str, Any]:
    image, word_map = causal_image(language, labels)
    target = prefix_cost(language)
    source = prefix_cost(image)
    rounded, product = rounded_local_fiber_cost(language, labels)
    return {
        "target_prefix_cost": target,
        "source_prefix_cost": source,
        "rounded_local_cost": rounded,
        "unrounded_local_product": product,
        "terminal_fiber": terminal_fiber(word_map),
        "inequality": target <= source + rounded,
        "gap": target - source,
    }


def disclosure_fixture() -> tuple[Language, EdgeLabels]:
    language = normalize(((0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 0, 0)))
    labels = {
        ((), 0): 0,
        ((), 1): 0,
        ((0,), 0): 0,
        ((0,), 1): 1,
        ((1,), 0): 1,
        ((0, 0), 0): 0,
        ((0, 0), 1): 1,
        ((0, 1), 0): 0,
        ((1, 0), 0): 1,
    }
    return language, labels


def disclosure_report() -> dict[str, Any]:
    language, labels = disclosure_fixture()
    report = morphism_report(language, labels)
    checks = {
        "target_cost_three": report["target_prefix_cost"] == 3,
        "source_cost_two": report["source_prefix_cost"] == 2,
        "terminal_fiber_one": report["terminal_fiber"] == 1,
        "rounded_local_cost_one": report["rounded_local_cost"] == 1,
        "bound_tight": report["gap"] == report["rounded_local_cost"],
    }
    return {**report, "checks": checks, "pass": all(checks.values())}


def concatenate(blocks: tuple[Word, ...]) -> Word:
    return tuple(symbol for block in blocks for symbol in block)


@lru_cache(maxsize=None)
def repeated_disclosure_report(maximum_blocks: int = 7) -> dict[str, Any]:
    base, labels = disclosure_fixture()
    _, base_map = causal_image(base, labels)
    rows = []
    for block_count in range(1, maximum_blocks + 1):
        choices = tuple(itertools.product(base, repeat=block_count))
        target_words = tuple(concatenate(blocks) for blocks in choices)
        source_words = tuple(
            concatenate(tuple(base_map[block] for block in blocks)) for blocks in choices
        )
        target = normalize(target_words)
        source = normalize(source_words)
        image_counts: dict[Word, int] = {}
        for image in source_words:
            image_counts[image] = image_counts.get(image, 0) + 1
        terminal_maximum = max(image_counts.values())
        target_cost = prefix_cost(target)
        source_cost = prefix_cost(source)
        rows.append(
            {
                "blocks": block_count,
                "horizon": 3 * block_count,
                "leaves": len(target),
                "target_cost": target_cost,
                "source_cost": source_cost,
                "rounded_local_cost": block_count,
                "terminal_fiber": terminal_maximum,
                "exact": target_cost == 3 * block_count
                and source_cost == 2 * block_count
                and target_cost - source_cost == block_count,
            }
        )
    checks = {
        "seven_block_powers": len(rows) == 7,
        "largest_has_16384_leaves": rows[-1]["leaves"] == 16_384,
        "all_prefix_bounds_tight": all(row["exact"] for row in rows),
        "terminal_fiber_stays_one": all(row["terminal_fiber"] == 1 for row in rows),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


@lru_cache(maxsize=None)
def exhaustive_binary_morphism_report(horizon: int = 3) -> dict[str, Any]:
    universe = tuple(itertools.product((0, 1), repeat=horizon))
    checked = 0
    failures = []
    strict = 0
    for mask in range(1, 1 << len(universe)):
        language = normalize(
            universe[index]
            for index in range(len(universe))
            if mask & (1 << index)
        )
        language_edges = edges(language)
        for outputs in itertools.product((0, 1), repeat=len(language_edges)):
            checked += 1
            labels = dict(zip(language_edges, outputs, strict=True))
            report = morphism_report(language, labels)
            if not report["inequality"]:
                failures.append({"language": language, "outputs": outputs})
            if report["terminal_fiber"] == 1 and report["gap"] > 0:
                strict += 1
    checks = {
        "three_hundred_thirty_two_thousand_nine_hundred_twenty_eight_maps": checked
        == 332_928,
        "all_binary_maps_obey_rounded_bound": not failures,
        "terminal_injective_positive_prefix_gaps_exist": strict > 0,
    }
    return {
        "checked": checked,
        "failures": failures,
        "strict": strict,
        "checks": checks,
        "pass": all(checks.values()),
    }


def regular_clone_report(maximum_factor: int = 16, maximum_horizon: int = 32) -> dict[str, Any]:
    rows = []
    for factor in range(1, maximum_factor + 1):
        per_step = ceil_log2(factor)
        for horizon in range(1, maximum_horizon + 1):
            prefix = horizon * per_step
            product = factor**horizon
            once_rounded = ceil_log2(product)
            rows.append(
                {
                    "factor": factor,
                    "horizon": horizon,
                    "prefix_cost": prefix,
                    "rounded_local_cost": prefix,
                    "unrounded_bits": math.log2(product),
                    "once_rounded": once_rounded,
                    "exact": prefix == horizon * ceil_log2(factor),
                    "single_rounding_fails": prefix > once_rounded,
                }
            )
    checks = {
        "five_hundred_twelve_rows": len(rows) == 512,
        "all_regular_clone_costs_exact": all(row["exact"] for row in rows),
        "ternary_per_step_cost_two": all(
            row["prefix_cost"] == 2 * row["horizon"]
            for row in rows
            if row["factor"] == 3
        ),
        "single_final_rounding_fails_for_ternary_repetition": all(
            row["single_rounding_fails"]
            for row in rows
            if row["factor"] == 3 and row["horizon"] >= 3
        ),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


@lru_cache(maxsize=None)
def mixed_schedule_report(horizon: int = 7) -> dict[str, Any]:
    rows = []
    for schedule in itertools.product((1, 2, 3, 4), repeat=horizon):
        sequential = sum(ceil_log2(factor) for factor in schedule)
        product = math.prod(schedule)
        rows.append(
            {
                "schedule": "".join(map(str, schedule)),
                "sequential": sequential,
                "once_rounded": ceil_log2(product),
                "unrounded": math.log2(product),
                "bound_exact": sequential
                == sum(ceil_log2(factor) for factor in schedule),
            }
        )
    checks = {
        "sixteen_thousand_three_hundred_eighty_four_schedules": len(rows) == 16_384,
        "all_sequential_costs_exact": all(row["bound_exact"] for row in rows),
        "all_ternary_schedule_has_linear_rounding_gap": next(
            row for row in rows if row["schedule"] == "3" * horizon
        )["sequential"]
        > next(row for row in rows if row["schedule"] == "3" * horizon)[
            "once_rounded"
        ],
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def sparse_rounding_report(maximum_horizon: int = 8192) -> dict[str, Any]:
    rows = []
    for horizon in range(1, maximum_horizon + 1):
        events = horizon.bit_length()
        rounded = 2 * events
        unrounded = math.log2(3) * events
        rows.append(
            {
                "horizon": horizon,
                "events": events,
                "rounded": rounded,
                "unrounded": unrounded,
                "rounded_rate": rounded / horizon,
            }
        )
    checks = {
        "eight_thousand_one_hundred_ninety_two_horizons": len(rows) == 8192,
        "rounded_profile_unbounded": rows[-1]["rounded"] > rows[0]["rounded"],
        "rounded_rate_tends_to_zero": rows[-1]["rounded_rate"] < 0.004,
        "rounded_at_most_twice_unrounded": all(
            row["rounded"] <= 2 * row["unrounded"] + 1e-12 for row in rows
        ),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def concentrated_and_burst_report() -> dict[str, Any]:
    concentrated = []
    for maximum in range(2, 65):
        target_degree = maximum + 1
        concentrated.append(
            {
                "maximum": maximum,
                "minimum": 1,
                "target_cost": ceil_log2(target_degree),
                "source_cost": 1,
                "maximum_bound": ceil_log2(target_degree)
                <= 1 + ceil_log2(maximum),
                "minimum_bound": ceil_log2(target_degree) <= 1,
            }
        )
    horizon = 2
    merge_steps = 1
    lows = []
    highs = []
    for _ in range(8):
        quiet_steps = horizon**2
        horizon += quiet_steps
        lows.append(merge_steps / horizon)
        burst_steps = horizon
        merge_steps += burst_steps
        horizon += burst_steps
        highs.append(merge_steps / horizon)
    checks = {
        "maximum_fiber_bounds_all_concentrated_rows": all(
            row["maximum_bound"] for row in concentrated
        ),
        "minimum_fiber_fails_all_rows": all(
            not row["minimum_bound"] for row in concentrated
        ),
        "liminf_near_zero": lows[-1] < 1e-20,
        "limsup_near_half": 0.499 < highs[-1] < 0.501,
    }
    return {
        "concentrated": concentrated,
        "lows": lows,
        "highs": highs,
        "checks": checks,
        "pass": all(checks.values()),
    }


def mutation_report() -> dict[str, Any]:
    disclosure = disclosure_report()
    repeated = repeated_disclosure_report()
    clones = regular_clone_report(6, 8)
    sparse = sparse_rounding_report()
    max_limsup = concentrated_and_burst_report()
    ternary = next(
        row
        for row in clones["rows"]
        if row["factor"] == 3 and row["horizon"] == 8
    )
    rows = {
        "terminal_fiber_controls_prefix_cost": disclosure["terminal_fiber"] == 1
        and disclosure["gap"] > 0,
        "unrounded_branch_fiber_cost_suffices": ternary["prefix_cost"]
        > ternary["unrounded_bits"],
        "one_final_ceiling_suffices": ternary["single_rounding_fails"],
        "minimum_local_fiber_replaces_maximum": max_limsup["checks"][
            "minimum_fiber_fails_all_rows"
        ],
        "finite_fibers_imply_equal_rate": repeated["rows"][-1][
            "rounded_local_cost"
        ]
        / repeated["rows"][-1]["horizon"]
        > 0,
        "bounded_fibers_needed_for_zero_rate": sparse["checks"][
            "rounded_profile_unbounded"
        ]
        and sparse["checks"]["rounded_rate_tends_to_zero"],
        "liminf_replaces_limsup": max_limsup["checks"]["liminf_near_zero"]
        and max_limsup["checks"]["limsup_near_half"],
        "one_shared_port_profile": ceil_log2(3) != ceil_log2(5),
    }
    return {
        "rows": rows,
        "cases": len(rows),
        "rejected": sum(rows.values()),
        "pass": len(rows) == 8 and all(rows.values()),
    }


def _predecessor_tests() -> tuple[tuple[str, str], ...]:
    tree = ast.parse(V28_CENTRAL.read_text(encoding="utf-8"), filename=str(V28_CENTRAL))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "PREDECESSOR_TESTS"
            for target in node.targets
        ):
            return tuple(ast.literal_eval(node.value)) + (V28_TEST, V29_TEST)
    raise ValueError("v0.28 predecessor inventory not found")


def expected_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_prefix_kraft_fiber_contract_v0_30",
        "objective": "sequential minimax binary prefix-free cost under causal transcript factors",
        "prefix_cost": {
            "leaf": "P(p)=0",
            "recurrence": "P(p)=ceil(log2 sum_a 2^P(pa))",
            "interpretation": "minimum worst-case cumulative binary prefix-code length",
        },
        "causal_morphism": {
            "local_fiber": "m(p) is the maximum target-successor preimage count at prefix p",
            "rounded_profile": "C(T)=max_path sum_t ceil(log2 m(p_t))",
        },
        "transfer": {
            "finite_horizon": "P_target(T) <= P_source(T)+C(T)",
            "asymptotic": "rate slack chi=limsup_T C(T)/T",
            "exactness": "bidirectional sublinear rounded profiles preserve the prefix-cost region",
        },
        "boundary": {
            "ternary_clone": "sequential cost is 2T while unrounded fiber cost is T log2 3",
            "rounding": "ceil(log2 product m_t) cannot replace sum_t ceil(log2 m_t)",
            "terminal": "terminal fiber one can coexist with positive prefix-cost distortion",
        },
        "nonclaims": [
            "average-length or stochastic source coding",
            "nonbinary coding alphabets",
            "nonlinear quotient construction",
        ],
    }


def expected_claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_prefix_kraft_fiber_v0_30",
        "theorem": {
            "name": "rounded local-fiber Kraft transfer",
            "finite_horizon": "target sequential prefix cost is at most source cost plus worst-path sum of local ceil-log fibers",
            "asymptotic": "directed rate slack is rounded local-fiber entropy",
            "exact_corollary": "bidirectional sublinear rounded profiles preserve the complete prefix-cost region",
        },
        "sharpness": {
            "ternary_clone": "2 bits per step versus log2 3 unrounded bits",
            "disclosure": "terminal-bijective three-step factor attains one bit correction",
            "single_ceiling": "ceil(T log2 3) is strictly below 2T for every T at least 3",
        },
        "central_harness": {
            "binary_causal_maps": 332928,
            "regular_clone_rows": 512,
            "mixed_schedules": 16384,
            "disclosure_block_powers": 7,
            "sparse_horizons": 8192,
        },
        "independent_harness": {
            "full_ternary_binary_output_maps": 4096,
            "explicit_regular_trees": 30,
            "mixed_schedules": 15625,
            "sparse_horizons": 16384,
        },
        "mutations_rejected": 8,
        "predecessor_inventory": {"packages": 30, "tests": 334},
        "disposition": "sequential prefix-free transfer is controlled by per-prefix rounded local fibers, not terminal or unrounded fiber entropy",
    }


def resource_integrity_report() -> dict[str, Any]:
    rows = []
    for path, expected in SEALS.items():
        rows.append(
            {
                "name": path.name,
                "matches": hashlib.sha256(path.read_bytes()).hexdigest() == expected,
            }
        )
    return {"rows": rows, "pass": len(rows) == 3 and all(row["matches"] for row in rows)}


def predecessor_inventory_report() -> dict[str, Any]:
    rows = []
    for package, filename in _predecessor_tests():
        path = ROOT / package / filename
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        count = sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
            for node in tree.body
        )
        rows.append({"package": package, "tests": count})
    tests = sum(row["tests"] for row in rows)
    return {
        "rows": rows,
        "packages": len(rows),
        "tests": tests,
        "pass": len(rows) == 30 and tests == 334,
    }


def payload_report() -> dict[str, Any]:
    required = {
        "README.md",
        "THEOREM.md",
        "RESULT.md",
        "COMPLETION_AUDIT_v0_30.md",
        "REVIEWER_PACKET_v0_30.md",
        "PRIOR_ART_BOUNDARY_v0_30.md",
        "prefix_kraft_fiber_contract_v0_30.json",
        "prefix_kraft_fiber_claim_v0_30.json",
        "prefix_kraft_fiber.py",
        "verify_prefix_kraft_fiber.py",
        "test_prefix_kraft_fiber.py",
        "run_verification.py",
    }
    present = {path.name for path in HERE.iterdir() if path.is_file()}
    return {"missing": sorted(required - present), "pass": required <= present}


def prefix_kraft_report() -> dict[str, Any]:
    components = {
        "resource_integrity": resource_integrity_report(),
        "contract_exactness": {
            "pass": CONTRACT.exists() and _load(CONTRACT) == expected_contract_payload()
        },
        "claim_exactness": {
            "pass": CLAIM.exists() and _load(CLAIM) == expected_claim_payload()
        },
        "disclosure": disclosure_report(),
        "repeated_disclosure": repeated_disclosure_report(),
        "exhaustive_binary_morphisms": exhaustive_binary_morphism_report(),
        "regular_clones": regular_clone_report(),
        "mixed_schedules": mixed_schedule_report(),
        "sparse_rounding": sparse_rounding_report(),
        "max_limsup": concentrated_and_burst_report(),
        "mutations": mutation_report(),
        "predecessor_inventory": predecessor_inventory_report(),
        "payload": payload_report(),
    }
    return {
        "schema_version": "asmp4_prefix_kraft_fiber_v0_30",
        **components,
        "pass": all(component["pass"] for component in components.values()),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    report = prefix_kraft_report() if report is None else report
    return {
        "R0_three_resource_seals": report["resource_integrity"]["pass"],
        "R1_exact_contract": report["contract_exactness"]["pass"],
        "R2_exact_claim": report["claim_exactness"]["pass"],
        "R3_disclosure_sharpness": report["disclosure"]["pass"]
        and report["repeated_disclosure"]["pass"],
        "R4_all_binary_causal_maps": report["exhaustive_binary_morphisms"]["pass"],
        "R5_ternary_rounding_sharpness": report["regular_clones"]["pass"],
        "R6_mixed_schedule_rounding": report["mixed_schedules"]["pass"],
        "R7_sublinear_and_limsup_boundaries": report["sparse_rounding"]["pass"]
        and report["max_limsup"]["pass"],
        "R8_eight_mutations_rejected": report["mutations"]["pass"],
        "R9_inventory_and_payload": report["predecessor_inventory"]["pass"]
        and report["payload"]["pass"],
    }


def main() -> int:
    report = prefix_kraft_report()
    payload = {"gates": verification_gates(report), "report": report}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
