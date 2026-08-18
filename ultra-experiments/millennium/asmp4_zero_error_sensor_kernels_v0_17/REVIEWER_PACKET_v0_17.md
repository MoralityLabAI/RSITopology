# Reviewer packet v0.17

## Claim

A finite memoryless registered sensor kernel is support-zero-error feasible iff its low- and high-`q` output supports are disjoint. Its exact rate depends on active raw support size, not probability magnitudes.

## High-value falsification attempts

- Give a safe common first control for a shared output emitted by both `q` classes.
- Find a feasible relation among the 52,384 overlap cases.
- Find an infeasible relation among the 724 disjoint-support cases.
- Produce an active raw output word missing from the charged transcript alphabet despite arbitrary disturbances and positive support.
- Break the combinatorial formula `3^l-2` for two ordered nonempty supports covering `l` outputs.
- Show that one of the 104 deterministic kernels fails to map to a v0.16 partition.

## Reproduction

Run the commands in `README.md`. Compare the exhaustive support loop with the independent multinomial calculation and inspect the frozen contract and claim.

## Scope firewall

Do not import conclusions into average-error or vanishing-error channels. Those quantifiers can charge probabilities and coding blocks rather than raw support, and require a separate registered theorem.
