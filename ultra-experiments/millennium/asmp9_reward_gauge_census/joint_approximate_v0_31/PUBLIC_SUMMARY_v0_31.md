# ASMP-9 joint approximate certificate v0.31

## Result

Version v0.31 establishes one deterministic composition rule for the finite
linear reward-quotient setting developed in v0.27-v0.30.

The observation model is

```text
y = (A + Delta) theta + C b + l + m + D s.
```

The result does four things that a scalar “add the error bars” treatment
would miss:

1. it projects exact context-only midpoint drift out rather than charging it
   as error;
2. it retains reuse and cancellation among semantic-calibration cells;
3. it imposes a live small-gain condition on multiplicative mechanical
   occupancy drift; and
4. it propagates the resulting zonotope directly into policy margins and
   regret.

For

```text
L = ((PA)^T(PA))^(-1)(PA)^T P,
P = I - C(C^T C)^(-1)C^T,
```

the exact access condition is `rank(PA)=dim(theta)`. When it holds, `LA=I`
and `LC=0`.

With registered row-drift widths `rho`, localization widths `eta`,
non-context midpoint widths `kappa`, and semantic-cell widths `epsilon`, the
mechanical gain is

```text
lambda = max_j sum_i |L_ji| rho_i.
```

If `lambda<1`, a finite reward radius follows, together with a zonotope whose
support in any policy direction can be computed exactly. At `lambda=1`, a
registered scalar witness erases the measurement channel entirely, so the
strict gate is not decorative.

## Registered execution

The original registered v0.31 invocation produced no output because its
Windows resident-memory helper failed after the in-memory calculation. That
attempt remains recorded as
`unavailable_resource_meter_failure_before_output`.

A separately registered v0.31.1 repair imported the sealed original runner
and replaced only the faulty resource query. It did not copy or alter the
scientific calculation, fixtures, thresholds, gates, or verifier.

The repaired execution returned:

```text
scientific gates                 12/12 pass
independent scientific checks    29/29 pass
repair-integrity checks          10/10 pass
runtime                          0.0156254 seconds
peak resident memory             19,697,664 bytes
GPU                              none
```

The primary exact-rational fixture had projected rank `3`, mechanical gain
`1/50`, additive radius `37/1500`, and reward radius `18197/11760`. All seven
registered directions covered the planted joint realization. The support
`90263/588000` in direction `(2,-3,1)` was attained by an explicit source
vertex.

The selected primary policy was uniquely certified over the outer set with
zero robust regret. A separate risk fixture attained its exact regret bound
`9/10`. An anisotropic control was certified by the zonotope
(`1/100` directional support against a `1/5` margin) but not by the
max-coordinate scalar relaxation (`9/10`). A shared-cell semantic control
had zero structured support while an independent-row surrogate reported
`1/5`.

## What changed in the ASMP-9 audit

The v0.30 audit listed joint approximate factorization as the first
load-bearing missing theorem. Version v0.31 closes that item under registered
deterministic source bounds.

It does not close the remaining empirical and general obligations:

- behavioral acquisition of the semantic rectangle and its source widths;
- stochastic, dependent-response sample complexity;
- coarser mechanics equivalences than exact registered occupancy rows;
- maximal invariance under richer reward and demonstrator classes; and
- a general no-go/classification theorem for incoherent latent value.

ASMP-9 therefore remains unresolved.

## Claim boundary

This is an exact finite theorem and executable instrument for one declared
linear access model. It is not evidence that human or model preferences obey
that model, not a robust-MDP solution, not a minimax statistical theorem, and
not an ASMP-9 resolution.
