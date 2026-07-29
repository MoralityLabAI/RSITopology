# ASMP-9 capped-simplex modulus development result v0.63

Status: **unregistered development result; not claim eligible**.

## Result

The one-dimensional v0.62 calibration has been replaced by a
full-dimensional exact calculation.  On the fixed binary fiber

```text
p(a|ab)=2/5,
p(a|ac)=3/5,
p(b|bc)=3/5,
```

the complete RUM region for the full-menu vector `x` is

```text
P={x in Delta_3:x_a<=2/5,x_b<=3/5,x_c<=2/5}.
```

For

```text
V(q)=sum_i(q_i-u_i)_+,
u=(2/5,3/5,2/5),
```

the exact TV distance to the RUM polygon is

```text
dist_TV(q,P)=V(q).
```

With probability floor `1/10`, `0<gamma<=1/50`, and

```text
N_gamma={q:V(q)>=gamma},
```

the two corruption moduli are

```text
Delta(P,N_gamma)=gamma,

Lambda(P,N_gamma)=1+(5/2)gamma.
```

Both are attained by

```text
p*=(2/5,3/10,3/10),

q*=(2/5+gamma,3/10-gamma/2,3/10-gamma/2).
```

## Multiplicative support certificate

If `E={i:q_i>u_i}`, `U_E=sum_(i in E)u_i`, and `d=V(q)`, then every
cross-tier pair obeys

```text
rho(p,q)
  >=max{
       1+d/U_E,
       (1-U_E)/(1-U_E-d)
     }.
```

The feasible cap sums are exactly

```text
U_E in {2/5,3/5,4/5}.
```

Their support bounds are minimized at `U_E=2/5`, giving
`1+(5/2)gamma`.  This exhausts all possible violation supports rather than
selecting a favorable pair.

## Development verification

```text
8 tests passed
```

The import-independent audit reported:

```json
{
  "common_observation_checks": 16,
  "gamma_cells": 4,
  "primal_checks": 8,
  "registered": false,
  "status": "development_checks_passed",
  "support_checks": 16
}
```

The burned gamma cells are:

```text
{1/4096,3/1600,1/200,1/50}.
```

The burned exact-grid denominators are `20` and `40`.

## Prior-art decision

The ARSP/RUM literature already gives finite polyhedral rationalizability,
and Kitamura-Stoye plus Smeulders-Cherchye-De Rock directly use distance to
that cone/polytope for statistical testing.  The result is therefore framed
as a closed-form specialization and calibration cell, not as new general
random-utility geometry.

## Freeze decision

The class is materially stronger than the v0.62 line segments and directly
answers the v0.61 matrix's request for a small nontrivial class with matching
primal and dual modulus certificates.  A prospective verification may use
only disjoint gamma cells and grid denominators, with the displayed
continuous inequalities remaining the proof.

## Claim boundary

This is an exact calculation on one three-alternative fixed-binary fiber.
It is not a general RUM-polytope algorithm, a minimax robust-choice theorem,
an empirical result, a welfare theorem, or a resolution of ASMP-9.

