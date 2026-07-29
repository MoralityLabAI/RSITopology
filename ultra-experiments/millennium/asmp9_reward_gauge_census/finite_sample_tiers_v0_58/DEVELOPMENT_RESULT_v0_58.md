# ASMP-9 finite-sample tier development result v0.58

Status: **unregistered development result; not claim eligible**.

## Verdict

The finite-sample successor closes one conceptual gap and exposes another.

1. Exact Luce/RUM/non-RUM tier labels are not uniformly learnable at any finite
   budget, even when every menu can be queried.
2. A declared separation promise restores a total three-tier classifier.
3. The resulting sufficient sample count depends quadratically on the v0.57
   Mobius interpolation condition number and can be extremely large.
4. On the three-alternative `BP_1` slice, a certified RUM/non-RUM pair requires
   `Omega(gamma^-2)` queries, matching the upper bound's margin exponent.

Thus exact structural identifiability does not silently imply practical
certifiability.

## Two explicit boundary paths

### Luce to non-Luce RUM

On three alternatives, a signed perturbation of the uniform ranking law leaves
every binary choice at `1/2` but changes the full-menu vector to

```text
(1/3-eta, 1/3, 1/3+eta).
```

For every `eta in (0,1/6)`, this is RUM by construction and non-Luce. It
converges to the uniform Luce kernel as `eta -> 0`.

### Non-Luce RUM to non-RUM

An explicit five-ranking mixture gives a positive, non-Luce RUM kernel with

```text
p(a|abc) = p(a|ab) = 2/5.
```

Increasing only `p(a|abc)` by any sufficiently small positive `epsilon`
violates regularity, producing a non-RUM kernel arbitrarily close to the RUM
boundary.

Both paths were classified independently by the frozen v0.54 exact
three-alternative classifier.

## Finite-budget obstruction

For the first path, pairwise menu laws are identical and the only informative
query is the full menu. Its single-draw KL divergence from the uniform kernel
is

```text
-(1/3) log(1-9 eta^2).
```

For any adaptive budget `B`, KL is at most `B` times that value. Le Cam plus
Pinsker lets `eta` be chosen small enough that the maximum classification error
exceeds any frozen `delta<1/2`. This proves nonexistence of a uniform finite
sample bound for exact tier labels.

## Necessary margin rate on one exact slice

The RUM-boundary kernel has binary Luce-cycle defect `6/125`. Since that
polynomial is 6-Lipschitz in coordinate maximum error,

```text
d(q_0,Lbar) >= 1/125.
```

For `0<gamma<=1/125`, perturbing the full-menu probabilities by
`(+2 gamma,-2 gamma,0)` produces a regularity violation of `2 gamma` and hence

```text
d(q_(2 gamma),P) >= gamma.
```

The pair belongs to the declared margin promise and has
single-informative-menu KL divergence

```text
-(2/5) log(1-25 gamma^2).
```

Le Cam plus Pinsker therefore requires

```text
B >=
  2(1-2 delta)^2
  / {-(2/5) log(1-25 gamma^2)}
  = Omega(gamma^-2)
```

queries for maximum error at most `delta`. This matches the sufficient
bound's separation-margin exponent only; it is not a full minimax theorem.

## Margin-promised positive result

In maximum menuwise `L1` distance, impose one declared `gamma` promise:

- true Luce;
- RUM non-Luce at distance at least `gamma` from the Luce closure; or
- non-RUM at distance at least `gamma` from the RUM polytope.

An estimate within `gamma/3` is classified using distances to the two nested
model sets and thresholds at `gamma/2`. Equality returns `inconclusive`.

For probability floor `a`, failure probability `delta`, and v0.57 maximum
interpolation norm `K_star`, define

```text
t_gamma
  = a * {
      1 - exp[-atanh(gamma/6)/K_star]
    }.
```

With

```text
Q(n,r) = sum_(k=2)^(r+2) k choose(n,k),

N >= log(2Q/delta)/(2 t_gamma^2)
```

iid samples per observed menu suffice. The proof uses coordinatewise
Hoeffding, exact Mobius interpolation, and the sharp likelihood-ratio
oscillation bound

```text
L1 <= 2 tanh(E/2).
```

## What the transparent bound costs

Representative sufficient per-menu counts are:

| `n` | `r` | floor `a` | margin `gamma` | `K_star` | `Q` | samples/menu |
|---:|---:|---:|---:|---:|---:|---:|
| 3 | 1 | 0.20 | 0.20 | 1 | 9 | 68,407 |
| 5 | 1 | 0.05 | 0.10 | 5 | 50 | 137,247,553 |
| 6 | 2 | 0.02 | 0.05 | 17 | 150 | 45,274,968,354 |
| 8 | 4 | 0.01 | 0.02 | 129 | 952 | 78,985,466,560,742 |
| 8 | 6 | 0.01 | 0.02 | 1 | 1,016 | 4,791,534,090 |

These are conservative sufficient counts, not lower bounds. Their value is
diagnostic: interior truncation orders can make extrapolation so ill
conditioned that exact access recovery is operationally useless without much
stronger structure or a sharper estimator.

The distance oracle is explicit at the access-model level. Distance to the
RUM polytope is a finite linear program over ranking weights. Distance to the
compact semialgebraic Luce closure is decidable for fixed finite `n` by
real-closed-field methods, but no efficient implementation is claimed.

## Verification

Development tests:

```text
8 passed
```

Independent verifier:

```json
{
  "close_path_checks": 8,
  "condition_grid_checks": 65,
  "lecam_budget_target_checks": 20,
  "margin_lower_bound_checks": 3,
  "maximum_n": 12,
  "registered": false,
  "status": "development_checks_passed"
}
```

## Prior-art verdict

Le Cam, Pinsker, Hoeffding, likelihood-ratio oscillation, and contextual-choice
estimation are classical. The candidate residual is the explicit composition
of those tools with the ASMP-9 tier object and v0.57 access condition number.
Novelty is not established.

## Freeze decision

Do **not** register yet. The strongest next review questions are:

1. whether the adaptive KL argument needs any access-model qualification;
2. whether the likelihood-ratio oscillation bound is stated at the right
   metric level;
3. whether a sharper multinomial or direct log-odds estimator materially
   changes the unusable interior-order counts; and
4. whether the semialgebraic Luce-distance oracle can be replaced by a
   practical certified algorithm without changing the thresholds.

## Claim boundary

This is not a minimax-rate theorem, an efficient test, evidence about human or
model values, or a full ASMP-9 resolution. It assumes iid menu responses,
known context degree, a known observed probability floor, and a frozen
separation promise.
