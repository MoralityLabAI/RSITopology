# ASMP-10 disjoint-seed transition-predictor protocol v0.5 — draft only

## Status

Drafted under the v0.4 branch rule; **not registered and not authorized to
run**. Construction seed 7 and every v0.4 artifact are excluded from fitting,
threshold choice, and evaluation.

## Estimand

Within a frozen modular-addition training family, does a target-blind block of
early spectral/representation observables improve held-out prediction of
capability-state dynamics beyond hyperparameters and the complete allowed
scalar learning-curve prefix?

The estimand is deliberately narrow. It does not claim a universal
capability-transition predictor or address recursive improvement.

## Frozen candidate family

- modulus 31, the v0.4 transformer architecture, AdamW, and 15,000 steps;
- train fractions `{0.50, 0.55, 0.60}`;
- weight decay `{1.0, 2.0}`;
- evaluation every 100 steps;
- early-observation cutoff at step 500;
- construction and final holdout seeds disjoint for both initialization and
  dataset permutation.

Before registration, exact seed lists, the seed-to-permutation derivation, and
the number of seed clusters must be fixed from a resource/power calculation.
No seed from `{0, 1, 7}` may enter either split.

## Capability-state outcomes

A time point qualifies under the unchanged v0.4 condition: held-out accuracy
at least 0.90 and held-out loss at most 0.50.

The outcome is not one scalar. It contains:

1. first sustained crossing: first five-evaluation qualifying streak;
2. reversion count and last reversion after that crossing;
3. terminally stable transition: earliest qualifying point after which every
   remaining evaluation through step 15,000 qualifies, available only when the
   terminal qualifying tail contains at least 20 evaluations; and
4. right-censoring when no terminally stable transition occurs.

The primary prediction target is terminal stability by step 15,000. First
crossing and time-to-terminal-stability are secondary. This prevents transient
metric spikes from being called irreversible phase changes.

## Target-blind feature blocks

All feature tables are computed and hashed before the outcome join.

- `B0` nuisance: train fraction, weight decay, split size, parameter count.
- `B1` loss-prefix baseline: `B0` plus every registered train/test loss and
  accuracy value through step 500. Hyperparameter-only performance is always
  reported so an easy phase boundary cannot masquerade as representation-level
  prediction.
- `B2` richer block: `B1` plus gradient-norm prefix, token-embedding stable
  rank, output-weight stable rank, representation effective rank, and parameter
  norm at step 500.

Representation geometry is computed on a frozen unlabeled probe universe.
Labels and post-step-500 metrics are forbidden inputs. Feature standardization,
missing-value policy, penalty grid, tie breaks, and model source are sealed
before labels unseal.

## Prediction and gates

Use seed-grouped splits only. A frozen ridge-logistic model predicts terminal
stability; a separately frozen discrete-time survival model handles the
right-censored timing endpoint. Hyperparameters are tuned only inside the
construction split by leave-one-seed-out cross-validation.

Primary evidence is the paired per-seed held-out log-loss difference
`logloss(B1) - logloss(B2)`. The richer block passes only if:

- the one-sided simultaneous 95% lower confidence bound is strictly positive;
- the point estimate exceeds a preregistered practical margin in nats per cell;
- calibration does not degrade beyond a frozen Brier-score margin; and
- the improvement exceeds the 95th percentile of a seeded, within-stratum
  permutation null for the entire richer feature block.

All numeric margins, bootstrap/permutation counts, and a minimum holdout seed
count must be filled by a target-free simulation before this draft can become a
registration. Equality is inconclusive. Instrument invalidity yields
`not_evaluated`, never a pass.

## Required controls

- outcome-label permutation returns nominal false-positive frequency;
- geometry-block permutation cannot pass specificity;
- a synthetic planted predictor is recovered;
- a loss-only planted world does not award incremental value to geometry;
- all six cells for a seed stay in the same fold; and
- feature hashes are sealed before any outcome table can be joined.

## Claim boundary

A pass would establish incremental prediction only in the frozen
modular-addition family and only for the registered capability-state outcome. A
null would bound the frozen early observables, not all training-time geometry.
Neither result establishes a general emergence law, self-improvement, or RSI.
