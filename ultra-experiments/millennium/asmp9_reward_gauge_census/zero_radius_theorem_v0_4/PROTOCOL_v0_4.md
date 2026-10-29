# ASMP-9 exact-tie width theorem verification protocol v0.4

## Status

Prospective verification protocol. Development used full grids through
`d=2,B=8`, `d=3,B=3`, and `d=4,B=3`. The verification cells below are fresh
for the exact-tie theorem.

## Frozen theorem

For exact ternary sign comparisons at `delta=0`, primitive integer reward rays
bounded by `B`, positive scale quotiented, and `d>=2`, the exact universal
coefficient width is:

```text
1      at B=1 or B=2;
B-1    at B>=3.
```

## Verification grid

- every ray pair:
  - `d=2`, `B=9..16`;
  - `d=3`, `B=7`;
  - `d=6`, `B=1`;
- exhaustive lower-witness search at `d=2`, `B=129..160`;
- 4096 seeded pairs in:
  - `(d=8,B=4,seed=90410)`;
  - `(d=16,B=8,seed=90411)`;
  - `(d=32,B=16,seed=90412)`.

## Gates

1. all registered hashes match;
2. every constructed query produces different exact ternary signs;
3. every constructed query respects the theorem width;
4. every lower witness is primitive and bounded;
5. no query below the theorem width separates a lower witness;
6. every registered full-pair universe is exhausted;
7. the Farey-cell unit controls and small-grid constructor tests pass before
   registration.

All gates passing yields:

```text
sharp_exact_tie_width_theorem_implementation_verified.
```

## Claim boundary

The written Farey proof carries the theorem. The run verifies its
implementation on fresh finite cells. This is not a novelty claim, a
finite-sample result, behavioral IRL, discounted shaping, or a full ASMP-9
resolution.

## Resources

CPU only; 4 GiB RAM; 10 minutes; no GPU.

