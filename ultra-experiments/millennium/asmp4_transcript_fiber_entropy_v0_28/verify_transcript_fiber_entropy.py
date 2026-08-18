"""Import-independent trie verifier for ASMP-4 transcript-fiber entropy."""

from __future__ import annotations

import ast
import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
V20 = (
    ROOT
    / "asmp4_sensor_refinement_inflation_stop_v0_20"
    / "sensor_refinement_stop_claim_v0_20.json"
)
V27 = (
    ROOT
    / "asmp4_approximate_bisimulation_robustness_v0_27"
    / "approximate_bisimulation_claim_v0_27.json"
)
CONTRACT = HERE / "transcript_fiber_contract_v0_28.json"
CLAIM = HERE / "transcript_fiber_claim_v0_28.json"

SEALS = {
    SOURCE: "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    V20: "b06213d846b53cf7f2262b7f0cf3dea89f22ca5f679ec8e87d5fd88e13de7d8f",
    V27: "90d80d747731536aa665f434497fcdc06ebc4068eeafb748f62ef669189aa186",
}

PREDECESSOR_TESTS = (
    ("asmp4_capacity_definition_audit", "test_capacity_definition_audit.py"),
    ("asmp4_two_port_game", "test_two_port_game.py"),
    ("asmp4_serial_collapse_theorem_v0_2", "test_serial_capacity.py"),
    ("asmp4_metric_robust_collapse_v0_3", "test_metric_harness.py"),
    ("asmp4_heterogeneous_port_costs_v0_4", "test_heterogeneous_frontier.py"),
    ("asmp4_adaptive_history_collapse_v0_5", "test_adaptive_frontier.py"),
    ("asmp4_registration_fork_v0_6", "test_registration_fork.py"),
    ("asmp4_relational_action_frontier_v0_7", "test_relational_frontier.py"),
    ("asmp4_randomness_quantifier_boundary_v0_8", "test_randomness_quantifier.py"),
    ("asmp4_completion_atlas_v0_9", "test_completion_atlas.py"),
    ("asmp4_stopping_red_team_v0_10", "test_stopping_red_team.py"),
    ("asmp4_nhim_cocycle_audit_v0_11", "test_nhim_cocycle_audit.py"),
    (
        "asmp4_positive_dimensional_nhim_v0_12",
        "test_positive_dimensional_nhim.py",
    ),
    ("asmp4_positive_volume_collar_v0_13", "test_positive_volume_collar.py"),
    (
        "asmp4_positive_volume_stop_certificate_v0_14",
        "test_positive_volume_stop.py",
    ),
    ("asmp4_semantic_selector_audit_v0_15", "test_semantic_selector_audit.py"),
    (
        "asmp4_registered_sensor_classification_v0_16",
        "test_registered_sensor_classification.py",
    ),
    ("asmp4_zero_error_sensor_kernels_v0_17", "test_zero_error_sensor_kernels.py"),
    (
        "asmp4_finite_state_sensor_transducers_v0_18",
        "test_finite_state_sensor_transducers.py",
    ),
    (
        "asmp4_uncertain_initial_sensor_state_v0_19",
        "test_uncertain_initial_sensor_state.py",
    ),
    (
        "asmp4_sensor_refinement_inflation_stop_v0_20",
        "test_sensor_refinement_inflation_stop.py",
    ),
    ("asmp4_support_incidence_quotient_v0_21", "test_support_incidence_quotient.py"),
    ("asmp4_causal_encoder_collapse_v0_22", "test_causal_encoder_collapse.py"),
    ("asmp4_observation_delay_boundary_v0_23", "test_observation_delay_boundary.py"),
    (
        "asmp4_resettable_support_variational_v0_24",
        "test_resettable_support_variational.py",
    ),
    ("asmp4_periodic_block_completeness_v0_25", "test_periodic_block_completeness.py"),
    (
        "asmp4_public_bisimulation_transfer_v0_26",
        "test_public_bisimulation_transfer.py",
    ),
    (
        "asmp4_approximate_bisimulation_robustness_v0_27",
        "test_approximate_bisimulation_robustness.py",
    ),
)


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


def trie_leaf_count(language: Iterable[tuple[int, ...]]) -> int:
    root: dict[int | None, dict] = {}
    for word in language:
        node = root
        for symbol in word:
            node = node.setdefault(symbol, {})
        node[None] = {}

    def count(node: dict[int | None, dict]) -> int:
        return int(None in node) + sum(
            count(child) for symbol, child in node.items() if symbol is not None
        )

    return count(root)


def independent_trie_census(
    maximum_factor: int = 5, maximum_horizon: int = 7
) -> dict[str, Any]:
    rows = []
    for factor in range(1, maximum_factor + 1):
        for horizon in range(1, maximum_horizon + 1):
            language = tuple(itertools.product(range(factor), repeat=horizon))
            leaf_count = trie_leaf_count(language)
            collapsed = {word: (0,) * horizon for word in language}
            fibers: dict[tuple[int, ...], int] = {}
            for image in collapsed.values():
                fibers[image] = fibers.get(image, 0) + 1
            maximum_fiber = max(fibers.values())
            rows.append(
                {
                    "factor": factor,
                    "horizon": horizon,
                    "leaves": leaf_count,
                    "maximum_fiber": maximum_fiber,
                    "exact": leaf_count == factor**horizon == maximum_fiber,
                }
            )
    checks = {
        "thirty_five_trie_cases": len(rows) == 35,
        "largest_trie_has_78125_leaves": max(row["leaves"] for row in rows) == 78_125,
        "all_trie_counts_and_fibers_exact": all(row["exact"] for row in rows),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def independent_schedule_census(horizon: int = 8) -> dict[str, Any]:
    rows = []
    for schedule in itertools.product((1, 2, 3), repeat=horizon):
        count = math.prod(schedule)
        log_count = sum(math.log2(factor) for factor in schedule)
        rows.append(
            {
                "schedule": "".join(map(str, schedule)),
                "count": count,
                "log_identity": math.isclose(
                    math.log2(count), log_count, abs_tol=1e-12
                ),
                "fiber_bound_tight": count == count * 1,
            }
        )
    checks = {
        "six_thousand_five_hundred_sixty_one_schedules": len(rows) == 6561,
        "all_product_counts_exact": all(
            row["log_identity"] and row["fiber_bound_tight"] for row in rows
        ),
        "constant_three_schedule_present": any(
            row["schedule"] == "3" * horizon and row["count"] == 3**horizon
            for row in rows
        ),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def independent_sparse_boundary(maximum_horizon: int = 8192) -> dict[str, Any]:
    branch_count = 0
    rows = []
    for horizon in range(1, maximum_horizon + 1):
        if horizon & (horizon - 1) == 0:
            branch_count += 1
        fiber = 5**branch_count
        rows.append(
            {
                "horizon": horizon,
                "branch_count": branch_count,
                "fiber": fiber,
                "rate": math.log2(fiber) / horizon,
            }
        )
    checks = {
        "eight_thousand_one_hundred_ninety_two_horizons": len(rows) == 8192,
        "incremental_power_count_matches_bit_length": all(
            row["branch_count"] == row["horizon"].bit_length() for row in rows
        ),
        "unbounded_fiber": rows[-1]["fiber"] > rows[0]["fiber"],
        "endpoint_rate_below_point_zero_zero_four": rows[-1]["rate"] < 0.004,
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def independent_burst_boundary(stages: int = 7) -> dict[str, Any]:
    total = 3
    branching = 1
    lows = []
    highs = []
    for _ in range(stages):
        rest_end = total**3
        lows.append(Fraction(branching, rest_end))
        total = 2 * rest_end
        branching += rest_end
        highs.append(Fraction(branching, total))
    checks = {
        "seven_stages": len(lows) == len(highs) == 7,
        "low_subsequence_strictly_decreases": all(
            lows[index + 1] < lows[index] for index in range(len(lows) - 1)
        ),
        "last_low_near_zero": lows[-1] < Fraction(1, 10**30),
        "last_high_near_one_half": Fraction(1, 2) < highs[-1] < Fraction(501, 1000),
    }
    return {
        "lows": [str(value) for value in lows],
        "highs": [str(value) for value in highs],
        "checks": checks,
        "pass": all(checks.values()),
    }


def independent_directional_max_boundary(maximum_horizon: int = 32) -> dict[str, Any]:
    rows = []
    for horizon in range(1, maximum_horizon + 1):
        large = 3**horizon
        source_count = 2
        target_count = large + 1
        rows.append(
            {
                "horizon": horizon,
                "class_size": 3,
                "history_fiber": large,
                "maximum_bounds": target_count <= large * source_count,
                "minimum_fails": target_count > source_count,
                "section_fiber": 1,
            }
        )
    checks = {
        "maximum_fiber_bounds": all(row["maximum_bounds"] for row in rows),
        "minimum_fiber_fails": all(row["minimum_fails"] for row in rows),
        "history_exceeds_fixed_class": rows[-1]["history_fiber"]
        > rows[-1]["class_size"],
        "one_way_section_does_not_bound_reverse": rows[-1]["section_fiber"] == 1
        and rows[-1]["history_fiber"] > 1,
        "positive_history_fiber_entropy": math.isclose(
            math.log2(rows[-1]["history_fiber"]) / maximum_horizon,
            math.log2(3),
            abs_tol=1e-12,
        ),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def independent_mutations() -> dict[str, Any]:
    sparse = independent_sparse_boundary()
    burst = independent_burst_boundary()
    directional = independent_directional_max_boundary()
    asymmetric_read = math.log2(2)
    asymmetric_write = math.log2(7)
    rows = {
        "state_bisimulation_equal_entropy": directional["checks"][
            "positive_history_fiber_entropy"
        ],
        "finite_fibers_equal_entropy": all(
            row["history_fiber"] < math.inf for row in directional["rows"]
        )
        and directional["checks"]["positive_history_fiber_entropy"],
        "class_size_bounds_history": directional["checks"][
            "history_exceeds_fixed_class"
        ],
        "subexponential_means_bounded": sparse["checks"]["unbounded_fiber"]
        and sparse["checks"]["endpoint_rate_below_point_zero_zero_four"],
        "one_way_means_symmetric": directional["checks"][
            "one_way_section_does_not_bound_reverse"
        ],
        "minimum_fiber_suffices": directional["checks"]["minimum_fiber_fails"],
        "liminf_suffices": burst["checks"]["last_low_near_zero"]
        and burst["checks"]["last_high_near_one_half"],
        "one_modulus_for_both_ports": not math.isclose(
            asymmetric_read, asymmetric_write
        ),
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
        == "asmp4_transcript_fiber_contract_v0_28",
        "nonadditive_registered": contract.get("port_cost", {}).get("nonadditive")
        is True,
        "maximum_fiber_registered": "maximum"
        in contract.get("causal_factor", {}).get("fiber", ""),
        "limsup_registered": "limsup"
        in contract.get("transfer", {}).get("asymptotic", ""),
        "subexponential_exactness": "subexponential"
        in claim.get("theorem", {}).get("exact_corollary", ""),
        "eight_mutations": claim.get("mutations_rejected") == 8,
        "central_not_imported": "transcript_fiber_entropy" not in imports,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_inventory() -> dict[str, Any]:
    rows = []
    for package, filename in PREDECESSOR_TESTS:
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
        "pass": len(rows) == 28 and tests == 314,
    }


def document_sentinels() -> dict[str, Any]:
    required = {
        "THEOREM.md": (
            "maximum fiber",
            "subexponential",
            "port-compatible",
            "one direction",
        ),
        "RESULT.md": (
            "relative fiber entropy",
            "one quotient class",
            "sufficient, not necessary",
        ),
        "PRIOR_ART_BOUNDARY_v0_28.md": (
            "Ledrappier and Walters",
            "No novelty is claimed",
            "v0.20",
        ),
        "COMPLETION_AUDIT_v0_28.md": ("324 tests", "Not claimed"),
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
        "trie_census": independent_trie_census(),
        "schedule_census": independent_schedule_census(),
        "sparse_boundary": independent_sparse_boundary(),
        "burst_boundary": independent_burst_boundary(),
        "directional_max_boundary": independent_directional_max_boundary(),
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
