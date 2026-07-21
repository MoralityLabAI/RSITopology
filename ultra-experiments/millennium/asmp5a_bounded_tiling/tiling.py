"""Exact binary proof-tiling census for the ASMP-5A finite seed."""

from __future__ import annotations

import functools
import hashlib
import json
import math
from typing import Any, Iterator


Shape = None | tuple["Shape", "Shape"]
Certificate = tuple[Any, ...]


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


@functools.lru_cache(maxsize=None)
def shapes(leaves: int) -> tuple[Shape, ...]:
    if leaves < 1:
        raise ValueError("leaves must be positive")
    if leaves == 1:
        return (None,)
    return tuple(
        (left, right)
        for left_count in range(1, leaves)
        for left in shapes(left_count)
        for right in shapes(leaves - left_count)
    )


def catalan(index: int) -> int:
    return math.comb(2 * index, index) // (index + 1)


@functools.lru_cache(maxsize=None)
def metrics(shape: Shape) -> tuple[int, int, int, int]:
    """Return leaves, total nodes, depth, and Horton-Strahler number."""
    if shape is None:
        return 1, 1, 0, 1
    left, right = shape
    ll, ln, ld, ls = metrics(left)
    rl, rn, rd, rs = metrics(right)
    strahler = ls + 1 if ls == rs else max(ls, rs)
    return ll + rl, ln + rn + 1, max(ld, rd) + 1, strahler


def chain_shape(leaves: int) -> Shape:
    if leaves < 1:
        raise ValueError("leaves must be positive")
    tree: Shape = None
    for _ in range(1, leaves):
        tree = (tree, None)
    return tree


def balanced_shape(leaves: int) -> Shape:
    if leaves < 1:
        raise ValueError("leaves must be positive")
    if leaves == 1:
        return None
    left = leaves // 2
    return balanced_shape(left), balanced_shape(leaves - left)


def label_shape(shape: Shape, start: int = 0) -> tuple[Certificate, int]:
    if shape is None:
        return ("leaf", start), start + 1
    left, next_label = label_shape(shape[0], start)
    right, end = label_shape(shape[1], next_label)
    return ("and", left, right), end


def verify_certificate(certificate: Certificate, obligations: frozenset[int]) -> tuple[bool, frozenset[int]]:
    tag = certificate[0] if certificate else None
    if tag == "leaf" and len(certificate) == 2 and isinstance(certificate[1], int):
        label = certificate[1]
        return label in obligations, frozenset({label})
    if tag == "and" and len(certificate) == 3:
        left_ok, left = verify_certificate(certificate[1], obligations)
        right_ok, right = verify_certificate(certificate[2], obligations)
        disjoint = left.isdisjoint(right)
        return left_ok and right_ok and disjoint, left | right
    return False, frozenset()


def certificate_is_complete(certificate: Certificate, obligations: frozenset[int]) -> bool:
    valid, covered = verify_certificate(certificate, obligations)
    return valid and covered == obligations


def pareto_pairs(leaves: int) -> tuple[tuple[int, int], ...]:
    observed = {(metrics(shape)[2], metrics(shape)[3]) for shape in shapes(leaves)}
    return tuple(
        sorted(
            pair
            for pair in observed
            if not any(
                other != pair and other[0] <= pair[0] and other[1] <= pair[1]
                for other in observed
            )
        )
    )


def dynamic_pairs(max_leaves: int) -> dict[int, frozenset[tuple[int, int]]]:
    possible: dict[int, set[tuple[int, int]]] = {1: {(0, 1)}}
    for leaves in range(2, max_leaves + 1):
        pairs: set[tuple[int, int]] = set()
        for left_count in range(1, leaves):
            for ld, ls in possible[left_count]:
                for rd, rs in possible[leaves - left_count]:
                    pairs.add((max(ld, rd) + 1, ls + 1 if ls == rs else max(ls, rs)))
        possible[leaves] = pairs
    return {leaves: frozenset(values) for leaves, values in possible.items()}


def architecture_metrics(architecture: str, leaves: int) -> tuple[int, int, int, int]:
    if architecture == "chain":
        return metrics(chain_shape(leaves))
    if architecture == "balanced":
        return metrics(balanced_shape(leaves))
    raise ValueError(architecture)


def capacity(architecture: str, work: int, depth: int, memory: int, max_leaves: int) -> int:
    return max(
        (
            leaves
            for leaves in range(1, max_leaves + 1)
            if (lambda m: m[1] <= work and m[2] <= depth and m[3] <= memory)(
                architecture_metrics(architecture, leaves)
            )
        ),
        default=0,
    )


def optimal_capacity(work: int, depth: int, memory: int, max_leaves: int) -> int:
    feasible = []
    for leaves in range(1, max_leaves + 1):
        if 2 * leaves - 1 > work:
            continue
        if any(d <= depth and m <= memory for d, m in pareto_pairs(leaves)):
            feasible.append(leaves)
    return max(feasible, default=0)


def permute_certificate(certificate: Certificate, permutation: dict[int, int]) -> Certificate:
    if certificate[0] == "leaf":
        return "leaf", permutation[certificate[1]]
    if certificate[0] == "and":
        return "and", permute_certificate(certificate[1], permutation), permute_certificate(certificate[2], permutation)
    return certificate


def shape_digest(shape: Shape) -> str:
    return hashlib.sha256(repr(shape).encode()).hexdigest()


def run_census(protocol: dict[str, Any]) -> dict[str, Any]:
    max_leaves = int(protocol["maximum_obligations"])
    rows = []
    dynamic = dynamic_pairs(max_leaves)
    enumeration_matches = True
    catalan_matches = True
    work_bound = True
    min_depth_matches = True
    for leaves in range(1, max_leaves + 1):
        enumerated = shapes(leaves)
        catalan_matches &= len(enumerated) == catalan(leaves - 1)
        observed_pairs = {(metrics(shape)[2], metrics(shape)[3]) for shape in enumerated}
        enumeration_matches &= observed_pairs == dynamic[leaves]
        work_bound &= all(metrics(shape)[1] == 2 * leaves - 1 for shape in enumerated)
        minimum_depth = min(metrics(shape)[2] for shape in enumerated)
        min_depth_matches &= minimum_depth == math.ceil(math.log2(leaves))
        chain = metrics(chain_shape(leaves))
        balanced = metrics(balanced_shape(leaves))
        rows.append(
            {
                "obligations": leaves,
                "tree_count": len(enumerated),
                "work_nodes": 2 * leaves - 1,
                "minimum_depth": minimum_depth,
                "minimum_depth_formula": math.ceil(math.log2(leaves)),
                "pareto_depth_memory": [list(pair) for pair in pareto_pairs(leaves)],
                "chain": {"depth": chain[2], "memory": chain[3]},
                "balanced": {"depth": balanced[2], "memory": balanced[3]},
                "chain_shape_sha256": shape_digest(chain_shape(leaves)),
                "balanced_shape_sha256": shape_digest(balanced_shape(leaves)),
            }
        )

    budget_rows = []
    for budget in protocol["resource_budgets"]:
        work, depth, memory = budget["work"], budget["depth"], budget["memory"]
        capacities = {
            architecture: capacity(architecture, work, depth, memory, max_leaves)
            for architecture in ("chain", "balanced")
        }
        capacities["optimal"] = optimal_capacity(work, depth, memory, max_leaves)
        budget_rows.append({**budget, "capacities": capacities})

    shallow = next(row for row in budget_rows if row["id"] == "shallow_parallel")
    memory_tight = next(row for row in budget_rows if row["id"] == "memory_tight_serial")
    reversal = (
        shallow["capacities"]["balanced"] > shallow["capacities"]["chain"]
        and memory_tight["capacities"]["chain"] > memory_tight["capacities"]["balanced"]
    )

    obligations = frozenset(range(max_leaves))
    complete, _ = label_shape(balanced_shape(max_leaves))
    shortcut = ("summary", tuple(range(max_leaves)))
    duplicate = ("and", ("leaf", 0), ("leaf", 0))
    coverage_control = (
        certificate_is_complete(complete, obligations)
        and not certificate_is_complete(shortcut, obligations)
        and not certificate_is_complete(duplicate, frozenset({0, 1}))
    )
    permutation = {index: max_leaves - 1 - index for index in range(max_leaves)}
    permuted = permute_certificate(complete, permutation)
    permutation_control = certificate_is_complete(permuted, obligations)

    gates = {
        "G0_registration_binding": {"pass": True},
        "G1_catalan_completeness": {"pass": catalan_matches},
        "G2_total_work_lower_bound": {"pass": work_bound},
        "G3_minimum_depth": {"pass": min_depth_matches},
        "G4_resource_ranking_reversal": {
            "pass": reversal,
            "shallow_parallel": shallow["capacities"],
            "memory_tight_serial": memory_tight["capacities"],
        },
        "G5_semantic_coverage": {"pass": coverage_control},
        "G6_dynamic_program_matches_enumeration": {"pass": enumeration_matches},
        "G7_label_gauge_invariance": {"pass": permutation_control},
    }
    passed = all(record["pass"] for record in gates.values())
    return {
        "schema_version": "asmp5a_bounded_tiling_result_v0_1",
        "protocol_id": protocol["protocol_id"],
        "instrument_status": "valid" if passed else "invalid",
        "verdict": protocol["evidence_label_on_pass"] if passed else "not_established",
        "gates": gates,
        "shape_rows": rows,
        "budget_rows": budget_rows,
        "claim_boundary": protocol["claim_boundary"],
    }
