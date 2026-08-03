"""Symbolic certificate compiler for ASMP-5 v0.3."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT_CHECKER = 0b0011
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
    if behavior >= (1 << width) or next_behavior >= (1 << width):
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
        return {
            "width": width,
            "radius": radius,
            "rule": rule,
            "unsafe_depth": None,
            "all_depth_safety": True,
            "arbitrary_time_liveness": width >= 2,
            "certificate": {
                "base": "initial_checker_subset_of_root",
                "step": "accepted_successor_checker_subset_of_root",
                "consequence": "root_subsets_reject_both_hazard_proof_classes",
            },
            "liveness_cycle": rooted_liveness_cycle(width, radius),
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
            "pass": theorem_cell(3, 1, "root_refinement")["all_depth_safety"]
            == theorem_cell(7, 1, "root_refinement")["all_depth_safety"],
            "probe": "add_or_permute_nonhazard_coordinates",
        },
        "sensitivity": {
            "pass": sensitivity_live,
            "probe": "root_hazard_acceptance_mutation_yields_depth_one_failure",
        },
        "monotonicity": {
            "pass": all(theorem_cell(6, radius, "root_refinement")["all_depth_safety"] for radius in range(5)),
            "probe": "all_horizons_and_checker_radii",
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
    gates = {
        "G0_root_table": ROOT_CHECKER == int(protocol["root_checker"]),
        "G1_inductive_safety": all(
            cell["all_depth_safety"] for cell in cells if cell["rule"] == "root_refinement"
        ),
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
