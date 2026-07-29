# ASMP-9 v0.34 burned-pilot report

**Status:** `burned_pilot_analyzed_not_confirmation`

The full two-cold-start calibration captured 1,944 receipts.
The common standard-gamble ruler bracketed
10/36 cell-by-family
curves. Compound lotteries bracketed
10/18
curves. Mixture-affinity calibration was unavailable.

## Measurement stability

```text
maximum cold-start log-odds delta  0
95th-percentile option-order bias  0.814139359
monotonicity violations            67
```

## Factorized policy probes

```text
registered probes                  18
median-slope matrix numerical rank 3
minimum max-norm effect magnitude  0.000593132945
95th-percentile secant residual    0.0437066681
maximum secant residual            0.0651738154
```

These numbers calibrate a successor protocol; they are not gates retrofitted
to this pilot. Any confirmation must freeze its thresholds, common norm set,
prompt-family split, and practical margin in a new registration before
executing the untouched holdout families.

## Claim boundary

This burned pilot may calibrate one prompt-level ASMP-9 successor on one quantized Qwen model and one separately reported Prime runtime. It is not confirmation evidence, does not validate expected utility or semantic policy identity, does not authorize edits or stochastic policy trials, and does not resolve ASMP-9.

Machine-readable analysis content SHA-256:
`757641da68def358bbe4987b58f9398eddd81e917fbfc02a6dfb8c8b5375be43`
