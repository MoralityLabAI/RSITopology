# ASMP-9 sharp query-width theorem verification protocol v0.3

## Status

Prospective verification protocol. The construction-development grid used
`d=2, B=1..16`, `d=3, B=1..4`, and `d=4, B=1..2`. The claim-verification
grid below is disjoint wherever it tests new full ray universes. No
claim-verification output may be read before this protocol, the theorem draft,
prior-art note, implementation, tests, and runner are committed and hashed.

## Purpose

Verify the constructive proof and extremal witnesses for the proposed
dimension-uniform coefficient-width theorem. This is a theorem-seed
verification protocol, not an empirical preference experiment.

## Frozen theorem target

For primitive integer reward rays of infinity-norm at most `B`, positive scale
quotiented, dimension at least two, and adversarial additive comparison
threshold `0 <= delta < 1`, the smallest query coefficient width sufficient in
the worst case is:

```text
2        when B=1;
2B-1     when B>=2.
```

## Frozen independent verification grid

- construction replay over every ray pair for:
  - `d=2, B=17..24`;
  - `d=3, B=5`;
  - `d=4, B=3`;
- exhaustive lower-witness query search for `d=2, B=33..64`;
- randomized property replay for `d in {5,8,16}`, `B in {2,4,8}`, with seeds
  `{90210,90211,90212}` assigned lexicographically and 4096 distinct ray pairs
  per cell;
- symbolic checks of every algebraic branch in the equal-extreme case.

## Gates

1. Every constructed query has strict opposite integer scores.
2. Every constructed query has width at most the stated formula.
3. Every lower witness is primitive and inside the reward bound.
4. No query below the stated width separates any lower witness.
5. The proof implementation and brute-force separator enumeration agree on all
   development fixtures in `test_width_theorem.py`.

Passing all gates yields
`sharp_query_width_theorem_implementation_verified`.

## Claim boundary

Passing verifies the implementation and supplies broad counterexample coverage;
the written proof carries the theorem. It does not establish novelty or solve
the behavioral, discounted, finite-sample, or inconsistent-demonstrator parts
of ASMP-9.

## Resources

CPU only; 4 GiB RAM; 10 minutes total wall time; no GPU.
