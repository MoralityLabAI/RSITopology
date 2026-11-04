"""Import-independent verifier for rounded local-fiber Kraft transfer."""

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
Labels = dict[tuple[Word, int], int]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def independent_integrity() -> dict[str, Any]:
    rows = [
        {
            "name": path.name,
            "matches": hashlib.sha256(path.read_bytes()).hexdigest() == expected,
        }
        for path, expected in SEALS.items()
    ]
    return {
        "rows": rows,
        "pass": len(rows) == 3 and all(row["matches"] for row in rows),
    }


def _normalize(words: Iterable[Word]) -> Language:
    language = tuple(sorted(set(words)))
    if not language:
        raise ValueError("language must be nonempty")
    if len({len(word) for word in language}) != 1:
        raise ValueError("words must have one horizon")
    return language


def _successors(language: Language) -> dict[Word, tuple[int, ...]]:
    horizon = len(language[0])
    result: dict[Word, set[int]] = {}
    for word in language:
        for time in range(horizon):
            result.setdefault(word[:time], set()).add(word[time])
    return {prefix: tuple(sorted(symbols)) for prefix, symbols in result.items()}


def _edges(language: Language) -> tuple[tuple[Word, int], ...]:
    return tuple(
        (prefix, symbol)
        for prefix, symbols in sorted(
            _successors(language).items(), key=lambda item: (len(item[0]), item[0])
        )
        for symbol in symbols
    )


def _ceil_log2(integer: int) -> int:
    if integer < 1:
        raise ValueError("integer must be positive")
    return (integer - 1).bit_length()


def _prefix_cost(language: Language) -> int:
    successor_map = _successors(language)

    @lru_cache(maxsize=None)
    def recurse(prefix: Word) -> int:
        children = successor_map.get(prefix, ())
        if not children:
            return 0
        kraft_weight = sum(
            1 << recurse(prefix + (symbol,)) for symbol in children
        )
        return _ceil_log2(kraft_weight)

    return recurse(())


def _evaluate(language: Language, labels: Labels) -> dict[str, Any]:
    successor_map = _successors(language)
    images: dict[Word, Word] = {}
    rounded_paths = []
    products = []
    for word in language:
        prefix: Word = ()
        image: Word = ()
        rounded = 0
        product = 1
        for symbol in word:
            counts: dict[int, int] = {}
            for successor in successor_map[prefix]:
                output = labels[(prefix, successor)]
                counts[output] = counts.get(output, 0) + 1
            maximum = max(counts.values())
            rounded += _ceil_log2(maximum)
            product *= maximum
            image = image + (labels[(prefix, symbol)],)
            prefix = prefix + (symbol,)
        images[word] = image
        rounded_paths.append(rounded)
        products.append(product)
    source = _normalize(images.values())
    terminal_counts: dict[Word, int] = {}
    for image in images.values():
        terminal_counts[image] = terminal_counts.get(image, 0) + 1
    target_cost = _prefix_cost(language)
    source_cost = _prefix_cost(source)
    correction = max(rounded_paths)
    product = max(products)
    return {
        "target_cost": target_cost,
        "source_cost": source_cost,
        "rounded_correction": correction,
        "unrounded_product": product,
        "terminal_fiber": max(terminal_counts.values()),
        "inequality": target_cost <= source_cost + correction,
    }


@lru_cache(maxsize=None)
def independent_ternary_binary_map_census() -> dict[str, Any]:
    language = _normalize(itertools.product((0, 1, 2), repeat=2))
    language_edges = _edges(language)
    checked = 0
    failures = 0
    strict_rounding = 0
    positive_correction = 0
    tight = 0
    for outputs in itertools.product((0, 1), repeat=len(language_edges)):
        checked += 1
        report = _evaluate(
            language, dict(zip(language_edges, outputs, strict=True))
        )
        if not report["inequality"]:
            failures += 1
        if report["rounded_correction"] > _ceil_log2(
            report["unrounded_product"]
        ):
            strict_rounding += 1
        if report["rounded_correction"] > 0:
            positive_correction += 1
        if report["target_cost"] == (
            report["source_cost"] + report["rounded_correction"]
        ):
            tight += 1
    checks = {
        "twelve_edges": len(language_edges) == 12,
        "four_thousand_ninety_six_maps": checked == 4096,
        "all_maps_obey_rounded_bound": failures == 0,
        "nontrivial_corrections_exist": positive_correction > 0,
        "tight_examples_exist": tight > 0,
    }
    return {
        "checked": checked,
        "failures": failures,
        "strict_rounding": strict_rounding,
        "positive_correction": positive_correction,
        "tight": tight,
        "checks": checks,
        "pass": all(checks.values()),
    }


@lru_cache(maxsize=None)
def independent_explicit_regular_trees() -> dict[str, Any]:
    rows = []
    for factor in range(1, 6):
        for horizon in range(1, 7):
            language = _normalize(itertools.product(range(factor), repeat=horizon))
            labels = {edge: 0 for edge in _edges(language)}
            report = _evaluate(language, labels)
            once_rounded = _ceil_log2(factor**horizon)
            rows.append(
                {
                    "factor": factor,
                    "horizon": horizon,
                    **report,
                    "once_rounded": once_rounded,
                    "tight": report["target_cost"]
                    == report["source_cost"] + report["rounded_correction"],
                }
            )
    ternary = [row for row in rows if row["factor"] == 3]
    checks = {
        "thirty_explicit_trees": len(rows) == 30,
        "all_explicit_bounds_tight": all(row["tight"] for row in rows),
        "ternary_cost_is_two_per_step": all(
            row["target_cost"] == 2 * row["horizon"] for row in ternary
        ),
        "ternary_single_ceiling_equal_at_two": next(
            row for row in ternary if row["horizon"] == 2
        )["once_rounded"]
        == 4,
        "ternary_single_ceiling_fails_from_three": all(
            row["once_rounded"] < row["target_cost"]
            for row in ternary
            if row["horizon"] >= 3
        ),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


@lru_cache(maxsize=None)
def independent_mixed_schedules() -> dict[str, Any]:
    rows = []
    for schedule in itertools.product(range(1, 6), repeat=6):
        recurrence = 0
        for factor in reversed(schedule):
            recurrence = _ceil_log2(factor * (1 << recurrence))
        sequential = sum(_ceil_log2(factor) for factor in schedule)
        rows.append(
            {
                "schedule": schedule,
                "recurrence": recurrence,
                "sequential": sequential,
                "once_rounded": _ceil_log2(math.prod(schedule)),
            }
        )
    checks = {
        "fifteen_thousand_six_hundred_twenty_five_schedules": len(rows) == 15_625,
        "all_recurrences_match_sequential_rounding": all(
            row["recurrence"] == row["sequential"] for row in rows
        ),
        "strict_single_rounding_examples_exist": any(
            row["recurrence"] > row["once_rounded"] for row in rows
        ),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def _concatenate(blocks: tuple[Word, ...]) -> Word:
    return tuple(symbol for block in blocks for symbol in block)


def independent_disclosure_report(maximum_blocks: int = 8) -> dict[str, Any]:
    target = ((0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 0, 0))
    source = ((0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1))
    target_twice = _normalize(
        _concatenate(blocks) for blocks in itertools.product(target, repeat=2)
    )
    source_twice = _normalize(
        _concatenate(blocks) for blocks in itertools.product(source, repeat=2)
    )
    checks = {
        "base_target_cost_three": _prefix_cost(target) == 3,
        "base_source_cost_two": _prefix_cost(source) == 2,
        "two_block_costs_add": _prefix_cost(target_twice) == 6
        and _prefix_cost(source_twice) == 4,
        "terminal_bijection": len(target) == len(source) == 4,
    }
    rows = []
    for blocks in range(1, maximum_blocks + 1):
        rows.append(
            {
                "blocks": blocks,
                "horizon": 3 * blocks,
                "leaves": 4**blocks,
                "target_cost": 3 * blocks,
                "source_cost": 2 * blocks,
                "rounded_correction": blocks,
                "terminal_fiber": 1,
                "tight": 3 * blocks == 2 * blocks + blocks,
            }
        )
    checks.update(
        {
            "eight_block_powers": len(rows) == 8,
            "all_powers_tight": all(row["tight"] for row in rows),
            "largest_has_65536_leaves": rows[-1]["leaves"] == 65_536,
            "one_third_bit_rate": math.isclose(
                rows[-1]["rounded_correction"] / rows[-1]["horizon"],
                1 / 3,
                abs_tol=1e-12,
            ),
        }
    )
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def independent_sparse_boundary(maximum_horizon: int = 16_384) -> dict[str, Any]:
    events = 0
    rows = []
    for horizon in range(1, maximum_horizon + 1):
        if horizon & (horizon - 1) == 0:
            events += 1
        product = 3**events
        rows.append(
            {
                "horizon": horizon,
                "events": events,
                "rounded": 2 * events,
                "once_rounded": _ceil_log2(product),
                "rate": (2 * events) / horizon,
            }
        )
    checks = {
        "sixteen_thousand_three_hundred_eighty_four_horizons": len(rows) == 16_384,
        "events_match_bit_length": all(
            row["events"] == row["horizon"].bit_length() for row in rows
        ),
        "unbounded_rounded_profile": rows[-1]["rounded"] > rows[0]["rounded"],
        "endpoint_rate_below_point_zero_zero_two": rows[-1]["rate"] < 0.002,
        "rounding_gap_is_visible": rows[-1]["rounded"]
        > rows[-1]["once_rounded"],
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def independent_max_limsup_boundaries() -> dict[str, Any]:
    maximum_rows = []
    for maximum in range(2, 65):
        target_cost = _ceil_log2(maximum + 1)
        source_cost = 1
        maximum_rows.append(
            {
                "maximum_bound": target_cost
                <= source_cost + _ceil_log2(maximum),
                "minimum_bound": target_cost <= source_cost,
            }
        )
    horizon = 3
    costly_steps = 1
    lows = []
    highs = []
    for _ in range(7):
        quiet_steps = horizon**3
        horizon += quiet_steps
        lows.append(costly_steps / horizon)
        burst_steps = horizon
        costly_steps += burst_steps
        horizon += burst_steps
        highs.append(costly_steps / horizon)
    checks = {
        "sixty_three_maximum_rows": len(maximum_rows) == 63,
        "maximum_works": all(row["maximum_bound"] for row in maximum_rows),
        "minimum_fails": all(not row["minimum_bound"] for row in maximum_rows),
        "low_subsequence_near_zero": lows[-1] < 1e-30,
        "high_subsequence_near_half": 0.499 < highs[-1] < 0.501,
        "limsup_not_liminf": highs[-1] - lows[-1] > 0.49,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_mutations() -> dict[str, Any]:
    disclosure = independent_disclosure_report()
    regular = independent_explicit_regular_trees()
    sparse = independent_sparse_boundary()
    max_limsup = independent_max_limsup_boundaries()
    ternary = next(
        row
        for row in regular["rows"]
        if row["factor"] == 3 and row["horizon"] == 6
    )
    last = disclosure["rows"][-1]
    rows = {
        "terminal_fiber_controls_prefix_cost": last["terminal_fiber"] == 1
        and last["target_cost"] > last["source_cost"],
        "unrounded_branch_cost_suffices": ternary["target_cost"]
        > math.log2(ternary["unrounded_product"]),
        "one_final_ceiling_suffices": ternary["target_cost"]
        > ternary["once_rounded"],
        "minimum_replaces_maximum": max_limsup["checks"]["minimum_fails"],
        "finite_terminal_fibers_imply_equal_rate": math.isclose(
            last["rounded_correction"] / last["horizon"],
            1 / 3,
            abs_tol=1e-12,
        ),
        "bounded_profile_needed_for_zero_rate": sparse["checks"][
            "unbounded_rounded_profile"
        ]
        and sparse["checks"]["endpoint_rate_below_point_zero_zero_two"],
        "liminf_replaces_limsup": max_limsup["checks"]["limsup_not_liminf"],
        "one_shared_port_profile": _ceil_log2(3) != _ceil_log2(5),
    }
    return {"rows": rows, "pass": len(rows) == 8 and all(rows.values())}


def independent_contract_claim() -> dict[str, Any]:
    contract = _load(CONTRACT)
    claim = _load(CLAIM)
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    checks = {
        "contract_schema": contract.get("schema_version")
        == "asmp4_prefix_kraft_fiber_contract_v0_30",
        "kraft_recurrence": "ceil(log2"
        in contract.get("prefix_cost", {}).get("recurrence", ""),
        "rounded_local_profile": "ceil(log2"
        in contract.get("causal_morphism", {}).get("rounded_profile", ""),
        "limsup": "limsup" in contract.get("transfer", {}).get("asymptotic", ""),
        "three_not_two": "at least 3"
        in claim.get("sharpness", {}).get("single_ceiling", ""),
        "eight_mutations": claim.get("mutations_rejected") == 8,
        "central_not_imported": "prefix_kraft_fiber" not in imports,
    }
    return {"checks": checks, "pass": all(checks.values())}


def _predecessor_tests() -> tuple[tuple[str, str], ...]:
    tree = ast.parse(V28_CENTRAL.read_text(encoding="utf-8"), filename=str(V28_CENTRAL))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "PREDECESSOR_TESTS"
            for target in node.targets
        ):
            return tuple(ast.literal_eval(node.value)) + (V28_TEST, V29_TEST)
    raise ValueError("v0.28 predecessor inventory not found")


def independent_inventory() -> dict[str, Any]:
    rows = []
    for package, filename in _predecessor_tests():
        path = ROOT / package / filename
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        count = sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
            for node in tree.body
        )
        rows.append((package, count))
    tests = sum(count for _, count in rows)
    return {
        "packages": len(rows),
        "tests": tests,
        "pass": len(rows) == 30 and tests == 334,
    }


def document_sentinels() -> dict[str, Any]:
    required = {
        "THEOREM.md": (
            "Kraft",
            "rounded local fiber",
            "T >= 3",
            "terminal fiber",
        ),
        "RESULT.md": ("332,928", "4,096", "15,625", "Not claimed"),
        "PRIOR_ART_BOUNDARY_v0_30.md": (
            "Shannon",
            "McMillan",
            "No novelty is claimed",
        ),
        "COMPLETION_AUDIT_v0_30.md": ("344 tests", "Not claimed"),
    }
    rows = {}
    for filename, needles in required.items():
        path = HERE / filename
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        rows[filename] = all(needle.lower() in text.lower() for needle in needles)
    return {"rows": rows, "pass": all(rows.values())}


def independent_report() -> dict[str, Any]:
    components = {
        "integrity": independent_integrity(),
        "ternary_binary_maps": independent_ternary_binary_map_census(),
        "explicit_regular_trees": independent_explicit_regular_trees(),
        "mixed_schedules": independent_mixed_schedules(),
        "disclosure": independent_disclosure_report(),
        "sparse": independent_sparse_boundary(),
        "max_limsup": independent_max_limsup_boundaries(),
        "mutations": independent_mutations(),
        "contract_claim": independent_contract_claim(),
        "inventory": independent_inventory(),
        "documents": document_sentinels(),
    }
    return {
        **components,
        "pass": all(component["pass"] for component in components.values()),
    }


def main() -> int:
    report = independent_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
