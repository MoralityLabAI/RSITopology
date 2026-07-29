from __future__ import annotations

import hashlib
import itertools
import json
from copy import deepcopy
from fractions import Fraction
from typing import Any, Mapping, Sequence


def q(value: Any) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(str(value))


def fraction_text(value: Any) -> str:
    value = q(value)
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def _unique_strings(values: Sequence, label: str) -> tuple[str, ...]:
    result = tuple(str(value) for value in values)
    if not result or len(result) != len(set(result)):
        raise ValueError(f"{label} must be nonempty and unique")
    return result


def normalize_mdp(spec: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and canonically normalize a stationary finite feature MDP."""
    states = tuple(sorted(_unique_strings(spec["states"], "states")))
    state_set = set(states)
    horizon = int(spec["horizon"])
    feature_dimension = int(spec["feature_dimension"])
    if horizon <= 0:
        raise ValueError("horizon must be positive")
    if feature_dimension <= 0:
        raise ValueError("feature_dimension must be positive")

    initial_raw = spec["initial_distribution"]
    if set(map(str, initial_raw)) != state_set:
        raise ValueError("initial distribution must cover exactly the states")
    initial = tuple(
        (state, q(initial_raw[state]))
        for state in states
    )
    if any(probability < 0 for _, probability in initial):
        raise ValueError("initial probabilities must be nonnegative")
    if sum((probability for _, probability in initial), Fraction(0)) != 1:
        raise ValueError("initial probabilities must sum to one")

    action_raw = spec["action_sets"]
    if set(map(str, action_raw)) != state_set:
        raise ValueError("action_sets must cover exactly the states")
    action_sets = tuple(
        (
            state,
            tuple(sorted(_unique_strings(action_raw[state], f"actions[{state}]"))),
        )
        for state in states
    )
    action_lookup = dict(action_sets)

    transition_map: dict[tuple[str, str, str], Fraction] = {}
    for row in spec["transitions"]:
        source = str(row["state"])
        action = str(row["action"])
        target = str(row["next_state"])
        probability = q(row["probability"])
        if source not in state_set or target not in state_set:
            raise ValueError("transition contains an unknown state")
        if action not in action_lookup[source]:
            raise ValueError("transition contains an unavailable action")
        if probability < 0:
            raise ValueError("transition probabilities must be nonnegative")
        key = (source, action, target)
        if key in transition_map:
            raise ValueError("duplicate transition row")
        transition_map[key] = probability

    for state, actions in action_sets:
        for action in actions:
            total = sum(
                (
                    probability
                    for (source, candidate, _), probability
                    in transition_map.items()
                    if source == state and candidate == action
                ),
                Fraction(0),
            )
            if total != 1:
                raise ValueError(
                    f"transition probabilities for {(state, action)} "
                    "must sum to one"
                )

    feature_map: dict[tuple[str, str, str], tuple[Fraction, ...]] = {}
    for row in spec["features"]:
        key = (
            str(row["state"]),
            str(row["action"]),
            str(row["next_state"]),
        )
        vector = tuple(q(value) for value in row["vector"])
        if len(vector) != feature_dimension:
            raise ValueError("feature vector dimension mismatch")
        if key in feature_map:
            raise ValueError("duplicate feature row")
        feature_map[key] = vector
    if set(feature_map) != set(transition_map):
        raise ValueError("features must cover exactly the transition support")

    return {
        "action_sets": action_sets,
        "feature_dimension": feature_dimension,
        "features": tuple(sorted(feature_map.items())),
        "horizon": horizon,
        "initial_distribution": initial,
        "states": states,
        "transitions": tuple(sorted(transition_map.items())),
    }


def _jsonable_normalized(value: Any) -> Any:
    if isinstance(value, Fraction):
        return fraction_text(value)
    if isinstance(value, dict):
        return {
            key: _jsonable_normalized(item)
            for key, item in sorted(value.items())
        }
    if isinstance(value, (tuple, list)):
        return [_jsonable_normalized(item) for item in value]
    return value


def mechanics_hash(spec: Mapping[str, Any]) -> str:
    normalized = _jsonable_normalized(normalize_mdp(spec))
    payload = json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def structural_conservativity(
    baseline: Mapping[str, Any],
    interventions: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    if not interventions:
        raise ValueError("at least one intervention level is required")
    baseline_normalized = normalize_mdp(baseline)
    rows = []
    levels = []
    for intervention in interventions:
        level = str(intervention["level"])
        if level in levels:
            raise ValueError("intervention levels must be unique")
        levels.append(level)
        normalized = normalize_mdp(intervention["mdp"])
        changed_fields = tuple(
            key
            for key in baseline_normalized
            if normalized[key] != baseline_normalized[key]
        )
        rows.append(
            {
                "changed_fields": changed_fields,
                "level": level,
                "mechanics_hash": mechanics_hash(intervention["mdp"]),
                "structurally_conservative": not changed_fields,
            }
        )
    return {
        "baseline_mechanics_hash": mechanics_hash(baseline),
        "intervention_rows": tuple(rows),
        "status": (
            "structurally_conservative"
            if all(row["structurally_conservative"] for row in rows)
            else "structurally_nonconservative"
        ),
        "structurally_conservative": all(
            row["structurally_conservative"] for row in rows
        ),
    }


def apply_registered_mutation(
    spec: Mapping[str, Any],
    mutation: Mapping[str, Any],
) -> dict[str, Any]:
    """Apply one sealed mechanical control mutation and validate the result."""
    result = deepcopy(dict(spec))
    kind = str(mutation["kind"])
    if kind == "set_horizon":
        result["horizon"] = int(mutation["value"])
    elif kind == "add_action":
        state = str(mutation["state"])
        action = str(mutation["action"])
        result["action_sets"][state].append(action)
        result["transitions"].extend(deepcopy(mutation["transitions"]))
        result["features"].extend(deepcopy(mutation["features"]))
    elif kind == "replace_transition_distribution":
        state = str(mutation["state"])
        action = str(mutation["action"])
        result["transitions"] = [
            row
            for row in result["transitions"]
            if not (
                str(row["state"]) == state
                and str(row["action"]) == action
            )
        ]
        result["features"] = [
            row
            for row in result["features"]
            if not (
                str(row["state"]) == state
                and str(row["action"]) == action
            )
        ]
        result["transitions"].extend(deepcopy(mutation["transitions"]))
        result["features"].extend(deepcopy(mutation["features"]))
    elif kind == "replace_feature":
        key = (
            str(mutation["state"]),
            str(mutation["action"]),
            str(mutation["next_state"]),
        )
        matches = [
            row
            for row in result["features"]
            if (
                str(row["state"]),
                str(row["action"]),
                str(row["next_state"]),
            )
            == key
        ]
        if len(matches) != 1:
            raise ValueError("replace_feature requires one matching row")
        matches[0]["vector"] = deepcopy(mutation["vector"])
    else:
        raise ValueError(f"unknown registered mutation kind: {kind}")
    normalize_mdp(result)
    return result


def deterministic_stationary_policies(
    spec: Mapping[str, Any],
) -> tuple[tuple[tuple[str, str], ...], ...]:
    normalized = normalize_mdp(spec)
    action_sets = normalized["action_sets"]
    return tuple(
        tuple(
            (state, action)
            for (state, _), action in zip(action_sets, choices)
        )
        for choices in itertools.product(
            *(actions for _, actions in action_sets)
        )
    )


def expected_feature_occupancy(
    spec: Mapping[str, Any],
    policy: Sequence[Sequence[str]],
) -> tuple[Fraction, ...]:
    normalized = normalize_mdp(spec)
    policy_map = {str(state): str(action) for state, action in policy}
    if set(policy_map) != set(normalized["states"]):
        raise ValueError("policy must choose one action in every state")
    action_lookup = dict(normalized["action_sets"])
    for state, action in policy_map.items():
        if action not in action_lookup[state]:
            raise ValueError("policy selects an unavailable action")

    transitions = dict(normalized["transitions"])
    features = dict(normalized["features"])
    distribution = dict(normalized["initial_distribution"])
    total = [Fraction(0)] * normalized["feature_dimension"]
    for _ in range(normalized["horizon"]):
        next_distribution = {
            state: Fraction(0) for state in normalized["states"]
        }
        for state, state_probability in distribution.items():
            action = policy_map[state]
            for target in normalized["states"]:
                probability = transitions.get(
                    (state, action, target), Fraction(0)
                )
                mass = state_probability * probability
                next_distribution[target] += mass
                if mass:
                    vector = features[(state, action, target)]
                    for index, value in enumerate(vector):
                        total[index] += mass * value
        distribution = next_distribution
    return tuple(total)


def semantic_calibration(
    declared_offsets: Sequence,
    value_table: Sequence[Sequence],
    reference_index: int = 0,
) -> dict[str, Any]:
    offsets = tuple(q(value) for value in declared_offsets)
    if not offsets:
        raise ValueError("at least one consequence level is required")
    if not 0 <= reference_index < len(offsets):
        raise IndexError("reference_index out of range")
    if not value_table:
        raise ValueError("at least one base object is required")
    if any(len(row) != len(offsets) for row in value_table):
        raise ValueError("value table must be rectangular")
    if any(value is None for row in value_table for value in row):
        return {
            "available": False,
            "classification": "incomplete_semantic_table",
            "complete": False,
        }

    values = tuple(tuple(q(value) for value in row) for row in value_table)
    reference_offset = offsets[reference_index]
    residuals = []
    interactions = []
    for row in values:
        base = row[reference_index]
        residuals.append(
            tuple(
                value - base - (offset - reference_offset)
                for value, offset in zip(row, offsets)
            )
        )
    anchor = values[0]
    for row in values:
        interactions.append(
            tuple(
                row[index]
                - row[reference_index]
                - anchor[index]
                + anchor[reference_index]
                for index in range(len(offsets))
            )
        )

    separable = all(
        value == 0 for row in interactions for value in row
    )
    calibrated = all(value == 0 for row in residuals for value in row)
    column_effects = tuple(
        value - anchor[reference_index] for value in anchor
    )
    declared_effects = tuple(
        value - reference_offset for value in offsets
    )
    nonzero_indices = [
        index
        for index, effect in enumerate(declared_effects)
        if effect != 0
    ]
    coefficient = None
    proportional = False
    if nonzero_indices:
        first = nonzero_indices[0]
        coefficient = column_effects[first] / declared_effects[first]
        proportional = all(
            (
                column_effects[index]
                == coefficient * declared_effects[index]
            )
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
    maximum_residual = max(
        abs(value) for row in residuals for value in row
    )
    return {
        "available": True,
        "calibrated": calibrated,
        "classification": classification,
        "column_effects": column_effects,
        "complete": True,
        "declared_effects": declared_effects,
        "interaction_residuals": tuple(interactions),
        "maximum_calibration_residual": maximum_residual,
        "proportional_coefficient": coefficient,
        "residuals": tuple(residuals),
        "separable": separable,
    }


def build_value_table(
    base_values: Sequence,
    declared_offsets: Sequence,
    coefficient: Any = 1,
    common_constant: Any = 0,
    adjustments: Sequence[Mapping[str, Any]] = (),
    missing_cells: Sequence[Sequence[int]] = (),
) -> tuple[tuple[Fraction | None, ...], ...]:
    bases = tuple(q(value) for value in base_values)
    offsets = tuple(q(value) for value in declared_offsets)
    if not bases or not offsets:
        raise ValueError("base_values and declared_offsets must be nonempty")
    coefficient = q(coefficient)
    common_constant = q(common_constant)
    table: list[list[Fraction | None]] = [
        [
            base + common_constant + coefficient * offset
            for offset in offsets
        ]
        for base in bases
    ]
    adjusted = set()
    for adjustment in adjustments:
        index = (
            int(adjustment["base_index"]),
            int(adjustment["level_index"]),
        )
        if index in adjusted:
            raise ValueError("duplicate adjustment")
        adjusted.add(index)
        row, column = index
        if not 0 <= row < len(bases) or not 0 <= column < len(offsets):
            raise IndexError("adjustment index out of range")
        value = table[row][column]
        if value is None:
            raise RuntimeError("unexpected missing cell before adjustment")
        table[row][column] = value + q(adjustment["delta"])
    missing = set()
    for item in missing_cells:
        if len(item) != 2:
            raise ValueError("missing cell must contain two indices")
        index = (int(item[0]), int(item[1]))
        if index in missing:
            raise ValueError("duplicate missing cell")
        missing.add(index)
        row, column = index
        if not 0 <= row < len(bases) or not 0 <= column < len(offsets):
            raise IndexError("missing-cell index out of range")
        table[row][column] = None
    return tuple(tuple(row) for row in table)


def pairwise_offset_bias_audit(
    declared_offsets: Sequence,
    value_table: Sequence[Sequence],
    reference_index: int = 0,
) -> dict[str, Any]:
    calibration = semantic_calibration(
        declared_offsets,
        value_table,
        reference_index,
    )
    if not calibration["available"]:
        return {
            "available": False,
            "status": "incomplete_semantic_table",
        }
    residuals = calibration["residuals"]
    epsilon = calibration["maximum_calibration_residual"]
    maximum_bias = Fraction(0)
    maximizer = None
    for left_row, right_row, left_level, right_level in itertools.product(
        range(len(residuals)),
        range(len(residuals)),
        range(len(residuals[0])),
        range(len(residuals[0])),
    ):
        bias = (
            residuals[left_row][left_level]
            - residuals[right_row][right_level]
        )
        if abs(bias) > maximum_bias:
            maximum_bias = abs(bias)
            maximizer = (
                left_row,
                right_row,
                left_level,
                right_level,
            )
    return {
        "available": True,
        "bound": 2 * epsilon,
        "bound_valid": maximum_bias <= 2 * epsilon,
        "maximum_pairwise_bias": maximum_bias,
        "maximizer": maximizer,
        "single_cell_residual_bound": epsilon,
    }


def calibration_constraint_matrix(
    base_object_count: int,
    consequence_count: int,
    reference_index: int = 0,
) -> tuple[tuple[Fraction, ...], ...]:
    if base_object_count <= 0 or consequence_count <= 0:
        raise ValueError("table dimensions must be positive")
    if not 0 <= reference_index < consequence_count:
        raise IndexError("reference_index out of range")
    width = base_object_count * consequence_count
    rows = []
    for base_index in range(base_object_count):
        for level_index in range(consequence_count):
            if level_index == reference_index:
                continue
            row = [Fraction(0)] * width
            row[base_index * consequence_count + level_index] = Fraction(1)
            row[base_index * consequence_count + reference_index] = Fraction(-1)
            rows.append(tuple(row))
    return tuple(rows)


def rational_rank(matrix: Sequence[Sequence]) -> int:
    if not matrix:
        return 0
    rows = [list(map(q, row)) for row in matrix]
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("matrix must be rectangular")
    rank = 0
    for column in range(width):
        pivot = next(
            (
                index
                for index in range(rank, len(rows))
                if rows[index][column]
            ),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [value / scale for value in rows[rank]]
        for index in range(len(rows)):
            if index == rank or rows[index][column] == 0:
                continue
            factor = rows[index][column]
            rows[index] = [
                value - factor * pivot_value
                for value, pivot_value in zip(rows[index], rows[rank])
            ]
        rank += 1
        if rank == len(rows):
            break
    return rank


def omitted_constraint_witness(
    base_object_count: int,
    consequence_count: int,
    omitted_base_index: int,
    omitted_level_index: int,
    reference_index: int = 0,
) -> tuple[tuple[Fraction, ...], ...]:
    if omitted_level_index == reference_index:
        raise ValueError("the reference column is not a calibration constraint")
    if not 0 <= omitted_base_index < base_object_count:
        raise IndexError("omitted_base_index out of range")
    if not 0 <= omitted_level_index < consequence_count:
        raise IndexError("omitted_level_index out of range")
    table = [
        [Fraction(0)] * consequence_count
        for _ in range(base_object_count)
    ]
    table[omitted_base_index][omitted_level_index] = Fraction(1)
    return tuple(tuple(row) for row in table)


def rational_midpoint_link(argument: Any, radius: Any) -> Fraction:
    argument = q(argument)
    radius = q(radius)
    if radius <= 0 or abs(argument) > radius:
        raise ValueError("argument must lie in the declared link radius")
    return Fraction(1, 2) + argument / (2 * radius)


def semantic_population_law(
    base_values: Sequence,
    declared_offsets: Sequence,
    coefficient: Any,
    radius: Any,
) -> tuple[tuple[Fraction, ...], ...]:
    coefficient = q(coefficient)
    return tuple(
        tuple(
            rational_midpoint_link(
                q(base_value) + coefficient * q(offset),
                radius,
            )
            for offset in declared_offsets
        )
        for base_value in base_values
    )


def rescaled_semantic_population_law(
    base_values: Sequence,
    declared_offsets: Sequence,
    coefficient: Any,
    alpha: Any,
    radius: Any,
) -> tuple[tuple[Fraction, ...], ...]:
    alpha = q(alpha)
    if alpha <= 0:
        raise ValueError("alpha must be positive")
    coefficient = q(coefficient)
    return tuple(
        tuple(
            rational_midpoint_link(
                (
                    alpha * q(base_value)
                    + alpha * coefficient * q(offset)
                )
                / alpha,
                radius,
            )
            for offset in declared_offsets
        )
        for base_value in base_values
    )


def v028_eligibility(
    baseline: Mapping[str, Any],
    interventions: Sequence[Mapping[str, Any]],
    declared_offsets: Sequence,
    value_table: Sequence[Sequence],
    reference_index: int = 0,
) -> dict[str, Any]:
    structural = structural_conservativity(baseline, interventions)
    semantic = semantic_calibration(
        declared_offsets,
        value_table,
        reference_index,
    )
    eligible = (
        structural["structurally_conservative"]
        and semantic["available"]
        and semantic["classification"] == "calibrated_additive"
    )
    reasons = []
    if not structural["structurally_conservative"]:
        reasons.append("mechanics_not_conservative")
    if not semantic["available"]:
        reasons.append("semantic_table_incomplete")
    elif semantic["classification"] != "calibrated_additive":
        reasons.append("semantic_calibration_not_established")
    return {
        "eligible": eligible,
        "reasons": tuple(reasons),
        "semantic": semantic,
        "structural": structural,
    }
