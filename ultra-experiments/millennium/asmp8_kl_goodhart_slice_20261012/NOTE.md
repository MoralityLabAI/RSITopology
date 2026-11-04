# ASMP-8 KL-slice Goodhart bound: exact replay

Status: replay note, 2026-10-12. The theorem, its proof, and the proposed v0.2
statement are in
[`../ASMP_V0_2_STATEMENT_REPAIRS_DRAFT_20261012.md`](../ASMP_V0_2_STATEMENT_REPAIRS_DRAFT_20261012.md)
item R3. This package computes exact KL-ball proxy maximisers on finite
outcome sets and checks the inequalities on concrete instances. It replays
the construction; it is not evidence beyond the instances it computes.

Code: `kl_goodhart_check.py` (stdlib only, a few seconds).

## 1. What is computed

Reference law `p_0` on a finite set, true reward `R`, proxy `R_hat`, error
`delta = R - R_hat`, reachable set `{pi : KL(pi || p_0) <= lambda}`. The
proxy maximiser over the KL ball is the exponential tilt
`pi_t ∝ p_0 exp(t R_hat)` with `KL(pi_t || p_0) = lambda`, found by
bisection, or the point mass on the proxy argmax once it is inside the ball.
Regret is the best true value in the ball minus the true value of the proxy
maximiser; the best true value is computed the same way with `R` in place of
`R_hat`.

## 2. Checks and outcomes

**Light tails (theorem).** Sixty outcomes, Gaussian-drawn rewards and an
error with sub-Gaussian constant `sigma = 0.329` (smallest constant on a
grid of `t`; the Hoeffding value `(max - min)/2 = 0.774` is also valid). The
bound `2 sigma sqrt(2 lambda)` holds at every budget; the ratio
regret/bound rises from 0.06 at `lambda = 0.01` to 0.20 at `lambda = 2`.
The bound is loose on generic instances, which is expected: sharpness needs
the proxy anti-aligned with the true reward.

**Sharpness (closed form).** For `R = u·w`, `R_hat = -s u·w`, `p_0 = N(0,I)`,
regret is `2 sqrt(2 lambda)` and the bound is `2 (1+s) sqrt(2 lambda)`; the
ratio is 0.909 at `s = 0.1`, 0.990 at `s = 0.01`, 0.999 at `s = 0.001`. A
proxy of arbitrarily small magnitude, anti-aligned with the truth, attains
the constant.

**Heavy tails.** Discrete Pareto-like law: `x_k = k^(2/3)` with
`p_0(k) ∝ k^(-2)` on 4,000 outcomes, so `P(x > a) ~ a^(-3/2)`.

- Unbounded, anti-correlated rewards `R = -x`, `R_hat = +x`: regret 36.0,
  63.7, 89.5, 113.8, 137.0, 159.3 at `lambda = 1, …, 6`, still growing; the
  asymptotic rate `exp(lambda / p)` is capped by the finite support (largest
  `x` is 252). A light-tailed two-point error of the same variance gives
  regret 8.8 then 9.6, saturating once the point mass is inside the ball.
- Bounded true reward in `[0, 1]` with the same errors: the fraction of the
  available true gain captured by the proxy maximiser is **negative** for
  the heavy-tailed error (−0.49, −0.33, −0.23, −0.16 at `lambda = 0.5, 1, 2,
  4`: the proxy-optimal policy is worse than the base) and +0.59, +0.57,
  +0.81, +0.88 for the light-tailed error. This is the catastrophic-Goodhart
  form of Kwa, Thomas, and Garriga-Alonso (arXiv 2407.14503) on a finite
  instance.

**Finite-sample corollary.** Uniform `p_0` on 40 outcomes, proxy equal to an
empirical mean of `m` noisy samples per outcome. With sup-norm error
`eps_m` of 0.216, 0.057, 0.020 at `m = 10, 100, 1000`, the maximum regret
over `lambda in {0.1, 1, 3, 3.6}` is 0.024, 0.007, 0.002, each below
`2 eps_m`, and independent of `lambda` in the sense that the bound is.

## 3. Claim boundary

Exact for the finite instances computed. The light-tail theorem and its
sharpness are proved in R3; the heavy-tail behaviour is illustrated, with
the bounded-reward form proved by Kwa et al. and the unbounded-reward
growth stated as a sketch in R3. Nothing here concerns learned reward
models on real data, best-of-`n` sampling beyond the KL-radius remark in R3,
or ASMP-8 as a whole.
