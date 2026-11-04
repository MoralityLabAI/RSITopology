"""Uncertain initial sensor-state boundary for ASMP-4 finite transducers."""

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
V18_CLAIM = (
    ROOT
    / "asmp4_finite_state_sensor_transducers_v0_18"
    / "finite_state_sensor_claim_v0_18.json"
)
CONTRACT = HERE / "uncertain_initial_sensor_contract_v0_19.json"
CLAIM = HERE / "uncertain_initial_sensor_claim_v0_19.json"

SEALS = {
    "canonical_source": (
        SOURCE,
        "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    ),
    "v0_18_transducer_claim": (
        V18_CLAIM,
        "758b3c0a668b4c77985928271ce314ca4bedd3205f2a570bd4c18fc29ae5916c",
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


def _system(
    name: str,
    states: tuple[int, ...],
    modes: tuple[int, ...],
    q_by_mode: tuple[int, ...],
    outputs: tuple[int, ...],
    initial_states: tuple[int, ...],
    support: Support,
) -> dict[str, Any]:
    return {
        "name": name,
        "states": states,
        "modes": modes,
        "q_by_mode": q_by_mode,
        "outputs": outputs,
        "initial_states": initial_states,
        "support": support,
    }


def analyze_system(system: dict[str, Any], max_horizon: int = 10) -> dict[str, Any]:
    outputs = system["outputs"]
    support: Support = system["support"]
    q_by_mode = system["q_by_mode"]
    start: Belief = frozenset(system["initial_states"])
    pending = deque((start,))
    beliefs = {start}
    transitions: dict[tuple[Belief, int], Belief] = {}
    violations = []
    while pending:
        belief = pending.popleft()
        for output in outputs:
            target_states = set()
            q_values = set()
            witnesses = []
            for state in belief:
                for mode in system["modes"]:
                    for emitted, successor in support[(state, mode)]:
                        if emitted == output:
                            target_states.add(successor)
                            q_values.add(q_by_mode[mode])
                            witnesses.append((state, mode, successor))
            if not target_states:
                continue
            target = frozenset(target_states)
            transitions[(belief, output)] = target
            if len(q_values) != 1:
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
                pending.append(target)

    ordered = sorted(beliefs, key=lambda item: (len(item), tuple(item)))
    index = {belief: position for position, belief in enumerate(ordered)}
    adjacency = np.zeros((len(ordered), len(ordered)), dtype=int)
    for (belief, _output), target in transitions.items():
        adjacency[index[belief], index[target]] += 1
    eigenvalues = np.linalg.eigvals(adjacency.astype(float))
    spectral_radius = float(max(abs(value) for value in eigenvalues))

    current: dict[Belief, int] = {start: 1}
    word_counts = []
    for _ in range(max_horizon):
        following: Counter[Belief] = Counter()
        for belief, multiplicity in current.items():
            for output in outputs:
                target = transitions.get((belief, output))
                if target is not None:
                    following[target] += multiplicity
        current = dict(following)
        word_counts.append(sum(current.values()))
    return {
        "feasible": not violations,
        "beliefs": [sorted(item) for item in ordered],
        "violations": violations,
        "adjacency": adjacency,
        "spectral_radius": spectral_radius,
        "word_counts": word_counts,
    }


def fixture_systems() -> dict[str, dict[str, Any]]:
    states = (0, 1)
    modes = (0, 1)
    q = (0, 1)
    toggle: Support = {}
    synchronizing: Support = {}
    dominant: Support = {}
    for state, mode in itertools.product(states, modes):
        toggle[(state, mode)] = ((q[mode] ^ state, 1 - state),)
        synchronizing[(state, mode)] = ((2 * q[mode] + state, 0),)
        dominant[(state, mode)] = (
            ((2 * q[mode], 0),)
            if state == 0
            else ((2 * q[mode], 1), (2 * q[mode] + 1, 1))
        )
    systems = (
        _system("known_toggle", states, modes, q, (0, 1), (0,), toggle),
        _system("uncertain_toggle", states, modes, q, (0, 1), states, toggle),
        _system(
            "synchronizing_transient",
            states,
            modes,
            q,
            (0, 1, 2, 3),
            states,
            synchronizing,
        ),
        _system(
            "union_dominant",
            states,
            modes,
            q,
            (0, 1, 2, 3),
            states,
            dominant,
        ),
        _system(
            "dominant_known_low_rate",
            states,
            modes,
            q,
            (0, 1, 2, 3),
            (0,),
            dominant,
        ),
    )
    return {system["name"]: system for system in systems}


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


def fixture_theorem_report(max_horizon: int = 10) -> dict[str, Any]:
    systems = fixture_systems()
    analyses = {
        name: analyze_system(system, max_horizon) for name, system in systems.items()
    }
    checks = {
        "known_toggle_feasible": analyses["known_toggle"]["feasible"],
        "uncertain_toggle_infeasible": not analyses["uncertain_toggle"]["feasible"],
        "uncertain_toggle_first_step_mixed": analyses["uncertain_toggle"]["violations"][
            0
        ]["belief"]
        == [0, 1],
        "synchronizing_feasible": analyses["synchronizing_transient"]["feasible"],
        "synchronizing_exact_transient": analyses["synchronizing_transient"][
            "word_counts"
        ]
        == [2 ** (time + 1) for time in range(1, max_horizon + 1)],
        "synchronizing_radius_two": math.isclose(
            analyses["synchronizing_transient"]["spectral_radius"], 2
        ),
        "dominant_uncertain_full_language": analyses["union_dominant"]["word_counts"]
        == [4**time for time in range(1, max_horizon + 1)],
        "dominant_uncertain_radius_four": math.isclose(
            analyses["union_dominant"]["spectral_radius"], 4
        ),
        "dominant_known_low_rate": analyses["dominant_known_low_rate"]["word_counts"]
        == [2**time for time in range(1, max_horizon + 1)],
        "dominant_known_radius_two": math.isclose(
            analyses["dominant_known_low_rate"]["spectral_radius"], 2
        ),
    }
    rows = [
        {
            "name": name,
            "feasible": analysis["feasible"],
            "beliefs": analysis["beliefs"],
            "word_counts": analysis["word_counts"],
            "spectral_radius": analysis["spectral_radius"],
            "read_threshold": (
                1 + math.log2(analysis["spectral_radius"])
                if analysis["feasible"]
                else None
            ),
        }
        for name, analysis in analyses.items()
    ]
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def _deterministic_system(
    entries: tuple[Event, ...], initial: tuple[int, ...]
) -> dict[str, Any]:
    support: Support = {}
    for state, q_value in itertools.product((0, 1), repeat=2):
        support[(state, q_value)] = (entries[2 * state + q_value],)
    return _system("census", (0, 1), (0, 1), (0, 1), (0, 1), initial, support)


def uncertain_initial_census_report(max_horizon: int = 7) -> dict[str, Any]:
    choices = tuple(itertools.product((0, 1), repeat=2))
    initial_sets = ((0,), (1,), (0, 1))
    signatures = Counter()
    feasible_by_initial = Counter()
    full_belief_histogram = Counter()
    full_mask_signatures = Counter()
    full_language_exact = True
    full_iff_global_disjoint = True
    for entries in itertools.product(choices, repeat=4):
        feasibility = []
        full_analysis = None
        for initial in initial_sets:
            analysis = analyze_system(
                _deterministic_system(entries, initial), max_horizon
            )
            feasibility.append(analysis["feasible"])
            feasible_by_initial[initial] += analysis["feasible"]
            if initial == (0, 1):
                full_analysis = analysis
        signature = tuple(feasibility)
        signatures[signature] += 1
        assert full_analysis is not None
        low = {entries[0][0], entries[2][0]}
        high = {entries[1][0], entries[3][0]}
        globally_disjoint = low.isdisjoint(high)
        full_iff_global_disjoint &= full_analysis["feasible"] == globally_disjoint
        if full_analysis["feasible"]:
            full_belief_histogram[len(full_analysis["beliefs"])] += 1
            full_mask_signatures[
                tuple(tuple(row) for row in full_analysis["beliefs"])
            ] += 1
            full_language_exact &= full_analysis["word_counts"] == [
                2**time for time in range(1, max_horizon + 1)
            ]

    expected_signatures = {
        (False, False, False): 160,
        (True, True, True): 32,
        (True, True, False): 32,
        (True, False, False): 16,
        (False, True, False): 16,
    }
    total_feasible = sum(feasible_by_initial.values())
    checks = {
        "all_768_pairs": 256 * len(initial_sets) == 768,
        "feasible_by_initial": feasible_by_initial == {(0,): 80, (1,): 80, (0, 1): 32},
        "feasible_192": total_feasible == 192,
        "infeasible_576": 768 - total_feasible == 576,
        "exact_signature_partition": signatures == expected_signatures,
        "both_singletons_but_not_uncertain_32": signatures[(True, True, False)] == 32,
        "full_iff_global_disjoint": full_iff_global_disjoint,
        "full_belief_histogram": full_belief_histogram == {1: 8, 2: 12, 3: 12},
        "full_language_binary": full_language_exact,
        "full_mask_signatures_total": sum(full_mask_signatures.values()) == 32,
    }
    return {
        "census": {
            "transducers": 256,
            "registered_pairs": 768,
            "feasible": total_feasible,
            "infeasible": 768 - total_feasible,
            "feasible_initial_0": feasible_by_initial[(0,)],
            "feasible_initial_1": feasible_by_initial[(1,)],
            "feasible_initial_full": feasible_by_initial[(0, 1)],
            "signature_histogram": {
                "000": signatures[(False, False, False)],
                "111": signatures[(True, True, True)],
                "110": signatures[(True, True, False)],
                "100": signatures[(True, False, False)],
                "010": signatures[(False, True, False)],
            },
            "full_belief_histogram": dict(sorted(full_belief_histogram.items())),
        },
        "checks": checks,
        "pass": all(checks.values()),
    }


def finite_margin_report(max_horizon: int = 7) -> dict[str, Any]:
    systems = fixture_systems()
    rows = []
    for name in ("synchronizing_transient", "union_dominant"):
        analysis = analyze_system(systems[name], max_horizon)
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
        "ceiling": all(
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
        "transient_first_horizon_four": next(
            row["language_words"]
            for row in rows
            if row["fixture"] == "synchronizing_transient"
        )
        == 4,
    }
    return {
        "formula": {
            "read": "L_T(I) ceil(rho*2^T)",
            "write": "2^T ceil(rho*2^T)",
            "rate": "1+log2(rho(A_I))",
        },
        "rows": rows,
        "checks": checks,
        "pass": all(checks.values()),
    }


def mutation_report() -> dict[str, Any]:
    systems = fixture_systems()
    known_toggle = analyze_system(systems["known_toggle"], 4)
    uncertain_toggle = analyze_system(systems["uncertain_toggle"], 4)
    sync = analyze_system(systems["synchronizing_transient"], 4)
    census = uncertain_initial_census_report(4)["census"]
    rows = {
        "replace_uncertain_set_by_representative": known_toggle["feasible"]
        and not uncertain_toggle["feasible"],
        "infer_union_from_both_singletons": census["signature_histogram"]["110"] == 32,
        "charge_alphabet_power_not_language": sync["word_counts"][3] != 4**4,
        "omit_normal_read_factor": 4 * 2 != 4,
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
        "pass": len(rows) == 19 and total == 224,
    }


def expected_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_uncertain_initial_sensor_contract_v0_19",
        "base_plant": "v0.13 positive-volume collar with arbitrary two-class q disturbance",
        "initial_state": {
            "parameter": "registered nonempty set I subseteq S",
            "knowledge": "controller knows I but not the adversarially selected actual initial sensor state",
            "start_belief": "B_0=I",
        },
        "transducer": {
            "parameter": "finite S, finite raw Y, and nonempty support E(s,z) subseteq Y x S",
            "charging": "raw output word and normal cell are separately injective",
            "normal_channel": "depends only on n and cannot encode initial sensor state, mode, or event",
            "safety_quantifier": "every initial sensor state in I, disturbance word, and supported event word",
        },
        "theorem": {
            "feasibility": "every reachable transition from B_0=I has singleton current q set",
            "language_count": "L_T(I)=e_I^T A_I^T 1",
            "finite_read_words": "L_T(I) ceil(rho*2^T)",
            "finite_write_words": "2^T ceil(rho*2^T)",
            "asymptotic_region": "[1+log2(rho(A_I)),infinity) x [2,infinity)",
        },
    }


def expected_claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_uncertain_initial_sensor_claim_v0_19",
        "status": "uncertain-initial-state subset-observer theorem",
        "sealed_resources": {
            "count": 2,
            "canonical_source_sha256": SEALS["canonical_source"][1],
            "v0_18_transducer_claim_sha256": SEALS["v0_18_transducer_claim"][1],
        },
        "general_theorem": {
            "start_belief": "B_0=I",
            "feasibility": "reachable q-homogeneity from I",
            "finite_read_words": "L_T(I) ceil(rho*2^T)",
            "finite_write_words": "2^T ceil(rho*2^T)",
            "asymptotic_region": "[1+log2(rho(A_I)),infinity) x [2,infinity)",
        },
        "two_state_census": {
            "registered_pairs": 768,
            "feasible": 192,
            "infeasible": 576,
            "feasible_by_initial_set": {"0": 80, "1": 80, "01": 32},
            "both_singletons_but_full_fails": 32,
        },
        "fixtures": {
            "known_toggle_feasible": True,
            "uncertain_toggle_infeasible": True,
            "synchronizing_transient_rate": 2,
            "union_dominant_rate": 3,
        },
        "mutation_audit": {"cases": 5, "rejected": 5},
        "predecessor_inventory": {"packages": 19, "tests": 224},
        "decision": "initial_sensor_state_knowledge_is_a_load_bearing_registered_parameter",
        "nonclaim": (
            "The theorem retains finite state, registered initial uncertainty, "
            "raw-output charging, and universal support safety. It does not cover "
            "probabilistic priors on the initial state, active calibration before "
            "safety begins, continuous state, raw compression, or block error."
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


def uncertain_initial_report() -> dict[str, Any]:
    integrity = resource_integrity_report()
    contract = contract_exactness_report()
    fixtures = fixture_theorem_report()
    census = uncertain_initial_census_report()
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
        "schema_version": "asmp4_uncertain_initial_sensor_state_v0_19",
        "resource_integrity": integrity,
        "contract_exactness": contract,
        "fixture_theorem": fixtures,
        "uncertain_initial_census": census,
        "finite_margin": margin,
        "mutations": mutations,
        "predecessor_inventory": inventory,
        "claim_exactness": claim,
        "pass": all(component["pass"] for component in components),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    report = uncertain_initial_report() if report is None else report
    return {
        "R0_two_resource_seals": report["resource_integrity"]["pass"],
        "R1_uncertain_initial_contract": report["contract_exactness"]["pass"],
        "R2_start_belief_fixtures": report["fixture_theorem"]["pass"],
        "R3_all_768_registered_pairs": report["uncertain_initial_census"]["pass"],
        "R4_transient_and_spectral_languages": report["fixture_theorem"]["pass"],
        "R5_exact_finite_margin": report["finite_margin"]["pass"],
        "R6_unknown_toggle_separation": report["fixture_theorem"]["checks"][
            "uncertain_toggle_infeasible"
        ],
        "R7_five_mutations_rejected": report["mutations"]["pass"],
        "R8_inventory_and_claim": report["predecessor_inventory"]["pass"]
        and report["claim_exactness"]["pass"],
        "R9_complete_payload": report["pass"],
    }


def main() -> int:
    report = uncertain_initial_report()
    payload = {"report": report, "gates": verification_gates(report)}
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
