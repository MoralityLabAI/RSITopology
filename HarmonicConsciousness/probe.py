"""Finite-dimensional harmonic diagnostics; a mechanism probe, not a consciousness test.

Complex modal amplitudes here are classical analytic-signal coordinates.  No
quantum interpretation or local-smoothing theorem is asserted by this module.
"""
from __future__ import annotations

import numpy as np


def _checked_modes(
    frequencies: np.ndarray, modes: np.ndarray, amplitudes: np.ndarray,
    observation: np.ndarray, horizon: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]:
    w = np.asarray(frequencies, dtype=float)
    q = np.asarray(modes, dtype=complex)
    a = np.asarray(amplitudes, dtype=complex)
    b = np.asarray(observation, dtype=complex)
    t = float(horizon)
    if w.ndim != 1 or not 1 <= len(w) or not np.all(np.isfinite(w)):
        raise ValueError("frequencies must be a nonempty finite vector")
    if q.ndim != 2 or q.shape[1] != len(w) or q.shape[0] < q.shape[1]:
        raise ValueError("modes must be a tall N x K array")
    if a.shape != (len(w),):
        raise ValueError("amplitudes must have one coefficient per mode")
    if b.ndim != 2 or b.shape[0] < 1 or b.shape[1] != q.shape[0]:
        raise ValueError("observation must be a nonempty M x N array")
    if not np.all(np.isfinite(q)) or not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
        raise ValueError("modes, amplitudes and observation must be finite")
    if not np.allclose(q.conj().T @ q, np.eye(len(w)), atol=1e-9):
        raise ValueError("modes must have orthonormal columns")
    if not np.isfinite(t) or t <= 0:
        raise ValueError("horizon must be finite and positive")
    return w, q, a, b, t


def localized_time_average(
    frequencies: np.ndarray, modes: np.ndarray, amplitudes: np.ndarray,
    observation: np.ndarray, horizon: float,
) -> dict[str, float | int | None]:
    """Exact finite-mode mean of ||B sum_k a_k exp(i*w_k*t) phi_k||^2.

    Equal *exact* frequencies are grouped into basis-invariant eigenspace
    vectors.  For near-degeneracies, retain their actual frequency gap.
    The off-diagonal interference bound is O(1/T) for a fixed positive gap;
    its constants need not be uniform as model dimension grows.
    """
    w, q, a, b, t = _checked_modes(frequencies, modes, amplitudes, observation, horizon)
    distinct, inverse = np.unique(w, return_inverse=True)
    projected = np.zeros((b.shape[0], len(distinct)), dtype=complex)
    for j, group in enumerate(inverse):
        projected[:, group] += b @ q[:, j] * a[j]
    gram = projected.conj().T @ projected
    delta = distinct[None, :] - distinct[:, None]
    # sinc(x) in NumPy means sin(pi*x)/(pi*x); this is exact integration.
    kernel = np.exp(0.5j * delta * t) * np.sinc(delta * t / (2 * np.pi))
    exact = float(np.real(np.sum(gram * kernel)))
    incoherent = float(np.real(np.trace(gram)))
    offdiag = ~np.eye(len(distinct), dtype=bool)
    gap = np.abs(delta[offdiag])
    if len(gap):
        bounds = np.minimum(1.0, 2.0 / (t * gap))
        upper = float(np.sum(np.abs(gram[offdiag]) * bounds))
        minimum_gap = float(np.min(gap))
    else:
        upper = 0.0
        minimum_gap = None
    return {
        "time_average": exact,
        "incoherent_energy": incoherent,
        "interference": exact - incoherent,
        "interference_bound": upper,
        "distinct_frequency_count": int(len(distinct)),
        "minimum_distinct_gap": minimum_gap,
        "horizon": t,
    }


def sampled_time_average(
    frequencies: np.ndarray, modes: np.ndarray, amplitudes: np.ndarray,
    observation: np.ndarray, horizon: float, samples: int = 20001,
) -> float:
    """Independent trapezoidal quadrature for checking the analytic identity."""
    w, q, a, b, t = _checked_modes(frequencies, modes, amplitudes, observation, horizon)
    if not isinstance(samples, int) or samples < 3:
        raise ValueError("samples must be an integer >= 3")
    times = np.linspace(0.0, t, samples)
    phase = np.exp(1j * w[:, None] * times[None, :])
    signals = (b @ q) @ (a[:, None] * phase)
    values = np.sum(np.abs(signals) ** 2, axis=0)
    return float((values[0] * 0.5 + np.sum(values[1:-1]) + values[-1] * 0.5) / (samples - 1))


def effective_rank(covariance: np.ndarray) -> float:
    """Covariance participation ratio tr(C)^2/tr(C^2), zero when C=0."""
    c = np.asarray(covariance, dtype=complex)
    if c.ndim != 2 or c.shape[0] != c.shape[1] or c.shape[0] == 0:
        raise ValueError("covariance must be nonempty and square")
    if not np.all(np.isfinite(c)) or not np.allclose(c, c.conj().T, atol=1e-9):
        raise ValueError("covariance must be finite and Hermitian")
    eig = np.linalg.eigvalsh(c)
    if np.min(eig) < -1e-9 * max(1.0, float(np.max(np.abs(eig)))):
        raise ValueError("covariance must be positive semidefinite")
    eig = np.maximum(eig, 0.0)
    power = float(np.sum(eig * eig))
    return float(np.sum(eig) ** 2 / power) if power > 0.0 else 0.0


def phase_locking(phase_a: np.ndarray, phase_b: np.ndarray, m: int = 1, n: int = 1) -> float:
    """Magnitude of m:n phase locking across time (descriptive statistic)."""
    a = np.asarray(phase_a, dtype=float)
    b = np.asarray(phase_b, dtype=float)
    if a.ndim != 1 or b.shape != a.shape or len(a) < 2:
        raise ValueError("phases must be same-length 1D vectors with >= 2 samples")
    if not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
        raise ValueError("phases must be finite")
    if not isinstance(m, int) or not isinstance(n, int) or m < 1 or n < 1:
        raise ValueError("harmonic indices must be positive integers")
    return float(abs(np.mean(np.exp(1j * (m * a - n * b)))))


def circular_shift_null(
    phase_a: np.ndarray, phase_b: np.ndarray, *, m: int = 1, n: int = 1,
    replicates: int = 199, seed: int = 20261027, minimum_shift: int = 32,
) -> dict[str, float | int]:
    """Illustrative stationary circular-shift surrogate, NOT a causal test.

    This preserves each input's univariate circular autocorrelation. It may be
    uninformative for pure tones and invalid for event-locked nonstationarity.
    """
    a = np.asarray(phase_a, dtype=float)
    b = np.asarray(phase_b, dtype=float)
    observed = phase_locking(a, b, m, n)
    if replicates < 1 or minimum_shift < 1 or len(a) <= 2 * minimum_shift:
        raise ValueError("invalid surrogate count or available shift range")
    rng = np.random.default_rng(seed)
    offsets = rng.integers(minimum_shift, len(a) - minimum_shift, size=replicates)
    null = np.array([phase_locking(a, np.roll(b, int(s)), m, n) for s in offsets])
    return {
        "observed": observed,
        "surrogate_mean": float(np.mean(null)),
        "surrogate_max": float(np.max(null)),
        "p_upper_tail": float((1 + np.sum(null >= observed)) / (replicates + 1)),
        "replicates": replicates,
        "seed": seed,
    }
