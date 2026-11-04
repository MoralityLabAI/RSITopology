# Reviewer packet v0.22

## Claim to attack

For the finite local two-`q` collar with same-step causal raw observation, raw
observer homogeneity is equivalent to encoder-optimized feasibility, and every
feasible experiment has exact region `[2,infinity) x [2,infinity)`.

## Highest-value falsification attempts

1. Find a feasible raw observer for which the belief-tracking encoder cannot
   compute the current `q` before the current write.
2. Find a mixed earliest raw transition repairable by downstream encoding
   under universal worst-case safety.
3. Find a possible `q` word missing from the causal encoded language, or a
   legal encoding with fewer than `2^T` current-class transcripts.
4. Find a feasible two-block static partition of the contextual witness.
5. Contradict the inherited `80/176` or `724/52,384` census split.

## Scope check

Delayed sensing, bounded encoder memory, forced-raw charging, and continuous
observations are successor contracts. They are not counterexamples unless the
review also shows that v0.22 silently relied on one of them.
