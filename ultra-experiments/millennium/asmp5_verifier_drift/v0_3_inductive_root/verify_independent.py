"""Import-independent graph replay for ASMP-5 v0.3."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
CHECKER_COUNT = 16
INDUCTIVE_RADII = (0, 1, 2, 3, 4)
TEMPLATE_WIDTH = 2
SOURCE_FILES = ("inductive_root.py", "run.py", "verify_independent.py")


def accepts(checker: int, hazard: int, proof_class: int) -> bool:
    return bool((checker >> (2 * hazard + proof_class)) & 1)


def allowed(state, successor, width: int, radius: int, rule: str, root: int) -> bool:
    behavior, checker = state
    next_behavior, next_checker = successor
    if width < 1 or radius < 0:
        return False
    if not 0 <= checker < CHECKER_COUNT or not 0 <= next_checker < CHECKER_COUNT:
        return False
    if not 0 <= behavior < (1 << width) or not 0 <= next_behavior < (1 << width):
        return False
    if rule == "root_refinement" and not 0 <= root < CHECKER_COUNT:
        return False
    if (behavior ^ next_behavior).bit_count() != 1:
        return False
    if (checker ^ next_checker).bit_count() > radius:
        return False
    hazard = next_behavior & 1
    for proof_class in (0, 1):
        current_ok = accepts(checker, hazard, proof_class)
        if rule == "self_endorsement" and current_ok:
            return True
        if rule == "pairwise_agreement" and current_ok and accepts(next_checker, hazard, proof_class):
            return True
        if rule == "root_refinement" and current_ok and not (next_checker & ~root):
            return True
    return False


def transition_truth_table_digest(root: int) -> dict[str, Any]:
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
                        is_allowed = allowed(
                            (behavior, checker),
                            (next_behavior, next_checker),
                            TEMPLATE_WIDTH,
                            radius,
                            "root_refinement",
                            root,
                        )
                        row = (
                            f"{radius},{behavior},{checker},{next_behavior},"
                            f"{next_checker},{int(is_allowed)}\n"
                        )
                        digest.update(row.encode("ascii"))
                        row_count += 1
                        allowed_count += int(is_allowed)
    return {
        "schema": "root_refinement_transition_truth_table_v1",
        "template_width": TEMPLATE_WIDTH,
        "checker_count": CHECKER_COUNT,
        "radii": list(INDUCTIVE_RADII),
        "row_count": row_count,
        "allowed_count": allowed_count,
        "sha256": digest.hexdigest(),
    }


def inductive_closure(root: int) -> dict[str, Any]:
    violations = []
    checked_edges = 0
    for radius in INDUCTIVE_RADII:
        for behavior in range(1 << TEMPLATE_WIDTH):
            if behavior & 1:
                continue
            for checker in range(CHECKER_COUNT):
                if checker & ~root:
                    continue
                for coordinate in range(TEMPLATE_WIDTH):
                    next_behavior = behavior ^ (1 << coordinate)
                    for next_checker in range(CHECKER_COUNT):
                        checked_edges += 1
                        if not allowed(
                            (behavior, checker),
                            (next_behavior, next_checker),
                            TEMPLATE_WIDTH,
                            radius,
                            "root_refinement",
                            root,
                        ):
                            continue
                        if next_behavior & 1 or next_checker & ~root:
                            violations.append(
                                {
                                    "radius": radius,
                                    "behavior": behavior,
                                    "checker": checker,
                                    "next_behavior": next_behavior,
                                    "next_checker": next_checker,
                                }
                            )
    base_case = 0 <= root < CHECKER_COUNT and all(
        not accepts(root, 1, proof_class) for proof_class in (0, 1)
    )
    return {
        "pass": base_case and not violations,
        "base_case": base_case,
        "checked_edges": checked_edges,
        "violations": violations,
    }


def replay(width: int, radius: int, horizon: int, rule: str, root: int) -> dict[str, Any]:
    layer = {(0, root)}
    unsafe_depth = None
    subset_failures = 0
    for depth in range(1, horizon + 1):
        following = set()
        for behavior, checker in layer:
            for coordinate in range(width):
                next_behavior = behavior ^ (1 << coordinate)
                for next_checker in range(16):
                    successor = (next_behavior, next_checker)
                    if allowed((behavior, checker), successor, width, radius, rule, root):
                        following.add(successor)
                        if rule == "root_refinement" and next_checker & ~root:
                            subset_failures += 1
        layer = following
        if unsafe_depth is None and any(behavior & 1 for behavior, _checker in layer):
            unsafe_depth = depth
    return {
        "unsafe_depth": unsafe_depth,
        "root_subset_failures": subset_failures,
        "final_layer_size": len(layer),
    }


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_bindings() -> dict[str, str]:
    return {name: sha256_file(HERE / name) for name in SOURCE_FILES}


def verify_payload(protocol: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    cells = {(row["width"], row["radius"], row["rule"]): row for row in result["cells"]}
    mismatches = []
    replay_rows = []
    for width in protocol["independent_replay"]["widths"]:
        for radius in protocol["independent_replay"]["radii"]:
            for rule in protocol["rules"]:
                observed = replay(width, radius, protocol["independent_replay"]["horizon"], rule, protocol["root_checker"])
                symbolic = cells[(width, radius, rule)]
                expected = symbolic["unsafe_depth"]
                if observed["unsafe_depth"] != expected or observed["root_subset_failures"]:
                    mismatches.append(
                        {
                            "width": width,
                            "radius": radius,
                            "rule": rule,
                            "expected": expected,
                            "observed": observed,
                        }
                    )
                replay_rows.append({"width": width, "radius": radius, "rule": rule, **observed})
    cycle_live = allowed((0, 3), (2, 3), 2, 0, "root_refinement", 3) and allowed(
        (2, 3), (0, 3), 2, 0, "root_refinement", 3
    )
    expected_relation = transition_truth_table_digest(protocol["root_checker"])
    transition_digest_matches = result.get("transition_relation") == expected_relation
    protocol_closure_matches = protocol.get("inductive_closure") == {
        "checker_domain": [0, CHECKER_COUNT - 1],
        "radii": list(INDUCTIVE_RADII),
        "template_width": TEMPLATE_WIDTH,
        "transition_digest_schema": "root_refinement_transition_truth_table_v1",
    }
    closure = inductive_closure(protocol["root_checker"])
    passed = (
        not mismatches
        and cycle_live
        and transition_digest_matches
        and protocol_closure_matches
        and closure["pass"]
        and all(result["gates"].values())
    )
    return {
        "schema_version": "asmp5_inductive_root_verification_v0_3",
        "pass": passed,
        "mismatches": mismatches,
        "replayed_cells": len(replay_rows),
        "safe_cycle_replayed": cycle_live,
        "transition_digest_matches": transition_digest_matches,
        "protocol_closure_matches": protocol_closure_matches,
        "transition_relation": expected_relation,
        "inductive_closure": closure,
        "measurement_reliability": (
            "independent_graph_replay_closure_and_digest_passed" if passed else "failed"
        ),
        "claim_support": result["claim_support"] if passed else "none",
        "operational_decision": "close_toy_horizon_gap" if passed else "repair",
    }


def verify() -> dict[str, Any]:
    protocol_path = HERE / "protocol_v0_3.json"
    result_path = HERE / "artifacts_v0_3" / "result_v0_3.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    verification = verify_payload(protocol, result)
    verification["bindings"] = {
        "protocol_v0_3.json": sha256_file(protocol_path),
        "result_v0_3.json": sha256_file(result_path),
    }
    verification["source_bindings"] = source_bindings()
    return verification


def build_synthesis(
    protocol_path: Path,
    result_path: Path,
    verification_path: Path,
) -> dict[str, Any]:
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    verification = json.loads(verification_path.read_text(encoding="utf-8"))
    bindings = {
        "protocol_v0_3.json": sha256_file(protocol_path),
        "result_v0_3.json": sha256_file(result_path),
        "verification_v0_3.json": sha256_file(verification_path),
    }
    binding_match = verification.get("bindings") == {
        key: bindings[key] for key in ("protocol_v0_3.json", "result_v0_3.json")
    } and verification.get("source_bindings") == source_bindings()
    passed = bool(verification.get("pass")) and binding_match
    return {
        "schema_version": "asmp5_inductive_root_synthesis_receipt_v0_3",
        "pass": passed,
        "bindings": bindings,
        "source_bindings": source_bindings(),
        "binding_match": binding_match,
        "conclusion_layers": {
            "task_result": result["task_result"] if passed else "not_established",
            "measurement_reliability": verification["measurement_reliability"],
            "claim_support": verification["claim_support"] if passed else "none",
            "operational_decision": verification["operational_decision"] if passed else "repair",
            "metric_robustness": result["metric_robustness"],
        },
        "claim_boundary": protocol["claim_boundary"],
    }


def main() -> None:
    verification = verify()
    output = HERE / "artifacts_v0_3" / "verification_v0_3.json"
    output.write_text(canonical_json(verification), encoding="utf-8", newline="\n")
    synthesis_output = HERE / "artifacts_v0_3" / "synthesis_receipt_v0_3.json"
    synthesis = build_synthesis(
        HERE / "protocol_v0_3.json",
        HERE / "artifacts_v0_3" / "result_v0_3.json",
        output,
    )
    synthesis_output.write_text(canonical_json(synthesis), encoding="utf-8", newline="\n")
    print(output)
    print(synthesis_output)
    if not verification["pass"] or not synthesis["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
