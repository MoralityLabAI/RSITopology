# ASMP-8 v0.3a prior-art boundary

This experiment combines established ingredients. It does not claim a new
concentration inequality or robust-optimization theorem.

## Direct anchors

- Hoeffding, W. (1963), *Probability Inequalities for Sums of Bounded Random
  Variables*, JASA 58(301), 13–30,
  <https://doi.org/10.1080/01621459.1963.10500830>. The registered audit
  radii use its one-sided bounded-variable inequality.
- Ben-Tal, A. and Nemirovski, A. (1999), *Robust Solutions of Uncertain Linear
  Programs*, Operations Research Letters 25(1), 1–13,
  <https://doi.org/10.1016/S0167-6377(99)00016-4>. The uncertainty-set/support
  function framing is classical robust optimization.
- Skalse, J., Howe, N. H. R., Krasheninnikov, D., and Krueger, D. (2022),
  *Defining and Characterizing Reward Hacking*,
  <https://arxiv.org/abs/2209.13085>. This supplies the formal reward-hacking
  setting and strong unrestricted negative results.
- Gao, L., Schulman, J., and Hilton, J. (2023), *Scaling Laws for Reward Model
  Overoptimization*, ICML 2023,
  <https://proceedings.mlr.press/v202/gao23h.html>. Their optimizer-specific
  empirical curves motivate testing more than one optimization path.

## What remains specific to this experiment

The contribution is an audited finite specialization:

- the radius is calibrated on target-blind reference-policy samples;
- one calibration is reused across multiple proxy-only policy paths;
- certificate soundness, non-vacuity, and rare-tail behavior are separated;
- a conservative KL/Pinsker lower bound and two invalid scalar baselines are
  reported beside the exact dual certificate; and
- every result is bound to a prospective protocol and replayable seed chain.

No novelty is claimed for Hoeffding, Hölder duality, Pinsker's inequality, or
distributionally robust optimization.
