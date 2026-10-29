# ASMP-4 semantic selector audit preregistration v0.15

The primary claim passes only if all 23 canonical clause units are covered exactly once and every unit is classified `no_selector`. A label of `ambiguous`, `selects_computed`, `selects_raw`, or `selects_parameterized` blocks the claim. Exact-string absence is a baseline, not the task judge.

The classification question is narrow: does the clause mandate the sensor's observation domain, its permitted computation/equivalence closure, injectivity on raw plant modes, a coarsest-sufficient-statistic quotient, or explicit registry parameterization? Merely stating that the architecture is registered, separate, causal, side-channel-free, or architecture-dependent does not select one of those alternatives.

The source is not held out. This is a complete deterministic audit of a frozen document. A separately staged held-out synthetic pack tests the robustness of the selector-risk metric across five independent probe families. Any post-outcome threshold change is exploratory and cannot support v0.15.
