# ASMP-3 round-robin review

## Verdict

**`revise_before_pilot`**. The trace game is bounded, inexpensive, and has a
useful exhaustive checker, but its primary estimand does not yet imply uniform
soundness and completeness.

## Findings

1. **`fatal` as specified — paired minimax gap.**
   `Delta_N = min_(o,nu)[P(reject|false,o,nu)-P(reject|true,o,nu)]` forces the
   same obfuscator/noise choice into both terms. A soundness adversary may choose
   a different true transcript from the false-transcript adversary. Moreover, a
   gap above `0.20` can coexist with unusable completeness (for example, false
   rejection `1.00`, true rejection `0.79`). Thus passing the frozen gate would
   not establish the stated verification property.

2. **`repairable` — correlated-noise class is not closed.**
   “Beta-binomial,” “two-state burst,” and “query-history adaptivity within the
   declared law” omit parameter ranges, mixing/minimum-entropy constraints, and
   whether marginal error is unconditional or conditional on history and atom.
   With only an unconditional `eta<=0.20`, an adaptive law can concentrate all
   errors on the canonical refuting atoms. Nine replications then need not
   amplify. The globally correlated control lies outside the positive class, so
   it does not by itself certify liveness *within* that class.

3. **`scope_narrowing` — adaptive obfuscator.**
   Selecting one transformation from a finite menu on construction seeds tests
   held-out transfer of a trained attack, not a worst-case adaptive obfuscator.
   This is valid if the claim says exactly that. The optimizer, objective,
   finite program universe, true/false-specific choices, tie breaking, and
   enforcement of the transcript-length budget must be sealed.

4. **`repairable` — gates.**
   The `>=0.99` locator condition lacks its own simultaneous confidence rule.
   The “adaptive reduction >=0.10” criterion needs a paired held-out interval,
   and multiplicity across sizes, laws, and obfuscators needs a named max-statistic
   or familywise construction. An expected-failure cell inside the admissible
   positive noise class is needed to show the main claim is not forced.

5. **`nonissue` — basic implementation liveness and claim boundary.**
   Noiseless, random-locator, syntactic-leak, exhaustive-small-`N`, and global
   correlation controls isolate sensible failures. The proposal correctly
   limits evidence to one synthetic game and does not claim ASMP-3 resolution.

6. **`repairable` — resource credibility.**
   Synthetic estimates are plausible, but cell counts and noise-parameter grids
   are absent, so `35–75 min` is not reproducible. Qwen costs cannot be assessed
   without the number and maximum token length of semantic judgments.

## Concrete repair

Replace the scalar gate with separately frozen uniform errors:

```text
FN_N = sup_(false,o,nu) P(accept),
FP_N = sup_(true,o,nu)  P(reject),
Delta_N^rob = 1 - FN_N - FP_N.
```

Require simultaneous upper bounds on both errors (with practical margins),
then derive the gap. Freeze a finite conditional-noise parameter table and
include one admissible mixing-boundary law where amplification fails. This
repairs the strongest objection without enlarging the experiment.
