"""Import-independent verifier for the ASMP-4 v0.7 relational frontier."""

from __future__ import annotations

import json
from collections import Counter
from fractions import Fraction
from itertools import product
from math import log2
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
MILLENNIUM = HERE.parent
ACTIONS = ("a", "d", "e")
SAFE = (
    frozenset({"a", "d"}),
    frozenset({"a", "e"}),
    frozenset({"d"}),
    frozenset({"e"}),
)
COARSE = ((0, 1), (2,), (3,))
RAW = ((0,), (1,), (2,), (3,))
COMPUTED = ((0, 2), (1, 3))
EXPECTED_FRONTIERS = {
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


def independent_partitions(size: int) -> list[tuple[tuple[int, ...], ...]]:
    """Generate partitions via restricted-growth strings."""

    if size < 1:
        raise ValueError("size must be positive")
    rows = []
    for labels in product(range(size), repeat=size):
        if labels[0] != 0:
            continue
        maximum = 0
        valid = True
        for index in range(1, size):
            if labels[index] > maximum + 1:
                valid = False
                break
            maximum = max(maximum, labels[index])
        if not valid or set(labels) != set(range(maximum + 1)):
            continue
        rows.append(
            tuple(
                tuple(index for index, label in enumerate(labels) if label == block)
                for block in range(maximum + 1)
            )
        )
    return rows


def independent_block_choices(
    relation: tuple[frozenset[str], ...],
    partition: tuple[tuple[int, ...], ...],
) -> tuple[tuple[str, ...], ...]:
    choices = []
    for block in partition:
        allowed = set(ACTIONS)
        for mode in block:
            allowed &= relation[mode]
        if not allowed:
            return ()
        choices.append(tuple(sorted(allowed, key=ACTIONS.index)))
    return tuple(choices)


def independent_minimum_actions(
    relation: tuple[frozenset[str], ...],
    partition: tuple[tuple[int, ...], ...],
) -> int | None:
    choices = independent_block_choices(relation, partition)
    if not choices:
        return None
    for count in range(1, len(ACTIONS) + 1):
        for candidate in product((False, True), repeat=len(ACTIONS)):
            chosen = {
                action
                for action, include in zip(ACTIONS, candidate, strict=True)
                if include
            }
            if len(chosen) == count and all(chosen & set(row) for row in choices):
                return count
    raise AssertionError("cover search failed")


def independent_local_census() -> dict[str, Any]:
    rows = []
    schemes = []
    for name, partition in (("coarse", COARSE), ("raw", RAW)):
        choices = independent_block_choices(SAFE, partition)
        assignments = tuple(product(*choices))
        histogram = Counter(len(set(row)) for row in assignments)
        rows.append(
            {
                "partition": name,
                "assignments": len(assignments),
                "histogram": dict(sorted(histogram.items())),
            }
        )
        schemes.extend((name, assignment) for assignment in assignments)
    pairs = sorted(
        {
            (len(COARSE if name == "coarse" else RAW), len(set(row)))
            for name, row in schemes
        }
    )
    nondominated = [
        pair
        for pair in pairs
        if not any(
            other != pair and other[0] <= pair[0] and other[1] <= pair[1]
            for other in pairs
        )
    ]
    return {
        "rows": rows,
        "schemes": [
            {"partition": name, "actions": list(assignment)}
            for name, assignment in schemes
        ],
        "nondominated": [list(pair) for pair in nondominated],
        "pass": (
            rows
            == [
                {"partition": "coarse", "assignments": 1, "histogram": {3: 1}},
                {
                    "partition": "raw",
                    "assignments": 4,
                    "histogram": {2: 1, 3: 3},
                },
            ]
            and nondominated == [(3, 3), (4, 2)]
        ),
    }


def independent_minimality_census() -> dict[str, Any]:
    rows = []
    signature_histogram: Counter[str] = Counter()
    for mode_count in range(1, 5):
        partitions = independent_partitions(mode_count)
        relations = 0
        feasible = 0
        tradeoff_relations = 0
        tradeoff_pairs = 0
        nonempty_subsets = tuple(
            frozenset(
                action
                for action, included in zip(ACTIONS, flags, strict=True)
                if included
            )
            for flags in product((False, True), repeat=len(ACTIONS))
            if any(flags)
        )
        for relation in product(nonempty_subsets, repeat=mode_count):
            relations += 1
            signatures = []
            for partition in partitions:
                action_count = independent_minimum_actions(relation, partition)
                if action_count is None:
                    signatures.append(None)
                else:
                    feasible += 1
                    signatures.append((len(partition), action_count))
            found = False
            for left in signatures:
                if left is None:
                    continue
                for right in signatures:
                    if right is not None and left[0] < right[0] and left[1] > right[1]:
                        found = True
                        tradeoff_pairs += 1
                        signature_histogram[
                            f"({left[0]},{left[1]})->({right[0]},{right[1]})"
                        ] += 1
            tradeoff_relations += int(found)
        rows.append(
            {
                "modes": mode_count,
                "relations": relations,
                "partitions": len(partitions),
                "feasible_cells": feasible,
                "tradeoff_relations": tradeoff_relations,
                "tradeoff_pairs": tradeoff_pairs,
            }
        )
    expected = [
        (1, 7, 1, 7, 0, 0),
        (2, 49, 2, 86, 0, 0),
        (3, 343, 5, 1289, 0, 0),
        (4, 2401, 15, 22839, 72, 72),
    ]
    observed = [
        (
            row["modes"],
            row["relations"],
            row["partitions"],
            row["feasible_cells"],
            row["tradeoff_relations"],
            row["tradeoff_pairs"],
        )
        for row in rows
    ]
    return {
        "rows": rows,
        "signature_histogram": dict(signature_histogram),
        "pass": observed == expected
        and dict(signature_histogram) == {"(3,3)->(4,2)": 72},
    }


Language = frozenset[tuple[str, ...]]


def _independent_prune(
    candidates: Iterable[tuple[int, Language]],
) -> tuple[tuple[int, Language], ...]:
    best: dict[Language, int] = {}
    for reads, language in candidates:
        best[language] = min(reads, best.get(language, reads))
    kept: list[tuple[int, Language]] = []
    for language, reads in sorted(best.items(), key=lambda row: (row[1], len(row[0]))):
        if any(
            prior_reads <= reads and prior_language <= language
            for prior_reads, prior_language in kept
        ):
            continue
        kept.append((reads, language))
    return tuple(kept)


def independent_adaptive_census(max_horizon: int = 3) -> dict[str, Any]:
    """Build explicit action-word sets rather than central integer masks."""

    if max_horizon != 3:
        raise ValueError("the frozen independent census has horizon three")
    local = independent_local_census()
    schemes = [tuple(row["actions"]) for row in local["schemes"]]
    states: tuple[tuple[int, Language], ...] = ((1, frozenset({()})),)
    rows = []
    for horizon in range(1, max_horizon + 1):
        candidates = []
        for actions in schemes:
            for children in product(states, repeat=len(actions)):
                language = frozenset(
                    (action, *word)
                    for action, child in zip(actions, children, strict=True)
                    for word in child[1]
                )
                candidates.append((sum(child[0] for child in children), language))
        states = _independent_prune(candidates)
        pairs = sorted({(reads, len(language)) for reads, language in states})
        frontier = tuple(
            pair
            for pair in pairs
            if not any(
                other != pair and other[0] <= pair[0] and other[1] <= pair[1]
                for other in pairs
            )
        )
        rows.append(
            {
                "horizon": horizon,
                "candidates": len(candidates),
                "states": len(states),
                "frontier": [list(pair) for pair in frontier],
                "matches": frontier == EXPECTED_FRONTIERS[horizon],
            }
        )
    return {
        "rows": rows,
        "pass": (
            [row["candidates"] for row in rows] == [5, 72, 84672]
            and [row["states"] for row in rows] == [2, 12, 1872]
            and all(row["matches"] for row in rows)
        ),
    }


def independent_moment_certificate(
    adaptive: dict[str, Any], local: dict[str, Any]
) -> dict[str, Any]:
    theta = log2(1.5)
    factors = []
    for scheme in local["schemes"]:
        multiplicities = Counter(scheme["actions"])
        factor = sum(len_group**theta for len_group in multiplicities.values())
        factors.append(factor)
    frontier_checks = []
    for row in adaptive["rows"]:
        horizon = row["horizon"]
        for reads, writes in row["frontier"]:
            frontier_checks.append(
                reads >= 3**horizon
                and writes >= 2**horizon
                and theta * log2(reads) + (1 - theta) * log2(writes)
                >= horizon * log2(3) - 1e-12
            )
    schedule_checks = []
    for horizon in range(1, 13):
        for coarse_steps in range(horizon + 1):
            reads = 3**coarse_steps * 4 ** (horizon - coarse_steps)
            writes = 3**coarse_steps * 2 ** (horizon - coarse_steps)
            schedule_checks.append(
                abs(
                    theta * log2(reads) + (1 - theta) * log2(writes) - horizon * log2(3)
                )
                <= 1e-12
            )
    return {
        "theta": theta,
        "local_factors": factors,
        "frontier_checks": len(frontier_checks),
        "schedule_checks": len(schedule_checks),
        "pass": (
            sum(abs(factor - 3) <= 1e-12 for factor in factors) == 2
            and sum(abs(factor - 3.5) <= 1e-12 for factor in factors) == 3
            and all(factor >= 3 - 1e-12 for factor in factors)
            and all(frontier_checks)
            and all(schedule_checks)
        ),
    }


def _basis(z_value: Fraction, index: int) -> Fraction:
    points = tuple(Fraction(value) for value in (-3, -1, 1, 3))
    result = Fraction(1)
    for other_index, point in enumerate(points):
        if other_index != index:
            result *= (z_value - point) / (points[index] - point)
    return result


def _h(mode: int, control: Fraction) -> Fraction:
    rows = (
        control * (control - 1),
        control * (control - 2),
        control - 1,
        control - 2,
    )
    return rows[mode]


def _dh(mode: int, control: Fraction) -> Fraction:
    rows = (2 * control - 1, 2 * control - 2, Fraction(1), Fraction(1))
    return rows[mode]


def independent_embedding() -> dict[str, Any]:
    points = tuple(Fraction(value) for value in (-3, -1, 1, 3))
    controls = {"a": Fraction(0), "d": Fraction(1), "e": Fraction(2)}
    rows = []
    for mode, point in enumerate(points):
        for action, control in controls.items():
            value = sum(_basis(point, index) * _h(index, control) for index in range(4))
            derivative = sum(
                _basis(point, index) * _dh(index, control) for index in range(4)
            )
            rows.append(
                {
                    "mode": mode,
                    "action": action,
                    "value": value,
                    "derivative": derivative,
                    "safe": action in SAFE[mode],
                }
            )
    return {
        "safe_pairs": sum(row["safe"] for row in rows),
        "unsafe_pairs": sum(not row["safe"] for row in rows),
        "pass": (
            all(
                row["value"] == 0 and row["derivative"] != 0
                for row in rows
                if row["safe"]
            )
            and all(row["value"] != 0 for row in rows if not row["safe"])
        ),
    }


def independent_registry_fork() -> dict[str, Any]:
    computed = independent_minimum_actions(SAFE, COMPUTED)
    coarse = independent_minimum_actions(SAFE, COARSE)
    raw = independent_minimum_actions(SAFE, RAW)
    return {
        "computed_pair": [len(COMPUTED), computed],
        "coarse_pair": [len(COARSE), coarse],
        "raw_pair": [len(RAW), raw],
        "pass": (computed, coarse, raw) == (2, 3, 2),
    }


def independent_randomized_kernel_census() -> dict[str, Any]:
    """Enumerate stochastic supports with explicit Python sets."""

    rows = []
    failures = []
    for label_count in range(1, 5):
        labels = tuple(range(label_count))
        nonempty_label_sets = tuple(
            frozenset(
                label for label, included in zip(labels, flags, strict=True) if included
            )
            for flags in product((False, True), repeat=label_count)
            if any(flags)
        )
        total = 0
        surjective = 0
        feasible = 0
        randomized = 0
        sensor_maps = 0
        controller_kernels = 0
        minimum_histogram: Counter[int] = Counter()
        for kernel in product(nonempty_label_sets, repeat=4):
            total += 1
            if set().union(*kernel) != set(labels):
                continue
            surjective += 1
            common_actions = []
            for label in labels:
                possible_modes = tuple(
                    mode for mode, support in enumerate(kernel) if label in support
                )
                common = set(ACTIONS)
                for mode in possible_modes:
                    common &= SAFE[mode]
                common_actions.append(frozenset(common))
            if any(not common for common in common_actions):
                continue
            feasible += 1
            randomized += int(any(len(support) > 1 for support in kernel))
            selections = tuple(product(*kernel))
            sensor_maps += len(selections)
            minimum_histogram[min(len(set(selection)) for selection in selections)] += 1
            for selection in selections:
                for label in set(selection):
                    modes = tuple(
                        mode
                        for mode, selected in enumerate(selection)
                        if selected == label
                    )
                    common = set(ACTIONS)
                    for mode in modes:
                        common &= SAFE[mode]
                    if not common:
                        failures.append((kernel, selection, label))
            controller_choices = []
            for common in common_actions:
                ordered = tuple(sorted(common, key=ACTIONS.index))
                choices = tuple(
                    frozenset(
                        action
                        for action, included in zip(ordered, flags, strict=True)
                        if included
                    )
                    for flags in product((False, True), repeat=len(ordered))
                    if any(flags)
                )
                controller_choices.append(choices)
            minimizing = min(
                selections, key=lambda selection: (len(set(selection)), selection)
            )
            for controller_support in product(*controller_choices):
                controller_kernels += 1
                original_actions = set().union(*controller_support)
                selected_actions = {
                    min(controller_support[label], key=ACTIONS.index)
                    for label in set(minimizing)
                }
                if not selected_actions <= original_actions:
                    failures.append((kernel, controller_support, "write_support"))
        rows.append(
            {
                "labels": label_count,
                "support_kernels": total,
                "surjective": surjective,
                "feasible": feasible,
                "randomized": randomized,
                "sensor_maps": sensor_maps,
                "controller_kernels": controller_kernels,
                "minimum_histogram": dict(sorted(minimum_histogram.items())),
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
            row["surjective"],
            row["feasible"],
            row["randomized"],
            row["sensor_maps"],
            row["controller_kernels"],
            row["minimum_histogram"],
        )
        for row in rows
    ]
    return {
        "rows": rows,
        "totals": {
            "support_kernels": sum(row["support_kernels"] for row in rows),
            "surjective": sum(row["surjective"] for row in rows),
            "feasible": sum(row["feasible"] for row in rows),
            "randomized": sum(row["randomized"] for row in rows),
            "sensor_maps": sum(row["sensor_maps"] for row in rows),
            "controller_kernels": sum(row["controller_kernels"] for row in rows),
        },
        "failures": len(failures),
        "pass": observed == expected and not failures,
    }


def claim_exactness() -> dict[str, Any]:
    claim_path = HERE / "relational_claim_v0_7.json"
    if not claim_path.exists():
        return {"exists": False, "pass": False}
    claim = json.loads(claim_path.read_text(encoding="utf-8"))
    expected = {
        "relations_through_four_modes": 2800,
        "feasible_relation_partition_cells": 24221,
        "strict_tradeoff_relations_at_four_modes": 72,
        "strict_tradeoff_partition_pairs": 72,
        "first_tradeoff_signature": "(3,3)->(4,2)",
    }
    return {
        "exists": True,
        "pass": (
            claim.get("schema_version") == "asmp4_relational_action_frontier_claim_v0_7"
            and claim.get("minimality_census") == expected
            and claim.get("adaptive_tree_census", {}).get("horizon_three_candidates")
            == 84672
            and claim.get("adaptive_tree_census", {}).get("horizon_three_states")
            == 1872
            and claim.get("randomized_kernel_census", {}).get("support_kernels")
            == 53108
            and claim.get("randomized_kernel_census", {}).get("zero_error_feasible")
            == 994
            and claim.get("randomized_kernel_census", {}).get(
                "derandomization_failures"
            )
            == 0
            and claim.get("three_registry_regions", {}).get("forced_raw")
            == "[2,infinity) x [1,infinity)"
        ),
    }


def document_sentinels() -> dict[str, Any]:
    paths = {
        "theorem": HERE / "THEOREM.md",
        "result": HERE / "RESULT.md",
        "stopping": HERE / "STOPPING_ARGUMENT_v0_7.md",
        "completion": HERE / "COMPLETION_AUDIT_v0_7.md",
        "prior_art": HERE / "PRIOR_ART_AUDIT_v0_7.md",
    }
    if not all(path.exists() for path in paths.values()):
        return {"files_exist": False, "pass": False}
    text = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}
    checks = {
        "moment_theorem": "Phi_theta(c)=sum_w c_w^theta" in text["theorem"],
        "exact_wedge": "theta r_read + (1-theta) r_write >= log2 3" in text["theorem"],
        "adaptive_scope": "public read-history adaptation" in text["theorem"],
        "minimality": "2,800 nonempty" in text["result"],
        "three_regions": "three pairwise-distinct exact regions" in text["result"],
        "stopping": "cannot select a sensor registry" in text["stopping"],
        "completion": "84,672" in text["completion"],
        "prior_art": "does not claim" in text["prior_art"],
        "kernel_derandomization": "support-derandomization theorem" in text["theorem"],
    }
    return {"files_exist": True, "checks": checks, "pass": all(checks.values())}


def predecessor_firewall() -> dict[str, Any]:
    claim_path = (
        MILLENNIUM / "asmp4_registration_fork_v0_6" / "registration_claim_v0_6.json"
    )
    if not claim_path.exists():
        return {"pass": False}
    claim = json.loads(claim_path.read_text(encoding="utf-8"))
    return {
        "v0_6_schema": claim.get("schema_version"),
        "pass": (
            claim.get("schema_version") == "asmp4_registration_fork_claim_v0_6"
            and claim.get("computed_sensor_class", {}).get("closed_asymptotic_region")
            == "[1,infinity) x [1,infinity)"
            and claim.get("forced_raw_sensor_class", {}).get("closed_asymptotic_region")
            == "[2,infinity) x [1,infinity)"
        ),
    }


def independent_report() -> dict[str, Any]:
    local = independent_local_census()
    minimality = independent_minimality_census()
    adaptive = independent_adaptive_census()
    moment = independent_moment_certificate(adaptive, local)
    embedding = independent_embedding()
    registries = independent_registry_fork()
    randomized_kernels = independent_randomized_kernel_census()
    claim = claim_exactness()
    documents = document_sentinels()
    predecessor = predecessor_firewall()
    checks = {
        "I0_independent_local_scheme_census": local["pass"],
        "I1_independent_minimality_census": minimality["pass"],
        "I2_independent_explicit_language_census": adaptive["pass"],
        "I3_independent_moment_certificate": moment["pass"],
        "I4_independent_rational_embedding": embedding["pass"],
        "I5_independent_three_registry_fork": registries["pass"],
        "I6_independent_randomized_kernel_derandomization": randomized_kernels["pass"],
        "I7_claim_exactness": claim["pass"],
        "I8_document_sentinels": documents["pass"],
        "I9_predecessor_firewall": predecessor["pass"],
    }
    return {
        "schema_version": "asmp4_relational_action_frontier_independent_v0_7",
        "local_scheme_census": local,
        "minimality_census": minimality,
        "adaptive_tree_census": adaptive,
        "moment_certificate": moment,
        "continuous_embedding": embedding,
        "three_registry_fork": registries,
        "randomized_kernel_derandomization": randomized_kernels,
        "claim_exactness": claim,
        "document_sentinels": documents,
        "predecessor_firewall": predecessor,
        "checks": checks,
        "pass": all(checks.values()),
    }


def main() -> int:
    report = independent_report()
    print(json.dumps(report, indent=2, sort_keys=True, default=str))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
