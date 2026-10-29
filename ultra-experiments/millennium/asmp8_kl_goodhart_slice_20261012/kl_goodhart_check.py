"""Exact replay for the ASMP-8 KL-slice theorem (repairs draft R3).

Setting: reference law p0 on a finite outcome set, true reward R, proxy R_hat,
error delta = R - R_hat.  Reachable set Pi_lambda = {pi : KL(pi || p0) <= lambda}.
Proxy maximiser: the KL-ball maximiser of E_pi[R_hat], which is the exponential
tilt pi_t ∝ p0 exp(t R_hat) with KL(pi_t || p0) = lambda (or the point mass on the
proxy argmax once that is inside the ball).  Regret = max_{pi in ball} E_pi[R] - E_{pi_hat}[R].

Checks:
  1. Light tails: regret <= 2 sigma sqrt(2 lambda) with sigma the sub-Gaussian
     constant of delta under p0 (computed here as the smallest sigma with
     log E exp(t(delta - E delta)) <= sigma^2 t^2 / 2 on a t-grid; for a bounded
     variable Hoeffding's (b-a)/2 is also a valid sigma and is reported).
  2. Sharpness: the Gaussian linear instance of R3 in closed form.
  3. Heavy tails: a discrete Pareto-like error at fixed KL budgets; the regret
     grows like exp(lambda / p) rather than sqrt(lambda).
  4. Finite-sample corollary: when the proxy is an empirical mean with sup-norm
     error eps_n, regret <= 2 eps_n for every lambda (KL-independent).

Stdlib only.  This replays the theorem's inequalities; it is not evidence
beyond the finite instances it computes.
"""
from __future__ import annotations

import math
import random
import sys


def kl(p: list[float], q: list[float]) -> float:
    return sum(pi * math.log(pi / qi) for pi, qi in zip(p, q) if pi > 0)


def tilt(p0: list[float], f: list[float], t: float) -> list[float]:
    m = max(f)
    w = [pi * math.exp(t * (fi - m)) for pi, fi in zip(p0, f)]
    z = sum(w)
    return [x / z for x in w]


def kl_ball_max(p0: list[float], f: list[float], lam: float) -> tuple[list[float], float]:
    """Maximise E_pi[f] over KL(pi||p0) <= lam.  Returns (pi, value)."""
    # point mass on an argmax of f is reachable iff -log p0(argmax set) <= lam
    fmax = max(f)
    mass = sum(pi for pi, fi in zip(p0, f) if fi == fmax)
    if -math.log(mass) <= lam + 1e-12:
        pi = [pi / mass if fi == fmax else 0.0 for pi, fi in zip(p0, f)]
        return pi, fmax
    lo, hi = 0.0, 1.0
    while kl(tilt(p0, f, hi), p0) < lam:
        hi *= 2.0
        if hi > 1e9:
            break
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if kl(tilt(p0, f, mid), p0) < lam:
            lo = mid
        else:
            hi = mid
    pi = tilt(p0, f, lo)
    return pi, sum(a * b for a, b in zip(pi, f))


def subgaussian_sigma(p0: list[float], d: list[float]) -> float:
    """Smallest sigma on a t-grid with log E exp(t (d - Ed)) <= sigma^2 t^2 / 2."""
    mean = sum(p * x for p, x in zip(p0, d))
    best = 0.0
    for k in range(1, 401):
        t = k * 0.05
        for sgn in (1.0, -1.0):
            lmgf = math.log(sum(p * math.exp(sgn * t * (x - mean)) for p, x in zip(p0, d)))
            best = max(best, math.sqrt(max(2.0 * lmgf, 0.0)) / t)
    return best


def regret(p0, R, Rhat, lam) -> float:
    pihat, _ = kl_ball_max(p0, Rhat, lam)
    _, best_true = kl_ball_max(p0, R, lam)
    return best_true - sum(a * b for a, b in zip(pihat, R))


def case_light_tails(seed: int = 7) -> None:
    rng = random.Random(seed)
    n = 60
    p0 = [rng.random() for _ in range(n)]
    s = sum(p0)
    p0 = [x / s for x in p0]
    R = [rng.gauss(0, 1) for _ in range(n)]
    delta = [rng.gauss(0, 0.3) for _ in range(n)]
    Rhat = [r - d for r, d in zip(R, delta)]
    sigma = subgaussian_sigma(p0, delta)
    sigma_hoeff = (max(delta) - min(delta)) / 2
    print("case 1: light-tailed error on 60 outcomes")
    print(f"  sub-Gaussian constant (grid) sigma = {sigma:.4f}; Hoeffding sigma = {sigma_hoeff:.4f}")
    worst_ratio = 0.0
    for lam in (0.01, 0.05, 0.1, 0.3, 0.5, 1.0, 2.0):
        reg = regret(p0, R, Rhat, lam)
        bound = 2 * sigma * math.sqrt(2 * lam)
        worst_ratio = max(worst_ratio, reg / bound)
        print(f"  lambda={lam:5.2f}: regret={reg:.5f}  bound 2 sigma sqrt(2 lambda)={bound:.5f}  ratio={reg/bound:.3f}")
        assert reg <= bound + 1e-9, "light-tail bound violated"
    print(f"  max regret/bound = {worst_ratio:.3f} (<= 1 required)")


def case_sharpness() -> None:
    print("case 2: Gaussian linear instance, closed form")
    print("  R = u.w, R_hat = -s u.w, p0 = N(0,I): regret = 2 sqrt(2 lambda); bound = 2 (1+s) sqrt(2 lambda)")
    for s in (1.0, 0.1, 0.01, 0.001):
        for lam in (0.5, 2.0):
            reg = 2 * math.sqrt(2 * lam)
            bound = 2 * (1 + s) * math.sqrt(2 * lam)
            print(f"  s={s:6.3f} lambda={lam}: regret/bound = {reg/bound:.4f}")


def case_heavy_tails() -> None:
    """Heavy-tailed proxy error on a discrete Pareto-like law: x_k = k^(2/3) with
    p0(k) ∝ k^(-2), so P(x > a) ~ a^(-3/2) (tail index p = 3/2).

    (a) Unbounded, anti-correlated rewards R = -x, R_hat = +x (error delta = -2x):
        the proxy maximiser chases the tail and the true loss grows like exp(lambda/p),
        against sqrt(lambda) for a light-tailed error of the same variance.
    (b) Bounded true reward in [0,1] with the same heavy-tailed error: regret is
        bounded by the range, but the proxy maximiser captures none of the
        available true gain (the Kwa-Thomas-Garriga-Alonso 'catastrophic Goodhart'
        form), while a light-tailed error of the same variance captures almost all.
    """
    print("case 3: heavy-tailed error (discrete Pareto, tail index 3/2) vs light-tailed error, same variance")
    n = 4000
    xs = [k ** (2.0 / 3.0) for k in range(1, n + 1)]
    w = [1.0 / (k * k) for k in range(1, n + 1)]
    z = sum(w)
    p0 = [v / z for v in w]
    mean = sum(p * x for p, x in zip(p0, xs))
    var = sum(p * (x - mean) ** 2 for p, x in zip(p0, xs))
    sd = math.sqrt(var)
    # (a) unbounded anti-correlated instance
    print("  (a) unbounded: R = -x, R_hat = +x (heavy); R = -y, R_hat = +y with y two-point, same variance (light)")
    ys = [mean + sd if k % 2 == 0 else mean - sd for k in range(n)]
    for name, v in (("heavy", xs), ("light", ys)):
        R = [-t for t in v]
        Rhat = [t for t in v]
        prev = None
        row = []
        for lam in (1.0, 2.0, 3.0, 4.0, 5.0, 6.0):
            reg = regret(p0, R, Rhat, lam)
            row.append(f"lam={lam:.0f}: {reg:8.3f}" + ("" if prev is None else f" (x{reg/prev:.2f})"))
            prev = reg
        print(f"    {name:5s}: " + " | ".join(row))
    print("      light (two-point, bounded support): saturates once the point mass on the better value is inside the ball;")
    print("      heavy: keeps growing with lambda (ratios shown); the asymptotic rate exp(lambda/p) is capped here by the")
    print("      finite support of 4000 outcomes (max x = 4000^(2/3) = 252), so the printed ratios fall short of e^(2/3) = 1.95")
    # (b) bounded true reward, same errors
    rng = random.Random(3)
    Rb = [rng.uniform(0.0, 1.0) for _ in range(n)]
    base = sum(p * r for p, r in zip(p0, Rb))
    print("  (b) bounded true reward in [0,1]; fraction of the available true gain captured by the proxy maximiser")
    for name, err in (("heavy", [x - mean for x in xs]), ("light", [y - mean for y in ys])):
        Rhat = [r - d for r, d in zip(Rb, err)]
        row = []
        for lam in (0.5, 1.0, 2.0, 4.0):
            pihat, _ = kl_ball_max(p0, Rhat, lam)
            _, best_true = kl_ball_max(p0, Rb, lam)
            got = sum(a * b for a, b in zip(pihat, Rb))
            frac = (got - base) / (best_true - base)
            row.append(f"lam={lam}: {frac:+.3f}")
        print(f"    {name:5s}: " + " | ".join(row))


def case_finite_sample(seed: int = 11) -> None:
    print("case 4: finite-sample corollary, sup-norm error gives KL-independent regret")
    rng = random.Random(seed)
    n = 40
    p0 = [1.0 / n] * n
    R = [rng.uniform(0, 1) for _ in range(n)]
    for m in (10, 100, 1000):
        # proxy = empirical mean of m noisy samples per outcome, noise uniform(-0.5, 0.5)
        Rhat = [r + sum(rng.uniform(-0.5, 0.5) for _ in range(m)) / m for r in R]
        eps = max(abs(a - b) for a, b in zip(R, Rhat))
        worst = max(regret(p0, R, Rhat, lam) for lam in (0.1, 1.0, 3.0, 3.6))
        print(f"  m={m:5d} samples/outcome: sup-norm error eps={eps:.4f}; max regret over lambda = {worst:.4f} <= 2 eps = {2*eps:.4f}")
        assert worst <= 2 * eps + 1e-9


def main() -> int:
    case_light_tails()
    case_sharpness()
    case_heavy_tails()
    case_finite_sample()
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
