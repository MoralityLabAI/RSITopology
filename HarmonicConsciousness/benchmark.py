"""CPU-only adversarial toy benchmarks for resonance and causal proxy metrics.

These measures are engineering observations, not IIT Phi, FRC, or consciousness.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

import numpy as np

Kind = Literal[
    "xor_grid", "xor_grid_cut", "phase_locked", "phase_free",
    "delay_register", "delay_register_cut",
]
KINDS: tuple[Kind, ...] = (
    "xor_grid", "xor_grid_cut", "phase_locked", "phase_free",
    "delay_register", "delay_register_cut",
)
STATUS = "synthetic_toy_no_consciousness_claim"
NODES = 16
WARMUP = 128
DEFAULT_LENGTH = 256
DEFAULT_DELAY = 12
DEFAULT_TRIALS = 24
DEFAULT_SEED = 20261027


def _neighbors(side: int) -> list[tuple[int, ...]]:
    return [tuple(sorted({
        ((row - 1) % side) * side + col,
        ((row + 1) % side) * side + col,
        row * side + (col - 1) % side,
        row * side + (col + 1) % side,
    })) for row in range(side) for col in range(side)]


@dataclass
class ToySystem:
    kind: Kind
    seed: int
    nodes: int = NODES

    def __post_init__(self) -> None:
        side = math.isqrt(self.nodes)
        if side * side != self.nodes or side < 4 or side % 2:
            raise ValueError("nodes must form an even-sided square grid (side >= 4)")
        self.neighbors = _neighbors(side)
        self.partition = np.array([(idx % side) < side // 2 for idx in range(self.nodes)])
        self.is_phase = self.kind in ("phase_locked", "phase_free")
        if self.is_phase:
            rng = np.random.default_rng(self.seed)
            self.phase = rng.uniform(-math.pi, math.pi, size=self.nodes)
            self.omega = .8 + .03 * np.linspace(-1., 1., self.nodes)
            for _ in range(WARMUP):
                self.step(0, warmup=True)
        else:
            self.bits = np.zeros(self.nodes, dtype=np.uint8)

    def step(self, cue: int, *, warmup: bool = False) -> None:
        if cue not in (0, 1):
            raise ValueError("cue must be 0 or 1")
        if self.kind.startswith("xor_grid"):
            # Two invertible XOR shears. Each updates one checkerboard color
            # from the other; their composition is reversible for fixed cue.
            side = math.isqrt(self.nodes)
            cut = self.kind.endswith("_cut")
            for parity in (0, 1):
                for vertex in range(self.nodes):
                    if ((vertex // side) + (vertex % side)) % 2 != parity:
                        continue
                    src = [j for j in self.neighbors[vertex]
                           if not cut or self.partition[j] == self.partition[vertex]]
                    if src:
                        self.bits[vertex] ^= np.bitwise_xor.reduce(self.bits[src])
            self.bits[0] ^= cue
        elif self.kind.startswith("delay_register"):
            updated = np.empty_like(self.bits)
            updated[0] = cue
            updated[1:] = self.bits[:-1]
            if self.kind.endswith("_cut"):
                updated[self.nodes // 2] = 0
            self.bits = updated
        elif self.is_phase:
            coupling = 2.5 if self.kind == "phase_locked" else 0.
            difference = self.phase[None, :] - self.phase[:, None]
            self.phase = (self.phase + .07 * (
                self.omega + (coupling / self.nodes) * np.sin(difference).sum(axis=1)
            )) % (2 * math.pi)
            if not warmup:
                self.phase[0] = (self.phase[0] + .025 * (2 * cue - 1)) % (2 * math.pi)
        else:
            raise ValueError(f"unknown system kind: {self.kind}")

    def perturb(self, index: int = 0) -> None:
        if not 0 <= index < self.nodes:
            raise ValueError("invalid intervention site")
        if self.is_phase:
            self.phase[index] = (self.phase[index] + math.pi / 2) % (2 * math.pi)
        else:
            self.bits[index] ^= 1

    def observe(self) -> np.ndarray:
        return np.cos(self.phase) if self.is_phase else self.bits.astype(float)

    def phase_order(self) -> float | None:
        return float(abs(np.exp(1j * self.phase).mean())) if self.is_phase else None

    def predict(self, delay: int) -> int:
        if not 1 <= delay < self.nodes:
            raise ValueError("delay must lie in [1, nodes)")
        if self.is_phase:
            return int(np.cos(self.phase[delay]) > 0)
        return int(self.bits[delay])


def simulate(kind: Kind, cues: np.ndarray, seed: int, delay: int,
             perturb_at: int | None = None) -> dict[str, np.ndarray]:
    if cues.ndim != 1 or np.any((cues != 0) & (cues != 1)):
        raise ValueError("cues must be a one-dimensional binary sequence")
    system = ToySystem(kind=kind, seed=seed)
    observations = np.empty((len(cues), system.nodes), dtype=float)
    predictions = np.empty(len(cues), dtype=np.uint8)
    orders = np.empty(len(cues), dtype=float) if system.is_phase else None
    for t, cue in enumerate(cues):
        system.step(int(cue))
        if perturb_at == t:
            system.perturb()
        observations[t] = system.observe()
        predictions[t] = system.predict(delay)
        if orders is not None:
            orders[t] = system.phase_order()
    return {"observations": observations, "predictions": predictions,
            "phase_order": orders}


def spectral_peak_fraction(signals: np.ndarray) -> float:
    """Max non-DC temporal Fourier-bin energy / total non-DC energy.

    Pooling power across channels destroys relative phase information. This
    metric is *intentionally* vulnerable to the phase-surrogate control.
    """
    if signals.ndim != 2 or signals.shape[0] < 4:
        raise ValueError("expected matrix with >= 4 time samples")
    centered = signals - signals.mean(axis=0, keepdims=True)
    power = (abs(np.fft.rfft(centered, axis=0)) ** 2).sum(axis=1)
    power[0] = 0.
    total = float(power.sum())
    return float(power.max() / total) if total > 1.e-20 else 0.


def mean_squared_correlation(signals: np.ndarray) -> float:
    """Zero-lag squared cross-channel correlation, excluding constant channels."""
    if signals.ndim != 2 or signals.shape[0] < 4:
        raise ValueError("expected matrix with >= 4 time samples")
    centered = signals - signals.mean(axis=0, keepdims=True)
    norms = np.linalg.norm(centered, axis=0)
    active = norms > 1.e-10
    if active.sum() < 2:
        return 0.
    normalized = centered[:, active] / norms[active]
    corr = normalized.T @ normalized
    i, j = np.triu_indices(corr.shape[0], 1)
    return float(np.mean(corr[i, j] ** 2))


def effective_dimension(signals: np.ndarray) -> float:
    """Participation ratio of the sample covariance eigenvalues, [1, nodes]."""
    if signals.ndim != 2 or signals.shape[0] < 4:
        raise ValueError("expected matrix with >= 4 time samples")
    z = signals - signals.mean(axis=0, keepdims=True)
    eigen = np.maximum(np.linalg.eigvalsh(z.T @ z), 0.)
    total = float(eigen.sum())
    return float(total ** 2 / np.sum(eigen ** 2)) if total > 1.e-20 else 0.


def channel_roll_surrogate(signals: np.ndarray, seed: int) -> np.ndarray:
    """Independent circular time shifts exactly preserve each channel's FFT PSD."""
    if signals.ndim != 2:
        raise ValueError("signals must be a matrix")
    rng = np.random.default_rng(seed)
    shifts = rng.integers(0, signals.shape[0], size=signals.shape[1])
    shifts[0] = 0
    return np.column_stack([np.roll(signals[:, i], int(shifts[i]))
                            for i in range(signals.shape[1])])


def probe_budget_to_find_failure(error_counts: list[int],
                                 opportunities: int, delta: float = .05) -> int | None:
    """Smallest random-without-replacement probe count with mean miss <= delta.

    Uses exact finite hypergeometric miss probabilities over the specified
    trials. None means this bound cannot falsify all sampled trajectories.
    Not a verification certificate, model of reflection, or measured FRC.
    """
    if opportunities < 1 or not 0 < delta < 1:
        raise ValueError("invalid audit parameters")
    if not error_counts or any(e < 0 or e > opportunities for e in error_counts):
        raise ValueError("invalid error counts")
    pmiss = np.ones(len(error_counts), dtype=float)
    for q in range(opportunities + 1):
        if float(pmiss.mean()) <= delta:
            return q
        if q == opportunities:
            break
        for i, errors in enumerate(error_counts):
            # C(m-e, q+1)/C(m, q+1) = previous * (m-e-q)/(m-q)
            pmiss[i] *= max(opportunities - errors - q, 0) / (opportunities - q)
    return None



def gf2_rank(matrix: np.ndarray) -> int:
    """Exact Gaussian-elimination rank of a binary matrix over GF(2)."""
    a = np.asarray(matrix)
    if a.ndim != 2 or np.any((a != 0) & (a != 1)):
        raise ValueError("matrix must be binary and two-dimensional")
    a = a.astype(np.uint8, copy=True)
    m, n = a.shape
    pivot_row = 0
    for col in range(n):
        hits = np.flatnonzero(a[pivot_row:, col])
        if len(hits) == 0:
            continue
        selected = pivot_row + int(hits[0])
        a[[pivot_row, selected]] = a[[selected, pivot_row]]
        for other in range(m):
            if other != pivot_row and a[other, col]:
                a[other] ^= a[pivot_row]
        pivot_row += 1
        if pivot_row == m:
            break
    return pivot_row


def binary_transition_matrix(kind: Kind) -> np.ndarray:
    """Extract exact one-step GF(2) map from basis interventions at cue=0."""
    if kind.startswith("phase_"):
        raise ValueError("phase oscillators are not GF(2)-linear")
    out = np.zeros((NODES, NODES), dtype=np.uint8)
    for j in range(NODES):
        system = ToySystem(kind=kind, seed=0)
        system.bits[j] = 1
        system.step(0)
        out[:, j] = system.bits
    return out


def partition_cross_rank(kind: Kind) -> int | None:
    """Rank(A_AB)+rank(A_BA), a structural dependence proxy, NOT IIT Phi.

    Grid bipartition is left/right spatial columns. Shift-register bipartition
    follows contiguous memory positions. Both are fixed independently of data.
    """
    if kind.startswith("phase_"):
        return None
    system = ToySystem(kind=kind, seed=0)
    partition = (system.partition if kind.startswith("xor_") else
                 np.arange(NODES) < NODES // 2)
    a = np.flatnonzero(partition)
    b = np.flatnonzero(~partition)
    mat = binary_transition_matrix(kind)
    return gf2_rank(mat[np.ix_(a, b)]) + gf2_rank(mat[np.ix_(b, a)])


def _cues(seed: int, trial: int, length: int) -> np.ndarray:
    return np.random.default_rng(np.random.SeedSequence([seed, trial, 710319])).integers(
        0, 2, length, dtype=np.uint8)


def _mean(rows: list[dict], key: str) -> float:
    return float(np.mean([row[key] for row in rows]))


def run_benchmark(*, seed: int = DEFAULT_SEED,
                  trials: int = DEFAULT_TRIALS,
                  length: int = DEFAULT_LENGTH,
                  delay: int = DEFAULT_DELAY) -> dict:
    if trials < 1 or length < 2 * delay + 10 or not 1 <= delay < NODES:
        raise ValueError("invalid run parameters")
    rows: list[dict] = []
    for trial in range(trials):
        cues = _cues(seed, trial, length)
        target = cues[:length - delay]
        majority = float(max(target.mean(), 1. - target.mean()))
        for kind in KINDS:
            system_seed = seed + 9001 + trial
            base = simulate(kind, cues, system_seed, delay)
            twin = simulate(kind, cues, system_seed, delay, perturb_at=length // 2)
            signals = base["observations"]
            predictions = base["predictions"][delay:]
            violations = int(np.count_nonzero(predictions != target))
            surrogate = channel_roll_surrogate(signals, seed + trial + 800000)
            lag_scores = {}
            for lag in (1, 4, 8):
                t = length // 2 + lag
                lag_scores[f"response_lag{lag}"] = float(
                    np.mean(abs(signals[t] - twin["observations"][t])))
            rows.append({
                "kind": kind, "trial": trial, "accuracy": float(1 - violations / len(target)),
                "majority_accuracy": majority, "errors": violations,
                "spectral_peak_fraction": spectral_peak_fraction(signals),
                "mean_squared_corr": mean_squared_correlation(signals),
                "effective_dimension": effective_dimension(signals),
                "phase_order_mean": float(base["phase_order"].mean()) if
                base["phase_order"] is not None else None,
                "surrogate_peak_delta": abs(spectral_peak_fraction(signals) -
                                            spectral_peak_fraction(surrogate)),
                "surrogate_corr_drop": mean_squared_correlation(signals) -
                                       mean_squared_correlation(surrogate),
                **lag_scores,
            })

    summary = {}
    for kind in KINDS:
        group = [row for row in rows if row["kind"] == kind]
        summary[kind] = {
            "mean_accuracy": _mean(group, "accuracy"),
            "mean_oracle_majority": _mean(group, "majority_accuracy"),
            "mean_gain_over_majority": float(np.mean([
                row["accuracy"] - row["majority_accuracy"] for row in group])),
            "mean_peak": _mean(group, "spectral_peak_fraction"),
            "mean_corr2": _mean(group, "mean_squared_corr"),
            "mean_effective_dimension": _mean(group, "effective_dimension"),
            "mean_phase_order": _mean(group, "phase_order_mean") if
            group[0]["phase_order_mean"] is not None else None,
            "mean_response_lag1": _mean(group, "response_lag1"),
            "mean_response_lag4": _mean(group, "response_lag4"),
            "mean_response_lag8": _mean(group, "response_lag8"),
            "gf2_cross_partition_rank": partition_cross_rank(kind),
            "max_surrogate_peak_delta": float(max(r["surrogate_peak_delta"] for r in group)),
            "mean_surrogate_corr_drop": _mean(group, "surrogate_corr_drop"),
            "q95_falsification_probes": probe_budget_to_find_failure(
                [row["errors"] for row in group], length - delay),
        }

    flags = {
        "locked_phase_high_order_low_task_gain": (
            summary["phase_locked"]["mean_phase_order"] >= .90 and
            summary["phase_locked"]["mean_gain_over_majority"] <= .10),
        "xor_structural_coupling_without_task_gain": (
            summary["xor_grid"]["gf2_cross_partition_rank"] >= 2 and
            summary["xor_grid_cut"]["gf2_cross_partition_rank"] == 0 and
            summary["xor_grid"]["mean_gain_over_majority"] <= .10),
        "xor_lag8_spread_at_least_tenth": (
            summary["xor_grid"]["mean_response_lag8"] >= .10),
        "memory_cut_degrades_task": (
            summary["delay_register"]["mean_accuracy"] == 1. and
            summary["delay_register_cut"]["mean_accuracy"] <= .65),
        "channel_psd_surrogate_same_peak_lower_corr": (
            summary["phase_locked"]["max_surrogate_peak_delta"] < 1.e-12 and
            summary["phase_locked"]["mean_surrogate_corr_drop"] > .15),
    }
    return {
        "schema": "harmonic_consciousness_adversarial_v0.1",
        "status": STATUS,
        "parameters": {"seed": seed, "trials": trials, "length": length,
                       "delay": delay, "nodes": NODES, "phase_warmup": WARMUP,
                       "probing_delta": .05},
        "metric_scope": {
            "spectral_peak_fraction": "temporal Fourier power concentration; ignores interchannel phase",
            "mean_corr2": "squared zero-lag cross-channel correlations; not causal",
            "effective_dimension": "covariance eigenvalue participation ratio; not consciousness",
            "phase_order": "Kuramoto order parameter, only meaningful for oscillator families",
            "gf2_cross_partition_rank": "rank_GF2(A_AB)+rank_GF2(A_BA) for frozen bipartition; NOT IIT Phi",
            "response_lag8": "mean absolute output-state contrast under one-node intervention; units depend on family",
            "q95_falsification_probes": "finite empirical random audit cost to find task failure; null is unfalsified in this test, not certified",
            "phi": "not computed; the XOR lattice is inspired by criticism of IIT, not an IIT instantiation",
            "FRC": "not estimated; no reflective sequence or infinite-depth lim-inf inference",
        },
        "protocol_flags": flags,
        "summary": summary,
        "trials": rows,
    }
