# ASMP-9 exact modulus slice development result v0.62

Status: **unregistered development result; not claim eligible**.

## Result

One continuous compact class now has exact primal and dual evaluations of both
robustness moduli introduced in v0.59-v0.60:

```text
Delta  = gamma,
Lambda = 1 + (5/2) gamma.
```

The class has three alternatives and fixed binary responses

```text
p(a|ab)=2/5,
p(a|ac)=3/5,
p(b|bc)=3/5.
```

Those binaries have Luce cycle defect `6/125`.  The RUM fiber varies along

```text
p_t(abc)=(2/5,2/5-t,1/5+t),
0<=t<=gamma/2,
```

and the non-RUM fiber varies along

```text
q_s(abc)=(2/5+s,2/5-s,1/5),
gamma<=s<=2gamma.
```

The registered development range is `0<gamma<=1/125`.  Every kernel is
positive and automatically lies in `BP_1` because `n=3`.

## Tier certificates

Every `p_t` has the explicit ranking mixture

```text
(1/5+t, 1/5-t, 1/5, 1/5-t, 0, 1/5+t)
```

in lexicographic ranking order.  It is RUM and non-Luce.

Every `q_s` has regularity violation

```text
q_s(a|abc)-q_s(a|ab)=s.
```

The maximum-menu `L1` distance from `q_s` to the RUM polytope is at least `s`:
each of the two coordinates in that regularity functional can change by at
most half the corresponding menu's `L1` distance.  Hence the non-RUM segment
lies at the promised distance at least `gamma`.

## Additive contamination modulus

For every cross-tier pair,

```text
TV(p_t,q_s)=s>=gamma.
```

The event `{a}` is the dual certificate, and every pair with `s=gamma` is a
primal witness.  Thus the exact fixed-Huber threshold is

```text
epsilon_star = gamma/(1+gamma).
```

## Multiplicative recording modulus

The `a` coordinate forces

```text
q_s(a)/p_t(a)>=1+(5/2)gamma.
```

Equality is attained at

```text
s_star=gamma,
t_star=(5/2)gamma^2.
```

At that point the `a` and `b` ratios both equal
`1+(5/2)gamma`, while the `c` ratio remains below it.  The exact
outcome-recording boundary is therefore

```text
u/ell = 1+(5/2)gamma.
```

The development verifier constructs a common record law at equality.

## Verification

```text
6 tests passed
```

The import-independent development audit reports:

```json
{
  "corruption_checks": 4,
  "gamma_cells": 4,
  "modulus_checks": 4,
  "registered": false,
  "status": "development_checks_passed",
  "tier_checks": 12
}
```

The four exact development values were:

```text
gamma in {1/4096, 3/1600, 1/200, 1/128}.
```

These finite checks validate the implementation and explicit witnesses.  The
displayed inequalities are the proof over the continuous segments.

## Interpretation

Version v0.61 established the conditional robustness ledger in terms of class
moduli but left the moduli bracketed.  Version v0.62 shows that the brackets
can be closed exactly on a continuous, non-singleton class with:

- an event-level TV dual;
- a coordinate-level likelihood-ratio dual;
- explicit RUM ranking mixtures;
- explicit non-RUM regularity witnesses; and
- constructive common observations at both corruption boundaries.

The result is intentionally a calibration slice.  It does not compute the
moduli of the full bounded-degree margin class and does not imply that either
corruption model describes a human or language model.

## Freeze decision

Do not register automatically.  Before a prospective successor:

1. obtain an independent proof review of the distance-to-RUM argument;
2. verify the common-observation constructions on fresh rational gamma cells;
3. conduct a direct prior-art/subsumption search for this robust-choice slice;
4. decide whether a one-dimensional exact slice adds enough beyond v0.61 to
   warrant claim-eligible registration; and
5. keep the next general target—higher-dimensional primal/dual moduli—separate.

## Claim boundary

This is an elementary exact development calculation on one deliberately
solvable compact slice.  It is not a general robust-choice theorem, a general
modulus algorithm, an empirical result, a welfare result, or a resolution of
ASMP-9.

