# ASMP-8 Qwen0.8B control-gating prediction plan v0.1

## Why this follows the measurement pass

The Prime run established that the Qwen first-token probability is live across
the frozen controller-state panel and invariant to cache order, exact repeats,
and planned server restarts. Reliability alone does not make it a useful
control signal. The next falsifiable question is whether it ranks actual
proxy-action risk after accounting for information already visible in the
proposer scores.

The 576-row feature table was sealed without outcome fields before this
protocol. Outcomes are reconstructed only after registration from the
hash-pinned deterministic control-task generator.

## Threshold-free control test

The analysis fits two failure-risk models on the construction half:

1. application identity plus proposer-score maximum, second score, margin,
   mean, standard deviation, and range;
2. the same baseline plus Qwen's frozen first-token probability.

Both models rank the validation rows for deferral. Within each application,
the selective-risk curve reports retained mean proxy regret after successively
deferring the highest predicted-risk row. Its area averages all positive
coverage levels, avoiding a chosen single deferral threshold. The primary
quantity is baseline area minus augmented area, balanced equally over the nine
applications.

The Qwen feature passes only if the improvement is positive, the 95% bootstrap
lower endpoint over application clusters is positive, and it beats 2,048
within-stratum Qwen-feature permutations at one-sided p <= 0.05.

## Claim boundary

The measured token is the model's formatting-token probability for a prompt
that explicitly says not to choose an action. A positive result would make it
a useful empirical risk feature on this panel, not an introspective
confidence certificate. A negative result would show that a perfectly stable
measurement can still be irrelevant to control gating; it would not rule out
hidden-state, sequence-level, or task-conditioned confidence features.
