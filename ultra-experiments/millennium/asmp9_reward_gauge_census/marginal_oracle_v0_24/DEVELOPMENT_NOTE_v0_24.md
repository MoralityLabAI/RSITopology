# ASMP-9 v0.24 development note

## Why this branch exists

Version v0.23 gave the exact edge-multivariate objective and refuted
one-exchange/M-concavity optimization.  It did not classify the global
optimizer.

Two successor routes were examined:

1. a universal balanced optimum at `epsilon=1/2`; and
2. recovery of hard value information from exact local marginal gains.

The first route is false.  The double-triangle ladder cell in
`THEORY_DRAFT_v0_24.md` is an exact burned counterexample.

The second route yields a clean theorem.  Uniform availability is a
degree-at-most-`m` polynomial with known value one at zero.  Exact ratios at
`m+1` dyadic nodes therefore determine its scale as well as its shape.
Per-edge ratios telescope to those uniform ratios.

## What the executable checks

`test_marginal_oracle_v0_24.py` checks on the triangle, diamond, and K4 that:

- uniform ratios reconstruct the exact floor value;
- the recovered polynomial predicts an additional held-out dyadic point;
- `m` one-edge ratios telescope to each uniform-round ratio;
- exactly `m^2` one-edge calls recover the curve; and
- nonpositive ratios are rejected.

These are implementation and algebra checks.  They are not empirical evidence
for a complexity theorem.

## Current status

Development-only.  No protocol, registration, fresh graph registry, result,
or public summary exists.  Do not cite this directory as a completed result.

