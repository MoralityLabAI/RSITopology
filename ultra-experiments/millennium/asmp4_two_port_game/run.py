"""Exact registered finite safety-game runner for ASMP-4."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import subprocess
import time
import tracemalloc
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()
State = tuple[Fraction, Fraction]


def F(value: str | int | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(str(value))


def ft(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}" if value.denominator != 1 else str(value.numerator)


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
    bindings: dict[str, Any] = {}
    for path in paths:
        relative = path.resolve().relative_to(REPO_ROOT).as_posix()
        if git("status", "--porcelain", "--", relative).stdout.strip():
            raise ValueError(f"sealed input is dirty or untracked: {relative}")
        committed = git("show", f"HEAD:{relative}", text=False).stdout
        working = path.resolve().read_bytes()
        if committed != working:
            raise ValueError(f"sealed input differs from HEAD: {relative}")
        bindings[relative] = {
            "sha256": hashlib.sha256(working).hexdigest(),
            "git_blob": git("rev-parse", f"HEAD:{relative}").stdout.strip(),
        }
    diff_payload = git("diff", "--binary", "HEAD", "--", text=False).stdout
    diff_hash = hashlib.sha256(diff_payload).hexdigest()
    if diff_hash != EMPTY_SHA256:
        raise ValueError("tracked diff is nonempty at registered run start")
    return {"commit": commit, "tracked_diff_sha256": diff_hash, "sealed_inputs": bindings}


def initial_states(protocol: dict[str, Any]) -> frozenset[State]:
    n_values = tuple(F(value) for value in protocol["plant"]["initial_n"])
    z_values = tuple(F(value) for value in protocol["plant"]["initial_z"])
    return frozenset(itertools.product(n_values, z_values))


def thresholds(protocol: dict[str, Any], read_bits: int) -> tuple[Fraction, ...]:
    return tuple(F(value) for value in protocol["interface"]["ordered_sensor_thresholds"][str(read_bits)])


def actions(protocol: dict[str, Any], write_bits: int) -> tuple[Fraction, ...]:
    return tuple(F(value) for value in protocol["interface"]["action_dictionaries"][str(write_bits)])


def sensor_symbol(
    state: State,
    *,
    a_n: Fraction,
    coupling: Fraction,
    cuts: Sequence[Fraction],
    relabel: bool = False,
) -> int:
    n_value, z_value = state
    q_value = a_n * n_value + coupling * z_value
    symbol = sum(q_value >= cut for cut in cuts)
    return len(cuts) - symbol if relabel else symbol


def plant_step(
    state: State,
    *,
    a_n: Fraction,
    a_z: Fraction,
    coupling: Fraction,
    action: Fraction,
    disturbance: Fraction,
) -> State:
    n_value, z_value = state
    return (
        a_n * n_value + coupling * z_value + action + disturbance,
        a_z * z_value,
    )


def safe(state: State) -> bool:
    return abs(state[0]) <= 1


def solve_universal(
    protocol: dict[str, Any],
    *,
    horizon: int,
    a_n: Fraction,
    a_z: Fraction,
    coupling: Fraction,
    read_bits: int,
    write_bits: int,
    relabel: bool = False,
) -> dict[str, Any]:
    states_0 = initial_states(protocol)
    disturbances = tuple(F(value) for value in protocol["plant"]["disturbances"])
    cuts = thresholds(protocol, read_bits)
    action_values = actions(protocol, write_bits)
    failed: set[tuple[int, frozenset[State]]] = set()
    stats = {"belief_sets_visited": 0, "action_assignments_tested": 0, "max_reachable_states": len(states_0)}

    def recurse(time_index: int, states: frozenset[State]) -> list[dict[str, str]] | None:
        if time_index == horizon:
            return []
        key = (time_index, states)
        if key in failed:
            return None
        stats["belief_sets_visited"] += 1
        stats["max_reachable_states"] = max(stats["max_reachable_states"], len(states))
        groups: dict[int, list[State]] = {}
        for state in sorted(states):
            symbol = sensor_symbol(
                state,
                a_n=a_n,
                coupling=coupling,
                cuts=cuts,
                relabel=relabel,
            )
            groups.setdefault(symbol, []).append(state)
        symbols = tuple(sorted(groups))
        for assignment in itertools.product(action_values, repeat=len(symbols)):
            stats["action_assignments_tested"] += 1
            policy = dict(zip(symbols, assignment))
            next_states: set[State] = set()
            valid = True
            for symbol, group in groups.items():
                action = policy[symbol]
                for state in group:
                    for disturbance in disturbances:
                        successor = plant_step(
                            state,
                            a_n=a_n,
                            a_z=a_z,
                            coupling=coupling,
                            action=action,
                            disturbance=disturbance,
                        )
                        if not safe(successor):
                            valid = False
                            break
                        next_states.add(successor)
                    if not valid:
                        break
                if not valid:
                    break
            if not valid:
                continue
            suffix = recurse(time_index + 1, frozenset(next_states))
            if suffix is not None:
                current = {str(symbol): ft(policy[symbol]) for symbol in symbols}
                return [current, *suffix]
        failed.add(key)
        return None

    witness = recurse(0, states_0)
    return {
        "feasible": witness is not None,
        "policy": witness,
        **stats,
    }


def replay_policy(
    protocol: dict[str, Any],
    *,
    policy: Sequence[dict[str, str]],
    horizon: int,
    a_n: Fraction,
    a_z: Fraction,
    coupling: Fraction,
    read_bits: int,
    relabel: bool = False,
) -> dict[str, Any]:
    states = initial_states(protocol)
    disturbances = tuple(F(value) for value in protocol["plant"]["disturbances"])
    cuts = thresholds(protocol, read_bits)
    maximum_count = len(states)
    if len(policy) != horizon:
        return {"pass": False, "reason": "wrong_horizon"}
    for time_index in range(horizon):
        mapping = {int(symbol): F(action) for symbol, action in policy[time_index].items()}
        next_states: set[State] = set()
        for state in states:
            symbol = sensor_symbol(state, a_n=a_n, coupling=coupling, cuts=cuts, relabel=relabel)
            if symbol not in mapping:
                return {"pass": False, "reason": "missing_symbol"}
            for disturbance in disturbances:
                successor = plant_step(
                    state,
                    a_n=a_n,
                    a_z=a_z,
                    coupling=coupling,
                    action=mapping[symbol],
                    disturbance=disturbance,
                )
                if not safe(successor):
                    return {"pass": False, "reason": "unsafe_successor"}
                next_states.add(successor)
        states = frozenset(next_states)
        maximum_count = max(maximum_count, len(states))
    return {"pass": True, "final_state_count": len(states), "maximum_state_count": maximum_count}


def quantifier_trap() -> dict[str, Any]:
    initial = (F(-1), F(1))
    available_actions = (F(-1), F(1))
    per_cell = all(any(state + action == 0 for action in available_actions) for state in initial)
    universal = any(all(state + action == 0 for state in initial) for action in available_actions)
    return {"per_cell_feasible": per_cell, "universal_feasible": universal, "pass": per_cell and not universal}


def analog_full_state_control(
    protocol: dict[str, Any],
    *,
    horizon: int,
    a_n: Fraction,
    a_z: Fraction,
    coupling: Fraction,
) -> bool:
    states = initial_states(protocol)
    disturbances = tuple(F(value) for value in protocol["plant"]["disturbances"])
    for _ in range(horizon):
        next_states = set()
        for n_value, z_value in states:
            q_value = a_n * n_value + coupling * z_value
            action = -q_value
            for disturbance in disturbances:
                successor = plant_step(
                    (n_value, z_value),
                    a_n=a_n,
                    a_z=a_z,
                    coupling=coupling,
                    action=action,
                    disturbance=disturbance,
                )
                if not safe(successor):
                    return False
                next_states.add(successor)
        states = frozenset(next_states)
    return True


def grid_key(horizon: int, read_bits: int, write_bits: int, coupling: Fraction, a_z: Fraction) -> str:
    return f"T={horizon}|r={read_bits}|w={write_bits}|c={ft(coupling)}|az={ft(a_z)}"


def run_registered(protocol: dict[str, Any]) -> dict[str, Any]:
    a_n = F(protocol["plant"]["primary_a_n"])
    horizons = tuple(int(value) for value in protocol["registered_grid"]["horizons"])
    read_grid = tuple(int(value) for value in protocol["interface"]["read_bits_per_step"])
    write_grid = tuple(int(value) for value in protocol["interface"]["write_bits_per_step"])
    couplings = tuple(F(value) for value in protocol["plant"]["coupling_grid"])
    tangent_rates = tuple(F(value) for value in protocol["plant"]["a_z_grid"])
    rows = []
    lookup: dict[str, dict[str, Any]] = {}
    every_witness_replays = True
    every_relabel_matches = True
    for horizon, read_bits, write_bits, coupling, a_z in itertools.product(
        horizons, read_grid, write_grid, couplings, tangent_rates
    ):
        solved = solve_universal(
            protocol,
            horizon=horizon,
            a_n=a_n,
            a_z=a_z,
            coupling=coupling,
            read_bits=read_bits,
            write_bits=write_bits,
        )
        relabeled = solve_universal(
            protocol,
            horizon=horizon,
            a_n=a_n,
            a_z=a_z,
            coupling=coupling,
            read_bits=read_bits,
            write_bits=write_bits,
            relabel=True,
        )
        replay = None
        if solved["feasible"]:
            replay = replay_policy(
                protocol,
                policy=solved["policy"],
                horizon=horizon,
                a_n=a_n,
                a_z=a_z,
                coupling=coupling,
                read_bits=read_bits,
            )
            every_witness_replays = every_witness_replays and replay["pass"]
        every_relabel_matches = every_relabel_matches and solved["feasible"] == relabeled["feasible"]
        row = {
            "horizon": horizon,
            "read_bits_per_step": read_bits,
            "write_bits_per_step": write_bits,
            "read_budget": horizon * read_bits,
            "write_budget": horizon * write_bits,
            "coupling": ft(coupling),
            "a_z": ft(a_z),
            "feasible": solved["feasible"],
            "universal_policy": solved["policy"],
            "witness_replay": replay,
            "belief_sets_visited": solved["belief_sets_visited"],
            "action_assignments_tested": solved["action_assignments_tested"],
            "max_reachable_states": solved["max_reachable_states"],
            "symbol_relabel_feasible": relabeled["feasible"],
        }
        rows.append(row)
        lookup[grid_key(horizon, read_bits, write_bits, coupling, a_z)] = row

    stable = solve_universal(
        protocol,
        horizon=3,
        a_n=F(protocol["plant"]["stable_control_a_n"]),
        a_z=F("3/2"),
        coupling=F(0),
        read_bits=0,
        write_bits=0,
    )
    underbudget_key = grid_key(2, 0, 0, F("1/2"), F("3/2"))
    zero_coupling_key = grid_key(2, 0, 0, F(0), F("3/2"))
    full_key = grid_key(2, 2, 2, F("1/2"), F("3/2"))
    read_deficient_key = grid_key(2, 0, 2, F("1/2"), F("3/2"))
    write_deficient_key = grid_key(2, 2, 0, F("1/2"), F("3/2"))

    zero_coupling_invariant = True
    for horizon, read_bits, write_bits in itertools.product(horizons, read_grid, write_grid):
        left = lookup[grid_key(horizon, read_bits, write_bits, F(0), F("6/5"))]["feasible"]
        right = lookup[grid_key(horizon, read_bits, write_bits, F(0), F("3/2"))]["feasible"]
        zero_coupling_invariant = zero_coupling_invariant and left == right

    trap = quantifier_trap()
    analog_pass = analog_full_state_control(
        protocol,
        horizon=2,
        a_n=a_n,
        a_z=F("3/2"),
        coupling=F("1/2"),
    )
    gates = {
        "G0_registration_binding": {"pass": True},
        "G1_universal_quantifier_trap": {"pass": trap["pass"], **trap},
        "G2_stable_zero_rate_liveness": {
            "pass": stable["feasible"],
            "universal_policy": stable["policy"],
        },
        "G3_authority_and_side_channel_controls": {
            "pass": analog_pass and not lookup[underbudget_key]["feasible"],
            "full_state_continuous_action_pass": analog_pass,
            "declared_underbudget_cell_pass": lookup[underbudget_key]["feasible"],
        },
        "G4_zero_coupling_tangent_invariance": {"pass": zero_coupling_invariant},
        "G5_coupling_changes_frontier": {
            "pass": lookup[zero_coupling_key]["feasible"] and not lookup[underbudget_key]["feasible"],
            "zero_coupling_cell_pass": lookup[zero_coupling_key]["feasible"],
            "strong_coupling_cell_pass": lookup[underbudget_key]["feasible"],
        },
        "G6_separate_port_boundary": {
            "pass": lookup[full_key]["feasible"]
            and not lookup[read_deficient_key]["feasible"]
            and not lookup[write_deficient_key]["feasible"],
            "r2_w2": lookup[full_key]["feasible"],
            "r0_w2": lookup[read_deficient_key]["feasible"],
            "r2_w0": lookup[write_deficient_key]["feasible"],
        },
        "G7_grid_and_witness_replay": {
            "pass": len(rows) == int(protocol["registered_grid"]["cell_count"])
            and every_witness_replays
            and every_relabel_matches,
            "cell_count": len(rows),
            "every_witness_replays": every_witness_replays,
            "every_symbol_relabel_matches": every_relabel_matches,
        },
    }
    passed = all(record["pass"] for record in gates.values())
    return {
        "schema_version": "asmp4_two_port_game_result_v0_1",
        "protocol_id": protocol["protocol_id"],
        "instrument_status": "valid" if passed else "invalid",
        "evidence_label": protocol["evidence_label_on_pass"] if passed else "not_established",
        "runner_gate_pass": passed,
        "stage_decision": "pending_independent_verification" if passed else "invalid_or_failed_stop_sequence",
        "gates": gates,
        "grid": rows,
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
    if protocol.get("schema_version") != "asmp4_two_port_game_protocol_v0_1":
        raise ValueError("unexpected protocol schema")
    sealed = (
        protocol_path,
        HERE / "CLAIM_PACKET.md",
        HERE / "README.md",
        Path(__file__).resolve(),
        HERE / "verify_result.py",
        HERE / "test_two_port_game.py",
    )
    output_dir = args.output_dir.resolve()
    if any(output_dir == path or output_dir in path.parents for path in sealed):
        raise ValueError("output directory aliases or contains a sealed input")
    result_path = output_dir / "result_v0_1.json"
    receipt_path = output_dir / "receipt_v0_1.json"
    if result_path.exists() or receipt_path.exists():
        raise FileExistsError("registered output already exists")
    registration = bind_committed_inputs(sealed)

    tracemalloc.start()
    started = time.perf_counter()
    result = run_registered(protocol)
    elapsed = time.perf_counter() - started
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    ceiling = protocol["resource_ceiling"]
    resource_pass = elapsed <= ceiling["wall_seconds"] and peak_bytes <= ceiling["python_peak_bytes"]
    result["resource_receipt"] = {
        "elapsed_seconds": elapsed,
        "python_tracemalloc_peak_bytes": peak_bytes,
        "wall_ceiling_seconds": ceiling["wall_seconds"],
        "python_peak_ceiling_bytes": ceiling["python_peak_bytes"],
        "pass": resource_pass,
    }
    if not resource_pass:
        result["instrument_status"] = "invalid"
        result["runner_gate_pass"] = False
        result["stage_decision"] = "invalid_resource_cap_stop_sequence"
    result["registration"] = registration
    result["protocol_sha256"] = sha256_file(protocol_path)
    result_payload = canonical_json(result).encode("utf-8")
    write_once(result_path, result_payload)
    receipt = {
        "schema_version": "asmp4_two_port_game_receipt_v0_1",
        "git_commit_at_run": registration["commit"],
        "git_tracked_diff_sha256_at_run": registration["tracked_diff_sha256"],
        "protocol_sha256": sha256_file(protocol_path),
        "claim_packet_sha256": sha256_file(HERE / "CLAIM_PACKET.md"),
        "runner_sha256": sha256_file(Path(__file__).resolve()),
        "verifier_sha256": sha256_file(HERE / "verify_result.py"),
        "tests_sha256": sha256_file(HERE / "test_two_port_game.py"),
        "result_sha256": hashlib.sha256(result_payload).hexdigest(),
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
    }
    write_once(receipt_path, canonical_json(receipt).encode("utf-8"))
    print(canonical_json({
        "instrument_status": result["instrument_status"],
        "runner_gate_pass": result["runner_gate_pass"],
        "stage_decision": result["stage_decision"],
        "elapsed_seconds": elapsed,
        "grid_cells": len(result["grid"]),
        "result": str(result_path),
    }), end="")
    return 0 if result["runner_gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
