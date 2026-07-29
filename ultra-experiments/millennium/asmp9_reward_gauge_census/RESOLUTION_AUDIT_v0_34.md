# ASMP-9 resolution audit after physical acquisition v0.34

## Status

**ASMP-9 remains unresolved. The first registered real-model acquisition
closed one attempted measurement channel.**

The v0.34.4 burned pilot executed all 1,944 registered receipts on Qwen
3.5-0.8B-Q4_K_M. Capture reliability passed exactly across two cold starts,
but the prompt-level common-ruler construction failed before confirmation:
only 10 of 36 standard-gamble curves bracketed, 44 of 54 total curves had a
monotonicity violation, and no mixture residual was available.

## What this resolves

It resolves a narrow engineering-scientific question left by v0.33:

> Does the registered single-token, two-option prompt interface provide a
> sufficiently stable scalar ruler to connect the exact 18-dimensional
> decision quotient to this real-model capture?

For this model, precision, prompt grammar, and norm grid, the answer is no.
The failure is not attributable to cold-start nondeterminism: both probability
and target-log-odds deltas were exactly zero across starts. Positional bias and
non-monotone response dominate the intended effects.

## What it does not resolve

The run does not decide:

- whether the model has a useful reward-like internal object;
- whether another access grammar supplies a scalar ruler;
- whether mixture affinity holds under a valid ruler;
- whether the synthetic quotient predicts held-out behavior;
- whether broader reward shaping is identifiable; or
- ASMP-9's full two-sided resolution obligation.

## Revised load-bearing sequence

The next sequence is now:

1. **measurement-channel repair:** prospectively validate an order-robust,
   monotone scoring channel on burned prompts;
2. **ruler admission:** require adequate crossing coverage and practical
   effects above the channel's order and secant floors;
3. **mixture admission:** compute mixture residuals only for jointly bracketed
   rows;
4. **decision-quotient confirmation:** only after steps 1-3 pass, freeze and
   execute disjoint holdout families.

More samples through the rejected v0.34.4 channel do not address its failure.
The untouched holdout remains sealed.

## Canonical record

- [Prime result](physical_acquisition_v0_34/PRIME_RESULT_v0_34_4.md)
- [Machine-readable analysis](physical_acquisition_v0_34/BURNED_PILOT_ANALYSIS_v0_34_4.json)
- [Closeout receipt](physical_acquisition_v0_34/PRIME_CLOSEOUT_v0_34_4.json)
- [Analysis registration](physical_acquisition_v0_34/PRIME_ANALYSIS_EXECUTION_v0_34_4.json)

## Claim boundary

This audit records a successful physical capture and a failed measurement
instrument on one quantized small model. It is neither a confirmation result
nor an ASMP-9 resolution.
