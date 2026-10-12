# ASMP-9 resolution audit after v0.23

## Newly closed subproblems

### Exact nonuniform local value at `epsilon=1/2`

For arbitrary positive integer counts in one finite simple biconnected block:

```text
F_G(n)
  = -2^(-sum_e n_e) Z_G(-1,{2^(n_e)-1}).
```

This closes the representation question using classical multivariate
Tutte/partial-orientation machinery.

### One-exchange optimizer geometry

The infinite K4 family

```text
(s-1,s,s+1,s+1,s,s-1), s>=2,
```

is a strict suboptimal one-exchange local maximum and explicitly violates the
M-concavity exchange axiom.  One-unit exchange ascent therefore lacks a
general global guarantee.

## Current chain

| question | status after v0.23 |
|---|---|
| count-floor exact value inside one block | closed by v0.21 |
| fixed-uniform above-floor exact value | closed by v0.22.1 |
| exact nonuniform local-value representation at `epsilon=1/2` | closed by v0.23 |
| factorization between arbitrary blocks | closed by v0.20 |
| exact allocation between known local tables | closed by v0.20 |
| one-exchange/M-concavity global optimizer hypothesis | refuted by v0.23 |
| global maximin optimizer inside one overlapping-cycle block | open |
| optimizer-search complexity | open |
| approximation complexity | open |
| arbitrary `epsilon` and endpoint probabilities | open |
| adaptive allocation | open |
| dependent or misspecified responses | open |
| behavioral reward identification / general IRL | open |

## Correct interpretation

v0.23 is not an NP-hardness result for optimizer search.  It supplies:

1. an exact polynomial representation of the nonuniform objective; and
2. a constructive obstruction to the most immediate local-search proof.

A global algorithm may still exist.  Conversely, #P-hard declared-value
evaluation does not automatically make optimizer output #P-hard or NP-hard.

## Next theorem target

The next load-bearing question is global optimizer complexity on one
overlapping-cycle block.  A successor must either:

- reduce a known search/counting problem to optimizer output with a precise
  oracle model;
- identify a nontrivial tractable graph class and prove a global algorithm;
  or
- freeze an approximation objective and classify it.

More K4 numerics or further uniform-count confirmations would not materially
advance the resolution audit.
