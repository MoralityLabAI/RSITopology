"""Post-run independent exact check of the v0.10 deterministic witness.

This verifier is intentionally not imported by the sealed implementation. It
reconstructs the two environments, solves the fixed-policy Bellman system by a
separate exact elimination routine, and evaluates every action gap directly.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Sequence


Vector = tuple[Fraction, ...]
Matrix = tuple[tuple[Fraction, ...], ...]
Kernel = tuple[tuple[Vector, Vector], ...]


def solve_exact(matrix: Matrix, target: Vector) -> Vector:
    size = len(matrix)
    work = [
        [*map(Fraction, row), Fraction(value)] for row, value in zip(matrix, target)
    ]
    for column in range(size):
        pivot = next(row for row in range(column, size) if work[row][column] != 0)
        work[column], work[pivot] = work[pivot], work[column]
        divisor = work[column][column]
        work[column] = [value / divisor for value in work[column]]
        for row in range(size):
            if row == column:
                continue
            multiplier = work[row][column]
            work[row] = [
                left - multiplier * right
                for left, right in zip(work[row], work[column])
            ]
    return tuple(work[row][-1] for row in range(size))


def environments(state_count: int) -> tuple[Kernel, Kernel]:
    baseline = []
    cyclic = []
    for state in range(state_count):
        self_loop = tuple(
            Fraction(int(target == state)) for target in range(state_count)
        )
        forward = tuple(
            Fraction(int(target == (state + 1) % state_count))
            for target in range(state_count)
        )
        baseline.append((self_loop, self_loop))
        cyclic.append((self_loop, forward))
    return tuple(baseline), tuple(cyclic)


def evaluate_action_zero(
    kernel: Kernel,
    reward: Sequence[Fraction],
    discount: Fraction,
) -> tuple[Vector, Vector]:
    state_count = len(kernel)
    matrix = tuple(
        tuple(
            Fraction(int(state == target)) - discount * kernel[state][0][target]
            for target in range(state_count)
        )
        for state in range(state_count)
    )
    selected_reward = tuple(reward[2 * state] for state in range(state_count))
    value = solve_exact(matrix, selected_reward)
    gaps = []
    for state in range(state_count):
        q_values = []
        for action in range(2):
            q_values.append(
                reward[2 * state + action]
                + discount
                * sum(
                    probability * value[target]
                    for target, probability in enumerate(kernel[state][action])
                )
            )
        gaps.append(q_values[0] - q_values[1])
    return value, tuple(gaps)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    spec = protocol["structured_cells"]
    discount = Fraction(spec["transition_discount"])
    rows = []
    for state_count in map(int, spec["state_counts"]):
        baseline, cyclic = environments(state_count)
        base_reward = tuple(
            Fraction(1 if action == 0 else 0)
            for _state in range(state_count)
            for action in range(2)
        )
        perturbed_reward = list(base_reward)
        perturbed_reward[1] = Fraction(1, 2)
        difference = tuple(
            right - left for left, right in zip(base_reward, perturbed_reward)
        )
        for environment_name, kernel in (
            ("self_loop", baseline),
            ("cyclic", cyclic),
        ):
            for reward_name, reward in (
                ("base", base_reward),
                ("perturbed", tuple(perturbed_reward)),
            ):
                value, gaps = evaluate_action_zero(kernel, reward, discount)
                rows.append(
                    {
                        "state_count": state_count,
                        "environment": environment_name,
                        "reward": reward_name,
                        "minimum_gap": str(min(gaps)),
                        "maximum_gap": str(max(gaps)),
                        "all_gaps_strictly_positive": all(gap > 0 for gap in gaps),
                        "value_is_constant": len(set(value)) == 1,
                    }
                )
        if len(set(difference)) == 1:
            raise AssertionError("witness difference is a global constant")

    checks = {
        "expected_cell_count": len(rows) == 4 * len(spec["state_counts"]),
        "every_policy_gap_strictly_positive": all(
            row["all_gaps_strictly_positive"] for row in rows
        ),
        "base_minimum_gap_is_one": all(
            row["minimum_gap"] == "1" for row in rows if row["reward"] == "base"
        ),
        "perturbed_minimum_gap_is_one_half": all(
            row["minimum_gap"] == "1/2" for row in rows if row["reward"] == "perturbed"
        ),
        "policy_values_are_constant": all(row["value_is_constant"] for row in rows),
    }
    result = {
        "status": (
            "independently_verified" if all(checks.values()) else "verification_failed"
        ),
        "method": "separate exact Bellman solve over reconstructed kernels",
        "post_run_status": "diagnostic verification, not preregistered gate",
        "discount": str(discount),
        "cell_count": len(rows),
        "checks": checks,
        "rows": rows,
    }
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite {args.output}")
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"status": result["status"], "checks": checks}, indent=2))
    raise SystemExit(0 if all(checks.values()) else 1)


if __name__ == "__main__":
    main()
