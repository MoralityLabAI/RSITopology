# ASMP-9 v0.81 design record from burned v0.80 outcomes

Status: **design evidence only; written before v0.81 registration and fresh execution**.

## Why a new decoder is justified

Version v0.80 used a separate Jeffreys-corrected inverse-logit estimate at each
beta and averaged the three estimates within each arm. Its registered maximum
cardinal error was `0.2448331701`, so R0 failed.

Two outcome-aware diagnostics were computed only to choose the v0.81 design:

| Decoder on burned v0.80 rows | Maximum absolute error |
| --- | ---: |
| frozen v0.80 armwise average of inverse logits | 0.2448331701 |
| armwise joint logistic likelihood | 0.2124128268 |
| context-level joint likelihood using known offsets `{0,-2,+2}` | 0.0343246083 |

The last decoder does not tune a threshold or infer an offset from outcomes.
The offsets are exact route-margin effects of the already registered physical
interventions. Version v0.81 freezes them before using fresh rows.

## Outcome-free planning quantities

For the registered four base-margin hypotheses, three decoder arms, three beta
values, and 512 samples per cell:

```text
decoder samples per context:       4,608
worst Hellinger union bound:        7.427073338e-12
accumulated TV penalty:             0.04503465814
robustified M0 bound:               0.04503465814
M0 threshold:                       0.05
M0 planning margin:                 0.00496534186
```

The minimum Fisher information over the four registered base margins is
`767.0212`, corresponding to an asymptotic standard-error reference of
`0.03611`. This reference is descriptive and is not a gate or a finite-sample
coverage claim.

## Firewall

No v0.80 row is an input to v0.81 execution or adjudication. The new global
seed, complete candidate-ID namespace, decoder source, offsets, thresholds,
and fixed sequence are sealed before fresh outcomes. The v0.80 failure remains
unchanged and valid.

