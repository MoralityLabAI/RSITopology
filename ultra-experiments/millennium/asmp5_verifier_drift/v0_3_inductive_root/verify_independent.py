"""Import-independent graph replay for ASMP-5 v0.3."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent


def accepts(checker: int, hazard: int, proof_class: int) -> bool:
    return bool((checker >> (2 * hazard + proof_class)) & 1)


def allowed(state, successor, width: int, radius: int, rule: str, root: int) -> bool:
    behavior, checker = state
    next_behavior, next_checker = successor
    if behavior >= (1 << width) or next_behavior >= (1 << width):
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


def verify() -> dict[str, Any]:
    protocol = json.loads((HERE / "protocol_v0_3.json").read_text(encoding="utf-8"))
    result = json.loads((HERE / "artifacts_v0_3" / "result_v0_3.json").read_text(encoding="utf-8"))
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
    passed = not mismatches and cycle_live and all(result["gates"].values())
    return {
        "schema_version": "asmp5_inductive_root_verification_v0_3",
        "pass": passed,
        "mismatches": mismatches,
        "replayed_cells": len(replay_rows),
        "safe_cycle_replayed": cycle_live,
        "measurement_reliability": "independent_graph_replay_passed" if passed else "failed",
        "claim_support": result["claim_support"] if passed else "none",
        "operational_decision": "close_toy_horizon_gap" if passed else "repair",
    }


def main() -> None:
    verification = verify()
    output = HERE / "artifacts_v0_3" / "verification_v0_3.json"
    output.write_text(canonical_json(verification), encoding="utf-8", newline="\n")
    print(output)
    if not verification["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
