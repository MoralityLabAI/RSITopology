# ASMP-4 metric-robust collapse v0.3

This successor strengthens the serial-collapse theorem so it no longer depends
on identifying whole-transcript growth with causal data rate.

The key addition is a downstream normal form. Besides moving controller
computation into the sensor, one can forward the read transcript and move the
same computation into the actuator. The two transformations prove equality of
the optimal read and write thresholds for every shared, relabel-invariant
and deterministic-prefix-invariant transcript-tree cost, including
whole-language cardinality, uniform causal branching, and exact worst-case
prefix-free length.

Run:

~~~powershell
python -m pytest test_metric_harness.py -q
python run_verification.py
python verify_metric_theorem.py
~~~

The exact harness enumerates all 65,809 nonempty binary transcript languages
through horizon four. It also checks a comb safety game whose terminal-language
rate tends to zero while its worst-path causal branching rate is exactly one
bit per step, plus strict read-above-write and write-above-read witnesses when
one of the two computation moves is deliberately forbidden. A 96-cell delay
replay checks both normal forms with independent fixed FIFO read/write delays.
Exact skew and sequential-rounding fixtures give the opposite strict orders
`C<P<B` and `C<B<P` among the three registered costs.

The [v0.4 heterogeneous-cost successor](../asmp4_heterogeneous_port_costs_v0_4/RESULT.md)
proves that positive unit conversions only rescale the rectangular thresholds,
then locates the sharper boundary with an exact expected-read/worst-write
nonrectangular finite and fixed-schedule prefix frontier. The
[v0.5 adaptive-history successor](../asmp4_adaptive_history_collapse_v0_5/RESULT.md)
computes the exact adaptive Bellman frontier and proves that logarithmic
write slack restores the closed asymptotic rectangle for every finite positive
i.i.d. plan alphabet.

The [v0.6 registration-fork successor](../asmp4_registration_fork_v0_6/RESULT.md)
shows that bilateral normal-form closure is not automatic across sensor
grammars: with all plant-side data fixed, a computed sensor gives corner
`(1,1)` and a forced raw sensor gives `(2,1)` under the canonical terminal-
language metric. The theorem here remains exact conditionally; it is not an
unconditional classification of registration classes that forbid upstream
computation.
