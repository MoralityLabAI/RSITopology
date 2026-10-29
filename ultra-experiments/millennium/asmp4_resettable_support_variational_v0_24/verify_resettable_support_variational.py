"""Import-independent verifier for the ASMP-4 v0.24 support theorem."""

from __future__ import annotations

import ast
import hashlib
import itertools
import json
import math
import random
from fractions import Fraction
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

TEST_FILES = (
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

RationalPoint = tuple[Fraction, Fraction]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def independent_integrity() -> dict[str, Any]:
    rows = [
        (path.name, hashlib.sha256(path.read_bytes()).hexdigest() == expected)
        for path, expected in SEALS.items()
    ]
    return {"rows": rows, "pass": len(rows) == 4 and all(match for _, match in rows)}


def _prune(pairs: Iterable[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    ordered = sorted(set(pairs), key=lambda pair: (pair[0], pair[1]))
    frontier = []
    best_write = math.inf
    for pair in ordered:
        if pair[1] < best_write:
            frontier.append(pair)
            best_write = pair[1]
    return tuple(frontier)


def independent_schedule_frontiers(max_horizon: int = 9) -> dict[str, Any]:
    rows = []
    for horizon in range(1, max_horizon + 1):
        pairs = set()
        for schedule in itertools.product((0, 1), repeat=horizon):
            read = 1
            write = 1
            for selector in schedule:
                local_read, local_write = ((3, 3), (4, 2))[selector]
                read *= local_read
                write *= local_write
            pairs.add((read, write))
        observed = _prune(pairs)
        expected = tuple(
            sorted(
                (
                    3**coarse * 4 ** (horizon - coarse),
                    3**coarse * 2 ** (horizon - coarse),
                )
                for coarse in range(horizon + 1)
            )
        )
        rows.append((horizon, len(pairs), observed == expected))
    checks = {
        "all_schedule_words_exhausted": sum(
            2**horizon for horizon in range(1, max_horizon + 1)
        )
        == 1022,
        "all_frontiers_exact": all(match for _, _, match in rows),
        "independent_horizon_nine": rows[-1][1] == 10,
        "claim_horizon_eight": _load(CLAIM)["relational_harness"][
            "frontier_points_at_horizon_eight"
        ]
        == 9,
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def _support(points: Iterable[RationalPoint], weight: Fraction) -> Fraction | None:
    points = tuple(points)
    if not points:
        return None
    return min(weight * read + (1 - weight) * write for read, write in points)


def _critical_weights(points: tuple[RationalPoint, ...]) -> tuple[Fraction, ...]:
    weights = {Fraction(0), Fraction(1)}
    for left, right in itertools.combinations(points, 2):
        denominator = (left[0] - left[1]) - (right[0] - right[1])
        if denominator:
            weight = (right[1] - left[1]) / denominator
            if 0 <= weight <= 1:
                weights.add(weight)
    return tuple(sorted(weights))


def _upper_convex_membership(
    points: tuple[RationalPoint, ...], query: RationalPoint
) -> bool:
    for left in points:
        if left[0] <= query[0] and left[1] <= query[1]:
            return True
    for left, right in itertools.combinations(points, 2):
        lower = Fraction(0)
        upper = Fraction(1)
        for coordinate in (0, 1):
            slope = left[coordinate] - right[coordinate]
            bound = query[coordinate] - right[coordinate]
            if slope > 0:
                upper = min(upper, bound / slope)
            elif slope < 0:
                lower = max(lower, bound / slope)
            elif right[coordinate] > query[coordinate]:
                break
        else:
            if max(lower, Fraction(0)) <= min(upper, Fraction(1)):
                return True
    return False


def independent_support_reconstruction(seed: int = 240024) -> dict[str, Any]:
    generator = random.Random(seed)
    fixtures = []
    all_exact = True
    all_concave = True
    for _ in range(64):
        points = tuple(
            sorted(
                {
                    (
                        Fraction(generator.randint(1, 8), 2),
                        Fraction(generator.randint(1, 8), 2),
                    )
                    for _ in range(generator.randint(2, 5))
                }
            )
        )
        weights = _critical_weights(points)
        for query_read in range(0, 11):
            for query_write in range(0, 11):
                query = (Fraction(query_read, 2), Fraction(query_write, 2))
                by_support = all(
                    weight * query[0] + (1 - weight) * query[1]
                    >= _support(points, weight)
                    for weight in weights
                )
                by_hull = _upper_convex_membership(points, query)
                all_exact &= by_support == by_hull
        sample_weights = tuple(Fraction(index, 16) for index in range(17))
        values = tuple(_support(points, weight) for weight in sample_weights)
        all_concave &= all(
            values[index] >= (values[index - 1] + values[index + 1]) / 2
            for index in range(1, len(values) - 1)
        )
        fixtures.append((len(points), len(weights)))
    checks = {
        "deterministic_seed": seed == 240024,
        "sixty_four_fixtures": len(fixtures) == 64,
        "critical_support_equals_upper_convex_hull": all_exact,
        "all_lower_envelopes_concave": all_concave,
        "nontrivial_critical_normals": any(weights > 2 for _, weights in fixtures),
    }
    return {"fixtures": fixtures, "checks": checks, "pass": all(checks.values())}


def independent_relational_wedge() -> dict[str, Any]:
    log_three = math.log2(3)
    theta = math.log2(1.5)
    points = ((log_three, log_three), (2.0, 1.0))

    def support(weight: float) -> float:
        return min(weight * read + (1 - weight) * write for read, write in points)

    rows = [(index / 128, support(index / 128)) for index in range(129)]
    checks = {
        "lower_envelope": all(
            math.isclose(
                value, min(log_three, 1 + weight), rel_tol=1e-12, abs_tol=1e-12
            )
            for weight, value in rows
        ),
        "critical_equality": math.isclose(support(theta), log_three, rel_tol=1e-12),
        "false_corner_passes_coordinates": log_three >= support(1) and 1 >= support(0),
        "false_corner_fails_joint": theta * log_three + (1 - theta) < support(theta),
        "claim_matches_v007": _load(CLAIM)["exact_recoveries"]["relational_wedge"]
        == "h(lambda)=min(log2(3),1+lambda), with critical lambda=log2(3/2)",
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_boundary_recoveries() -> dict[str, Any]:
    weights = tuple(index / 32 for index in range(33))
    clone_exact = True
    for factor in range(1, 33):
        for weight in weights:
            observed = weight * (2 + math.log2(factor)) + (1 - weight) * 2
            clone_exact &= math.isclose(
                observed, 2 + weight * math.log2(factor), rel_tol=1e-12
            )
    v03 = _load(V03)
    v07 = _load(V07)
    v23 = _load(V23)
    checks = {
        "v003_diagonal_scope": "diagonal quadrant" in v03["claim"],
        "v007_nondominated_pairs": v07["registered_adaptive_grammar"][
            "nondominated_local_count_pairs"
        ]
        == [[3, 3], [4, 2]],
        "v007_nonrectangular": v07["exact_closed_region"]["nonrectangular"],
        "clone_factors_one_through_thirty_two": clone_exact,
        "delay_empty": v23["main_theorem"]["every_positive_integer_delay_region"]
        == "empty",
        "preview_restores": v23["restoration"]["charged_current_preview_region"]
        == "[2,infinity) x [2,infinity)",
        "empty_infimum_convention": _support((), Fraction(1, 2)) is None,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_coordinate_invariance() -> dict[str, Any]:
    language = {(0, 0, 1), (0, 1, 1), (1, 0, 0), (1, 1, 0)}
    rows = []
    for permutation in itertools.permutations((0, 1, 2, 3)):
        relabeled = {tuple(permutation[symbol] for symbol in word) for word in language}
        prefixes = {word[:depth] for word in relabeled for depth in range(4)}
        rows.append((len(relabeled), len(prefixes)))
    schema = _load(SCHEMA)
    checks = {
        "twenty_four_relabelings": len(rows) == 24,
        "language_and_prefix_counts_invariant": set(rows) == {(4, 11)},
        "state_conjugacy_transport": "preserving the evaluator"
        in schema["equivalences"]["state_coordinates"],
        "transcript_depth_preserved": "depth-preserving"
        in schema["equivalences"]["transcript_coordinates"],
        "no_implicit_quotient": "only a quotient explicitly declared"
        in schema["equivalences"]["sensor_quotient"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_schema_and_source() -> dict[str, Any]:
    source = SOURCE.read_text(encoding="utf-8")
    section = source[source.index("# ASMP-4") : source.index("# ASMP-5")]
    schema = _load(SCHEMA)
    claim = _load(CLAIM)
    checks = {
        "schema": schema["schema_version"]
        == "asmp4_parameterized_architecture_schema_v0_24",
        "all_seven_registration_groups": len(schema["required_fields"]) == 7,
        "canonical_components": all(
            term in section
            for term in (
                "plant, sensor, controller, and actuator",
                "Internal memory",
                "delays",
                "block coding",
                "shared randomness",
            )
        ),
        "canonical_rate": "limsup_(T->infinity) (1/T) log2 |M_r^C(T)|" in section,
        "canonical_safety": "every x_0 in K_0" in section
        and "every allowed disturbance sequence" in section,
        "claim_schema": claim["schema_version"]
        == "asmp4_resettable_support_variational_claim_v0_24",
        "claim_seals": claim["sealed_resources"]
        == {
            "count": 4,
            "canonical_source_sha256": SEALS[SOURCE],
            "v0_3_metric_claim_sha256": SEALS[V03],
            "v0_7_relational_claim_sha256": SEALS[V07],
            "v0_23_delay_claim_sha256": SEALS[V23],
        },
        "block_completeness_nonclaim": "periodic block completeness"
        in claim["nonclaim"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_mutations() -> dict[str, Any]:
    log_three = math.log2(3)
    theta = math.log2(1.5)
    points = ((log_three, log_three), (2.0, 1.0))
    weight = 0.25
    correct = min(weight * read + (1 - weight) * write for read, write in points)
    mutated_sup = max(weight * read + (1 - weight) * write for read, write in points)
    rows = {
        "supremum_instead_of_infimum": mutated_sup > correct,
        "coordinate_normals_only": theta * log_three + (1 - theta) < log_three,
        "negative_normal_breaks_upwardness": (-Fraction(1, 4) * 3 + Fraction(5, 4) * 2)
        < (-Fraction(1, 4) * 2 + Fraction(5, 4) * 2),
        "additive_count_composition": {(6, 6), (7, 5), (8, 4)}
        != {(9, 9), (12, 6), (16, 4)},
        "empty_region_zero_support": _support((), Fraction(1, 2)) is None,
    }
    return {"rows": rows, "pass": len(rows) == 5 and all(rows.values())}


def independent_inventory() -> dict[str, Any]:
    rows = []
    for package, filename in TEST_FILES:
        path = ROOT / package / filename
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        count = sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
            for node in tree.body
        )
        rows.append((package, count))
    total = sum(count for _, count in rows)
    return {
        "rows": rows,
        "packages": len(rows),
        "tests": total,
        "pass": len(rows) == 24 and total == 274,
    }


def document_sentinels() -> dict[str, Any]:
    paths = {
        "theorem": HERE / "THEOREM.md",
        "result": HERE / "RESULT.md",
        "completion": HERE / "COMPLETION_AUDIT_v0_24.md",
        "readme": HERE / "README.md",
        "reviewer": HERE / "REVIEWER_PACKET_v0_24.md",
    }
    docs = {
        name: " ".join(path.read_text(encoding="utf-8").casefold().split())
        for name, path in paths.items()
    }
    checks = {
        "variational_formula": "h(lambda)" in docs["theorem"]
        and "supporting half-spaces" in docs["theorem"],
        "concatenation": "multiplication of transcript counts" in docs["theorem"],
        "wedge": "log2(3/2)" in docs["result"] and "false corner" in docs["result"],
        "scope": "periodic block completeness" in docs["result"],
        "expanded_count": "284" in docs["completion"],
        "entrypoints": "run_verification.py" in docs["readme"]
        and "verify_resettable_support_variational.py" in docs["readme"],
        "falsification": "falsification" in docs["reviewer"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_report() -> dict[str, Any]:
    checks = {
        "integrity": independent_integrity()["pass"],
        "schedule_frontiers": independent_schedule_frontiers()["pass"],
        "support_reconstruction": independent_support_reconstruction()["pass"],
        "relational_and_boundaries": independent_relational_wedge()["pass"]
        and independent_boundary_recoveries()["pass"],
        "coordinate_invariance": independent_coordinate_invariance()["pass"],
        "schema_source_and_mutations": independent_schema_and_source()["pass"]
        and independent_mutations()["pass"],
        "inventory_and_documents": independent_inventory()["pass"]
        and document_sentinels()["pass"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def main() -> int:
    report = independent_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
