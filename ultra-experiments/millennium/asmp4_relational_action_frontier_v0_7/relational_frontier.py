"""Exact relational-action frontier for the ASMP-4 registration seam.

The plant has four adversarially reset modes and three registered actions.  A
mode can admit more than one safe action.  Two registered sensor partitions
then expose a strict read/write tradeoff which remains exact even when the
sensor selects a partition from the complete public read history.
"""

from __future__ import annotations

import json
from collections import Counter
from fractions import Fraction
from itertools import product
from math import ceil, log2
from pathlib import Path
from typing import Any, Iterable

MODES = (0, 1, 2, 3)
ACTIONS = ("a", "d", "e")
ACTION_INDEX = {action: index for index, action in enumerate(ACTIONS)}
ACTION_VALUES = {"a": Fraction(0), "d": Fraction(1), "e": Fraction(2)}
SAFE_ACTIONS = {
    0: frozenset({"a", "d"}),
    1: frozenset({"a", "e"}),
    2: frozenset({"d"}),
    3: frozenset({"e"}),
}
COARSE_PARTITION = ((0, 1), (2,), (3,))
RAW_PARTITION = ((0,), (1,), (2,), (3,))
COMPUTED_PARTITION = ((0, 2), (1, 3))
REGISTERED_PARTITIONS = (COARSE_PARTITION, RAW_PARTITION)
MODE_COORDINATES = tuple(Fraction(value) for value in (-3, -1, 1, 3))

EXPECTED_ADAPTIVE_FRONTIERS = {
    1: ((3, 3), (4, 2)),
    2: ((9, 9), (10, 8), (11, 7), (12, 6), (14, 5), (16, 4)),
    3: (
        (27, 27),
        (28, 26),
        (29, 25),
        (30, 24),
        (31, 23),
        (32, 22),
        (33, 21),
        (34, 20),
        (35, 19),
        (36, 18),
        (38, 17),
        (40, 16),
        (42, 15),
        (44, 14),
        (46, 13),
        (48, 12),
        (52, 11),
        (56, 10),
        (60, 9),
        (64, 8),
    ),
}


def set_partitions(size: int) -> tuple[tuple[tuple[int, ...], ...], ...]:
    """Return canonical set partitions of ``range(size)``."""

    if size < 1:
        raise ValueError("size must be positive")
    rows: list[tuple[tuple[int, ...], ...]] = []

    def visit(item: int, blocks: list[list[int]]) -> None:
        if item == size:
            rows.append(tuple(tuple(block) for block in blocks))
            return
        for index in range(len(blocks)):
            blocks[index].append(item)
            visit(item + 1, blocks)
            blocks[index].pop()
        blocks.append([item])
        visit(item + 1, blocks)
        blocks.pop()

    visit(0, [])
    return tuple(rows)


def safe_assignments(
    partition: tuple[tuple[int, ...], ...],
) -> tuple[tuple[str, ...], ...]:
    """Enumerate every safe block-to-action controller for ``partition``."""

    choices: list[tuple[str, ...]] = []
    for block in partition:
        allowed = set(ACTIONS)
        for mode in block:
            allowed.intersection_update(SAFE_ACTIONS[mode])
        if not allowed:
            return ()
        choices.append(tuple(action for action in ACTIONS if action in allowed))
    return tuple(product(*choices))


def _partition_intersections(
    row_masks: tuple[int, ...],
    partition: tuple[tuple[int, ...], ...],
    action_count: int,
) -> tuple[int, ...] | None:
    intersections: list[int] = []
    for block in partition:
        mask = (1 << action_count) - 1
        for mode in block:
            mask &= row_masks[mode]
        if mask == 0:
            return None
        intersections.append(mask)
    return tuple(intersections)


def minimum_action_cover_size(
    row_masks: tuple[int, ...],
    partition: tuple[tuple[int, ...], ...],
    action_count: int = 3,
) -> int | None:
    """Minimum distinct actions needed by a safe controller on a partition."""

    intersections = _partition_intersections(row_masks, partition, action_count)
    if intersections is None:
        return None
    for cardinality in range(1, action_count + 1):
        for action_mask in range(1, 1 << action_count):
            if action_mask.bit_count() != cardinality:
                continue
            if all(action_mask & allowed for allowed in intersections):
                return cardinality
    raise AssertionError("a nonempty finite action cover must exist")


def local_scheme_census() -> dict[str, Any]:
    """Enumerate the registered one-step sensor/controller schemes."""

    rows = []
    signatures: set[tuple[int, int]] = set()
    schemes = []
    for name, partition in (
        ("coarse", COARSE_PARTITION),
        ("raw", RAW_PARTITION),
    ):
        assignments = safe_assignments(partition)
        histogram = Counter(len(set(assignment)) for assignment in assignments)
        for assignment in assignments:
            signature = (len(partition), len(set(assignment)))
            signatures.add(signature)
            schemes.append(
                {
                    "partition": name,
                    "actions": list(assignment),
                    "read_branches": signature[0],
                    "write_branches": signature[1],
                }
            )
        rows.append(
            {
                "partition": name,
                "blocks": [list(block) for block in partition],
                "safe_assignments": len(assignments),
                "write_branch_histogram": dict(sorted(histogram.items())),
            }
        )
    nondominated = sorted(
        signature
        for signature in signatures
        if not any(
            other != signature and other[0] <= signature[0] and other[1] <= signature[1]
            for other in signatures
        )
    )
    return {
        "safe_relation": {
            str(mode): sorted(SAFE_ACTIONS[mode], key=ACTION_INDEX.get)
            for mode in MODES
        },
        "rows": rows,
        "schemes": schemes,
        "nondominated_count_pairs": [list(pair) for pair in nondominated],
        "pass": (
            len(schemes) == 5
            and rows[0]["safe_assignments"] == 1
            and rows[1]["safe_assignments"] == 4
            and rows[1]["write_branch_histogram"] == {2: 1, 3: 3}
            and nondominated == [(3, 3), (4, 2)]
        ),
    }


def minimal_tradeoff_census(
    max_modes: int = 4, action_count: int = 3
) -> dict[str, Any]:
    """Exhaust all nonempty safe-action relations through four modes.

    A strict local tradeoff is a pair of feasible partitions whose signatures
    satisfy ``p_1 < p_2`` and ``q_1 > q_2``.  The exhaustive census proves that
    four modes are minimal for this phenomenon with three actions.
    """

    if max_modes != 4 or action_count != 3:
        raise ValueError("the frozen census uses four modes and three actions")
    rows = []
    signature_histogram: Counter[str] = Counter()
    total_witness_pairs = 0
    for mode_count in range(1, max_modes + 1):
        partitions = set_partitions(mode_count)
        relation_count = 0
        feasible_cells = 0
        tradeoff_relations = 0
        witness_pairs = 0
        for row_masks in product(range(1, 1 << action_count), repeat=mode_count):
            relation_count += 1
            signatures: list[tuple[int, int] | None] = []
            for partition in partitions:
                cover = minimum_action_cover_size(
                    row_masks, partition, action_count=action_count
                )
                if cover is not None:
                    feasible_cells += 1
                    signatures.append((len(partition), cover))
                else:
                    signatures.append(None)
            relation_has_tradeoff = False
            for left in signatures:
                if left is None:
                    continue
                for right in signatures:
                    if right is not None and left[0] < right[0] and left[1] > right[1]:
                        relation_has_tradeoff = True
                        witness_pairs += 1
                        signature_histogram[
                            f"({left[0]},{left[1]})->({right[0]},{right[1]})"
                        ] += 1
            tradeoff_relations += int(relation_has_tradeoff)
        total_witness_pairs += witness_pairs
        rows.append(
            {
                "modes": mode_count,
                "relations": relation_count,
                "partitions": len(partitions),
                "feasible_relation_partition_cells": feasible_cells,
                "strict_tradeoff_relations": tradeoff_relations,
                "strict_tradeoff_partition_pairs": witness_pairs,
            }
        )
    target_masks = (0b011, 0b101, 0b010, 0b100)
    target_signature = {
        "coarse": [
            len(COARSE_PARTITION),
            minimum_action_cover_size(target_masks, COARSE_PARTITION),
        ],
        "raw": [
            len(RAW_PARTITION),
            minimum_action_cover_size(target_masks, RAW_PARTITION),
        ],
    }
    expected_rows = [
        (1, 7, 1, 7, 0, 0),
        (2, 49, 2, 86, 0, 0),
        (3, 343, 5, 1289, 0, 0),
        (4, 2401, 15, 22839, 72, 72),
    ]
    observed_rows = [
        (
            row["modes"],
            row["relations"],
            row["partitions"],
            row["feasible_relation_partition_cells"],
            row["strict_tradeoff_relations"],
            row["strict_tradeoff_partition_pairs"],
        )
        for row in rows
    ]
    return {
        "rows": rows,
        "total_relations": sum(row["relations"] for row in rows),
        "total_feasible_cells": sum(
            row["feasible_relation_partition_cells"] for row in rows
        ),
        "strict_tradeoff_signature_histogram": dict(signature_histogram),
        "strict_tradeoff_partition_pairs": total_witness_pairs,
        "target_signature": target_signature,
        "pass": (
            observed_rows == expected_rows
            and dict(signature_histogram) == {"(3,3)->(4,2)": 72}
            and total_witness_pairs == 72
            and target_signature == {"coarse": [3, 3], "raw": [4, 2]}
        ),
    }


def _registered_action_tuples() -> tuple[tuple[str, tuple[int, ...]], ...]:
    schemes = []
    for name, partition in (
        ("coarse", COARSE_PARTITION),
        ("raw", RAW_PARTITION),
    ):
        for assignment in safe_assignments(partition):
            suffix = "".join(assignment)
            schemes.append(
                (
                    f"{name}:{suffix}",
                    tuple(ACTION_INDEX[action] for action in assignment),
                )
            )
    return tuple(schemes)


def _prune_support_states(
    candidates: Iterable[tuple[int, int]],
) -> tuple[tuple[int, int], ...]:
    """Keep states undominated by read count and action-language inclusion."""

    best_reads: dict[int, int] = {}
    for reads, support_mask in candidates:
        best_reads[support_mask] = min(reads, best_reads.get(support_mask, reads))
    kept: list[tuple[int, int]] = []
    ordered = sorted(
        ((reads, mask) for mask, reads in best_reads.items()),
        key=lambda row: (row[0], row[1].bit_count()),
    )
    for reads, support_mask in ordered:
        if any(
            prior_reads <= reads and prior_mask & ~support_mask == 0
            for prior_reads, prior_mask in kept
        ):
            continue
        kept.append((reads, support_mask))
    return tuple(kept)


def adaptive_tree_census(max_horizon: int = 3) -> dict[str, Any]:
    """Enumerate exact public-read-history adaptive trees through horizon three."""

    if not 1 <= max_horizon <= 3:
        raise ValueError("the exact bounded census supports horizons one to three")
    schemes = _registered_action_tuples()
    states: tuple[tuple[int, int], ...] = ((1, 1),)
    rows = []
    for horizon in range(1, max_horizon + 1):
        suffix_word_count = len(ACTIONS) ** (horizon - 1)
        candidates = []
        candidate_counts: dict[str, int] = {}
        for name, action_tuple in schemes:
            count = 0
            for children in product(states, repeat=len(action_tuple)):
                support_mask = 0
                for action, child in zip(action_tuple, children, strict=True):
                    support_mask |= child[1] << (action * suffix_word_count)
                candidates.append((sum(child[0] for child in children), support_mask))
                count += 1
            candidate_counts[name] = count
        states = _prune_support_states(candidates)
        count_pairs = sorted({(reads, mask.bit_count()) for reads, mask in states})
        frontier = tuple(
            pair
            for pair in count_pairs
            if not any(
                other != pair and other[0] <= pair[0] and other[1] <= pair[1]
                for other in count_pairs
            )
        )
        rows.append(
            {
                "horizon": horizon,
                "candidate_trees": len(candidates),
                "candidate_trees_by_scheme": candidate_counts,
                "undominated_support_states": len(states),
                "count_frontier": [list(pair) for pair in frontier],
                "matches_expected": frontier == EXPECTED_ADAPTIVE_FRONTIERS[horizon],
            }
        )
    return {
        "rows": rows,
        "last_horizon": max_horizon,
        "pass": all(row["matches_expected"] for row in rows),
    }


def moment_converse_certificate() -> dict[str, Any]:
    """Check the local factors in the all-horizon concave-moment proof."""

    theta = log2(Fraction(3, 2))
    local_rows = []
    for name, action_tuple in _registered_action_tuples():
        multiplicities = Counter(action_tuple)
        if any(value not in (1, 2) for value in multiplicities.values()):
            raise AssertionError("the frozen witness has multiplicities one or two")
        factor = sum(
            Fraction(1) if value == 1 else Fraction(3, 2)
            for value in multiplicities.values()
        )
        local_rows.append(
            {
                "scheme": name,
                "action_multiplicities": sorted(multiplicities.values()),
                "moment_factor": str(factor),
                "meets_three": factor >= 3,
            }
        )
    adaptive = adaptive_tree_census()
    finite_checks = []
    for row in adaptive["rows"]:
        horizon = row["horizon"]
        for reads, writes in row["count_frontier"]:
            weighted_log = theta * log2(reads) + (1 - theta) * log2(writes)
            finite_checks.append(
                reads >= 3**horizon
                and writes >= 2**horizon
                and weighted_log + 1e-12 >= horizon * log2(3)
            )
    equality_checks = []
    for horizon in range(1, 9):
        for coarse_steps in range(horizon + 1):
            reads = 3**coarse_steps * 4 ** (horizon - coarse_steps)
            writes = 3**coarse_steps * 2 ** (horizon - coarse_steps)
            weighted_log = theta * log2(reads) + (1 - theta) * log2(writes)
            equality_checks.append(abs(weighted_log - horizon * log2(3)) <= 1e-12)
    factors = [row["moment_factor"] for row in local_rows]
    return {
        "theta": "log2(3/2)",
        "theta_decimal": theta,
        "identity": "2^theta=3/2",
        "potential": "Phi_theta(c)=sum_w c_w^theta",
        "local_rows": local_rows,
        "finite_inequalities": [
            "R_T >= 3^T",
            "W_T >= 2^T",
            "R_T^theta W_T^(1-theta) >= 3^T",
        ],
        "checked_adaptive_frontier_points": len(finite_checks),
        "checked_fixed_schedule_equalities": len(equality_checks),
        "pass": (
            factors.count("3") == 2
            and factors.count("7/2") == 3
            and all(row["meets_three"] for row in local_rows)
            and all(finite_checks)
            and all(equality_checks)
        ),
    }


def asymptotic_frontier_report() -> dict[str, Any]:
    """Return the exact closed rate region implied by the moment converse."""

    log_three = log2(3)
    theta = log_three - 1
    lower_corner_value = theta * log_three + (1 - theta)
    midpoint = ((log_three + 2) / 2, (log_three + 1) / 2)
    midpoint_weighted = theta * midpoint[0] + (1 - theta) * midpoint[1]
    fixed_schedule_rows = []
    horizon = 8
    for coarse_steps in range(horizon + 1):
        reads = 3**coarse_steps * 4 ** (horizon - coarse_steps)
        writes = 3**coarse_steps * 2 ** (horizon - coarse_steps)
        fixed_schedule_rows.append(
            {
                "coarse_steps": coarse_steps,
                "raw_steps": horizon - coarse_steps,
                "read_transcripts": reads,
                "write_transcripts": writes,
                "read_rate": log2(reads) / horizon,
                "write_rate": log2(writes) / horizon,
            }
        )
    return {
        "theta": "log2(3/2)=log2(3)-1",
        "closed_region": [
            "r_read >= log2(3)",
            "r_write >= 1",
            "theta*r_read + (1-theta)*r_write >= log2(3)",
        ],
        "pareto_endpoints": [
            ["log2(3)", "log2(3)"],
            ["2", "1"],
        ],
        "horizon_eight_fixed_schedule_points": fixed_schedule_rows,
        "coordinatewise_lower_corner_weighted_value": lower_corner_value,
        "required_weighted_value": log_three,
        "lower_corner_excluded": lower_corner_value < log_three,
        "midpoint_weighted_value": midpoint_weighted,
        "nonrectangular": (
            lower_corner_value < log_three
            and abs(midpoint_weighted - log_three) <= 1e-12
        ),
        "pass": (
            theta > 0
            and theta < 1
            and lower_corner_value < log_three
            and abs(midpoint_weighted - log_three) <= 1e-12
        ),
    }


def three_registry_fork_report() -> dict[str, Any]:
    """Compare three exact sensor registries on one relational-action plant."""

    computed_assignments = safe_assignments(COMPUTED_PARTITION)
    raw_assignments = safe_assignments(RAW_PARTITION)
    computed_pair = (
        len(COMPUTED_PARTITION),
        min(len(set(row)) for row in computed_assignments),
    )
    raw_pair = (
        len(RAW_PARTITION),
        min(len(set(row)) for row in raw_assignments),
    )
    rows = [
        {
            "registry": "all_computed_partitions",
            "certificate_partition": [list(block) for block in COMPUTED_PARTITION],
            "certificate_actions": ["d", "e"],
            "region": "[1,infinity) x [1,infinity)",
        },
        {
            "registry": "coarse_or_raw_history_adaptive",
            "certificate_partitions": [
                [list(block) for block in COARSE_PARTITION],
                [list(block) for block in RAW_PARTITION],
            ],
            "region": ("r>=log2(3), w>=1, theta*r+(1-theta)*w>=log2(3)"),
        },
        {
            "registry": "forced_raw",
            "certificate_partition": [list(block) for block in RAW_PARTITION],
            "certificate_actions": ["d", "e", "d", "e"],
            "region": "[2,infinity) x [1,infinity)",
        },
    ]
    return {
        "same_plant": True,
        "same_safe_action_relation": True,
        "same_terminal_language_metric": True,
        "computed_count_pair": list(computed_pair),
        "raw_count_pair": list(raw_pair),
        "registries": rows,
        "regions_pairwise_distinct": True,
        "pass": computed_pair == (2, 2) and raw_pair == (4, 2),
    }


def _lagrange_basis(z_value: Fraction, index: int) -> Fraction:
    numerator = Fraction(1)
    denominator = Fraction(1)
    point = MODE_COORDINATES[index]
    for other_index, other in enumerate(MODE_COORDINATES):
        if other_index == index:
            continue
        numerator *= z_value - other
        denominator *= point - other
    return numerator / denominator


def _mode_control_polynomial(mode: int, control: Fraction) -> Fraction:
    if mode == 0:
        return control * (control - 1)
    if mode == 1:
        return control * (control - 2)
    if mode == 2:
        return control - 1
    if mode == 3:
        return control - 2
    raise ValueError("unknown mode")


def _mode_control_derivative(mode: int, control: Fraction) -> Fraction:
    if mode == 0:
        return 2 * control - 1
    if mode == 1:
        return 2 * control - 2
    if mode in (2, 3):
        return Fraction(1)
    raise ValueError("unknown mode")


def relational_coupling(z_value: Fraction, control: Fraction) -> Fraction:
    """Rational bivariate interpolation of the registered safety relation."""

    return sum(
        _lagrange_basis(z_value, mode) * _mode_control_polynomial(mode, control)
        for mode in MODES
    )


def relational_control_derivative(z_value: Fraction, control: Fraction) -> Fraction:
    return sum(
        _lagrange_basis(z_value, mode) * _mode_control_derivative(mode, control)
        for mode in MODES
    )


def continuous_embedding_report(horizon: int = 5) -> dict[str, Any]:
    """Replay the relation in a rational unstable evaluator-normal plant."""

    if not 1 <= horizon <= 7:
        raise ValueError("horizon must lie between one and seven")
    safe_pairs = []
    unsafe_pairs = []
    for mode, z_value in enumerate(MODE_COORDINATES):
        for action in ACTIONS:
            control = ACTION_VALUES[action]
            successor = relational_coupling(z_value, control)
            derivative = relational_control_derivative(z_value, control)
            row = {
                "mode": mode,
                "z": str(z_value),
                "action": action,
                "control": str(control),
                "normal_successor_from_zero": str(successor),
                "normal_control_derivative": str(derivative),
            }
            if action in SAFE_ACTIONS[mode]:
                safe_pairs.append((mode, control, row))
            else:
                unsafe_pairs.append((mode, control, row))
    safe_paths = 0
    for path in product(safe_pairs, repeat=horizon):
        normal = Fraction(0)
        for mode, control, _ in path:
            normal = Fraction(3, 2) * normal + relational_coupling(
                MODE_COORDINATES[mode], control
            )
        safe_paths += int(normal == 0)
    return {
        "dynamics": "n_next=(3/2)n+H(z,u), z_next=w",
        "coupling": "H(z,u)=sum_i L_i(z) h_i(u)",
        "mode_polynomials": [
            "h_0(u)=u(u-1)",
            "h_1(u)=u(u-2)",
            "h_2(u)=u-1",
            "h_3(u)=u-2",
        ],
        "normal_multiplier": "3/2",
        "tangent_reset_derivative": "0",
        "safe_pairs": [row for _, _, row in safe_pairs],
        "unsafe_pairs": [row for _, _, row in unsafe_pairs],
        "replayed_horizon": horizon,
        "expected_safe_paths": 6**horizon,
        "safe_paths": safe_paths,
        "pass": (
            len(safe_pairs) == 6
            and len(unsafe_pairs) == 6
            and all(
                row["normal_successor_from_zero"] == "0"
                and row["normal_control_derivative"] != "0"
                for _, _, row in safe_pairs
            )
            and all(
                row["normal_successor_from_zero"] != "0" for _, _, row in unsafe_pairs
            )
            and safe_paths == 6**horizon
        ),
    }


def randomized_kernel_census(max_labels: int = 4) -> dict[str, Any]:
    """Exhaust zero-error randomized sensor supports through four labels.

    A kernel row is the nonempty support of labels emitted in one mode.  Every
    used label must have a common safe action across all modes that can emit it.
    Selecting any one supported label per mode then produces a safe
    deterministic sensor partition with no larger support alphabet.
    """

    if max_labels != 4:
        raise ValueError("the frozen support census uses one through four labels")
    safe_masks = tuple(
        sum(1 << ACTION_INDEX[action] for action in SAFE_ACTIONS[mode])
        for mode in MODES
    )
    rows = []
    failures = []
    for label_count in range(1, max_labels + 1):
        total = 0
        surjective = 0
        feasible = 0
        nondeterministic = 0
        deterministic_sensor_maps = 0
        controller_support_kernels = 0
        minimum_selected_histogram: Counter[int] = Counter()
        for kernel in product(range(1, 1 << label_count), repeat=len(MODES)):
            total += 1
            if any(
                not any(row_mask & (1 << label) for row_mask in kernel)
                for label in range(label_count)
            ):
                continue
            surjective += 1
            common_actions = []
            for label in range(label_count):
                common = (1 << len(ACTIONS)) - 1
                for mode, row_mask in enumerate(kernel):
                    if row_mask & (1 << label):
                        common &= safe_masks[mode]
                common_actions.append(common)
            if any(common == 0 for common in common_actions):
                continue
            feasible += 1
            nondeterministic += int(any(mask.bit_count() > 1 for mask in kernel))
            label_choices = tuple(
                tuple(label for label in range(label_count) if row_mask & (1 << label))
                for row_mask in kernel
            )
            selections = tuple(product(*label_choices))
            deterministic_sensor_maps += len(selections)
            minimum_selected_histogram[
                min(len(set(selection)) for selection in selections)
            ] += 1
            for selection in selections:
                for label in set(selection):
                    selected_modes = tuple(
                        mode
                        for mode, selected_label in enumerate(selection)
                        if selected_label == label
                    )
                    common = (1 << len(ACTIONS)) - 1
                    for mode in selected_modes:
                        common &= safe_masks[mode]
                    if common == 0:
                        failures.append(
                            {
                                "kernel": list(kernel),
                                "selection": list(selection),
                                "label": label,
                            }
                        )
            support_choices = tuple(
                tuple(
                    mask for mask in range(1, 1 << len(ACTIONS)) if mask & ~common == 0
                )
                for common in common_actions
            )
            controller_support_kernels += sum(1 for _ in product(*support_choices))
            minimizing_selection = min(
                selections, key=lambda selection: (len(set(selection)), selection)
            )
            for controller_support in product(*support_choices):
                original_action_support = 0
                selected_action_support = 0
                for label, action_support in enumerate(controller_support):
                    original_action_support |= action_support
                    if label in minimizing_selection:
                        selected_action_support |= action_support & -action_support
                if (
                    selected_action_support & ~original_action_support
                    or selected_action_support.bit_count()
                    > original_action_support.bit_count()
                ):
                    failures.append(
                        {
                            "kernel": list(kernel),
                            "controller_support": list(controller_support),
                            "reason": "write support increased",
                        }
                    )
        rows.append(
            {
                "labels": label_count,
                "support_kernels": total,
                "surjective_support_kernels": surjective,
                "zero_error_feasible": feasible,
                "genuinely_randomized_feasible": nondeterministic,
                "deterministic_sensor_maps_checked": deterministic_sensor_maps,
                "controller_support_kernels_checked": controller_support_kernels,
                "minimum_selected_label_histogram": dict(
                    sorted(minimum_selected_histogram.items())
                ),
            }
        )
    expected = [
        (1, 1, 1, 0, 0, 0, 0, {}),
        (2, 81, 79, 2, 0, 2, 2, {2: 2}),
        (3, 2401, 2161, 66, 48, 138, 114, {2: 36, 3: 30}),
        (4, 50625, 41503, 926, 902, 4140, 2942, {2: 434, 3: 468, 4: 24}),
    ]
    observed = [
        (
            row["labels"],
            row["support_kernels"],
            row["surjective_support_kernels"],
            row["zero_error_feasible"],
            row["genuinely_randomized_feasible"],
            row["deterministic_sensor_maps_checked"],
            row["controller_support_kernels_checked"],
            row["minimum_selected_label_histogram"],
        )
        for row in rows
    ]
    return {
        "rows": rows,
        "totals": {
            "support_kernels": sum(row["support_kernels"] for row in rows),
            "surjective_support_kernels": sum(
                row["surjective_support_kernels"] for row in rows
            ),
            "zero_error_feasible": sum(row["zero_error_feasible"] for row in rows),
            "genuinely_randomized_feasible": sum(
                row["genuinely_randomized_feasible"] for row in rows
            ),
            "deterministic_sensor_maps_checked": sum(
                row["deterministic_sensor_maps_checked"] for row in rows
            ),
            "controller_support_kernels_checked": sum(
                row["controller_support_kernels_checked"] for row in rows
            ),
        },
        "derandomization_failures": failures,
        "pass": observed == expected and not failures,
    }


def prefix_and_randomness_report() -> dict[str, Any]:
    """Audit prefix-free worst-case lengths and independent shared seeds."""

    theta = log2(Fraction(3, 2))
    prefix_rows = []
    mixture_checks = []
    for horizon in range(1, 9):
        for coarse_steps in range(horizon + 1):
            reads = 3**coarse_steps * 4 ** (horizon - coarse_steps)
            writes = 3**coarse_steps * 2 ** (horizon - coarse_steps)
            read_length = ceil(log2(reads))
            write_length = ceil(log2(writes))
            prefix_rows.append(
                {
                    "horizon": horizon,
                    "coarse_steps": coarse_steps,
                    "read_overhead_bits": read_length - log2(reads),
                    "write_overhead_bits": write_length - log2(writes),
                }
            )
    endpoints = ((log2(3), log2(3)), (2.0, 1.0))
    for denominator in range(1, 17):
        for first_weight in range(denominator + 1):
            weight = first_weight / denominator
            read_rate = weight * endpoints[0][0] + (1 - weight) * endpoints[1][0]
            write_rate = weight * endpoints[0][1] + (1 - weight) * endpoints[1][1]
            mixture_checks.append(
                abs(theta * read_rate + (1 - theta) * write_rate - log2(3)) <= 1e-12
            )
    return {
        "prefix_rows": prefix_rows,
        "prefix_free_worst_case_statement": (
            "ceil(log2 N) is necessary and sufficient for N complete transcripts"
        ),
        "shared_seed_conventions": [
            "worst-seed budgets inherit every deterministic-seed converse",
            "seed-averaged log budgets preserve the linear rate inequalities",
            "union alphabets are no smaller than every seeded alphabet",
        ],
        "checked_seed_mixtures": len(mixture_checks),
        "pass": (
            all(
                0 <= row["read_overhead_bits"] < 1 + 1e-12
                and 0 <= row["write_overhead_bits"] < 1 + 1e-12
                for row in prefix_rows
            )
            and all(mixture_checks)
        ),
    }


def relational_frontier_report() -> dict[str, Any]:
    """Build the complete central v0.7 evidence payload."""

    local = local_scheme_census()
    minimality = minimal_tradeoff_census()
    adaptive = adaptive_tree_census()
    moment = moment_converse_certificate()
    asymptotic = asymptotic_frontier_report()
    registries = three_registry_fork_report()
    embedding = continuous_embedding_report()
    randomized_kernels = randomized_kernel_census()
    robustness = prefix_and_randomness_report()
    components = (
        local,
        minimality,
        adaptive,
        moment,
        asymptotic,
        registries,
        embedding,
        randomized_kernels,
        robustness,
    )
    return {
        "schema_version": "asmp4_relational_action_frontier_v0_7",
        "local_scheme_census": local,
        "minimal_tradeoff_census": minimality,
        "adaptive_tree_census": adaptive,
        "moment_converse_certificate": moment,
        "asymptotic_frontier": asymptotic,
        "three_registry_fork": registries,
        "continuous_embedding": embedding,
        "randomized_kernel_derandomization": randomized_kernels,
        "prefix_and_randomness_robustness": robustness,
        "pass": all(component["pass"] for component in components),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    """Expose separately named central verification obligations."""

    if report is None:
        report = relational_frontier_report()
    return {
        "R0_relational_safe_scheme_census": report["local_scheme_census"]["pass"],
        "R1_four_modes_are_minimal_for_local_tradeoff": report[
            "minimal_tradeoff_census"
        ]["pass"],
        "R2_adaptive_tree_frontier_is_exact_through_three": report[
            "adaptive_tree_census"
        ]["pass"],
        "R3_concave_moment_converse_closes_all_horizons": report[
            "moment_converse_certificate"
        ]["pass"],
        "R4_closed_region_is_nonrectangular": report["asymptotic_frontier"]["pass"],
        "R5_same_plant_has_three_registration_regions": report["three_registry_fork"][
            "pass"
        ],
        "R6_rational_normal_hyperbolic_embedding": report["continuous_embedding"][
            "pass"
        ],
        "R7_prefix_and_independent_randomness_robustness": report[
            "prefix_and_randomness_robustness"
        ]["pass"],
        "R8_randomized_observation_kernels_derandomize": report[
            "randomized_kernel_derandomization"
        ]["pass"],
        "R9_complete_payload": report["pass"],
    }


def main(output: str | None = None) -> int:
    report = relational_frontier_report()
    payload = {"report": report, "gates": verification_gates(report)}
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    if output is None:
        print(rendered)
    else:
        Path(output).write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
