"""Definition audit for the canonical ASMP-4 two-port capacity region.

This is a development/audit harness, not a preregistered claim-eligible run.
It checks whether the existing finite ASMP-4 grid can be interpreted as the
canonical achieved-transcript budget region.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "asmp4_two_port_game"
PROTOCOL_PATH = SOURCE / "protocol_v0_1.json"
RESULT_PATH = SOURCE / "artifacts" / "result_v0_1.json"

State = tuple[Fraction, Fraction]


def F(value: str | int | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(str(value))


def ft(value: Fraction) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return value


def initial_states(protocol: dict[str, Any]) -> frozenset[State]:
    return frozenset(
        (F(n_value), F(z_value))
        for n_value in protocol["plant"]["initial_n"]
        for z_value in protocol["plant"]["initial_z"]
    )


def sensor_symbol(
    state: State,
    *,
    a_n: Fraction,
    coupling: Fraction,
    cuts: Sequence[Fraction],
) -> int:
    q_value = a_n * state[0] + coupling * state[1]
    return sum(q_value >= cut for cut in cuts)


def plant_step(
    state: State,
    *,
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


def safe(state: State) -> bool:
    return abs(state[0]) <= 1


def row_key(row: dict[str, Any]) -> tuple[int, str, str, int, int]:
    return (
        int(row["horizon"]),
        str(row["coupling"]),
        str(row["a_z"]),
        int(row["read_bits_per_step"]),
        int(row["write_bits_per_step"]),
    )


def row_context(row: dict[str, Any]) -> tuple[int, str, str]:
    return int(row["horizon"]), str(row["coupling"]), str(row["a_z"])


def upward_closure_violations(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """Find failures of the upper-set axiom forced by ``rate <= budget``."""

    lookup = {row_key(row): row for row in rows}
    read_budgets = sorted({int(row["read_bits_per_step"]) for row in rows})
    write_budgets = sorted({int(row["write_bits_per_step"]) for row in rows})
    violations: list[dict[str, Any]] = []
    for source in rows:
        if not source["feasible"]:
            continue
        horizon, coupling, a_z, source_read, source_write = row_key(source)
        for target_read in read_budgets:
            for target_write in write_budgets:
                if target_read < source_read or target_write < source_write:
                    continue
                target = lookup[(horizon, coupling, a_z, target_read, target_write)]
                if not target["feasible"]:
                    violations.append(
                        {
                            "horizon": horizon,
                            "coupling": coupling,
                            "a_z": a_z,
                            "feasible_source": [source_read, source_write],
                            "infeasible_larger_budget": [target_read, target_write],
                        }
                    )
    return violations


def action_dictionary_nesting_violations(
    protocol: dict[str, Any],
) -> list[dict[str, Any]]:
    """Check whether a larger nominal write budget retains lower-budget actions."""

    dictionaries = {
        int(bits): frozenset(F(value) for value in values)
        for bits, values in protocol["interface"]["action_dictionaries"].items()
    }
    violations: list[dict[str, Any]] = []
    for lower, higher in itertools.combinations(sorted(dictionaries), 2):
        missing = sorted(dictionaries[lower] - dictionaries[higher])
        if missing:
            violations.append(
                {
                    "lower_bits": lower,
                    "higher_bits": higher,
                    "lower_budget_actions_missing_at_higher_budget": [
                        ft(value) for value in missing
                    ],
                }
            )
    return violations


def witness_transcript_profile(
    protocol: dict[str, Any], row: dict[str, Any]
) -> dict[str, Any]:
    """Replay a feasible witness while retaining read and write histories."""

    if not row["feasible"]:
        raise ValueError("transcript profiles require a feasible row")
    policy = row.get("universal_policy")
    if not isinstance(policy, list) or len(policy) != int(row["horizon"]):
        raise ValueError("reported witness has the wrong horizon")

    a_n = F(protocol["plant"]["primary_a_n"])
    a_z = F(row["a_z"])
    coupling = F(row["coupling"])
    disturbances = tuple(F(value) for value in protocol["plant"]["disturbances"])
    cuts = tuple(
        F(value)
        for value in protocol["interface"]["ordered_sensor_thresholds"][
            str(row["read_bits_per_step"])
        ]
    )
    action_values = tuple(
        F(value)
        for value in protocol["interface"]["action_dictionaries"][
            str(row["write_bits_per_step"])
        ]
    )
    action_to_symbol = {action: index for index, action in enumerate(action_values)}
    if len(action_to_symbol) != len(action_values):
        raise ValueError("action dictionary must not contain duplicate codewords")

    histories: set[tuple[State, tuple[int, ...], tuple[int, ...]]] = {
        (state, (), ()) for state in initial_states(protocol)
    }
    prefixes: list[dict[str, Any]] = []
    for time_index, mapping_payload in enumerate(policy):
        if not isinstance(mapping_payload, dict):
            raise TypeError("policy rows must be JSON objects")
        mapping = {int(symbol): F(action) for symbol, action in mapping_payload.items()}
        future: set[tuple[State, tuple[int, ...], tuple[int, ...]]] = set()
        for state, read_history, write_history in histories:
            read_symbol = sensor_symbol(state, a_n=a_n, coupling=coupling, cuts=cuts)
            if read_symbol not in mapping:
                raise ValueError(f"witness omits realized read symbol {read_symbol}")
            action = mapping[read_symbol]
            if action not in action_to_symbol:
                raise ValueError(
                    "witness action is absent from the registered write dictionary"
                )
            write_symbol = action_to_symbol[action]
            for disturbance in disturbances:
                next_state = plant_step(
                    state,
                    a_n=a_n,
                    a_z=a_z,
                    coupling=coupling,
                    action=action,
                    disturbance=disturbance,
                )
                if not safe(next_state):
                    raise ValueError("reported feasible witness leaves the safe set")
                future.add(
                    (
                        next_state,
                        read_history + (read_symbol,),
                        write_history + (write_symbol,),
                    )
                )
        histories = future
        read_count = len({history[1] for history in histories})
        write_count = len({history[2] for history in histories})
        prefixes.append(
            {
                "time": time_index + 1,
                "read_transcript_count": read_count,
                "write_transcript_count": write_count,
                "trajectory_history_count": len(histories),
            }
        )

    horizon = int(row["horizon"])
    final = (
        prefixes[-1]
        if prefixes
        else {
            "read_transcript_count": 1,
            "write_transcript_count": 1,
        }
    )
    read_count = int(final["read_transcript_count"])
    write_count = int(final["write_transcript_count"])
    return {
        "row": {
            "horizon": horizon,
            "coupling": str(row["coupling"]),
            "a_z": str(row["a_z"]),
            "nominal_read_bits_per_step": int(row["read_bits_per_step"]),
            "nominal_write_bits_per_step": int(row["write_bits_per_step"]),
        },
        "prefixes": prefixes,
        "read_transcript_count": read_count,
        "write_transcript_count": write_count,
        "achieved_read_bits_per_step": math.log2(read_count) / horizon
        if horizon
        else 0.0,
        "achieved_write_bits_per_step": math.log2(write_count) / horizon
        if horizon
        else 0.0,
    }


def profile_all_witnesses(
    protocol: dict[str, Any], rows: Sequence[dict[str, Any]]
) -> dict[str, Any]:
    profiles = [
        witness_transcript_profile(protocol, row) for row in rows if row["feasible"]
    ]
    data_processing_violations = [
        profile
        for profile in profiles
        if profile["write_transcript_count"] > profile["read_transcript_count"]
    ]
    read_overstatements = [
        profile
        for profile in profiles
        if profile["read_transcript_count"]
        < 2
        ** (profile["row"]["nominal_read_bits_per_step"] * profile["row"]["horizon"])
    ]
    write_overstatements = [
        profile
        for profile in profiles
        if profile["write_transcript_count"]
        < 2
        ** (profile["row"]["nominal_write_bits_per_step"] * profile["row"]["horizon"])
    ]
    strict_collapses = [
        profile
        for profile in profiles
        if profile["write_transcript_count"] < profile["read_transcript_count"]
    ]
    return {
        "profiles": profiles,
        "feasible_witness_count": len(profiles),
        "data_processing_violation_count": len(data_processing_violations),
        "strict_write_collapses_count": len(strict_collapses),
        "nominal_read_rate_overstatement_count": len(read_overstatements),
        "nominal_write_rate_overstatement_count": len(write_overstatements),
    }


def action_pool(protocol: dict[str, Any]) -> tuple[Fraction, ...]:
    return tuple(
        sorted(
            {
                F(action)
                for dictionary in protocol["interface"]["action_dictionaries"].values()
                for action in dictionary
            }
        )
    )


def open_loop_feasible(
    protocol: dict[str, Any],
    *,
    horizon: int,
    coupling: str,
    a_z: str,
) -> tuple[bool, tuple[Fraction, ...] | None]:
    """Exhaust the registered action pool over time with no state information."""

    a_n = F(protocol["plant"]["primary_a_n"])
    coupling_value = F(coupling)
    a_z_value = F(a_z)
    disturbances = tuple(F(value) for value in protocol["plant"]["disturbances"])
    for sequence in itertools.product(action_pool(protocol), repeat=horizon):
        belief = initial_states(protocol)
        sequence_safe = True
        for action in sequence:
            future: set[State] = set()
            for state in belief:
                for disturbance in disturbances:
                    next_state = plant_step(
                        state,
                        a_n=a_n,
                        a_z=a_z_value,
                        coupling=coupling_value,
                        action=action,
                        disturbance=disturbance,
                    )
                    if not safe(next_state):
                        sequence_safe = False
                        break
                    future.add(next_state)
                if not sequence_safe:
                    break
            if not sequence_safe:
                break
            belief = frozenset(future)
        if sequence_safe:
            return True, sequence
    return False, None


def zero_port_audit(
    protocol: dict[str, Any], rows: Sequence[dict[str, Any]]
) -> dict[str, Any]:
    """Compare both zero-information cuts with exhaustive open-loop control."""

    lookup = {row_key(row): row for row in rows}
    contexts = sorted({row_context(row) for row in rows})
    max_read = max(int(row["read_bits_per_step"]) for row in rows)
    max_write = max(int(row["write_bits_per_step"]) for row in rows)
    records: list[dict[str, Any]] = []
    for horizon, coupling, a_z in contexts:
        open_loop, sequence = open_loop_feasible(
            protocol,
            horizon=horizon,
            coupling=coupling,
            a_z=a_z,
        )
        read_zero = bool(lookup[(horizon, coupling, a_z, 0, max_write)]["feasible"])
        write_zero = bool(lookup[(horizon, coupling, a_z, max_read, 0)]["feasible"])
        zero_zero = bool(lookup[(horizon, coupling, a_z, 0, 0)]["feasible"])
        records.append(
            {
                "horizon": horizon,
                "coupling": coupling,
                "a_z": a_z,
                "exhaustive_open_loop_feasible": open_loop,
                "open_loop_witness": None
                if sequence is None
                else [ft(action) for action in sequence],
                "raw_r0_wmax_feasible": read_zero,
                "raw_rmax_w0_feasible": write_zero,
                "raw_r0_w0_feasible": zero_zero,
                "raw_zero_port_disagreement": read_zero != write_zero,
                "raw_r0_wmax_mismatches_open_loop": read_zero != open_loop,
                "raw_rmax_w0_mismatches_open_loop": write_zero != open_loop,
                "raw_r0_w0_mismatches_open_loop": zero_zero != open_loop,
            }
        )
    return {
        "records": records,
        "context_count": len(records),
        "raw_zero_port_disagreement_count": sum(
            record["raw_zero_port_disagreement"] for record in records
        ),
        "raw_r0_wmax_open_loop_mismatch_count": sum(
            record["raw_r0_wmax_mismatches_open_loop"] for record in records
        ),
        "raw_rmax_w0_open_loop_mismatch_count": sum(
            record["raw_rmax_w0_mismatches_open_loop"] for record in records
        ),
        "raw_r0_w0_open_loop_mismatch_count": sum(
            record["raw_r0_w0_mismatches_open_loop"] for record in records
        ),
    }


def time_aware_zero_rate_fixture() -> dict[str, Any]:
    """A one-symbol decoder with memory beats every fixed memoryless decoder."""

    controls = (F(-1), F(1))
    scheduled = (F(1), F(-1))
    state = F(0)
    scheduled_states = [state]
    for action in scheduled:
        state += action
        scheduled_states.append(state)
    scheduled_pass = all(F(0) <= value <= F(1) for value in scheduled_states)

    constant_results: dict[str, bool] = {}
    for action in controls:
        state = F(0)
        states = [state]
        for _ in scheduled:
            state += action
            states.append(state)
        constant_results[ft(action)] = all(F(0) <= value <= F(1) for value in states)

    return {
        "plant": "x_(t+1)=x_t+u_t; x_0=0; K={0,1}; U={-1,+1}; T=2",
        "one_symbol_time_aware_action_sequence": [ft(action) for action in scheduled],
        "one_symbol_time_aware_state_sequence": [
            ft(value) for value in scheduled_states
        ],
        "one_symbol_time_aware_pass": scheduled_pass,
        "fixed_memoryless_decoder_results": constant_results,
        "every_fixed_memoryless_decoder_fails": not any(constant_results.values()),
        "read_transcript_count": 1,
        "write_transcript_count": 1,
        "achieved_read_bits_per_step": 0.0,
        "achieved_write_bits_per_step": 0.0,
    }


def run_audit(
    protocol_path: Path = PROTOCOL_PATH,
    result_path: Path = RESULT_PATH,
) -> dict[str, Any]:
    protocol = load_json(protocol_path)
    result = load_json(result_path)
    rows = result.get("grid")
    if not isinstance(rows, list) or not rows:
        raise ValueError("source result must contain a nonempty grid")

    upward = upward_closure_violations(rows)
    nesting = action_dictionary_nesting_violations(protocol)
    profiled = profile_all_witnesses(protocol, rows)
    zero_port = zero_port_audit(protocol, rows)
    fixture = time_aware_zero_rate_fixture()

    load_key = (2, "1/2", "3/2", 2, 2)
    load_row = next(row for row in rows if row_key(row) == load_key)
    load_profile = witness_transcript_profile(protocol, load_row)

    return {
        "schema_version": "asmp4_capacity_definition_audit_v0_1",
        "audit_kind": "development_definition_and_harness_alignment_audit",
        "source": {
            "protocol": str(protocol_path.relative_to(HERE.parent)),
            "protocol_sha256": sha256_file(protocol_path),
            "result": str(result_path.relative_to(HERE.parent)),
            "result_sha256": sha256_file(result_path),
            "source_instrument_status": result.get("instrument_status"),
            "source_runner_gate_pass": result.get("runner_gate_pass"),
        },
        "canonical_lemmas": {
            "deterministic_data_processing": (
                "For each horizon T, the controller induces a function from each "
                "realized read transcript to one write transcript; therefore "
                "|M_w(T)| <= |M_r(T)| and r_w <= r_r."
            ),
            "zero_port_equivalence": (
                "With fixed plant-independent initialization and no charged side "
                "information, either a singleton read-transcript set or a singleton "
                "write-transcript set makes the actuator control sequence open-loop."
            ),
            "budget_upper_set": (
                "Because R_K is defined by achieved_rate <= budget, feasibility at "
                "(R_r,R_w) implies feasibility at every componentwise larger budget."
            ),
        },
        "checks": {
            "source_exact_run_is_internally_valid": {
                "pass": bool(result.get("runner_gate_pass"))
                and result.get("instrument_status") == "valid",
            },
            "raw_grid_is_upward_closed": {
                "pass": not upward,
                "violation_count": len(upward),
                "violations": upward,
            },
            "action_authority_is_nested_across_write_budgets": {
                "pass": not nesting,
                "violation_count": len(nesting),
                "violations": nesting,
            },
            "raw_zero_port_cuts_match": {
                "pass": zero_port["raw_zero_port_disagreement_count"] == 0,
                "disagreement_count": zero_port["raw_zero_port_disagreement_count"],
            },
            "raw_zero_port_cuts_match_exhaustive_open_loop": {
                "pass": (
                    zero_port["raw_r0_wmax_open_loop_mismatch_count"] == 0
                    and zero_port["raw_rmax_w0_open_loop_mismatch_count"] == 0
                ),
                "read_zero_mismatch_count": zero_port[
                    "raw_r0_wmax_open_loop_mismatch_count"
                ],
                "write_zero_mismatch_count": zero_port[
                    "raw_rmax_w0_open_loop_mismatch_count"
                ],
            },
            "reported_witnesses_obey_data_processing": {
                "pass": profiled["data_processing_violation_count"] == 0,
                "witness_count": profiled["feasible_witness_count"],
                "violation_count": profiled["data_processing_violation_count"],
                "strict_write_collapses_count": profiled[
                    "strict_write_collapses_count"
                ],
            },
            "nominal_rates_equal_achieved_transcript_rates": {
                "pass": (
                    profiled["nominal_read_rate_overstatement_count"] == 0
                    and profiled["nominal_write_rate_overstatement_count"] == 0
                ),
                "read_overstatement_count": profiled[
                    "nominal_read_rate_overstatement_count"
                ],
                "write_overstatement_count": profiled[
                    "nominal_write_rate_overstatement_count"
                ],
            },
            "canonical_decoder_memory_fixture": {
                "pass": fixture["one_symbol_time_aware_pass"]
                and fixture["every_fixed_memoryless_decoder_fails"],
                "fixture": fixture,
            },
        },
        "load_bearing_source_cell_achieved_profile": load_profile,
        "zero_port_open_loop_audit": zero_port,
        "decision": {
            "status": "stop_and_repair_problem_definition",
            "reason": (
                "The finite v0.1 run is reproducible within its frozen memoryless "
                "grammar, but its nominal grid is not the canonical achieved-"
                "transcript capacity region. A full ASMP-4 resolution claim is not "
                "well-posed until the rate semantics, actuator authority, decoder "
                "memory, and registered plant class are fixed consistently."
            ),
        },
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=PROTOCOL_PATH)
    parser.add_argument("--result", type=Path, default=RESULT_PATH)
    parser.add_argument("--compact", action="store_true")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    payload = run_audit(args.protocol.resolve(), args.result.resolve())
    print(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":") if args.compact else None,
            indent=None if args.compact else 2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
