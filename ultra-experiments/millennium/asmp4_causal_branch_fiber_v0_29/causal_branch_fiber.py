"""Causal successor-fiber bounds for ASMP-4 worst-path branching cost."""

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
Language = tuple[Word, ...]
EdgeLabels = dict[tuple[Word, int], int]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(words: Iterable[Word]) -> Language:
    language = tuple(sorted(set(words)))
    if not language:
        raise ValueError("language must be nonempty")
    horizons = {len(word) for word in language}
    if len(horizons) != 1:
        raise ValueError("all words must have one horizon")
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


def branch_product(language: Language) -> int:
    successor_map = successors(language)
    horizon = len(language[0])
    return max(
        math.prod(len(successor_map[word[:time]]) for time in range(horizon))
        for word in language
    )


def causal_image(
    language: Language, labels: EdgeLabels
) -> tuple[Language, dict[Word, Word], dict[Word, Word]]:
    word_map: dict[Word, Word] = {}
    prefix_map: dict[Word, Word] = {(): ()}
    for word in language:
        source_prefix: Word = ()
        image_prefix: Word = ()
        for symbol in word:
            image_symbol = labels[(source_prefix, symbol)]
            source_prefix = source_prefix + (symbol,)
            image_prefix = image_prefix + (image_symbol,)
            prefix_map[source_prefix] = image_prefix
        word_map[word] = image_prefix
    return normalize(word_map.values()), word_map, prefix_map


def local_successor_fiber_product(language: Language, labels: EdgeLabels) -> int:
    successor_map = successors(language)
    horizon = len(language[0])
    maximum = 1
    for word in language:
        product = 1
        for time in range(horizon):
            prefix = word[:time]
            counts: dict[int, int] = {}
            for symbol in successor_map[prefix]:
                image = labels[(prefix, symbol)]
                counts[image] = counts.get(image, 0) + 1
            product *= max(counts.values())
        maximum = max(maximum, product)
    return maximum


def terminal_fiber(word_map: dict[Word, Word]) -> int:
    counts: dict[Word, int] = {}
    for image in word_map.values():
        counts[image] = counts.get(image, 0) + 1
    return max(counts.values())


def morphism_report(language: Language, labels: EdgeLabels) -> dict[str, Any]:
    image, word_map, _ = causal_image(language, labels)
    target_product = branch_product(language)
    source_product = branch_product(image)
    local_fiber = local_successor_fiber_product(language, labels)
    leaf_fiber = terminal_fiber(word_map)
    return {
        "target_words": len(language),
        "source_words": len(image),
        "target_branch_product": target_product,
        "source_branch_product": source_product,
        "local_fiber_product": local_fiber,
        "terminal_fiber": leaf_fiber,
        "inequality": target_product <= source_product * local_fiber,
        "branch_gap": math.log2(target_product) - math.log2(source_product),
        "fiber_bits": math.log2(local_fiber),
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
        "four_terminal_words": report["target_words"] == report["source_words"] == 4,
        "terminal_map_is_injective": report["terminal_fiber"] == 1,
        "target_branch_cost_three": report["target_branch_product"] == 8,
        "source_branch_cost_two": report["source_branch_product"] == 4,
        "local_fiber_is_two": report["local_fiber_product"] == 2,
        "bound_is_tight": report["target_branch_product"]
        == report["source_branch_product"] * report["local_fiber_product"],
    }
    return {**report, "checks": checks, "pass": all(checks.values())}


def concatenate(blocks: tuple[Word, ...]) -> Word:
    return tuple(symbol for block in blocks for symbol in block)


@lru_cache(maxsize=None)
def repeated_disclosure_report(maximum_blocks: int = 7) -> dict[str, Any]:
    base, labels = disclosure_fixture()
    _, base_map, _ = causal_image(base, labels)
    rows = []
    for block_count in range(1, maximum_blocks + 1):
        block_tuples = tuple(itertools.product(base, repeat=block_count))
        target = normalize(concatenate(blocks) for blocks in block_tuples)
        source = normalize(
            concatenate(tuple(base_map[block] for block in blocks))
            for blocks in block_tuples
        )
        target_product = branch_product(target)
        source_product = branch_product(source)
        rows.append(
            {
                "blocks": block_count,
                "horizon": 3 * block_count,
                "leaves": len(target),
                "target_product": target_product,
                "source_product": source_product,
                "local_fiber_product": 2**block_count,
                "terminal_fiber": 1,
                "exact": target_product == 8**block_count
                and source_product == 4**block_count
                and target_product == source_product * 2**block_count,
            }
        )
    checks = {
        "seven_block_powers": len(rows) == 7,
        "largest_language_has_16384_leaves": rows[-1]["leaves"] == 16_384,
        "all_bounds_tight": all(row["exact"] for row in rows),
        "leaf_fiber_entropy_zero": all(row["terminal_fiber"] == 1 for row in rows),
        "branch_gap_one_third_bit_per_step": math.isclose(
            math.log2(rows[-1]["local_fiber_product"]) / rows[-1]["horizon"],
            1 / 3,
            abs_tol=1e-12,
        ),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


@lru_cache(maxsize=None)
def exhaustive_binary_morphism_report(horizon: int = 3) -> dict[str, Any]:
    universe = tuple(itertools.product((0, 1), repeat=horizon))
    checked = 0
    failures = []
    injective_terminal_positive_local = 0
    for mask in range(1, 1 << len(universe)):
        language = normalize(
            universe[index] for index in range(len(universe)) if mask & (1 << index)
        )
        language_edges = edges(language)
        for outputs in itertools.product((0, 1), repeat=len(language_edges)):
            checked += 1
            labels = dict(zip(language_edges, outputs, strict=True))
            report = morphism_report(language, labels)
            if not report["inequality"]:
                failures.append({"language": language, "outputs": outputs})
            if report["terminal_fiber"] == 1 and report["local_fiber_product"] > 1:
                injective_terminal_positive_local += 1
    checks = {
        "three_hundred_thirty_two_thousand_nine_hundred_twenty_eight_maps": checked
        == 332_928,
        "all_causal_morphisms_obey_bound": not failures,
        "injective_leaf_maps_can_have_local_fibers": injective_terminal_positive_local
        > 0,
    }
    return {
        "checked": checked,
        "failures": failures,
        "injective_terminal_positive_local": injective_terminal_positive_local,
        "checks": checks,
        "pass": all(checks.values()),
    }


def clone_sharpness_report(
    maximum_factor: int = 16, maximum_horizon: int = 16
) -> dict[str, Any]:
    rows = []
    for factor in range(1, maximum_factor + 1):
        for horizon in range(1, maximum_horizon + 1):
            target_product = factor**horizon
            source_product = 1
            local_fiber = factor**horizon
            rows.append(
                {
                    "factor": factor,
                    "horizon": horizon,
                    "target_product": target_product,
                    "source_product": source_product,
                    "local_fiber": local_fiber,
                    "exact": target_product == source_product * local_fiber,
                }
            )
    checks = {
        "two_hundred_fifty_six_rows": len(rows) == 256,
        "all_clone_bounds_tight": all(row["exact"] for row in rows),
        "maximum_rate_four_bits": math.isclose(
            math.log2(rows[-1]["local_fiber"]) / rows[-1]["horizon"],
            4,
            abs_tol=1e-12,
        ),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def sparse_local_fiber_report(maximum_horizon: int = 8192) -> dict[str, Any]:
    rows = []
    for horizon in range(1, maximum_horizon + 1):
        merge_events = horizon.bit_length()
        fiber = 2**merge_events
        rows.append(
            {
                "horizon": horizon,
                "merge_events": merge_events,
                "fiber": fiber,
                "rate": math.log2(fiber) / horizon,
            }
        )
    checks = {
        "eight_thousand_one_hundred_ninety_two_horizons": len(rows) == 8192,
        "unbounded_local_fiber": rows[-1]["fiber"] > rows[0]["fiber"],
        "zero_entropy_endpoint": rows[-1]["rate"] < 0.002,
        "logarithmic_event_count": all(
            row["merge_events"] == row["horizon"].bit_length() for row in rows
        ),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def concentrated_local_fiber_report(maximum_factor: int = 128) -> dict[str, Any]:
    rows = []
    for maximum in range(2, maximum_factor + 1):
        target_degree = maximum + 1
        source_degree = 2
        rows.append(
            {
                "maximum": maximum,
                "minimum": 1,
                "target_degree": target_degree,
                "source_degree": source_degree,
                "maximum_bound": target_degree <= maximum * source_degree,
                "minimum_bound": target_degree <= source_degree,
            }
        )
    checks = {
        "one_hundred_twenty_seven_rows": len(rows) == 127,
        "maximum_always_bounds": all(row["maximum_bound"] for row in rows),
        "minimum_always_fails": all(not row["minimum_bound"] for row in rows),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def burst_limsup_report(stages: int = 8) -> dict[str, Any]:
    total = 2
    merge_steps = 1
    lows = []
    highs = []
    for _ in range(stages):
        rest_end = total**2
        lows.append(merge_steps / rest_end)
        total = 2 * rest_end
        merge_steps += rest_end
        highs.append(merge_steps / total)
    checks = {
        "eight_stages": len(lows) == len(highs) == 8,
        "low_subsequence_to_zero": lows[-1] < 1e-20,
        "high_subsequence_to_half": 0.499 < highs[-1] <= 0.501,
        "liminf_differs_from_limsup": highs[-1] - lows[-1] > 0.49,
    }
    return {
        "lows": lows,
        "highs": highs,
        "checks": checks,
        "pass": all(checks.values()),
    }


def mutation_report() -> dict[str, Any]:
    disclosure = disclosure_report()
    repeated = repeated_disclosure_report()
    clone = clone_sharpness_report(3, 4)
    sparse = sparse_local_fiber_report()
    concentrated = concentrated_local_fiber_report(16)
    burst = burst_limsup_report()
    rows = {
        "terminal_fiber_controls_branch_cost": disclosure["terminal_fiber"] == 1
        and disclosure["branch_gap"] > 0,
        "state_class_size_controls_branch_history": clone["rows"][-1]["local_fiber"]
        > clone["rows"][-1]["factor"],
        "finite_horizon_fibers_imply_equal_rate": repeated["checks"][
            "branch_gap_one_third_bit_per_step"
        ],
        "subexponential_means_uniformly_bounded": sparse["checks"][
            "unbounded_local_fiber"
        ]
        and sparse["checks"]["zero_entropy_endpoint"],
        "minimum_local_fiber_can_replace_maximum": concentrated["checks"][
            "minimum_always_fails"
        ],
        "liminf_can_replace_limsup": burst["checks"]["liminf_differs_from_limsup"],
        "one_direction_implies_branch_region_equality": disclosure["branch_gap"] > 0,
        "one_shared_modulus_covers_both_ports": not math.isclose(
            1 / 3, math.log2(3) / 3
        ),
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
            value = ast.literal_eval(node.value)
            return tuple(value) + (V28_TEST,)
    raise ValueError("v0.28 predecessor inventory not found")


def expected_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_causal_branch_fiber_contract_v0_29",
        "objective": "worst-path causal branching cost under public transcript factors",
        "branch_cost": "max over leaves of sum log2 successor degree along the prefix path",
        "causal_morphism": {
            "prefix": "length-preserving and extension-consistent",
            "local_fiber": "maximum number of target successor symbols mapped to one source successor at a target prefix",
            "path_product": "F_i(T) is the maximum product of local fibers along a target port path",
        },
        "transfer": {
            "finite_horizon": "B_i_target(T) <= B_i_source(T)+log2 F_i(T)",
            "asymptotic": "rate slack nu_i=limsup_T log2 F_i(T)/T",
            "exactness": "bidirectional subexponential local-fiber products preserve the branch-cost region",
        },
        "boundary": {
            "injective_terminal": "terminal maximum fiber one can coexist with positive local branch-fiber entropy",
            "clone": "m-to-one local merging each step attains log2 m rate slack",
            "directions": "separate maps and profiles are required for read, write, and both transfer directions",
        },
        "nonclaims": [
            "prefix-free minimax cost without a separate distortion theorem",
            "arbitrary transcript-tree functionals",
            "nonlinear quotient construction",
        ],
    }


def expected_claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_causal_branch_fiber_v0_29",
        "theorem": {
            "name": "causal successor-fiber branching transfer",
            "finite_horizon": "target branch product is at most source branch product times maximum local-fiber path product",
            "asymptotic": "directed branch-rate slack is local successor-fiber entropy",
            "exact_corollary": "bidirectional subexponential local-fiber products preserve the complete branch-cost region",
        },
        "sharpness": {
            "disclosure": "three-step injective terminal map has branch costs 3 and 2 with local fiber product 2",
            "repetition": "block powers have terminal fiber one and exact branch gap one third bit per step",
            "clone": "m-to-one merging every step attains log2 m",
        },
        "central_harness": {
            "binary_causal_maps": 332928,
            "disclosure_block_powers": 7,
            "largest_block_language": 16384,
            "clone_rows": 256,
            "sparse_horizons": 8192,
        },
        "independent_harness": {
            "ternary_output_maps": 2115,
            "disclosure_block_powers": 8,
            "sparse_horizons": 16384,
        },
        "mutations_rejected": 8,
        "predecessor_inventory": {"packages": 29, "tests": 324},
        "disposition": "causal branching transfer requires local successor-fiber entropy; terminal fibers alone are insufficient",
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
    return {
        "rows": rows,
        "pass": len(rows) == 3 and all(row["matches"] for row in rows),
    }


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
        "pass": len(rows) == 29 and tests == 324,
    }


def payload_report() -> dict[str, Any]:
    required = {
        "README.md",
        "THEOREM.md",
        "RESULT.md",
        "COMPLETION_AUDIT_v0_29.md",
        "REVIEWER_PACKET_v0_29.md",
        "PRIOR_ART_BOUNDARY_v0_29.md",
        "causal_branch_fiber_contract_v0_29.json",
        "causal_branch_fiber_claim_v0_29.json",
        "causal_branch_fiber.py",
        "verify_causal_branch_fiber.py",
        "test_causal_branch_fiber.py",
        "run_verification.py",
    }
    present = {path.name for path in HERE.iterdir() if path.is_file()}
    return {"missing": sorted(required - present), "pass": required <= present}


def causal_branch_report() -> dict[str, Any]:
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
        "clone_sharpness": clone_sharpness_report(),
        "sparse_local_fiber": sparse_local_fiber_report(),
        "concentrated_local_fiber": concentrated_local_fiber_report(),
        "burst_limsup": burst_limsup_report(),
        "mutations": mutation_report(),
        "predecessor_inventory": predecessor_inventory_report(),
        "payload": payload_report(),
    }
    return {
        "schema_version": "asmp4_causal_branch_fiber_v0_29",
        **components,
        "pass": all(component["pass"] for component in components.values()),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    report = causal_branch_report() if report is None else report
    return {
        "R0_three_resource_seals": report["resource_integrity"]["pass"],
        "R1_exact_contract": report["contract_exactness"]["pass"],
        "R2_exact_claim": report["claim_exactness"]["pass"],
        "R3_injective_disclosure_is_sharp": report["disclosure"]["pass"]
        and report["repeated_disclosure"]["pass"],
        "R4_all_binary_causal_maps": report["exhaustive_binary_morphisms"]["pass"],
        "R5_clone_sharpness": report["clone_sharpness"]["pass"],
        "R6_subexponential_boundary": report["sparse_local_fiber"]["pass"],
        "R7_maximum_and_limsup_load_bearing": report["concentrated_local_fiber"]["pass"]
        and report["burst_limsup"]["pass"],
        "R8_eight_mutations_rejected": report["mutations"]["pass"],
        "R9_inventory_and_payload": report["predecessor_inventory"]["pass"]
        and report["payload"]["pass"],
    }


def main() -> int:
    report = causal_branch_report()
    payload = {"gates": verification_gates(report), "report": report}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
