"""Independent finite-state verifier for ASMP-5."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence


HERE = Path(__file__).resolve().parent
State = tuple[int, int, int]


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


def check_bit(mask: int, index: int) -> int:
    return (mask // (2 ** index)) % 2


def neighbor_checkers(checker: int, radius: int) -> list[int]:
    return [other for other in range(16) if bin(checker ^ other).count("1") <= radius]


def updates(state: State, width: int, radius: int, tokens: Sequence[int]) -> Iterator[tuple[int, int, int]]:
    behavior, checker, _ = state
    for coordinate in range(width):
        proposed = behavior ^ (1 << coordinate)
        for next_checker in neighbor_checkers(checker, radius):
            for token in tokens:
                yield proposed, next_checker, token


def accepted(state: State, edge: tuple[int, int, int], regime: str, rule: str, root: int, classes: dict[int, int]) -> bool:
    _, installed, _ = state
    proposed, next_checker, proof = edge
    active = installed if regime == "adaptive" else root
    index = 2 * check_bit(proposed, 0) + classes[proof]
    now = bool(check_bit(active, index))
    if rule == "self_endorsement":
        return now
    if rule == "pairwise_agreement":
        return now and bool(check_bit(next_checker, index))
    if rule == "root_refinement":
        return now and (next_checker & ~root) == 0
    raise AssertionError(rule)


def independent_layers(width: int, radius: int, horizon: int, regime: str, rule: str, root: int, tokens: Sequence[int], classes: dict[int, int]) -> list[tuple[State, ...]]:
    levels: list[tuple[State, ...]] = [((0, root, 0),)]
    for depth in range(horizon):
        future = {
            (edge[0], edge[1], depth + 1)
            for state in levels[-1]
            for edge in updates(state, width, radius, tokens)
            if accepted(state, edge, regime, rule, root, classes)
        }
        levels.append(tuple(sorted(future)))
    return levels


def digest_levels(levels: Sequence[Sequence[State]]) -> str:
    digest = hashlib.sha256()
    for depth, level in enumerate(levels):
        for state in level:
            digest.update(f"{depth}:{state[0]}:{state[1]}:{state[2]}\n".encode())
    return digest.hexdigest()


def swap_coordinates(value: int, left: int, right: int) -> int:
    return value if check_bit(value, left) == check_bit(value, right) else value ^ (1 << left) ^ (1 << right)


def swap_invariant(levels: Sequence[Sequence[State]], left: int, right: int) -> bool:
    return all(
        tuple(sorted((swap_coordinates(state[0], left, right), state[1], state[2]) for state in level)) == tuple(level)
        for level in levels
    )


def summarize(levels: Sequence[Sequence[State]]) -> tuple[int | None, int, int, list[int]]:
    unsafe = next((depth for depth, level in enumerate(levels) if any(check_bit(state[0], 0) for state in level)), None)
    safe_behaviors = {state[0] for level in levels for state in level if check_bit(state[0], 0) == 0}
    safe_progress = max((state[2] for level in levels for state in level if check_bit(state[0], 0) == 0), default=-1)
    return unsafe, len(safe_behaviors), safe_progress, [len(level) for level in levels]


def verify_path(path: list[dict[str, int]] | None, *, width: int, radius: int, regime: str, rule: str, root: int, classes: dict[int, int], require_safe: bool) -> bool:
    if path is None:
        return False
    state: State = (0, root, 0)
    seen = {0}
    for expected_progress, record in enumerate(path, 1):
        edge = (record["to_behavior"], record["to_checker"], record["proof"])
        if record["from_behavior"] != state[0] or record["from_checker"] != state[1] or record["progress"] != expected_progress:
            return False
        if (state[0] ^ edge[0]).bit_count() != 1 or (state[1] ^ edge[1]).bit_count() > radius:
            return False
        if not accepted(state, edge, regime, rule, root, classes):
            return False
        if require_safe and check_bit(edge[0], 0):
            return False
        if require_safe and edge[0] in seen:
            return False
        seen.add(edge[0])
        state = (edge[0], edge[1], expected_progress)
    return True


def universe_hashes(width: int, radius: int, horizon: int, tokens: Sequence[int]) -> tuple[int, str, str, str]:
    edge_hash = hashlib.sha256()
    observable_hash = hashlib.sha256()
    count = 0
    for progress in range(horizon):
        for behavior in range(1 << width):
            for checker in range(16):
                for edge in updates((behavior, checker, progress), width, radius, tokens):
                    edge_hash.update(f"{width}|{radius}|{progress}|{behavior}|{checker}|{edge[0]}|{edge[1]}|{edge[2]}\n".encode())
                    observable_hash.update(f"{check_bit(edge[0], 0)}|{edge[2]}|{checker}|{edge[1]}\n".encode())
                    count += 1
    label_payload = canonical_json({behavior: check_bit(behavior, 0) == 0 for behavior in range(1 << width)}).encode()
    return count, edge_hash.hexdigest(), observable_hash.hexdigest(), hashlib.sha256(label_payload).hexdigest()


def verify(result_path: Path, receipt_path: Path) -> dict[str, Any]:
    protocol = json.loads((HERE / "protocol_v0_1.json").read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {
        "result_hash_matches_receipt": sha256_file(result_path) == receipt.get("result_sha256"),
        "protocol_hash_matches_receipt": sha256_file(HERE / "protocol_v0_1.json") == receipt.get("protocol_sha256"),
        "claim_hash_matches_receipt": sha256_file(HERE / "CLAIM_PACKET.md") == receipt.get("claim_packet_sha256"),
        "verifier_hash_matches_receipt": sha256_file(Path(__file__).resolve()) == receipt.get("verifier_sha256"),
        "schema_exact": result.get("schema_version") == "asmp5_verifier_drift_result_v0_1",
        "runner_valid": result.get("instrument_status") == "valid" and result.get("runner_gate_pass") is True,
        "label_exact": result.get("evidence_label") == "exact_bounded_verifier_drift_counterexample",
    }
    horizon, root = int(protocol["horizon"]), int(protocol["root_checker"])
    tokens = tuple(map(int, protocol["proof_tokens"]))
    classes = {int(key): int(value) for key, value in protocol["proof_classes"].items()}
    expected_keys = set(itertools.product(map(int, protocol["behavior_widths"]), map(int, protocol["mutation_radii"]), protocol["certificate_rules"], protocol["regimes"]))
    cells = result.get("cells", [])
    by_key = {(c["width"], c["radius"], c["rule"], c["regime"]): c for c in cells}
    checks["cell_universe_exact"] = len(cells) == 36 and set(by_key) == expected_keys
    recomputation = checks["cell_universe_exact"]
    state_rename_ok = checks["cell_universe_exact"]
    swap_left, swap_right = map(int, protocol["controls"]["behavior_coordinate_swap"])
    if recomputation:
        for key, cell in by_key.items():
            width, radius, rule, regime = key
            levels = independent_layers(width, radius, horizon, regime, rule, root, tokens, classes)
            unsafe, safe_count, safe_progress, counts = summarize(levels)
            recomputation = recomputation and cell["unsafe_depth"] == unsafe
            recomputation = recomputation and cell["reachable_safe_behavior_count"] == safe_count
            recomputation = recomputation and cell["maximum_safe_progress"] == safe_progress
            recomputation = recomputation and cell["reachable_state_count_by_depth"] == counts
            recomputation = recomputation and cell["reachability_digest"] == digest_levels(levels)
            state_rename_ok = state_rename_ok and swap_invariant(levels, swap_left, swap_right)
            if cell["unsafe_path"] is not None:
                recomputation = recomputation and verify_path(cell["unsafe_path"], width=width, radius=radius, regime=regime, rule=rule, root=root, classes=classes, require_safe=False)
    checks["all_cells_independently_recomputed"] = recomputation
    checks["behavior_state_renaming_recomputed"] = state_rename_ok
    universes = result.get("gates", {}).get("G1_shared_candidate_universe", {}).get("universe_receipts", [])
    universe_ok = len(universes) == 6
    for record in universes:
        observed = universe_hashes(record["width"], record["radius"], horizon, tokens)
        universe_ok = universe_ok and observed == (record["candidate_edge_count"], record["candidate_edge_sha256"], record["observable_tuple_sha256"], record["semantic_label_table_sha256"])
    checks["candidate_universes_independently_hashed"] = universe_ok
    separating = []
    for radius in (1, 2):
        for rule in ("self_endorsement", "pairwise_agreement"):
            adaptive, frozen = by_key[(6, radius, rule, "adaptive")], by_key[(6, radius, rule, "frozen_root")]
            if adaptive["unsafe_depth"] is not None and adaptive["unsafe_depth"] <= 4 and frozen["unsafe_depth"] is None:
                separating.append((radius, rule))
    checks["primary_separation_recomputed"] = bool(separating)
    checks["radius_zero_arms_identical"] = all(
        by_key[(width, 0, rule, "adaptive")]["reachability_digest"] == by_key[(width, 0, rule, "frozen_root")]["reachability_digest"]
        for width in (4, 6) for rule in protocol["certificate_rules"]
    )
    refinement = by_key[(6, 1, "root_refinement", "adaptive")]
    safe_chain = result.get("gates", {}).get("G4_root_refinement_and_liveness", {}).get("safe_chain")
    checks["root_refinement_blocks_unsafe"] = refinement["unsafe_depth"] is None
    checks["nine_vector_safe_chain_replays"] = len(safe_chain or []) == 8 and verify_path(safe_chain, width=6, radius=1, regime="adaptive", rule="root_refinement", root=root, classes=classes, require_safe=True)
    checks["runner_gates_exact_and_pass"] = set(result.get("gates", {})) == {
        "G0_registration_binding", "G1_shared_candidate_universe", "G2_semantic_label_isolation",
        "G3_adaptive_root_separation", "G4_root_refinement_and_liveness", "G5_controls", "G6_census_completeness",
    } and all(gate.get("pass") is True for gate in result.get("gates", {}).values())
    checks["resource_ceiling_pass"] = result.get("resource_receipt", {}).get("pass") is True
    checks["registration_commit_agrees"] = result.get("registration", {}).get("commit") == receipt.get("git_commit_at_run")
    passed = all(checks.values())
    return {
        "schema_version": "asmp5_verifier_drift_verification_v0_1",
        "instrument_status": "valid" if passed else "invalid",
        "G7_independent_verification": {"pass": passed, "checks": checks},
        "stage_decision": "pass" if passed else "invalid_stop_sequence",
        "next_stage": "ASMP-3" if passed else None,
        "claim_boundary": "Independent verification of one exact bounded finite universe; no open-ended reflective-safety inference.",
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.result.is_file() or not args.receipt.is_file():
        raise FileNotFoundError("result and receipt required")
    if args.output.resolve() in {args.result.resolve(), args.receipt.resolve()}:
        raise ValueError("verification output aliases input")
    result = verify(args.result.resolve(), args.receipt.resolve())
    write_once(args.output.resolve(), canonical_json(result).encode())
    print(canonical_json(result), end="")
    return 0 if result["stage_decision"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
