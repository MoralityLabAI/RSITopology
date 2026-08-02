# ASMP-4 v0.12 classical NHIM definition scope

## Checked source

The primary source is Berger and Bounemoura,
[*A geometrical proof of the persistence of normally hyperbolic submanifolds*](https://arxiv.org/pdf/1109.3280),
[arXiv DOI](https://doi.org/10.48550/arXiv.1109.3280).  PDF pages 3 and 4
were rendered and visually checked.  Definition 1 requires a smooth ambient
manifold, a `C^1` diffeomorphism, a closed compact connected invariant
submanifold, an invariant `E^s/E^u/TN` splitting, normal hyperbolicity, and
tangent domination.  Theorem 2.1 states persistence for that class.

## Exact mapping

Use the smooth cylinder `C=S^1 x R` and the global diffeomorphism

```text
f(theta,n)=(theta+1/4 mod 1,(3/2)n).
```

Its inverse is `(theta-1/4 mod 1,(2/3)n)`.  The circle
`N=S^1 x {0}` is closed, compact, connected, smooth, invariant, and genuinely
one-dimensional.  Along `N`,

```text
E^s={0}, E^u=span(d/dn), TN=span(d/dtheta).
```

The tangent norm is `1` and the unstable inverse norm is `2/3`.  Choosing
`lambda=3/4` gives

```text
2/3 < 3/4 < 1,
(2/3)*1 < 3/4.
```

These are Definition 1's normal-hyperbolicity and domination inequalities.
The source explicitly permits `E^s={0}`, calling this the normally expanded
case.

## Scope controls

This extension removes the zero-dimensional-manifold objection.  It does not
prove positive-volume confinement: the invariant circle still has zero ambient volume
in the two-dimensional cylinder.  It does not claim that ASMP-4 selected this
classical definition, the cylinder plant, or either sensor registry.  External
expert review remains absent.
