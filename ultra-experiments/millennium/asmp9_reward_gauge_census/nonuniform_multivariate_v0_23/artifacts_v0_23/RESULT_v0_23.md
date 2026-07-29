# ASMP-9 v0.23 result: exact nonuniform value and an exchange trap

## Verdict

```text
nonuniform_multivariate_and_exchange_obstruction_established_v0_23
```

All eleven prospectively registered gates passed.  A separate implementation
then passed all 21 independent verification checks.

This closes one representation gap and one tempting optimizer hypothesis.  It
does not classify the global maximin optimizer.

## Theorem 1 — exact heterogeneous-count representation

Let `G=(V,E)` be a finite simple biconnected comparison block.  At
`epsilon=1/2`, give edge `e` an arbitrary positive integer trial count `n_e`
and write:

```text
z_e = 2^(-n_e),
N = sum_e n_e.
```

The exact probability that the residual comparison object is live is:

```text
F_G(n)
  = - product_e z_e
      Z_G(-1,{z_e^(-1)-1})
  = -2^(-N) Z_G(-1,{2^(n_e)-1}),
```

where:

```text
Z_G(q,{v_e})
  = sum_{A subset E} q^k(A) product_{e in A} v_e
```

is the classical multivariate Tutte/random-cluster polynomial.

This identity is a direct edge-multivariate lift of Backman's weighted
strongly connected partial-orientation formula.  The graph polynomial and
orientation machinery are prior art; the contribution here is their exact
translation into the ASMP-9 conditional-access ledger.

### Coefficient certificate

For a fixed bidirected/interior edge set `B`, the coefficient identity is:

```text
number of strong oriented completions with bidirected set B
  = -sum_{A superset B} (-1)^k(A).
```

It follows by contracting `B` and applying the classical
`T_{G/B}(0,2)` interpretation of totally cyclic orientations.  The run
checked this identity by two independent finite enumerations on six
prospectively registered masks.

## Theorem 2 — an infinite strict local trap on K4

Order the K4 edges as:

```text
(01,02,03,12,13,23).
```

For every integer `s>=2`, define:

```text
trap     x_s = (s-1,s,s+1,s+1,s,s-1),
balanced y_s = (s,s,s,s,s,s).
```

Both use `6s` trials.  With `t=2^s`, the common-denominator numerator for
opposite-pair powers `x,y,w` is:

```text
S(x,y,w)
  = (xyw)^2 - 2(x^2+y^2+w^2) - 8xyw
    + 12(x+y+w) - 24.
```

The balanced point is strictly better:

```text
S(t,t,t)-S(t/2,t,2t)
  = 3t(3t-4)/2 > 0.
```

Nevertheless, every feasible one-unit transfer out of `x_s` strictly lowers
the objective.  The thirty ordered moves for `s>2` fall into nine factor
classes, all positive for `t>=4`.  At `s=2`, the ten moves that would violate
the positive-count floor are excluded and the remaining twenty are still
strictly worse.

Therefore `x_s` is a strict suboptimal one-exchange local maximum for every
`s>=2`.

## Theorem 3 — explicit non-M-concavity

Take `x=x_s`, `y=y_s`, either high edge `i`, and either eligible low edge
`j`.  The exchange-axiom deficit is:

```text
f(x)+f(y)-f(x-e_i+e_j)-f(y+e_i-e_j)
  = t^2(4t-5)/2 > 0.
```

Both possible low-edge choices violate the inequality that M-concavity would
require for at least one `j`.  Hence the fixed-total K4 objective is not
M-concave.

The consequence is precise: one-unit exchange ascent has no general
global-optimality guarantee for this frozen ASMP objective.  This is not an
optimizer-hardness or approximation theorem.

## Fresh validation block

The fresh graph was a seven-vertex, eleven-edge biconnected block selected
using structural predicates only and verified nonisomorphic to every entry in
the frozen burned registry.  No polynomial or availability outcome on the
graph was read before registration.

The three heterogeneous count cells matched exactly:

| cell | total trials | common-denominator numerator | reduced exact availability |
|---|---:|---:|---:|
| heterogeneous A | 36 | 64,521,765,108 | 16,130,441,277 / 17,179,869,184 |
| heterogeneous B | 37 | 134,409,854,628 | 33,602,463,657 / 34,359,738,368 |
| heterogeneous C | 36 | 67,098,427,236 | 16,774,606,809 / 17,179,869,184 |

For every row:

```text
direct 3^|E| residual-status census
  = edge-multivariate q=-1 evaluation.
```

The coefficient checks were:

| interior mask | direct completions | polynomial coefficient |
|---:|---:|---:|
| 0 | 336 | 336 |
| 1 | 258 | 258 |
| 21 | 126 | 126 |
| 341 | 60 | 60 |
| 1365 | 32 | 32 |
| 2047 | 1 | 1 |

Uniform counts `r=2` and `r=4` also reproduced the ordinary Backman/Tutte
specialization exactly.

## Fresh K4 implementation checks

The family theorem was derived symbolically before registration.  The
registered values `s={9,11,17}` were fresh numeric checks of the sealed
implementation, not fresh evidence for the already-derived algebraic family.

| `s` | trap numerator | balanced numerator | balanced − trap | smallest trap − neighbor gap |
|---:|---:|---:|---:|---:|
| 9 | 18,014,397,433,009,128 | 18,014,397,434,185,704 | 1,176,576 | 133,301,760 |
| 11 | 73,786,976,226,074,775,528 | 73,786,976,226,093,637,608 | 18,862,080 | 8,575,260,672 |
| 17 | 5,070,602,400,912,899,591,407,920,218,088 | 5,070,602,400,912,899,591,485,228,842,984 | 77,308,624,896 | 2,251,739,684,536,320 |

All nine move-factor classes appeared at every registered `s`; every
trap-minus-neighbor gap was positive; every balanced-minus-trap gap equaled
its closed form; and all four registered M-concavity exchange deficits per
cell were positive and exact.

## Gate record

| gate | result |
|---|---|
| G0 registration binding | pass |
| G1 freshness and structure | pass |
| G2 multivariate identity | pass |
| G3 coefficientwise identity | pass |
| G4 uniform specialization | pass |
| G5 K4 closed forms | pass |
| G6 strict local maximum | pass |
| G7 strict suboptimality | pass |
| G8 M-concavity violation | pass |
| G9 structured attribution | pass |
| G10 resource and scope | pass |

## Reproducibility

```text
prereveal implementation commit:
  1383f21c7a53e1d273d4139f95cff0c336d77e5f

registration commit:
  e45d94b

registration SHA-256:
  7ed6486f26193cfc8870badacde54184f9567b5fe348ad88a76166544a6f8f9e

result SHA-256:
  3733e73324905fbb7b1d44817a46607539409126c39a0120c73e372d8a4eae92

independent verification:
  21 / 21 checks passed

wall time:
  9.633018699998502 seconds

peak resident memory:
  39,989,248 bytes

GPU:
  not used
```

## Claim boundary

Established:

- the exact edge-multivariate representation for arbitrary positive integer
  counts at `epsilon=1/2` on one finite simple biconnected block;
- the infinite K4 strict-local/suboptimal family;
- a direct M-concavity exchange-axiom violation; and
- failure of a general global guarantee for one-unit exchange ascent.

Not established:

- the global maximin optimizer on arbitrary biconnected blocks;
- optimizer-search hardness, approximation complexity, or inapproximability;
- arbitrary endpoint probabilities or `epsilon`;
- adaptive allocation, dependent responses, or response misspecification;
- behavioral reward identification or general IRL; or
- ASMP-9 resolution.
