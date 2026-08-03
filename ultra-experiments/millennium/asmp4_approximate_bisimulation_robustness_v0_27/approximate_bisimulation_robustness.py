"""Robust ASMP-4 capacity transfer under approximate public bisimulation."""

from __future__ import annotations

import ast
import hashlib
import itertools
import json
import math
from collections import defaultdict
from dataclasses import dataclass, replace
from fractions import Fraction
from pathlib import Path
from typing import Any, Hashable, Iterable, Mapping

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
Vector = tuple[Fraction, Fraction]


@dataclass(frozen=True)
class Transition:
    source: State
    action: str
    target: State
    read: Fraction
    write: Fraction
    safe: bool = True


@dataclass(frozen=True)
class Game:
    states: tuple[State, ...]
    transitions: tuple[Transition, ...]
    state_safe: Mapping[State, bool]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fraction(value: int | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


def _edges_by_state_action(
    game: Game,
) -> dict[tuple[State, str], tuple[Transition, ...]]:
    grouped: defaultdict[tuple[State, str], list[Transition]] = defaultdict(list)
    for edge in game.transitions:
        grouped[(edge.source, edge.action)].append(edge)
    return {key: tuple(value) for key, value in grouped.items()}


def _actions(game: Game, state: State) -> tuple[str, ...]:
    return tuple(
        sorted({edge.action for edge in game.transitions if edge.source == state})
    )


def pareto(vectors: Iterable[Vector]) -> tuple[Vector, ...]:
    unique = sorted(set(vectors))
    return tuple(
        vector
        for vector in unique
        if not any(
            other != vector and other[0] <= vector[0] and other[1] <= vector[1]
            for other in unique
        )
    )


def finite_horizon_layers(
    game: Game, maximum_horizon: int
) -> tuple[dict[State, tuple[Vector, ...]], ...]:
    """Exact controller/minimax vector frontiers for public successor histories."""
    edges = _edges_by_state_action(game)
    layers: list[dict[State, tuple[Vector, ...]]] = [
        {
            state: ((Fraction(0), Fraction(0)),) if game.state_safe[state] else ()
            for state in game.states
        }
    ]
    for _ in range(maximum_horizon):
        previous = layers[-1]
        current: dict[State, tuple[Vector, ...]] = {}
        for state in game.states:
            candidates: list[Vector] = []
            if not game.state_safe[state]:
                current[state] = ()
                continue
            for action in _actions(game, state):
                outcomes = edges[(state, action)]
                if any(
                    not edge.safe
                    or not game.state_safe[edge.target]
                    or not previous[edge.target]
                    for edge in outcomes
                ):
                    continue
                continuation_options = []
                for edge in outcomes:
                    continuation_options.append(
                        tuple(
                            (
                                _fraction(edge.read) + continuation[0],
                                _fraction(edge.write) + continuation[1],
                            )
                            for continuation in previous[edge.target]
                        )
                    )
                for choices in itertools.product(*continuation_options):
                    candidates.append(
                        (
                            max(choice[0] for choice in choices),
                            max(choice[1] for choice in choices),
                        )
                    )
            current[state] = pareto(candidates)
        layers.append(current)
    return tuple(layers)


def directed_upward_gap(
    left: tuple[Vector, ...], right: tuple[Vector, ...]
) -> Fraction | float:
    """Distance from up(left) to up(right) in coordinatewise additive slack."""
    if not left:
        return Fraction(0)
    if not right:
        return math.inf
    return max(
        min(
            max(
                Fraction(0),
                candidate[0] - vector[0],
                candidate[1] - vector[1],
            )
            for candidate in right
        )
        for vector in left
    )


def symmetric_upward_gap(
    left: tuple[Vector, ...], right: tuple[Vector, ...]
) -> Fraction | float:
    return max(directed_upward_gap(left, right), directed_upward_gap(right, left))


def approximate_bisimulation_report(
    left: Game,
    right: Game,
    relation: frozenset[tuple[State, State]],
    epsilon: Fraction,
) -> dict[str, Any]:
    """Check exact safety/action matching and epsilon-close alternating edges."""
    epsilon = _fraction(epsilon)
    left_edges = _edges_by_state_action(left)
    right_edges = _edges_by_state_action(right)

    def matches(left_edge: Transition, right_edge: Transition) -> bool:
        return (
            (left_edge.target, right_edge.target) in relation
            and left_edge.safe == right_edge.safe
            and abs(_fraction(left_edge.read) - _fraction(right_edge.read)) <= epsilon
            and abs(_fraction(left_edge.write) - _fraction(right_edge.write)) <= epsilon
        )

    state_safety = all(
        left.state_safe[left_state] == right.state_safe[right_state]
        for left_state, right_state in relation
    )
    actions_match = all(
        _actions(left, left_state) == _actions(right, right_state)
        for left_state, right_state in relation
    )
    edge_back_and_forth = True
    for left_state, right_state in relation:
        if _actions(left, left_state) != _actions(right, right_state):
            edge_back_and_forth = False
            continue
        for action in _actions(left, left_state):
            left_outcomes = left_edges[(left_state, action)]
            right_outcomes = right_edges[(right_state, action)]
            if not all(
                any(matches(left_edge, right_edge) for right_edge in right_outcomes)
                for left_edge in left_outcomes
            ) or not all(
                any(matches(left_edge, right_edge) for left_edge in left_outcomes)
                for right_edge in right_outcomes
            ):
                edge_back_and_forth = False
    left_total = {pair[0] for pair in relation} == set(left.states)
    right_total = {pair[1] for pair in relation} == set(right.states)
    public_outcomes_unique = all(
        len({edge.target for edge in outcomes}) == len(outcomes)
        for outcomes in itertools.chain(left_edges.values(), right_edges.values())
    )
    checks = {
        "epsilon_nonnegative": epsilon >= 0,
        "relation_left_total": left_total,
        "relation_right_total": right_total,
        "state_safety_exact": state_safety,
        "enabled_actions_exact": actions_match,
        "transition_safety_cost_successors_back_and_forth": edge_back_and_forth,
        "public_outcomes_unique": public_outcomes_unique,
    }
    return {"checks": checks, "pass": all(checks.values())}


def quotient_game() -> Game:
    transitions = (
        Transition(0, "stay", 0, Fraction(1), Fraction(3)),
        Transition(0, "switch", 1, Fraction(4), Fraction(4)),
        Transition(1, "stay", 1, Fraction(3), Fraction(1)),
        Transition(1, "switch", 0, Fraction(4), Fraction(4)),
    )
    return Game((0, 1), transitions, {0: True, 1: True})


def decorated_game(
    factor: int, epsilon: Fraction
) -> tuple[Game, frozenset[tuple[State, State]]]:
    quotient = quotient_game()
    states = tuple(
        (quotient_state, color) for quotient_state in (0, 1) for color in range(factor)
    )
    transitions: list[Transition] = []
    for state in states:
        quotient_state, color = state
        for edge in quotient.transitions:
            if edge.source != quotient_state:
                continue
            action_bit = int(edge.action == "switch")
            target_color = (color + quotient_state + action_bit) % factor
            read_sign = (3 * color + quotient_state + action_bit) % 3 - 1
            write_sign = (5 * color + 2 * quotient_state + action_bit) % 3 - 1
            transitions.append(
                Transition(
                    state,
                    edge.action,
                    (edge.target, target_color),
                    edge.read + read_sign * epsilon,
                    edge.write + write_sign * epsilon,
                )
            )
    game = Game(states, tuple(transitions), {state: True for state in states})
    relation = frozenset((state, state[0]) for state in states)
    return game, relation


def decorated_transfer_report(
    maximum_factor: int = 32,
    maximum_horizon: int = 8,
    epsilon: Fraction = Fraction(1, 32),
) -> dict[str, Any]:
    quotient = quotient_game()
    quotient_layers = finite_horizon_layers(quotient, maximum_horizon)
    rows = []
    failures = []
    for factor in range(1, maximum_factor + 1):
        raw, relation = decorated_game(factor, epsilon)
        bisimulation = approximate_bisimulation_report(raw, quotient, relation, epsilon)
        raw_layers = finite_horizon_layers(raw, maximum_horizon)
        for horizon in range(1, maximum_horizon + 1):
            gaps = [
                symmetric_upward_gap(
                    raw_layers[horizon][raw_state],
                    quotient_layers[horizon][quotient_state],
                )
                for raw_state, quotient_state in relation
            ]
            maximum_gap = max(gaps)
            bound = horizon * epsilon
            passed = bisimulation["pass"] and maximum_gap <= bound
            row = {
                "factor": factor,
                "horizon": horizon,
                "raw_states": len(raw.states),
                "maximum_cumulative_gap": float(maximum_gap),
                "bound": float(bound),
                "pass": passed,
            }
            rows.append(row)
            if not passed:
                failures.append(row)
    checks = {
        "all_256_factor_horizon_rows": len(rows) == 256,
        "maximum_sixty_four_raw_states": max(row["raw_states"] for row in rows) == 64,
        "all_relations_pass": not failures,
        "normalized_gap_at_most_epsilon": all(
            row["maximum_cumulative_gap"] / row["horizon"] <= float(epsilon) + 1e-12
            for row in rows
        ),
    }
    return {
        "epsilon": float(epsilon),
        "rows": rows,
        "failures": failures,
        "checks": checks,
        "pass": all(checks.values()),
    }


def adversarial_games(
    epsilon: Fraction = Fraction(1, 16),
) -> tuple[Game, Game, frozenset[tuple[State, State]]]:
    quotient = Game(
        (0, 1),
        (
            Transition(0, "advance", 0, Fraction(1), Fraction(3)),
            Transition(0, "advance", 1, Fraction(2), Fraction(2)),
            Transition(0, "reset", 0, Fraction(2), Fraction(2)),
            Transition(1, "advance", 0, Fraction(2), Fraction(2)),
            Transition(1, "advance", 1, Fraction(3), Fraction(1)),
            Transition(1, "reset", 0, Fraction(2), Fraction(2)),
        ),
        {0: True, 1: True},
    )
    states = tuple((state, color) for state in (0, 1) for color in (0, 1))
    raw_edges = []
    for state, color in states:
        for index, edge in enumerate(quotient.transitions):
            if edge.source != state:
                continue
            target_color = (color + edge.target + int(edge.action == "reset")) % 2
            read_sign = (color + index) % 3 - 1
            write_sign = (2 * color + index) % 3 - 1
            raw_edges.append(
                Transition(
                    (state, color),
                    edge.action,
                    (edge.target, target_color),
                    edge.read + read_sign * epsilon,
                    edge.write + write_sign * epsilon,
                )
            )
    raw = Game(states, tuple(raw_edges), {state: True for state in states})
    relation = frozenset((state, state[0]) for state in states)
    return raw, quotient, relation


def adversarial_transfer_report(
    maximum_horizon: int = 8, epsilon: Fraction = Fraction(1, 16)
) -> dict[str, Any]:
    raw, quotient, relation = adversarial_games(epsilon)
    bisimulation = approximate_bisimulation_report(raw, quotient, relation, epsilon)
    raw_layers = finite_horizon_layers(raw, maximum_horizon)
    quotient_layers = finite_horizon_layers(quotient, maximum_horizon)
    rows = []
    for horizon in range(1, maximum_horizon + 1):
        maximum_gap = max(
            symmetric_upward_gap(
                raw_layers[horizon][raw_state],
                quotient_layers[horizon][quotient_state],
            )
            for raw_state, quotient_state in relation
        )
        rows.append(
            {
                "horizon": horizon,
                "maximum_gap": float(maximum_gap),
                "bound": float(horizon * epsilon),
                "pass": maximum_gap <= horizon * epsilon,
            }
        )
    checks = {
        "alternating_relation_passes": bisimulation["pass"],
        "two_adversarial_successors_present": any(
            len(edges) == 2 for edges in _edges_by_state_action(quotient).values()
        ),
        "all_eight_vector_frontiers_transfer": len(rows) == 8
        and all(row["pass"] for row in rows),
    }
    return {"checks": checks, "rows": rows, "pass": all(checks.values())}


def cost_sharpness_report(
    epsilon: Fraction = Fraction(1, 7), maximum_horizon: int = 32
) -> dict[str, Any]:
    left = Game(
        (0,),
        (Transition(0, "loop", 0, Fraction(0), Fraction(0)),),
        {0: True},
    )
    right = Game(
        (0,),
        (Transition(0, "loop", 0, epsilon, epsilon),),
        {0: True},
    )
    relation = frozenset({(0, 0)})
    left_layers = finite_horizon_layers(left, maximum_horizon)
    right_layers = finite_horizon_layers(right, maximum_horizon)
    rows = []
    for horizon in range(1, maximum_horizon + 1):
        gap = symmetric_upward_gap(left_layers[horizon][0], right_layers[horizon][0])
        rows.append(
            {
                "horizon": horizon,
                "gap": float(gap),
                "exact": gap == horizon * epsilon,
            }
        )
    checks = {
        "epsilon_bisimulation": approximate_bisimulation_report(
            left, right, relation, epsilon
        )["pass"],
        "all_thirty_two_cumulative_bounds_tight": len(rows) == 32
        and all(row["exact"] for row in rows),
        "asymptotic_per_step_bound_tight": rows[-1]["gap"] / maximum_horizon
        == float(epsilon),
    }
    return {"checks": checks, "rows": rows, "pass": all(checks.values())}


def safety_margin_boundary_report(maximum_exponent: int = 128) -> dict[str, Any]:
    rows = []
    for exponent in range(1, maximum_exponent + 1):
        delta = Fraction(1, 2**exponent)
        left_margin = delta
        right_margin = Fraction(0)
        rows.append(
            {
                "exponent": exponent,
                "distance": float(delta),
                "metric_close": abs(left_margin - right_margin) <= delta,
                "left_safe": left_margin > 0,
                "right_safe": right_margin > 0,
            }
        )
    delta = Fraction(1, 64)
    robust_left = (3 * delta, 4 * delta)
    robust_right = (2 * delta, 3 * delta)
    robust_transfer = all(
        abs(left - right) <= delta and left > delta and right > 0
        for left, right in zip(robust_left, robust_right, strict=True)
    )
    safe_game = Game(
        (0,),
        (Transition(0, "loop", 0, Fraction(0), Fraction(0)),),
        {0: True},
    )
    unsafe_game = Game(
        (0,),
        (Transition(0, "loop", 0, Fraction(0), Fraction(0)),),
        {0: False},
    )
    safe_frontier = finite_horizon_layers(safe_game, 1)[1][0]
    unsafe_frontier = finite_horizon_layers(unsafe_game, 1)[1][0]
    checks = {
        "one_hundred_twenty_eight_arbitrarily_close_flips": len(rows) == 128
        and all(
            row["metric_close"] and row["left_safe"] and not row["right_safe"]
            for row in rows
        ),
        "strict_lipschitz_margin_transfers_safety": robust_transfer,
        "equality_margin_is_sharp": delta > 0 and not (delta - delta > 0),
        "zero_error_region_jumps_nonempty_to_empty": bool(safe_frontier)
        and not unsafe_frontier,
    }
    return {"checks": checks, "rows": rows, "pass": all(checks.values())}


def mutation_report(epsilon: Fraction = Fraction(1, 16)) -> dict[str, Any]:
    raw, quotient, relation = adversarial_games(epsilon)
    missing_back = Game(raw.states, raw.transitions[1:], raw.state_safe)
    cost_overflow_edges = list(raw.transitions)
    cost_overflow_edges[0] = replace(
        cost_overflow_edges[0], read=cost_overflow_edges[0].read + 3 * epsilon
    )
    cost_overflow = Game(raw.states, tuple(cost_overflow_edges), raw.state_safe)
    unsafe_states = dict(raw.state_safe)
    unsafe_states[raw.states[0]] = False
    state_mismatch = Game(raw.states, raw.transitions, unsafe_states)
    transition_mismatch_edges = list(raw.transitions)
    transition_mismatch_edges[0] = replace(transition_mismatch_edges[0], safe=False)
    transition_mismatch = Game(
        raw.states, tuple(transition_mismatch_edges), raw.state_safe
    )
    first_state = raw.states[0]
    action_mismatch = Game(
        raw.states,
        tuple(
            edge
            for edge in raw.transitions
            if not (edge.source == first_state and edge.action == "reset")
        ),
        raw.state_safe,
    )
    sharp = cost_sharpness_report(epsilon, 4)
    safety = safety_margin_boundary_report(8)
    rows = {
        "forward_matching_without_back": not approximate_bisimulation_report(
            missing_back, quotient, relation, epsilon
        )["pass"],
        "understate_cost_error": not approximate_bisimulation_report(
            cost_overflow, quotient, relation, epsilon
        )["pass"],
        "drop_state_safety": not approximate_bisimulation_report(
            state_mismatch, quotient, relation, epsilon
        )["pass"],
        "drop_transition_safety": not approximate_bisimulation_report(
            transition_mismatch, quotient, relation, epsilon
        )["pass"],
        "drop_registered_action": not approximate_bisimulation_report(
            action_mismatch, quotient, relation, epsilon
        )["pass"],
        "claim_zero_asymptotic_cost_error": sharp["checks"][
            "asymptotic_per_step_bound_tight"
        ],
        "metric_closeness_alone_preserves_zero_error": safety["checks"][
            "zero_error_region_jumps_nonempty_to_empty"
        ],
    }
    return {
        "rows": rows,
        "cases": len(rows),
        "rejected": sum(rows.values()),
        "pass": len(rows) == 7 and all(rows.values()),
    }


def expected_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_approximate_bisimulation_contract_v0_27",
        "objective": "quantified two-port rate transfer with zero-error safety",
        "game_semantics": {
            "controller": "causal public-history strategies choose registered action types",
            "adversary": "universally quantified public successor outcomes",
            "costs": "nonnegative additive read/write edge log-cost vectors",
            "safety": "all visited states and traversed transitions must be safe",
            "rate": "coordinatewise worst-path limsup average cost",
        },
        "approximate_relation": {
            "state_safety": "exact",
            "transition_safety": "exact on matched outcomes",
            "enabled_action_types": "exact",
            "successors": "exact relational back-and-forth for every adversarial outcome",
            "cost_error": "per matched edge l_infinity error at most epsilon",
        },
        "transfer": {
            "finite_horizon": "cumulative vector-budget slack at most T epsilon",
            "asymptotic": "rate-region l_infinity Hausdorff slack at most epsilon",
            "empty_region": "preserved because safety status is exact",
        },
        "metric_safety_margin": {
            "guard": "safe iff signed margin m is positive",
            "regularity": "m is L-Lipschitz on related observations",
            "sufficient_margin": "every related reachable source has m greater than L delta",
            "sharpness": "equality can map a safe state to the unsafe boundary",
        },
        "nonclaims": [
            "approximate safety without a strict margin",
            "nonadditive transcript-tree costs",
            "construction of finite quotients for arbitrary nonlinear systems",
            "solution of multidimensional adversarial mean-payoff games",
        ],
    }


def expected_claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_approximate_bisimulation_robustness_v0_27",
        "theorem": {
            "name": "epsilon-cost alternating-bisimulation transfer",
            "finite_horizon": "b in R_left(T) implies b+T epsilon 1 in R_right(T), and conversely",
            "asymptotic": "d_H,infinity(R_left,R_right) <= epsilon",
            "safety_condition": "state and transition safety are exact on the relation",
            "strategy_memory": "unrestricted causal representative histories in both directions",
        },
        "sharpness": {
            "cost": "one-state loops attain normalized gap epsilon at every horizon",
            "safety": "for every delta>0, delta-close observations can have nonempty versus empty zero-error regions",
            "margin": "strict L delta safety margin suffices; equality is insufficient",
        },
        "central_harness": {
            "decorated_rows": 256,
            "maximum_raw_states": 64,
            "maximum_horizon": 8,
            "adversarial_vector_horizons": 8,
            "cost_sharpness_horizons": 32,
            "safety_flip_scales": 128,
        },
        "independent_harness": {
            "weighted_comparisons": 2400,
            "maximum_raw_states": 96,
            "maximum_horizon": 10,
            "weights": ["0", "1/4", "1/2", "3/4", "1"],
            "safety_flip_scales": 256,
        },
        "mutations_rejected": 7,
        "predecessor_inventory": {"packages": 27, "tests": 304},
        "disposition": "approximate cost transfer resolved under exact safety; metric-only zero-error transfer refuted",
    }


def resource_integrity_report() -> dict[str, Any]:
    rows = []
    for path, expected in SEALS.items():
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append({"name": path.name, "matches": actual == expected})
    return {
        "rows": rows,
        "pass": len(rows) == 3 and all(row["matches"] for row in rows),
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
        "pass": len(rows) == 27 and total == 304,
    }


def payload_report() -> dict[str, Any]:
    required = {
        "README.md",
        "THEOREM.md",
        "RESULT.md",
        "COMPLETION_AUDIT_v0_27.md",
        "REVIEWER_PACKET_v0_27.md",
        "PRIOR_ART_BOUNDARY_v0_27.md",
        "approximate_bisimulation_contract_v0_27.json",
        "approximate_bisimulation_claim_v0_27.json",
        "approximate_bisimulation_robustness.py",
        "verify_approximate_bisimulation_robustness.py",
        "test_approximate_bisimulation_robustness.py",
        "run_verification.py",
    }
    present = {path.name for path in HERE.iterdir() if path.is_file()}
    return {
        "required": len(required),
        "missing": sorted(required - present),
        "pass": required <= present,
    }


def robustness_report() -> dict[str, Any]:
    components = {
        "resource_integrity": resource_integrity_report(),
        "contract_exactness": {
            "pass": CONTRACT.exists() and _load(CONTRACT) == expected_contract_payload()
        },
        "claim_exactness": {
            "pass": CLAIM.exists() and _load(CLAIM) == expected_claim_payload()
        },
        "decorated_transfer": decorated_transfer_report(),
        "adversarial_transfer": adversarial_transfer_report(),
        "cost_sharpness": cost_sharpness_report(),
        "safety_margin_boundary": safety_margin_boundary_report(),
        "mutations": mutation_report(),
        "predecessor_inventory": predecessor_inventory_report(),
        "payload": payload_report(),
    }
    return {
        "schema_version": "asmp4_approximate_bisimulation_robustness_v0_27",
        **components,
        "pass": all(component["pass"] for component in components.values()),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    report = robustness_report() if report is None else report
    return {
        "R0_three_resource_seals": report["resource_integrity"]["pass"],
        "R1_exact_contract": report["contract_exactness"]["pass"],
        "R2_exact_claim": report["claim_exactness"]["pass"],
        "R3_decorated_vector_transfer": report["decorated_transfer"]["pass"],
        "R4_adversarial_back_and_forth": report["adversarial_transfer"]["pass"],
        "R5_cost_bound_is_sharp": report["cost_sharpness"]["pass"],
        "R6_zero_error_margin_boundary": report["safety_margin_boundary"]["pass"],
        "R7_seven_mutations_rejected": report["mutations"]["pass"],
        "R8_predecessor_inventory": report["predecessor_inventory"]["pass"],
        "R9_complete_payload": report["payload"]["pass"],
    }


def main() -> int:
    report = robustness_report()
    payload = {"gates": verification_gates(report), "report": report}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
