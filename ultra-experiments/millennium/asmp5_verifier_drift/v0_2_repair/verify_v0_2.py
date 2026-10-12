"""Independent replay verifier for ASMP-5 v0.2 artifacts."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any, Iterable, Sequence


HERE = Path(__file__).resolve().parent
State = tuple[int, int]


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bit(mask: int, index: int) -> int:
    return (mask // (2**index)) % 2


def neighbors(checker: int, radius: int) -> list[int]:
    return [other for other in range(16) if bin(checker ^ other).count("1") <= radius]


def proof_for(state: State, proposed: int, successor: int, regime: str, rule: str, root: int) -> int | None:
    active = state[1] if regime == "adaptive" else root
    hazard = bit(proposed, 0)
    for proof_class in (0, 1):
        present = bool(bit(active, 2 * hazard + proof_class))
        if rule == "self_endorsement" and present:
            return proof_class
        if rule == "pairwise_agreement" and present and bit(successor, 2 * hazard + proof_class):
            return proof_class
        if rule == "root_refinement" and present and (successor & ~root) == 0:
            return proof_class
    return None


def replay_layers(width: int, radius: int, horizon: int, regime: str, rule: str, root: int):
    levels: list[tuple[State, ...]] = [((0, root),)]
    for _depth in range(horizon):
        future = set()
        for state in levels[-1]:
            for coordinate in range(width):
                proposed = state[0] ^ (1 << coordinate)
                for successor in neighbors(state[1], radius):
                    if proof_for(state, proposed, successor, regime, rule, root) is not None:
                        future.add((proposed, successor))
        levels.append(tuple(sorted(future)))
    return levels


def digest(levels: Sequence[Sequence[State]]) -> str:
    value = hashlib.sha256()
    for depth, level in enumerate(levels):
        for behavior, checker in level:
            value.update(f"{depth}:{behavior}:{checker}:{depth}\n".encode())
    return value.hexdigest()


def summary(levels):
    unsafe = next((depth for depth, level in enumerate(levels) if any(bit(state[0], 0) for state in level)), None)
    safe = {state[0] for level in levels for state in level if bit(state[0], 0) == 0}
    progress = max((depth for depth, level in enumerate(levels) if any(bit(state[0], 0) == 0 for state in level)), default=-1)
    return unsafe, len(safe), progress, [len(level) for level in levels]


def verify_path(path, width, radius, regime, rule, root, require_safe, distinct):
    if path is None:
        return False
    state = (0, root)
    seen = {0}
    for depth, step in enumerate(path, 1):
        if step["from_behavior"] != state[0] or step["from_checker"] != state[1] or step["progress"] != depth:
            return False
        proposed, successor = step["to_behavior"], step["to_checker"]
        if (state[0] ^ proposed).bit_count() != 1 or (state[1] ^ successor).bit_count() > radius:
            return False
        expected_class = proof_for(state, proposed, successor, regime, rule, root)
        if expected_class is None or step["proof"] not in ({0, 2} if expected_class == 0 else {1, 3}):
            return False
        if require_safe and bit(proposed, 0):
            return False
        if distinct and proposed in seen:
            return False
        seen.add(proposed)
        state = (proposed, successor)
    return True


def universe_record(width, radius, horizon, tokens):
    count = horizon * (1 << width) * 16 * width * len(tokens) * sum(math.comb(4, d) for d in range(radius + 1))
    specification = {
        "behavior_order": "ascending single-bit flips",
        "checker_order": "ascending hamming-distance-at-most-radius",
        "proof_order": list(tokens),
        "progress_layers": horizon,
        "radius": radius,
        "width": width,
    }
    label_payload = {behavior: bit(behavior, 0) == 0 for behavior in range(1 << width)}
    return {
        "width": width,
        "radius": radius,
        "candidate_edge_count": count,
        "candidate_universe_spec_sha256": hashlib.sha256(canonical_json(specification).encode()).hexdigest(),
        "semantic_label_table_sha256": hashlib.sha256(canonical_json(label_payload).encode()).hexdigest(),
    }


def verify(result_path: Path, receipt_path: Path) -> dict[str, Any]:
    protocol = json.loads((HERE / "protocol_v0_2.json").read_text(encoding="utf-8"))
    registration = json.loads((HERE / "registration_v0_2.json").read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    checks = {
        "result_hash_matches": sha256(result_path) == receipt["result_sha256"],
        "protocol_hash_matches": sha256(HERE / "protocol_v0_2.json") == receipt["protocol_sha256"],
        "registration_hash_matches": sha256(HERE / "registration_v0_2.json") == receipt["registration_sha256"],
        "schema_exact": result.get("schema_version") == "asmp5_verifier_drift_result_v0_2",
        "runner_valid": result.get("runner_gate_pass") is True and result.get("instrument_status") == "valid",
        "resource_pass": result.get("resource_receipt", {}).get("pass") is True,
    }
    horizon, root = protocol["horizon"], protocol["root_checker"]
    keys = set(itertools.product(protocol["behavior_widths"], protocol["mutation_radii"], protocol["certificate_rules"], protocol["regimes"]))
    cells = result.get("cells", [])
    lookup = {(c["width"], c["radius"], c["rule"], c["regime"]): c for c in cells}
    checks["cell_universe_exact"] = len(cells) == protocol["registered_cell_count"] and set(lookup) == keys
    replay_ok = checks["cell_universe_exact"]
    for key, cell in lookup.items():
        levels = replay_layers(*key[:2], horizon, key[3], key[2], root)
        unsafe, safe_count, progress, counts = summary(levels)
        replay_ok = replay_ok and cell["unsafe_depth"] == unsafe
        replay_ok = replay_ok and cell["reachable_safe_behavior_count"] == safe_count
        replay_ok = replay_ok and cell["maximum_safe_progress"] == progress
        replay_ok = replay_ok and cell["reachable_state_count_by_depth"] == counts
        replay_ok = replay_ok and cell["reachability_digest"] == digest(levels)
        if cell["unsafe_path"] is not None:
            replay_ok = replay_ok and verify_path(cell["unsafe_path"], key[0], key[1], key[3], key[2], root, False, False)
    checks["all_cells_independently_recomputed"] = replay_ok
    expected_universes = [
        universe_record(width, radius, horizon, protocol["proof_tokens"])
        for width in protocol["behavior_widths"]
        for radius in protocol["mutation_radii"]
    ]
    checks["candidate_universe_counts_and_specs_recomputed"] = result["gates"]["G1_shared_candidate_universe"]["universe_receipts"] == expected_universes
    separating = []
    for radius in (1, 2):
        for rule in ("self_endorsement", "pairwise_agreement"):
            adaptive, rooted = lookup[(6, radius, rule, "adaptive")], lookup[(6, radius, rule, "frozen_root")]
            if adaptive["unsafe_depth"] is not None and adaptive["unsafe_depth"] <= 4 and rooted["unsafe_depth"] is None:
                separating.append((radius, rule))
    checks["primary_separation_recomputed"] = bool(separating)
    chain = result["gates"]["G4_root_refinement_and_liveness"]["safe_chain"]
    checks["safe_chain_replays"] = len(chain or []) == 8 and verify_path(chain, 6, 1, "adaptive", "root_refinement", root, True, True)
    checks["all_runner_gates_pass"] = len(result.get("gates", {})) == 8 and all(gate["pass"] for gate in result["gates"].values())
    checks["registration_sources_still_match"] = all(
        sha256(HERE.parents[3] / relative) == expected for relative, expected in registration["source_hashes"].items()
    )
    passed = all(checks.values())
    return {
        "schema_version": "asmp5_verifier_drift_verification_v0_2",
        "instrument_status": "valid" if passed else "invalid",
        "decision": "pass" if passed else "invalid_stop",
        "checks": checks,
        "claim_boundary": "Independent replay of one finite matched verifier-drift census; no open-ended reflective-safety inference.",
    }


def write_once(path: Path, payload: bytes) -> None:
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def parse_args(argv: Iterable[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    verification = verify(args.result.resolve(), args.receipt.resolve())
    write_once(args.output.resolve(), canonical_json(verification).encode())
    print(canonical_json(verification), end="")
    return 0 if verification["decision"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
