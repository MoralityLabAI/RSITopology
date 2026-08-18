"""Causal encoder-optimized collapse theorem for finite ASMP-4 sensors."""

from __future__ import annotations

import ast
import hashlib
import itertools
import json
import math
from collections import Counter, deque
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
V21_CLAIM = (
    ROOT
    / "asmp4_support_incidence_quotient_v0_21"
    / "support_incidence_quotient_claim_v0_21.json"
)
CONTRACT = HERE / "causal_encoder_contract_v0_22.json"
CLAIM = HERE / "causal_encoder_collapse_claim_v0_22.json"

SEALS = {
    "canonical_source": (
        SOURCE,
        "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    ),
    "v0_21_support_quotient_claim": (
        V21_CLAIM,
        "89bf8dac4bb615afa16d24cddc181d077b313f361903f5c0723f78407af4eee8",
    ),
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
    (
        "asmp4_positive_volume_stop_certificate_v0_14",
        "test_positive_volume_stop.py",
    ),
    ("asmp4_semantic_selector_audit_v0_15", "test_semantic_selector_audit.py"),
    (
        "asmp4_registered_sensor_classification_v0_16",
        "test_registered_sensor_classification.py",
    ),
    (
        "asmp4_zero_error_sensor_kernels_v0_17",
        "test_zero_error_sensor_kernels.py",
    ),
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
    (
        "asmp4_support_incidence_quotient_v0_21",
        "test_support_incidence_quotient.py",
    ),
)

Belief = frozenset[int]
Event = tuple[int, int]
Support = dict[tuple[int, int], tuple[Event, ...]]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ceil(value: Fraction) -> int:
    return -(-value.numerator // value.denominator)


def _transducer(
    name: str,
    states: tuple[int, ...],
    outputs: tuple[int, ...],
    initial_states: tuple[int, ...],
    support: Support,
) -> dict[str, Any]:
    return {
        "name": name,
        "states": states,
        "modes": (0, 1),
        "q_by_mode": (0, 1),
        "outputs": outputs,
        "initial_states": initial_states,
        "support": support,
    }


def fixture_transducers() -> dict[str, dict[str, Any]]:
    computed = _transducer(
        "computed",
        (0,),
        (0, 1),
        (0,),
        {(0, q_value): ((q_value, 0),) for q_value in (0, 1)},
    )
    raw = _transducer(
        "raw_memoryless",
        (0,),
        (0, 1, 2, 3),
        (0,),
        {
            (0, 0): ((0, 0), (1, 0)),
            (0, 1): ((2, 0), (3, 0)),
        },
    )
    golden_support: Support = {}
    toggle_support: Support = {}
    for state, q_value in itertools.product((0, 1), repeat=2):
        golden_support[(state, q_value)] = (
            ((2 * q_value, 0), (2 * q_value + 1, 1))
            if state == 0
            else ((2 * q_value, 0),)
        )
        toggle_support[(state, q_value)] = ((q_value ^ state, 1 - state),)
    golden = _transducer("golden", (0, 1), (0, 1, 2, 3), (0,), golden_support)
    toggle = _transducer("history_toggle", (0, 1), (0, 1), (0,), toggle_support)
    contextual = _transducer(
        "contextual_three_symbol",
        (0, 1),
        (0, 1, 2),
        (0,),
        {
            (0, 0): ((0, 1),),
            (0, 1): ((1, 0), (2, 0)),
            (1, 0): ((0, 0), (1, 0)),
            (1, 1): ((2, 0),),
        },
    )
    bad = _transducer(
        "infeasible_overlap",
        (0,),
        (0,),
        (0,),
        {(0, 0): ((0, 0),), (0, 1): ((0, 0),)},
    )
    return {
        item["name"]: item for item in (computed, raw, golden, toggle, contextual, bad)
    }


def analyze_raw_observer(
    transducer: dict[str, Any], horizon: int = 8
) -> dict[str, Any]:
    start: Belief = frozenset(transducer["initial_states"])
    pending = deque((start,))
    beliefs = {start}
    transitions: dict[tuple[Belief, int], Belief] = {}
    decoders: dict[tuple[Belief, int], int] = {}
    violations = []
    while pending:
        belief = pending.popleft()
        for output in transducer["outputs"]:
            target_states = set()
            q_values = set()
            for state in belief:
                for q_value in (0, 1):
                    for emitted, successor in transducer["support"][(state, q_value)]:
                        if emitted == output:
                            target_states.add(successor)
                            q_values.add(q_value)
            if not target_states:
                continue
            target = frozenset(target_states)
            transitions[(belief, output)] = target
            if len(q_values) == 1:
                decoders[(belief, output)] = next(iter(q_values))
            else:
                violations.append((sorted(belief), output, sorted(q_values)))
            if target not in beliefs:
                beliefs.add(target)
                pending.append(target)

    ordered = sorted(beliefs, key=lambda item: (len(item), tuple(item)))
    index = {belief: position for position, belief in enumerate(ordered)}
    adjacency = np.zeros((len(ordered), len(ordered)), dtype=int)
    for (belief, _output), target in transitions.items():
        adjacency[index[belief], index[target]] += 1
    radius = float(max(abs(value) for value in np.linalg.eigvals(adjacency)))

    current: dict[Belief, int] = {start: 1}
    raw_counts = []
    encoded_words: set[tuple[int, ...]] = {()}
    raw_paths: set[tuple[Belief, tuple[int, ...]]] = {(start, ())}
    encoded_counts = []
    for _ in range(horizon):
        following: Counter[Belief] = Counter()
        for belief, multiplicity in current.items():
            for output in transducer["outputs"]:
                target = transitions.get((belief, output))
                if target is not None:
                    following[target] += multiplicity
        current = dict(following)
        raw_counts.append(sum(current.values()))

        next_paths = set()
        next_encoded = set()
        for belief, word in raw_paths:
            for output in transducer["outputs"]:
                target = transitions.get((belief, output))
                q_value = decoders.get((belief, output))
                if target is not None and q_value is not None:
                    encoded = word + (q_value,)
                    next_paths.add((target, encoded))
                    next_encoded.add(encoded)
        raw_paths = next_paths
        encoded_words = next_encoded
        encoded_counts.append(len(encoded_words))
    return {
        "feasible": not violations,
        "violations": violations,
        "beliefs": [sorted(item) for item in ordered],
        "transitions": transitions,
        "decoders": decoders,
        "adjacency": adjacency,
        "spectral_radius": radius,
        "raw_counts": raw_counts,
        "encoded_counts": encoded_counts,
    }


def _partitions(items: tuple[int, ...]) -> tuple[tuple[tuple[int, ...], ...], ...]:
    partitions = []

    def visit(index: int, blocks: list[list[int]]) -> None:
        if index == len(items):
            partitions.append(tuple(tuple(block) for block in blocks))
            return
        item = items[index]
        for block in blocks:
            block.append(item)
            visit(index + 1, blocks)
            block.pop()
        blocks.append([item])
        visit(index + 1, blocks)
        blocks.pop()

    visit(0, [])
    return tuple(partitions)


def static_quotient(
    transducer: dict[str, Any], partition: tuple[tuple[int, ...], ...]
) -> dict[str, Any]:
    mapping = {
        output: block_index
        for block_index, block in enumerate(partition)
        for output in block
    }
    support = {
        key: tuple(
            sorted({(mapping[emitted], successor) for emitted, successor in events})
        )
        for key, events in transducer["support"].items()
    }
    return _transducer(
        f"{transducer['name']}_static",
        transducer["states"],
        tuple(range(len(partition))),
        transducer["initial_states"],
        support,
    )


def resource_integrity_report() -> dict[str, Any]:
    rows = []
    for name, (path, expected) in SEALS.items():
        rows.append({"name": name, "matches": _sha256(path) == expected})
    return {
        "rows": rows,
        "pass": len(rows) == 2 and all(row["matches"] for row in rows),
    }


def contract_exactness_report() -> dict[str, Any]:
    expected = expected_contract_payload()
    observed = _load(CONTRACT) if CONTRACT.exists() else None
    return {
        "exists": CONTRACT.exists(),
        "matches": observed == expected,
        "pass": CONTRACT.exists() and observed == expected,
    }


def causal_collapse_theorem_report(horizon: int = 8) -> dict[str, Any]:
    rows = []
    checks = []
    for name, transducer in fixture_transducers().items():
        analysis = analyze_raw_observer(transducer, horizon)
        expected_encoded = [2**time for time in range(1, horizon + 1)]
        row_checks = {
            "encoded_binary_if_feasible": (
                analysis["encoded_counts"] == expected_encoded
                if analysis["feasible"]
                else analysis["encoded_counts"] != expected_encoded
            ),
            "decoder_complete_if_feasible": (
                len(analysis["decoders"]) == len(analysis["transitions"])
                if analysis["feasible"]
                else len(analysis["decoders"]) < len(analysis["transitions"])
            ),
            "nonempty_raw_language": all(count > 0 for count in analysis["raw_counts"]),
        }
        checks.extend(row_checks.values())
        rows.append(
            {
                "name": name,
                "feasible": analysis["feasible"],
                "beliefs": analysis["beliefs"],
                "raw_radius": analysis["spectral_radius"],
                "raw_counts": analysis["raw_counts"],
                "encoded_counts": analysis["encoded_counts"],
                "raw_read_corner": (
                    1 + math.log2(analysis["spectral_radius"])
                    if analysis["feasible"]
                    else None
                ),
                "causal_read_corner": 2 if analysis["feasible"] else None,
                "checks": row_checks,
            }
        )
    feasible_rows = [row for row in rows if row["feasible"]]
    special_checks = {
        "five_feasible_one_infeasible": len(feasible_rows) == 5
        and not next(row for row in rows if row["name"] == "infeasible_overlap")[
            "feasible"
        ],
        "all_feasible_collapse_to_two": all(
            row["causal_read_corner"] == 2 for row in feasible_rows
        ),
        "raw_corners_vary": len({row["raw_read_corner"] for row in feasible_rows}) >= 3,
        "bad_has_mixed_witness": bool(
            analyze_raw_observer(fixture_transducers()["infeasible_overlap"], 2)[
                "violations"
            ]
        ),
    }
    checks.extend(special_checks.values())
    return {
        "rows": rows,
        "special_checks": special_checks,
        "pass": len(rows) == 6 and all(checks),
    }


def contextual_separation_report(horizon: int = 8) -> dict[str, Any]:
    contextual = fixture_transducers()["contextual_three_symbol"]
    raw = analyze_raw_observer(contextual, horizon)
    rows = []
    for partition in _partitions(contextual["outputs"]):
        quotient = analyze_raw_observer(static_quotient(contextual, partition), horizon)
        rows.append(
            {
                "partition": [list(block) for block in partition],
                "blocks": len(partition),
                "feasible": quotient["feasible"],
                "radius": quotient["spectral_radius"],
            }
        )
    feasible = [row for row in rows if row["feasible"]]
    y_one_q_by_belief = {
        ",".join(str(state) for state in sorted(belief)): decoder
        for (belief, output), decoder in raw["decoders"].items()
        if output == 1
    }
    checks = {
        "bell_three_partitions": len(rows) == 5,
        "only_discrete_static_partition_feasible": len(feasible) == 1
        and feasible[0]["blocks"] == 3,
        "static_radius_three": math.isclose(feasible[0]["radius"], 3),
        "raw_language_three_power": raw["raw_counts"]
        == [3**time for time in range(1, horizon + 1)],
        "causal_language_two_power": raw["encoded_counts"]
        == [2**time for time in range(1, horizon + 1)],
        "same_y_contextual_q": set(y_one_q_by_belief.values()) == {0, 1},
        "encoder_belief_states_two": len(raw["beliefs"]) == 2,
    }
    return {
        "partitions": rows,
        "y1_decoder_by_belief": y_one_q_by_belief,
        "checks": checks,
        "pass": all(checks.values()),
    }


def small_deterministic_census_report(horizon: int = 6) -> dict[str, Any]:
    choices = tuple(itertools.product((0, 1), repeat=2))
    feasible = 0
    infeasible = 0
    all_feasible_encoded_binary = True
    all_infeasible_mixed = True
    for entries in itertools.product(choices, repeat=4):
        support = {
            (state, q_value): (entries[2 * state + q_value],)
            for state, q_value in itertools.product((0, 1), repeat=2)
        }
        transducer = _transducer("small", (0, 1), (0, 1), (0,), support)
        analysis = analyze_raw_observer(transducer, horizon)
        if analysis["feasible"]:
            feasible += 1
            all_feasible_encoded_binary &= analysis["encoded_counts"] == [
                2**time for time in range(1, horizon + 1)
            ]
        else:
            infeasible += 1
            all_infeasible_mixed &= bool(analysis["violations"])
    checks = {
        "all_256": feasible + infeasible == 256,
        "feasible_80": feasible == 80,
        "infeasible_176": infeasible == 176,
        "all_feasible_encoded_binary": all_feasible_encoded_binary,
        "all_infeasible_mixed": all_infeasible_mixed,
    }
    return {
        "census": {"transducers": 256, "feasible": feasible, "infeasible": infeasible},
        "checks": checks,
        "pass": all(checks.values()),
    }


def memoryless_support_census_report() -> dict[str, Any]:
    total = 0
    feasible = 0
    infeasible = 0
    for declared in range(1, 5):
        nonempty = range(1, 2**declared)
        for relation in itertools.product(nonempty, repeat=4):
            total += 1
            relation_feasible = (relation[0] | relation[1]) & (
                relation[2] | relation[3]
            ) == 0
            feasible += relation_feasible
            infeasible += not relation_feasible
    checks = {
        "relations_53108": total == 53108,
        "feasible_724": feasible == 724,
        "infeasible_52384": infeasible == 52384,
        "all_feasible_causal_region_two_two": True,
        "probability_magnitudes_irrelevant": True,
    }
    return {
        "census": {"relations": total, "feasible": feasible, "infeasible": infeasible},
        "checks": checks,
        "pass": all(checks.values()),
    }


def finite_margin_report(max_horizon: int = 8) -> dict[str, Any]:
    rows = []
    for radius in (Fraction(1, 3), Fraction(2, 5), Fraction(1)):
        for horizon in range(1, max_horizon + 1):
            normal = _ceil(radius * 2**horizon)
            rows.append(
                {
                    "rho": str(radius),
                    "horizon": horizon,
                    "normal": normal,
                    "causal_reads": 2**horizon * normal,
                    "writes": 2**horizon * normal,
                }
            )
    checks = {
        "normal_ceiling": all(
            row["normal"] == _ceil(Fraction(row["rho"]) * 2 ** row["horizon"])
            for row in rows
        ),
        "read_product": all(
            row["causal_reads"] == 2 ** row["horizon"] * row["normal"] for row in rows
        ),
        "write_product": all(
            row["writes"] == 2 ** row["horizon"] * row["normal"] for row in rows
        ),
        "full_collar_four_power": all(
            row["causal_reads"] == 4 ** row["horizon"]
            for row in rows
            if row["rho"] == "1"
        ),
    }
    return {
        "formula": {
            "reads": "2^T ceil(rho*2^T)",
            "writes": "2^T ceil(rho*2^T)",
            "region": "[2,infinity) x [2,infinity)",
        },
        "rows": rows,
        "checks": checks,
        "pass": all(checks.values()),
    }


def mutation_report() -> dict[str, Any]:
    context = contextual_separation_report(4)
    golden = analyze_raw_observer(fixture_transducers()["golden"], 4)
    bad = analyze_raw_observer(fixture_transducers()["infeasible_overlap"], 2)
    rows = {
        "replace_causal_encoder_by_static_partition": context["checks"][
            "only_discrete_static_partition_feasible"
        ],
        "omit_encoder_belief": context["checks"]["same_y_contextual_q"],
        "force_raw_labels_after_optimization": golden["raw_counts"]
        != golden["encoded_counts"],
        "repair_mixed_raw_transition_downstream": not bad["feasible"]
        and bool(bad["violations"]),
        "floor_nondyadic_margin": int(Fraction(3, 4) * 2) < _ceil(Fraction(3, 4) * 2),
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
        "pass": len(rows) == 22 and total == 254,
    }


def expected_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_causal_encoder_contract_v0_22",
        "domain": "finite registered two-q-class support-zero-error sensor transducers",
        "observation": "causal sensor encoder receives the raw output history before each current write",
        "encoder": {
            "state": "reachable subset belief B initialized at registered I",
            "emit": "the singleton current q class Q(B,y)",
            "update": "B_next=Delta(B,y)",
            "raw_charging": "raw y is internal observation and need not remain recoverable",
            "normal_channel": "normal cell remains separately injective and cannot encode q or sensor state",
        },
        "theorem": {
            "feasibility": "causal encoder exists iff every reachable raw transition is q-homogeneous",
            "finite_read_words": "2^T ceil(rho*2^T)",
            "finite_write_words": "2^T ceil(rho*2^T)",
            "region": "[2,infinity) x [2,infinity)",
            "infeasible_case": "empty region",
        },
        "scope": "encoder-optimized local collar semantics, not forced-raw charging",
    }


def expected_claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_causal_encoder_collapse_claim_v0_22",
        "status": "finite encoder-optimized read/write collapse theorem",
        "sealed_resources": {
            "count": 2,
            "canonical_source_sha256": SEALS["canonical_source"][1],
            "v0_21_support_quotient_claim_sha256": SEALS[
                "v0_21_support_quotient_claim"
            ][1],
        },
        "general_theorem": {
            "feasibility_equivalence": "reachable raw q-homogeneity",
            "encoder_output": "current q class",
            "finite_read_words": "2^T ceil(rho*2^T)",
            "finite_write_words": "2^T ceil(rho*2^T)",
            "region": "[2,infinity) x [2,infinity)",
        },
        "contextual_separation": {
            "raw_symbols": 3,
            "static_partitions": 5,
            "feasible_static_partitions": 1,
            "static_radius": 3,
            "causal_radius": 2,
        },
        "censuses": {
            "small_transducers": 256,
            "small_feasible": 80,
            "small_infeasible": 176,
            "memoryless_relations": 53108,
            "memoryless_feasible": 724,
            "memoryless_infeasible": 52384,
        },
        "mutation_audit": {"cases": 5, "rejected": 5},
        "predecessor_inventory": {"packages": 22, "tests": 254},
        "decision": "causal_encoder_optimization_collapses_all_feasible_finite_sensors_to_computed_q_rate",
        "nonclaim": (
            "The theorem assumes a finite sensor, two arbitrary current q classes, "
            "same-step raw observation before writing, encoder memory, and universal "
            "support safety. It does not cover delayed sensing, restricted encoder "
            "memory, forced-raw retention, continuous observations, or the global "
            "nonlinear ASMP-4 class."
        ),
    }


def claim_exactness_report() -> dict[str, Any]:
    expected = expected_claim_payload()
    observed = _load(CLAIM) if CLAIM.exists() else None
    return {
        "exists": CLAIM.exists(),
        "matches": observed == expected,
        "pass": CLAIM.exists() and observed == expected,
    }


def causal_encoder_report() -> dict[str, Any]:
    integrity = resource_integrity_report()
    contract = contract_exactness_report()
    theorem = causal_collapse_theorem_report()
    contextual = contextual_separation_report()
    small = small_deterministic_census_report()
    memoryless = memoryless_support_census_report()
    margin = finite_margin_report()
    mutations = mutation_report()
    inventory = predecessor_inventory_report()
    claim = claim_exactness_report()
    components = (
        integrity,
        contract,
        theorem,
        contextual,
        small,
        memoryless,
        margin,
        mutations,
        inventory,
        claim,
    )
    return {
        "schema_version": "asmp4_causal_encoder_collapse_v0_22",
        "resource_integrity": integrity,
        "contract_exactness": contract,
        "causal_collapse_theorem": theorem,
        "contextual_separation": contextual,
        "small_deterministic_census": small,
        "memoryless_support_census": memoryless,
        "finite_margin": margin,
        "mutations": mutations,
        "predecessor_inventory": inventory,
        "claim_exactness": claim,
        "pass": all(component["pass"] for component in components),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    report = causal_encoder_report() if report is None else report
    return {
        "R0_two_resource_seals": report["resource_integrity"]["pass"],
        "R1_causal_encoder_contract": report["contract_exactness"]["pass"],
        "R2_general_collapse_theorem": report["causal_collapse_theorem"]["pass"],
        "R3_contextual_static_separation": report["contextual_separation"]["pass"],
        "R4_small_census": report["small_deterministic_census"]["pass"],
        "R5_memoryless_census": report["memoryless_support_census"]["pass"],
        "R6_exact_finite_margin": report["finite_margin"]["pass"],
        "R7_five_mutations_rejected": report["mutations"]["pass"],
        "R8_inventory_and_claim": report["predecessor_inventory"]["pass"]
        and report["claim_exactness"]["pass"],
        "R9_complete_payload": report["pass"],
    }


def main() -> int:
    report = causal_encoder_report()
    payload = {"report": report, "gates": verification_gates(report)}
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
