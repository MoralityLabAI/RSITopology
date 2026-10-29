# Result v0.22

Under encoder-optimized semantics, every feasible finite sensor transducer for
the local two-`q` collar collapses to the computed region. A causal encoder
tracks the raw subset belief and emits only the uniquely decoded current `q`
class. Exact reads and writes are both
`2^T ceil(rho*2^T)`, giving region
`[2,infinity) x [2,infinity)`.

The equivalence is sharp: a mixed raw observer transition cannot be repaired
by any downstream causal encoding because opposite `q` executions have the
same available history but require disjoint current control intervals.

A contextual three-symbol fixture separates static from causal processing.
All five static partitions are exhausted; only the discrete partition is
feasible, with raw language `3^T` and spectral radius 3. The belief-aware
causal encoder has language `2^T`.

The complete 256-transducer census preserves the `80/176` feasible split, and
the complete 53,108-relation memoryless census preserves the `724/52,384`
split. Every feasible member receives the same exact encoder-optimized region.

This resolves the finite local collar family under the declared
encoder-optimized timing. It does not address delayed observation, restricted
encoder memory, forced-raw retention, continuous sensors, or the global
nonlinear ASMP-4 class.

The v0.23 successor addresses the delayed-observation item for this local
plant: every positive integer delay is impossible for arbitrary current modes
without preview, while charged current preview restores this v0.22 region.
The frozen v0.22 claim remains the same-step theorem.

The complete 23-package chain passes all 264 tests in 307.25 seconds.
