# ASMP-4 metric-robust collapse result v0.3

## Result

The ASMP-4 serial collapse is robust to the rate-definition ambiguity found in
v0.2.

For every shared nonnegative port cost J that depends only on the realized
transcript tree and is invariant under symbol relabeling and deterministic
fixed-prefix insertion/deletion:

~~~text
h_read^J(K_0,K) = h_write^J(K_0,K) = h_J(K_0,K),

closure(R_K^J) =
  [h_J(K_0,K), infinity) x [h_J(K_0,K), infinity).
~~~

Two normal forms carry the proof:

1. move deterministic controller computation upstream into the sensor and copy
   the original write tree onto both ports; or
2. forward the read tree and move the same computation downstream into the
   actuator.

This applies both to the canonical whole-language cost
log2 |M(T)| and to the history-dependent worst-path branching cost used in
uncertain-system invariance feedback entropy. It also applies to the exact
minimax worst-case prefix-free length obtained from the Kraft recurrence.

If only one computation move is admissible, it gives only one inequality:
upstream closure implies h_read <= h_write, while downstream closure implies
h_write <= h_read. The harness contains strict witnesses in both directions.

## Metric correction

The scalar entropy value depends on which cost is registered. In the exact comb
safety game:

~~~text
terminal words = T+1,
terminal-language rate = log2(T+1)/T -> 0,
causal branching cost = T,
causal branching rate = 1 bit/step.
~~~

Thus v0.2's diagonal region for the canonical ASMP-4 formula remains valid, but
its total-control-language entropy must not be identified with uncertain-system
invariance feedback entropy without a branching-equivalence assumption.

## Evidence

- Every one of the 65,809 nonempty binary transcript languages through horizon
  four satisfies terminal-language cost <= worst-path branching cost.
- Symbol relabeling preserves both metrics in every census cell.
- The comb game is independently realized by the finite safety solver in the
  v0.2 harness.
- Upstream and downstream tree-copy fixtures preserve both metrics exactly.
- A forced four-symbol raw sensor gives a strict two-bit read versus one-bit
  write threshold.
- A fixed direct-action actuator gives a strict T-bit write versus
  log2(T+1)-bit read threshold.
- Both normal forms preserve their source transcript tree and the applied plant
  input in all 96 combinations of read delay, write delay, and horizon in the
  fixed-FIFO replay.
- A skew tree verifies the strict three-way separation
  log2(2^d+2) < d+1 < d+log2(3) between terminal, prefix-free, and uniform
  branching costs through depth 12.
- A four-leaf sequential-rounding tree verifies the opposite strict order
  `2 < log2(6) < 3` between terminal, branching, and minimax-prefix costs.

The proof remains nonempirical. The census guards definitions and boundary
examples.

The v0.4 successor sharpens one phrase in this boundary: positive
port-specific unit conversions do not break collapse. They only rescale the
two thresholds. A genuinely different tree ordering can break the one-block
and fixed-schedule rectangle; that successor gives an exact no-lag prefix-code
frontier for expected read length versus worst-case write length. The v0.5
adaptive-history successor then proves that public common-history block coding
restores the rectangular asymptotic corner for every finite positive i.i.d.
plan alphabet under expected-read/worst-write prefix costs.

The v0.6 registration-fork successor makes the normal-form closure qualifier
decisive for canonical status. On one fixed plant and the canonical terminal-
language metric, a computed sensor has region `[1,infinity) x [1,infinity)`,
while a forced injective raw sensor has `[2,infinity) x [1,infinity)`. The
second class is not upstream-normal-form closed. This preserves the theorem in
its written scope but prevents treating that scope as automatic for every
“registered causal code.”
