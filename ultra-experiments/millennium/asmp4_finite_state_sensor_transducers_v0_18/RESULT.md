# Result v0.18

The memoryless support condition from v0.17 generalizes exactly to reachable
beliefs for a finite hidden-state sensor. A registered transducer is feasible
if and only if every reachable subset-observer transition assigns the observed
raw symbol a singleton current `q` class.

If `A` is the reachable observer's output-multiplicity adjacency matrix and
`L_T` its length-`T` raw language, the exact inner-collar counts are

- reads: `L_T ceil(rho*2^T)`;
- writes: `2^T ceil(rho*2^T)`.

The exact asymptotic region is
`[1+log2(rho(A)),infinity) x [2,infinity)`. The golden fixture realizes a
non-integer read corner `2+log2(phi)`, while the history-toggle fixture proves
that global current-output support separation is not necessary once histories
track hidden sensor state.

Two independent observers exhaust all 256 deterministic binary-output,
two-state, binary-`q` transducers: 80 are feasible and 176 infeasible. Of the
feasible set, 32 have globally disjoint class outputs and 48 are genuinely
history-essential.

This closes the finite known-initial-state support-zero-error lane. Unknown
initial state, continuous memory, raw-output compression, expected length,
average or block error, and the global nonlinear variational theorem remain
outside the claim.

The complete 19-package chain passes all 224 focused tests in 370.34 seconds.

The v0.19 successor closes the finite registered initial-set boundary. The
frozen v0.18 known-initial-state claim remains unchanged.
