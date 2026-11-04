"""Symbolic certificate compiler for ASMP-5 v0.3."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT_CHECKER = 0b0011
CHECKER_COUNT = 16
INDUCTIVE_RADII = (0, 1, 2, 3, 4)
TEMPLATE_WIDTH = 2
RULES = ("self_endorsement", "pairwise_agreement", "root_refinement")


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def bit(value: int, index: int) -> int:
    return (value >> index) & 1


def checker_accepts(checker: int, hazard: int, proof_class: int) -> bool:
    return bool(bit(checker, 2 * hazard + proof_class))


def hamming(left: int, right: int) -> int:
    return (left ^ right).bit_count()


def transition_allowed(
    *,
    behavior: int,
    checker: int,
    next_behavior: int,
    next_checker: int,
    width: int,
    radius: int,
    rule: str,
    root_checker: int = ROOT_CHECKER,
) -> bool:
    if rule not in RULES:
        raise ValueError(f"unknown rule: {rule}")
    if width < 1 or radius < 0:
        return False
    if not 0 <= checker < CHECKER_COUNT or not 0 <= next_checker < CHECKER_COUNT:
        return False
    if not 0 <= behavior < (1 << width) or not 0 <= next_behavior < (1 << width):
        return False
    if rule == "root_refinement" and not 0 <= root_checker < CHECKER_COUNT:
        return False
    if (behavior ^ next_behavior).bit_count() != 1:
        return False
    if hamming(checker, next_checker) > radius:
        return False
    hazard = bit(next_behavior, 0)
    for proof_class in (0, 1):
        present = checker_accepts(checker, hazard, proof_class)
        if rule == "self_endorsement" and present:
            return True
        if rule == "pairwise_agreement" and present and checker_accepts(
            next_checker, hazard, proof_class
        ):
            return True
        if rule == "root_refinement" and present and (next_checker & ~root_checker) == 0:
            return True
    return False


def transition_truth_table_digest(root_checker: int = ROOT_CHECKER) -> dict[str, Any]:
    """Hash the complete rooted transition relation on the two-bit template.

    Width two contains the hazard coordinate and one representative
    nonhazard coordinate. Every four-bit checker pair, behavior, one-bit edge,
    and distinct Hamming-radius regime is included. Radii above four add no
    transitions in the frozen checker grammar.
    """

    digest = hashlib.sha256()
    digest.update(b"ASMP5-root-refinement-transition-truth-table-v1\n")
    row_count = 0
    allowed_count = 0
    for radius in INDUCTIVE_RADII:
        for behavior in range(1 << TEMPLATE_WIDTH):
            for checker in range(CHECKER_COUNT):
                for coordinate in range(TEMPLATE_WIDTH):
                    next_behavior = behavior ^ (1 << coordinate)
                    for next_checker in range(CHECKER_COUNT):
                        allowed = transition_allowed(
                            behavior=behavior,
                            checker=checker,
                            next_behavior=next_behavior,
                            next_checker=next_checker,
                            width=TEMPLATE_WIDTH,
                            radius=radius,
                            rule="root_refinement",
                            root_checker=root_checker,
                        )
                        row = (
                            f"{radius},{behavior},{checker},{next_behavior},"
                            f"{next_checker},{int(allowed)}\n"
                        )
                        digest.update(row.encode("ascii"))
                        row_count += 1
                        allowed_count += int(allowed)
    return {
        "schema": "root_refinement_transition_truth_table_v1",
        "template_width": TEMPLATE_WIDTH,
        "checker_count": CHECKER_COUNT,
        "radii": list(INDUCTIVE_RADII),
        "row_count": row_count,
        "allowed_count": allowed_count,
        "sha256": digest.hexdigest(),
    }


def rooted_one_step_closure(radius: int, root_checker: int = ROOT_CHECKER) -> dict[str, Any]:
    """Exhaust the inductive safety step using the primary transition relation."""

    if radius < 0:
        raise ValueError("radius must be nonnegative")
    violations: list[dict[str, int]] = []
    checked_edges = 0
    accepted_edges = 0
    for behavior in range(1 << TEMPLATE_WIDTH):
        if bit(behavior, 0):
            continue
        for checker in range(CHECKER_COUNT):
            if checker & ~root_checker:
                continue
            for coordinate in range(TEMPLATE_WIDTH):
                next_behavior = behavior ^ (1 << coordinate)
                for next_checker in range(CHECKER_COUNT):
                    checked_edges += 1
                    allowed = transition_allowed(
                        behavior=behavior,
                        checker=checker,
                        next_behavior=next_behavior,
                        next_checker=next_checker,
                        width=TEMPLATE_WIDTH,
                        radius=radius,
                        rule="root_refinement",
                        root_checker=root_checker,
                    )
                    if not allowed:
                        continue
                    accepted_edges += 1
                    if bit(next_behavior, 0) or next_checker & ~root_checker:
                        violations.append(
                            {
                                "behavior": behavior,
                                "checker": checker,
                                "next_behavior": next_behavior,
                                "next_checker": next_checker,
                            }
                        )
    base_case = not (root_checker & ~ROOT_CHECKER) and all(
        not checker_accepts(root_checker, 1, proof_class) for proof_class in (0, 1)
    )
    return {
        "radius": radius,
        "base_case": base_case,
        "checked_edges": checked_edges,
        "accepted_edges": accepted_edges,
        "violations": violations,
        "pass": base_case and not violations,
    }


def rooted_induction_certificate(root_checker: int = ROOT_CHECKER) -> dict[str, Any]:
    closures = [rooted_one_step_closure(radius, root_checker) for radius in INDUCTIVE_RADII]
    return {
        "pass": all(record["pass"] for record in closures),
        "radii_complete": "radii_0_through_4_cover_all_four_bit_checker_distances",
        "closures": closures,
        "transition_truth_table": transition_truth_table_digest(root_checker),
    }


def nonhazard_permutation_invariance(root_checker: int = ROOT_CHECKER) -> dict[str, Any]:
    """Swap the two nonhazard coordinates and compare every rooted edge."""

    width = 3

    def swap_nonhazard(value: int) -> int:
        hazard = value & 1
        bit_one = (value >> 1) & 1
        bit_two = (value >> 2) & 1
        return hazard | (bit_one << 2) | (bit_two << 1)

    failures: list[dict[str, int]] = []
    checked_edges = 0
    for radius in INDUCTIVE_RADII:
        for behavior in range(1 << width):
            for checker in range(CHECKER_COUNT):
                for coordinate in range(width):
                    next_behavior = behavior ^ (1 << coordinate)
                    for next_checker in range(CHECKER_COUNT):
                        original = transition_allowed(
                            behavior=behavior,
                            checker=checker,
                            next_behavior=next_behavior,
                            next_checker=next_checker,
                            width=width,
                            radius=radius,
                            rule="root_refinement",
                            root_checker=root_checker,
                        )
                        permuted = transition_allowed(
                            behavior=swap_nonhazard(behavior),
                            checker=checker,
                            next_behavior=swap_nonhazard(next_behavior),
                            next_checker=next_checker,
                            width=width,
                            radius=radius,
                            rule="root_refinement",
                            root_checker=root_checker,
                        )
                        checked_edges += 1
                        if original != permuted:
                            failures.append(
                                {
                                    "radius": radius,
                                    "behavior": behavior,
                                    "checker": checker,
                                    "coordinate": coordinate,
                                    "next_checker": next_checker,
                                }
                            )
    return {"pass": not failures, "checked_edges": checked_edges, "failures": failures}


def unrooted_witness(width: int, radius: int, rule: str) -> list[dict[str, int]] | None:
    """Return the parametric two-step drift witness when its premises hold."""

    if width < 2 or radius < 1 or rule not in {"self_endorsement", "pairwise_agreement"}:
        return None
    permissive = ROOT_CHECKER | (1 << 2)
    path = [
        {
            "from_behavior": 0,
            "from_checker": ROOT_CHECKER,
            "to_behavior": 1 << 1,
            "to_checker": permissive,
        },
        {
            "from_behavior": 1 << 1,
            "from_checker": permissive,
            "to_behavior": (1 << 1) | 1,
            "to_checker": permissive,
        },
    ]
    assert all(
        transition_allowed(
            behavior=step["from_behavior"],
            checker=step["from_checker"],
            next_behavior=step["to_behavior"],
            next_checker=step["to_checker"],
            width=width,
            radius=radius,
            rule=rule,
        )
        for step in path
    )
    return path


def rooted_liveness_cycle(width: int, radius: int) -> list[dict[str, int]] | None:
    if width < 2 or radius < 0:
        return None
    cycle = [
        {
            "from_behavior": 0,
            "from_checker": ROOT_CHECKER,
            "to_behavior": 1 << 1,
            "to_checker": ROOT_CHECKER,
        },
        {
            "from_behavior": 1 << 1,
            "from_checker": ROOT_CHECKER,
            "to_behavior": 0,
            "to_checker": ROOT_CHECKER,
        },
    ]
    assert all(
        transition_allowed(
            behavior=step["from_behavior"],
            checker=step["from_checker"],
            next_behavior=step["to_behavior"],
            next_checker=step["to_checker"],
            width=width,
            radius=radius,
            rule="root_refinement",
        )
        for step in cycle
    )
    return cycle


def theorem_cell(width: int, radius: int, rule: str) -> dict[str, Any]:
    if width < 1 or radius < 0:
        raise ValueError("width must be positive and radius nonnegative")
    if rule == "root_refinement":
        closure = rooted_one_step_closure(radius)
        liveness_cycle = rooted_liveness_cycle(width, radius)
        return {
            "width": width,
            "radius": radius,
            "rule": rule,
            "unsafe_depth": None,
            "all_depth_safety": closure["pass"],
            "arbitrary_time_liveness": width >= 2 and liveness_cycle is not None,
            "certificate": {
                "base": "initial_checker_subset_of_root",
                "step": "accepted_successor_checker_subset_of_root",
                "consequence": "root_subsets_reject_both_hazard_proof_classes",
                "one_step_closure": closure,
            },
            "liveness_cycle": liveness_cycle,
        }
    witness = unrooted_witness(width, radius, rule)
    return {
        "width": width,
        "radius": radius,
        "rule": rule,
        "unsafe_depth": 2 if witness is not None else None,
        "all_depth_safety": witness is None,
        "arbitrary_time_liveness": None,
        "witness": witness,
    }


def robustness_probes() -> dict[str, dict[str, Any]]:
    induction = rooted_induction_certificate()
    permutation = nonhazard_permutation_invariance()
    mutated_root = ROOT_CHECKER | (1 << 2)
    sensitivity_live = transition_allowed(
        behavior=0,
        checker=mutated_root,
        next_behavior=1,
        next_checker=mutated_root,
        width=2,
        radius=0,
        rule="root_refinement",
        root_checker=mutated_root,
    )
    return {
        "invariance": {
            "pass": permutation["pass"],
            "probe": "permute_representative_nonhazard_coordinates",
            "checked_edges": permutation["checked_edges"],
        },
        "sensitivity": {
            "pass": sensitivity_live,
            "probe": "root_hazard_acceptance_mutation_yields_depth_one_failure",
        },
        "monotonicity": {
            "pass": induction["pass"],
            "probe": "all_horizons_and_checker_radii",
            "radii": list(INDUCTIVE_RADII),
        },
        "anti_gaming": {
            "pass": unrooted_witness(6, 1, "self_endorsement") is not None
            and unrooted_witness(6, 1, "pairwise_agreement") is not None,
            "probe": "matched_unrooted_failure_remains_live",
        },
        "clean_control": {
            "pass": rooted_liveness_cycle(6, 1) is not None,
            "probe": "safe_certificate_is_not_deadlock",
        },
    }


def compile_result(protocol: dict[str, Any]) -> dict[str, Any]:
    replay = protocol["independent_replay"]
    cells = [
        theorem_cell(width, radius, rule)
        for width in replay["widths"]
        for radius in replay["radii"]
        for rule in protocol["rules"]
    ]
    probes = robustness_probes()
    induction = rooted_induction_certificate()
    closure_registration = protocol.get("inductive_closure")
    expected_closure_registration = {
        "checker_domain": [0, CHECKER_COUNT - 1],
        "radii": list(INDUCTIVE_RADII),
        "template_width": TEMPLATE_WIDTH,
        "transition_digest_schema": "root_refinement_transition_truth_table_v1",
    }
    gates = {
        "G0_root_table": ROOT_CHECKER == int(protocol["root_checker"])
        and closure_registration == expected_closure_registration,
        "G1_inductive_safety": all(
            cell["all_depth_safety"] for cell in cells if cell["rule"] == "root_refinement"
        )
        and induction["pass"],
        "G2_arbitrary_time_liveness": all(
            cell["arbitrary_time_liveness"]
            for cell in cells
            if cell["rule"] == "root_refinement" and cell["width"] >= 2
        ),
        "G3_unrooted_separation": all(
            cell["unsafe_depth"] == 2
            for cell in cells
            if cell["rule"] != "root_refinement" and cell["radius"] >= 1
        ),
        "G4_metric_robustness": all(record["pass"] for record in probes.values()),
    }
    passed = all(gates.values())
    return {
        "schema_version": "asmp5_inductive_root_result_v0_3",
        "protocol_id": protocol["protocol_id"],
        "transition_relation": induction["transition_truth_table"],
        "induction_certificate": induction,
        "metric_robustness": probes,
        "task_result": "all_depth_rooted_safety_with_arbitrary_time_liveness" if passed else "not_established",
        "measurement_reliability": "pending_independent_replay" if passed else "failed",
        "claim_support": "bounded_exact_grammar_only" if passed else "none",
        "operational_decision": "run_independent_replay" if passed else "repair",
        "gates": gates,
        "cells": cells,
        "claim_boundary": protocol["claim_boundary"],
    }


def load_protocol(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
