# ASMP-9 v0.25 post-run note

## Chronology

1. The theorem draft, primary-source dispositions, protocol, fresh cells,
   runner, verifier, environment lock, and tests were committed and pushed at
   `0f1795360faf5b250316d97b1e5a4032f8dd263f`.
2. `registration_v0_25.json` sealed 15 files with implementation commit
   `0f17953...` and SHA-256
   `6b839a8ac1bfbf46b28a016061e243f3e8d0c8e4385c69c802d26168b25a83fd`.
   That record was committed and pushed at
   `f1c4bf3a9ca100512ea61dbad629ee008d6cb8b6`.
3. The fresh formula, smoothing, and optimizer cells were evaluated only
   after both commits were public.

No gate, fresh cell, threshold, claim boundary, or resource cap changed after
registration.

## Outcome

All nine registered gates passed.  The verdict is
`generalized_theta_reduction_established_v0_25`.

- Three fresh heterogeneous path-state cells matched the independent v0.23
  multivariate evaluator exactly.
- The fresh `(2,3,4)` smoothing census checked 43,740 admissible one-unit
  transfers.  Every transfer strictly improved the numerator; the smallest
  improvement was 4.
- Reduced path-total search matched full positive edge-count enumeration on
  all three fresh optimizer cells.
- Every full-enumeration optimizer in those cells was path-internally
  balanced.
- The registered composition counts were exact: 21, 21, and 56 reduced cells
  versus 462, 792, and 792 full edge allocations.
- Runtime was 0.4444 seconds, peak resident memory was 21,598,208 bytes, and
  no GPU was used.

The independent verifier used a direct three-state edge-orientation census
for the formula cells and a separately implemented path-total optimizer.  All
11 checks passed.

## Interpretation

The proof, not the finite census, establishes strict within-path balancing
for the declared generalized-theta class.  The registered run validates that
the implementation realizes the proof on fresh cells and agrees with
independent exact evaluators.

This closes a nontrivial tractable overlapping-cycle class left open by the
v0.23 K4 exchange trap.  It does not classify the optimizer on arbitrary
biconnected blocks.
