from __future__ import annotations

from fractions import Fraction
from typing import Sequence


def q(value) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(str(value))


def dot(left: Sequence, right: Sequence) -> Fraction:
    if len(left) != len(right):
        raise ValueError("dimension mismatch")
    return sum((q(a) * q(b) for a, b in zip(left, right)), Fraction(0))


def subtract(left: Sequence, right: Sequence) -> tuple[Fraction, ...]:
    if len(left) != len(right):
        raise ValueError("dimension mismatch")
    return tuple(q(a) - q(b) for a, b in zip(left, right))


def squared_norm(vector: Sequence) -> Fraction:
    return dot(vector, vector)


def solve_square(matrix: Sequence[Sequence], rhs: Sequence) -> tuple[Fraction, ...]:
    rows = [list(map(q, row)) + [q(value)] for row, value in zip(matrix, rhs)]
    size = len(rows)
    if size == 0:
        return ()
    if len(rhs) != size or any(len(row) != size + 1 for row in rows):
        raise ValueError("square system required")
    for column in range(size):
        pivot = next(
            (index for index in range(column, size) if rows[index][column]),
            None,
        )
        if pivot is None:
            raise ValueError("singular gauge Gram matrix")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        pivot_value = rows[column][column]
        rows[column] = [value / pivot_value for value in rows[column]]
        for index in range(size):
            if index == column or rows[index][column] == 0:
                continue
            factor = rows[index][column]
            rows[index] = [
                value - factor * pivot_entry
                for value, pivot_entry in zip(rows[index], rows[column])
            ]
    return tuple(row[-1] for row in rows)


def quotient_residual(
    estimated_reward: Sequence,
    true_reward: Sequence,
    gauge_basis: Sequence[Sequence],
) -> tuple[Fraction, ...]:
    """Return the minimum-Euclidean-norm representative of estimate minus truth."""
    error = subtract(estimated_reward, true_reward)
    if not gauge_basis:
        return error
    basis = [tuple(map(q, row)) for row in gauge_basis]
    if any(len(row) != len(error) for row in basis):
        raise ValueError("gauge dimension mismatch")
    gram = [[dot(left, right) for right in basis] for left in basis]
    rhs = [dot(row, error) for row in basis]
    coefficients = solve_square(gram, rhs)
    projection = tuple(
        sum(
            (coefficient * row[index] for coefficient, row in zip(coefficients, basis)),
            Fraction(0),
        )
        for index in range(len(error))
    )
    residual = subtract(error, projection)
    if any(dot(row, residual) for row in basis):
        raise RuntimeError("quotient projection failed exact orthogonality")
    return residual


def decision_gauge_valid(
    policy_occupancies: Sequence[Sequence],
    gauge_basis: Sequence[Sequence],
) -> bool:
    if not policy_occupancies:
        raise ValueError("at least one policy is required")
    width = len(policy_occupancies[0])
    if width == 0 or any(len(row) != width for row in policy_occupancies):
        raise ValueError("policy occupancy matrix must be rectangular")
    if any(len(row) != width for row in gauge_basis):
        raise ValueError("gauge dimension mismatch")
    reference = policy_occupancies[0]
    return all(
        dot(subtract(policy, reference), gauge) == 0
        for policy in policy_occupancies[1:]
        for gauge in gauge_basis
    )


def first_argmax(values: Sequence[Fraction]) -> int:
    if not values:
        raise ValueError("at least one value is required")
    maximum = max(values)
    return next(index for index, value in enumerate(values) if value == maximum)


def policy_values(
    policy_occupancies: Sequence[Sequence], reward: Sequence
) -> tuple[Fraction, ...]:
    return tuple(dot(policy, reward) for policy in policy_occupancies)


def global_diameter_squared(policy_occupancies: Sequence[Sequence]) -> Fraction:
    return max(
        squared_norm(subtract(left, right))
        for left in policy_occupancies
        for right in policy_occupancies
    )


def evaluate_plugin_policy(
    policy_occupancies: Sequence[Sequence],
    true_reward: Sequence,
    estimated_reward: Sequence,
    gauge_basis: Sequence[Sequence],
) -> dict:
    gauge_valid = decision_gauge_valid(policy_occupancies, gauge_basis)
    if not gauge_valid:
        return {
            "status": "decision_gauge_invalid",
            "certificate_available": False,
        }
    true_values = policy_values(policy_occupancies, true_reward)
    estimated_values = policy_values(policy_occupancies, estimated_reward)
    true_policy = first_argmax(true_values)
    selected_policy = first_argmax(estimated_values)
    regret = true_values[true_policy] - true_values[selected_policy]
    residual = quotient_residual(estimated_reward, true_reward, gauge_basis)
    delta_squared = squared_norm(residual)
    diameter_squared = global_diameter_squared(policy_occupancies)
    selected_difference = subtract(
        policy_occupancies[true_policy],
        policy_occupancies[selected_policy],
    )
    selected_diameter_squared = squared_norm(selected_difference)
    global_bound_squared = delta_squared * diameter_squared
    selected_bound_squared = delta_squared * selected_diameter_squared

    selected_certified = True
    margin_rows = []
    for competitor, competitor_value in enumerate(estimated_values):
        if competitor == selected_policy:
            continue
        margin = estimated_values[selected_policy] - competitor_value
        difference_squared = squared_norm(
            subtract(
                policy_occupancies[selected_policy],
                policy_occupancies[competitor],
            )
        )
        row_certified = (
            margin > 0 and margin * margin > delta_squared * difference_squared
        )
        selected_certified &= row_certified
        margin_rows.append(
            {
                "competitor": competitor,
                "difference_squared": difference_squared,
                "margin": margin,
                "policy_identity_certified": row_certified,
            }
        )
    return {
        "certificate_available": True,
        "delta_squared": delta_squared,
        "diameter_squared": diameter_squared,
        "estimated_policy": selected_policy,
        "global_bound_squared": global_bound_squared,
        "global_bound_valid": regret * regret <= global_bound_squared,
        "margin_rows": tuple(margin_rows),
        "policy_identity_certified": selected_certified,
        "regret": regret,
        "selected_bound_squared": selected_bound_squared,
        "selected_bound_valid": regret * regret <= selected_bound_squared,
        "selected_diameter_squared": selected_diameter_squared,
        "status": "evaluated",
        "true_policy": true_policy,
    }


def scaled_cardinal_target(
    policy_occupancies: Sequence[Sequence],
    reward: Sequence,
    evaluated_policy: int,
    scale_factors: Sequence,
    fixed_regret_threshold,
) -> tuple[dict, ...]:
    if not 0 <= evaluated_policy < len(policy_occupancies):
        raise IndexError("evaluated policy out of range")
    threshold = q(fixed_regret_threshold)
    rows = []
    for scale in map(q, scale_factors):
        if scale <= 0:
            raise ValueError("scale factors must be positive")
        scaled_reward = tuple(scale * q(value) for value in reward)
        values = policy_values(policy_occupancies, scaled_reward)
        optimum = first_argmax(values)
        regret = values[optimum] - values[evaluated_policy]
        rows.append(
            {
                "fixed_threshold_pass": regret <= threshold,
                "optimal_policy": optimum,
                "regret": regret,
                "scale": scale,
            }
        )
    return tuple(rows)
