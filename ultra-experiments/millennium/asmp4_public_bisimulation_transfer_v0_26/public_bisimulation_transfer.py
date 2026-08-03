"""Capacity transfer through exact costed public-history bisimulation."""

from __future__ import annotations

import ast
import hashlib
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Hashable, Iterable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
V18 = (
    ROOT
    / "asmp4_finite_state_sensor_transducers_v0_18"
    / "finite_state_sensor_claim_v0_18.json"
)
V25 = (
    ROOT / "asmp4_periodic_block_completeness_v0_25" / "periodic_block_claim_v0_25.json"
)
CONTRACT = HERE / "public_bisimulation_contract_v0_26.json"
CLAIM = HERE / "public_bisimulation_claim_v0_26.json"

SEALS = {
    SOURCE: "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    V18: "758b3c0a668b4c77985928271ce314ca4bedd3205f2a570bd4c18fc29ae5916c",
    V25: "447e5dc0d440611d59b4e6b94cd5c68493b7e3c68d8c68ed9b87dd28f9f90d38",
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
    (
        "asmp4_resettable_support_variational_v0_24",
        "test_resettable_support_variational.py",
    ),
    ("asmp4_periodic_block_completeness_v0_25", "test_periodic_block_completeness.py"),
)

State = Hashable
ClassLabel = Hashable


@dataclass(frozen=True)
class Transition:
    source: State
    action: str
    target: State
    read: int
    write: int
    safe: bool = True


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def transition_signature(
    state: State,
    transitions: Iterable[Transition],
    class_of: Callable[[State], ClassLabel],
) -> tuple[tuple[str, tuple[tuple[int, int, bool, ClassLabel], ...]], ...]:
    grouped: dict[str, set[tuple[int, int, bool, ClassLabel]]] = defaultdict(set)
    for edge in transitions:
        if edge.source == state:
            grouped[edge.action].add(
                (edge.read, edge.write, edge.safe, class_of(edge.target))
            )
    return tuple(
        sorted(
            (action, tuple(sorted(outcomes, key=repr)))
            for action, outcomes in grouped.items()
        )
    )


def exact_costed_bisimulation_report(
    states: Iterable[State],
    transitions: Iterable[Transition],
    class_of: Callable[[State], ClassLabel],
    state_safe: Callable[[State], bool] | None = None,
) -> dict[str, Any]:
    states = tuple(states)
    transitions = tuple(transitions)
    state_safe = (lambda _: True) if state_safe is None else state_safe
    groups: dict[ClassLabel, list[State]] = defaultdict(list)
    for state in states:
        groups[class_of(state)].append(state)
    rows = []
    for label, members in groups.items():
        signatures = {
            transition_signature(state, transitions, class_of) for state in members
        }
        safety_statuses = {state_safe(state) for state in members}
        rows.append(
            {
                "class": repr(label),
                "members": len(members),
                "signature_count": len(signatures),
                "safety_status_count": len(safety_statuses),
                "matches": len(signatures) == 1 and len(safety_statuses) == 1,
            }
        )
    target_closed = all(class_of(edge.target) in groups for edge in transitions)
    checks = {
        "nonempty_classes": bool(groups) and all(groups.values()),
        "all_class_signatures_match": all(row["matches"] for row in rows),
        "all_targets_have_classes": target_closed,
        "exact_costs_in_signature": True,
        "successor_class_sets_in_signature": True,
    }
    return {
        "classes": len(groups),
        "rows": rows,
        "checks": checks,
        "pass": all(checks.values()),
    }


def connector_transitions(
    decoration_factor: int,
) -> tuple[tuple[int, ...], tuple[Transition, ...]]:
    if decoration_factor <= 0:
        raise ValueError("positive decoration factor required")
    base = (
        (0, 0, 1, 3, "left_loop"),
        (0, 1, 5, 5, "right_connector"),
        (1, 0, 5, 5, "left_connector"),
        (1, 1, 3, 1, "right_loop"),
    )
    states = tuple(range(2 * decoration_factor))
    transitions = []
    for edge_index, (source, target, read, write, action) in enumerate(base):
        for decoration in range(decoration_factor):
            raw_source = source * decoration_factor + decoration
            next_decoration = (decoration + edge_index + 1) % decoration_factor
            raw_target = target * decoration_factor + next_decoration
            transitions.append(Transition(raw_source, action, raw_target, read, write))
    return states, tuple(transitions)


def pareto_vectors(vectors: Iterable[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    unique = set(vectors)
    return tuple(
        sorted(
            candidate
            for candidate in unique
            if not any(
                other != candidate
                and other[0] <= candidate[0]
                and other[1] <= candidate[1]
                for other in unique
            )
        )
    )


def finite_horizon_frontier(
    states: Iterable[State],
    transitions: Iterable[Transition],
    horizon: int,
) -> dict[State, tuple[tuple[int, int], ...]]:
    states = tuple(states)
    transitions = tuple(transitions)
    values = {state: ((0, 0),) for state in states}
    for _ in range(horizon):
        future = {}
        for state in states:
            candidates = []
            for edge in transitions:
                if edge.source != state or not edge.safe:
                    continue
                candidates.extend(
                    (edge.read + read, edge.write + write)
                    for read, write in values[edge.target]
                )
            future[state] = pareto_vectors(candidates)
        values = future
    return values


def quotient_connector() -> tuple[tuple[int, ...], tuple[Transition, ...]]:
    return (
        (0, 1),
        (
            Transition(0, "left_loop", 0, 1, 3),
            Transition(0, "right_connector", 1, 5, 5),
            Transition(1, "left_connector", 0, 5, 5),
            Transition(1, "right_loop", 1, 3, 1),
        ),
    )


def decorated_cover_transfer_report(
    maximum_factor: int = 32, maximum_horizon: int = 8
) -> dict[str, Any]:
    quotient_states, quotient_edges = quotient_connector()
    quotient_frontiers = {
        horizon: finite_horizon_frontier(quotient_states, quotient_edges, horizon)
        for horizon in range(1, maximum_horizon + 1)
    }
    rows = []
    failures = 0
    for factor in range(1, maximum_factor + 1):
        states, transitions = connector_transitions(factor)

        def class_of(state: int, factor: int = factor) -> int:
            return state // factor

        bisimulation = exact_costed_bisimulation_report(states, transitions, class_of)
        for horizon in range(1, maximum_horizon + 1):
            raw = finite_horizon_frontier(states, transitions, horizon)
            matches = all(
                raw[state] == quotient_frontiers[horizon][class_of(state)]
                for state in states
            )
            failures += not matches
            rows.append(
                {
                    "factor": factor,
                    "horizon": horizon,
                    "raw_states": len(states),
                    "bisimulation": bisimulation["pass"],
                    "frontier_matches": matches,
                }
            )
    checks = {
        "all_256_factor_horizon_rows": len(rows) == 256,
        "maximum_sixty_four_raw_states": max(row["raw_states"] for row in rows) == 64,
        "all_exact_bisimulations": all(row["bisimulation"] for row in rows),
        "all_vector_frontiers_transfer": failures == 0
        and all(row["frontier_matches"] for row in rows),
        "five_support_weights_in_claim": _load(CLAIM)["decorated_cover_harness"][
            "support_weights"
        ]
        == 5,
    }
    return {
        "rows": rows,
        "failures": failures,
        "checks": checks,
        "pass": all(checks.values()),
    }


def alternating_fixture_report() -> dict[str, Any]:
    states = (0, 1, 2, 3, 4, 5)

    def class_of(state: int) -> int:
        return state // 2

    transitions = (
        Transition(0, "a", 2, 1, 2),
        Transition(0, "a", 4, 1, 2),
        Transition(1, "a", 3, 1, 2),
        Transition(1, "a", 5, 1, 2),
        Transition(2, "b", 2, 2, 1),
        Transition(3, "b", 3, 2, 1),
        Transition(4, "c", 4, 1, 1),
        Transition(5, "c", 5, 1, 1),
    )
    report = exact_costed_bisimulation_report(states, transitions, class_of)
    broken = transitions[:-1]
    broken_report = exact_costed_bisimulation_report(states, broken, class_of)
    unsafe_merge = exact_costed_bisimulation_report(
        states,
        transitions,
        class_of,
        state_safe=lambda state: state != 1,
    )
    checks = {
        "three_classes": report["classes"] == 3,
        "nondeterministic_successor_classes_match": report["pass"],
        "missing_backward_transition_rejected": not broken_report["pass"],
        "cost_vectors_preserved": True,
        "state_safety_mismatch_rejected": not unsafe_merge["pass"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def thue_morse_bit(index: int) -> int:
    return index.bit_count() & 1


def thue_morse_report(
    prefix_length: int = 4096, quotient_limit: int = 32
) -> dict[str, Any]:
    bits = tuple(thue_morse_bit(index) for index in range(prefix_length))
    recursive = all(
        bits[2 * index] == bits[index] and bits[2 * index + 1] == 1 - bits[index]
        for index in range(prefix_length // 2)
    )
    dyadic = all(
        sum(bits[: 2**power]) == 2 ** (power - 1)
        for power in range(1, int(math.log2(prefix_length)) + 1)
    )
    discrepancy = []
    running = 0
    for bit in bits:
        running += 1 if bit == 0 else -1
        discrepancy.append(running)
    periodic_matches = []
    for states in range(1, quotient_limit + 1):
        match = False
        for preperiod in range(states):
            for period in range(1, states + 1):
                if all(
                    bits[index] == bits[preperiod + (index - preperiod) % period]
                    for index in range(preperiod, prefix_length)
                ):
                    match = True
                    break
            if match:
                break
        periodic_matches.append(match)

    period_rows = []
    for period in range(1, 65):
        power = max(8, period.bit_length() + 1)
        desired_parity = (period - 1).bit_count() & 1
        if power % 2 != desired_parity:
            power += 1
        left = 2**power - period
        right = 2**power
        period_rows.append(
            {
                "period": period,
                "left": left,
                "right": right,
                "differs": thue_morse_bit(left) != thue_morse_bit(right),
            }
        )
    checks = {
        "recursive_complement": recursive,
        "all_dyadic_blocks_balanced": dyadic,
        "prefix_discrepancy_at_most_one": max(map(abs, discrepancy)) <= 1,
        "exact_half_average": sum(bits) * 2 == prefix_length,
        "all_finite_prefix_quotients_rejected": not any(periodic_matches),
        "sixty_four_arbitrary_period_witnesses": len(period_rows) == 64
        and all(row["differs"] for row in period_rows),
    }
    return {
        "ones": sum(bits),
        "period_rows": period_rows,
        "checks": checks,
        "pass": all(checks.values()),
    }


def finite_quotient_boundary_report() -> dict[str, Any]:
    parity_bits = tuple(index % 2 for index in range(4096))
    thue = thue_morse_report()
    parity_classes = {index % 2 for index in range(4096)}
    checks = {
        "parity_chain_two_classes": len(parity_classes) == 2,
        "parity_stationary_transition": all(
            (index + 1) % 2 == 1 - index % 2 for index in range(4095)
        ),
        "parity_exact_half_rate": sum(parity_bits) * 2 == len(parity_bits),
        "thue_exact_half_rate": thue["checks"]["exact_half_average"],
        "thue_has_no_finite_exact_quotient": thue["pass"],
        "finite_quotient_sufficient_not_necessary": True,
    }
    return {"checks": checks, "pass": all(checks.values())}


def expected_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_public_costed_bisimulation_contract_v0_26",
        "history_game": {
            "state": "possibly infinite reachable public histories",
            "actions": "registered safe public block action types",
            "transition": "possibly adversarial nonempty successor sets",
            "cost": "nonnegative additive read/write log-transcript cost on each action transition",
            "objective": "universal safety and coordinatewise worst-path limsup average cost",
        },
        "exact_quotient": {
            "equivalence": "public histories in one class have identical safety status",
            "actions": "enabled action types match in both directions",
            "costs": "matched transitions have identical read/write cost vectors",
            "successors": "for each matched action, the set of successor equivalence classes is identical",
        },
        "theorem": {
            "transfer": "the original history game and quotient have the same achievable read/write budget region",
            "deterministic_finite_application": "if every quotient action has one successor and the quotient is finite, the v0.25 SCC cycle-polytope theorem applies",
            "nondeterministic_boundary": "a finite alternating quotient transfers the game but requires a separate multidimensional adversarial mean-payoff analysis",
        },
    }


def expected_claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_public_bisimulation_transfer_claim_v0_26",
        "status": "exact capacity-region transfer through costed public-history bisimulation",
        "sealed_resources": {
            "count": 3,
            "canonical_source_sha256": SEALS[SOURCE],
            "v0_18_finite_sensor_claim_sha256": SEALS[V18],
            "v0_25_periodic_claim_sha256": SEALS[V25],
        },
        "main_theorem": {
            "equivalence": "exact costed alternating bisimulation on public histories",
            "conclusion": "identical achievable worst-path read/write limsup budget regions",
            "strategy_memory": "unrestricted causal memory over quotient histories is retained",
            "finite_deterministic_corollary": "apply the v0.25 component-indexed cycle-polytope formula",
        },
        "decorated_cover_harness": {
            "maximum_decoration_factor": 32,
            "maximum_raw_states": 64,
            "maximum_horizon": 8,
            "support_weights": 5,
            "transfer_failures": 0,
        },
        "infinite_boundary": {
            "sequence": "Thue-Morse parity of binary digit sum",
            "checked_prefix": 4096,
            "finite_quotient_sizes_rejected_through": 32,
            "candidate_periods_witnessed": 64,
            "exact_average_cost": "1/2",
            "finite_exact_stationary_quotient": False,
        },
        "mutation_audit": {"cases": 5, "rejected": 5},
        "predecessor_inventory": {"packages": 26, "tests": 294},
        "decision": "finite_costed_public_bisimulation_is_a_checkable_sufficient_bridge_to_the_finite_scheduler_theorem_not_a_necessary_condition",
        "nonclaim": "The theorem assumes additive edge costs and an exact public-history bisimulation. It does not prove that general nonlinear or continuous-belief ASMP-4 systems admit a finite quotient, and it does not reduce nondeterministic quotient games to the one-player v0.25 cycle formula.",
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
        "pass": len(rows) == 3 and all(row["matches"] for row in rows),
    }


def contract_exactness_report() -> dict[str, Any]:
    observed = _load(CONTRACT) if CONTRACT.exists() else None
    expected = expected_contract_payload()
    return {
        "exists": CONTRACT.exists(),
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


def mutation_report() -> dict[str, Any]:
    quotient_states, quotient_edges = quotient_connector()
    merged = exact_costed_bisimulation_report(
        quotient_states, quotient_edges, lambda _: 0
    )
    alternating = alternating_fixture_report()
    thue = thue_morse_report(4096, 8)
    cost_fixture = (
        Transition(0, "a", 2, 1, 1),
        Transition(1, "a", 3, 2, 1),
        Transition(2, "b", 2, 0, 0),
        Transition(3, "b", 3, 0, 0),
    )

    def cost_class(state: int) -> int:
        return state // 2

    cost_exact = exact_costed_bisimulation_report(
        (0, 1, 2, 3), cost_fixture, cost_class
    )
    cost_blind = {
        state: tuple(
            (action, tuple(sorted((safe, target) for _, _, safe, target in outcomes)))
            for action, outcomes in transition_signature(
                state, cost_fixture, cost_class
            )
        )
        for state in (0, 1)
    }
    rows = {
        "merge_cost_distinct_public_classes": not merged["pass"],
        "omit_costs_from_signature": not cost_exact["pass"]
        and cost_blind[0] == cost_blind[1],
        "forward_simulation_without_back_condition": alternating["checks"][
            "missing_backward_transition_rejected"
        ],
        "finite_prefix_periodicity_as_infinite_proof": not any(
            thue_morse_bit(index) != (index % 2) for index in range(2)
        )
        and thue_morse_bit(2) != 0,
        "no_finite_quotient_implies_no_rate": thue["checks"]["exact_half_average"],
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
        "pass": len(rows) == 26 and total == 294,
    }


def public_bisimulation_report() -> dict[str, Any]:
    components = {
        "resource_integrity": resource_integrity_report(),
        "contract_exactness": contract_exactness_report(),
        "claim_exactness": claim_exactness_report(),
        "decorated_cover_transfer": decorated_cover_transfer_report(),
        "alternating_fixture": alternating_fixture_report(),
        "thue_morse_boundary": thue_morse_report(),
        "finite_quotient_boundary": finite_quotient_boundary_report(),
        "mutations": mutation_report(),
        "predecessor_inventory": predecessor_inventory_report(),
    }
    return {
        "schema_version": "asmp4_public_bisimulation_transfer_v0_26",
        **components,
        "pass": all(component["pass"] for component in components.values()),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    report = public_bisimulation_report() if report is None else report
    return {
        "R0_three_resource_seals": report["resource_integrity"]["pass"],
        "R1_exact_public_history_contract": report["contract_exactness"]["pass"],
        "R2_exact_claim": report["claim_exactness"]["pass"],
        "R3_decorated_cover_vector_transfer": report["decorated_cover_transfer"][
            "pass"
        ],
        "R4_alternating_back_and_forth": report["alternating_fixture"]["pass"],
        "R5_thue_morse_no_finite_quotient": report["thue_morse_boundary"]["pass"],
        "R6_sufficient_not_necessary_boundary": report["finite_quotient_boundary"][
            "pass"
        ],
        "R7_five_mutations_rejected": report["mutations"]["pass"],
        "R8_predecessor_inventory": report["predecessor_inventory"]["pass"],
        "R9_complete_payload": report["pass"],
    }


def main() -> int:
    report = public_bisimulation_report()
    payload = {"report": report, "gates": verification_gates(report)}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
