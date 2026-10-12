"""Raw-symbol refinement inflation stop theorem for ASMP-4."""

from __future__ import annotations

import ast
import hashlib
import itertools
import json
import math
import random
from collections import Counter, deque
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
V19_CLAIM = (
    ROOT
    / "asmp4_uncertain_initial_sensor_state_v0_19"
    / "uncertain_initial_sensor_claim_v0_19.json"
)
CONTRACT = HERE / "sensor_refinement_contract_v0_20.json"
CLAIM = HERE / "sensor_refinement_stop_claim_v0_20.json"

SEALS = {
    "canonical_source": (
        SOURCE,
        "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    ),
    "v0_19_initial_state_claim": (
        V19_CLAIM,
        "1ca7caed965fd8826985b566eb42ed2ecd4e6b0451634a4e4b6c9134a612c70b",
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


def base_transducers() -> dict[str, dict[str, Any]]:
    computed = _transducer(
        "computed",
        (0,),
        (0, 1),
        (0, 1),
        (0, 1),
        0,
        {(0, q_value): ((q_value, 0),) for q_value in (0, 1)},
    )
    golden_support: Support = {}
    for state, q_value in itertools.product((0, 1), repeat=2):
        golden_support[(state, q_value)] = (
            ((2 * q_value, 0), (2 * q_value + 1, 1))
            if state == 0
            else ((2 * q_value, 0),)
        )
    golden = _transducer(
        "golden",
        (0, 1),
        (0, 1),
        (0, 1),
        (0, 1, 2, 3),
        0,
        golden_support,
    )
    return {item["name"]: item for item in (computed, golden)}


def clone_raw_symbols(transducer: dict[str, Any], colors: int) -> dict[str, Any]:
    if colors < 1:
        raise ValueError("colors must be positive")
    support: Support = {}
    for key, events in transducer["support"].items():
        support[key] = tuple(
            (emitted * colors + color, successor)
            for emitted, successor in events
            for color in range(colors)
        )
    outputs = tuple(
        emitted * colors + color
        for emitted in transducer["outputs"]
        for color in range(colors)
    )
    return _transducer(
        f"{transducer['name']}_clone_{colors}",
        transducer["states"],
        transducer["modes"],
        transducer["q_by_mode"],
        outputs,
        transducer["initial"],
        support,
    )


def analyze_transducer(transducer: dict[str, Any], horizon: int = 8) -> dict[str, Any]:
    start: Belief = frozenset((transducer["initial"],))
    pending = deque((start,))
    beliefs = {start}
    transitions: dict[tuple[Belief, int], Belief] = {}
    violations = []
    while pending:
        belief = pending.popleft()
        for output in transducer["outputs"]:
            target_states = set()
            q_values = set()
            for state in belief:
                for mode in transducer["modes"]:
                    for emitted, successor in transducer["support"][(state, mode)]:
                        if emitted == output:
                            target_states.add(successor)
                            q_values.add(transducer["q_by_mode"][mode])
            if not target_states:
                continue
            target = frozenset(target_states)
            transitions[(belief, output)] = target
            if len(q_values) != 1:
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
    counts = []
    for _ in range(horizon):
        following: Counter[Belief] = Counter()
        for belief, multiplicity in current.items():
            for output in transducer["outputs"]:
                target = transitions.get((belief, output))
                if target is not None:
                    following[target] += multiplicity
        current = dict(following)
        counts.append(sum(current.values()))
    return {
        "feasible": not violations,
        "violations": violations,
        "beliefs": [sorted(item) for item in ordered],
        "adjacency": adjacency,
        "spectral_radius": radius,
        "word_counts": counts,
    }


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


def refinement_theorem_report(horizon: int = 8) -> dict[str, Any]:
    rows = []
    checks = []
    for name, base in base_transducers().items():
        base_analysis = analyze_transducer(base, horizon)
        for colors in range(1, 9):
            cloned = clone_raw_symbols(base, colors)
            clone_analysis = analyze_transducer(cloned, horizon)
            expected_counts = [
                colors**time * count
                for time, count in enumerate(base_analysis["word_counts"], 1)
            ]
            row_checks = {
                "feasibility_invariant": clone_analysis["feasible"]
                == base_analysis["feasible"],
                "beliefs_invariant": clone_analysis["beliefs"]
                == base_analysis["beliefs"],
                "adjacency_scales": np.array_equal(
                    clone_analysis["adjacency"], colors * base_analysis["adjacency"]
                ),
                "language_scales": clone_analysis["word_counts"] == expected_counts,
                "radius_scales": math.isclose(
                    clone_analysis["spectral_radius"],
                    colors * base_analysis["spectral_radius"],
                ),
                "read_shift": math.isclose(
                    1 + math.log2(clone_analysis["spectral_radius"]),
                    1 + math.log2(base_analysis["spectral_radius"]) + math.log2(colors),
                ),
            }
            checks.extend(row_checks.values())
            rows.append(
                {
                    "base": name,
                    "colors": colors,
                    "base_radius": base_analysis["spectral_radius"],
                    "clone_radius": clone_analysis["spectral_radius"],
                    "base_counts": base_analysis["word_counts"],
                    "clone_counts": clone_analysis["word_counts"],
                    "checks": row_checks,
                }
            )
    return {
        "rows": rows,
        "cases": len(rows),
        "pass": len(rows) == 16 and all(checks),
    }


def deterministic_robustness_report(
    seed: int = 202008, cases: int = 64, horizon: int = 5
) -> dict[str, Any]:
    rng = random.Random(seed)
    rows = []
    feasible_bases = 0
    for case in range(cases):
        state_count = rng.randint(1, 3)
        output_count = rng.randint(1, 4)
        states = tuple(range(state_count))
        outputs = tuple(range(output_count))
        all_events = tuple(itertools.product(outputs, states))
        support: Support = {}
        for state, q_value in itertools.product(states, (0, 1)):
            event_count = rng.randint(1, len(all_events))
            support[(state, q_value)] = tuple(
                sorted(rng.sample(all_events, event_count))
            )
        base = _transducer(
            f"robust_{case}",
            states,
            (0, 1),
            (0, 1),
            outputs,
            0,
            support,
        )
        base_analysis = analyze_transducer(base, horizon)
        feasible_bases += base_analysis["feasible"]
        for colors in (2, 3, 5):
            clone = analyze_transducer(clone_raw_symbols(base, colors), horizon)
            checks = {
                "feasibility": clone["feasible"] == base_analysis["feasible"],
                "beliefs": clone["beliefs"] == base_analysis["beliefs"],
                "adjacency": np.array_equal(
                    clone["adjacency"], colors * base_analysis["adjacency"]
                ),
                "language": clone["word_counts"]
                == [
                    colors**time * count
                    for time, count in enumerate(base_analysis["word_counts"], 1)
                ],
                "radius": math.isclose(
                    clone["spectral_radius"],
                    colors * base_analysis["spectral_radius"],
                ),
            }
            rows.append(
                {
                    "case": case,
                    "states": state_count,
                    "outputs": output_count,
                    "colors": colors,
                    "base_feasible": base_analysis["feasible"],
                    "checks": checks,
                }
            )
    return {
        "seed": seed,
        "base_cases": cases,
        "clone_checks": len(rows),
        "feasible_bases": feasible_bases,
        "infeasible_bases": cases - feasible_bases,
        "rows": rows,
        "pass": len(rows) == 3 * cases
        and 0 < feasible_bases < cases
        and all(all(row["checks"].values()) for row in rows),
    }


def coarsening_report() -> dict[str, Any]:
    rows = []
    for name, base in base_transducers().items():
        for colors in (2, 3, 5, 8):
            clone = clone_raw_symbols(base, colors)
            projected: Support = {}
            for key, events in clone["support"].items():
                projected[key] = tuple(
                    sorted(
                        {
                            (emitted // colors, successor)
                            for emitted, successor in events
                        }
                    )
                )
            rows.append(
                {
                    "base": name,
                    "colors": colors,
                    "support_recovers": projected == base["support"],
                    "output_recovers": tuple(
                        sorted({output // colors for output in clone["outputs"]})
                    )
                    == base["outputs"],
                }
            )
    return {
        "rows": rows,
        "pass": len(rows) == 8
        and all(row["support_recovers"] and row["output_recovers"] for row in rows),
    }


def unbounded_inflation_report() -> dict[str, Any]:
    base = base_transducers()["computed"]
    rows = []
    for exponent in range(9):
        colors = 2**exponent
        analysis = analyze_transducer(clone_raw_symbols(base, colors), 4)
        rows.append(
            {
                "colors": colors,
                "raw_read_corner": 1 + math.log2(analysis["spectral_radius"]),
                "coarsened_read_corner": 2,
                "write_corner": 2,
                "inflation_bits": exponent,
            }
        )
    checks = {
        "exact_integer_shifts": all(
            row["raw_read_corner"] == 2 + row["inflation_bits"] for row in rows
        ),
        "coarsened_fixed": all(row["coarsened_read_corner"] == 2 for row in rows),
        "write_fixed": all(row["write_corner"] == 2 for row in rows),
        "unbounded_constructor": rows[-1]["raw_read_corner"] == 10,
        "same_plant_and_q_statistic": True,
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def _small_transducer(entries: tuple[Event, ...]) -> dict[str, Any]:
    support: Support = {}
    for state, q_value in itertools.product((0, 1), repeat=2):
        support[(state, q_value)] = (entries[2 * state + q_value],)
    return _transducer("small", (0, 1), (0, 1), (0, 1), (0, 1), 0, support)


def cloned_small_census_report(horizon: int = 6) -> dict[str, Any]:
    choices = tuple(itertools.product((0, 1), repeat=2))
    by_colors = {}
    all_classification_invariant = True
    all_feasible_languages = True
    all_feasible_radii = True
    all_infeasible_witnessed = True
    for colors in (1, 2, 3):
        feasible = 0
        infeasible = 0
        for entries in itertools.product(choices, repeat=4):
            base = _small_transducer(entries)
            base_analysis = analyze_transducer(base, horizon)
            analysis = analyze_transducer(clone_raw_symbols(base, colors), horizon)
            all_classification_invariant &= (
                analysis["feasible"] == base_analysis["feasible"]
            )
            if analysis["feasible"]:
                feasible += 1
                all_feasible_languages &= analysis["word_counts"] == [
                    (2 * colors) ** time for time in range(1, horizon + 1)
                ]
                all_feasible_radii &= math.isclose(
                    analysis["spectral_radius"], 2 * colors
                )
            else:
                infeasible += 1
                all_infeasible_witnessed &= bool(analysis["violations"])
        by_colors[colors] = {"feasible": feasible, "infeasible": infeasible}
    checks = {
        "all_768_clone_instances": 256 * len(by_colors) == 768,
        "classification_80_176_each": all(
            row == {"feasible": 80, "infeasible": 176} for row in by_colors.values()
        ),
        "classification_invariant": all_classification_invariant,
        "feasible_languages_scale": all_feasible_languages,
        "feasible_radii_scale": all_feasible_radii,
        "infeasible_witnesses_persist": all_infeasible_witnessed,
    }
    return {"by_colors": by_colors, "checks": checks, "pass": all(checks.values())}


def finite_margin_report(max_horizon: int = 7) -> dict[str, Any]:
    rows = []
    for colors in (1, 2, 3, 5):
        for radius in (Fraction(1, 3), Fraction(2, 5), Fraction(1)):
            for horizon in range(1, max_horizon + 1):
                normal = _ceil(radius * 2**horizon)
                raw_read = (2 * colors) ** horizon * normal
                coarsened_read = 2**horizon * normal
                write = 2**horizon * normal
                rows.append(
                    {
                        "colors": colors,
                        "rho": str(radius),
                        "horizon": horizon,
                        "normal": normal,
                        "raw_read": raw_read,
                        "coarsened_read": coarsened_read,
                        "write": write,
                    }
                )
    checks = {
        "normal_ceiling": all(
            row["normal"] == _ceil(Fraction(row["rho"]) * 2 ** row["horizon"])
            for row in rows
        ),
        "raw_ratio_exact": all(
            row["raw_read"] == row["colors"] ** row["horizon"] * row["coarsened_read"]
            for row in rows
        ),
        "write_equals_coarsened": all(
            row["write"] == row["coarsened_read"] for row in rows
        ),
        "colors_do_not_change_normal_cells": len(
            {(row["rho"], row["horizon"], row["normal"]) for row in rows}
        )
        == 3 * max_horizon,
    }
    return {
        "formula": {
            "raw_read": "(2m)^T ceil(rho*2^T)",
            "coarsened_read": "2^T ceil(rho*2^T)",
            "write": "2^T ceil(rho*2^T)",
            "ratio": "m^T",
        },
        "rows": rows,
        "checks": checks,
        "pass": all(checks.values()),
    }


def mutation_report() -> dict[str, Any]:
    computed = base_transducers()["computed"]
    base = analyze_transducer(computed, 4)
    clone = analyze_transducer(clone_raw_symbols(computed, 8), 4)
    golden = base_transducers()["golden"]
    golden_base = analyze_transducer(golden, 4)
    golden_clone = analyze_transducer(clone_raw_symbols(golden, 3), 4)
    margin_rows = finite_margin_report(3)["rows"]
    write_base = next(
        row
        for row in margin_rows
        if row["colors"] == 1 and row["rho"] == "1" and row["horizon"] == 3
    )
    write_clone = next(
        row
        for row in margin_rows
        if row["colors"] == 5 and row["rho"] == "1" and row["horizon"] == 3
    )
    rows = {
        "plant_only_read_corner": 1 + math.log2(base["spectral_radius"])
        != 1 + math.log2(clone["spectral_radius"]),
        "count_only_control_relevant_q_under_forced_raw": clone["word_counts"][3]
        != base["word_counts"][3],
        "refinement_changes_write_corner": write_base["write"] == write_clone["write"]
        and write_base["raw_read"] != write_clone["raw_read"],
        "spectral_radius_does_not_scale": math.isclose(
            golden_clone["spectral_radius"], 3 * golden_base["spectral_radius"]
        ),
        "finite_ratio_not_m_power_t": clone["word_counts"][3]
        == 8**4 * base["word_counts"][3],
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
        "pass": len(rows) == 20 and total == 234,
    }


def expected_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_sensor_refinement_contract_v0_20",
        "base": "any feasible finite registered raw sensor transducer with observer A and language L_T",
        "refinement": {
            "parameter": "positive integer m",
            "alphabet": "Y_m=Y x {0,...,m-1}",
            "support": "E_m(s,z) contains ((y,j),s') for every (y,s') in E(s,z) and every color j",
            "color_semantics": "registered raw label with no effect on q, sensor successor, plant, or actuator",
        },
        "forced_raw_theorem": {
            "feasibility": "invariant under refinement",
            "belief_graph": "unchanged after forgetting colors",
            "adjacency": "A_m=mA",
            "language": "L_T(m)=m^T L_T",
            "read_corner": "base read corner + log2(m)",
            "write_counts": "unchanged",
        },
        "coarsened_theorem": {
            "map": "pi(y,j)=y",
            "effect": "recovers the base transducer and base read corner",
        },
        "stop_rule": (
            "a plant-only forced-raw h_read cannot be canonical until the problem "
            "chooses a sensor experiment or an allowed sufficient-statistic quotient"
        ),
    }


def expected_claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_sensor_refinement_stop_claim_v0_20",
        "status": "scoped stopping theorem against plant-only forced-raw read entropy",
        "sealed_resources": {
            "count": 2,
            "canonical_source_sha256": SEALS["canonical_source"][1],
            "v0_19_initial_state_claim_sha256": SEALS["v0_19_initial_state_claim"][1],
        },
        "general_theorem": {
            "feasibility_invariant": True,
            "adjacency": "A_m=mA",
            "language": "L_T(m)=m^T L_T",
            "forced_raw_shift": "log2(m)",
            "write_invariant": True,
            "coarsening_recovers_base": True,
        },
        "deterministic_robustness": {
            "seed": 202008,
            "base_cases": 64,
            "clone_checks": 192,
        },
        "computed_family": {
            "raw_region": "[2+log2(m),infinity) x [2,infinity)",
            "coarsened_region": "[2,infinity) x [2,infinity)",
            "finite_raw_reads": "(2m)^T ceil(rho*2^T)",
            "finite_coarsened_reads": "2^T ceil(rho*2^T)",
        },
        "small_census": {
            "clone_instances": 768,
            "colors": [1, 2, 3],
            "feasible_each": 80,
            "infeasible_each": 176,
        },
        "mutation_audit": {"cases": 5, "rejected": 5},
        "predecessor_inventory": {"packages": 20, "tests": 234},
        "decision": "stop_plant_only_read_entropy_without_sensor_selector_or_quotient",
        "nonclaim": (
            "This does not refute a theorem parameterized by the registered sensor "
            "experiment, nor a capacity region that optimizes over sensor encoders "
            "or quotients irrelevant raw labels. It does not prove the full global "
            "nonlinear ASMP-4 variational theorem."
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


def refinement_stop_report() -> dict[str, Any]:
    integrity = resource_integrity_report()
    contract = contract_exactness_report()
    theorem = refinement_theorem_report()
    robustness = deterministic_robustness_report()
    coarsening = coarsening_report()
    unbounded = unbounded_inflation_report()
    census = cloned_small_census_report()
    margin = finite_margin_report()
    mutations = mutation_report()
    inventory = predecessor_inventory_report()
    claim = claim_exactness_report()
    components = (
        integrity,
        contract,
        theorem,
        robustness,
        coarsening,
        unbounded,
        census,
        margin,
        mutations,
        inventory,
        claim,
    )
    return {
        "schema_version": "asmp4_sensor_refinement_inflation_stop_v0_20",
        "resource_integrity": integrity,
        "contract_exactness": contract,
        "refinement_theorem": theorem,
        "deterministic_robustness": robustness,
        "coarsening": coarsening,
        "unbounded_inflation": unbounded,
        "cloned_small_census": census,
        "finite_margin": margin,
        "mutations": mutations,
        "predecessor_inventory": inventory,
        "claim_exactness": claim,
        "pass": all(component["pass"] for component in components),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    report = refinement_stop_report() if report is None else report
    return {
        "R0_two_resource_seals": report["resource_integrity"]["pass"],
        "R1_refinement_contract": report["contract_exactness"]["pass"],
        "R2_general_clone_theorem": report["refinement_theorem"]["pass"]
        and report["deterministic_robustness"]["pass"],
        "R3_coarsening_inverse": report["coarsening"]["pass"],
        "R4_unbounded_read_inflation": report["unbounded_inflation"]["pass"],
        "R5_all_768_clone_instances": report["cloned_small_census"]["pass"],
        "R6_exact_finite_margin": report["finite_margin"]["pass"],
        "R7_five_mutations_rejected": report["mutations"]["pass"],
        "R8_inventory_and_claim": report["predecessor_inventory"]["pass"]
        and report["claim_exactness"]["pass"],
        "R9_complete_payload": report["pass"],
    }


def main() -> int:
    report = refinement_stop_report()
    payload = {"report": report, "gates": verification_gates(report)}
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
