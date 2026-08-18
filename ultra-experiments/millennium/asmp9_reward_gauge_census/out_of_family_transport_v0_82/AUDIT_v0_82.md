# Independent audit of ASMP-9 v0.82

## Integrity

- Prereveal commit: `44ff49fd53f1f504f6faf23dc06e744420005f11`.
- Registration SHA-256:
  `9d77e777f020f0e4c696afb1cb15569fd6613dbb256107c988a6ae8aac06417a`.
- Authorization SHA-256:
  `adb131f0016a49330fe77a38d3b63d32a9a8acd23a766b7770735ad65d370f58`.
- Raw records SHA-256:
  `0826af13da580bec025881cc0640b3105f914ca6de4ff548c6e5c3d6f170a2dc`.
- Registered transport analysis SHA-256:
  `55db7f37082ce482cbb364246db814638237cfc888bd1da157719cead0f65d5c`.

The remote branch contained the exact registration before the wrapper start
event.  The result release does not alter the registration or authorization.

## Independent recomputation

`audit_v082.py` does not import the registered scorer, base analyzer, or
transport-gate module.  From `records_v0_82.jsonl` it independently checked:

- exactly 528 unique registered rows;
- the exact twelve-scenario universe;
- finite log probabilities and exact log-odds arithmetic;
- byte-identical repeat pairs;
- display-order canonicalization;
- all 48 directed specificity contrasts;
- the measurement epsilon;
- local liveness, prediction-envelope membership, and common-interval
  intersection; and
- owned-process runner, analysis, cleanup, and lingering-PID status.

It reproduced `N0/I0/L0/T0/R0 = pass`, `G0 = fail`, 11 envelope hits, 21
intersection hits, and the final negative decision.

## Resource-label reconciliation

The native v0.68 wrapper label is retained verbatim in the archive.  Its sole
invalidating condition was the inherited system-wide page-file rule.  Under
the precommitted v0.82 contract that movement is noncausal telemetry; no owned
hard-limit, exit-code, or cleanup failure occurred.  Both labels are exposed
so an auditor can apply either resource convention without changing the
scientific rows.

## Audit boundary

This is an artifact-integrity and deterministic-recomputation audit.  It is
not independent model inference or evidence beyond the frozen finite registry.

