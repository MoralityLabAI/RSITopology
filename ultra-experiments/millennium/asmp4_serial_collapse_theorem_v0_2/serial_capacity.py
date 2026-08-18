"""Exact finite instruments for the ASMP-4 serial-collapse theorem.

The mathematical theorem is not proved by this file.  This harness exhausts
small finite plants, observation maps, and serial encoder/controller/decoder
codes; it also evaluates the closed-form finite-horizon examples used by the
theorem.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Mapping, Sequence


def F(value: int | str | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(str(value))


def ceil_fraction(value: Fraction) -> int:
    return -(-value.numerator // value.denominator)


@dataclass(frozen=True)
class FinitePlant:
    states: tuple[str, ...]
    initial_states: frozenset[str]
    safe_states: frozenset[str]
    actions: tuple[str, ...]
    disturbances: tuple[str, ...]
    observations: Mapping[str, str]
    transitions: Mapping[tuple[str, str, str], str]

    def __post_init__(self) -> None:
        state_set = frozenset(self.states)
        if not self.initial_states <= state_set:
            raise ValueError("initial states must belong to the state set")
        if not self.safe_states <= state_set:
            raise ValueError("safe states must belong to the state set")
        if not self.initial_states <= self.safe_states:
            raise ValueError("initial states must already be safe")
        if not self.actions or not self.disturbances:
            raise ValueError("actions and disturbances must be nonempty")
        if set(self.observations) != state_set:
            raise ValueError("the observation map must cover every state")
        expected = set(itertools.product(self.states, self.actions, self.disturbances))
        if set(self.transitions) != expected:
            raise ValueError("the transition table must be total")
        if not set(self.transitions.values()) <= state_set:
            raise ValueError("transition targets must belong to the state set")

    def observation(self, state: str) -> str:
        return self.observations[state]

    def step(self, state: str, action: str, disturbance: str) -> str:
        return self.transitions[(state, action, disturbance)]


PathRecord = tuple[str, tuple[str, ...], tuple[str, ...]]


def minimum_action_transcripts(plant: FinitePlant, horizon: int) -> dict[str, Any]:
    """Exact minimum number of realized action words for an observation policy."""

    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    paths: frozenset[PathRecord] = frozenset(
        (state, (plant.observation(state),), ()) for state in plant.initial_states
    )
    visited = 0

    def search(
        step: int, current: frozenset[PathRecord]
    ) -> tuple[int, list[dict[str, str]]] | None:
        nonlocal visited
        visited += 1
        if step == horizon:
            return len({record[2] for record in current}), []

        observation_histories = sorted({record[1] for record in current})
        best: tuple[int, list[dict[str, str]]] | None = None
        for action_vector in itertools.product(
            plant.actions, repeat=len(observation_histories)
        ):
            mapping = dict(zip(observation_histories, action_vector, strict=True))
            future: set[PathRecord] = set()
            valid = True
            for state, observation_history, action_history in current:
                action = mapping[observation_history]
                for disturbance in plant.disturbances:
                    next_state = plant.step(state, action, disturbance)
                    if next_state not in plant.safe_states:
                        valid = False
                        break
                    future.add(
                        (
                            next_state,
                            observation_history + (plant.observation(next_state),),
                            action_history + (action,),
                        )
                    )
                if not valid:
                    break
            if not valid:
                continue
            suffix = search(step + 1, frozenset(future))
            if suffix is None:
                continue
            count, suffix_policy = suffix
            serialized_mapping = {
                "|".join(history): action for history, action in sorted(mapping.items())
            }
            candidate = count, [serialized_mapping, *suffix_policy]
            if best is None or candidate[0] < best[0]:
                best = candidate
        return best

    solved = search(0, paths)
    return {
        "feasible": solved is not None,
        "minimum_action_transcript_count": None if solved is None else solved[0],
        "witness_policy": None if solved is None else solved[1],
        "search_nodes": visited,
    }


def one_step_serial_budget_feasible(
    plant: FinitePlant, read_cap: int, write_cap: int
) -> bool:
    """Exhaust one-step encoder, controller, and actuator maps."""

    if read_cap < 1 or write_cap < 1:
        raise ValueError("transcript caps must be positive")
    initial_observations = sorted(
        {plant.observation(state) for state in plant.initial_states}
    )
    for sensor_vector in itertools.product(
        range(read_cap), repeat=len(initial_observations)
    ):
        sensor = dict(zip(initial_observations, sensor_vector, strict=True))
        for controller_vector in itertools.product(range(write_cap), repeat=read_cap):
            for decoder_vector in itertools.product(plant.actions, repeat=write_cap):
                valid = True
                for state in plant.initial_states:
                    read_symbol = sensor[plant.observation(state)]
                    write_symbol = controller_vector[read_symbol]
                    action = decoder_vector[write_symbol]
                    for disturbance in plant.disturbances:
                        if (
                            plant.step(state, action, disturbance)
                            not in plant.safe_states
                        ):
                            valid = False
                            break
                    if not valid:
                        break
                if valid:
                    return True
    return False


def one_step_transition_plant(
    transition_values: Sequence[str], *, partial_observation: bool
) -> FinitePlant:
    """Build one member of the exhaustive two-safe-state transition census."""

    states = ("L", "R", "BAD")
    actions = ("l", "r")
    disturbance = ("d",)
    keys = tuple(itertools.product(("L", "R"), actions))
    if len(transition_values) != len(keys):
        raise ValueError("four transition values are required")
    transitions: dict[tuple[str, str, str], str] = {
        (state, action, "d"): target
        for (state, action), target in zip(keys, transition_values, strict=True)
    }
    for action in actions:
        transitions[("BAD", action, "d")] = "BAD"
    observations = {
        "L": "safe" if partial_observation else "L",
        "R": "safe" if partial_observation else "R",
        "BAD": "BAD",
    }
    return FinitePlant(
        states=states,
        initial_states=frozenset(("L", "R")),
        safe_states=frozenset(("L", "R")),
        actions=actions,
        disturbances=disturbance,
        observations=observations,
        transitions=transitions,
    )


def exhaustive_one_step_census() -> dict[str, Any]:
    """Verify the diagonal-quadrant formula over every registered tiny plant."""

    plant_count = 0
    budget_cell_count = 0
    mismatch_records: list[dict[str, Any]] = []
    minimum_histogram: dict[str, int] = {"1": 0, "2": 0, "infeasible": 0}
    for transition_values in itertools.product(("L", "R", "BAD"), repeat=4):
        for partial_observation in (False, True):
            plant = one_step_transition_plant(
                transition_values,
                partial_observation=partial_observation,
            )
            plant_count += 1
            central = minimum_action_transcripts(plant, 1)
            minimum = central["minimum_action_transcript_count"]
            minimum_histogram["infeasible" if minimum is None else str(minimum)] += 1
            for read_cap, write_cap in itertools.product((1, 2), repeat=2):
                budget_cell_count += 1
                brute_force = one_step_serial_budget_feasible(
                    plant, read_cap, write_cap
                )
                predicted = (
                    minimum is not None and read_cap >= minimum and write_cap >= minimum
                )
                if brute_force != predicted:
                    mismatch_records.append(
                        {
                            "transition_values": list(transition_values),
                            "partial_observation": partial_observation,
                            "read_cap": read_cap,
                            "write_cap": write_cap,
                            "minimum": minimum,
                            "brute_force": brute_force,
                            "predicted": predicted,
                        }
                    )
    return {
        "plant_observation_pairs": plant_count,
        "budget_cells": budget_cell_count,
        "minimum_transcript_histogram": minimum_histogram,
        "mismatch_count": len(mismatch_records),
        "mismatches": mismatch_records,
        "pass": not mismatch_records,
    }


def mode_switching_plant(*, partial_observation: bool = False) -> FinitePlant:
    """Adversarially switch the live mode after every correct action."""

    states = ("0", "1", "BAD")
    actions = ("0", "1")
    disturbances = ("0", "1")
    transitions: dict[tuple[str, str, str], str] = {}
    for state, action, next_mode in itertools.product(states, actions, disturbances):
        if state == "BAD" or action != state:
            transitions[(state, action, next_mode)] = "BAD"
        else:
            transitions[(state, action, next_mode)] = next_mode
    observations = {
        "0": "mode" if partial_observation else "0",
        "1": "mode" if partial_observation else "1",
        "BAD": "BAD",
    }
    return FinitePlant(
        states=states,
        initial_states=frozenset(("0", "1")),
        safe_states=frozenset(("0", "1")),
        actions=actions,
        disturbances=disturbances,
        observations=observations,
        transitions=transitions,
    )


def actuator_mode_side_information_replay(horizon: int) -> dict[str, Any]:
    """Replay the mode game when the actuator sees the current mode locally."""

    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    plant = mode_switching_plant()
    states = set(plant.initial_states)
    for _ in range(horizon):
        future: set[str] = set()
        for state in states:
            local_action = state
            for disturbance in plant.disturbances:
                next_state = plant.step(state, local_action, disturbance)
                if next_state not in plant.safe_states:
                    return {
                        "safe": False,
                        "write_transcript_count": 1,
                    }
                future.add(next_state)
        states = future
    return {
        "safe": True,
        "write_transcript_count": 1,
    }


def uncertainty_timing_plant() -> FinitePlant:
    """The unseen current disturbance must be guessed before it is applied."""

    states = ("S", "BAD")
    actions = ("0", "1")
    disturbances = ("0", "1")
    transitions: dict[tuple[str, str, str], str] = {}
    for state, action, disturbance in itertools.product(states, actions, disturbances):
        transitions[(state, action, disturbance)] = (
            "S" if state == "S" and action == disturbance else "BAD"
        )
    return FinitePlant(
        states=states,
        initial_states=frozenset(("S",)),
        safe_states=frozenset(("S",)),
        actions=actions,
        disturbances=disturbances,
        observations={"S": "S", "BAD": "BAD"},
        transitions=transitions,
    )


def restricted_authority_plant() -> FinitePlant:
    """A fully observed two-mode plant with only one required action available."""

    return FinitePlant(
        states=("0", "1", "BAD"),
        initial_states=frozenset(("0", "1")),
        safe_states=frozenset(("0", "1")),
        actions=("0",),
        disturbances=("hold",),
        observations={"0": "0", "1": "1", "BAD": "BAD"},
        transitions={
            ("0", "0", "hold"): "0",
            ("1", "0", "hold"): "BAD",
            ("BAD", "0", "hold"): "BAD",
        },
    )


def one_shot_event_plant() -> FinitePlant:
    """Full-observation game whose safe control language is a binary comb."""

    states = ("WAIT", "EVENT", "DONE", "BAD")
    actions = ("0", "1")
    disturbances = ("WAIT", "EVENT")
    transitions: dict[tuple[str, str, str], str] = {}
    for state, action, disturbance in itertools.product(states, actions, disturbances):
        if state == "WAIT" and action == "0":
            target = disturbance
        elif state == "EVENT" and action == "1":
            target = "DONE"
        elif state == "DONE" and action == "0":
            target = "DONE"
        else:
            target = "BAD"
        transitions[(state, action, disturbance)] = target
    return FinitePlant(
        states=states,
        initial_states=frozenset(("WAIT", "EVENT")),
        safe_states=frozenset(("WAIT", "EVENT", "DONE")),
        actions=actions,
        disturbances=disturbances,
        observations={state: state for state in states},
        transitions=transitions,
    )


def comb_transcript_language(horizon: int) -> tuple[tuple[str, ...], ...]:
    """Words with at most one event symbol, followed by deterministic zeros."""

    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    words = [("0",) * horizon]
    words.extend(
        ("0",) * event_time + ("1",) + ("0",) * (horizon - event_time - 1)
        for event_time in range(horizon)
    )
    return tuple(sorted(words))


def transcript_tree_metrics(
    words: Sequence[Sequence[str]],
) -> dict[str, int | float | bool]:
    """Compare terminal-language and worst-path causal-branching costs."""

    normalized = tuple(tuple(word) for word in words)
    if not normalized:
        raise ValueError("the transcript language must be nonempty")
    if len(set(normalized)) != len(normalized):
        raise ValueError("the transcript language must not contain duplicates")
    horizons = {len(word) for word in normalized}
    if len(horizons) != 1:
        raise ValueError("all transcript words must have one common horizon")
    horizon = horizons.pop()
    worst_product = 1
    for word in normalized:
        product = 1
        for event in range(horizon):
            prefix = word[:event]
            successors = {
                candidate[event]
                for candidate in normalized
                if candidate[:event] == prefix
            }
            product *= len(successors)
        worst_product = max(worst_product, product)
    language_count = len(normalized)
    return {
        "horizon": horizon,
        "language_count": language_count,
        "branching_product": worst_product,
        "language_bits": math.log2(language_count),
        "branching_bits": math.log2(worst_product),
        "branching_dominates_language": worst_product >= language_count,
    }


def causal_metric_gap_report(max_horizon: int = 8) -> dict[str, Any]:
    """Exact comb-game separation of language growth and causal branching."""

    if max_horizon < 1:
        raise ValueError("max_horizon must be positive")
    plant = one_shot_event_plant()
    rows = []
    for horizon in range(1, max_horizon + 1):
        minimum = minimum_action_transcripts(plant, horizon)
        metrics = transcript_tree_metrics(comb_transcript_language(horizon))
        rows.append(
            {
                "horizon": horizon,
                "solver_minimum": minimum["minimum_action_transcript_count"],
                **metrics,
            }
        )
    return {
        "rows": rows,
        "pass": all(
            row["solver_minimum"] == row["horizon"] + 1
            and row["language_count"] == row["horizon"] + 1
            and row["branching_product"] == 2 ** row["horizon"]
            and row["branching_dominates_language"]
            for row in rows
        ),
    }


def scalar_exact_transcript_count(
    expansion: Fraction | str | int,
    initial_half_width: Fraction | str | int,
    safe_half_width: Fraction | str | int,
    horizon: int,
) -> int:
    """Exact scalar covering number for x+=a*x+u with unrestricted control."""

    a = abs(F(expansion))
    delta = F(initial_half_width)
    limit = F(safe_half_width)
    if a <= 0 or delta <= 0 or limit <= 0:
        raise ValueError("expansion and widths must be positive")
    if delta > limit:
        raise ValueError("the initial interval must lie inside the safe interval")
    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    return max(1, ceil_fraction((a**horizon) * delta / limit))


def scalar_exact_rate(
    expansion: Fraction | str | int,
    initial_half_width: Fraction | str | int,
    safe_half_width: Fraction | str | int,
    horizon: int,
) -> float:
    if horizon == 0:
        return 0.0
    return (
        math.log2(
            scalar_exact_transcript_count(
                expansion, initial_half_width, safe_half_width, horizon
            )
        )
        / horizon
    )


def diagonal_box_exact_transcript_count(
    expansions: Sequence[Fraction | str | int],
    initial_half_widths: Sequence[Fraction | str | int],
    safe_half_widths: Sequence[Fraction | str | int],
    horizon: int,
) -> int:
    if not (len(expansions) == len(initial_half_widths) == len(safe_half_widths)):
        raise ValueError("expansions and widths must have equal dimensions")
    result = 1
    for expansion, initial, safe_limit in zip(
        expansions, initial_half_widths, safe_half_widths, strict=True
    ):
        result *= scalar_exact_transcript_count(expansion, initial, safe_limit, horizon)
    return result


def shear_exact_transcript_count(
    tangent_half_width: Fraction | str | int,
    safe_normal_half_width: Fraction | str | int,
    horizon: int,
) -> int:
    """Exact count for n+=n+z+u, z+=z, n0=0, |z0|<=delta."""

    delta = F(tangent_half_width)
    limit = F(safe_normal_half_width)
    if delta <= 0 or limit <= 0 or horizon < 0:
        raise ValueError("widths must be positive and horizon nonnegative")
    return max(1, ceil_fraction(F(horizon) * delta / limit))


def fixed_fifo_delay_relay_report(
    max_delay: int = 3, max_horizon: int = 5
) -> dict[str, Any]:
    """Exhaust a binary parity controller and its deadline-shifted relay."""

    if max_delay < 0 or max_horizon < 0:
        raise ValueError("delay and horizon bounds must be nonnegative")
    rows: list[dict[str, Any]] = []
    for delay in range(max_delay + 1):
        for horizon in range(max_horizon + 1):
            emission_count = max(0, horizon - delay)
            original_write_words: set[tuple[int, ...]] = set()
            relayed_read_words: set[tuple[int, ...]] = set()
            relayed_write_words: set[tuple[int, ...]] = set()
            for emissions in itertools.product((0, 1), repeat=emission_count):
                original_write: list[int] = []
                relayed_read: list[int] = []
                parity = 0
                for event in range(horizon):
                    if event >= delay:
                        parity ^= emissions[event - delay]
                    original_write.append(parity)
                    # At emission s, the sensor can compute this parity for
                    # delivery event s+delay.  Before the first delivery the
                    # relay emits the same plant-independent zero prefix.
                    relayed_read.append(parity)
                original_word = tuple(original_write)
                relayed_word = tuple(relayed_read)
                original_write_words.add(original_word)
                relayed_read_words.add(relayed_word)
                relayed_write_words.add(relayed_word)
            expected = 2**emission_count
            rows.append(
                {
                    "delay": delay,
                    "horizon": horizon,
                    "expected_count": expected,
                    "original_write_count": len(original_write_words),
                    "relayed_read_count": len(relayed_read_words),
                    "relayed_write_count": len(relayed_write_words),
                    "languages_match": (
                        original_write_words
                        == relayed_read_words
                        == relayed_write_words
                    ),
                }
            )
    return {
        "rows": rows,
        "pass": all(
            row["languages_match"]
            and row["original_write_count"] == row["expected_count"]
            and row["relayed_read_count"] == row["expected_count"]
            and row["relayed_write_count"] == row["expected_count"]
            for row in rows
        ),
    }


def boundary_fixture_report(max_horizon: int = 4) -> dict[str, Any]:
    full_mode = mode_switching_plant()
    partial_mode = mode_switching_plant(partial_observation=True)
    mode_rows = []
    for horizon in range(1, max_horizon + 1):
        full = minimum_action_transcripts(full_mode, horizon)
        partial = minimum_action_transcripts(partial_mode, horizon)
        actuator_side_information = actuator_mode_side_information_replay(horizon)
        mode_rows.append(
            {
                "horizon": horizon,
                "full_observation_minimum": full["minimum_action_transcript_count"],
                "partial_observation_feasible": partial["feasible"],
                "actuator_mode_side_information_safe": actuator_side_information[
                    "safe"
                ],
                "actuator_mode_side_information_minimum": actuator_side_information[
                    "write_transcript_count"
                ],
            }
        )
    uncertainty = minimum_action_transcripts(uncertainty_timing_plant(), 1)
    restricted_authority = minimum_action_transcripts(restricted_authority_plant(), 1)
    scalar_rows = [
        {
            "horizon": horizon,
            "unstable_count": scalar_exact_transcript_count(
                F(2), F("1/4"), F(1), horizon
            ),
            "stable_count": scalar_exact_transcript_count(
                F("4/5"), F(1), F(1), horizon
            ),
            "shear_count": shear_exact_transcript_count(F("1/2"), F(1), horizon),
        }
        for horizon in range(1, max_horizon + 1)
    ]
    return {
        "mode_switching": mode_rows,
        "unseen_current_disturbance_feasible": uncertainty["feasible"],
        "full_authority_one_step_feasible": mode_rows[0]["full_observation_minimum"]
        == 2,
        "restricted_authority_one_step_feasible": restricted_authority["feasible"],
        "scalar_and_nonhyperbolic": scalar_rows,
    }


def verification_payload() -> dict[str, Any]:
    census = exhaustive_one_step_census()
    boundaries = boundary_fixture_report()
    delay_relay = fixed_fifo_delay_relay_report()
    causal_metric_gap = causal_metric_gap_report()
    diagonal_counts = [
        {
            "horizon": horizon,
            "count": diagonal_box_exact_transcript_count(
                (2, 3, "1/2"),
                ("1/4", "1/9", 1),
                (1, 1, 1),
                horizon,
            ),
        }
        for horizon in range(1, 5)
    ]
    gates = {
        "G0_exhaustive_serial_census": census["pass"]
        and census["plant_observation_pairs"] == 162
        and census["budget_cells"] == 648,
        "G1_mode_switching_exact_growth": all(
            row["full_observation_minimum"] == 2 ** row["horizon"]
            for row in boundaries["mode_switching"]
        ),
        "G2_partial_observation_kill": all(
            not row["partial_observation_feasible"]
            for row in boundaries["mode_switching"]
        ),
        "G3_side_information_collapse": all(
            row["actuator_mode_side_information_safe"]
            and row["actuator_mode_side_information_minimum"] == 1
            for row in boundaries["mode_switching"]
        ),
        "G4_uncertainty_timing_kill": not boundaries[
            "unseen_current_disturbance_feasible"
        ],
        "G5_exact_finite_horizon_margin": [
            row["unstable_count"] for row in boundaries["scalar_and_nonhyperbolic"]
        ]
        == [1, 1, 2, 4],
        "G6_stable_zero_rate": all(
            row["stable_count"] == 1 for row in boundaries["scalar_and_nonhyperbolic"]
        ),
        "G7_nonhyperbolic_polynomial_growth": [
            row["shear_count"] for row in boundaries["scalar_and_nonhyperbolic"]
        ]
        == [1, 1, 2, 2],
        "G8_diagonal_positive_exponent_recovery": [
            row["count"] for row in diagonal_counts
        ]
        == [1, 1, 6, 36],
        "G9_authority_control": boundaries["full_authority_one_step_feasible"]
        and not boundaries["restricted_authority_one_step_feasible"],
        "G10_fixed_fifo_delay_relay": delay_relay["pass"],
        "G11_causal_metric_gap": causal_metric_gap["pass"],
    }
    return {
        "schema_version": "asmp4_serial_collapse_verification_v0_2",
        "theorem_scope": (
            "Deterministic noiseless serial sensor-controller-actuator codes "
            "with realized transcript cardinality, plant-independent "
            "initialization, timing-compatible zero or fixed FIFO delay, and "
            "no controller or actuator side information."
        ),
        "census": census,
        "boundary_fixtures": boundaries,
        "fixed_fifo_delay_relay": delay_relay,
        "causal_metric_gap": causal_metric_gap,
        "diagonal_box_counts": diagonal_counts,
        "gates": gates,
        "pass": all(gates.values()),
    }
