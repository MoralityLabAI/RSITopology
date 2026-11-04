"""Exact finite-MDP reward-access geometry for ASMP-9 v0.10."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import Iterable, Sequence


Matrix = tuple[tuple[Fraction, ...], ...]
TransitionKernel = tuple[
    tuple[tuple[Fraction, ...], ...], ...
]  # state, action, next_state


def as_fraction_matrix(rows: Iterable[Iterable[object]]) -> Matrix:
    return tuple(tuple(Fraction(value) for value in row) for row in rows)


def matrix_rank(matrix: Sequence[Sequence[object]]) -> int:
    work = [list(map(Fraction, row)) for row in matrix]
    if not work:
        return 0
    width = len(work[0])
    if any(len(row) != width for row in work):
        raise ValueError("ragged matrix")
    rank = 0
    for column in range(width):
        pivot = next(
            (
                row
                for row in range(rank, len(work))
                if work[row][column] != 0
            ),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        divisor = work[rank][column]
        work[rank] = [value / divisor for value in work[rank]]
        for row in range(len(work)):
            if row == rank or work[row][column] == 0:
                continue
            multiplier = work[row][column]
            work[row] = [
                left - multiplier * right
                for left, right in zip(work[row], work[rank])
            ]
        rank += 1
        if rank == len(work):
            break
    return rank


def nullspace_basis(matrix: Sequence[Sequence[object]]) -> Matrix:
    work = [list(map(Fraction, row)) for row in matrix]
    if not work:
        return ()
    width = len(work[0])
    if any(len(row) != width for row in work):
        raise ValueError("ragged matrix")
    pivot_columns: list[int] = []
    rank = 0
    for column in range(width):
        pivot = next(
            (
                row
                for row in range(rank, len(work))
                if work[row][column] != 0
            ),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        divisor = work[rank][column]
        work[rank] = [value / divisor for value in work[rank]]
        for row in range(len(work)):
            if row == rank or work[row][column] == 0:
                continue
            multiplier = work[row][column]
            work[row] = [
                left - multiplier * right
                for left, right in zip(work[row], work[rank])
            ]
        pivot_columns.append(column)
        rank += 1
        if rank == len(work):
            break
    free_columns = [
        column for column in range(width) if column not in pivot_columns
    ]
    basis: list[tuple[Fraction, ...]] = []
    for free in free_columns:
        vector = [Fraction(0) for _ in range(width)]
        vector[free] = Fraction(1)
        for row, pivot in reversed(list(enumerate(pivot_columns))):
            vector[pivot] = -sum(
                work[row][column] * vector[column]
                for column in free_columns
            )
        basis.append(tuple(vector))
    return tuple(basis)


def matvec(
    matrix: Sequence[Sequence[object]], vector: Sequence[object]
) -> tuple[Fraction, ...]:
    return tuple(
        sum(
            Fraction(coefficient) * Fraction(value)
            for coefficient, value in zip(row, vector)
        )
        for row in matrix
    )


def validate_kernel(kernel: TransitionKernel) -> tuple[int, int]:
    state_count = len(kernel)
    if state_count < 1:
        raise ValueError("kernel needs at least one state")
    action_count = len(kernel[0])
    if action_count < 1:
        raise ValueError("kernel needs at least one action")
    for state in kernel:
        if len(state) != action_count:
            raise ValueError("action count must be constant")
        for distribution in state:
            if len(distribution) != state_count:
                raise ValueError("transition row has wrong state count")
            if any(value < 0 for value in distribution):
                raise ValueError("negative transition probability")
            if sum(distribution) != 1:
                raise ValueError("transition row must sum to one")
    return state_count, action_count


def shaping_matrix(
    kernel: TransitionKernel, discount: Fraction
) -> Matrix:
    """Return G=I_state-lift-gamma*P for reward r=base+G*V."""
    state_count, action_count = validate_kernel(kernel)
    discount = Fraction(discount)
    if not 0 < discount < 1:
        raise ValueError("discount must lie strictly between zero and one")
    rows = []
    for state in range(state_count):
        for action in range(action_count):
            rows.append(
                tuple(
                    Fraction(int(next_state == state))
                    - discount * kernel[state][action][next_state]
                    for next_state in range(state_count)
                )
            )
    return tuple(rows)


def image_intersection_dimension(matrices: Sequence[Matrix]) -> int:
    """Exact dimension of the intersection of matrix column spaces."""
    if not matrices:
        raise ValueError("at least one matrix is required")
    row_count = len(matrices[0])
    widths = [len(matrix[0]) if matrix else 0 for matrix in matrices]
    if any(len(matrix) != row_count for matrix in matrices):
        raise ValueError("matrices must share a codomain")
    if len(matrices) == 1:
        return matrix_rank(matrices[0])

    total_width = sum(widths)
    offsets = [0]
    for width in widths:
        offsets.append(offsets[-1] + width)
    constraints: list[list[Fraction]] = []
    for index in range(1, len(matrices)):
        for row in range(row_count):
            equation = [Fraction(0) for _ in range(total_width)]
            for column in range(widths[0]):
                equation[column] = matrices[0][row][column]
            for column in range(widths[index]):
                equation[offsets[index] + column] = -matrices[index][row][
                    column
                ]
            constraints.append(equation)
    solution_dimension = total_width - matrix_rank(constraints)
    kernel_dimensions = sum(
        width - matrix_rank(matrix)
        for width, matrix in zip(widths, matrices)
    )
    return solution_dimension - kernel_dimensions


def residual_reward_ambiguity_dimension(
    environments: Sequence[tuple[TransitionKernel, Fraction]]
) -> int:
    return image_intersection_dimension(
        tuple(shaping_matrix(kernel, discount) for kernel, discount in environments)
    )


def self_loop_kernel(state_count: int, action_count: int) -> TransitionKernel:
    return tuple(
        tuple(
            tuple(
                Fraction(int(next_state == state))
                for next_state in range(state_count)
            )
            for _ in range(action_count)
        )
        for state in range(state_count)
    )


def cyclic_action_kernel(
    state_count: int, action_count: int = 2
) -> TransitionKernel:
    if state_count < 2 or action_count < 2:
        raise ValueError("cyclic kernel needs at least two states and actions")
    return tuple(
        tuple(
            tuple(
                Fraction(
                    int(
                        next_state
                        == (
                            state
                            if action == 0
                            else (state + action) % state_count
                        )
                    )
                )
                for next_state in range(state_count)
            )
            for action in range(action_count)
        )
        for state in range(state_count)
    )


def deterministic_kernel(
    state_count: int,
    action_count: int,
    successors: Sequence[int],
) -> TransitionKernel:
    if len(successors) != state_count * action_count:
        raise ValueError("one successor is required per state-action")
    if any(not 0 <= value < state_count for value in successors):
        raise ValueError("successor outside state universe")
    cursor = iter(successors)
    return tuple(
        tuple(
            tuple(
                Fraction(int(next_state == successor))
                for next_state in range(state_count)
            )
            for successor in (next(cursor) for _ in range(action_count))
        )
        for _ in range(state_count)
    )


def deterministic_kernels(
    state_count: int, action_count: int
) -> Iterable[TransitionKernel]:
    for successors in product(
        range(state_count), repeat=state_count * action_count
    ):
        yield deterministic_kernel(state_count, action_count, successors)


def action_difference_matrix(kernel: TransitionKernel) -> Matrix:
    state_count, action_count = validate_kernel(kernel)
    rows = []
    for state in range(state_count):
        reference = kernel[state][0]
        for action in range(1, action_count):
            rows.append(
                tuple(
                    kernel[state][action][next_state]
                    - reference[next_state]
                    for next_state in range(state_count)
                )
            )
    return tuple(rows)


def successor_difference_components(kernel: TransitionKernel) -> int:
    """Components of the deterministic successor-difference graph."""
    state_count, action_count = validate_kernel(kernel)
    successors: list[list[int]] = []
    for state in range(state_count):
        row = []
        for action in range(action_count):
            distribution = kernel[state][action]
            ones = [i for i, value in enumerate(distribution) if value == 1]
            if len(ones) != 1:
                raise ValueError("kernel is not deterministic")
            row.append(ones[0])
        successors.append(row)
    adjacency = [set() for _ in range(state_count)]
    for row in successors:
        reference = row[0]
        for target in row[1:]:
            adjacency[reference].add(target)
            adjacency[target].add(reference)
    unseen = set(range(state_count))
    count = 0
    while unseen:
        count += 1
        stack = [unseen.pop()]
        while stack:
            vertex = stack.pop()
            for neighbor in adjacency[vertex] & unseen:
                unseen.remove(neighbor)
                stack.append(neighbor)
    return count


def baseline_pair_intersection_dimension(
    kernel: TransitionKernel, discount: Fraction
) -> int:
    state_count, action_count = validate_kernel(kernel)
    baseline = self_loop_kernel(state_count, action_count)
    return residual_reward_ambiguity_dimension(
        ((baseline, discount), (kernel, discount))
    )


def trajectory_difference_matrix(
    coordinate_count: int, query_edges: Sequence[tuple[int, int]]
) -> Matrix:
    rows = []
    for left, right in query_edges:
        if not (
            0 <= left < coordinate_count and 0 <= right < coordinate_count
        ):
            raise ValueError("trajectory coordinate outside universe")
        row = [Fraction(0) for _ in range(coordinate_count)]
        row[left] += 1
        row[right] -= 1
        rows.append(tuple(row))
    return tuple(rows)


def trajectory_ambiguity_dimension(
    coordinate_count: int, query_edges: Sequence[tuple[int, int]]
) -> int:
    return coordinate_count - matrix_rank(
        trajectory_difference_matrix(coordinate_count, query_edges)
    )


def deterministic_policy_witness(
    state_count: int, discount: Fraction
) -> dict[str, object]:
    """Construct two non-gauge rewards with the same strict policy twice."""
    if state_count < 2:
        raise ValueError("witness needs at least two states")
    action_count = 2
    baseline = self_loop_kernel(state_count, action_count)
    cyclic = cyclic_action_kernel(state_count, action_count)
    reward = tuple(
        Fraction(1 if action == 0 else 0)
        for _state in range(state_count)
        for action in range(action_count)
    )
    perturbed = list(reward)
    perturbed[1] = Fraction(1, 2)
    difference = tuple(
        right - left for left, right in zip(reward, perturbed)
    )
    common_gauge_dimension = residual_reward_ambiguity_dimension(
        ((baseline, discount), (cyclic, discount))
    )
    # Under the action-0 policy, V=1/(1-gamma) in every state. Every action-1
    # gap is 1, except the perturbed state where it is 1/2.
    base_minimum_gap = Fraction(1)
    perturbed_minimum_gap = Fraction(1, 2)
    is_constant_difference = len(set(difference)) == 1
    return {
        "state_count": state_count,
        "reward": reward,
        "perturbed_reward": tuple(perturbed),
        "difference": difference,
        "base_minimum_gap": base_minimum_gap,
        "perturbed_minimum_gap": perturbed_minimum_gap,
        "common_gauge_dimension": common_gauge_dimension,
        "difference_is_common_constant": is_constant_difference,
        "same_strict_policy": (
            base_minimum_gap > 0 and perturbed_minimum_gap > 0
        ),
    }
