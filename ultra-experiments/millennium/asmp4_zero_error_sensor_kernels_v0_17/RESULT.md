# Result

V0.17 extends the registered sensor grammar from deterministic partitions to stochastic memoryless kernels.

Cross-`q` supports are disjoint exactly when the kernel is support-zero-error feasible. A feasible kernel with `a` active raw outputs has exact region `[1+log2(a),infinity) x [2,infinity)` and finite counts `a^T ceil(rho*2^T)` reads and `2^T ceil(rho*2^T)` writes. Probability magnitudes do not enter beyond deciding which outputs have positive support.

The complete census covers 53,108 relations through four output symbols: 724 feasible, 52,384 infeasible, and 620 genuinely randomized feasible. An independent combinatorial derivation agrees with the exhaustive implementation. The 104 labeled deterministic feasible kernels collapse to the four unlabeled v0.16 partitions.

This does not classify block error, expected-length coding, memory, hidden sensor state, or vanishing failure probability.

The v0.18 successor closes the finite known-initial-state hidden-sensor lane:
global support separation is replaced by reachable subset-observer
homogeneity, with read rate governed by the observer language's spectral
radius. The frozen v0.17 memoryless claim remains unchanged.

The complete 18-package chain passes all 214 focused tests in 374.34 seconds.
