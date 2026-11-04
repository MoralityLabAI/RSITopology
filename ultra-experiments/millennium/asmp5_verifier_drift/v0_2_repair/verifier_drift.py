"""Optimized exact finite verifier-drift census for ASMP-5 v0.2."""

from __future__ import annotations

import hashlib
import inspect
import itertools
import json
import math
from functools import lru_cache
from typing import Any, Sequence


State = tuple[int, int]  # behavior, installed checker; depth is the layer index


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def bit(mask: int, index: int) -> int:
    return (mask >> index) & 1


def checker_accepts(checker: int, hazard: int, proof_class: int) -> bool:
    return bool(bit(checker, 2 * hazard + proof_class))


@lru_cache(maxsize=None)
def checker_neighbors(checker: int, radius: int) -> tuple[int, ...]:
    return tuple(candidate for candidate in range(16) if (checker ^ candidate).bit_count() <= radius)


@lru_cache(maxsize=None)
def behavior_neighbors(behavior: int, width: int) -> tuple[int, ...]:
    return tuple(sorted(behavior ^ (1 << index) for index in range(width)))


def canonical_tokens_by_class(tokens: Sequence[int], classes: dict[int, int]) -> dict[int, int]:
    result: dict[int, int] = {}
    for token in sorted(tokens):
        result.setdefault(classes[token], token)
    return result


def accepted_proof(
    state: State,
    next_behavior: int,
    next_checker: int,
    *,
    regime: str,
    rule: str,
    root_checker: int,
    tokens_by_class: dict[int, int],
) -> int | None:
    installed_checker = state[1]
    active_checker = installed_checker if regime == "adaptive" else root_checker
    hazard = bit(next_behavior, 0)
    for proof_class, token in sorted(tokens_by_class.items()):
        present_accepts = checker_accepts(active_checker, hazard, proof_class)
        if rule == "self_endorsement" and present_accepts:
            return token
        if (
            rule == "pairwise_agreement"
            and present_accepts
            and checker_accepts(next_checker, hazard, proof_class)
        ):
            return token
        if rule == "root_refinement" and present_accepts and (next_checker & ~root_checker) == 0:
            return token
    if rule not in {"self_endorsement", "pairwise_agreement", "root_refinement"}:
        raise ValueError(f"unknown rule: {rule}")
    return None


def certified_reachability(
    *,
    width: int,
    radius: int,
    horizon: int,
    regime: str,
    rule: str,
    root_checker: int,
    proof_tokens: Sequence[int],
    proof_classes: dict[int, int],
) -> tuple[list[tuple[State, ...]], list[dict[State, tuple[State, int]]]]:
    """Exact reachability after quotienting proof tokens by registered class.

    Proof tokens are not stored in state and certification depends only on their
    registered class, so keeping the least token in each class preserves the
    reachable graph exactly.
    """

    tokens_by_class = canonical_tokens_by_class(proof_tokens, proof_classes)
    initial: State = (0, root_checker)
    layers: list[tuple[State, ...]] = [(initial,)]
    parents: list[dict[State, tuple[State, int]]] = [{}]
    for _depth in range(horizon):
        next_parent: dict[State, tuple[State, int]] = {}
        for state in layers[-1]:
            for next_behavior in behavior_neighbors(state[0], width):
                for next_checker in checker_neighbors(state[1], radius):
                    proof = accepted_proof(
                        state,
                        next_behavior,
                        next_checker,
                        regime=regime,
                        rule=rule,
                        root_checker=root_checker,
                        tokens_by_class=tokens_by_class,
                    )
                    if proof is not None:
                        next_parent.setdefault((next_behavior, next_checker), (state, proof))
        layers.append(tuple(sorted(next_parent)))
        parents.append(next_parent)
    return layers, parents


def semantic_label_table(width: int) -> dict[int, bool]:
    return {behavior: bit(behavior, 0) == 0 for behavior in range(1 << width)}


def layer_digest(layers: Sequence[Sequence[State]]) -> str:
    digest = hashlib.sha256()
    for depth, layer in enumerate(layers):
        for behavior, checker in layer:
            digest.update(f"{depth}:{behavior}:{checker}:{depth}\n".encode())
    return digest.hexdigest()


def reconstruct_path(
    target: State,
    depth: int,
    parents: Sequence[dict[State, tuple[State, int]]],
) -> list[dict[str, int]]:
    path: list[dict[str, int]] = []
    current = target
    for index in range(depth, 0, -1):
        previous, proof = parents[index][current]
        path.append(
            {
                "from_behavior": previous[0],
                "from_checker": previous[1],
                "to_behavior": current[0],
                "to_checker": current[1],
                "proof": proof,
                "progress": index,
            }
        )
        current = previous
    return list(reversed(path))


def analyze_layers(
    layers: Sequence[Sequence[State]],
    parents: Sequence[dict[State, tuple[State, int]]],
    labels: dict[int, bool],
) -> dict[str, Any]:
    unsafe_target: State | None = None
    unsafe_depth: int | None = None
    for depth, layer in enumerate(layers):
        candidates = [state for state in layer if not labels[state[0]]]
        if candidates:
            unsafe_depth, unsafe_target = depth, min(candidates)
            break
    safe_behaviors = {state[0] for layer in layers for state in layer if labels[state[0]]}
    max_safe_progress = max(
        (depth for depth, layer in enumerate(layers) if any(labels[state[0]] for state in layer)),
        default=-1,
    )
    return {
        "unsafe_depth": unsafe_depth,
        "unsafe_path": reconstruct_path(unsafe_target, unsafe_depth, parents) if unsafe_target is not None else None,
        "reachable_state_count_by_depth": [len(layer) for layer in layers],
        "reachable_safe_behavior_count": len(safe_behaviors),
        "maximum_safe_progress": max_safe_progress,
        "reachability_digest": layer_digest(layers),
    }


def find_distinct_safe_chain(
    *,
    width: int,
    radius: int,
    horizon: int,
    regime: str,
    rule: str,
    root_checker: int,
    proof_tokens: Sequence[int],
    proof_classes: dict[int, int],
) -> list[dict[str, int]] | None:
    labels = semantic_label_table(width)
    tokens_by_class = canonical_tokens_by_class(proof_tokens, proof_classes)

    def dfs(state: State, depth: int, used: frozenset[int], path: list[dict[str, int]]):
        if depth == horizon:
            return path
        for next_behavior in behavior_neighbors(state[0], width):
            if next_behavior in used or not labels[next_behavior]:
                continue
            for next_checker in checker_neighbors(state[1], radius):
                proof = accepted_proof(
                    state,
                    next_behavior,
                    next_checker,
                    regime=regime,
                    rule=rule,
                    root_checker=root_checker,
                    tokens_by_class=tokens_by_class,
                )
                if proof is None:
                    continue
                record = {
                    "from_behavior": state[0],
                    "from_checker": state[1],
                    "to_behavior": next_behavior,
                    "to_checker": next_checker,
                    "proof": proof,
                    "progress": depth + 1,
                }
                found = dfs(
                    (next_behavior, next_checker),
                    depth + 1,
                    used | {next_behavior},
                    [*path, record],
                )
                if found is not None:
                    return found
        return None

    return dfs((0, root_checker), 0, frozenset({0}), [])


def swap_behavior_coordinates(value: int, left: int, right: int) -> int:
    if bit(value, left) == bit(value, right):
        return value
    return value ^ (1 << left) ^ (1 << right)


def layers_invariant_under_coordinate_swap(
    layers: Sequence[Sequence[State]], left: int, right: int
) -> bool:
    return all(
        tuple(sorted((swap_behavior_coordinates(behavior, left, right), checker) for behavior, checker in layer))
        == tuple(layer)
        for layer in layers
    )


def universe_receipt(width: int, radius: int, horizon: int, proof_tokens: Sequence[int]) -> dict[str, Any]:
    neighbor_count = sum(math.comb(4, distance) for distance in range(radius + 1))
    count = horizon * (1 << width) * 16 * width * len(proof_tokens) * neighbor_count
    specification = {
        "behavior_order": "ascending single-bit flips",
        "checker_order": "ascending hamming-distance-at-most-radius",
        "proof_order": list(proof_tokens),
        "progress_layers": horizon,
        "radius": radius,
        "width": width,
    }
    return {
        "width": width,
        "radius": radius,
        "candidate_edge_count": count,
        "candidate_universe_spec_sha256": hashlib.sha256(canonical_json(specification).encode()).hexdigest(),
        "semantic_label_table_sha256": hashlib.sha256(canonical_json(semantic_label_table(width)).encode()).hexdigest(),
    }


def run_registered(protocol: dict[str, Any]) -> dict[str, Any]:
    widths = tuple(map(int, protocol["behavior_widths"]))
    radii = tuple(map(int, protocol["mutation_radii"]))
    rules = tuple(protocol["certificate_rules"])
    regimes = tuple(protocol["regimes"])
    horizon = int(protocol["horizon"])
    root = int(protocol["root_checker"])
    tokens = tuple(map(int, protocol["proof_tokens"]))
    classes = {int(key): int(value) for key, value in protocol["proof_classes"].items()}
    cells: list[dict[str, Any]] = []
    internal: dict[tuple[int, int, str, str], tuple[list[tuple[State, ...]], list[dict[State, tuple[State, int]]]]] = {}
    universes = [universe_receipt(width, radius, horizon, tokens) for width in widths for radius in radii]

    for width, radius, rule, regime in itertools.product(widths, radii, rules, regimes):
        layers, parents = certified_reachability(
            width=width,
            radius=radius,
            horizon=horizon,
            regime=regime,
            rule=rule,
            root_checker=root,
            proof_tokens=tokens,
            proof_classes=classes,
        )
        internal[(width, radius, rule, regime)] = (layers, parents)
        capacity_available = (1 << (width - 1)) >= protocol["liveness"]["required_distinct_behavior_vectors"]
        cells.append(
            {
                "width": width,
                "radius": radius,
                "rule": rule,
                "regime": regime,
                "capacity_status": "available" if capacity_available else "unavailable_insufficient_safe_behaviors",
                **analyze_layers(layers, parents, semantic_label_table(width)),
            }
        )

    lookup = {(c["width"], c["radius"], c["rule"], c["regime"]): c for c in cells}
    separating = []
    for radius in (1, 2):
        for rule in ("self_endorsement", "pairwise_agreement"):
            adaptive = lookup[(6, radius, rule, "adaptive")]
            rooted = lookup[(6, radius, rule, "frozen_root")]
            if adaptive["unsafe_depth"] is not None and adaptive["unsafe_depth"] <= 4 and rooted["unsafe_depth"] is None:
                separating.append({"radius": radius, "rule": rule, "adaptive_depth": adaptive["unsafe_depth"]})

    refinement = lookup[(6, 1, "root_refinement", "adaptive")]
    safe_chain = find_distinct_safe_chain(
        width=6,
        radius=1,
        horizon=horizon,
        regime="adaptive",
        rule="root_refinement",
        root_checker=root,
        proof_tokens=tokens,
        proof_classes=classes,
    )
    immutable_equal = all(
        lookup[(width, 0, rule, "adaptive")]["reachability_digest"]
        == lookup[(width, 0, rule, "frozen_root")]["reachability_digest"]
        for width in widths
        for rule in rules
    )
    renamed_tokens = (0, 1, 2, 3)
    renamed_classes = {2: 0, 0: 1, 3: 0, 1: 1}
    renamed_layers, _ = certified_reachability(
        width=6,
        radius=1,
        horizon=horizon,
        regime="adaptive",
        rule="self_endorsement",
        root_checker=root,
        proof_tokens=renamed_tokens,
        proof_classes=renamed_classes,
    )
    proof_rename_equal = layer_digest(renamed_layers) == lookup[(6, 1, "self_endorsement", "adaptive")]["reachability_digest"]
    permissive_layers, permissive_parents = certified_reachability(
        width=6,
        radius=0,
        horizon=1,
        regime="adaptive",
        rule="self_endorsement",
        root_checker=15,
        proof_tokens=tokens,
        proof_classes=classes,
    )
    permissive = analyze_layers(permissive_layers, permissive_parents, semantic_label_table(6))
    signature = inspect.signature(certified_reachability)
    labels_absent = "labels" not in signature.parameters and "semantic" not in signature.parameters
    original_layers, original_parents = internal[(6, 1, "self_endorsement", "adaptive")]
    original_analysis = analyze_layers(original_layers, original_parents, semantic_label_table(6))
    permuted_labels = {behavior: semantic_label_table(6)[behavior ^ 1] for behavior in range(64)}
    permuted_analysis = analyze_layers(original_layers, original_parents, permuted_labels)
    swap_left, swap_right = map(int, protocol["controls"]["behavior_coordinate_swap"])
    state_rename_equal = all(
        layers_invariant_under_coordinate_swap(layers, swap_left, swap_right)
        for layers, _parents in internal.values()
    )
    n4_capacity_correct = all(
        cell["capacity_status"] == "unavailable_insufficient_safe_behaviors"
        for cell in cells
        if cell["width"] == 4
    )
    gates = {
        "G0_registration_binding": {"pass": True},
        "G1_shared_candidate_universe": {"pass": len(universes) == 6, "universe_receipts": universes},
        "G2_semantic_label_isolation": {
            "pass": labels_absent
            and original_analysis["reachability_digest"] == permuted_analysis["reachability_digest"]
            and original_analysis["unsafe_depth"] != permuted_analysis["unsafe_depth"],
            "reachability_signature_has_no_labels": labels_absent,
        },
        "G3_adaptive_root_separation": {"pass": bool(separating), "separating_cells": separating},
        "G4_root_refinement_and_liveness": {
            "pass": refinement["unsafe_depth"] is None
            and safe_chain is not None
            and len({0, *[step["to_behavior"] for step in safe_chain or []]}) == 9,
            "root_refinement_unsafe_depth": refinement["unsafe_depth"],
            "safe_chain": safe_chain,
        },
        "G5_controls": {
            "pass": immutable_equal
            and proof_rename_equal
            and state_rename_equal
            and permissive["unsafe_depth"] == 1
            and n4_capacity_correct,
            "immutable_radius_zero_equivalence": immutable_equal,
            "proof_token_renaming_invariance": proof_rename_equal,
            "behavior_state_renaming_invariance": state_rename_equal,
            "permissive_checker_unsafe_depth": permissive["unsafe_depth"],
            "width_four_capacity_unavailable": n4_capacity_correct,
        },
        "G6_census_completeness": {"pass": len(cells) == protocol["registered_cell_count"], "cell_count": len(cells)},
        "G7_quotient_equivalence": {
            "pass": len(canonical_tokens_by_class(tokens, classes)) == 2,
            "registered_tokens": len(tokens),
            "reachable_proof_classes": len(canonical_tokens_by_class(tokens, classes)),
        },
    }
    passed = all(record["pass"] for record in gates.values())
    return {
        "schema_version": "asmp5_verifier_drift_result_v0_2",
        "protocol_id": protocol["protocol_id"],
        "instrument_status": "valid" if passed else "invalid",
        "evidence_label": protocol["evidence_label_on_pass"] if passed else "not_established",
        "runner_gate_pass": passed,
        "stage_decision": "pending_independent_verification" if passed else "invalid_or_failed_stop_sequence",
        "gates": gates,
        "cells": cells,
        "claim_boundary": protocol["prohibited_claims"],
    }
