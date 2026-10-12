"""Bounds for the canonical rate threshold h* of the scalar uncertain plant
(NOTE.md section 4).

Plant: x' = a x + u + w, |w| <= delta < 1, K = K0 = [-1, 1], rho = a / (1 - delta).

Proved in NOTE.md:  log2 rho <= h* <= log2 ceil(rho);  h* = log2 rho when rho is an
integer or delta = 0.  This script computes, in exact integer arithmetic on a
fullness grid, the minimal leaf count V_T of a T-step interval-cell scheme (cells
are intervals; continuation masses are rounded UP to the grid, so every scheme the
DP finds is a genuine safe scheme).  By restarting the scheme every T steps,
(1/T) log2 V_T is a valid upper bound on h* for every T.  It also replays the
greedy per-step schedule and the uniform ceil(rho) schedule.

Nothing here is evidence for the lower bound, which is the proof in NOTE.md.
"""
from __future__ import annotations

import math
import sys
from fractions import Fraction


def ceil_frac(q: Fraction) -> int:
    return -((-q.numerator) // q.denominator)


def greedy_rate(a: Fraction, delta: Fraction, T: int) -> float:
    """Average log2 m_t of the greedy schedule m_t = ceil(rho ell_t); checks safety."""
    rho = a / (1 - delta)
    ell = Fraction(1)
    log_sum = 0.0
    for t in range(T):
        m = ceil_frac(rho * ell)
        log_sum += math.log2(m)
        ell = a * ell / m + delta
        assert ell <= 1, f"greedy schedule unsafe at step {t}"
    return log_sum / T


def dp_upper_bound(a: Fraction, delta: Fraction, G: int, T: int) -> list[tuple[int, float]]:
    """Minimal leaf count of a T-step interval-cell scheme on a fullness grid of 1/G.

    A cell of fullness theta = i/G (half-length theta / rho) is safe iff theta <= 1.
    Its continuation has mass f(theta) = a theta + rho delta in cell units; we round
    that mass UP to the grid (over-covering is safe).  V[i] = minimal leaves from a
    cell of fullness i/G; W[j] = minimal leaves needed to cover grid mass j with cells.
    Returns [(T, log2(V_T[G]) / T), ...] for the horizons recorded.
    """
    rho = a / (1 - delta)
    # continuation mass index for fullness i/G: ceil(G * (a * i/G + rho*delta)) = ceil(a*i + G*rho*delta)
    fidx = [0] * (G + 1)
    for i in range(1, G + 1):
        fidx[i] = ceil_frac(a * i + G * rho * delta)
    jmax = fidx[G]
    V = [1] * (G + 1)  # V_0: one leaf from any cell
    V[0] = 0
    out = []
    for level in range(1, T + 1):
        W = [0] * (jmax + 1)
        for j in range(1, jmax + 1):
            best = None
            imax = min(G, j)
            for i in range(1, imax + 1):
                c = V[i] + W[j - i]
                if best is None or c < best:
                    best = c
            W[j] = best
        V_new = [0] * (G + 1)
        for i in range(1, G + 1):
            V_new[i] = W[fidx[i]]
        V = V_new
        out.append((level, math.log2(V[G]) / level))
    return out


def main() -> int:
    G = int(sys.argv[1]) if len(sys.argv) > 1 else 240
    T = int(sys.argv[2]) if len(sys.argv) > 2 else 80

    # Case 1: the running example a = 5/2, delta = 1/10 (rho = 25/9, not an integer).
    a, delta = Fraction(5, 2), Fraction(1, 10)
    rho = a / (1 - delta)
    lower = math.log2(rho)
    uniform = math.log2(ceil_frac(rho))
    greedy = greedy_rate(a, delta, 2000)
    dp = dp_upper_bound(a, delta, G, T)
    print(f"case 1: a={a} delta={delta} rho={float(rho):.6f}")
    print(f"  proved lower bound   log2(rho)        = {lower:.6f}")
    print(f"  uniform scheme       log2(ceil(rho))  = {uniform:.6f}")
    print(f"  greedy scheme (T=2000) average rate   = {greedy:.6f}")
    for lvl, r in dp:
        if lvl in (10, 20, 40, 60, T):
            print(f"  DP interval-cell scheme, horizon {lvl:3d}: upper bound {r:.6f}")
    best = min(r for _, r in dp)
    assert best >= lower - 1e-12, "DP upper bound fell below the proved lower bound"
    print(f"  best DP upper bound over horizons <= {T}: {best:.6f}  (gap to lower bound {best - lower:.4f})")

    # Case 2: rho integer (a = 2, delta = 1/3, rho = 3): DP must return exactly 3^T leaves.
    a2, d2 = Fraction(2), Fraction(1, 3)
    dp2 = dp_upper_bound(a2, d2, 60, 12)
    r2 = dp2[-1][1]
    assert abs(r2 - math.log2(3)) < 1e-12, f"integer-rho case failed: {r2}"
    print(f"case 2: a=2 delta=1/3 (rho=3): DP rate {r2:.6f} = log2 3 exactly")

    # Case 3: delta = 0, a = 5/2: classical data-rate value log2 a, approached from above.
    dp3 = dp_upper_bound(Fraction(5, 2), Fraction(0), 120, 60)
    r3 = dp3[-1][1]
    print(f"case 3: a=5/2 delta=0: DP rate at horizon 60 = {r3:.6f}, log2 a = {math.log2(2.5):.6f}")
    assert r3 >= math.log2(2.5) - 1e-12
    print("all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
