"""Same-size dormant-causal-gate adversary for observational metrics.

All conclusions are about finite-state causal identification, not consciousness,
IIT's integrated information Phi, or asymptotic FRC.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import numpy as np

from .benchmark import (
    DEFAULT_DELAY, DEFAULT_LENGTH, DEFAULT_SEED, DEFAULT_TRIALS, NODES,
    effective_dimension, gf2_rank, mean_squared_correlation,
    spectral_peak_fraction,
)

Variant = Literal["plain", "dormant_gate"]
STATUS = "model_free_finite_state_causal_identifiability_only"
GATE_SITE = 15
TARGET_SITE = 7


@dataclass
class GateRegister:
    """16-coordinate GF(2) register with one ordinary-input-unreachable bit.

    For ordinary cue streams u[t] from the zero state, x[15] stays zero.
    The dormant system adds x[15] to x'[7]. Both models have 16 coordinates
    and the exact same full-state passive trace on any binary input stream.
    """

    variant: Variant
    state: np.ndarray = field(default_factory=lambda: np.zeros(NODES, dtype=np.uint8))

    def __post_init__(self) -> None:
        if self.variant not in ("plain", "dormant_gate"):
            raise ValueError("unknown register variant")
        self.state = np.asarray(self.state, dtype=np.uint8).copy()
        if self.state.shape != (NODES,) or np.any(self.state > 1):
            raise ValueError("state must be 16 GF(2) coordinates")

    def step(self, cue: int) -> None:
        if int(cue) not in (0, 1):
            raise ValueError("cue must be binary")
        nxt = np.zeros(NODES, dtype=np.uint8)
        nxt[0] = int(cue)
        nxt[1:15] = self.state[0:14]
        if self.variant == "dormant_gate":
            nxt[TARGET_SITE] ^= self.state[GATE_SITE]
        self.state = nxt

    def intervene(self, *, site: int = GATE_SITE) -> None:
        if not 0 <= site < NODES:
            raise ValueError("intervention site outside state")
        self.state[site] ^= 1

    def predict(self, delay: int = DEFAULT_DELAY) -> int:
        if not 1 <= delay < 15:
            raise ValueError("delay requires 1 <= delay < 15")
        return int(self.state[delay])


def run_trace(variant: Variant, cues: np.ndarray, *, delay: int = DEFAULT_DELAY,
              intervene_at: int | None = None) -> tuple[np.ndarray, np.ndarray]:
    cues = np.asarray(cues)
    if cues.ndim != 1 or np.any((cues != 0) & (cues != 1)):
        raise ValueError("cues must be a one-dimensional binary stream")
    system = GateRegister(variant)
    observations = np.empty((len(cues), NODES), dtype=np.uint8)
    predictions = np.empty(len(cues), dtype=np.uint8)
    for t, cue in enumerate(cues):
        system.step(int(cue))
        if t == intervene_at:
            system.intervene(site=GATE_SITE)
        observations[t] = system.state
        predictions[t] = system.predict(delay)
    return observations, predictions


def linear_map(variant: Variant) -> tuple[np.ndarray, np.ndarray]:
    """Return exact transition A and cue vector B over GF(2)."""
    a = np.empty((NODES, NODES), dtype=np.uint8)
    for j in range(NODES):
        state = np.zeros(NODES, dtype=np.uint8)
        state[j] = 1
        system = GateRegister(variant, state)
        system.step(0)
        a[:, j] = system.state
    system = GateRegister(variant)
    system.step(1)
    b = system.state
    return a, b


def cross_partition_rank(variant: Variant) -> int:
    """Sum of exact directed GF(2) cross-block ranks, never IIT Phi."""
    a, _ = linear_map(variant)
    left, right = np.arange(8), np.arange(8, NODES)
    return gf2_rank(a[np.ix_(left, right)]) + gf2_rank(a[np.ix_(right, left)])


def input_controllability_rank(variant: Variant) -> int:
    """Rank_GF2 [B, AB, ..., A^(15)B] under ordinary binary cues."""
    a, b = linear_map(variant)
    columns = []
    v = b.copy()
    for _ in range(NODES):
        columns.append(v.copy())
        v = (a @ v) % 2
    return gf2_rank(np.column_stack(columns))


def run_adversary(*, seed: int = DEFAULT_SEED, trials: int = DEFAULT_TRIALS,
                  length: int = DEFAULT_LENGTH,
                  delay: int = DEFAULT_DELAY) -> dict:
    if trials < 1 or length < 2 * delay + 12 or not 1 <= delay < 15:
        raise ValueError("invalid experiment parameters")
    attack_time = length // 2
    rows: list[dict] = []
    for trial in range(trials):
        cues = np.random.default_rng(
            np.random.SeedSequence([seed, trial, 710319])
        ).integers(0, 2, length, dtype=np.uint8)
        normal_plain, pred_plain = run_trace("plain", cues, delay=delay)
        normal_gated, pred_gated = run_trace("dormant_gate", cues, delay=delay)
        lesion_plain, lesion_pred_plain = run_trace(
            "plain", cues, delay=delay, intervene_at=attack_time)
        lesion_gated, lesion_pred_gated = run_trace(
            "dormant_gate", cues, delay=delay, intervene_at=attack_time)
        target = cues[:-delay]
        gap = np.abs(lesion_plain.astype(np.int8) - lesion_gated.astype(np.int8))
        spectral_plain = spectral_peak_fraction(normal_plain.astype(float))
        spectral_gated = spectral_peak_fraction(normal_gated.astype(float))
        corr_plain = mean_squared_correlation(normal_plain.astype(float))
        corr_gated = mean_squared_correlation(normal_gated.astype(float))
        dim_plain = effective_dimension(normal_plain.astype(float))
        dim_gated = effective_dimension(normal_gated.astype(float))
        rows.append({
            "trial": trial,
            "passive_full_trace_equal": bool(np.array_equal(normal_plain, normal_gated)),
            "passive_prediction_equal": bool(np.array_equal(pred_plain, pred_gated)),
            "plain_accuracy": float(np.mean(pred_plain[delay:] == target)),
            "gated_accuracy": float(np.mean(pred_gated[delay:] == target)),
            "passive_spectral_peak_abs_delta": abs(spectral_plain - spectral_gated),
            "passive_corr_squared_abs_delta": abs(corr_plain - corr_gated),
            "passive_effective_dimension_abs_delta": abs(dim_plain - dim_gated),
            "post_lesion_lag0_difference": float(gap[attack_time].sum()),
            "post_lesion_lag1_difference": float(gap[attack_time + 1].sum()),
            "post_lesion_lag6_difference": float(gap[attack_time + 6].sum()),
            "post_lesion_lag6_prediction_disagrees": bool(
                lesion_pred_plain[attack_time + 6] !=
                lesion_pred_gated[attack_time + 6]
            ),
            "passive_gate_coordinate_never_active": bool(
                np.all(normal_plain[:, GATE_SITE] == 0)
                and np.all(normal_gated[:, GATE_SITE] == 0)
            ),
        })
    plain_cross = cross_partition_rank("plain")
    gated_cross = cross_partition_rank("dormant_gate")
    plain_cont = input_controllability_rank("plain")
    gated_cont = input_controllability_rank("dormant_gate")
    flags = {
        "complete_observational_equivalence": all(
            r["passive_full_trace_equal"] and r["passive_prediction_equal"]
            for r in rows),
        "ordinary_input_maintains_exact_recall": all(
            r["plain_accuracy"] == 1.0 and r["gated_accuracy"] == 1.0
            for r in rows),
        "spectral_and_correlation_identical": all(
            r["passive_spectral_peak_abs_delta"] == 0.0 and
            r["passive_corr_squared_abs_delta"] == 0.0 and
            r["passive_effective_dimension_abs_delta"] == 0.0
            for r in rows),
        "equal_state_dimensions_but_different_causal_ranks": (
            plain_cross == 1 and gated_cross == 2),
        "gate_unreachable_from_ordinary_input": (
            plain_cont == gated_cont == NODES - 1 and
            all(r["passive_gate_coordinate_never_active"] for r in rows)),
        "intervention_distinguishes_at_lag1": all(
            r["post_lesion_lag0_difference"] == 0 and
            r["post_lesion_lag1_difference"] == 1 for r in rows),
        "intervention_changes_delayed_recall": all(
            r["post_lesion_lag6_difference"] == 1 and
            r["post_lesion_lag6_prediction_disagrees"] for r in rows),
    }
    return {
        "schema": "harmonic_consciousness_dormant_gate_v0.2",
        "status": STATUS,
        "parameters": {"seed": seed, "trials": trials, "length": length,
                       "delay": delay, "nodes": NODES, "attack_time": attack_time,
                       "gate_site": GATE_SITE, "target_site": TARGET_SITE},
        "exact_structure": {
            "cross_partition_rank": {"plain": plain_cross, "dormant_gate": gated_cross},
            "input_controllability_rank": {"plain": plain_cont, "dormant_gate": gated_cont},
            "normal_input_distinguishing_queries": "impossible_within_specified_input_oracle",
            "single_state_intervention_distinguishes": True,
        },
        "metric_scope": {
            "passive_spectra": "finite-trace temporal Fourier summary; no causal identification",
            "cross_partition_rank": "exact GF(2) linear one-step transition rank; NOT IIT Phi",
            "input_controllability_rank": "rank of GF(2) controllability matrix from cue input",
            "intervention": "forced toggle of normally unreachable x15 after update",
            "FRC": "not estimated; no reflective rounds or resource liminf",
            "consciousness": "no ground truth and no subjective-experience inference",
        },
        "diagnostics": flags,
        "trials": rows,
    }
