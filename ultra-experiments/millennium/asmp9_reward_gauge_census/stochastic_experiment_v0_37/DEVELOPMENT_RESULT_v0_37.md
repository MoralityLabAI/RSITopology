# ASMP-9 stochastic-experiment development result v0.37

## Status

`development_not_claim_eligible`

This was a burned liveness census over the unregistered probability grid
`{0, 1/2, 1}`. It chose the confirmation design; it is not a preregistered
scientific result.

## What the pilot established

All 729 rational binary-output experiments on three targets and two nuisance
states were evaluated under four target decisions:

- each of the three nontrivial binary partitions; and
- identity recovery.

Every minimax risk and directional deficiency was returned with an exact
rational primal and dual LP certificate. Floating-point optimization proposed
active constraint sets but could not certify a value.

### A zero-error quotient does not determine bounded risk

For both observation semantics, at least one connected-component quotient
contained multiple exact minimax-risk profiles.

| oracle | component quotients | heterogeneous quotients | largest risk spread |
| --- | ---: | ---: | ---: |
| one sampled transcript | 4 | 1 | `1/6` |
| exact population law | 5 | 1 | `1/6` |

In each stratum, two experiments whose confusability graph had the same single
component produced identity-recovery risks `1/2` and `2/3`.

This is an instrument-liveness result, not a novel theorem. Full-support
channels already make the general phenomenon elementary.

### Full deficiency can price irrelevant nuisance information

The frozen conservatism witness compares:

```text
A: output is always 0
B: output equals nuisance xi, independently of theta.
```

Their expanded-parameter directional deficiency is `1/2`: one kernel cannot
simulate both nuisance outputs from the constant observation. Yet every
registered target-only decision has exactly the same minimax risk under `A`
and `B`; the maximum risk gap is zero. Full deficiency is therefore a valid
upper bound but can charge for information irrelevant to the target decision.

### Classical anchors

- informative-to-uninformative deficiency: `0`;
- uninformative-to-informative deficiency: `1/4`;
- registered risk-transfer comparisons: `100`;
- risk-transfer violations: `0`; and
- minimum exact bound-minus-gap margin: `0`.

The zero minimum is expected because some comparisons attain the classical
deficiency risk bound exactly.

## Design consequence

The claim-eligible successor must use a disjoint rational probability grid and
freeze both observation semantics. Its contribution is an exact ASMP-9
access ledger:

1. zero-error confusability and component quotient;
2. target-only minimax risk;
3. full expanded-parameter deficiency; and
4. the gap showing when the full comparison is conservative.

Blackwell dominance, Le Cam deficiency, nuisance-parameter comparison, and
the risk-transfer theorem remain attributed to their classical sources.

## Artifact

`DEVELOPMENT_RESULT_v0_37.json` is deterministic and has SHA-256
`6dec0df89c3e5840481780622acbfb1f07b443eccac4be42881f0e30eef0fe77`.

