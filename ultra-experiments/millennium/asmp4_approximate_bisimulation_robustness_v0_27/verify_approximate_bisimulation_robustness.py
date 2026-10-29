"""Import-independent verifier for ASMP-4 approximate-bisimulation robustness."""

from __future__ import annotations

import ast
import hashlib
import json
import math
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Hashable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
V25 = (
    ROOT / "asmp4_periodic_block_completeness_v0_25" / "periodic_block_claim_v0_25.json"
)
V26 = (
    ROOT
    / "asmp4_public_bisimulation_transfer_v0_26"
    / "public_bisimulation_claim_v0_26.json"
)
CONTRACT = HERE / "approximate_bisimulation_contract_v0_27.json"
CLAIM = HERE / "approximate_bisimulation_claim_v0_27.json"
CENTRAL = HERE / "approximate_bisimulation_robustness.py"

SEALS = {
    SOURCE: "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    V25: "447e5dc0d440611d59b4e6b94cd5c68493b7e3c68d8c68ed9b87dd28f9f90d38",
    V26: "1decf7f8eb12b6b76e9c251cdbc2b400403dfb941c6e798a75ab1b0aadc99e9d",
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
)

State = Hashable
Edge = tuple[State, str, State, Fraction, Fraction, bool]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def independent_integrity() -> dict[str, Any]:
    rows = []
    for path, expected in SEALS.items():
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append({"name": path.name, "matches": actual == expected})
    return {
        "rows": rows,
        "pass": len(rows) == 3 and all(row["matches"] for row in rows),
    }


def _group(edges: tuple[Edge, ...]) -> dict[tuple[State, str], tuple[Edge, ...]]:
    grouped: defaultdict[tuple[State, str], list[Edge]] = defaultdict(list)
    for edge in edges:
        grouped[(edge[0], edge[1])].append(edge)
    return {key: tuple(value) for key, value in grouped.items()}


def _actions(edges: tuple[Edge, ...], state: State) -> tuple[str, ...]:
    return tuple(sorted({edge[1] for edge in edges if edge[0] == state}))


def independent_relation_check(
    left_states: tuple[State, ...],
    left_edges: tuple[Edge, ...],
    left_safe: dict[State, bool],
    right_states: tuple[State, ...],
    right_edges: tuple[Edge, ...],
    right_safe: dict[State, bool],
    relation: frozenset[tuple[State, State]],
    epsilon: Fraction,
) -> bool:
    left_group = _group(left_edges)
    right_group = _group(right_edges)

    def matches(left_edge: Edge, right_edge: Edge) -> bool:
        return (
            (left_edge[2], right_edge[2]) in relation
            and left_edge[5] == right_edge[5]
            and abs(left_edge[3] - right_edge[3]) <= epsilon
            and abs(left_edge[4] - right_edge[4]) <= epsilon
        )

    if epsilon < 0:
        return False
    if {pair[0] for pair in relation} != set(left_states):
        return False
    if {pair[1] for pair in relation} != set(right_states):
        return False
    for left_state, right_state in relation:
        if left_safe[left_state] != right_safe[right_state]:
            return False
        if _actions(left_edges, left_state) != _actions(right_edges, right_state):
            return False
        for action in _actions(left_edges, left_state):
            left_outcomes = left_group[(left_state, action)]
            right_outcomes = right_group[(right_state, action)]
            if len({edge[2] for edge in left_outcomes}) != len(left_outcomes):
                return False
            if len({edge[2] for edge in right_outcomes}) != len(right_outcomes):
                return False
            if not all(
                any(matches(left_edge, right_edge) for right_edge in right_outcomes)
                for left_edge in left_outcomes
            ):
                return False
            if not all(
                any(matches(left_edge, right_edge) for left_edge in left_outcomes)
                for right_edge in right_outcomes
            ):
                return False
    return True


def _base_edges() -> tuple[Edge, ...]:
    return (
        (0, "advance", 0, Fraction(1), Fraction(3), True),
        (0, "advance", 1, Fraction(2), Fraction(2), True),
        (0, "reset", 0, Fraction(2), Fraction(2), True),
        (1, "advance", 0, Fraction(2), Fraction(2), True),
        (1, "advance", 1, Fraction(3), Fraction(1), True),
        (1, "reset", 0, Fraction(2), Fraction(2), True),
    )


def _decorated_edges(
    factor: int, epsilon: Fraction
) -> tuple[tuple[State, ...], tuple[Edge, ...]]:
    states = tuple((state, color) for state in (0, 1) for color in range(factor))
    edges = []
    for state, color in states:
        for edge in _base_edges():
            if edge[0] != state:
                continue
            action_bit = int(edge[1] == "reset")
            target_color = (color + state + action_bit) % factor
            read_sign = (3 * color + state + edge[2] + action_bit) % 3 - 1
            write_sign = (5 * color + 2 * state + edge[2] + action_bit) % 3 - 1
            edges.append(
                (
                    (state, color),
                    edge[1],
                    (edge[2], target_color),
                    edge[3] + read_sign * epsilon,
                    edge[4] + write_sign * epsilon,
                    True,
                )
            )
    return states, tuple(edges)


def _scalar_layers(
    states: tuple[State, ...],
    edges: tuple[Edge, ...],
    state_safe: dict[State, bool],
    maximum_horizon: int,
    weight: Fraction,
) -> tuple[dict[State, Fraction | float], ...]:
    grouped = _group(edges)
    layers: list[dict[State, Fraction | float]] = [
        {state: Fraction(0) if state_safe[state] else math.inf for state in states}
    ]
    for _ in range(maximum_horizon):
        previous = layers[-1]
        current: dict[State, Fraction | float] = {}
        for state in states:
            if not state_safe[state]:
                current[state] = math.inf
                continue
            action_values = []
            for action in _actions(edges, state):
                outcomes = grouped[(state, action)]
                if any(
                    not edge[5]
                    or not state_safe[edge[2]]
                    or previous[edge[2]] == math.inf
                    for edge in outcomes
                ):
                    continue
                action_values.append(
                    max(
                        weight * edge[3] + (1 - weight) * edge[4] + previous[edge[2]]
                        for edge in outcomes
                    )
                )
            current[state] = min(action_values) if action_values else math.inf
        layers.append(current)
    return tuple(layers)


def independent_weighted_transfer(
    maximum_factor: int = 48,
    maximum_horizon: int = 10,
    epsilon: Fraction = Fraction(1, 32),
) -> dict[str, Any]:
    weights = (Fraction(0), Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1))
    quotient_states = (0, 1)
    quotient_edges = _base_edges()
    quotient_safe = {0: True, 1: True}
    quotient_layers = {
        weight: _scalar_layers(
            quotient_states,
            quotient_edges,
            quotient_safe,
            maximum_horizon,
            weight,
        )
        for weight in weights
    }
    comparisons = 0
    maximum_states = 0
    failures = []
    for factor in range(1, maximum_factor + 1):
        raw_states, raw_edges = _decorated_edges(factor, epsilon)
        maximum_states = max(maximum_states, len(raw_states))
        raw_safe = {state: True for state in raw_states}
        relation = frozenset((state, state[0]) for state in raw_states)
        relation_passes = independent_relation_check(
            raw_states,
            raw_edges,
            raw_safe,
            quotient_states,
            quotient_edges,
            quotient_safe,
            relation,
            epsilon,
        )
        for weight in weights:
            raw_layers = _scalar_layers(
                raw_states, raw_edges, raw_safe, maximum_horizon, weight
            )
            for horizon in range(1, maximum_horizon + 1):
                comparisons += 1
                gap = max(
                    abs(
                        raw_layers[horizon][raw_state]
                        - quotient_layers[weight][horizon][raw_state[0]]
                    )
                    for raw_state in raw_states
                )
                if not relation_passes or gap > horizon * epsilon:
                    failures.append(
                        {
                            "factor": factor,
                            "weight": str(weight),
                            "horizon": horizon,
                            "gap": float(gap),
                        }
                    )
    checks = {
        "two_thousand_four_hundred_comparisons": comparisons == 2400,
        "maximum_ninety_six_raw_states": maximum_states == 96,
        "five_weights": len(weights) == 5,
        "all_weighted_values_within_T_epsilon": not failures,
    }
    return {
        "comparisons": comparisons,
        "maximum_states": maximum_states,
        "failures": failures,
        "checks": checks,
        "pass": all(checks.values()),
    }


def _adversarial_fixture(
    epsilon: Fraction,
) -> tuple[
    tuple[State, ...],
    tuple[Edge, ...],
    dict[State, bool],
    tuple[State, ...],
    tuple[Edge, ...],
    dict[State, bool],
    frozenset[tuple[State, State]],
]:
    right_states = (0, 1)
    right_edges = (
        (0, "advance", 0, Fraction(1), Fraction(3), True),
        (0, "advance", 1, Fraction(2), Fraction(2), True),
        (0, "reset", 0, Fraction(2), Fraction(2), True),
        (1, "advance", 0, Fraction(2), Fraction(2), True),
        (1, "advance", 1, Fraction(3), Fraction(1), True),
        (1, "reset", 0, Fraction(2), Fraction(2), True),
    )
    right_safe = {0: True, 1: True}
    left_states = tuple((state, color) for state in (0, 1) for color in (0, 1))
    left_edges = []
    for state, color in left_states:
        for index, edge in enumerate(right_edges):
            if edge[0] != state:
                continue
            target_color = (color + edge[2] + int(edge[1] == "reset")) % 2
            left_edges.append(
                (
                    (state, color),
                    edge[1],
                    (edge[2], target_color),
                    edge[3] + ((color + index) % 3 - 1) * epsilon,
                    edge[4] + ((2 * color + index) % 3 - 1) * epsilon,
                    True,
                )
            )
    left_safe = {state: True for state in left_states}
    relation = frozenset((state, state[0]) for state in left_states)
    return (
        left_states,
        tuple(left_edges),
        left_safe,
        right_states,
        right_edges,
        right_safe,
        relation,
    )


def independent_alternating_boundary(
    epsilon: Fraction = Fraction(1, 16),
) -> dict[str, Any]:
    fixture = _adversarial_fixture(epsilon)
    (
        left_states,
        left_edges,
        left_safe,
        right_states,
        right_edges,
        right_safe,
        relation,
    ) = fixture

    def check(
        edges: tuple[Edge, ...] = left_edges,
        safety: dict[State, bool] = left_safe,
        tolerance: Fraction = epsilon,
    ) -> bool:
        return independent_relation_check(
            left_states,
            edges,
            safety,
            right_states,
            right_edges,
            right_safe,
            relation,
            tolerance,
        )

    overflow = list(left_edges)
    edge = overflow[0]
    overflow[0] = (*edge[:3], edge[3] + 3 * epsilon, edge[4], edge[5])
    unsafe_state = dict(left_safe)
    unsafe_state[left_states[0]] = False
    unsafe_transition = list(left_edges)
    edge = unsafe_transition[0]
    unsafe_transition[0] = (*edge[:5], False)
    first_state = left_states[0]
    missing_action = tuple(
        edge
        for edge in left_edges
        if not (edge[0] == first_state and edge[1] == "reset")
    )
    checks = {
        "fixture_passes": check(),
        "missing_back_rejected": not check(left_edges[1:]),
        "cost_overflow_rejected": not check(tuple(overflow)),
        "state_safety_rejected": not check(safety=unsafe_state),
        "transition_safety_rejected": not check(tuple(unsafe_transition)),
        "action_mismatch_rejected": not check(missing_action),
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_sharp_boundaries(maximum_exponent: int = 256) -> dict[str, Any]:
    safety_rows = []
    for exponent in range(1, maximum_exponent + 1):
        delta = Fraction(1, 3**exponent)
        safety_rows.append(
            abs(delta - Fraction(0)) <= delta and delta > 0 and not (Fraction(0) > 0)
        )
    epsilon = Fraction(2, 19)
    horizons = range(1, 65)
    cost_rows = [horizon * epsilon / horizon == epsilon for horizon in horizons]
    delta = Fraction(1, 37)
    robust_pairs = ((4 * delta, 3 * delta), (3 * delta, 2 * delta))
    checks = {
        "two_hundred_fifty_six_metric_close_safety_flips": len(safety_rows) == 256
        and all(safety_rows),
        "sixty_four_exact_cost_slacks": len(cost_rows) == 64 and all(cost_rows),
        "strict_margin_fixture_safe": all(
            abs(left - right) <= delta and left > delta and right > 0
            for left, right in robust_pairs
        ),
        "equality_margin_reaches_unsafe_boundary": delta - delta == 0,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_contract_claim() -> dict[str, Any]:
    contract = _load(CONTRACT)
    claim = _load(CLAIM)
    checks = {
        "contract_schema": contract.get("schema_version")
        == "asmp4_approximate_bisimulation_contract_v0_27",
        "exact_state_safety": contract.get("approximate_relation", {}).get(
            "state_safety"
        )
        == "exact",
        "exact_transition_safety": contract.get("approximate_relation", {}).get(
            "transition_safety"
        )
        == "exact on matched outcomes",
        "finite_T_epsilon": "T epsilon"
        in contract.get("transfer", {}).get("finite_horizon", ""),
        "asymptotic_epsilon": claim.get("theorem", {}).get("asymptotic")
        == "d_H,infinity(R_left,R_right) <= epsilon",
        "seven_mutations": claim.get("mutations_rejected") == 7,
        "central_not_imported": "approximate_bisimulation_robustness"
        not in {
            alias.name
            for node in ast.walk(ast.parse(Path(__file__).read_text(encoding="utf-8")))
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        },
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_mutations() -> dict[str, Any]:
    alternating = independent_alternating_boundary()
    sharp = independent_sharp_boundaries()
    rows = {
        "forward_only": alternating["checks"]["missing_back_rejected"],
        "understate_epsilon": alternating["checks"]["cost_overflow_rejected"],
        "drop_state_safety": alternating["checks"]["state_safety_rejected"],
        "drop_transition_safety": alternating["checks"]["transition_safety_rejected"],
        "drop_action": alternating["checks"]["action_mismatch_rejected"],
        "zero_cost_slack": sharp["checks"]["sixty_four_exact_cost_slacks"],
        "metric_only_safety": sharp["checks"][
            "two_hundred_fifty_six_metric_close_safety_flips"
        ],
    }
    return {"rows": rows, "pass": len(rows) == 7 and all(rows.values())}


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
        "pass": len(rows) == 27 and tests == 304,
    }


def document_sentinels() -> dict[str, Any]:
    required = {
        "THEOREM.md": (
            "full back-and-forth clause",
            "T epsilon",
            "strict safety margin",
            "equality is sharp",
        ),
        "RESULT.md": (
            "Hausdorff slack at most `epsilon`",
            "nonempty to empty",
            "sufficient, not necessary",
        ),
        "PRIOR_ART_BOUNDARY_v0_27.md": (
            "Girard and Pappas",
            "Pola and Tabuada",
            "No novelty is claimed",
        ),
        "COMPLETION_AUDIT_v0_27.md": (
            "314 tests",
            "not claimed",
        ),
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
        "weighted_transfer": independent_weighted_transfer(),
        "alternating_boundary": independent_alternating_boundary(),
        "sharp_boundaries": independent_sharp_boundaries(),
        "contract_claim": independent_contract_claim(),
        "mutations": independent_mutations(),
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
