# ASMP-9 dynamic response development result v0.66

Status: **unregistered development result; not claim eligible**.

## Verdict

Dynamic elicitation has three distinct finite outcomes:

```text
unidentifiable
identify_only_altering
identify_and_restore.
```

The distinction is exact for a declared deterministic response/update
transducer and terminal distortion.  It prevents successful initial-state
prediction from being mistaken for non-manipulative measurement, and prevents
a predictable query-created terminal state from being mistaken for discovery
of the initial value.

The core recursion is classical adaptive state identification.  Version v0.66
claims no new automata theorem.

## Exact characterization

The solver tracks labelled `(initial,current)` state pairs.  Safe singleton
beliefs initialize a least fixed point.  A belief enters the winning set
exactly when one query sends every possible output branch to an already
winning belief.

Membership after `k` iterations is equivalent to existence of an adaptive
decision tree of worst-case depth at most `k`.

If two unresolved initial labels reach the same current state under one output
history, they are irrecoverably merged.  No future query can identify which
initial label produced that history.

## Non-vacuous separations

- A read-then-reset query identifies the initial state perfectly but cannot
  restore it.
- A reset-then-read query makes the final state perfectly predictable while
  making the initial state unidentifiable.
- A reversible probe identifies in one step and restores in two.
- In a three-state fixture, every state pair is individually distinguishable,
  but no one adaptive experiment distinguishes the full set.

The last fixture rules out a tempting pairwise-only access criterion.

## Exhaustive census

All `256` complete deterministic transducers with two latent states, two
queries, and binary outputs were classified:

| Status | Count |
|---|---:|
| `unidentifiable` | 64 |
| `identify_only_altering` | 40 |
| `identify_and_restore` | 152 |

All `64` inverse-closed permutation-transition machines satisfy:

```text
ordinary identification iff identify-and-restore.
```

Their split is `16` unidentifiable and `48` identify-and-restore, with zero in
the altering-only class.

## Verification

The dedicated suite passes `10/10` tests.  It:

- compares the least fixed point with independent bounded decision-tree search
  on all `256` binary transducers under both ordinary and exact-restoration
  goals;
- verifies safe identification implies ordinary identification on all cells;
- verifies the inverse-closed implication on all `64` applicable cells;
- checks all three pairs in the pairwise-but-not-global fixture;
- verifies the terminal-distortion frontier on a nonuniform cost matrix; and
- fails closed on malformed machines, beliefs, budgets, and distortions.

The import-independent verifier reproduces the complete `64/40/152` census.

## What this changes

The static v0.65 strategic branch is no longer the last finite obstruction.
Even with a known deterministic response law, the query protocol can be a
write channel into the target.  ASMP-9 must distinguish:

```text
identifying an initial value,
identifying a terminal value,
restoring a value after measurement,
and constructing a value through measurement.
```

## Claim boundary

This result assumes a known deterministic finite transducer and evaluates only
terminal disturbance.  It does not validate a latent-state model for humans or
language models, prevent transient manipulation, cover strategic or stochastic
dynamics, establish a morally correct distortion, or resolve ASMP-9.
