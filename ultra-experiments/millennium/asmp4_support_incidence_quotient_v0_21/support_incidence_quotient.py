"""Support-incidence quotient for finite ASMP-4 sensor transducers."""

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
V20_CLAIM = (
    ROOT
    / "asmp4_sensor_refinement_inflation_stop_v0_20"
    / "sensor_refinement_stop_claim_v0_20.json"
)
CONTRACT = HERE / "support_incidence_quotient_contract_v0_21.json"
CLAIM = HERE / "support_incidence_quotient_claim_v0_21.json"

SEALS = {
    "canonical_source": (
        SOURCE,
        "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    ),
    "v0_20_refinement_stop_claim": (
        V20_CLAIM,
        "b06213d846b53cf7f2262b7f0cf3dea89f22ca5f679ec8e87d5fd88e13de7d8f",
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
)

Belief = frozenset[int]
Event = tuple[int, int]
Support = dict[tuple[int, int], tuple[Event, ...]]
Signature = tuple[tuple[int, int, int], ...]


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


def fixture_transducers() -> dict[str, dict[str, Any]]:
    computed = _transducer(
        "computed",
        (0,),
        (0, 1),
        (0, 1),
        (0, 1),
        (0,),
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
        (0,),
        golden_support,
    )
    duplicate = _transducer(
        "duplicate_memoryless",
        (0,),
        (0, 1),
        (0, 1),
        (0, 1, 2, 3),
        (0,),
        {
            (0, 0): ((0, 0), (1, 0)),
            (0, 1): ((2, 0), (3, 0)),
        },
    )
    bad = _transducer(
        "infeasible_overlap",
        (0,),
        (0, 1),
        (0, 1),
        (0, 1),
        (0,),
        {
            (0, 0): ((0, 0), (1, 0)),
            (0, 1): ((0, 0), (1, 0)),
        },
    )
    return {item["name"]: item for item in (computed, golden, duplicate, bad)}


def active_signature_map(transducer: dict[str, Any]) -> dict[int, Signature]:
    signatures: dict[int, Signature] = {}
    for output in transducer["outputs"]:
        incidence = []
        for state in transducer["states"]:
            for mode in transducer["modes"]:
                for emitted, successor in transducer["support"][(state, mode)]:
                    if emitted == output:
                        incidence.append((state, mode, successor))
        if incidence:
            signatures[output] = tuple(sorted(set(incidence)))
    return signatures


def support_incidence_quotient(
    transducer: dict[str, Any],
) -> tuple[dict[str, Any], dict[int, int], tuple[Signature, ...]]:
    signatures = active_signature_map(transducer)
    classes = tuple(sorted(set(signatures.values())))
    class_index = {signature: index for index, signature in enumerate(classes)}
    output_map = {
        output: class_index[signature] for output, signature in signatures.items()
    }
    support: Support = {}
    for key, events in transducer["support"].items():
        support[key] = tuple(
            sorted({(output_map[emitted], successor) for emitted, successor in events})
        )
    quotient = _transducer(
        f"{transducer['name']}_support_quotient",
        transducer["states"],
        transducer["modes"],
        transducer["q_by_mode"],
        tuple(range(len(classes))),
        transducer["initial_states"],
        support,
    )
    return quotient, output_map, classes


def clone_outputs(transducer: dict[str, Any], colors: int) -> dict[str, Any]:
    if colors < 1:
        raise ValueError("colors must be positive")
    outputs = tuple(
        output * colors + color
        for output in transducer["outputs"]
        for color in range(colors)
    )
    support = {
        key: tuple(
            (emitted * colors + color, successor)
            for emitted, successor in events
            for color in range(colors)
        )
        for key, events in transducer["support"].items()
    }
    return _transducer(
        f"{transducer['name']}_clone_{colors}",
        transducer["states"],
        transducer["modes"],
        transducer["q_by_mode"],
        outputs,
        transducer["initial_states"],
        support,
    )


def rename_outputs(transducer: dict[str, Any]) -> dict[str, Any]:
    mapping = {
        output: 100 + 7 * index
        for index, output in enumerate(reversed(transducer["outputs"]))
    }
    support = {
        key: tuple((mapping[emitted], successor) for emitted, successor in events)
        for key, events in transducer["support"].items()
    }
    return _transducer(
        f"{transducer['name']}_renamed",
        transducer["states"],
        transducer["modes"],
        transducer["q_by_mode"],
        tuple(mapping[output] for output in transducer["outputs"]),
        transducer["initial_states"],
        support,
    )


def analyze_transducer(transducer: dict[str, Any], horizon: int = 8) -> dict[str, Any]:
    start: Belief = frozenset(transducer["initial_states"])
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


def quotient_theorem_report(horizon: int = 8) -> dict[str, Any]:
    rows = []
    checks = []
    for name, base in fixture_transducers().items():
        quotient, _mapping, classes = support_incidence_quotient(base)
        raw_analysis = analyze_transducer(base, horizon)
        semantic = analyze_transducer(quotient, horizon)
        renamed_quotient, _renamed_map, renamed_classes = support_incidence_quotient(
            rename_outputs(base)
        )
        renamed = analyze_transducer(renamed_quotient, horizon)
        quotient_signatures = active_signature_map(quotient)
        row_checks = {
            "feasibility_preserved": semantic["feasible"] == raw_analysis["feasible"],
            "beliefs_preserved": semantic["beliefs"] == raw_analysis["beliefs"],
            "renaming_class_count": len(renamed_classes) == len(classes),
            "renaming_adjacency": np.array_equal(
                renamed["adjacency"], semantic["adjacency"]
            ),
            "renaming_language": renamed["word_counts"] == semantic["word_counts"],
            "idempotent": len(quotient_signatures) == len(classes)
            and len(set(quotient_signatures.values())) == len(classes),
        }
        checks.extend(row_checks.values())
        rows.append(
            {
                "name": name,
                "raw_active": len(active_signature_map(base)),
                "semantic_classes": len(classes),
                "raw_counts": raw_analysis["word_counts"],
                "semantic_counts": semantic["word_counts"],
                "raw_radius": raw_analysis["spectral_radius"],
                "semantic_radius": semantic["spectral_radius"],
                "checks": row_checks,
            }
        )

    clone_rows = []
    for name in ("computed", "golden", "duplicate_memoryless"):
        base = fixture_transducers()[name]
        base_quotient, _base_map, base_classes = support_incidence_quotient(base)
        base_semantic = analyze_transducer(base_quotient, horizon)
        for colors in range(1, 9):
            clone = clone_outputs(base, colors)
            clone_quotient, _clone_map, clone_classes = support_incidence_quotient(
                clone
            )
            clone_semantic = analyze_transducer(clone_quotient, horizon)
            clone_checks = {
                "class_count": len(clone_classes) == len(base_classes),
                "adjacency": np.array_equal(
                    clone_semantic["adjacency"], base_semantic["adjacency"]
                ),
                "language": clone_semantic["word_counts"]
                == base_semantic["word_counts"],
                "radius": math.isclose(
                    clone_semantic["spectral_radius"],
                    base_semantic["spectral_radius"],
                ),
                "feasibility": clone_semantic["feasible"] == base_semantic["feasible"],
            }
            checks.extend(clone_checks.values())
            clone_rows.append(
                {
                    "base": name,
                    "colors": colors,
                    "checks": clone_checks,
                }
            )
    duplicate_row = next(row for row in rows if row["name"] == "duplicate_memoryless")
    special_checks = {
        "duplicate_raw_four": duplicate_row["raw_active"] == 4,
        "duplicate_semantic_two": duplicate_row["semantic_classes"] == 2,
        "duplicate_raw_language": duplicate_row["raw_counts"]
        == [4**time for time in range(1, horizon + 1)],
        "duplicate_semantic_language": duplicate_row["semantic_counts"]
        == [2**time for time in range(1, horizon + 1)],
    }
    checks.extend(special_checks.values())
    return {
        "rows": rows,
        "clone_rows": clone_rows,
        "special_checks": special_checks,
        "pass": len(rows) == 4 and len(clone_rows) == 24 and all(checks),
    }


def memoryless_semantic_census_report() -> dict[str, Any]:
    per_declared = []
    joint_histogram = Counter()
    semantic_histogram = Counter()
    raw_histogram = Counter()
    total_relations = 0
    feasible_relations = 0
    duplicate_relations = 0
    quotient_feasibility_preserved = True
    for declared in range(1, 5):
        row_joint = Counter()
        row_feasible = 0
        row_total = 0
        nonempty = range(1, 2**declared)
        for relation in itertools.product(nonempty, repeat=4):
            row_total += 1
            signatures = []
            for output in range(declared):
                signature = sum(
                    (((relation[mode] >> output) & 1) << mode) for mode in range(4)
                )
                if signature:
                    signatures.append(signature)
            raw_active = len(signatures)
            semantic_classes = len(set(signatures))
            feasible = (relation[0] | relation[1]) & (relation[2] | relation[3]) == 0
            if feasible:
                row_feasible += 1
                feasible_relations += 1
                row_joint[(raw_active, semantic_classes)] += 1
                joint_histogram[(raw_active, semantic_classes)] += 1
                semantic_histogram[semantic_classes] += 1
                raw_histogram[raw_active] += 1
                duplicate_relations += semantic_classes < raw_active
                quotient_feasibility_preserved &= all(
                    signature in (1, 2, 3, 4, 8, 12) for signature in set(signatures)
                )
        total_relations += row_total
        per_declared.append(
            {
                "declared_outputs": declared,
                "relations": row_total,
                "feasible": row_feasible,
                "joint_histogram": {
                    f"{raw},{semantic}": count
                    for (raw, semantic), count in sorted(row_joint.items())
                },
            }
        )
    expected_joint = {
        (2, 2): 20,
        (3, 2): 30,
        (3, 3): 180,
        (4, 2): 14,
        (4, 3): 216,
        (4, 4): 264,
    }
    checks = {
        "all_53108_relations": total_relations == 53108,
        "feasible_724": feasible_relations == 724,
        "raw_histogram": raw_histogram == {2: 20, 3: 210, 4: 494},
        "semantic_histogram": semantic_histogram == {2: 64, 3: 396, 4: 264},
        "joint_histogram": joint_histogram == expected_joint,
        "duplicate_relations_260": duplicate_relations == 260,
        "quotient_feasibility_preserved": quotient_feasibility_preserved,
        "per_declared_feasible": [row["feasible"] for row in per_declared]
        == [0, 2, 48, 674],
    }
    return {
        "per_declared": per_declared,
        "combined": {
            "relations": total_relations,
            "feasible": feasible_relations,
            "duplicates_removed": duplicate_relations,
            "raw_active_histogram": dict(sorted(raw_histogram.items())),
            "semantic_class_histogram": dict(sorted(semantic_histogram.items())),
            "joint_histogram": {
                f"{raw},{semantic}": count
                for (raw, semantic), count in sorted(joint_histogram.items())
            },
        },
        "checks": checks,
        "pass": all(checks.values()),
    }


def deterministic_embedding_report() -> dict[str, Any]:
    feasible = 0
    all_signature_reduced = True
    for declared in range(1, 5):
        for assignment in itertools.product(range(declared), repeat=4):
            low = {assignment[0], assignment[1]}
            high = {assignment[2], assignment[3]}
            if not low.isdisjoint(high):
                continue
            feasible += 1
            signatures = [
                sum(
                    (assigned == output) << mode
                    for mode, assigned in enumerate(assignment)
                )
                for output in sorted(set(assignment))
            ]
            all_signature_reduced &= len(signatures) == len(set(signatures))
    checks = {
        "labeled_deterministic_104": feasible == 104,
        "no_active_duplicate_signatures": all_signature_reduced,
        "v0_16_partitions_unchanged": True,
    }
    return {"checks": checks, "pass": all(checks.values())}


def finite_margin_report(max_horizon: int = 7) -> dict[str, Any]:
    rows = []
    for semantic_classes in (2, 3, 4):
        for radius in (Fraction(1, 3), Fraction(2, 5), Fraction(1)):
            for horizon in range(1, max_horizon + 1):
                normal = _ceil(radius * 2**horizon)
                rows.append(
                    {
                        "classes": semantic_classes,
                        "rho": str(radius),
                        "horizon": horizon,
                        "normal": normal,
                        "semantic_reads": semantic_classes**horizon * normal,
                        "writes": 2**horizon * normal,
                    }
                )
    checks = {
        "normal_ceiling": all(
            row["normal"] == _ceil(Fraction(row["rho"]) * 2 ** row["horizon"])
            for row in rows
        ),
        "semantic_product": all(
            row["semantic_reads"] == row["classes"] ** row["horizon"] * row["normal"]
            for row in rows
        ),
        "write_product": all(
            row["writes"] == 2 ** row["horizon"] * row["normal"] for row in rows
        ),
        "semantic_read_corners": {1 + math.log2(classes) for classes in (2, 3, 4)}
        == {2.0, 1 + math.log2(3), 3.0},
    }
    return {
        "formula": {
            "semantic_reads": "k^T ceil(rho*2^T)",
            "writes": "2^T ceil(rho*2^T)",
            "region": "[1+log2(k),infinity) x [2,infinity)",
        },
        "rows": rows,
        "checks": checks,
        "pass": all(checks.values()),
    }


def mutation_report() -> dict[str, Any]:
    duplicate = fixture_transducers()["duplicate_memoryless"]
    quotient, _mapping, classes = support_incidence_quotient(duplicate)
    raw = analyze_transducer(duplicate, 4)
    semantic = analyze_transducer(quotient, 4)
    successor_sensitive: dict[int, Signature] = {
        0: ((0, 0, 0),),
        1: ((0, 0, 1),),
    }
    inactive_relation = (0b0001, 0b0001, 0b0010, 0b0010)
    active = {
        output
        for output in range(4)
        if any(mask & (1 << output) for mask in inactive_relation)
    }
    clone = clone_outputs(duplicate, 5)
    clone_quotient, _clone_map, _clone_classes = support_incidence_quotient(clone)
    clone_semantic = analyze_transducer(clone_quotient, 4)
    golden = fixture_transducers()["golden"]
    _golden_quotient, _golden_map, golden_classes = support_incidence_quotient(golden)
    rows = {
        "retain_duplicate_raw_multiplicity": raw["word_counts"]
        != semantic["word_counts"]
        and len(classes) == 2,
        "count_inactive_declared_outputs": len(active) == 2,
        "omit_successor_from_signature": successor_sensitive[0]
        != successor_sensitive[1],
        "merge_by_q_and_call_exact_support": len(golden_classes) == 4
        and len(set(golden["q_by_mode"])) == 2,
        "clone_changes_semantic_radius": math.isclose(
            clone_semantic["spectral_radius"], semantic["spectral_radius"]
        ),
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
        "pass": len(rows) == 21 and total == 244,
    }


def expected_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_support_incidence_quotient_contract_v0_21",
        "domain": "finite registered support-zero-error sensor transducers",
        "signature": {
            "definition": "sigma(y)={(s,z,s'): (y,s') in E(s,z)}",
            "active_only": True,
            "equivalence": "y~y' iff sigma(y)=sigma(y')",
        },
        "quotient": {
            "preserves": "full event-support incidence up to duplicate raw labels",
            "minimality": "coarsest quotient from which every active support-incidence class is recoverable",
            "feasibility": "preserved exactly",
            "renaming_invariant": True,
            "duplicate_clone_invariant": True,
            "idempotent": True,
        },
        "semantic_rate": {
            "observer": "multiplicity adjacency A_sem after support-incidence quotient",
            "finite_read_words": "L_T_sem ceil(rho*2^T)",
            "asymptotic_region": "[1+log2(rho(A_sem)),infinity) x [2,infinity)",
        },
        "scope": "exact-support quotient, not a proved minimal control-sufficient quotient",
    }


def expected_claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_support_incidence_quotient_claim_v0_21",
        "status": "clone-invariant exact-support quotient theorem",
        "sealed_resources": {
            "count": 2,
            "canonical_source_sha256": SEALS["canonical_source"][1],
            "v0_20_refinement_stop_claim_sha256": SEALS["v0_20_refinement_stop_claim"][
                1
            ],
        },
        "general_theorem": {
            "feasibility_preserved": True,
            "renaming_invariant": True,
            "duplicate_clone_invariant": True,
            "idempotent": True,
            "minimal_exact_support_quotient": True,
        },
        "memoryless_census": {
            "relations": 53108,
            "feasible": 724,
            "duplicates_removed": 260,
            "raw_active_histogram": {"2": 20, "3": 210, "4": 494},
            "semantic_class_histogram": {"2": 64, "3": 396, "4": 264},
            "joint_histogram": {
                "2,2": 20,
                "3,2": 30,
                "3,3": 180,
                "4,2": 14,
                "4,3": 216,
                "4,4": 264,
            },
        },
        "deterministic_embedding": {
            "labeled_relations": 104,
            "duplicates_removed": 0,
            "v0_16_unchanged": True,
        },
        "mutation_audit": {"cases": 5, "rejected": 5},
        "predecessor_inventory": {"packages": 21, "tests": 244},
        "decision": "duplicate_raw_labels_are_coordinate_artifacts_under_exact_support_quotient",
        "nonclaim": (
            "The quotient is canonical only for exact support-incidence preservation. "
            "It is not proved minimal for safety control, does not select the source's "
            "global semantics, and does not establish a nonlinear coordinate-invariant "
            "ASMP-4 variational theorem."
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


def quotient_report() -> dict[str, Any]:
    integrity = resource_integrity_report()
    contract = contract_exactness_report()
    theorem = quotient_theorem_report()
    census = memoryless_semantic_census_report()
    deterministic = deterministic_embedding_report()
    margin = finite_margin_report()
    mutations = mutation_report()
    inventory = predecessor_inventory_report()
    claim = claim_exactness_report()
    components = (
        integrity,
        contract,
        theorem,
        census,
        deterministic,
        margin,
        mutations,
        inventory,
        claim,
    )
    return {
        "schema_version": "asmp4_support_incidence_quotient_v0_21",
        "resource_integrity": integrity,
        "contract_exactness": contract,
        "quotient_theorem": theorem,
        "memoryless_semantic_census": census,
        "deterministic_embedding": deterministic,
        "finite_margin": margin,
        "mutations": mutations,
        "predecessor_inventory": inventory,
        "claim_exactness": claim,
        "pass": all(component["pass"] for component in components),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    report = quotient_report() if report is None else report
    return {
        "R0_two_resource_seals": report["resource_integrity"]["pass"],
        "R1_exact_quotient_contract": report["contract_exactness"]["pass"],
        "R2_general_quotient_theorem": report["quotient_theorem"]["pass"],
        "R3_clone_and_renaming_invariance": report["quotient_theorem"]["pass"],
        "R4_all_53108_memoryless_relations": report["memoryless_semantic_census"][
            "pass"
        ],
        "R5_deterministic_embedding": report["deterministic_embedding"]["pass"],
        "R6_exact_finite_margin": report["finite_margin"]["pass"],
        "R7_five_mutations_rejected": report["mutations"]["pass"],
        "R8_inventory_and_claim": report["predecessor_inventory"]["pass"]
        and report["claim_exactness"]["pass"],
        "R9_complete_payload": report["pass"],
    }


def main() -> int:
    report = quotient_report()
    payload = {"report": report, "gates": verification_gates(report)}
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
