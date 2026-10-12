# ASMP-10 disjoint-seed transition-predictor protocol v0.5.1 - draft only

## Status and amendment relation

This is an additive successor to `PREDICTOR_PROTOCOL_DRAFT_v0_5.md`. The v0.5
file is retained byte-for-byte because it is named in the sealed v0.4 receipt.
This document is **not registered and not authorized to run**.

Construction seed 7, seeds 0 and 1 from earlier pilots, every v0.4 outcome, and
all six v0.4 hyperparameter cells are burned for confirmation. They may inform
this draft but may not enter fitting, threshold selection, or final evaluation.

## Estimand

Within the frozen modular-addition family and conditional on the registered
AdamW optimizer, does a target-blind early geometry block improve held-out
prediction of a three-way, finite-horizon capability-state outcome beyond the
complete frozen family of hyperparameter, scalar-prefix, published
mechanistic-progress, and effective-theory baselines?

The three outcome classes are:

1. no adjudicable horizon-stable transition;
2. early horizon-stable transition; and
3. delayed horizon-stable transition.

This is a two-sided target. A predictor that merely orders data fraction or
predicts that more weight decay always makes transitions earlier is
insufficient.

## Candidate training family

- modulus 31 and the v0.4 transformer architecture;
- AdamW only, learning rate 0.001 and betas `(0.9, 0.98)`;
- train fractions `{0.50, 0.55, 0.60}`;
- weight decay `{1.0, 2.0}`;
- 15,000 optimizer steps;
- primary metric evaluation every 25 optimizer steps, including step 0 and
  step 15,000;
- full model checkpoints every 100 optimizer steps or 60 seconds, whichever
  occurs first;
- early-observation cutoff at step 500; and
- disjoint initialization seeds and dataset-permutation seeds.

The claim is optimizer-conditional. A future matched SGD or other optimizer
arm would be a separately registered mechanism test, not an unplanned subgroup
of this run.

Before registration, exact seed lists, sample counts, source revisions,
environment hashes, and a target-free power/resource calculation must be
filled. No execution is allowed while any field is unresolved.

## Frozen hysteretic capability state

### Thresholds

An evaluation is `up-qualified` when both:

- held-out accuracy is at least 0.90; and
- held-out loss is at most 0.50.

An evaluation is `down-qualified` when either:

- held-out accuracy is below 0.80; or
- held-out loss is above 0.75.

An evaluation between the two boundaries is in the hysteresis band and retains
the current state. Equality is resolved exactly as the inequalities above
state; it is not discretionary.

### Dwell and state transitions

The state begins `incapable`.

- It enters `capable` only after 21 consecutive up-qualified evaluations on
  the 25-step grid. The first and last qualifying samples are therefore 500
  optimizer steps apart. The state becomes available at the final confirming
  sample, while the event onset is recorded as the first sample in the
  confirmed dwell.
- It exits `capable` only after 5 consecutive down-qualified evaluations. The
  first and last adverse samples are 100 optimizer steps apart.
- Any sample that is not down-qualified resets the exit streak. Any sample
  that is not up-qualified resets the entry streak.

An isolated excursion cannot itself change state.

### Horizon-stable transition and three-way label

A horizon-stable transition is a capable entry after which no registered exit
occurs through step 15,000 and for which at least 500 optimizer steps remain in
the observation horizon. This is finite-horizon stability, never terminal or
irreversible stability beyond the run.

Let the memorization step be the first entry under an independently frozen
five-evaluation train-accuracy state. Let delay equal stable-transition step
minus memorization step. Here `stable-transition step` means the confirmed
dwell's onset step, not the later confirmation step; both are stored.

- `early_horizon_stable`: adjudicable stable transition with delay below 500;
- `delayed_horizon_stable`: adjudicable stable transition with delay at least
  500; and
- `no_adjudicable_horizon_stable_transition`: no such entry by step 14,500.

An entry after step 14,500 is right-censored for timing analysis and receives
the third primary class. Its separate censoring flag is retained.

## Evaluation-density validity gate

The 25-step metric grid is primary. The exact same metrics are deterministically
subsampled to 50-step and 100-step grids. On each grid, dwell lengths are
translated by elapsed optimizer time: `(11, 3)` evaluations for entry/exit on
the 50-step grid and `(6, 2)` on the 100-step grid.

For every held-out seed/cell:

- the three-way label must agree on all three grids;
- the order of state entries and exits must agree; and
- stable-transition steps must differ by no more than the coarsest grid width,
  100 steps.

Any violation sets `instrument_status = cadence_dependent` and the prediction
gate to `not_evaluated`. The disagreement is reported; it cannot be averaged
away or relabeled inconclusive. Full checkpoints are not substituted for
missing metric evaluations.

## Target-blind feature blocks and frozen baseline family

Every feature table is computed and hashed before outcome joining.

- `B0_hyperparameter`: train fraction, weight decay, split size, model size,
  optimizer identity, learning rate, and seed-cluster metadata.
- `B1_scalar_prefix`: `B0` plus all train/test loss, train/test accuracy,
  gradient norm, global parameter norm, last-layer norm, and logit-scale values
  through step 500.
- `B2_published_progress`: `B1` plus restricted loss, excluded loss, registered
  Fourier concentration/Gini measures, and a construction-split
  effective-theory phase-map prediction.
- `B3_geometry`: token-embedding stable rank, output-weight stable rank,
  representation effective rank, the registered spectral trajectory through
  step 500, and no post-cutoff value.

The implementation and source revision for each published measure must be
sealed before registration. Key Fourier frequencies are selected on the
construction split only and then frozen. Holdout-specific final-state
frequency selection is prohibited.

The primary nested comparison is:

`B2_published_progress` versus `B2_published_progress + B3_geometry`.

The richer baseline is a single frozen supermodel, not whichever comparator is
weakest after outcomes are seen. Results against `B0` and `B1` are required
diagnostics only.

## Prediction and gates

All six cells for one seed cluster remain in one fold. A frozen multinomial
ridge-logistic model predicts the three-way outcome. A separately frozen
discrete-time multistate survival model analyzes entry and exit timing.
Hyperparameters are tuned only inside the construction split with grouped
cross-validation.

Primary evidence is paired held-out multiclass log-loss improvement:

`logloss(B2_published_progress) - logloss(B2_published_progress + B3_geometry)`.

Geometry passes only if all of the following hold:

- the one-sided simultaneous 95% lower confidence bound is strictly positive;
- the point estimate exceeds a preregistered practical margin in nats per
  seed/cell;
- no per-class one-vs-rest log loss worsens past its frozen margin;
- calibration does not worsen past a frozen multiclass Brier-score margin; and
- the improvement exceeds the 95th percentile of a seeded, within-stratum
  permutation null for the complete geometry block.

All margins, resampling counts, minimum class counts, and censoring ceilings
must be fixed by target-free simulation. Equality is inconclusive. Invalid or
cadence-dependent instruments are `not_evaluated` and stop the sequence.

## Required controls

- label permutation returns nominal false-positive frequency;
- geometry-block permutation cannot pass specificity;
- a synthetic planted three-class predictor is recovered;
- a loss/progress-only planted world does not award incremental value to
  geometry;
- a synthetic one-grid spike never causes state exit;
- a persistent adverse dwell causes exactly one exit;
- 25/50/100-step replay catches a planted revert-and-recover cycle hidden from
  the 100-step grid;
- feature and implementation hashes are sealed before outcome join; and
- the HRM resource wrapper records hard caps, checkpoints, cleanup, and abort
  causes exactly as in v0.4.

## Claim boundary

A pass establishes incremental prediction only for this modular-addition
family, registered AdamW dynamics, and frozen finite-horizon state machine. A
null bounds only the registered early observables. A cadence failure diagnoses
the endpoint instrument, not the predictor. No result establishes a universal
capability-transition law, persistent ungrokking, self-improvement, or RSI.

The reusable infrastructure result is narrower: the HRM hard-cap,
checkpoint/resume, cleanup, and receipt workflow transferred successfully from
training control to a preregistered dynamics experiment.
