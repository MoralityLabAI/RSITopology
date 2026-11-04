# Reviewer packet v0.16

## Claim

For the declared positive-volume collar and forced registered partition `P`, feasibility holds iff `P` refines the `q` fibers. A feasible `k`-block partition has exact region `[1+log2(k),infinity) x [2,infinity)`, with the stated finite-margin word counts.

## High-value falsification attempts

- Find a sixteenth unlabeled partition of four modes or a missed feasible partition.
- Give a safe first control for two `n=0` states sharing one sensor block when their `q` values are 0 and 8.
- Compress the forced `P`-symbol transcript below `k^T` words while retaining every symbol word injectively.
- Make one control word cover more than `2/2^T` initial normal length.
- Exhibit a feasible refinement edge that lowers read rate or changes write rate.

## Reproduction

Run the three commands in `README.md`. Compare the central recursive partition generator with the independent label-assignment generator, then inspect the contract and frozen claim JSON.

## Scope

The theorem is complete for the finite partition grammar of this one plant. General sensor kernels, noisy observations, memory-constrained encoders, continuous observation spaces, and the global ASMP-4 variational theory remain outside the claim.
