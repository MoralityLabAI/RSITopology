# ASMP-9 physical acquisition v0.34.4: Prime result

## Verdict

**The physical capture succeeded; the registered prompt-level utility
instrument did not.**

The full 1,944-receipt, two-cold-start calibration completed without a resource
abort. Every choice vector was complete, and the maximum probability and
target-log-odds differences between cold starts were both exactly zero.
Nevertheless, the common-ruler interface was too order-sensitive and
non-monotone to support the intended mixture or utility analysis:

| Diagnostic | Result |
|---|---:|
| standard-gamble curves bracketed | 10 / 36 |
| compound-gamble curves bracketed | 10 / 18 |
| curves with at least one monotonicity violation | 44 / 54 |
| total monotonicity violations | 67 |
| median absolute option-order bias | 0.588965 |
| 95th-percentile absolute option-order bias | 0.814139 |
| mixture residuals available | 0 |

This is a measurement-boundary result. It does not show that Qwen lacks a
reward representation, that expected utility is false, or that the v0.33
decision quotient is wrong.

## What remained live

The 18 frozen factorized probes produced a rank-three median slope matrix
across the three policy contrasts. Their maximum-norm effects ranged from
`0.000593` to `0.064001`, and their 95th-percentile absolute secant residual
was `0.043707`.

That liveness does not rescue the measurement. The 95th-percentile order bias
was 12.72 times the largest observed maximum-norm policy effect. The
pilot-derived practical effect floor (`2 * order_bias_q95 = 1.628279`) was
25.44 times that largest effect. These are calibration comparisons, not
post-hoc confirmation gates.

## Scientific consequence

The v0.33 algebraic factorization remains an exact description of the frozen
synthetic object. This run rejects the attempted bridge from that object to a
single-token, two-option, prompt-level common ruler on this Q4 Qwen 0.8B
runtime. In particular:

1. exact cold-start repeatability rules out runtime nondeterminism as the
   explanation;
2. extensive order bias and monotonicity violations prevent a stable scalar
   ruler from being inferred;
3. absent jointly bracketed component and mixture curves, mixture-affinity is
   `unavailable`, not zero and not refuted; and
4. the untouched holdout families remain closed.

A successor should change the measurement channel, not merely increase sample
count. A credible next fork must prospectively isolate positional bias (for
example, calibrated logit scoring or a separately validated multi-token
choice grammar), re-establish monotone ruler crossings, and only then reopen
mixture or decision-quotient confirmation.

## Execution and resources

- Prime pod: `fa3b9e2ed2b5455b88f16c616fd20923`
- GPU: one RTX 6000 Ada, listed at USD 0.75/hour
- Pod lifetime: 2,421 seconds; listed-rate upper-bound cost USD 0.504375
- Capture runtime: 210 seconds
- Analysis runtime: 2 seconds
- Peak GPU allocation above baseline: 1,054 MB
- Peak GPU temperature: 38 C
- Thermal pauses: 0
- Active pods after closeout: 0

The recovered archive contains 2,004 manifest-bound files. Every manifest
entry was independently rehashed after extraction with zero failures.

## Hash chain

| Object | SHA-256 |
|---|---|
| v0.34.4 registration | `6f518cede92b5b6defad6caf00db4066f331ae3cc595ea7c82dfd0950bfc7482` |
| pilot records | `8797772ac629a5b02cbc116acdc890236c3768989fbb02620ed857717b906c40` |
| capture summary | `c9cd3c18ddcd45f48376ee710e49ba9d33a5acc39a1113aaf08bb12356938d6d` |
| analysis JSON | `9fec63ebcfaa1761b3826a70901e85f7c43b98cb7d77113c70a61b66832dfbf0` |
| analysis content | `757641da68def358bbe4987b58f9398eddd81e917fbfc02a6dfb8c8b5375be43` |
| recovered archive | `b4e7f656220a375d08f4699b605823f789c64340517f58702798816c2253b6e2` |

## Claim boundary

This completed burned pilot calibrates one explicit prompt-level access grammar
on one Q4 Qwen 0.8B model and one Prime runtime. It is not confirmation,
does not establish expected utility, does not identify a maximal shaping
gauge, does not authorize edits or policy changes, and does not resolve
ASMP-9.
