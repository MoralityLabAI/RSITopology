# ASMP-3 v0.1 protocol-scope adjudication packet

## Decision requested

Determine which object the v0.1 phrase “admits a protocol” quantifies over:

```text
Disposition F — frozen game
  Admissible transcript encodings are fixed before protocol strategies.
  A protocol may choose verifier/prover algorithms only inside that alphabet.

Disposition E — existential encoding
  A protocol may introduce any encoding that fits the transcript budget.
  The admissible-encoding sentence is a resource/serialization constraint,
  not a fixed alphabet.
```

This is a scope decision, not a request to recompute the parity formula.

## Canonical evidence for Disposition F

The canonical setting says to freeze:

- the decision relation;
- public-coin message order and stopping rule;
- the atomic query language and registered replications;
- the ideal and noisy oracle model; and
- transcript, query, and verifier resource budgets.

It then states that “Admissible transcript encodings ... are part of the game.”
The ordinary literal reading is that a task-game instance contains its
admissible encodings before one asks whether a verifier strategy succeeds.

Under that reading, `G_fix` in
`FROZEN_GAME_SPECIFICATION_v0_7.md` is a legal task-game family. Its three
displayed conjecture conditions hold and its exact best gap vanishes.

## Canonical evidence for Disposition E

The named conjecture says:

> A task family admits a constant-gap ... oversight protocol if and only if ...

In complexity theory, “admits a protocol” often existentially quantifies over
the protocol's message functions and encoding. The v0.1 document does not
provide a formal type signature separating:

```text
task-family data,
game data,
protocol data,
verifier strategy data.
```

Under that reading, `G_admit` is legal. The two advocates send the `d` semantic
bits, the verifier selects a differing coordinate, and one persistent-noise
query yields gap `3/5`.

## Facts that do not depend on the disposition

The v0.7 exact harness and independent checker establish:

1. `r_R=d` for the complete frozen terminal-transcript universe;
2. a uniform honest strategy for every realized adversarial move sequence;
3. `a_H(k)<=1/5`;
4. frozen-encoding minimax gap `(3/5)^d`;
5. existential-encoding vector-protocol gap `3/5`; and
6. polylogarithmic verifier, query, and transcript costs on both branches.

The disposition changes which protocol class is being characterized; it does
not change these calculations.

## Reviewer questions

1. Does v0.1 make admissible transcript encodings part of the frozen task-game
   tuple, or part of the existential protocol?
2. If frozen, is `G_fix` within the full canonical scope rather than a narrower
   subclass?
3. If existential, is the vector-disagreement protocol legal under every stated
   resource and oracle restriction?
4. Does the chosen reading make the displayed iff a closed mathematical
   sentence, or is a successor problem version required?
5. Under the chosen reading, should the parity result be classified as:
   `negative-resolution candidate`, `definition-debt theorem`, or
   `partial progress`?

## Required adjudication record

An attributable reviewer should report:

- identity, relevant complexity/game-semantics expertise, and conflicts;
- the SHA-256 of `RELEASE_MANIFEST_v0_7.json`;
- one of `frozen_game`, `existential_encoding`, or `not_closed`;
- answers and evidence for all five questions;
- whether the decision is intended as a v0.1 interpretation or a proposed v0.2
  amendment; and
- permission to store the adjudication.

Model-generated reviews are useful stress tests but cannot supply the
authoritative independent scope decision.

## Disposition consequences

### If `frozen_game`

Merge the v0.3 probability proof and v0.7 game specification into one sealed
negative-resolution review target. Remove the pre-review hold only after an
independent complexity reviewer confirms that the complete game is canonical.

### If `existential_encoding`

Retire the parity family as a counterexample to protocol admission. Preserve
the exact quantifier-fork theorem as a definition-debt result and continue the
broader characterization program.

### If `not_closed`

Publish a successor ASMP-3 version with explicit type signatures and do not
advertise either branch as resolving v0.1.
