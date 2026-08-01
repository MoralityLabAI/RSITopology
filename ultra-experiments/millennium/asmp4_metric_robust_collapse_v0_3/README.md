# ASMP-4 metric-robust collapse v0.3

This successor strengthens the serial-collapse theorem so it no longer depends
on identifying whole-transcript growth with causal data rate.

The key addition is a downstream normal form. Besides moving controller
computation into the sensor, one can forward the read transcript and move the
same computation into the actuator. The two transformations prove equality of
the optimal read and write thresholds for every shared, relabel-invariant
transcript-tree cost, including whole-language cardinality, uniform causal
branching, and exact worst-case prefix-free length.

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
An exact skew-tree fixture separates all three registered costs.
