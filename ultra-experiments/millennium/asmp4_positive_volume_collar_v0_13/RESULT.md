# Result

The v0.13 harness passes its central construction and independent interval-geometry verifier.

The safe set `S^1 x [-1,1] x modes` has normalized volume 2 and contains the positive-dimensional NHIM `S^1 x {0}`. The full-collar transcript counts are exactly `4^T` for computed reads and writes and `8^T` for forced raw reads. Thus the registered regions are `[2,infinity) x [2,infinity)` and `[3,infinity) x [2,infinity)`.

For every fixed `0<rho<=1`, the exact normal spanning number is `ceil(rho*2^T)`. The independent harness tests both dyadic and non-dyadic margins, constructs safe interval covers, and checks the matching final-diameter converse.

Five adversarial mutations are rejected. The expanded ASMP-4 chain passes all
174 focused tests in 230.32 seconds.

The result removes the positive-dimension and positive-volume degeneracy objections. It remains a registered counterexample/fork, not the global ASMP-4 classification and not a robustness theorem.

The [v0.14 successor](../asmp4_positive_volume_stop_certificate_v0_14/RESULT.md)
turns the surviving fork into an explicit harness stopping decision without
changing this frozen result.
