# Review of Fable `files(3).zip`

Source archive SHA-256:
`FB1C354BC48329B16BE6C8043910F0FFBE7A476CDC2F7FA0709136A329FB6725`.

## Adopted

- Environment metadata is now embedded in every new result receipt. A separate
  Windows/Python-3.11 replay lock records the exact local numerical stack.
- The sparse fixture has a `geometry_noise` control. `0.0` takes the original
  code path without consuming RNG and is tested for bit-identical outputs.
- Geometry receipts report occupancy margin and warn below `0.10`. This is a
  fixture-calibrated warning, not a new gate.
- Per-fold and mean KL-normalized information coefficients are reported as a
  descriptive policy sensitivity.
- The dense occupancy sweep is registered as a standing control and checkpoints
  after every noise/seed cell.
- Fable's backfill and sweeps are imported with source hashes and remain external
  diagnostic evidence.

## Deliberate correction

The patch proposed replacing the v0.2 standardized-uplift gate with

\[
IC=\frac{\text{standardized uplift}}{\sqrt{2\,KL}}.
\]

This is equivalent to a fixed standardized threshold only when all folds bind
at one common KL cap. If a fold is non-binding or nearly uniform, the ratio
changes the estimand and can be unstable near zero KL. Protocol v0.2.1 therefore
keeps v0.2's primary gate unchanged and treats IC as descriptive. Outcome-based
selection of the KL cap remains prohibited.

The statement that v0.1's absolute threshold was “arithmetically unreachable”
is also narrowed: it was unreachable for this planted fixture at the frozen
cap and arbitrary synthetic reward scale. That does not make absolute reward
units meaningless in every real task.

## Not promoted

The external backfill reports standardized uplift `0.1239902`, above v0.2's
`0.10` threshold, with rank `32`. It annotates the v0.1 receipt but does not
upgrade it: the replay ran outside the repository's approved enforcement and
receipt path. The full local calibration sweep is prepared but not executed
because current CPU/I/O hard-cap delegation remains blocked.

## Second-review resolution

Fable's follow-up confirmed the implementation and the decision to keep the
occupancy margin fixture-calibrated and non-gating. Its remaining scientific
seam is now explicit: sparse `geometry_noise=0` preserves the legacy RNG stream,
whereas every positive level consumes an extra skew draw. Zero is therefore a
compatibility baseline; graded positive-noise sweeps use their smallest
positive level as the paired reference. This rule is frozen in protocol v0.2.1,
the fixture docstring, and a protocol test.

The follow-up's host recommendation was converted into guarded, reviewable
assets rather than applied: a tracked systemd drop-in, an installer requiring a
literal host-change confirmation, a read-only verifier, and a probe-first
runbook. Promotion remains blocked.
