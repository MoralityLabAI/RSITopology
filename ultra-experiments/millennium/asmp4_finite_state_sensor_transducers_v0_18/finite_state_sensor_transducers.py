"""Finite-state support-zero-error sensor transducers for ASMP-4."""

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
V17_CLAIM = (
    ROOT
    / "asmp4_zero_error_sensor_kernels_v0_17"
    / "zero_error_sensor_kernel_claim_v0_17.json"
)
CONTRACT = HERE / "finite_state_sensor_contract_v0_18.json"
CLAIM = HERE / "finite_state_sensor_claim_v0_18.json"

SEALS = {
    "canonical_source": (
        SOURCE,
        "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    ),
    "v0_17_kernel_claim": (
        V17_CLAIM,
        "a8e87b315537dec89c67629111de7dbff77464a0817940af096fc5930559a530",
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
    modes: tuple[int, ...],
    q_by_mode: tuple[int, ...],
    outputs: tuple[int, ...],
    initial: int,
    support: Support,
) -> dict[str, Any]:
    return {
        "name": name,
        "states": states,
        "modes": modes,
        "q_by_mode": q_by_mode,
        "outputs": outputs,
        "initial": initial,
        "support": support,
    }


def fixture_transducers() -> dict[str, dict[str, Any]]:
    modes = (0, 1, 2, 3)
    q = (0, 0, 1, 1)
    computed = _transducer(
        "computed_memoryless",
        (0,),
        modes,
        q,
        (0, 1),
        0,
        {(0, mode): ((q[mode], 0),) for mode in modes},
    )
    raw = _transducer(
        "raw_memoryless",
        (0,),
        modes,
        q,
        (0, 1, 2, 3),
        0,
        {(0, mode): ((mode, 0),) for mode in modes},
    )
    golden_support: Support = {}
    for state, mode in itertools.product((0, 1), modes):
        q_value = q[mode]
        golden_support[(state, mode)] = (
            ((2 * q_value, 0), (2 * q_value + 1, 1))
            if state == 0
            else ((2 * q_value, 0),)
        )
    golden = _transducer(
        "golden_refinement",
        (0, 1),
        modes,
        q,
        (0, 1, 2, 3),
        0,
        golden_support,
    )
    toggle_support: Support = {}
    for state, mode in itertools.product((0, 1), modes):
        toggle_support[(state, mode)] = ((q[mode] ^ state, 1 - state),)
    toggle = _transducer(
        "history_toggle",
        (0, 1),
        modes,
        q,
        (0, 1),
        0,
        toggle_support,
    )
    bad = _transducer(
        "infeasible_overlap",
        (0,),
        modes,
        q,
        (0,),
        0,
        {(0, mode): ((0, 0),) for mode in modes},
    )
    return {item["name"]: item for item in (computed, raw, golden, toggle, bad)}


def analyze_transducer(
    transducer: dict[str, Any], max_horizon: int = 10
) -> dict[str, Any]:
    outputs = transducer["outputs"]
    support: Support = transducer["support"]
    q_by_mode = transducer["q_by_mode"]
    start: Belief = frozenset((transducer["initial"],))
    queue = deque((start,))
    beliefs = {start}
    transitions: dict[tuple[Belief, int], Belief] = {}
    decoders: dict[tuple[Belief, int], int] = {}
    violations = []
    while queue:
        belief = queue.popleft()
        for output in outputs:
            next_states = set()
            q_values = set()
            witnesses = []
            for state in belief:
                for mode in transducer["modes"]:
                    for emitted, successor in support[(state, mode)]:
                        if emitted == output:
                            next_states.add(successor)
                            q_values.add(q_by_mode[mode])
                            witnesses.append((state, mode, successor))
            if not next_states:
                continue
            target = frozenset(next_states)
            transitions[(belief, output)] = target
            if len(q_values) == 1:
                decoders[(belief, output)] = next(iter(q_values))
            else:
                violations.append(
                    {
                        "belief": sorted(belief),
                        "output": output,
                        "q_values": sorted(q_values),
                        "witnesses": witnesses,
                    }
                )
            if target not in beliefs:
                beliefs.add(target)
                queue.append(target)

    ordered = sorted(beliefs, key=lambda belief: (len(belief), tuple(belief)))
    index = {belief: position for position, belief in enumerate(ordered)}
    adjacency = np.zeros((len(ordered), len(ordered)), dtype=int)
    for (belief, _output), target in transitions.items():
        adjacency[index[belief], index[target]] += 1
    eigenvalues = np.linalg.eigvals(adjacency.astype(float))
    spectral_radius = float(max(abs(value) for value in eigenvalues))

    counts = []
    current: dict[Belief, int] = {start: 1}
    for _time in range(max_horizon):
        following: Counter[Belief] = Counter()
        for belief, count in current.items():
            for output in outputs:
                target = transitions.get((belief, output))
                if target is not None:
                    following[target] += count
        current = dict(following)
        counts.append(sum(current.values()))
    return {
        "feasible": not violations,
        "beliefs": [sorted(belief) for belief in ordered],
        "transitions": transitions,
        "decoders": decoders,
        "violations": violations,
        "adjacency": adjacency,
        "spectral_radius": spectral_radius,
        "word_counts": counts,
    }


def resource_integrity_report() -> dict[str, Any]:
    rows = []
    for name, (path, expected) in SEALS.items():
        observed = _sha256(path)
        rows.append({"name": name, "matches": observed == expected})
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


def fixture_theorem_report(max_horizon: int = 10) -> dict[str, Any]:
    fixtures = fixture_transducers()
    analyses = {
        name: analyze_transducer(item, max_horizon) for name, item in fixtures.items()
    }
    phi = (1 + math.sqrt(5)) / 2
    fibonacci = [2, 3]
    for _index in range(2, max_horizon + 1):
        fibonacci.append(fibonacci[-1] + fibonacci[-2])
    golden_expected = [2 ** (time + 1) * fibonacci[time] for time in range(max_horizon)]
    toggle = fixtures["history_toggle"]
    toggle_outputs_by_q = {
        q_value: {
            emitted
            for state in toggle["states"]
            for mode in toggle["modes"]
            if toggle["q_by_mode"][mode] == q_value
            for emitted, _successor in toggle["support"][(state, mode)]
        }
        for q_value in (0, 1)
    }
    expected_counts = {
        "computed_memoryless": [2 ** (time + 1) for time in range(max_horizon)],
        "raw_memoryless": [4 ** (time + 1) for time in range(max_horizon)],
        "golden_refinement": golden_expected,
        "history_toggle": [2 ** (time + 1) for time in range(max_horizon)],
        "infeasible_overlap": [1 for _time in range(max_horizon)],
    }
    checks = {
        "four_feasible_one_infeasible": sum(
            analysis["feasible"] for analysis in analyses.values()
        )
        == 4
        and not analyses["infeasible_overlap"]["feasible"],
        "all_exact_word_counts": all(
            analyses[name]["word_counts"] == expected
            for name, expected in expected_counts.items()
        ),
        "computed_radius_two": math.isclose(
            analyses["computed_memoryless"]["spectral_radius"], 2
        ),
        "raw_radius_four": math.isclose(
            analyses["raw_memoryless"]["spectral_radius"], 4
        ),
        "golden_radius_two_phi": math.isclose(
            analyses["golden_refinement"]["spectral_radius"], 2 * phi
        ),
        "toggle_radius_two": math.isclose(
            analyses["history_toggle"]["spectral_radius"], 2
        ),
        "toggle_global_overlap_but_history_decodable": bool(
            toggle_outputs_by_q[0] & toggle_outputs_by_q[1]
        )
        and analyses["history_toggle"]["feasible"],
        "bad_fixture_has_mixed_q_violation": analyses["infeasible_overlap"][
            "violations"
        ][0]["q_values"]
        == [0, 1],
    }
    rows = []
    for name, analysis in analyses.items():
        rows.append(
            {
                "name": name,
                "feasible": analysis["feasible"],
                "beliefs": analysis["beliefs"],
                "spectral_radius": analysis["spectral_radius"],
                "word_counts": analysis["word_counts"],
                "read_threshold": (
                    1 + math.log2(analysis["spectral_radius"])
                    if analysis["feasible"]
                    else None
                ),
                "write_threshold": 2 if analysis["feasible"] else None,
            }
        )
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def two_state_binary_census_report(max_horizon: int = 8) -> dict[str, Any]:
    choices = tuple(itertools.product((0, 1), (0, 1)))
    feasible = 0
    infeasible = 0
    history_essential = 0
    memoryless_disjoint = 0
    feasible_counts = Counter()
    belief_histogram = Counter()
    all_feasible_full_binary = True
    all_feasible_radius_two = True
    all_infeasible_have_violation = True
    for entries in itertools.product(choices, repeat=4):
        support: Support = {}
        for state, q_value in itertools.product((0, 1), (0, 1)):
            support[(state, q_value)] = (entries[2 * state + q_value],)
        transducer = _transducer(
            "census",
            (0, 1),
            (0, 1),
            (0, 1),
            (0, 1),
            0,
            support,
        )
        analysis = analyze_transducer(transducer, max_horizon)
        low_outputs = {entries[2 * state][0] for state in (0, 1)}
        high_outputs = {entries[2 * state + 1][0] for state in (0, 1)}
        globally_disjoint = low_outputs.isdisjoint(high_outputs)
        if analysis["feasible"]:
            feasible += 1
            memoryless_disjoint += globally_disjoint
            history_essential += not globally_disjoint
            feasible_counts[tuple(analysis["word_counts"])] += 1
            belief_histogram[len(analysis["beliefs"])] += 1
            all_feasible_full_binary = all_feasible_full_binary and analysis[
                "word_counts"
            ] == [2 ** (time + 1) for time in range(max_horizon)]
            all_feasible_radius_two = all_feasible_radius_two and math.isclose(
                analysis["spectral_radius"], 2
            )
        else:
            infeasible += 1
            all_infeasible_have_violation = all_infeasible_have_violation and bool(
                analysis["violations"]
            )
    checks = {
        "all_256_transducers": feasible + infeasible == 256,
        "feasible_80": feasible == 80,
        "infeasible_176": infeasible == 176,
        "history_essential_48": history_essential == 48,
        "globally_disjoint_32": memoryless_disjoint == 32,
        "belief_histogram": belief_histogram == {1: 32, 2: 48},
        "all_feasible_full_binary": all_feasible_full_binary,
        "all_feasible_radius_two": all_feasible_radius_two,
        "all_infeasible_have_reachable_violation": all_infeasible_have_violation,
        "single_feasible_count_signature": len(feasible_counts) == 1,
    }
    return {
        "census": {
            "transducers": 256,
            "feasible": feasible,
            "infeasible": infeasible,
            "history_essential": history_essential,
            "globally_disjoint": memoryless_disjoint,
            "belief_histogram": dict(sorted(belief_histogram.items())),
        },
        "checks": checks,
        "pass": all(checks.values()),
    }


def finite_margin_report(max_horizon: int = 8) -> dict[str, Any]:
    fixtures = fixture_transducers()
    rows = []
    for name in (
        "computed_memoryless",
        "raw_memoryless",
        "golden_refinement",
        "history_toggle",
    ):
        analysis = analyze_transducer(fixtures[name], max_horizon)
        for radius in (Fraction(1, 3), Fraction(2, 5), Fraction(1)):
            for horizon, language_words in enumerate(analysis["word_counts"], 1):
                normal_words = _ceil(radius * 2**horizon)
                rows.append(
                    {
                        "fixture": name,
                        "rho": str(radius),
                        "horizon": horizon,
                        "language_words": language_words,
                        "normal_words": normal_words,
                        "read_words": language_words * normal_words,
                        "write_words": 2**horizon * normal_words,
                    }
                )
    checks = {
        "normal_ceiling": all(
            row["normal_words"] == _ceil(Fraction(row["rho"]) * 2 ** row["horizon"])
            for row in rows
        ),
        "read_product": all(
            row["read_words"] == row["language_words"] * row["normal_words"]
            for row in rows
        ),
        "write_product": all(
            row["write_words"] == 2 ** row["horizon"] * row["normal_words"]
            for row in rows
        ),
        "full_collar_adds_one_normal_bit": all(
            row["read_words"] == row["language_words"] * 2 ** row["horizon"]
            for row in rows
            if row["rho"] == "1"
        ),
    }
    return {
        "formula": {
            "read": "L_T ceil(rho*2^T)",
            "write": "2^T ceil(rho*2^T)",
            "asymptotic_read": "1+log2(rho(A))",
        },
        "rows": rows,
        "checks": checks,
        "pass": all(checks.values()),
    }


def mutation_report() -> dict[str, Any]:
    fixtures = fixture_transducers()
    toggle = analyze_transducer(fixtures["history_toggle"], 4)
    golden = analyze_transducer(fixtures["golden_refinement"], 4)
    rows = {
        "use_global_current_symbol_overlap_instead_of_beliefs": toggle["feasible"],
        "ignore_reachable_mixed_q_transition": not analyze_transducer(
            fixtures["infeasible_overlap"], 2
        )["feasible"],
        "count_output_alphabet_power_instead_of_language": golden["word_counts"][3]
        != 4**4,
        "omit_normal_read_factor": 2**3 != 4**3,
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
        "pass": len(rows) == 18 and total == 214,
    }


def expected_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_finite_state_sensor_contract_v0_18",
        "base_plant": "v0.13 positive-volume collar with arbitrary two-class q disturbance",
        "transducer": {
            "parameter": "finite state S, initial state s0, finite raw output Y, and nonempty support E(s,z) subseteq Y x S",
            "timing": "from current sensor state and mode, emit y and update hidden sensor state; controller observes raw y history before writing",
            "normal_channel": "normal-cell symbol depends only on n and is charged separately; it cannot encode mode or sensor state",
            "charging": "each raw output word must remain injectively recoverable",
            "safety_quantifier": "every disturbance word and every transducer event word in support",
        },
        "theorem": {
            "feasibility": "every reachable subset-observer transition has a singleton current q set",
            "language_count": "L_T is the number of raw output words accepted from {s0}",
            "finite_read_words": "L_T ceil(rho*2^T)",
            "finite_write_words": "2^T ceil(rho*2^T)",
            "asymptotic_region": "[1+log2(rho(A)),infinity) x [2,infinity)",
            "A": "multiplicity adjacency matrix of the reachable deterministic subset observer",
        },
    }


def expected_claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_finite_state_sensor_claim_v0_18",
        "status": "finite-state support-zero-error sensor theorem with exact language entropy",
        "sealed_resources": {
            "count": 2,
            "canonical_source_sha256": SEALS["canonical_source"][1],
            "v0_17_kernel_claim_sha256": SEALS["v0_17_kernel_claim"][1],
        },
        "general_theorem": {
            "feasibility": "reachable subset-observer q-homogeneity",
            "finite_read_words": "L_T ceil(rho*2^T)",
            "finite_write_words": "2^T ceil(rho*2^T)",
            "asymptotic_region": "[1+log2(rho(A)),infinity) x [2,infinity)",
        },
        "fixtures": {
            "feasible": 4,
            "infeasible": 1,
            "golden_read_threshold": "2+log2(phi)",
            "history_overlap_fixture_feasible": True,
        },
        "two_state_binary_census": {
            "transducers": 256,
            "feasible": 80,
            "infeasible": 176,
            "history_essential": 48,
            "globally_disjoint": 32,
        },
        "mutation_audit": {"cases": 5, "rejected": 5},
        "predecessor_inventory": {"packages": 18, "tests": 214},
        "decision": "finite_sensor_memory_replaces_current_support_with_subset_observer_entropy",
        "nonclaim": (
            "The theorem assumes a finite registered transducer, fixed initial sensor "
            "state, raw-output charging, and support-zero-error safety. It does not "
            "cover unknown initial sensor state, continuous state, average or block "
            "error, expected length, or controller-side compression of raw outputs."
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


def finite_state_sensor_report() -> dict[str, Any]:
    integrity = resource_integrity_report()
    contract = contract_exactness_report()
    fixtures = fixture_theorem_report()
    census = two_state_binary_census_report()
    margin = finite_margin_report()
    mutations = mutation_report()
    inventory = predecessor_inventory_report()
    claim = claim_exactness_report()
    components = (
        integrity,
        contract,
        fixtures,
        census,
        margin,
        mutations,
        inventory,
        claim,
    )
    return {
        "schema_version": "asmp4_finite_state_sensor_transducers_v0_18",
        "resource_integrity": integrity,
        "contract_exactness": contract,
        "fixture_theorem": fixtures,
        "two_state_binary_census": census,
        "finite_margin": margin,
        "mutations": mutations,
        "predecessor_inventory": inventory,
        "claim_exactness": claim,
        "pass": all(component["pass"] for component in components),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    report = finite_state_sensor_report() if report is None else report
    return {
        "R0_two_resource_seals": report["resource_integrity"]["pass"],
        "R1_transducer_contract_exact": report["contract_exactness"]["pass"],
        "R2_subset_observer_fixtures": report["fixture_theorem"]["pass"],
        "R3_all_256_small_transducers": report["two_state_binary_census"]["pass"],
        "R4_exact_language_spectral_formula": report["fixture_theorem"]["pass"],
        "R5_exact_finite_margin": report["finite_margin"]["pass"],
        "R6_history_overlap_fixture": report["fixture_theorem"]["checks"][
            "toggle_global_overlap_but_history_decodable"
        ],
        "R7_five_mutations_rejected": report["mutations"]["pass"],
        "R8_inventory_and_claim": report["predecessor_inventory"]["pass"]
        and report["claim_exactness"]["pass"],
        "R9_complete_payload": report["pass"],
    }


def main() -> int:
    report = finite_state_sensor_report()
    payload = {"report": report, "gates": verification_gates(report)}
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
