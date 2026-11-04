# ASMP-8 v0.3a claim packet: calibrated dual certificates

## Question

ASMP-8 v0.2 proved that, for a fixed proxy-error radius, the robust lower
bound

```text
true_gain >= proxy_gain - error_radius * dual_policy_movement
```

is sharp. Version 0.3a asks the next question: can a target-blind audit sample
calibrate a radius that is simultaneously valid for several proxy-only
optimization paths, and does the resulting bound safely certify any positive
true-reward gains?

## Frozen estimand

The outcome universe is finite. A hidden deterministic error function
`e(x) = true_reward(x) - proxy_reward(x)` is audited by IID draws from the
reference policy `p0`. For `|e| <= 1`, one-sided Hoeffding bounds estimate

```text
delta_1 >= E_p0 |e|
delta_2 >= sqrt(E_p0 e^2)
delta_infinity = 1
```

simultaneously. For every policy selected without seeing `e`, the three lower
bounds are

```text
LB_1        = proxy_gain - delta_1 * max_x |pi(x)/p0(x) - 1|
LB_2        = proxy_gain - delta_2 * sqrt(E_p0[(pi/p0 - 1)^2])
LB_infinity = proxy_gain - delta_infinity * E_p0|pi/p0 - 1|.
```

The registered certificate uses their maximum. Because the two sampled norm
bounds are simultaneous and the infinity bound is deterministic, a positive
maximum is a valid certificate whenever the calibration instrument is valid.
The same radii are reused without refitting across Gibbs, best-of-n,
top-spike, and scrambled-Gibbs policy paths.

## Frozen interpretation

The experiment separates three possible outcomes:

1. **unsafe:** a positive certificate occurs while true gain is non-positive
   and the registered norm bounds were valid;
2. **valid but vacuous:** certificate soundness holds, but too few positive
   policies can be certified;
3. **valid and non-vacuous on the registry:** soundness holds and the
   registered non-vacuity and transfer gates pass.

The rare-tail family is deliberately included because average proxy error can
look small while an optimizer concentrates on the bad tail.

## Claim boundary

A pass is evidence that a classical concentration bound plus the v0.2
dual-norm identity yields a sound, sometimes non-vacuous certificate on this
finite synthetic registry. It is not a learned reward-model result, a claim
that Hoeffding calibration is efficient, evidence about RL training dynamics,
or a resolution of ASMP-8.
