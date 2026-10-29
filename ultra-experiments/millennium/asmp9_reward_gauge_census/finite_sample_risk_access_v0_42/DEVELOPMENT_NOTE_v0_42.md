# ASMP-9 v0.42 development note

Everything in this note is burned development evidence. It is not a registered
confirmation.

## Centered calibration

`DEVELOPMENT_PROTOCOL_v0_42.json` froze three sample counts against the already
known v0.41 population deficiencies. `DEVELOPMENT_RESULT_v0_42.json` matched
all three predictions:

| Samples per target/query | Adaptive classification | Open-loop classification |
|---:|---|---|
| 480 | inconclusive | inconclusive |
| 4,800 | pass | inconclusive |
| 48,000 | pass | fail |

The exact analytic floors under the centered approximation were 1,033 samples
for the adaptive pass and 5,985 for the open-loop fail.

This calibration used the population deficiency as the interval center. It
validated gate arithmetic but did not test channel sampling or empirical
polytope compilation.

## Sampled integration

The next burned run used 4,800 iid flip indicators per target/query, pooled
the registered shared flip parameter over four targets, rebuilt the rational
query channels, and ran the unchanged v0.41 adaptive/open-loop compiler.

The simultaneous query event held and all four exact population deficiencies
fell inside their intervals. Decisions were:

```text
classification/adaptive -> pass
classification/open_loop -> inconclusive
root_group/adaptive -> inconclusive
root_group/open_loop -> inconclusive
```

The group-loss intervals are narrower in absolute terms because their
target-wise loss spans are `1/3` and `2/3`, but the frozen group tolerance is
also closer to its population deficiency. The run therefore tests the
registered loss-span propagation rather than copying the classification
decision.

The exact counts, rational empirical error rates, exact deficiencies, and
intervals are in `DEVELOPMENT_SAMPLED_RESULT_v0_42.json`.

## Confirmation separation

The prospective confirmation uses:

- 48,000 fresh samples per target/query;
- a seed derived from the exact write-once registration bytes;
- strict `1/1000` practical margins; and
- a sample size at which all four decisions are arithmetically forced whenever
  the simultaneous channel event holds.

Neither burned seed is reused.
