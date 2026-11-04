# ASMP-10 successor scope v0.2

## Objective

Push the obstruction beyond unrestricted finite-degree polynomial
continuations while keeping the positive prediction branch genuinely live.
This document scopes work; it is not a registration or authorization to run.

## Negative branch: bounded analytic continuation

Replace the bare degree bound with a declared coefficient or analytic-norm
bound. A candidate finite problem is:

- losses have degree at most `D` and coefficient norm at most `B` in a frozen
  basis;
- prefix jets are observed with registered error `delta`;
- compute the maximum future capability-score separation among all losses
  consistent with those observations and bounds;
- report the exact or certified upper/lower envelope as a function of
  `(n,k,D,B,delta)`.

The Hermite kernel still describes invisible directions, but the norm bound
limits their amplitude. The resulting quantity is not merely “kernel nonempty”
but the largest future regret the kernel can hide. For small degrees this is a
CPU linear/convex optimization problem with exact controls.

This supplies the regularity assumption missing from v0.1 and asks how much it
actually buys.

## Training-model branch: prefix-matched grokking pairs

In a separately frozen solvable or tightly controlled modular-arithmetic
family:

1. define the continuous capability score and threshold before viewing curves;
2. match pairs on the full allowed loss prefix, not merely one endpoint;
3. test whether different hyperparameters or latent circuit states retain
   materially different transition-time distributions after that matching;
4. compare a loss-prefix-only predictor with prospectively frozen richer
   observables such as representation rank, circuit coefficients, or an LLC
   surrogate on disjoint seeds; and
5. require the richer predictor to beat the loss-only baseline out of sample.

A null bounds only the frozen training family and observables. A positive
result shows prediction in that family; it does not defeat the unrestricted
v0.1 obstruction.

## Pilot correction

The completed pilot already included AdamW weight decay `1.0`, which Power et
al. used as their default weight-decay setting. Their original experiments also
report that less training data generally requires *more* optimization to reach
generalization. Therefore “drop the train fraction to pull the transition into
the affordable window” is not frozen as an assumption.

A future liveness pilot should instead use a small prospective factorial grid,
for example:

- training fraction `{0.40, 0.55, 0.70}`;
- weight decay `{1.0, 2.0}`;
- a horizon long enough to include at least `10^4` steps;
- one construction seed per cell, stopping once a cell supplies a reproducible
  delayed transition candidate; and
- no claim-eligible predictor fitting on those construction seeds.

This grid tests rather than assumes whether more data shortens transition time
without eliminating the delayed-generalization regime. It must wait for an
idle GPU and a fresh hard-cap authorization.

Primary anchor: Alethea Power et al., [“Grokking: Generalization Beyond
Overfitting on Small Algorithmic
Datasets”](https://arxiv.org/abs/2201.02177). The paper reports weight decay 1
as the default AdamW setting and optimization budgets up to `5e5`–`1e6` steps
for its strongest delayed-generalization examples.

## Two-sided interpretation

The research target is the gap between:

- a bounded continuation class where prefix observables provably constrain
  future outcomes; and
- a realistic training family where richer early observables beat the best
  frozen loss-only predictor on held-out transitions.

Neither branch alone resolves ASMP-10.

