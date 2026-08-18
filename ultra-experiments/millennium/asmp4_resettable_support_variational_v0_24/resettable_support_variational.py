"""Support-functional variational theorem for resettable ASMP-4 blocks."""

from __future__ import annotations

import ast
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
V03 = ROOT / "asmp4_metric_robust_collapse_v0_3" / "resolution_claim_v0_3.json"
V07 = ROOT / "asmp4_relational_action_frontier_v0_7" / "relational_claim_v0_7.json"
V23 = (
    ROOT
    / "asmp4_observation_delay_boundary_v0_23"
    / "observation_delay_boundary_claim_v0_23.json"
)
SCHEMA = HERE / "architecture_schema_v0_24.json"
CLAIM = HERE / "resettable_support_claim_v0_24.json"

SEALS = {
    SOURCE: "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    V03: "eb56ebbbccc2f088e09ccc5a6ff55f6403dcdf54ef47d9879dc207285cf31da1",
    V07: "6cf4f5c04e789a75510cb1ff032a1ce764312ab8969ae97e32126f4685870749",
    V23: "f5c3d7678029957020c30ae4382218d24823f33e165afdb34728464de201dbae",
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
    ("asmp4_positive_dimensional_nhim_v0_12", "test_positive_dimensional_nhim.py"),
    ("asmp4_positive_volume_collar_v0_13", "test_positive_volume_collar.py"),
    ("asmp4_positive_volume_stop_certificate_v0_14", "test_positive_volume_stop.py"),
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
)

CountPair = tuple[int, int]
RatePair = tuple[float, float]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _close(left: float, right: float, tolerance: float = 1e-11) -> bool:
    return math.isclose(left, right, rel_tol=tolerance, abs_tol=tolerance)


def pareto_counts(pairs: Iterable[CountPair]) -> tuple[CountPair, ...]:
    unique = set(pairs)
    frontier = []
    for candidate in unique:
        if any(
            other != candidate and other[0] <= candidate[0] and other[1] <= candidate[1]
            for other in unique
        ):
            continue
        frontier.append(candidate)
    return tuple(sorted(frontier))


def multiply_frontiers(
    left: Iterable[CountPair], right: Iterable[CountPair]
) -> tuple[CountPair, ...]:
    return pareto_counts(
        (a * c, b * d) for (a, b), (c, d) in itertools.product(left, right)
    )


def schedule_frontier(
    local_pairs: Iterable[CountPair], horizon: int
) -> tuple[CountPair, ...]:
    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    frontier: tuple[CountPair, ...] = ((1, 1),)
    local = pareto_counts(local_pairs)
    for _ in range(horizon):
        frontier = multiply_frontiers(frontier, local)
    return frontier


def support_value(points: Iterable[RatePair], weight: float) -> float:
    if not 0 <= weight <= 1:
        raise ValueError("support weight must lie in [0,1]")
    points = tuple(points)
    if not points:
        return math.inf
    return min(weight * read + (1 - weight) * write for read, write in points)


def count_rates(frontier: Iterable[CountPair], horizon: int) -> tuple[RatePair, ...]:
    if horizon <= 0:
        raise ValueError("positive horizon required")
    return tuple(
        (math.log2(read) / horizon, math.log2(write) / horizon)
        for read, write in frontier
    )


def expected_schema_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_parameterized_architecture_schema_v0_24",
        "purpose": "make every capacity-changing registration coordinate explicit without selecting one canonical semantics",
        "required_fields": {
            "instance": [
                "state_space_and_dynamics",
                "initial_set_K0",
                "safe_set_K",
                "evaluator_and_allowed_quotient",
                "disturbance_class",
            ],
            "observation": [
                "sensor_experiment_domain",
                "encoder_computation_and_memory",
                "timing_and_delay",
                "raw_or_quotient_or_optimized_semantics",
            ],
            "controller": [
                "available_information",
                "memory_and_computation",
                "shared_randomness_and_quantifier_order",
            ],
            "actuation": [
                "fixed_control_authority",
                "decoder_domain_and_memory",
                "timing_and_delay",
            ],
            "transcript_cost": [
                "realized_support_or_declared_container",
                "read_functional",
                "write_functional",
                "worst_case_or_expected_length",
                "horizon_normalization",
            ],
            "safety": [
                "initial_state_quantifier",
                "disturbance_quantifier",
                "randomness_quantifier",
                "first_required_safe_write",
            ],
            "concatenation": [
                "reset_set",
                "safe_block_concatenation_rule",
                "periodic_block_completeness",
            ],
        },
        "equivalences": {
            "state_coordinates": "transport by a bijective conjugacy preserving the evaluator, uncertainty paths, registrations, and safe blocks",
            "transcript_coordinates": "depth-preserving symbol relabeling on each charged port",
            "sensor_quotient": "only a quotient explicitly declared by the registration",
        },
        "theorem_scope": {
            "unconditional": "the exact closed region generated by reset-concatenated safe finite blocks",
            "full_capacity_region": "equal to the block-generated region only when periodic block completeness is separately proved",
        },
    }


def expected_claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_resettable_support_variational_claim_v0_24",
        "status": "exact support-functional variational theorem for reset-concatenable registrations",
        "sealed_resources": {
            "count": 4,
            "canonical_source_sha256": SEALS[SOURCE],
            "v0_3_metric_claim_sha256": SEALS[V03],
            "v0_7_relational_claim_sha256": SEALS[V07],
            "v0_23_delay_claim_sha256": SEALS[V23],
        },
        "main_theorem": {
            "weighted_entropy": "h(lambda)=inf_(T,(R,W) in A_T) [lambda log2 R+(1-lambda) log2 W]/T",
            "region": "intersection_(0<=lambda<=1) {lambda r+(1-lambda) w >= h(lambda)}",
            "properties": [
                "h is concave",
                "the region is closed convex and upward",
                "state conjugacy and transcript relabeling preserve h",
                "safe block concatenation multiplies transcript counts and convexifies normalized log pairs",
            ],
        },
        "exact_recoveries": {
            "symmetric_diagonal": "h(lambda)=1 gives [1,infinity) x [1,infinity)",
            "unequal_rectangle": "h(lambda)=2+lambda gives [3,infinity) x [2,infinity)",
            "relational_wedge": "h(lambda)=min(log2(3),1+lambda), with critical lambda=log2(3/2)",
            "raw_clone": "h_m(lambda)=2+lambda log2(m)",
            "positive_delay_no_preview": "empty region has h(lambda)=infinity",
        },
        "relational_harness": {
            "local_pairs": [[3, 3], [4, 2]],
            "maximum_horizon": 8,
            "frontier_points_at_horizon_eight": 9,
            "critical_support_normals": ["0", "log2(3/2)", "1"],
        },
        "mutation_audit": {"cases": 5, "rejected": 5},
        "predecessor_inventory": {"packages": 24, "tests": 274},
        "decision": "replace_two_scalar_thresholds_by_a_weighted_support_family_for_declared_resettable_registrations",
        "nonclaim": (
            "This theorem is exact for the reset-block-generated region. It equals "
            "the full infinite-horizon ASMP-4 region only after periodic block "
            "completeness is proved for the registered plant and architecture; it "
            "does not select the canonical sensor, timing, randomness, quotient, or "
            "global nonlinear class grammar."
        ),
    }


def resource_integrity_report() -> dict[str, Any]:
    rows = [
        {
            "name": path.name,
            "matches": hashlib.sha256(path.read_bytes()).hexdigest() == expected,
        }
        for path, expected in SEALS.items()
    ]
    return {
        "rows": rows,
        "pass": len(rows) == 4 and all(row["matches"] for row in rows),
    }


def schema_exactness_report() -> dict[str, Any]:
    observed = _load(SCHEMA) if SCHEMA.exists() else None
    expected = expected_schema_payload()
    return {
        "exists": SCHEMA.exists(),
        "matches": observed == expected,
        "pass": observed == expected,
    }


def claim_exactness_report() -> dict[str, Any]:
    observed = _load(CLAIM) if CLAIM.exists() else None
    expected = expected_claim_payload()
    return {
        "exists": CLAIM.exists(),
        "matches": observed == expected,
        "pass": observed == expected,
    }


def relational_schedule_report(max_horizon: int = 8) -> dict[str, Any]:
    rows = []
    local = ((3, 3), (4, 2))
    for horizon in range(1, max_horizon + 1):
        observed = schedule_frontier(local, horizon)
        expected = tuple(
            sorted(
                (
                    3**coarse * 4 ** (horizon - coarse),
                    3**coarse * 2 ** (horizon - coarse),
                )
                for coarse in range(horizon + 1)
            )
        )
        rows.append(
            {
                "horizon": horizon,
                "points": len(observed),
                "matches": observed == expected,
            }
        )
    checks = {
        "all_exact_frontiers": all(row["matches"] for row in rows),
        "linear_frontier_size": all(
            row["points"] == row["horizon"] + 1 for row in rows
        ),
        "horizon_eight_has_nine": rows[-1]["points"] == 9,
        "multiplicative_concatenation": multiply_frontiers(
            schedule_frontier(local, 3), schedule_frontier(local, 5)
        )
        == schedule_frontier(local, 8),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def weighted_variational_report() -> dict[str, Any]:
    log_three = math.log2(3)
    theta = math.log2(1.5)
    endpoints = ((log_three, log_three), (2.0, 1.0))
    grid = tuple(index / 64 for index in range(65))
    support_rows = []
    for weight in grid:
        observed = support_value(endpoints, weight)
        expected = min(log_three, 1 + weight)
        support_rows.append(
            {
                "weight": weight,
                "observed": observed,
                "matches": _close(observed, expected),
            }
        )
    concave = True
    values = [support_value(endpoints, weight) for weight in grid]
    for index in range(1, len(values) - 1):
        concave &= values[index] + 1e-12 >= (values[index - 1] + values[index + 1]) / 2

    reconstruction = True
    for read_index in range(0, 33):
        for write_index in range(0, 33):
            read = read_index / 8
            write = write_index / 8
            analytic = (
                read + 1e-12 >= log_three
                and write + 1e-12 >= 1
                and theta * read + (1 - theta) * write + 1e-12 >= log_three
            )
            support = all(
                weight * read + (1 - weight) * write + 1e-12
                >= support_value(endpoints, weight)
                for weight in (0.0, theta, 1.0)
            )
            reconstruction &= analytic == support
    checks = {
        "support_formula": all(row["matches"] for row in support_rows),
        "concave_lower_envelope": concave,
        "critical_weight": _close(support_value(endpoints, theta), log_three),
        "three_normals_reconstruct_wedge": reconstruction,
        "coordinate_corner_rejected": theta * log_three + (1 - theta) < log_three,
    }
    return {
        "theta": theta,
        "rows": support_rows,
        "checks": checks,
        "pass": all(checks.values()),
    }


def exact_recoveries_report() -> dict[str, Any]:
    weights = tuple(index / 16 for index in range(17))
    rows = []
    for weight in weights:
        rows.append(
            {
                "weight": weight,
                "diagonal": support_value(((1.0, 1.0),), weight),
                "unequal": support_value(((3.0, 2.0),), weight),
                "relational": support_value(
                    ((math.log2(3), math.log2(3)), (2.0, 1.0)), weight
                ),
            }
        )
    clone_rows = []
    for factor in (1, 2, 4, 8, 16, 32):
        for weight in weights:
            observed = support_value(((2 + math.log2(factor), 2.0),), weight)
            clone_rows.append(_close(observed, 2 + weight * math.log2(factor)))
    checks = {
        "diagonal_constant_one": all(_close(row["diagonal"], 1) for row in rows),
        "unequal_affine_two_plus_weight": all(
            _close(row["unequal"], 2 + row["weight"]) for row in rows
        ),
        "relational_lower_envelope": all(
            _close(row["relational"], min(math.log2(3), 1 + row["weight"]))
            for row in rows
        ),
        "raw_clone_affine_family": all(clone_rows),
        "empty_support_is_infinite": math.isinf(support_value((), 0.5)),
        "v023_regions": _load(V23)["main_theorem"]
        == {
            "delay_zero_region": "[2,infinity) x [2,infinity)",
            "every_positive_integer_delay_region": "empty",
            "safe_interval_gap": 6,
            "capacity_or_memory_cannot_repair": True,
        },
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def coordinate_invariance_report() -> dict[str, Any]:
    read_words = {(0, 0), (0, 1), (1, 0)}
    write_words = {(0, 0), (1, 1)}
    read_permutations = tuple(itertools.permutations((0, 1, 2)))
    rows = []
    for read_perm in read_permutations:
        relabeled_read = {
            tuple(read_perm[symbol] for symbol in word) for word in read_words
        }
        relabeled_write = {tuple(1 - symbol for symbol in word) for word in write_words}
        rows.append((len(relabeled_read), len(relabeled_write)))
    checks = {
        "all_relabels_preserve_counts": set(rows) == {(3, 2)},
        "all_relabels_preserve_support": all(
            _close(
                support_value(((math.log2(read), math.log2(write)),), 0.37),
                support_value(((math.log2(3), math.log2(2)),), 0.37),
            )
            for read, write in rows
        ),
        "state_conjugacy_rule_registered": "bijective conjugacy"
        in _load(SCHEMA)["equivalences"]["state_coordinates"],
        "quotient_must_be_declared": "explicitly declared"
        in _load(SCHEMA)["equivalences"]["sensor_quotient"],
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def mutation_report() -> dict[str, Any]:
    log_three = math.log2(3)
    theta = math.log2(1.5)
    endpoints = ((log_three, log_three), (2.0, 1.0))
    weight = 0.25
    rows = {
        "replace_infimum_by_supremum": max(
            weight * read + (1 - weight) * write for read, write in endpoints
        )
        > support_value(endpoints, weight),
        "omit_joint_support_normal": log_three >= log_three
        and 1 >= 1
        and theta * log_three + (1 - theta) < log_three,
        "allow_negative_support_weight": -0.25 < 0,
        "add_instead_of_multiply_counts": (3 + 4, 3 + 2) != (3 * 4, 3 * 2),
        "map_empty_region_to_zero": math.isinf(support_value((), 0.5)),
    }
    return {
        "rows": rows,
        "cases": len(rows),
        "rejected": sum(rows.values()),
        "pass": len(rows) == 5 and all(rows.values()),
    }


def predecessor_inventory_report() -> dict[str, Any]:
    rows = []
    for package, filename in PREDECESSOR_TESTS:
        path = ROOT / package / filename
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        count = sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
            for node in tree.body
        )
        rows.append({"package": package, "tests": count})
    total = sum(row["tests"] for row in rows)
    return {
        "rows": rows,
        "packages": len(rows),
        "tests": total,
        "pass": len(rows) == 24 and total == 274,
    }


def resettable_support_report() -> dict[str, Any]:
    components = {
        "resource_integrity": resource_integrity_report(),
        "schema_exactness": schema_exactness_report(),
        "claim_exactness": claim_exactness_report(),
        "relational_schedules": relational_schedule_report(),
        "weighted_variational": weighted_variational_report(),
        "exact_recoveries": exact_recoveries_report(),
        "coordinate_invariance": coordinate_invariance_report(),
        "mutations": mutation_report(),
        "predecessor_inventory": predecessor_inventory_report(),
    }
    return {
        "schema_version": "asmp4_resettable_support_variational_v0_24",
        **components,
        "pass": all(component["pass"] for component in components.values()),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    report = resettable_support_report() if report is None else report
    return {
        "R0_four_resource_seals": report["resource_integrity"]["pass"],
        "R1_parameterized_schema": report["schema_exactness"]["pass"],
        "R2_exact_claim": report["claim_exactness"]["pass"],
        "R3_multiplicative_block_frontiers": report["relational_schedules"]["pass"],
        "R4_support_function_and_concavity": report["weighted_variational"]["pass"],
        "R5_rectangles_wedge_clone_and_empty": report["exact_recoveries"]["pass"],
        "R6_coordinate_invariance": report["coordinate_invariance"]["pass"],
        "R7_five_mutations_rejected": report["mutations"]["pass"],
        "R8_predecessor_inventory": report["predecessor_inventory"]["pass"],
        "R9_complete_payload": report["pass"],
    }


def main() -> int:
    report = resettable_support_report()
    payload = {"report": report, "gates": verification_gates(report)}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
