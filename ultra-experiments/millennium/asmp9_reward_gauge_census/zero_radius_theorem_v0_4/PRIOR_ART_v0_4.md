# ASMP-9 exact-tie width theorem: prior-art boundary

The proof is a specialization of the classical Farey-neighbor property.
Consecutive fractions `a/b<c/d` in the Farey sequence of order `N` satisfy
`bc-ad=1` and every fraction strictly between them has denominator at least
`b+d>N`. When `N=B-1`, an interval can contain at most one reduced fraction
with denominator at most `B`.

The remaining ingredients are elementary:

- coordinate-sign queries;
- reconstruction of a positive ray from pairwise coordinate ratios; and
- primitivity to choose one representative per rational ray.

The surrounding one-bit measurement and reward-invariance literature is
recorded in:

- `../ordinal_frontier_v0_2/PRIOR_ART_v0_2.md`; and
- `../width_theorem_v0_3/PRIOR_ART_v0_3.md`.

Accordingly, the exact-zero formula should be presented as a classical
Farey-sequence corollary packaged as an ASMP-9 access theorem, not as new number
theory. A literature review should still check whether this precise
coefficient-width statement already appears in finite one-bit recovery or
integer threshold-identification work.

