# ASMP-9 corrected sharp-width verification protocol v0.3.1

## Status

Prospective repair of the v0.3 scope error. Version 0.3 remains immutable and
scientifically superseded. Version 0.3.1 changes the theorem domain from
`0<=delta<1` to `0<delta<1`, adds a zero-radius discontinuity control, and uses
fresh full-pair cells and seeds.

## Frozen theorem

For primitive integer reward rays bounded by `B`, dimension at least two,
positive scale quotiented, and `0<delta<1`, the exact universal robust
comparison width is:

```text
2        at B=1;
2B-1     at B>=2.
```

## Fresh verification grid

- every ray pair:
  - `d=2`, `B=25..32`;
  - `d=3`, `B=6`;
  - `d=5`, `B=2`;
- exhaustive lower-witness search at `d=2`, `B=65..96`;
- 4096 seeded pairs in:
  - `(d=6,B=3,seed=90310)`;
  - `(d=10,B=5,seed=90311)`;
  - `(d=20,B=9,seed=90312)`;
- endpoint-discontinuity controls at `B in {1,2,8,32}`.

## Gates

1. registration and hashes valid;
2. every constructed query gives strict opposite scores;
3. every constructed query respects the sharp bound;
4. every lower witness is primitive and has no narrower strict-opposite query;
5. every full-pair universe is exhausted;
6. each endpoint control is separated by a narrower tie query at `delta=0`
   but not by that query under `delta=1/2`.

## Decision

All gates passing yields:

```text
corrected_sharp_query_width_theorem_implementation_verified.
```

Any failure invalidates the verification. Passing does not establish novelty;
the written proof carries the theorem.

## Resources

CPU only; 4 GiB RAM; 10 minutes; no GPU.

