from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def q(value):
    return value if isinstance(value, Fraction) else Fraction(str(value))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json_exclusive(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def dot(left, right):
    return sum((q(a) * q(b) for a, b in zip(left, right)), Fraction(0))


def rank(matrix):
    if not matrix:
        return 0
    rows = [list(map(q, row)) for row in matrix]
    width = len(rows[0])
    result = 0
    for column in range(width):
        pivot = next(
            (
                index
                for index in range(result, len(rows))
                if rows[index][column]
            ),
            None,
        )
        if pivot is None:
            continue
        rows[result], rows[pivot] = rows[pivot], rows[result]
        scale = rows[result][column]
        rows[result] = [value / scale for value in rows[result]]
        for index in range(len(rows)):
            if index == result:
                continue
            factor = rows[index][column]
            if factor:
                rows[index] = [
                    value - factor * pivot_value
                    for value, pivot_value in zip(rows[index], rows[result])
                ]
        result += 1
    return result


def normalized_mdp(spec):
    states = tuple(sorted(map(str, spec["states"])))
    if not states or len(states) != len(set(states)):
        raise ValueError("invalid states")
    action_sets = tuple(
        (state, tuple(sorted(map(str, spec["action_sets"][state]))))
        for state in states
    )
    actions = dict(action_sets)
    initial = tuple(
        (state, q(spec["initial_distribution"][state])) for state in states
    )
    if sum((value for _, value in initial), Fraction(0)) != 1:
        raise ValueError("invalid initial law")
    transitions = {}
    for row in spec["transitions"]:
        key = (
            str(row["state"]),
            str(row["action"]),
            str(row["next_state"]),
        )
        if key in transitions:
            raise ValueError("duplicate transition")
        transitions[key] = q(row["probability"])
    for state, candidates in action_sets:
        for action in candidates:
            if sum(
                (
                    value
                    for (source, candidate, _), value in transitions.items()
                    if source == state and candidate == action
                ),
                Fraction(0),
            ) != 1:
                raise ValueError("invalid transition law")
    features = {}
    for row in spec["features"]:
        key = (
            str(row["state"]),
            str(row["action"]),
            str(row["next_state"]),
        )
        features[key] = tuple(map(q, row["vector"]))
    if set(features) != set(transitions):
        raise ValueError("feature support mismatch")
    if any(
        len(vector) != int(spec["feature_dimension"])
        for vector in features.values()
    ):
        raise ValueError("feature dimension mismatch")
    return {
        "action_sets": action_sets,
        "feature_dimension": int(spec["feature_dimension"]),
        "features": tuple(sorted(features.items())),
        "horizon": int(spec["horizon"]),
        "initial_distribution": initial,
        "states": states,
        "transitions": tuple(sorted(transitions.items())),
    }


def independent_mutation(spec, mutation):
    result = deepcopy(spec)
    kind = mutation["kind"]
    if kind == "set_horizon":
        result["horizon"] = mutation["value"]
    elif kind == "add_action":
        result["action_sets"][mutation["state"]].append(mutation["action"])
        result["transitions"].extend(deepcopy(mutation["transitions"]))
        result["features"].extend(deepcopy(mutation["features"]))
    elif kind == "replace_transition_distribution":
        state, action = mutation["state"], mutation["action"]
        result["transitions"] = [
            row
            for row in result["transitions"]
            if not (row["state"] == state and row["action"] == action)
        ] + deepcopy(mutation["transitions"])
        result["features"] = [
            row
            for row in result["features"]
            if not (row["state"] == state and row["action"] == action)
        ] + deepcopy(mutation["features"])
    elif kind == "replace_feature":
        key = (
            mutation["state"],
            mutation["action"],
            mutation["next_state"],
        )
        for row in result["features"]:
            if (row["state"], row["action"], row["next_state"]) == key:
                row["vector"] = deepcopy(mutation["vector"])
                break
        else:
            raise ValueError("feature mutation target missing")
    else:
        raise ValueError("unknown mutation")
    normalized_mdp(result)
    return result


def policies_and_occupancies(spec):
    normalized = normalized_mdp(spec)
    actions = normalized["action_sets"]
    transitions = dict(normalized["transitions"])
    features = dict(normalized["features"])
    policies = tuple(
        dict(zip((state for state, _ in actions), choices))
        for choices in itertools.product(*(items for _, items in actions))
    )
    occupancies = []
    for policy in policies:
        distribution = dict(normalized["initial_distribution"])
        total = [Fraction(0)] * normalized["feature_dimension"]
        for _ in range(normalized["horizon"]):
            following = {state: Fraction(0) for state in normalized["states"]}
            for state, state_probability in distribution.items():
                action = policy[state]
                for target in normalized["states"]:
                    probability = transitions.get(
                        (state, action, target), Fraction(0)
                    )
                    mass = state_probability * probability
                    following[target] += mass
                    if mass:
                        for index, value in enumerate(
                            features[(state, action, target)]
                        ):
                            total[index] += mass * value
            distribution = following
        occupancies.append(tuple(total))
    return policies, tuple(occupancies)


def make_table(cell, offsets):
    table = [
        [
            q(base)
            + q(cell["common_constant"])
            + q(cell["coefficient"]) * offset
            for offset in offsets
        ]
        for base in cell["base_values"]
    ]
    for adjustment in cell["adjustments"]:
        table[int(adjustment["base_index"])][
            int(adjustment["level_index"])
        ] += q(adjustment["delta"])
    for row, column in cell["missing_cells"]:
        table[int(row)][int(column)] = None
    return tuple(tuple(row) for row in table)


def semantic_summary(table, offsets, reference):
    if any(value is None for row in table for value in row):
        return {
            "available": False,
            "classification": "incomplete_semantic_table",
        }
    residuals = tuple(
        tuple(
            q(value)
            - q(row[reference])
            - (offset - offsets[reference])
            for value, offset in zip(row, offsets)
        )
        for row in table
    )
    anchor = table[0]
    interactions = tuple(
        tuple(
            q(row[index])
            - q(row[reference])
            - q(anchor[index])
            + q(anchor[reference])
            for index in range(len(offsets))
        )
        for row in table
    )
    separable = all(value == 0 for row in interactions for value in row)
    calibrated = all(value == 0 for row in residuals for value in row)
    effects = tuple(
        q(value) - q(anchor[reference]) for value in anchor
    )
    declared = tuple(value - offsets[reference] for value in offsets)
    nonzero = [index for index, value in enumerate(declared) if value]
    coefficient = None
    proportional = False
    if nonzero:
        coefficient = effects[nonzero[0]] / declared[nonzero[0]]
        proportional = all(
            effects[index] == coefficient * declared[index]
            for index in range(len(offsets))
        )
    if calibrated:
        classification = "calibrated_additive"
    elif separable and proportional:
        classification = "separable_unknown_scale"
    elif separable:
        classification = "separable_unknown_offset_map"
    else:
        classification = "context_interaction"
    return {
        "available": True,
        "classification": classification,
        "coefficient": coefficient,
        "maximum_residual": max(
            abs(value) for row in residuals for value in row
        ),
        "residuals": residuals,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)

    registration = json.loads(args.registration.read_text())
    protocol = json.loads((REPO / registration["protocol_path"]).read_text())
    result = json.loads(args.result.read_text())
    receipt = json.loads(args.receipt.read_text())
    fresh = protocol["fresh_validation"]
    baseline = fresh["baseline_mdp"]
    normalized = normalized_mdp(baseline)
    offsets = tuple(map(q, fresh["declared_offsets"]))
    reference = int(fresh["reference_index"])
    checks = {}

    checks["registration_hash"] = (
        sha256(args.registration)
        == result["registration_sha256"]
        == receipt["registration_sha256"]
    )
    checks["result_hash"] = sha256(args.result) == receipt["result_sha256"]
    checks["protocol_hash"] = (
        sha256(REPO / registration["protocol_path"])
        == receipt["protocol_sha256"]
    )
    checks["sealed_files"] = all(
        sha256(REPO / relative) == expected
        for relative, expected in registration["sealed_files"].items()
    )
    checks["gate_universe"] = set(result["gate_passes"]) == set(
        protocol["gate_ids"]
    )
    checks["all_gates_pass"] = all(result["gate_passes"].values())
    checks["verdict"] = (
        result["verdict"] == protocol["verdict_map"]["all_gates_pass"]
    )

    policies, occupancies = policies_and_occupancies(baseline)
    checks["baseline_mdp"] = (
        normalized["horizon"] == 4
        and normalized["feature_dimension"] == 3
        and len(policies) == 4
    )
    checks["policy_occupancies"] = [
        [str(value) for value in row] for row in occupancies
    ] == result["policy_occupancies"]

    changed_rows = {}
    for control in fresh["mechanical_controls"]:
        mutated = independent_mutation(baseline, control["mutation"])
        candidate = normalized_mdp(mutated)
        changed = tuple(
            key for key in normalized if normalized[key] != candidate[key]
        )
        changed_rows[control["name"]] = tuple(sorted(changed))
    checks["mechanical_controls"] = all(
        changed_rows[control["name"]]
        == tuple(sorted(control["expected_changed_fields"]))
        for control in fresh["mechanical_controls"]
    )

    tables = {
        name: make_table(cell, offsets)
        for name, cell in fresh["semantic_cells"].items()
    }
    semantic = {
        name: semantic_summary(table, offsets, reference)
        for name, table in tables.items()
    }
    checks["calibrated_semantics"] = (
        semantic["calibrated"]["classification"]
        == "calibrated_additive"
        and semantic["calibrated"]["maximum_residual"] == 0
    )
    checks["semantic_controls"] = (
        semantic["unknown_scale"]["classification"]
        == "separable_unknown_scale"
        and semantic["unknown_scale"]["coefficient"] == Fraction(9, 7)
        and semantic["interaction"]["classification"]
        == "context_interaction"
        and semantic["incomplete"]["classification"]
        == "incomplete_semantic_table"
    )

    constraint = fresh["constraint_cell"]
    base_count = int(constraint["base_object_count"])
    level_count = int(constraint["consequence_count"])
    constraint_reference = int(constraint["reference_index"])
    matrix = []
    for base_index in range(base_count):
        for level_index in range(level_count):
            if level_index == constraint_reference:
                continue
            row = [Fraction(0)] * (base_count * level_count)
            row[base_index * level_count + level_index] = 1
            row[base_index * level_count + constraint_reference] = -1
            matrix.append(tuple(row))
    checks["constraint_rank"] = (
        rank(matrix) == len(matrix) == base_count * (level_count - 1)
    )
    omission_valid = True
    row_index = 0
    for base_index in range(base_count):
        for level_index in range(level_count):
            if level_index == constraint_reference:
                continue
            witness = [Fraction(0)] * (base_count * level_count)
            witness[base_index * level_count + level_index] = 1
            evaluations = tuple(dot(row, witness) for row in matrix)
            omission_valid &= (
                evaluations[row_index] == 1
                and all(
                    value == 0
                    for index, value in enumerate(evaluations)
                    if index != row_index
                )
            )
            row_index += 1
    checks["constraint_omissions"] = omission_valid

    population = fresh["population_cell"]
    radius = q(population["radius"])
    coefficient = q(population["coefficient"])
    baseline_law = tuple(
        tuple(
            Fraction(1, 2)
            + (q(base) + coefficient * offset) / (2 * radius)
            for offset in offsets
        )
        for base in population["base_values"]
    )
    scale_laws = []
    for alpha_value in population["scale_factors"]:
        alpha = q(alpha_value)
        scale_laws.append(
            tuple(
                tuple(
                    Fraction(1, 2)
                    + (
                        alpha * q(base)
                        + alpha * coefficient * offset
                    )
                    / alpha
                    / (2 * radius)
                    for offset in offsets
                )
                for base in population["base_values"]
            )
        )
    checks["unknown_scale_coupling"] = all(
        law == baseline_law for law in scale_laws
    )
    checks["mechanics_semantic_no_go"] = (
        len(
            {
                semantic[name]["classification"]
                for name in ("calibrated", "unknown_scale", "interaction")
            }
        )
        == 3
    )

    approximate = fresh["approximate_cell"]
    residuals = tuple(
        tuple(map(q, row)) for row in approximate["residuals"]
    )
    epsilon = q(approximate["epsilon"])
    max_residual = max(abs(value) for row in residuals for value in row)
    max_bias = max(
        abs(left - right)
        for left in itertools.chain.from_iterable(residuals)
        for right in itertools.chain.from_iterable(residuals)
    )
    checks["approximate_bound"] = (
        max_residual == epsilon and max_bias <= 2 * epsilon
    )
    checks["approximate_sharpness"] = max_bias == 2 * epsilon

    structural_positive = all(
        normalized_mdp(deepcopy(baseline)) == normalized
        for _ in offsets
    )
    checks["eligibility_positive"] = (
        structural_positive
        and semantic["calibrated"]["classification"]
        == "calibrated_additive"
    )
    checks["eligibility_negative_controls"] = (
        semantic["unknown_scale"]["classification"]
        != "calibrated_additive"
        and not semantic["incomplete"]["available"]
        and all(bool(changed) for changed in changed_rows.values())
    )

    identifiers = {row["identifier"] for row in protocol["prior_art"]}
    checks["prior_art"] = identifiers == {
        "DOI:10.1016/0022-2496(64)90015-X",
        "Krantz-Luce-Suppes-Tversky-1971",
        "ICML-1999-Ng-Harada-Russell",
        "PMLR:80:1262-1270",
        "PMLR:202:32033-32058",
        "PMLR:235:24808-24828",
        "ASMP-9-v0.28",
        "ASMP-9-v0.29",
    }
    checks["claim_boundary"] = (
        "ASMP-9 is resolved."
        in protocol["structured_claims"]["forbidden"]
        and "no novelty is claimed" in protocol["claim_boundary"]
    )
    checks["resource_caps"] = (
        receipt["wall_seconds"] <= protocol["resource_caps"]["wall_seconds"]
        and receipt["peak_resident_bytes"]
        <= protocol["resource_caps"]["peak_resident_bytes"]
        and not protocol["resource_caps"]["gpu_allowed"]
    )

    output = {
        "check_count": len(checks),
        "checks": checks,
        "pass": all(checks.values()),
        "receipt_sha256": sha256(args.receipt),
        "result_sha256": sha256(args.result),
        "verifier_sha256": sha256(Path(__file__)),
    }
    write_json_exclusive(args.output, output)
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
