"""HRC-FRC-01: spectral evaluation design and a synthetic resonance trap.

A model-free experiment.  'Spectral query' means access to a measured modal
coefficient (a richer channel than EvalMath's equality-trigger oracle).
A designer can choose a band from a REGISTERED Laplacian, a certified global
roughness bound, and a target upper error; it cannot read the held-out true
error vector to choose a band. Only the readout harness reads that vector.

This is classical finite-dimensional functional analysis. It does not test
subjective consciousness, authorize weight edits, or prove continuum local
smoothing. All quantities in this module are approximate float64 diagnostics.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import numpy as np


@dataclass(frozen=True)
class Geometry:
    """Eigengap-safe full-eigenspace spectral projector."""
    eigenvalues: np.ndarray
    basis: np.ndarray
    projector: np.ndarray
    rank: int
    next_eigenvalue: float | None
    cutoff: float
    operator_sha256: str


def _spectrum(operator: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x = np.asarray(operator, dtype=float)
    if x.ndim != 2 or x.shape[0] != x.shape[1] or not x.size:
        raise ValueError("operator must be a nonempty square matrix")
    if not np.all(np.isfinite(x)) or not np.allclose(x, x.T, atol=1e-10):
        raise ValueError("operator must be finite symmetric")
    vals, vecs = np.linalg.eigh((x + x.T) / 2)
    if np.min(vals) < -1e-9:
        raise ValueError("registered operator must be positive semidefinite")
    vals = np.maximum(vals, 0)
    return vals, vecs


def _bands(vals: np.ndarray) -> tuple[int, ...]:
    """Allowed spectral ranks, including all exactly/approximately degenerate eigenspaces."""
    n = len(vals)
    ends = []
    for j in range(n):
        if j == n - 1 or not np.isclose(vals[j], vals[j+1], atol=1e-9, rtol=1e-9):
            ends.append(j+1)
    return tuple(ends)


def spectral_projector(operator: np.ndarray, rank: int) -> Geometry:
    """Only accept band endpoints that include each eigenvalue's FULL multiplicity."""
    vals, vecs = _spectrum(operator)
    if type(rank) is not int or rank not in _bands(vals):
        raise ValueError("rank must end at a complete eigenspace")
    projection = vecs[:, :rank] @ vecs[:, :rank].T
    next_val = None if rank == len(vals) else float(vals[rank])
    fingerprint = sha256(np.asarray(operator, dtype=np.float64).tobytes()).hexdigest()
    return Geometry(vals, vecs, projection, rank, next_val, float(vals[rank-1]), fingerprint)


def tail_upper_bound(roughness_budget: float, next_eigenvalue: float | None,
                     order: float = 1.0) -> float:
    """||tail||^2 <= <e,L^s e> / lambda_next^s, or 0 for a full band."""
    b = float(roughness_budget)
    s = float(order)
    if not np.isfinite(b) or b < 0 or not np.isfinite(s) or s <= 0:
        raise ValueError("roughness budget must be nonnegative, order positive")
    if next_eigenvalue is None:
        return 0.0
    if next_eigenvalue <= 0:
        return float("inf") if b > 0 else 0.0
    return b / next_eigenvalue ** s


def choose_certified_band(operator: np.ndarray, roughness_budget: float,
                          tolerance: float, order: float = 1.0) -> Geometry:
    """Target-blind minimization of modal-query count subject to tail bound.

    This selector cannot see the target residual. It uses registered geometry,
    a fixed external bound on its spectral roughness, and an error tolerance.
    """
    tol = float(tolerance)
    if not np.isfinite(tol) or tol < 0:
        raise ValueError("tolerance must be nonnegative finite")
    vals, _ = _spectrum(operator)
    for rank in _bands(vals):
        g = spectral_projector(operator, rank)
        if tail_upper_bound(roughness_budget, g.next_eigenvalue, order) <= tol:
            return g
    raise AssertionError("the full band has zero unobserved tail")


def spectral_error_receipt(operator: np.ndarray, error: np.ndarray,
                           band: Geometry, roughness_budget: float,
                           order: float = 1.0) -> dict[str, float | bool]:
    """External audit of a *preselected* band. Never use this for selection."""
    e = np.asarray(error, dtype=float)
    vals, vecs = _spectrum(operator)
    if e.shape != (len(vals),) or not np.all(np.isfinite(e)):
        raise ValueError("error vector must have registered shape and finite values")
    # Guard against substituting an unrelated operator after band selection.
    fingerprint = sha256(np.asarray(operator, dtype=np.float64).tobytes()).hexdigest()
    if fingerprint != band.operator_sha256:
        raise ValueError("band is bound to a different registered operator")
    if not np.allclose(vals, band.eigenvalues, atol=1e-9):
        raise ValueError("band eigenspectrum differs from audited operator")
    if band.projector.shape != (len(vals), len(vals)) or not np.allclose(
        band.projector, vecs[:, :band.rank] @ vecs[:, :band.rank].T, atol=1e-9
    ):
        raise ValueError("band projector does not match registered eigenspaces")
    coords = vecs.T @ e
    roughness = float(np.sum((vals ** float(order)) * coords**2))
    projected = band.projector @ e
    tail = e - projected
    observed = float(np.dot(projected, projected))
    hidden = float(np.dot(tail, tail))
    global_sq = float(np.dot(e, e))
    allowed = float(roughness_budget)
    if allowed < 0 or not np.isfinite(allowed):
        raise ValueError("invalid externally registered roughness budget")
    assumption_valid = roughness <= allowed + 1e-9
    cap = tail_upper_bound(allowed, band.next_eigenvalue, order)
    return {
        "observed_band_squared_error": observed,
        "hidden_tail_squared_error": hidden,
        "external_squared_error": global_sq,
        "spectral_roughness": roughness,
        "registered_roughness_budget": allowed,
        "smoothness_assumption_verified_by_audit": bool(assumption_valid),
        "certified_tail_bound": cap,
        "bound_covers_hidden_tail": bool(assumption_valid and hidden <= cap + 1e-8),
    }


def calibrate_step(operator: np.ndarray, error: np.ndarray, band: Geometry,
                   rate: float, roughness_budget: float) -> tuple[np.ndarray, dict]:
    """One synthetic training step e' = (I - eta P)e, no learned model."""
    eta = float(rate)
    if not np.isfinite(eta) or not 0 <= eta <= 1:
        raise ValueError("rate must be finite in [0,1]")
    before = spectral_error_receipt(operator, error, band, roughness_budget)
    projected = band.projector @ np.asarray(error, dtype=float)
    updated = np.asarray(error, dtype=float) - eta * projected
    after = spectral_error_receipt(operator, updated, band, roughness_budget)
    predicted_change = (2*eta - eta**2) * before["observed_band_squared_error"]
    realized_change = before["external_squared_error"] - after["external_squared_error"]
    return updated, {
        "modal_query_count": band.rank,
        "predicted_error_reduction": float(predicted_change),
        "actual_external_error_reduction": float(realized_change),
        "self_predicted_remaining_error": after["observed_band_squared_error"],
        "actual_remaining_external_error": after["external_squared_error"],
        "unobserved_tail_after": after["hidden_tail_squared_error"],
        "certified_external_error_upper": after["observed_band_squared_error"] + after["certified_tail_bound"],
        "tail_assumption_valid": after["smoothness_assumption_verified_by_audit"],
        "claimed_bound_covers_external": after["smoothness_assumption_verified_by_audit"] and (
            after["external_squared_error"] <= after["observed_band_squared_error"]
            + after["certified_tail_bound"] + 1e-8
        ),
    }


def cycle_graph_laplacian(size: int) -> np.ndarray:
    if type(size) is not int or size < 4:
        raise ValueError("cycle graph needs at least four vertices")
    a = np.zeros((size, size), dtype=float)
    for i in range(size):
        a[i, (i+1) % size] = a[i, (i-1) % size] = -1
        a[i, i] = 2
    return a


def high_frequency_trigger(size: int) -> np.ndarray:
    """On an even cycle, alternating signs are the max-eigenvalue mode."""
    if type(size) is not int or size < 4 or size % 2:
        raise ValueError("even cycle required")
    return np.array([(-1.0)**k for k in range(size)]) / np.sqrt(size)


def simulate_calibration(
    operator: np.ndarray, initial_error: np.ndarray, *,
    strategy: str, generations: int, rate: float, registered_budget: float,
    tail_tolerance: float, fixed_low_rank: int = 1,
) -> dict:
    """Two declared evaluation-design policies at identical training rate.

    'self_confirming' keeps a frozen low-frequency band. 'spectral_audit'
    selects the narrowest band certifying a registered tail tolerance. The
    selection step has no access to the held-out residual vector.
    """
    if type(generations) is not int or generations < 0:
        raise ValueError("generations must be a nonnegative integer")
    if strategy == "self_confirming":
        band = spectral_projector(operator, fixed_low_rank)
    elif strategy == "spectral_audit":
        band = choose_certified_band(operator, registered_budget, tail_tolerance)
    else:
        raise ValueError("strategy must be self_confirming or spectral_audit")
    e = np.asarray(initial_error, dtype=float).copy()
    before = spectral_error_receipt(operator, e, band, registered_budget)
    history = []
    for k in range(generations):
        e, result = calibrate_step(operator, e, band, rate, registered_budget)
        history.append({"generation": k, **result})
    after = spectral_error_receipt(operator, e, band, registered_budget)
    return {
        "strategy": strategy,
        "band_rank": band.rank,
        "registered_tail_upper": tail_upper_bound(registered_budget, band.next_eigenvalue),
        "total_modal_queries": band.rank * generations,
        "initial_external_squared_error": before["external_squared_error"],
        "final_external_squared_error": after["external_squared_error"],
        "final_invisible_tail_squared_error": after["hidden_tail_squared_error"],
        "assumption_verified_ex_post": after["smoothness_assumption_verified_by_audit"],
        "history": history,
    }



def simulate_adaptive_band(
    operator: np.ndarray, initial_error: np.ndarray, *,
    generations: int, rate: float, registered_budget: float,
    tail_tolerance: float, order: float = 1.0,
) -> dict:
    """Self-design next eval from certified *remaining* roughness information.

    After a measured band is trained with e'=(I-eta P)e, its roughness drops by
    (2eta-eta^2) <Pe,L^s Pe>, which can be computed from *observed* modal
    coefficients. This shrinks the prior bound without opening a sealed test.
    The selected band is frozen before the coefficient responses are read.
    """
    if type(generations) is not int or generations < 0:
        raise ValueError("generations must be nonnegative")
    eta = float(rate)
    if not np.isfinite(eta) or not 0 <= eta <= 1:
        raise ValueError("rate must lie in [0,1]")
    roughness_bound = float(registered_budget)
    tail_upper_bound(roughness_bound, 1, order)
    vals, vecs = _spectrum(operator)
    error = np.asarray(initial_error, dtype=float).copy()
    if error.shape != (len(vals),) or not np.all(np.isfinite(error)):
        raise ValueError("invalid target shape")
    history = []
    total = 0
    for generation in range(generations):
        # The decision reads only current *certified bound* and frozen L.
        g = choose_certified_band(operator, roughness_bound, tail_tolerance, order)
        # This is the registered eval response; record only the selected modes.
        measured = vecs[:, :g.rank].T @ error
        projected = g.projector @ error
        removed_roughness = (2*eta - eta**2) * float(
            np.sum(vals[:g.rank] ** order * measured**2)
        )
        next_error, step = calibrate_step(operator, error, g, eta, roughness_bound)
        # Numerical cancellation is capped only at machine precision. The
        # tracked budget is a mathematical contract in exact algebra; a
        # production proof requires outward-rounded interval arithmetic.
        next_budget = max(0.0, roughness_bound - removed_roughness)
        next_truth = spectral_error_receipt(operator, next_error, g, next_budget, order)
        history.append({
            "generation": generation,
            "selected_band_rank": g.rank,
            "budget_before": roughness_bound,
            "budget_after": next_budget,
            "roughness_reduction_from_observed_modes": removed_roughness,
            "bound_valid_ex_post": next_truth["smoothness_assumption_verified_by_audit"],
            **step,
        })
        total += g.rank
        error, roughness_bound = next_error, next_budget
    true_final = float(np.dot(error, error))
    return {
        "strategy": "adaptive_spectral_self_design",
        "initial_roughness_budget": float(registered_budget),
        "final_roughness_budget": roughness_bound,
        "total_modal_queries": total,
        "final_external_squared_error": true_final,
        "ranks": [x["selected_band_rank"] for x in history],
        "all_budget_checks_passed": all(x["bound_valid_ex_post"] for x in history),
        "history": history,
    }


def random_equal_cost_control(initial_error: np.ndarray, *, rank: int,
                              generations: int, rate: float,
                              replicates: int = 128, seed: int = 20261027) -> dict:
    """Fresh Haar-isotropic projector per generation, without spectral guarantee.

    This is a target-blind cost-matched baseline. Each replicate redraws an
    independent rank-r random subspace for every round. The exact expectation
    is ||e_0||^2 * (1-(2eta-eta^2)*r/n)**generations.
    """
    e = np.asarray(initial_error, dtype=float)
    if e.ndim != 1 or len(e) < 2 or not np.all(np.isfinite(e)):
        raise ValueError("initial error must be finite nonempty vector")
    if type(rank) is not int or not 1 <= rank <= len(e):
        raise ValueError("rank out of range")
    if type(generations) is not int or generations < 0:
        raise ValueError("generations must be nonnegative")
    if type(replicates) is not int or replicates < 1:
        raise ValueError("replicates must be positive")
    if type(seed) is not int:
        raise ValueError("seed must be an int")
    eta = float(rate)
    if not np.isfinite(eta) or not 0 <= eta <= 1:
        raise ValueError("invalid rate")
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(replicates):
        state = e.copy()
        for _ in range(generations):
            basis, _ = np.linalg.qr(rng.standard_normal((len(e),rank)), mode="reduced")
            state = state - eta * basis @ (basis.T @ state)
        values.append(float(np.dot(state,state)))
    expected = float(np.dot(e,e)) * (1 - (2*eta-eta**2)*rank/len(e))**generations
    return {
        "seed": seed,
        "replicates": replicates,
        "rank": rank,
        "scalar_linear_queries_per_replica": rank * generations,
        "mean_final_squared_error": float(np.mean(values)),
        "analytic_isotropic_expected_squared_error": expected,
        "independent_tail_certificate": False,
    }

def verify_synthetic() -> dict:
    n = 12
    l = cycle_graph_laplacian(n)
    error = high_frequency_trigger(n)
    # Global bound B^2=4 is registered before choosing bands. It holds for
    # this synthetic high-frequency eigenmode, with equality.
    low_rank = 3  # {0, lambda_1, lambda_1} as a full eigenspace family.
    low = simulate_calibration(l, error, strategy="self_confirming",
                              generations=12, rate=.25, registered_budget=4,
                              tail_tolerance=.05, fixed_low_rank=low_rank)
    audited = simulate_calibration(l, error, strategy="spectral_audit",
                                  generations=12, rate=.25, registered_budget=4,
                                  tail_tolerance=.05, fixed_low_rank=low_rank)
    adaptive = simulate_adaptive_band(l, error, generations=12, rate=.25,
                                      registered_budget=4, tail_tolerance=.05)
    random_control = random_equal_cost_control(error, rank=3, generations=12,
                                              rate=.25, replicates=256, seed=20261027)
    smooth_error = spectral_projector(l, low_rank).basis[:, 1]
    on_band = simulate_calibration(l, smooth_error, strategy="self_confirming",
                                   generations=12, rate=.25, registered_budget=4,
                                   tail_tolerance=.05, fixed_low_rank=low_rank)
    random_on_band = random_equal_cost_control(smooth_error, rank=3, generations=12,
                                               rate=.25, replicates=256, seed=20261027)
    wrong_assumption = spectral_error_receipt(l, error, spectral_projector(l, low_rank), .1)
    checks = {
        "low_band_invisible_high_error": abs(low["final_external_squared_error"] - 1) < 1e-10,
        "blind_self_prediction_zero": all(abs(x["self_predicted_remaining_error"]) < 1e-10
                                          for x in low["history"]),
        "external_error_reduced_when_full_band_audited": audited["final_external_squared_error"] < .002,
        "certified_band_query_budget_higher": audited["total_modal_queries"] > low["total_modal_queries"],
        "one_step_predictions_valid_within_band": all(
            abs(x["predicted_error_reduction"] - x["actual_external_error_reduction"]) < 1e-10
            for policy in (low, audited) for x in policy["history"]),
        "false_smoothness_assumption_detected": not wrong_assumption["smoothness_assumption_verified_by_audit"],
        "adaptive_band_cost_saving": adaptive["total_modal_queries"] < audited["total_modal_queries"],
        "adaptive_band_reaches_external_threshold": adaptive["final_external_squared_error"] < .05,
        "adaptive_band_budget_valid": adaptive["all_budget_checks_passed"],
        "random_cost_matched_detects_high_mode": random_control["mean_final_squared_error"] < .5,
        "spectral_lowband_wins_when_error_in_band": on_band["final_external_squared_error"] < .002
                                                     and random_on_band["mean_final_squared_error"] > .15,
        "random_isotropic_exact_expectation": abs(random_control["mean_final_squared_error"] - random_control["analytic_isotropic_expected_squared_error"]) < .07,
        "hidden_tail_bound_covers_when_assumption_true": all(x["claimed_bound_covers_external"]
                                                             for policy in (low, audited) for x in policy["history"]),
    }
    return {
        "schema": "hrc-frc-spectral-v0.2",
        "evidence": "synthetic_only",
        "real_models_run": 0,
        "consciousness_claim": False,
        "checks": checks,
        "all_passed": all(checks.values()),
        "controls": {
            "cycle_size": n,
            "training_rate": .25,
            "generations": 12,
            "roughness_budget": 4,
            "tail_tolerance": .05,
            "low_rank": low_rank,
        },
        "self_confirming": {k: v for k, v in low.items() if k != "history"},
        "spectral_audit": {k: v for k, v in audited.items() if k != "history"},
        "adaptive_spectral_self_design": {k: v for k, v in adaptive.items() if k != "history"},
        "wrong_smoothness_assumption": wrong_assumption,
        "random_equal_cost_control": random_control,
        "smooth_low_mode_target": {"low_band": {k:v for k,v in on_band.items() if k != "history"},
                                   "random_equal_cost": random_on_band},
    }
