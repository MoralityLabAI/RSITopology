"""Exact bounded verifier-drift census for ASMP-5."""

from __future__ import annotations

import argparse
import hashlib
import inspect
import itertools
import json
import platform
import subprocess
import time
import tracemalloc
from collections import deque
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()
State = tuple[int, int, int]
Edge = tuple[int, int, int]


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_once(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"refusing to overwrite non-identical artifact: {path}")
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def git(*args: str, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=REPO_ROOT, check=True, capture_output=True, text=text)


def bind_committed_inputs(paths: Sequence[Path]) -> dict[str, Any]:
    commit = git("rev-parse", "HEAD").stdout.strip()
    bindings = {}
    for path in paths:
        relative = path.resolve().relative_to(REPO_ROOT).as_posix()
        if git("status", "--porcelain", "--", relative).stdout.strip():
            raise ValueError(f"sealed input dirty or untracked: {relative}")
        payload = path.read_bytes()
        if git("show", f"HEAD:{relative}", text=False).stdout != payload:
            raise ValueError(f"sealed input differs from HEAD: {relative}")
        bindings[relative] = {
            "sha256": hashlib.sha256(payload).hexdigest(),
            "git_blob": git("rev-parse", f"HEAD:{relative}").stdout.strip(),
        }
    diff_hash = hashlib.sha256(git("diff", "--binary", "HEAD", "--", text=False).stdout).hexdigest()
    if diff_hash != EMPTY_SHA256:
        raise ValueError("tracked diff nonempty at run start")
    return {"commit": commit, "tracked_diff_sha256": diff_hash, "sealed_inputs": bindings}


def bit(mask: int, index: int) -> int:
    return (mask >> index) & 1


def checker_accepts(checker: int, hazard: int, proof_class: int) -> bool:
    return bool(bit(checker, 2 * hazard + proof_class))


def checker_neighbors(checker: int, radius: int) -> tuple[int, ...]:
    return tuple(candidate for candidate in range(16) if (checker ^ candidate).bit_count() <= radius)


def candidate_edges(state: State, width: int, radius: int, proof_tokens: Sequence[int]) -> Iterator[Edge]:
    """Generate the shared candidate universe; semantic labels are intentionally absent."""
    behavior, installed_checker, _progress = state
    for next_behavior in sorted(behavior ^ (1 << index) for index in range(width)):
        for next_checker in checker_neighbors(installed_checker, radius):
            for proof in proof_tokens:
                yield next_behavior, next_checker, proof


def edge_is_certified(
    state: State,
    edge: Edge,
    *,
    regime: str,
    rule: str,
    root_checker: int,
    proof_classes: dict[int, int],
) -> bool:
    _behavior, installed_checker, _progress = state
    next_behavior, next_checker, proof = edge
    active_checker = installed_checker if regime == "adaptive" else root_checker
    hazard = bit(next_behavior, 0)
    present_accepts = checker_accepts(active_checker, hazard, proof_classes[proof])
    if rule == "self_endorsement":
        return present_accepts
    if rule == "pairwise_agreement":
        return present_accepts and checker_accepts(next_checker, hazard, proof_classes[proof])
    if rule == "root_refinement":
        return present_accepts and (next_checker & ~root_checker) == 0
    raise ValueError(f"unknown rule: {rule}")


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
) -> tuple[list[tuple[State, ...]], list[dict[State, tuple[State, Edge]]]]:
    """Return exact layers and first parents. No semantic label argument exists."""
    initial = (0, root_checker, 0)
    layers: list[tuple[State, ...]] = [(initial,)]
    parents: list[dict[State, tuple[State, Edge]]] = [{}]
    for progress in range(horizon):
        next_parent: dict[State, tuple[State, Edge]] = {}
        for state in layers[-1]:
            for edge in candidate_edges(state, width, radius, proof_tokens):
                if edge_is_certified(
                    state,
                    edge,
                    regime=regime,
                    rule=rule,
                    root_checker=root_checker,
                    proof_classes=proof_classes,
                ):
                    candidate = (edge[0], edge[1], progress + 1)
                    next_parent.setdefault(candidate, (state, edge))
        layers.append(tuple(sorted(next_parent)))
        parents.append(next_parent)
    return layers, parents


def semantic_label_table(width: int) -> dict[int, bool]:
    return {behavior: bit(behavior, 0) == 0 for behavior in range(1 << width)}


def layer_digest(layers: Sequence[Sequence[State]]) -> str:
    digest = hashlib.sha256()
    for depth, layer in enumerate(layers):
        for state in layer:
            digest.update(f"{depth}:{state[0]}:{state[1]}:{state[2]}\n".encode())
    return digest.hexdigest()


def swap_behavior_coordinates(value: int, left: int, right: int) -> int:
    if bit(value, left) == bit(value, right):
        return value
    return value ^ (1 << left) ^ (1 << right)


def layers_invariant_under_coordinate_swap(
    layers: Sequence[Sequence[State]], left: int, right: int
) -> bool:
    for layer in layers:
        reframed = tuple(sorted((swap_behavior_coordinates(state[0], left, right), state[1], state[2]) for state in layer))
        if reframed != tuple(layer):
            return False
    return True


def reconstruct_path(
    target: State,
    depth: int,
    parents: Sequence[dict[State, tuple[State, Edge]]],
) -> list[dict[str, int]]:
    path: list[dict[str, int]] = []
    current = target
    for index in range(depth, 0, -1):
        previous, edge = parents[index][current]
        path.append({
            "from_behavior": previous[0],
            "from_checker": previous[1],
            "to_behavior": current[0],
            "to_checker": current[1],
            "proof": edge[2],
            "progress": current[2],
        })
        current = previous
    return list(reversed(path))


def analyze_layers(
    layers: Sequence[Sequence[State]],
    parents: Sequence[dict[State, tuple[State, Edge]]],
    labels: dict[int, bool],
) -> dict[str, Any]:
    unsafe_target = None
    unsafe_depth = None
    for depth, layer in enumerate(layers):
        candidates = [state for state in layer if not labels[state[0]]]
        if candidates:
            unsafe_depth = depth
            unsafe_target = min(candidates)
            break
    safe_behaviors = sorted({state[0] for layer in layers for state in layer if labels[state[0]]})
    max_safe_progress = max((state[2] for layer in layers for state in layer if labels[state[0]]), default=-1)
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
    labels: dict[int, bool],
) -> list[dict[str, int]] | None:
    initial: State = (0, root_checker, 0)

    def dfs(state: State, used: frozenset[int], path: list[dict[str, int]]) -> list[dict[str, int]] | None:
        if state[2] == horizon:
            return path
        for edge in candidate_edges(state, width, radius, proof_tokens):
            if edge[0] in used or not labels[edge[0]]:
                continue
            if not edge_is_certified(
                state, edge, regime=regime, rule=rule, root_checker=root_checker, proof_classes=proof_classes
            ):
                continue
            successor_state = (edge[0], edge[1], state[2] + 1)
            record = {
                "from_behavior": state[0], "from_checker": state[1],
                "to_behavior": edge[0], "to_checker": edge[1],
                "proof": edge[2], "progress": successor_state[2],
            }
            found = dfs(successor_state, used | {edge[0]}, [*path, record])
            if found is not None:
                return found
        return None

    return dfs(initial, frozenset({0}), [])


def universe_receipt(width: int, radius: int, horizon: int, proof_tokens: Sequence[int]) -> dict[str, Any]:
    edge_digest = hashlib.sha256()
    observable_digest = hashlib.sha256()
    count = 0
    for progress in range(horizon):
        for behavior in range(1 << width):
            for checker in range(16):
                state = (behavior, checker, progress)
                for edge in candidate_edges(state, width, radius, proof_tokens):
                    edge_digest.update(f"{width}|{radius}|{progress}|{behavior}|{checker}|{edge[0]}|{edge[1]}|{edge[2]}\n".encode())
                    observable_digest.update(f"{bit(edge[0], 0)}|{edge[2]}|{checker}|{edge[1]}\n".encode())
                    count += 1
    labels_payload = canonical_json(semantic_label_table(width)).encode()
    return {
        "width": width,
        "radius": radius,
        "candidate_edge_count": count,
        "candidate_edge_sha256": edge_digest.hexdigest(),
        "observable_tuple_sha256": observable_digest.hexdigest(),
        "semantic_label_table_sha256": hashlib.sha256(labels_payload).hexdigest(),
    }


def renamed_proof_classes(protocol: dict[str, Any]) -> tuple[tuple[int, ...], dict[int, int]]:
    rename = {int(old): int(new) for old, new in protocol["controls"]["proof_token_renaming"]["old_to_new"].items()}
    old_classes = {int(key): int(value) for key, value in protocol["proof_classes"].items()}
    new_tokens = tuple(sorted(rename.values()))
    new_classes = {rename[old]: old_classes[old] for old in rename}
    return new_tokens, new_classes


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
    internal: dict[tuple[int, int, str, str], tuple[list[tuple[State, ...]], list[dict[State, tuple[State, Edge]]]]] = {}
    universes = [universe_receipt(width, radius, horizon, tokens) for width in widths for radius in radii]
    for width, radius, rule, regime in itertools.product(widths, radii, rules, regimes):
        layers, parents = certified_reachability(
            width=width, radius=radius, horizon=horizon, regime=regime, rule=rule,
            root_checker=root, proof_tokens=tokens, proof_classes=classes,
        )
        internal[(width, radius, rule, regime)] = (layers, parents)
        labels = semantic_label_table(width)
        analysis = analyze_layers(layers, parents, labels)
        capacity_available = sum(labels.values()) >= protocol["liveness"]["required_distinct_behavior_vectors"]
        cells.append({
            "width": width, "radius": radius, "rule": rule, "regime": regime,
            "capacity_status": "available" if capacity_available else "unavailable_insufficient_safe_behaviors",
            **analysis,
        })
    lookup = {(c["width"], c["radius"], c["rule"], c["regime"]): c for c in cells}
    separating = []
    for radius in (1, 2):
        for rule in ("self_endorsement", "pairwise_agreement"):
            adaptive = lookup[(6, radius, rule, "adaptive")]
            rooted = lookup[(6, radius, rule, "frozen_root")]
            if adaptive["unsafe_depth"] is not None and adaptive["unsafe_depth"] <= 4 and rooted["unsafe_depth"] is None:
                separating.append({"radius": radius, "rule": rule, "adaptive_depth": adaptive["unsafe_depth"]})
    refinement = lookup[(6, 1, "root_refinement", "adaptive")]
    liveness_path = find_distinct_safe_chain(
        width=6, radius=1, horizon=horizon, regime="adaptive", rule="root_refinement",
        root_checker=root, proof_tokens=tokens, proof_classes=classes, labels=semantic_label_table(6),
    )
    immutable_equal = all(
        lookup[(width, 0, rule, "adaptive")]["reachability_digest"] == lookup[(width, 0, rule, "frozen_root")]["reachability_digest"]
        for width in widths for rule in rules
    )
    renamed_tokens, renamed_classes = renamed_proof_classes(protocol)
    renamed_layers, _ = certified_reachability(
        width=6, radius=1, horizon=horizon, regime="adaptive", rule="self_endorsement",
        root_checker=root, proof_tokens=renamed_tokens, proof_classes=renamed_classes,
    )
    proof_rename_equal = layer_digest(renamed_layers) == lookup[(6, 1, "self_endorsement", "adaptive")]["reachability_digest"]
    permissive_layers, permissive_parents = certified_reachability(
        width=6, radius=0, horizon=1, regime="adaptive", rule="self_endorsement",
        root_checker=15, proof_tokens=tokens, proof_classes=classes,
    )
    permissive = analyze_layers(permissive_layers, permissive_parents, semantic_label_table(6))
    reachability_signature = inspect.signature(certified_reachability)
    labels_absent = "labels" not in reachability_signature.parameters and "semantic" not in reachability_signature.parameters
    original_layers, original_parents = internal[(6, 1, "self_endorsement", "adaptive")]
    original_analysis = analyze_layers(original_layers, original_parents, semantic_label_table(6))
    permuted_labels = {behavior: semantic_label_table(6)[behavior ^ 1] for behavior in range(1 << 6)}
    permuted_analysis = analyze_layers(original_layers, original_parents, permuted_labels)
    label_permutation_reachability = original_analysis["reachability_digest"] == permuted_analysis["reachability_digest"]
    label_permutation_changes_analysis = original_analysis["unsafe_depth"] != permuted_analysis["unsafe_depth"]
    swap_left, swap_right = map(int, protocol["controls"]["behavior_coordinate_swap"])
    state_rename_equal = all(
        layers_invariant_under_coordinate_swap(layers, swap_left, swap_right)
        for layers, _parents in internal.values()
    )
    n4_capacity_correct = all(cell["capacity_status"] == "unavailable_insufficient_safe_behaviors" for cell in cells if cell["width"] == 4)
    gates = {
        "G0_registration_binding": {"pass": True},
        "G1_shared_candidate_universe": {
            "pass": len(universes) == len(widths) * len(radii) and all(item["candidate_edge_count"] > 0 for item in universes),
            "universe_receipts": universes,
        },
        "G2_semantic_label_isolation": {
            "pass": labels_absent and label_permutation_reachability and label_permutation_changes_analysis,
            "reachability_signature_has_no_labels": labels_absent,
            "label_permutation_preserves_reachability": label_permutation_reachability,
            "label_permutation_changes_analysis_only": label_permutation_changes_analysis,
        },
        "G3_adaptive_root_separation": {"pass": bool(separating), "separating_cells": separating},
        "G4_root_refinement_and_liveness": {
            "pass": refinement["unsafe_depth"] is None and liveness_path is not None and len({0, *[step["to_behavior"] for step in liveness_path or []]}) == 9,
            "root_refinement_unsafe_depth": refinement["unsafe_depth"],
            "safe_chain": liveness_path,
        },
        "G5_controls": {
            "pass": immutable_equal and proof_rename_equal and state_rename_equal and permissive["unsafe_depth"] == 1 and n4_capacity_correct,
            "immutable_radius_zero_equivalence": immutable_equal,
            "proof_token_renaming_invariance": proof_rename_equal,
            "behavior_state_renaming_invariance": state_rename_equal,
            "permissive_checker_unsafe_depth": permissive["unsafe_depth"],
            "width_four_capacity_unavailable": n4_capacity_correct,
        },
        "G6_census_completeness": {
            "pass": len(cells) == int(protocol["registered_cell_count"]),
            "cell_count": len(cells),
        },
    }
    passed = all(record["pass"] for record in gates.values())
    return {
        "schema_version": "asmp5_verifier_drift_result_v0_1",
        "protocol_id": protocol["protocol_id"],
        "instrument_status": "valid" if passed else "invalid",
        "evidence_label": protocol["evidence_label_on_pass"] if passed else "not_established",
        "runner_gate_pass": passed,
        "stage_decision": "pending_independent_verification" if passed else "invalid_or_failed_stop_sequence",
        "gates": gates,
        "cells": cells,
        "claim_boundary": protocol["prohibited_claims"],
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    protocol_path = args.protocol.resolve()
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    if protocol.get("schema_version") != "asmp5_verifier_drift_protocol_v0_1":
        raise ValueError("unexpected protocol schema")
    sealed = (protocol_path, HERE / "CLAIM_PACKET.md", HERE / "README.md", Path(__file__).resolve(), HERE / "verify_result.py", HERE / "test_verifier_drift.py")
    output_dir = args.output_dir.resolve()
    if any(output_dir == path or output_dir in path.parents for path in sealed):
        raise ValueError("output directory aliases a sealed input")
    result_path, receipt_path = output_dir / "result_v0_1.json", output_dir / "receipt_v0_1.json"
    if result_path.exists() or receipt_path.exists():
        raise FileExistsError("registered outputs already exist")
    registration = bind_committed_inputs(sealed)
    tracemalloc.start()
    started = time.perf_counter()
    result = run_registered(protocol)
    elapsed = time.perf_counter() - started
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    ceiling = protocol["resource_ceiling"]
    resource_pass = elapsed <= ceiling["wall_seconds"] and peak <= ceiling["python_peak_bytes"]
    result["resource_receipt"] = {"elapsed_seconds": elapsed, "python_tracemalloc_peak_bytes": peak, "pass": resource_pass, "wall_ceiling_seconds": ceiling["wall_seconds"], "python_peak_ceiling_bytes": ceiling["python_peak_bytes"]}
    if not resource_pass:
        result["instrument_status"] = "unavailable"
        result["runner_gate_pass"] = False
        result["stage_decision"] = ceiling["on_exceed"]
    result["registration"] = registration
    result["protocol_sha256"] = sha256_file(protocol_path)
    payload = canonical_json(result).encode()
    write_once(result_path, payload)
    receipt = {
        "schema_version": "asmp5_verifier_drift_receipt_v0_1",
        "git_commit_at_run": registration["commit"],
        "git_tracked_diff_sha256_at_run": registration["tracked_diff_sha256"],
        "protocol_sha256": sha256_file(protocol_path),
        "claim_packet_sha256": sha256_file(HERE / "CLAIM_PACKET.md"),
        "runner_sha256": sha256_file(Path(__file__).resolve()),
        "verifier_sha256": sha256_file(HERE / "verify_result.py"),
        "tests_sha256": sha256_file(HERE / "test_verifier_drift.py"),
        "result_sha256": hashlib.sha256(payload).hexdigest(),
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
    }
    write_once(receipt_path, canonical_json(receipt).encode())
    print(canonical_json({"instrument_status": result["instrument_status"], "runner_gate_pass": result["runner_gate_pass"], "stage_decision": result["stage_decision"], "elapsed_seconds": elapsed, "cells": len(result["cells"]), "result": str(result_path)}), end="")
    return 0 if result["runner_gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
