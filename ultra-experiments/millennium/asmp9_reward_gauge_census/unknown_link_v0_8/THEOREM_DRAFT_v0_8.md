# Unknown response links enlarge the value gauge

## Status

Development theorem draft. The semiparametric single-index identifiability
issues are classical. This document isolates their finite paired-comparison
consequence for ASMP-9.

## Response model

For items with scalar utilities `u_1,...,u_n`, let:

```text
P(j preferred to i) = F(beta (u_j-u_i)),
```

where `beta>0` and:

```text
F(-x)=1-F(x), F(0)=1/2,
```

with `F` strictly increasing.

The observation is the exact complete pairwise probability law. This is a
population oracle; finite-sample estimation is not part of the current
theorem.

## Theorem 1: unknown temperature is scale gauge when the link is known

If `F` is known and injective, the complete law determines:

```text
v_i = beta (u_i-u_root)
```

on each connected comparison component. Unknown positive `beta` therefore
introduces no ambiguity beyond positive utility scale, plus one additive
constant per component.

This result holds on any connected comparison graph after applying `F^-1` to
the observed probabilities and using the v0.7 scalar-coherence test.

## Theorem 2: an unknown monotone link creates non-affine ambiguity

Let the nuisance class contain every strictly increasing symmetric link. For a
generic finite utility vector, the complete probability law determines at
most the labelled weak order of its pairwise utility differences.

More precisely, suppose two utility vectors `u,u'` have the same equality and
order relations among every labelled oriented difference:

```text
u_j-u_i.
```

For every admissible link `F`, there is an admissible link `F'` such that:

```text
F(u_j-u_i) = F'(u'_j-u'_i)
```

for every ordered pair `(i,j)`.

### Proof

The shared labelled difference order defines a strictly increasing odd map
`g` from the finite set of differences of `u'` to the corresponding
differences of `u`. Extend `g` to a strictly increasing odd function on the
real line by piecewise-linear interpolation and monotone tails. Then:

```text
F'(x)=F(g(x))
```

is strictly increasing and symmetric, and agrees on every observed pair.

Repeated observations cannot break this ambiguity because the entire response
law, not only its mean estimate, is identical.

## Exact three-item counterexample

Take:

```text
u  = (0,1,3),
u' = (0,1,4).
```

They are not related by a positive affine transformation: normalizing the
first nonzero gap to one leaves final coordinates `3` and `4`.

Use the rational symmetric link, for `x>=0`:

```text
F(x) = 1/2 + x/(2(1+x)),
F(-x)=1-F(x).
```

The positive-gap probabilities are:

```text
F(1)=3/4, F(2)=5/6, F(3)=7/8.
```

Define `F'` on the positive half-line by strictly increasing interpolation
through:

```text
(0,1/2), (1,3/4), (3,5/6), (4,7/8),
```

with a strictly increasing tail to one, and extend by symmetry. Then the
complete labelled pairwise laws of `(u,F)` and `(u',F')` are exactly equal.

Three items are minimal: with only two distinct utilities, every nonzero gap
is related to every other by positive scale.

For three ordered items written:

```text
u=(0,a,a+b), a>0, b>0,
```

the labelled difference order records only whether `a<b`, `a=b`, or `a>b`.
After quotienting positive affine transformations, the utility ray is
parameterized by the ratio `a/b`. Thus each strict class contains a continuum
of observationally equivalent, non-affine utility rays when the link may vary.

## Access consequence

Complete pairwise probabilities do not identify a utility ray when the
response link is an unrestricted monotone nuisance over a finite item design.
To recover more than labelled difference order, an access protocol must add at
least one of:

- a known parametric link;
- a sufficiently restrictive normalized link class;
- a rich intervention family that calibrates the link away from the observed
  finite gaps; or
- an explicitly weaker target, such as an ordinal preference object.

This is not contradicted by positive semiparametric single-index theorems that
assume rich covariate support and normalization. The finite complete graph
supplies only finitely many design points.

## Claim boundary

This is an exact finite-design nonidentifiability statement. It does not
characterize the minimal rich intervention family, finite-sample estimation,
context-dependent links, or general IRL. Novelty is not claimed.
