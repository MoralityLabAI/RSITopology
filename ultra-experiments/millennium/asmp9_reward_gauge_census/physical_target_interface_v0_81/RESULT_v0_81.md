# ASMP-9 structured physical target-interface result v0.81

## Verdict

```text
structured_finite_sample_target_recovery_established_on_controlled_fixture
```

All six gates passed on fresh rows. ASMP-9 remains unresolved.

## Chronology and integrity

- prereveal registration commit:
  `f8c6ba7d0da03d74e84e26bae82d98b1cae3f075`;
- registration SHA-256:
  `7e9b2807ba92bb3e5ba73739c7429f7fe55c8ad13136103e2371749b8f4480b4`;
- fresh candidate namespace: `v081|...`;
- primary rows SHA-256:
  `a1b86786de0a785c0c60eafcf163103305705085a177fae482fe8dd8897a3c8b`;
- primary and replay rows, results, and run receipts were byte-identical; and
- an import-independent post-run implementation rederived every gate.

The registration commit was pushed before the fresh execution directory was
created.

## Fixed-sequence result

| Gate | Decision | Evidence |
| --- | --- | --- |
| W0 | `pass` | shaping targets matched; non-gauge offsets were exactly ±2; both deltas had squared norm 2 |
| I0 | `pass` | primary/replay rows, results, and receipts were byte-identical |
| D0 | `pass` | exact decoder-arm set and offsets; shaping rows excluded; all four likelihood scores bracketed a unique root |
| R0 | `pass` | maximum cardinal error `0.0665203691 <= 0.15`; all signs correct |
| L0 | `pass` | maximum shaping/base probability difference `0.05078125 <= 0.12` |
| M0 | `pass` | robustified bound `0.04503465814 <= 0.05` |

## Matched decoder result

The fresh rows provide a direct control for the mechanism that v0.81 changed:

| Decoder on the same fresh rows | Maximum absolute error | Frozen R0 threshold |
| --- | ---: | ---: |
| v0.80-style armwise average of inverse logits | 0.1853778422 | 0.15 |
| v0.81 intervention-structured joint likelihood | 0.0665203691 | 0.15 |

The baseline is descriptive and consumes no gate. Nevertheless, it shows that
the full-pass result is not explained merely by a lucky fresh seed making the
old decoder pass: on these same rows the old estimator remains above the
registered practical-error threshold.

The structured decoder estimates one base margin per context from the base and
known ±2 non-gauge interventions. Its largest error occurred in the held-out
`holdout_high` context. Both held-out contexts passed the same frozen cardinal
criterion used for construction contexts.

## Robustness boundary

The M0 decomposition was:

```text
Hellinger union bound:       0.0000000000074271
accumulated TV penalty:      0.0450346581355146
robustified bound:           0.0450346581429416
threshold:                   0.05
remaining margin:            0.0049653418570584
```

The finite-hypothesis discrimination term is negligible; the registered
misspecification budget is binding. This is a narrow positive region, not a
claim that additional observations monotonically improve the robust
certificate. More decoder-consumed samples would eventually fail M0 through
TV accumulation even while point estimation improves.

## What changed from v0.80

Version v0.80 remains a valid negative result for an armwise decoder. Version
v0.81 establishes a different, prospectively frozen statement: when physical
interventions have known target offsets, their responses can be combined in a
single likelihood and can repair the finite-sample cardinal-recovery failure
at the same per-query sample count.

This is an access result. The gain is purchased by stronger registered
structure—known intervention effects—not by changing the target, error
threshold, response channel, or sample count after seeing outcomes.

## Claim boundary

The result is exact only for one controlled finite-MDP softmax fixture with
known intervention offsets, four registered base-margin hypotheses, iid
Bernoulli responses, and the frozen per-sample TV stress. It does not show
that the intervention offsets are available in natural systems, validate a
softmax demonstrator model, identify human or language-model values, establish
moral adequacy, or resolve ASMP-9.

