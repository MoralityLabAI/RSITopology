# ASMP-9 v0.21 development note

## Pre-registration work

Development used only previously burned graphs:

- triangle;
- diamond;
- theta graph;
- `K4`;
- a one-point union of two triangles; and
- every one of the 1,024 simple labelled graphs on five vertices.

Across that universe, explicit total-orientation enumeration agreed exactly
with the independent deletion-contraction implementation of `T_G(0,2)`.
The bridge control also confirmed the required scope distinction: classical
total cyclicity is impossible in the presence of a bridge, while the ASMP
quotient event removes original bridges.

The development implementation and nine tests were committed as:

```text
ca7ca070dc614ea5f38a364b2df100cdf3c839fb
```

## Prior-art audit

Before freezing the protocol, the following source claims were checked:

- Las Vergnas owns the orientation interpretation;
- Jaeger, Vertigan, and Welsh's graphic Tutte dichotomy includes `(0,2)` in
  the #P-hard region; and
- Oliveira, Hiraishi, and Imai describe the counting problem as known
  #P-hard and give classical parameterized algorithms.

Accordingly, v0.21 claims only an ASMP access-object translation and
localization, not new graph-enumeration mathematics.

## Fresh-cell handling

The burned registry contains 29 graph-shaped records extracted from all
earlier ASMP-9 machine-readable protocols.  The proposed wheel, Petersen,
pentagonal-prism, subdivided-`K4`, bridge-control, and block-product full
graphs have zero exact-isomorphism matches in that registry.

Only topology, biconnectivity, bridge count, pairwise nonisomorphism, and
freshness were inspected before registration.  No totally cyclic count,
Tutte value, ASMP numerator, or availability was computed on a registered
v0.21 cell before the registration artifact was sealed.

