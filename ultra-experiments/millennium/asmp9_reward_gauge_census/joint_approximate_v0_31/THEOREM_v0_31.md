# Joint approximate quotient certificate

## Status

This document records the mathematical statement exercised by
`ASMP-9-JOINT-APPROXIMATE-v0.31`.

It is a finite deterministic composition theorem. It consolidates classical
nuisance residualization, set-membership estimation, support-function
calculus, and robust linear policy comparison. No novelty is claimed for
those ingredients.

## Setting

Let `theta` be a `p`-dimensional reward coordinate after quotienting a
declared decision-null gauge. The localized scalar observations satisfy

```text
y = (A + Delta) theta + C b + l + m + D s.
```

Here:

- `A` is the nominal quotient occupancy design;
- `C b` is arbitrary context-only midpoint drift in a declared nuisance
  subspace;
- `Delta` is mechanical occupancy-row drift;
- `l` is threshold-localization error;
- `m` is midpoint residual outside the declared context model; and
- `D s` is semantic-calibration residual, where `D` records reuse of the
  same semantic cells by different observations.

Assume `C` has full column rank, allowing the zero-column case, and define

```text
P = I - C(C^T C)^(-1)C^T.
```

All uncertainty widths below are fixed independently of the realized
observation.

## Theorem 1: exact nuisance quotient

The exact model `y = A theta + C b` identifies `theta` if and only if

```text
rank(PA) = p.
```

When this condition holds, define

```text
L = ((PA)^T(PA))^(-1)(PA)^T P.
```

Then

```text
LA = I_p
LC = 0.
```

Consequently, arbitrary drift in the registered context subspace is removed
exactly and should not be charged as approximation error.

### Proof

Because `P` is the orthogonal projector onto the complement of `col(C)`,
projecting the exact model gives `Py = PA theta`. Full column rank of `PA`
therefore gives the displayed left inverse. Conversely, if `PA` is rank
deficient, some nonzero `h` satisfies `PAh = 0`, hence `Ah` lies in
`col(C)`. A change from `theta` to `theta+h` can then be cancelled by a
change in `b`, so `theta` is not identified. The identities for `L` follow
from its definition and `PC=0`. QED.

## Theorem 2: joint deterministic outer certificate

Use the infinity norm on `theta`. Suppose the registered source bounds are

```text
||Delta_i||_1 <= rho_i,
|l_i| <= eta_i,
|m_i| <= kappa_i,
|s_t| <= epsilon_t.
```

Let

```text
theta_hat = L y,
```

and define

```text
a =
max_j [
  sum_i |L_ji| (eta_i + kappa_i)
  + sum_t |(LD)_jt| epsilon_t
],

lambda = max_j sum_i |L_ji| rho_i.
```

If `lambda < 1`, then

```text
||theta||_infinity <= R_theta

R_theta =
(||theta_hat||_infinity + a) / (1 - lambda).
```

Moreover, the true reward coordinate belongs to `theta_hat + E`, where the
centrally symmetric outer zonotope is

```text
E =
L Box(eta + kappa + rho R_theta)
  + LD Box(epsilon).
```

Its support function is exactly

```text
h_E(q) =
sum_i (eta_i + kappa_i + rho_i R_theta) |(L^T q)_i|
+ sum_t epsilon_t |(D^T L^T q)_t|.
```

"Exactly" here refers to the support of the constructed outer zonotope. The
zonotope can conservatively contain source combinations that the underlying
mechanical model cannot realize jointly.

### Proof

The identities in Theorem 1 give

```text
theta_hat - theta = L Delta theta + L(l + m) + LDs.
```

For coordinate `j`, Hölder's inequality and the rowwise drift bounds give

```text
|(L Delta theta)_j|
<= [sum_i |L_ji| rho_i] ||theta||_infinity.
```

The additive terms are bounded coordinatewise by the definition of `a`.
Therefore

```text
||theta_hat - theta||_infinity
<= lambda ||theta||_infinity + a.
```

Combining this with

```text
||theta||_infinity
<= ||theta_hat||_infinity
 + ||theta_hat-theta||_infinity
```

and solving the scalar inequality proves the radius bound. Substituting
`R_theta` into each rowwise mechanical bound gives the outer zonotope.
Support functions commute with linear images, add under Minkowski sums, and
the support of `Box(w)` in direction `z` is `sum_i w_i |z_i|`. This proves
the formula. Central symmetry absorbs the sign between estimation error and
parameter error. QED.

## Proposition 3: the strict mechanical gate is live

For the unstructured row-drift class in Theorem 2, the boundary
`lambda = 1` cannot be admitted uniformly.

### Witness

Take the scalar cell `A=L=1`, no additive error, and `rho=1`. The admissible
choice `Delta=-1` erases the measurement channel:

```text
y = (1-1) theta = 0
```

for every `theta`. No finite uniform reward certificate is possible in this
cell.

This witness does not prove that every structured problem with gain at least
one is impossible. It proves that the declared norm-only certificate must
abstain at the boundary.

## Theorem 4: exact decision calculation over the outer set

Let a finite policy family have quotient occupancies `mu_pi`. Let
`pi_hat` maximize `theta_hat^T mu_pi`, and for each competitor define

```text
q_pi = mu_pi_hat - mu_pi,
m_pi = theta_hat^T q_pi.
```

Over the constructed uncertainty set `theta_hat + E`:

```text
minimum true margin against pi
= m_pi - h_E(-q_pi).
```

Thus

```text
m_pi > h_E(-q_pi)
```

for every competitor certifies that `pi_hat` is the unique optimizer
throughout the outer set. Equality is inconclusive.

The exact worst-case regret over that same outer set is

```text
max_pi max(0, h_E(-q_pi) - m_pi).
```

### Proof

For `theta = theta_hat + e`, the competitor's advantage is

```text
theta^T(mu_pi-mu_pi_hat) = -m_pi + e^T(-q_pi).
```

Maximizing the last term over `E` gives `h_E(-q_pi)`. Taking the positive
part and the maximum over the finite policy family proves both statements.
QED.

## Corollary: why the set shape matters

Replacing `E` by an infinity-norm box of radius
`max_j h_E(e_j)` remains conservative, but can fail to certify a policy that
the zonotope certifies. Likewise, replacing `Ds` by independent row errors
can lose exact cancellations created by reuse of the same semantic cell.

The registered controls exhibit both separations.

## Claim boundary

This theorem assumes:

- a fixed finite linear reward quotient;
- a declared context nuisance basis;
- known source-wise deterministic widths;
- a known semantic-cell incidence map;
- a finite policy family with known quotient occupancies; and
- rowwise `l1` mechanical-drift bounds.

It does not derive those widths from human or model behavior, establish
minimax stochastic sample complexity, cover strategic or non-scalar
demonstrators, characterize a maximal MDP equivalence, prove that a real
semantic numeraire exists, or resolve ASMP-9.
