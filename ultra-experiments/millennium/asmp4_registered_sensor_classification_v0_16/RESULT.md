# Result

V0.16 responds constructively to the v0.15 finding that canonical ASMP-4 may intend a registered sensor experiment as theorem data.

For the positive-volume collar, a sensor experiment is now an explicit mode partition with an injective charging rule. All 15 partitions are classified. The four partitions refining the control-relevant `q` fibers are feasible and have region `[1+log2(k),infinity) x [2,infinity)` for `k` sensor blocks. The other eleven are impossible at the first step because one reported symbol merges modes whose safe-control intervals are `[-1,1]` and `[7,9]`.

The exact finite-margin formulas are `k^T ceil(rho*2^T)` read words and `2^T ceil(rho*2^T)` write words. Central and independent implementations use different partition generators and reproduce the `1,2,1` feasible histogram over block counts `2,3,4`.

This resolves the local registered sensor ambiguity for this plant. It is not the universal ASMP-4 registered-class grammar and does not establish the requested global nonlinear theorem.

The complete 17-package regression passes all 204 focused tests in 303.52
seconds.

The [v0.17 successor](../asmp4_zero_error_sensor_kernels_v0_17/RESULT.md)
recovers these four partitions as the deterministic subfamily of a complete
finite support-kernel census.
