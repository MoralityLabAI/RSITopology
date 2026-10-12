# ASMP-4 v0.11 primary NHIM definition scope

## Why this audit exists

V0.6 used the formal derivative `dF_n/du=1` while its registered action set was
binary.  That derivative is useful algebra, but a derivative with respect to a
discrete domain is not by itself an operational local-reachability theorem.
V0.11 repairs the category mismatch with a bounded interval authority and then
checks the disturbed closed loop against an explicit primary NHIM definition.

## Checked primary definition

The source is Li, Lu, and Bates, [*Normally hyperbolic invariant manifolds for
random dynamical systems: Part I - persistence*](https://users.math.msu.edu/users/liji/1.pdf),
[DOI 10.1090/S0002-9947-2013-05825-4](https://doi.org/10.1090/S0002-9947-2013-05825-4).
PDF pages 4 and 5 were rendered and visually checked.  They contain Definitions
2.1-2.4: metric dynamical base, cocycle, invariant random manifold, and normal
hyperbolicity via invariant `E^u/E^c/E^s` splitting and rate bounds.

The offline receipt freezes the URLs, page anchors, PDF hash, and the mapping of
all Definition 2.4 clauses.  The regression suite does not redownload the PDF.

## Exact mapping

Let the base be the bi-infinite full shift

```text
Omega={-3,-1,1,3}^Z
```

with its invertible left shift and any full-support Bernoulli measure.  The
smooth fiber is `X=R`, with evaluator-normal coordinate `n`.  The current
observed mode is `z_t=omega_t`.  Under the safe feedback `u_t=q(z_t)`, the
closed-loop fiber cocycle is

```text
phi(k,omega,n)=(3/2)^k n,  k in Z.
```

The random manifold is the compact connected smooth point `M(omega)={0}`.  Its
splitting is

```text
E^u=R,  E^c={0}=T_0 M(omega),  E^s={0}.
```

The unstable restriction is an isomorphism.  Take
`exp(alpha)=4/3 < exp(beta)=3/2`.  The unstable backward norm is exactly
`(2/3)^k`; stable and center projection bounds are vacuous.  The cocycle and
invariance equalities hold for every mode sequence, not merely almost every
one.

## Scope controls

This mapping does not claim that ASMP-4 selected this formalism.  It supplies a
concrete registered positive-class interpretation under which the same sensor
fork survives.  The safety proof remains universal over every mode sequence;
the probability measure is definitional scaffolding for the cited random-
dynamical-system category, not a relaxation to probabilistic safety.

The zero-dimensional fibers are deliberate.  A point is a compact connected
smooth zero-manifold, and its tangent/center bundle is exactly zero.  This audit
does not claim perturbation robustness, positive-volume safety, an exhaustive
NHIM literature review, external expert acceptance, or a full canonical ASMP-4
classification.
