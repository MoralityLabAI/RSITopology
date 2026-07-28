# ASMP-9 conditional-fiber exact-arithmetic repair v0.13.1

## Cause

The v0.13 registered attempt materialized large arrays of exact integer
weights and asked `Fraction` to reduce enormous numerator/denominator pairs.
It exceeded the 180-second cap and approached the 2-GiB memory cap before
emitting any result.

## Repair

The v0.13.1 implementation:

- streams exact null and alternative normalizers in one forward pass;
- locates the exact randomized rejection boundary in one reverse pass;
- keeps the power as an unreduced integer ratio;
- verifies size and power-band inequalities by exact cross multiplication;
  and
- emits byte hashes and bit lengths for the exact integers plus a 30-digit
  decimal rendering.

No scientific input, cell, threshold, gate, resource cap, or claim boundary
changes.

## Pre-registration equivalence

The streaming and literal implementations agreed exactly on 36 burned cells:

```text
k in {3,4,6}
n in {1,2,5,9}
R in {3/2,2,5/2}
alpha = 1/20
```

Agreement covered rejection boundary, randomized-boundary probability, and
power as exact rational numbers.

On the largest burned preflight analog:

```text
k = 16
n = 4833
R = 4/3
```

the streaming implementation completed in `5.66` seconds and returned:

```text
power = 0.803227561306324966654389277106
```

inside the unchanged `[0.78,0.82]` band. This benchmark is burned
implementation evidence, not a registered scientific result.
