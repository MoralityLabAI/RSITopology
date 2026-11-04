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


def dp_lower_bound(a: Fraction, delta: Fraction, G: int, T: int) -> list[tuple[int, float]]:
    """Rigorous lower bound on the minimal leaf count of ANY safe code (NOTE.md 4.7).

    Every realised node has fullness f in [0,1]; its children have fullnesses f_i in [0,1]
    with sum f_i >= a f + rho delta.  Rounding children DOWN to the grid (g_i = floor(G f_i)/G)
    and crediting each child 1/G of mass (g_i + 1/G > f_i) relaxes the constraint, and the
    cost of a child only decreases by monotonicity, so the resulting knapsack value is a lower
    bound on the true DP value V_T(1), hence on |L(T)| for every safe code.
    """
    rho = a / (1 - delta)
    fidx = [0] * (G + 1)
    for i in range(0, G + 1):
        fidx[i] = ceil_frac(a * i + G * rho * delta)
    jmax = fidx[G]
    V = [1] * (G + 1)
    out = []
    for level in range(1, T + 1):
        W = [0] * (jmax + 1)
        for j in range(1, jmax + 1):
            best = None
            for g in range(0, min(G, j - 1) + 1):   # item weight g+1 <= j
                c = V[g] + W[j - (g + 1)]
                if best is None or c < best:
                    best = c
            W[j] = best
        V = [W[fidx[i]] for i in range(G + 1)]
        out.append((level, math.log2(V[G]) / level))
    return out


def potential_lower_bound(a: Fraction, delta: Fraction) -> tuple[float, float]:
    """Explicit strict lower bound rho* > rho via the potential f + c (NOTE.md 4.7).

    For c > 0 the growth factor rho'(c) is the minimum over the critical fullness values of
    L_c(f) / (f + c), L_c(f) = a f + rho delta + c ceil(a f + rho delta).  Returns (rho*, c*).
    """
    rho = a / (1 - delta)
    m0 = rho * delta
    thresholds = [k for k in range(1, int(math.ceil(float(rho))) + 1) if m0 < k < rho]

    def factor(c: float) -> float:
        # L_c(f) is linear with slope a between jump points; the ratio L_c/(f+c) is monotone on
        # each piece, so the minimum over [0,1] is attained at an endpoint of a piece: f = 0,
        # f = 1, or either side of a jump f_k = (k - rho delta)/a.
        vals = []
        m0f = float(m0)
        vals.append((m0f + c * math.ceil(m0f - 1e-15)) / c)                       # f = 0 exactly
        vals.append((m0f + c * (math.floor(m0f + 1e-15) + 1)) / c)                # f = 0+, ceiling may step up
        for k in thresholds:
            fk = float(k - m0) / float(a)
            vals.append((k + c * k) / (fk + c))                                   # f_k-: mass k, ceiling k
            vals.append((k + c * (k + 1)) / (fk + c))                             # f_k+: mass k, ceiling k+1
        vals.append((float(rho) + c * math.ceil(float(rho) - 1e-15)) / (1 + c))  # f = 1
        # cross-check on a fine grid
        for i in range(1, 2000):
            f = i / 2000.0
            m = float(a) * f + m0f
            vals.append((m + c * math.ceil(m - 1e-12)) / (f + c))
        return min(vals)

    best_c, best = 0.0, float(rho)
    c = 1e-4
    while c < 10.0:
        v = factor(c)
        if v > best:
            best, best_c = v, c
        c *= 1.01
    return best, best_c


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
    print(f"  best DP upper bound over horizons <= {T}: {best:.6f}  (gap to mass bound {best - lower:.4f})")
    rstar, cstar = potential_lower_bound(a, delta)
    print(f"  potential lower bound: rho* = {rstar:.6f} at c = {cstar:.4f}, log2(rho*) = {math.log2(rstar):.6f} > log2(rho) = {lower:.6f}")
    assert rstar > float(rho), "strictness failed"
    dplo = dp_lower_bound(a, delta, G, T)
    lo_T = dplo[-1][1]
    print(f"  floor-relaxed DP lower bound at horizon {T}: {lo_T:.6f}  (valid for every safe code)")
    assert lo_T >= lower - 1e-12 and lo_T <= best + 1e-12
    print(f"  bracket for h*: [{max(lo_T, math.log2(rstar)):.6f}, {best:.6f}] bits per step")

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
