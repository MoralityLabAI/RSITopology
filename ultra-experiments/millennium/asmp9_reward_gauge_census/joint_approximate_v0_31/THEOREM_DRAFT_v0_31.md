# ASMP-9 v0.31 development theorem: joint approximate quotient certificate

Status: development-only. Not registered and not claim-eligible.

## Setting

Let `theta` be reward coordinates after quotienting a declared decision-null
gauge. A nominal calibrated experiment has quotient occupancy design `A`.
Each measurement belongs to a registered context, represented by a
full-column-rank nuisance design `C`. The localized scalar vector obeys:

```text
y = (A + Delta) theta + C b + l + m + D s.
```

Here:

- `Delta` is mechanical occupancy-row drift;
- `b` is arbitrary exactly context-factorable midpoint drift;
- `l` is threshold-localization error;
- `m` is residual midpoint drift outside the factor model;
- `D s` is semantic-calibration error, with `D` preserving which scalar
  consequence cells are reused across comparisons.

All source bounds and units are declared before outcomes.

## A. Exact nuisance projection

Let:

```text
P = I - C(C^T C)^(-1)C^T.
```

Reward coordinates are identifiable in the exact model if and only if:

```text
rank(PA) = dim(theta).
```

When this holds, define:

```text
L = ((PA)^T(PA))^(-1)(PA)^T P.
```

Then:

```text
LA = I
LC = 0.
```

Thus exact context-only midpoint drift is removed rather than charged as
error. If `PA` loses rank, a reward direction is observationally confounded
with context drift.

## B. Joint bounded-error certificate

Use `||theta||_infinity`. Suppose:

```text
||Delta_i||_1 <= rho_i,
|l_i| <= eta_i,
|m_i| <= kappa_i,
|s_j| <= epsilon_j.
```

Let the nominal estimator be:

```text
theta_hat = L y.
```

Define the additive image radius:

```text
a =
max_j [
  sum_i |L_ji|(eta_i+kappa_i)
  + sum_t |(LD)_jt| epsilon_t
].
```

Define the mechanical feedback gain:

```text
lambda =
max_j sum_i |L_ji| rho_i.
```

If `lambda < 1`, then:

```text
||theta||_infinity
<= R_theta
:= (||theta_hat||_infinity + a)/(1-lambda).
```

The true quotient error is contained in the centrally symmetric zonotope:

```text
E =
L Box(eta + kappa + rho R_theta)
  + LD Box(epsilon).
```

For every decision direction `q`, its exact support function is:

```text
h_E(q) =
sum_i (eta_i+kappa_i+rho_i R_theta) |(L^Tq)_i|
+ sum_t epsilon_t |(D^T L^T q)_t|.
```

This formula retains shared-cell correlations. Replacing `Ds` by independent
per-query `2 epsilon` boxes is valid but can be strictly looser.

### Proof

Projection gives:

```text
theta_hat-theta = L Delta theta + L(l+m+Ds).
```

Hölder's inequality and the registered row bounds imply:

```text
||theta_hat-theta||_infinity
<= lambda ||theta||_infinity + a.
```

Using
`||theta||_infinity <= ||theta_hat||_infinity
 + ||theta_hat-theta||_infinity`
and solving the scalar inequality gives `R_theta`. Substituting this bound
back into each row gives the zonotope. Support functions commute with linear
images and add over Minkowski sums, proving the displayed formula.

## C. Liveness of the mechanical gate

The strict contraction is not cosmetic. In the scalar exact-design cell
`A=L=1`, drift radius `rho=1` permits `Delta=-1`, making the true design zero.
Every reward value then produces the same observation. Therefore no finite
uniform certificate exists at the boundary for the registered unstructured
row-drift class.

This does not say every structured problem with `lambda>=1` is impossible.
It says this declared norm-only certificate must abstain there.

## D. Exact robust policy handoff

Let the center estimate choose policy `pi_hat`. For competitor `pi`, let:

```text
q_pi = mu_(pi_hat)-mu_pi
m_pi = theta_hat^T q_pi.
```

Over the outer uncertainty set `theta_hat+E`, the worst-case loss of this
margin is exactly `h_E(-q_pi)`. Hence:

```text
m_pi > h_E(-q_pi) for every competitor
```

certifies unique policy identity. Equality is inconclusive.

The exact worst-case regret over the outer set is:

```text
max_pi max(0, h_E(-q_pi)-m_pi).
```

This is sharper than a global-radius-times-diameter bound whenever the
uncertainty is anisotropic or shared semantic cells cancel in the relevant
policy direction.

## E. Scope

This theorem is a consolidation of nuisance residualization, errors-in-
variables/set-membership estimation, support-function calculus, and robust
linear policy comparison. Novelty is not claimed.

It assumes:

- a fixed finite linear reward quotient;
- known source-wise deterministic bounds;
- a context nuisance basis;
- a semantically calibrated-cell incidence map;
- a finite policy family with known quotient occupancies; and
- a mechanical row-drift class bounded in `l1`.

It does not derive those bounds from human or model data, prove minimax sample
complexity, cover strategic/non-scalar demonstrators, characterize maximal
MDP equivalence, or resolve ASMP-9.
