# ASMP-7 excluded-band degradation protocol v0.2

## Amendment status

This is an additive successor to v0.1. It does not alter any v0.1 protocol,
source, registration, result, or receipt.

## Question

How does the exact minimum charged-audit sample count change as the forbidden
capability boundary approaches the compliant boundary in the frozen 16-point
Boolean registry?

## Frozen model

The v0.1 target, compliant class, challenge meter, randomized-response channel,
and separate error limits are retained:

```text
X0       = {f : k(f) <= 8}
X1(k1)   = {f : k(f) >= k1}, k1 in {9,10,11,12,13,14,15,16}
FP limit = FN limit = 1/20
theta    in {1/2,3/5,2/3,3/4,4/5,1}
m        in {0,...,32768}
```

`k1=16` contains only the parity target and is labelled
`singleton_boundary_control`; it is retained as a registry boundary control,
not treated as a representative capability class.

For one report,

```text
q(k,theta) = (1-theta) + (2*theta-1)*k/16.
```

The compliant boundary is channel-invariant:

```text
q(8,theta) = 1/2.
```

The complete separation is therefore

```text
delta(k1,theta) = q(k1,theta)-1/2
                = (2*theta-1)*(k1-8)/16.
```

At `theta=1/2`, both classes collapse to `Binomial(m,1/2)` and no finite `m`
can meet both error limits.

## Exact minimum test

For each cell, use the exact size-`1/20` randomized UMP upper-tail test:

```text
declare forbidden for K > c;
declare forbidden with probability gamma for K = c;
declare compliant for K < c.
```

The implementation may use floating-point SciPy binomial functions only to
locate a candidate `m` and cutoff. It must then use integer binomial numerators
and rational arithmetic to:

1. construct the exact size-`1/20` test;
2. prove that the reported `m*` is feasible;
3. prove that `m*-1` is infeasible; or
4. when no solution is reported, prove the test at the uniform cap is
   infeasible.

Floating point cannot determine any cell status or gate. Feasibility is
monotone in `m` because the `(m+1)`-sample experiment Blackwell-dominates the
`m`-sample experiment by discarding one observation; the UMP test has at least
the power of that discarded-observation test. Thus exact adjacent checks
certify the minimum.

## Descriptive reference curve

For each nonzero gap report

```text
m_normal = [z_0.95 * (sqrt(1/4) + sqrt(q1*(1-q1))) / delta]^2.
```

Also fit `log(m*) = a + b*log(delta)` on the frozen descriptive subset of
feasible, non-singleton cells with `m*>=100`. Report `b`, `R^2`, and residuals.
The fit is explanatory only. It cannot pass or fail a scientific gate and is
not evidence for a new asymptotic law.

## Frozen gates

- **E0 exact adjacency:** every feasible cell has exact `FP=1/20`, exact
  `FN<=1/20`, and exact predecessor `FN>1/20`; every capped-infeasible cell has
  exact cap `FN>1/20`.
- **R0 v0.1 reproduction:** at `k1=14`, the v0.1 minimum counts `73,50,15` for
  `theta=3/4,4/5,1` reproduce exactly, and `theta<=2/3` remains infeasible at
  the old cap `m=128`.
- **C0 class census:** each forbidden-class cardinality equals the exact
  binomial sum `sum_{k=k1}^16 C(16,k)`.
- **O0 order:** wherever both values are finite, `m*` is nonincreasing as
  `theta` increases and as `k1` increases.
- **S0 surface liveness:** every cell with `theta>1/2` is feasible within the
  uniform cap. This is a directional gate; failure is a valid bounded result,
  not an invalid instrument.
- **B0 boundary label:** `k1=16` is labelled
  `singleton_boundary_control` in every emitted row.

## Outcome labels

Each cell is exactly one of:

- `feasible_exact`;
- `infeasible_within_uniform_cap`; or
- `invalid_exact_arithmetic`.

Any E0, R0, C0, O0, or B0 failure yields `invalid_instrument`. An S0 failure
yields `registered_surface_incomplete` without changing the cap.

## Claim boundary

This exact result concerns only the frozen Boolean registry, independent
with-replacement challenges, fresh randomized response, and assumed meter
coverage. It does not establish real-model capability attestability, a
universal compression theorem, an asymptotic sample-complexity theorem, or the
adequacy of the omitted policy band. The normal curve is descriptive.

