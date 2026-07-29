# ASMP-9 capped-simplex modulus verification result v0.63

Status: **prospectively registered finite theorem verification**.

Verdict: **`capped_simplex_moduli_verified`**.

## Result

On the complete floor-truncated, three-alternative stochastic-choice fiber
with fixed binary responses

```text
p(a|ab)=2/5,
p(a|ac)=3/5,
p(b|bc)=3/5,
```

the random-utility full-menu laws form the capped simplex

```text
P={x in Delta_3:x_a<=2/5,x_b<=3/5,x_c<=2/5}.
```

For cap-violation mass

```text
V(q)=sum_i(q_i-u_i)_+,
u=(2/5,3/5,2/5),
```

the exact projection and cross-tier moduli are

```text
dist_TV(q,P)=V(q),

Delta(P,N_gamma)=gamma,

Lambda(P,N_gamma)=1+(5/2)gamma,
```

where every probability is at least `1/10`,
`N_gamma={q:V(q)>=gamma}`, and `0<gamma<=1/50`.

The fixed-Huber and bounded-recording ambiguity boundaries are therefore

```text
epsilon*=gamma/(1+gamma),

u/ell=1+(5/2)gamma.
```

Equality is confusable and remains non-passing.

## Matching certificates

The additive and multiplicative primal witness is

```text
p*=(2/5,3/10,3/10),

q*=(2/5+gamma,3/10-gamma/2,3/10-gamma/2).
```

The TV dual is total cap-violation mass.  The multiplicative dual exhausts
every feasible violated-facet support.  If `U_E` is the total RUM cap on a
violation support, then

```text
rho(p,q)
  >=max{
       1+gamma/U_E,
       (1-U_E)/(1-U_E-gamma)
     }.
```

The only feasible cap sums are `2/5`, `3/5`, and `4/5`; the minimum is the
`2/5` singleton support and equals `1+(5/2)gamma`.

## Prospective chronology

1. Source theorem, prior-art gate, proof audit, tests, fresh cells, primary
   verifier, and independent replay were committed and pushed as
   `6e28b6cd07c073cb5004c57bd2c56f999a408f56`.
2. The write-once registration was committed and pushed as
   `4acfb85273f6d21b30b143b200755fba87704925`.
3. Only then was `verify_v0_63.py` executed.

Registration SHA-256:

```text
5fcc7001ec7292181a5dce5252e47ed9bba48d30b3a2fee5570c52dbc434e84c
```

The burned development gamma cells and grids were explicitly excluded from
confirmation.

## Verification

All nine gates passed:

```text
H0 T0 R0 P0 M0 C0 X0 I0 RESOURCE
```

The run checked:

```text
8 unit tests;
919 fresh exact-grid laws;
919 ranking reconstructions;
153,853 exact projection comparisons;
4 fresh gamma cells;
16 support-bound checks;
12 modulus checks; and
16 corruption-boundary checks.
```

Fresh gamma cells:

```text
{1/3072,7/5000,1/256,3/200}.
```

Fresh grid denominators:

```text
{30,50}.
```

The independent implementation reproduced the complete rows, counts, gates,
and fact digest:

```text
2e59da53ab82e96c7e904916e8e78047dd62dcb6f967f61c841102ea4e672376
```

Resource use:

```text
26.56 seconds,
22,978,560 resident bytes,
1 worker.
```

## What this closes

Version v0.61 left exact evaluation of a nontrivial class modulus as the next
load-bearing finite step.  Version v0.63 closes that step on one
full-dimensional polygonal class with:

- exact primal witnesses;
- exact dual lower certificates;
- explicit equality semantics;
- exact optimizer-support identification; and
- prospective independent verification.

It is stronger than v0.62's two chosen line segments and supersedes that
slice as the relevant calibration result.

## What remains open

The next load-bearing ASMP-9 target is no longer another clean observed-menu
modulus.  It is a sharp access theorem or counterexample with hidden choice
sets and latent selection confounding, followed by strategic/dynamic response
and physical access validation.

## Claim boundary

This is an exact finite specialization of classical RUM-polytope and robust
testing geometry.  It is not a general efficient modulus algorithm, a novelty
claim for random-utility geometry, an empirical result, a hidden-menu or
latent-confounding theorem, a strategic-response theorem, a welfare theorem,
or a resolution of ASMP-9.

