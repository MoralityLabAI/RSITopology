# ASMP-9 generalized-theta optimizer development (v0.25)

This branch develops an exact global optimizer for a nontrivial
overlapping-cycle class at `epsilon=1/2`.

The key candidate theorem is:

> Every global optimum on a generalized theta block balances counts within
> each individual path.

The remaining optimization enumerates path totals using a closed exact
availability formula.  For a fixed number of paths it is polynomial in the
numerical trial budget and pseudopolynomial when the budget is binary encoded.

Status: development-only, unregistered, and not claim-eligible.

Read:

1. `PRIOR_ART_GATE_v0_25.md`;
2. `THEORY_DRAFT_v0_25.md`;
3. `DEVELOPMENT_NOTE_v0_25.md`; and
4. `theta_optimizer.py`.

