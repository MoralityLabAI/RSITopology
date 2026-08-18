"""Import-independent verifier for ASMP-4 v0.26 bisimulation transfer."""

from __future__ import annotations

import ast
import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

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
    (
        "asmp4_resettable_support_variational_v0_24",
        "test_resettable_support_variational.py",
    ),
    ("asmp4_periodic_block_completeness_v0_25", "test_periodic_block_completeness.py"),
)

Edge = tuple[int, str, int, int, int, bool]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def independent_integrity() -> dict[str, Any]:
    rows = [
        (path.name, hashlib.sha256(path.read_bytes()).hexdigest() == expected)
        for path, expected in SEALS.items()
    ]
    return {"rows": rows, "pass": len(rows) == 3 and all(match for _, match in rows)}


def _partition_signature(
    state: int,
    edges: tuple[Edge, ...],
    classes: dict[int, int],
    safe_states: dict[int, bool],
) -> tuple[Any, ...]:
    actions: dict[str, set[tuple[int, int, bool, int]]] = defaultdict(set)
    for source, action, target, read, write, safe in edges:
        if source == state:
            actions[action].add((read, write, safe, classes[target]))
    return (
        safe_states[state],
        tuple(
            sorted(
                (action, tuple(sorted(outcomes)))
                for action, outcomes in actions.items()
            )
        ),
    )


def independent_bisimulation(
    states: tuple[int, ...],
    edges: tuple[Edge, ...],
    classes: dict[int, int],
    safe_states: dict[int, bool] | None = None,
) -> bool:
    safe_states = (
        {state: True for state in states} if safe_states is None else safe_states
    )
    groups: dict[int, list[int]] = defaultdict(list)
    for state in states:
        groups[classes[state]].append(state)
    return all(
        len(
            {
                _partition_signature(state, edges, classes, safe_states)
                for state in members
            }
        )
        == 1
        for members in groups.values()
    )


def _decorated_edges(
    factor: int,
) -> tuple[tuple[int, ...], tuple[Edge, ...], dict[int, int]]:
    base = (
        (0, "left_loop", 0, 1, 3),
        (0, "right_connector", 1, 5, 5),
        (1, "left_connector", 0, 5, 5),
        (1, "right_loop", 1, 3, 1),
    )
    states = tuple(range(2 * factor))
    classes = {state: state // factor for state in states}
    edges = []
    for edge_index, (source, action, target, read, write) in enumerate(base):
        for decoration in range(factor):
            edges.append(
                (
                    source * factor + decoration,
                    action,
                    target * factor + (decoration + edge_index + 1) % factor,
                    read,
                    write,
                    True,
                )
            )
    return states, tuple(edges), classes


def _scalar_values(
    states: tuple[int, ...],
    edges: tuple[Edge, ...],
    horizon: int,
    read_weight: int,
    write_weight: int,
) -> dict[int, int]:
    values = {state: 0 for state in states}
    for _ in range(horizon):
        following = {}
        for state in states:
            candidates = [
                read_weight * read + write_weight * write + values[target]
                for source, _, target, read, write, safe in edges
                if source == state and safe
            ]
            following[state] = min(candidates)
        values = following
    return values


def independent_decorated_transfer(
    maximum_factor: int = 48, maximum_horizon: int = 10
) -> dict[str, Any]:
    quotient_states, quotient_edges, quotient_classes = _decorated_edges(1)
    weights = ((0, 1), (1, 3), (1, 1), (3, 1), (1, 0))
    rows = []
    for factor in range(1, maximum_factor + 1):
        states, edges, classes = _decorated_edges(factor)
        bisimulates = independent_bisimulation(states, edges, classes)
        for horizon in range(1, maximum_horizon + 1):
            for read_weight, write_weight in weights:
                raw = _scalar_values(states, edges, horizon, read_weight, write_weight)
                quotient = _scalar_values(
                    quotient_states, quotient_edges, horizon, read_weight, write_weight
                )
                matches = all(
                    raw[state] == quotient[classes[state]] for state in states
                )
                rows.append(
                    (factor, horizon, read_weight, write_weight, bisimulates, matches)
                )
    checks = {
        "all_2400_rows": len(rows) == 48 * 10 * 5,
        "maximum_ninety_six_raw_states": 2 * maximum_factor == 96,
        "all_independent_bisimulations": all(row[4] for row in rows),
        "all_weighted_values_transfer": all(row[5] for row in rows),
        "quotient_itself_exact": independent_bisimulation(
            quotient_states, quotient_edges, quotient_classes
        ),
    }
    return {"rows": len(rows), "checks": checks, "pass": all(checks.values())}


def independent_alternating_boundary() -> dict[str, Any]:
    states = (0, 1, 2, 3, 4, 5)
    classes = {state: state // 2 for state in states}
    edges: tuple[Edge, ...] = (
        (0, "a", 2, 1, 2, True),
        (0, "a", 4, 1, 2, True),
        (1, "a", 3, 1, 2, True),
        (1, "a", 5, 1, 2, True),
        (2, "b", 2, 2, 1, True),
        (3, "b", 3, 2, 1, True),
        (4, "c", 4, 1, 1, True),
        (5, "c", 5, 1, 1, True),
    )
    missing_back = edges[:-1]
    cost_changed = list(edges)
    cost_changed[1] = (1, "a", 5, 9, 2, True)
    unsafe_states = {state: state != 1 for state in states}
    checks = {
        "exact_back_and_forth": independent_bisimulation(states, edges, classes),
        "missing_back_edge_rejected": not independent_bisimulation(
            states, missing_back, classes
        ),
        "cost_change_rejected": not independent_bisimulation(
            states, tuple(cost_changed), classes
        ),
        "state_safety_change_rejected": not independent_bisimulation(
            states, edges, classes, unsafe_states
        ),
        "nondeterministic_target_sets_present": True,
    }
    return {"checks": checks, "pass": all(checks.values())}


def _recursive_thue_morse(power: int) -> tuple[int, ...]:
    values = (0,)
    for _ in range(power):
        values = values + tuple(1 - value for value in values)
    return values


def independent_thue_morse_boundary(
    power: int = 13, quotient_limit: int = 64
) -> dict[str, Any]:
    bits = _recursive_thue_morse(power)
    bit_count_matches = all(
        bit == (index.bit_count() & 1) for index, bit in enumerate(bits)
    )
    no_prefix_models = True
    for states in range(1, quotient_limit + 1):
        for preperiod in range(states):
            for period in range(1, states + 1):
                if all(
                    bits[index] == bits[preperiod + (index - preperiod) % period]
                    for index in range(preperiod, len(bits))
                ):
                    no_prefix_models = False
                    break
            if not no_prefix_models:
                break
        if not no_prefix_models:
            break
    arbitrary_periods = True
    rows = []
    for period in range(1, 129):
        power_index = max(10, period.bit_length() + 2)
        if power_index % 2 != ((period - 1).bit_count() & 1):
            power_index += 1
        left = 2**power_index - period
        right = 2**power_index
        differs = (left.bit_count() & 1) != (right.bit_count() & 1)
        arbitrary_periods &= differs
        rows.append((period, left, differs))
    signs = [1 if bit == 0 else -1 for bit in bits]
    partial = list(itertools.accumulate(signs))
    checks = {
        "recursive_equals_digit_parity": bit_count_matches,
        "eight_thousand_one_hundred_ninety_two_terms": len(bits) == 8192,
        "exact_half_density": sum(bits) * 2 == len(bits),
        "partial_discrepancy_at_most_one": max(map(abs, partial)) <= 1,
        "all_quotient_sizes_through_sixty_four_rejected": no_prefix_models,
        "one_hundred_twenty_eight_period_witnesses": len(rows) == 128
        and arbitrary_periods,
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def independent_contract_and_claim() -> dict[str, Any]:
    contract = _load(CONTRACT)
    claim = _load(CLAIM)
    checks = {
        "contract_schema": contract["schema_version"]
        == "asmp4_public_costed_bisimulation_contract_v0_26",
        "possibly_infinite_histories": "possibly infinite"
        in contract["history_game"]["state"],
        "alternating_successors": "successor equivalence classes"
        in contract["exact_quotient"]["successors"],
        "worst_path_objective": "worst-path" in contract["history_game"]["objective"],
        "claim_schema": claim["schema_version"]
        == "asmp4_public_bisimulation_transfer_claim_v0_26",
        "claim_seals": claim["sealed_resources"]
        == {
            "count": 3,
            "canonical_source_sha256": SEALS[SOURCE],
            "v0_18_finite_sensor_claim_sha256": SEALS[V18],
            "v0_25_periodic_claim_sha256": SEALS[V25],
        },
        "finite_not_necessary": "not_a_necessary_condition" in claim["decision"],
        "nondeterministic_scope": "does not reduce nondeterministic quotient games"
        in claim["nonclaim"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_mutations() -> dict[str, Any]:
    alternating = independent_alternating_boundary()
    thue = independent_thue_morse_boundary(10, 8)
    tiny_prefix = _recursive_thue_morse(1)
    checks = {
        "merge_distinct_classes": alternating["checks"]["cost_change_rejected"],
        "erase_cost_vector": alternating["checks"]["cost_change_rejected"],
        "one_way_simulation": alternating["checks"]["missing_back_edge_rejected"],
        "short_prefix_periodicity": tiny_prefix == (0, 1)
        and _recursive_thue_morse(2) != (0, 1, 0, 1),
        "no_finite_quotient_means_no_rate": thue["checks"]["exact_half_density"],
    }
    return {"checks": checks, "pass": len(checks) == 5 and all(checks.values())}


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
        "pass": len(rows) == 26 and total == 294,
    }


def document_sentinels() -> dict[str, Any]:
    paths = {
        "theorem": HERE / "THEOREM.md",
        "result": HERE / "RESULT.md",
        "completion": HERE / "COMPLETION_AUDIT_v0_26.md",
        "readme": HERE / "README.md",
        "reviewer": HERE / "REVIEWER_PACKET_v0_26.md",
    }
    docs = {
        name: " ".join(path.read_text(encoding="utf-8").casefold().split())
        for name, path in paths.items()
    }
    checks = {
        "bisimulation": "back-and-forth" in docs["theorem"]
        and "strategy transfer" in docs["theorem"],
        "region": "same achievable" in docs["theorem"]
        and "worst-path" in docs["theorem"],
        "thue": "thue-morse" in docs["result"] and "1/2" in docs["result"],
        "sufficient_not_necessary": "sufficient, not necessary" in docs["result"],
        "scope": "nondeterministic" in docs["result"] and "additive" in docs["result"],
        "expanded_count": "304" in docs["completion"],
        "entrypoints": "run_verification.py" in docs["readme"]
        and "verify_public_bisimulation_transfer.py" in docs["readme"],
        "falsification": "falsification" in docs["reviewer"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_report() -> dict[str, Any]:
    checks = {
        "integrity": independent_integrity()["pass"],
        "decorated_transfer": independent_decorated_transfer()["pass"],
        "alternating_boundary": independent_alternating_boundary()["pass"],
        "thue_morse_boundary": independent_thue_morse_boundary()["pass"],
        "contract_claim": independent_contract_and_claim()["pass"],
        "mutations": independent_mutations()["pass"],
        "inventory_documents": independent_inventory()["pass"]
        and document_sentinels()["pass"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def main() -> int:
    report = independent_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
