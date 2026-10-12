# ASMP-9 v0.22 development note

## Prior-art correction

The first development idea was to interpolate a degree-`|E|` availability
polynomial from several uniform trial counts and recover the v0.21 count-floor
value.  That reduction was valid but unnecessarily weak.

Backman's `(k,l)`-chromatic strongly-connected partial-orientation formula
directly identifies every uniform trial count with a single Tutte point.
After substituting the ASMP state weights, all those points lie on `H_-1`,
which the Jaeger-Vertigan-Welsh theorem already classifies as hard.  The
registered theorem therefore uses the direct fixed-count result and does not
claim the interpolation observation.

## Burned development evidence

On triangle, diamond, theta, and `K4`, direct ternary-status availability
agreed with the exact weighted Tutte formula for `r in {1,2,3,4}`.  Direct
fair-microtrial enumeration also agreed on the triangle for `r in {1,2,3}`.
Twenty-five tests passed.

The development implementation was committed at:

```text
3e1fc072dca79d12eef9b768c79fa115b38b8823
```

## Fresh-cell handling

The wheel-6, octahedral, and Wagner full graphs have no exact-isomorphism
match among 35 prior protocol graph records.  The two six-vertex graphs have
10 and 12 edges respectively and therefore lie outside v0.20's burned
six-vertex/at-most-nine-edge development atlas.

Only graph structure and freshness were inspected before registration.  No
registered availability, Tutte evaluation, or microtrial numerator was read.

