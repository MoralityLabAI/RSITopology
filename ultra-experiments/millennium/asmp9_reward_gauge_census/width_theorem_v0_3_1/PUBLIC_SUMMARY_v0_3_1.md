# A sharp access-width theorem for robust reward comparisons

## Result

After quotienting potential shaping into cycle-return coordinates, consider
primitive integer reward rays bounded by `B` and pairwise comparison queries
with integer coefficients. Positive reward scale is treated as gauge.

For every dimension `d>=2` and every strictly positive adversarial
comparison-threshold radius below one return unit:

```text
0 < delta < 1,
```

the exact worst-case coefficient width required to distinguish every bounded
reward ray is:

```text
Q*(B) = 2        if B=1,
        2B-1     if B>=2.
```

The bound is dimension-independent and sharp.

## Why it is sharp

The upper bound is constructive. Any two independent reward rays have a
nonzero two-coordinate minor. That minor produces an integer comparison with
strict opposite scores. A short case analysis reduces the apparent `2B` bound
to `2B-1`.

The lower witness for `B>=2` is:

```text
z =(B,   B-1),
z'=(B-1, B-2).
```

Every strict-opposite comparison for this pair needs a coefficient of magnitude
at least `2B-1`. The witness embeds in every higher dimension.

Below that width, an adaptive algorithm cannot escape: after each query the
adversary can choose a response compatible with both reward rays, keeping them
on the same decision-tree path.

## The endpoint correction

The first registered version incorrectly stated the domain as
`0<=delta<1`. That version is preserved with status:

```text
superseded_scope_error_delta_zero.
```

At exactly `delta=0`, ties are observed without ambiguity and can separate two
rays even when their scores are not strictly opposite. The corrected theorem
therefore uses `0<delta<1`. Fresh controls show the same narrower query:

- separates the lower witness through a tie at `delta=0`; and
- fails to separate it at `delta=1/2`.

The zero-radius coefficient threshold is now a separate theorem target.

## Verification

The corrected version was registered before its fresh verification grid.

- 23,124,674 full-grid ray pairs checked;
- dimensions 2, 3, and 5 in the full grids;
- exhaustive lower-witness query search for bounds 65 through 96;
- 12,288 additional seeded pairs in dimensions 6, 10, and 20;
- all seven corrected gates passed;
- 28 theorem and endpoint unit tests passed; and
- the artifact verifier reproduced input hashes, output hashes, scope,
  verdict, and all gates.

The written proof carries the theorem; the census checks its implementation
and extremal branches.

## ASMP-9 contribution and remaining gap

This resolves one access-grammar subproblem: the exact coefficient width needed
for robust finite-lattice preference separation after potential shaping has
already been removed.

It does not resolve ASMP-9. Remaining resolution obligations include:

1. the separate zero-radius width and minimum-query laws;
2. finite-sample recovery under a declared stochastic response model;
3. discounted potential shaping;
4. identification from policies or demonstrations rather than direct
   trajectory comparisons; and
5. a no-go or robust positive theorem for misspecified or inconsistent
   demonstrators.

The exact formula's novelty is not established. It should be treated as a
candidate-new elementary specialization pending review by a
discrete-geometry or one-bit-recovery specialist.

