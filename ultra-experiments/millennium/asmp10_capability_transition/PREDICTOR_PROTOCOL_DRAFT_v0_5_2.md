# ASMP-10 transition-predictor protocol v0.5.2 - draft amendment

## Status and precedence

This is an additive amendment to `PREDICTOR_PROTOCOL_DRAFT_v0_5_1.md`. Both
documents are drafts. Neither is registered or authorized to run. Where the
two conflict, v0.5.2 controls. The sealed v0.4 artifacts and the v0.5.1
addendum remain byte-identical.

## Why the exit dwell changed

The v0.4 metric grid was spaced by 100 optimizer steps. Every recorded
post-crossing failure was absent at the preceding evaluation and recovered by
the following evaluation. The continuous excursion duration is therefore
interval-censored below 200 steps; it was not measured as 100 steps.

The six retained `checkpoint.pt` files are rolling final checkpoints at step
15,000. No checkpoint history around the seven excursions exists, so a denser
burned-data replay cannot recover their duration.

The primary adverse-exit dwell is therefore **300 optimizer steps**, which is
strictly above the censored upper bound with 100 steps of margin and divides
exactly across the registered 25-, 50-, and 100-step evaluation grids.

## Primary prediction object

The primary object is frozen as a **three-way categorical endpoint**, scored
by grouped held-out multinomial log loss:

1. `no_adjudicable_horizon_stable_transition`;
2. `early_horizon_stable`; and
3. `delayed_horizon_stable`.

The class definitions, 500-step delayed boundary, 500-step terminal
observation tail, and horizon of 15,000 steps remain as in v0.5.1. Interval
coverage for transition time and the multistate hazard curve are secondary
descriptive endpoints. They cannot pass the primary gate or substitute for a
failed categorical result. The target-free power calculation must therefore
be based on paired held-out multinomial log-loss improvement, not interval
coverage or hazard-model power.

## State-machine amendment

Entry remains conjunctive and exit remains disjunctive:

- up-qualified: test accuracy at least 0.90 **and** test loss at most 0.50;
- down-qualified: test accuracy below 0.80 **or** test loss above 0.75;
- entry dwell: 500 optimizer steps; and
- exit dwell: 300 optimizer steps.

This asymmetry is intentional. A stability claim must satisfy both registered
performance requirements to be earned, while sustained failure of either
requirement is enough to revoke it. The distinct thresholds provide
hysteresis; the dwell requirements prevent isolated samples from changing
state.

At the 25-step primary cadence, entry and exit require 21 and 13 consecutive
samples respectively. At 50 steps they require 11 and 7; at 100 steps they
require 6 and 4.

## Dwell-fragility validity gate

Cadence stability does not imply dwell-parameter stability. On the primary
25-step grid, the complete state calculation is replayed with exit dwells of
`{250, 300, 400}` optimizer steps. These values are all above the censored
v0.4 duration bound; 300 is primary.

For every held-out seed/cell, all three replays must agree on:

- the three-way primary class;
- the ordered sequence of entry and exit event kinds; and
- the final capable/incapable state.

Any disagreement sets `instrument_status = dwell_fragile` and
`gate_decision = not_evaluated`. The dwell result is reported separately from
the cadence-replay result. A cell cannot pass by averaging across dwell values.

The existing cadence gate is retained using the primary 300-step exit dwell:
25-, 50-, and 100-step grids must agree under the v0.5.1 rules. Cadence or
dwell invalidity stops the prediction sequence.

## Task and baseline completeness

The confirmation family is restricted to modular addition under the frozen
architecture and modulus. No other task enters v0.5.2. This restriction is
substantive: restricted/excluded Fourier losses and the registered Fourier
progress measures must be defined for every confirmation cell.

The full `B2_published_progress` block from v0.5.1 is mandatory in every fold.
If any registered published-progress feature is missing, nonfinite, selected
using a holdout outcome, or undefined for a cell, then
`instrument_status = incomplete_baseline` and the geometry comparison is
`not_evaluated`. There is no weaker-baseline fallback.

## Spike-consequence diagnostic

Confirmation reports a descriptive table for every post-entry loss/gradient
spike: magnitude, position relative to entry, current hysteretic state, and
whether it begins a threshold excursion or a registered state exit. It is not
a prediction target and has no gate. This preserves the v0.4 observation that
only 7 of 15 post-crossing spikes caused old-detector excursions without
opening a new hypothesis after seeing that result.

## Power calculation dependency

The power simulation may now proceed against exactly one primary estimand:
paired seed-grouped multinomial log-loss improvement of
`B2_published_progress + B3_geometry` over `B2_published_progress`.

Before registration it must freeze:

- class-probability scenarios, including rare-class stress cases;
- number of independent seed clusters and all six cells per cluster;
- practical log-loss margin;
- simultaneous-confidence and permutation-null settings;
- censoring and missing-baseline invalidity rates; and
- expected compute under the HRM hard-cap wrapper.

## Claim boundary

This amendment makes the endpoint measurable and falsifiable within a finite
horizon. It does not show that early geometry predicts it. The v0.4 excursion
durations remain censored, and the 300-step dwell is a conservative registered
design choice whose fragility will itself be tested.

