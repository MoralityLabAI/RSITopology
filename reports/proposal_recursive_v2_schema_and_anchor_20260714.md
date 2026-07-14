# Proposal-recursion v2.0.3 schema and chronology report

Date: 2026-07-14

## Result

The three requested schema refinements are implemented and executable.

1. The two-component composite gate has a registered total table over all 25
   ordered pairs in `{pass, fail, inconclusive, unavailable, invalid}`. Any
   valid component failure makes the conjunctive composite fail; only
   `pass/pass` advances. Every component retains its own stop reason and
   extension consequence. There is no `dominant_sequence_stop` field and no
   consequence severity ranking.
2. The timestamp design is a sandwich. A later run-specific pre-anchor must
   seal the protocol, evaluator, runner, complete source universe, seeds,
   splits, and environment lock and become independently Bitcoin-verified
   before the runner may read source data. The exact write-once run receipt is
   then submitted as the post-anchor. No manifest can be emitted until the
   post submission validates against that receipt.
3. The immutable v1 release has been forward-submitted to four external
   calendars. This bounds future tampering after the proof is upgraded, but it
   cannot retroactively establish that the v1 protocol predated its run.

## Schema anchor versus run authorization

The v2.0.3 schema payload has SHA-256:

```text
f3f5b150872031032348d5ef804a667d93d0d552e2b2cae7aba959cdc04ced87
```

It was submitted under the distinct role `schema_chronology`. Its embedded
purpose is `schema_chronology_only`; the validator rejects it as run
authorization even after Bitcoin verification. This dates the design without
opening the data. A later full experiment needs a new payload with
`anchor_purpose=run_authorization` and the complete run universe.

The current proof status is `calendar_submitted_pending_bitcoin`. It is not yet
an independently verified Bitcoin timestamp, and no source-data access is
authorized by it.

## Superseded drafts

The pending v2.0.0 and v2.0.2 submissions and the unanchored v2.0.1 draft are
preserved. None authorized data access. V2.0.3 supersedes them because it:

- captures and hashes verification-command output rather than inferring
  verification from proof structure;
- requires a nonempty independently verified Bitcoin-block record for a
  run-specific pre-anchor;
- distinguishes schema chronology from run authorization in both payload and
  receipt role; and
- uses the actual schema-directory path for its environment lock.

## Paper framing

The three negative results are one claim tested with progressively stronger
instruments: attribution-selected sites, hard-rank cuts, and a continuous
gauge-invariant family. Each closes an escape route left by the previous
instrument. The methods protocol is therefore the third instrument, not an
appendix.

Suggested abstract sentence:

> Across attribution-selected sites, hard spectral cuts, and a continuous
> gauge-invariant atlas, progressively stronger instruments failed to recover
> a stable global edit object; the preregistered third instrument then stopped
> its own author's planned investment under an unfavorable outcome.

This supports a methods-and-negative-results claim. It is not evidence that
recursive self-improvement exists or that no behavioral superstructure exists.

## Verification

- Focused v2 evaluator and anchor-guard suite: 12 tests passed.
- The 25 table cells are compared exactly against the executable evaluator.
- Schema-only anchors are tested to be incapable of authorizing source access.
- Pending post anchors require a serialized external calendar.
- Final verified anchors require a nonempty independently verified block list.
