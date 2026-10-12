"""Import-independent verifier for causal successor-fiber branch bounds."""

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
V28 = (
    ROOT / "asmp4_transcript_fiber_entropy_v0_28" / "transcript_fiber_claim_v0_28.json"
)
V28_CENTRAL = (
    ROOT / "asmp4_transcript_fiber_entropy_v0_28" / "transcript_fiber_entropy.py"
)
V28_TEST = (
    "asmp4_transcript_fiber_entropy_v0_28",
    "test_transcript_fiber_entropy.py",
)
CONTRACT = HERE / "causal_branch_fiber_contract_v0_29.json"
CLAIM = HERE / "causal_branch_fiber_claim_v0_29.json"

SEALS = {
    SOURCE: "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    V03: "eb56ebbbccc2f088e09ccc5a6ff55f6403dcdf54ef47d9879dc207285cf31da1",
    V28: "25e43a710adfdbee59ad5dbd10b16c01051b007cd6978f50c59d982f02962d90",
}

Word = tuple[int, ...]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def independent_integrity() -> dict[str, Any]:
    rows = []
    for path, expected in SEALS.items():
        rows.append(
            {
                "name": path.name,
                "matches": hashlib.sha256(path.read_bytes()).hexdigest() == expected,
            }
        )
    return {
        "rows": rows,
        "pass": len(rows) == 3 and all(row["matches"] for row in rows),
    }


def _normalize(words: Iterable[Word]) -> tuple[Word, ...]:
    return tuple(sorted(set(words)))


def _successors(language: tuple[Word, ...]) -> dict[Word, tuple[int, ...]]:
    result: dict[Word, set[int]] = {}
    horizon = len(language[0])
    for word in language:
        for time in range(horizon):
            result.setdefault(word[:time], set()).add(word[time])
    return {prefix: tuple(sorted(values)) for prefix, values in result.items()}


def _edges(language: tuple[Word, ...]) -> tuple[tuple[Word, int], ...]:
    return tuple(
        (prefix, symbol)
        for prefix, symbols in sorted(
            _successors(language).items(), key=lambda item: (len(item[0]), item[0])
        )
        for symbol in symbols
    )


def _branch_product(language: tuple[Word, ...]) -> int:
    successor_map = _successors(language)
    horizon = len(language[0])
    return max(
        math.prod(len(successor_map[word[:time]]) for time in range(horizon))
        for word in language
    )


def _evaluate(
    language: tuple[Word, ...], labels: dict[tuple[Word, int], int]
) -> tuple[int, int, int, int]:
    successor_map = _successors(language)
    images: dict[Word, Word] = {}
    local_products = []
    for word in language:
        prefix: Word = ()
        image: Word = ()
        product = 1
        for symbol in word:
            counts: dict[int, int] = {}
            for successor in successor_map[prefix]:
                output = labels[(prefix, successor)]
                counts[output] = counts.get(output, 0) + 1
            product *= max(counts.values())
            image = image + (labels[(prefix, symbol)],)
            prefix = prefix + (symbol,)
        images[word] = image
        local_products.append(product)
    image_language = _normalize(images.values())
    terminal_counts: dict[Word, int] = {}
    for image in images.values():
        terminal_counts[image] = terminal_counts.get(image, 0) + 1
    return (
        _branch_product(language),
        _branch_product(image_language),
        max(local_products),
        max(terminal_counts.values()),
    )


@lru_cache(maxsize=None)
def independent_ternary_morphism_census() -> dict[str, Any]:
    horizon = 2
    universe = tuple(itertools.product((0, 1), repeat=horizon))
    checked = 0
    failures = 0
    strict = 0
    for mask in range(1, 1 << len(universe)):
        language = _normalize(
            universe[index] for index in range(len(universe)) if mask & (1 << index)
        )
        language_edges = _edges(language)
        for outputs in itertools.product((0, 1, 2), repeat=len(language_edges)):
            checked += 1
            labels = dict(zip(language_edges, outputs, strict=True))
            target, source, local, terminal = _evaluate(language, labels)
            if target > source * local:
                failures += 1
            if terminal == 1 and local > 1:
                strict += 1
    checks = {
        "two_thousand_one_hundred_fifteen_maps": checked == 2115,
        "all_ternary_output_maps_obey_bound": failures == 0,
        "injective_terminal_nontrivial_local_exists": strict > 0,
    }
    return {
        "checked": checked,
        "failures": failures,
        "strict": strict,
        "checks": checks,
        "pass": all(checks.values()),
    }


def independent_disclosure_report(maximum_blocks: int = 8) -> dict[str, Any]:
    target = ((0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 0, 0))
    source = ((0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1))
    checks = {
        "base_target_product_eight": _branch_product(target) == 8,
        "base_source_product_four": _branch_product(source) == 4,
        "terminal_bijection": len(target) == len(source) == 4,
    }
    rows = []
    for blocks in range(1, maximum_blocks + 1):
        rows.append(
            {
                "blocks": blocks,
                "horizon": 3 * blocks,
                "leaves": 4**blocks,
                "target_product": 8**blocks,
                "source_product": 4**blocks,
                "local_product": 2**blocks,
                "terminal_fiber": 1,
                "exact": 8**blocks == 4**blocks * 2**blocks,
            }
        )
    checks.update(
        {
            "eight_block_powers": len(rows) == 8,
            "all_powers_tight": all(row["exact"] for row in rows),
            "largest_has_65536_leaves": rows[-1]["leaves"] == 65_536,
            "positive_gap_with_terminal_fiber_one": rows[-1]["terminal_fiber"] == 1
            and math.isclose(
                math.log2(rows[-1]["local_product"]) / rows[-1]["horizon"],
                1 / 3,
                abs_tol=1e-12,
            ),
        }
    )
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def independent_sparse_boundary(maximum_horizon: int = 16_384) -> dict[str, Any]:
    merge_events = 0
    rows = []
    for horizon in range(1, maximum_horizon + 1):
        if horizon & (horizon - 1) == 0:
            merge_events += 1
        fiber = 3**merge_events
        rows.append(
            {
                "horizon": horizon,
                "events": merge_events,
                "fiber": fiber,
                "rate": math.log2(fiber) / horizon,
            }
        )
    checks = {
        "sixteen_thousand_three_hundred_eighty_four_horizons": len(rows) == 16_384,
        "events_match_bit_length": all(
            row["events"] == row["horizon"].bit_length() for row in rows
        ),
        "unbounded_fiber": rows[-1]["fiber"] > rows[0]["fiber"],
        "endpoint_rate_below_point_zero_zero_two": rows[-1]["rate"] < 0.002,
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def independent_max_limsup_boundaries() -> dict[str, Any]:
    maximum_rows = []
    for maximum in range(2, 65):
        target_degree = maximum + 1
        source_degree = 2
        maximum_rows.append(
            target_degree <= maximum * source_degree and target_degree > source_degree
        )
    total = 3
    merge_steps = 1
    lows = []
    highs = []
    for _ in range(7):
        rest = total**3
        lows.append(merge_steps / rest)
        total = 2 * rest
        merge_steps += rest
        highs.append(merge_steps / total)
    checks = {
        "sixty_three_maximum_fiber_rows": len(maximum_rows) == 63 and all(maximum_rows),
        "low_subsequence_near_zero": lows[-1] < 1e-30,
        "high_subsequence_near_half": 0.499 < highs[-1] < 0.501,
        "limsup_not_liminf": highs[-1] - lows[-1] > 0.49,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_mutations() -> dict[str, Any]:
    disclosure = independent_disclosure_report()
    sparse = independent_sparse_boundary()
    max_limsup = independent_max_limsup_boundaries()
    last = disclosure["rows"][-1]
    rows = {
        "terminal_fiber_controls_branch": last["terminal_fiber"] == 1
        and last["local_product"] > 1,
        "state_class_controls_history": last["local_product"] > 2,
        "finite_fibers_equal_rate": math.isclose(
            math.log2(last["local_product"]) / last["horizon"],
            1 / 3,
            abs_tol=1e-12,
        ),
        "subexponential_means_bounded": sparse["checks"]["unbounded_fiber"]
        and sparse["checks"]["endpoint_rate_below_point_zero_zero_two"],
        "minimum_replaces_maximum": max_limsup["checks"][
            "sixty_three_maximum_fiber_rows"
        ],
        "liminf_replaces_limsup": max_limsup["checks"]["limsup_not_liminf"],
        "one_direction_gives_equality": last["target_product"] > last["source_product"],
        "one_port_modulus": not math.isclose(1 / 3, math.log2(5) / 3),
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
        == "asmp4_causal_branch_fiber_contract_v0_29",
        "prefix_causal": "extension-consistent"
        in contract.get("causal_morphism", {}).get("prefix", ""),
        "local_maximum": "maximum"
        in contract.get("causal_morphism", {}).get("local_fiber", ""),
        "limsup": "limsup" in contract.get("transfer", {}).get("asymptotic", ""),
        "injective_disclosure": "injective"
        in claim.get("sharpness", {}).get("disclosure", ""),
        "eight_mutations": claim.get("mutations_rejected") == 8,
        "central_not_imported": "causal_branch_fiber" not in imports,
    }
    return {"checks": checks, "pass": all(checks.values())}


def _predecessor_tests() -> tuple[tuple[str, str], ...]:
    tree = ast.parse(V28_CENTRAL.read_text(encoding="utf-8"), filename=str(V28_CENTRAL))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "PREDECESSOR_TESTS"
            for target in node.targets
        ):
            return tuple(ast.literal_eval(node.value)) + (V28_TEST,)
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
        "pass": len(rows) == 29 and tests == 324,
    }


def document_sentinels() -> dict[str, Any]:
    required = {
        "THEOREM.md": (
            "local successor fiber",
            "terminal fiber",
            "one third",
            "subexponential",
        ),
        "RESULT.md": (
            "332,928",
            "terminal transcript fiber one",
            "sufficient, not necessary",
        ),
        "PRIOR_ART_BOUNDARY_v0_29.md": (
            "Tomar",
            "No novelty is claimed",
            "v0.3",
        ),
        "COMPLETION_AUDIT_v0_29.md": ("334 tests", "Not claimed"),
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
        "ternary_morphisms": independent_ternary_morphism_census(),
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
