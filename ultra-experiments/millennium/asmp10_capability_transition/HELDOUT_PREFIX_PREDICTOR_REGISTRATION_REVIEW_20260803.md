# ASMP-10 held-out prefix-predictor registration review - 2026-08-03

## Decision

`no_go_pending_executable_joint_power_design`

This is a negative feasibility audit of one proposed v0.6 design, not a
predictor result, source registration, authorization, or scientific run. The
held-out predictor obligation remains unexecuted.

The reviewed proposal used six construction and eight confirmation seed
clusters over six cells per cluster, or `14 * 6 = 84` sequential training
chunks. The inferential confirmation unit is the seed cluster, so its effective
confirmation count is eight, not 48 cells or 84 chunks.

## Exact sign-gate audit

One proposed conjunct was that at least seven of eight confirmation-cluster
differences be positive. If each sign is independently positive with
probability `p`, its pass probability is

```text
P[X >= 7], X ~ Binomial(8,p).
```

The exact values are:

| Per-cluster positive probability | Gate pass probability |
|---:|---:|
| `1/2` | `9/256 = 0.03515625` |
| `4/5` | `196608/390625 = 0.50331648` |
| `9/10` | `81310473/100000000 = 0.81310473` |

Thus this gate alone has only about 50% power when a cluster is favorable with
probability 0.8. Requiring the observed mean improvement to exceed `0.02` nats
also gives approximately 50% power when the true mean is exactly `0.02`.

Even before small-sample and simultaneous-inference penalties, a normal
approximation for a one-sided 95% lower bound above zero with 80% power at true
mean `0.02` and `n=8` requires cluster standard deviation no greater than
approximately

```text
0.02 * sqrt(8) / (z_0.95 + z_0.80) = 0.02275 nats.
```

The actual proposed decision was stricter: it conjoined the lower bound, mean
margin, sign gate, three per-class noninferiority contrasts, Brier
noninferiority, a synchronized permutation gate, class support, cadence/dwell,
and run-validity requirements. Its joint power cannot be inferred from any one
component and was not established by the proposal.

## Leakage and model-selection blockers

Six construction clusters yield only 36 correlated cell rows and five
training clusters per fold in six-fold grouped cross-validation. A large
trajectory feature stack may be algebraically fit by ridge regression without
being credibly selected or calibrated at that sample size.

All scaling, regularization, calibration, Fourier or geometry selection,
feature reduction, and baseline completeness checks must occur inside the
construction split and be sealed before confirmation. Confirmation must score
the final construction-fitted models once. Refitting, cross-validation, or
feature choice using the eight confirmation labels invalidates the holdout.
The six cells within a seed must be aggregated or jointly resampled; independent
cell or stratum permutations would pseudoreplicate.

## Precedence and resource boundary

Any v0.6 contract must explicitly amend, rather than silently replace, the
unregistered v0.5.2 draft and preserve or expressly supersede its three-way
categorical endpoint, complete B2 baseline, cadence `{25,50,100}`, exit dwell
`{250,300,400}` with `300` primary, and stop-on-invalid-cell rule. Burned pilot
seeds and cells remain unavailable for confirmation.

Pilot timing implies roughly 18.8 GPU-hours for 84 runs at the older metric
cadence, before denser evaluation, B2/B3 extraction, and checkpoint I/O. A
fixed eight-cluster confirmation design is therefore neither demonstrably
powered nor demonstrably minimal.

## Required next attempt

Before any GPU execution, a source-frozen target-free simulator must evaluate
the complete conjunctive decision under a registered family of:

- cluster effect sizes and intracluster correlations;
- rare-class prevalence and class-support failures;
- invalid-cell and censoring rates;
- calibration and noninferiority margins;
- synchronized cluster-level permutation nulls; and
- total compute, checkpoint, artifact, and cleanup ceilings.

It must report type-I error, each-gate power, joint power, and invalid-run
probability, then choose confirmation cluster count from those results. If the
resource ceiling cannot support a design with the frozen joint-power target,
the sign, class, and Brier conditions must be demoted to diagnostics or the
experiment labeled exploratory. Neither route may be described as a
claim-eligible held-out confirmation without an explicit amended contract.

## Five conclusion layers

- **Metric robustness:** not evaluated; only exact design arithmetic was
  audited.
- **Task result:** no predictor was trained or evaluated.
- **Measurement reliability:** the cluster-unit and binomial calculations are
  exact; the normal calculation is explicitly only an optimistic approximation.
- **Claim support:** the fixed eight-confirmation-cluster conjunction lacks a
  credible power basis.
- **Operational decision:** stop before source registration or GPU execution;
  build and freeze the target-free joint-power simulator first.

References: [`LIVENESS_PILOT_RESULT_v0_4.md`](LIVENESS_PILOT_RESULT_v0_4.md),
[`PREDICTOR_PROTOCOL_DRAFT_v0_5_1.md`](PREDICTOR_PROTOCOL_DRAFT_v0_5_1.md), and
[`PREDICTOR_PROTOCOL_DRAFT_v0_5_2.md`](PREDICTOR_PROTOCOL_DRAFT_v0_5_2.md).
