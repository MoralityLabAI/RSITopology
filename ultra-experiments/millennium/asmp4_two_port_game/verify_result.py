"""Independent exact verifier for the registered ASMP-4 finite game."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence


HERE = Path(__file__).resolve().parent
State = tuple[Fraction, Fraction]


def F(value: str | int | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(str(value))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def write_once(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"refusing to overwrite non-identical artifact: {path}")
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def states_0(protocol: dict[str, Any]) -> frozenset[State]:
    return frozenset(
        (F(n_value), F(z_value))
        for n_value in protocol["plant"]["initial_n"]
        for z_value in protocol["plant"]["initial_z"]
    )


def sensor(state: State, a_n: Fraction, coupling: Fraction, cuts: Sequence[Fraction], relabel: bool) -> int:
    q_value = a_n * state[0] + coupling * state[1]
    raw = sum(q_value >= cut for cut in cuts)
    return len(cuts) - raw if relabel else raw


def successor(
    state: State,
    a_n: Fraction,
    a_z: Fraction,
    coupling: Fraction,
    action: Fraction,
    disturbance: Fraction,
) -> State:
    return (
        a_n * state[0] + coupling * state[1] + action + disturbance,
        a_z * state[1],
    )


def exact_feasible(
    protocol: dict[str, Any],
    horizon: int,
    read_bits: int,
    write_bits: int,
    coupling: Fraction,
    a_z: Fraction,
    *,
    a_n: Fraction | None = None,
    relabel: bool = False,
) -> bool:
    """Independently enumerate time-indexed symbol/action maps over exact beliefs."""
    normal_rate = a_n if a_n is not None else F(protocol["plant"]["primary_a_n"])
    cuts = tuple(F(value) for value in protocol["interface"]["ordered_sensor_thresholds"][str(read_bits)])
    action_set = tuple(F(value) for value in protocol["interface"]["action_dictionaries"][str(write_bits)])
    disturbances = tuple(F(value) for value in protocol["plant"]["disturbances"])
    rejected: set[tuple[int, frozenset[State]]] = set()

    def search(step: int, belief: frozenset[State]) -> bool:
        if step == horizon:
            return True
        key = (step, belief)
        if key in rejected:
            return False
        by_message: dict[int, list[State]] = {}
        for state in belief:
            message = sensor(state, normal_rate, coupling, cuts, relabel)
            by_message.setdefault(message, []).append(state)
        messages = tuple(sorted(by_message))
        for action_vector in itertools.product(action_set, repeat=len(messages)):
            decoder = dict(zip(messages, action_vector))
            future: set[State] = set()
            admissible = True
            for message, group in by_message.items():
                for state in group:
                    for disturbance in disturbances:
                        candidate = successor(
                            state, normal_rate, a_z, coupling, decoder[message], disturbance
                        )
                        if abs(candidate[0]) > 1:
                            admissible = False
                            break
                        future.add(candidate)
                    if not admissible:
                        break
                if not admissible:
                    break
            if admissible and search(step + 1, frozenset(future)):
                return True
        rejected.add(key)
        return False

    return search(0, states_0(protocol))


def replay_reported_witness(protocol: dict[str, Any], row: dict[str, Any]) -> bool:
    policy = row.get("universal_policy")
    if not row["feasible"]:
        return policy is None
    if not isinstance(policy, list) or len(policy) != row["horizon"]:
        return False
    normal_rate = F(protocol["plant"]["primary_a_n"])
    a_z = F(row["a_z"])
    coupling = F(row["coupling"])
    cuts = tuple(F(value) for value in protocol["interface"]["ordered_sensor_thresholds"][str(row["read_bits_per_step"])])
    disturbances = tuple(F(value) for value in protocol["plant"]["disturbances"])
    belief = states_0(protocol)
    for mapping_payload in policy:
        mapping = {int(key): F(value) for key, value in mapping_payload.items()}
        future: set[State] = set()
        for state in belief:
            message = sensor(state, normal_rate, coupling, cuts, False)
            if message not in mapping:
                return False
            for disturbance in disturbances:
                candidate = successor(state, normal_rate, a_z, coupling, mapping[message], disturbance)
                if abs(candidate[0]) > 1:
                    return False
                future.add(candidate)
        belief = frozenset(future)
    return True


def analog_control_passes(protocol: dict[str, Any]) -> bool:
    belief = states_0(protocol)
    a_n, a_z, coupling = F("3/2"), F("3/2"), F("1/2")
    disturbances = tuple(F(value) for value in protocol["plant"]["disturbances"])
    for _ in range(2):
        future: set[State] = set()
        for state in belief:
            action = -(a_n * state[0] + coupling * state[1])
            for disturbance in disturbances:
                candidate = successor(state, a_n, a_z, coupling, action, disturbance)
                if abs(candidate[0]) > 1:
                    return False
                future.add(candidate)
        belief = frozenset(future)
    return True


def row_key(row: dict[str, Any]) -> tuple[int, int, int, Fraction, Fraction]:
    return (
        int(row["horizon"]),
        int(row["read_bits_per_step"]),
        int(row["write_bits_per_step"]),
        F(row["coupling"]),
        F(row["a_z"]),
    )


def verify(result_path: Path, receipt_path: Path) -> dict[str, Any]:
    protocol = json.loads((HERE / "protocol_v0_1.json").read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {
        "result_hash_matches_receipt": sha256_file(result_path) == receipt.get("result_sha256"),
        "protocol_hash_matches_receipt": sha256_file(HERE / "protocol_v0_1.json") == receipt.get("protocol_sha256"),
        "claim_hash_matches_receipt": sha256_file(HERE / "CLAIM_PACKET.md") == receipt.get("claim_packet_sha256"),
        "verifier_hash_matches_receipt": sha256_file(Path(__file__).resolve()) == receipt.get("verifier_sha256"),
        "schema_exact": result.get("schema_version") == "asmp4_two_port_game_result_v0_1",
        "runner_status_valid": result.get("instrument_status") == "valid" and result.get("runner_gate_pass") is True,
        "evidence_label_exact": result.get("evidence_label") == "exact_registered_architecture_phase_map",
    }
    rows = result.get("grid", [])
    expected_keys = set(
        itertools.product(
            map(int, protocol["registered_grid"]["horizons"]),
            map(int, protocol["interface"]["read_bits_per_step"]),
            map(int, protocol["interface"]["write_bits_per_step"]),
            map(F, protocol["plant"]["coupling_grid"]),
            map(F, protocol["plant"]["a_z_grid"]),
        )
    )
    observed_keys = {row_key(row) for row in rows}
    checks["grid_universe_exact"] = len(rows) == 108 and len(observed_keys) == 108 and observed_keys == expected_keys
    exact_rows = True
    witnesses_replay = True
    relabel_invariance = True
    if checks["grid_universe_exact"]:
        for row in rows:
            key = row_key(row)
            independent = exact_feasible(protocol, *key[:3], key[3], key[4])
            relabeled = exact_feasible(protocol, *key[:3], key[3], key[4], relabel=True)
            exact_rows = exact_rows and independent == row["feasible"]
            relabel_invariance = relabel_invariance and relabeled == independent == row["symbol_relabel_feasible"]
            witnesses_replay = witnesses_replay and replay_reported_witness(protocol, row)
    else:
        exact_rows = witnesses_replay = relabel_invariance = False
    checks["all_cells_independently_recomputed"] = exact_rows
    checks["all_reported_witnesses_replay"] = witnesses_replay
    checks["symbol_relabel_invariance_recomputed"] = relabel_invariance

    lookup = {row_key(row): row["feasible"] for row in rows}
    get = lambda h, r, w, c, az: lookup.get((h, r, w, F(c), F(az)))
    checks["stable_zero_rate_liveness_recomputed"] = exact_feasible(
        protocol, 3, 0, 0, F(0), F("3/2"), a_n=F("4/5")
    )
    checks["continuous_authority_control_recomputed"] = analog_control_passes(protocol)
    checks["coupling_frontier_recomputed"] = get(2, 0, 0, 0, "3/2") is True and get(2, 0, 0, "1/2", "3/2") is False
    checks["separate_ports_recomputed"] = get(2, 2, 2, "1/2", "3/2") is True and get(2, 0, 2, "1/2", "3/2") is False and get(2, 2, 0, "1/2", "3/2") is False
    checks["zero_coupling_tangent_invariance_recomputed"] = all(
        get(h, r, w, 0, "6/5") == get(h, r, w, 0, "3/2")
        for h, r, w in itertools.product((2, 3), (0, 1, 2), (0, 1, 2))
    )
    trap_per_cell = all(any(state + action == 0 for action in (F(-1), F(1))) for state in (F(-1), F(1)))
    trap_universal = any(all(state + action == 0 for state in (F(-1), F(1))) for action in (F(-1), F(1)))
    checks["quantifier_trap_recomputed"] = trap_per_cell and not trap_universal
    checks["runner_gate_universe_and_passes"] = set(result.get("gates", {})) == {
        "G0_registration_binding",
        "G1_universal_quantifier_trap",
        "G2_stable_zero_rate_liveness",
        "G3_authority_and_side_channel_controls",
        "G4_zero_coupling_tangent_invariance",
        "G5_coupling_changes_frontier",
        "G6_separate_port_boundary",
        "G7_grid_and_witness_replay",
    } and all(record.get("pass") is True for record in result.get("gates", {}).values())
    checks["resource_ceiling_pass"] = result.get("resource_receipt", {}).get("pass") is True
    checks["registration_commit_agrees"] = result.get("registration", {}).get("commit") == receipt.get("git_commit_at_run")

    passed = all(checks.values())
    return {
        "schema_version": "asmp4_two_port_game_verification_v0_1",
        "instrument_status": "valid" if passed else "invalid",
        "G8_independent_verification": {"pass": passed, "checks": checks},
        "stage_decision": "pass" if passed else "invalid_stop_sequence",
        "next_stage": "ASMP-5" if passed else None,
        "claim_boundary": "Exact verification of the registered finite architecture only; no asymptotic theorem claim.",
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
        raise FileNotFoundError("result and receipt are required")
    if args.output.resolve() in {args.result.resolve(), args.receipt.resolve()}:
        raise ValueError("verification output aliases an input")
    verification = verify(args.result.resolve(), args.receipt.resolve())
    write_once(args.output.resolve(), canonical_json(verification).encode("utf-8"))
    print(canonical_json(verification), end="")
    return 0 if verification["stage_decision"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
