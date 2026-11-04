# ASMP-6 v0.3 source-freeze note

## Current state

`source_candidate_not_executed_requires_commit_before_run`

This package is ready for source review only. It is not yet prospectively
frozen, no registered cell has been executed, and no result or verification
artifact belongs in the source-freeze commit.

## Atomic source set

The following eight files must be reviewed and committed together:

1. `PROTOCOL_v0_3.md`
2. `README.md`
3. `SOURCE_FREEZE.md`
4. `manifest_v0_3.json`
5. `multiletter_tensorization.py`
6. `run.py`
7. `test_multiletter_tensorization.py`
8. `verify_independent.py`

The manifest freezes the same sorted file list. The runner and independent
verifier reject a source commit unless every current byte matches the named Git
blob at that exact 40-hex commit.

Scientific entrypoints additionally require `python -I` and reject every live
entry other than the exact eight regular source files, including `__pycache__`,
symlinks, junctions, and other reparse points. Write-once artifacts live in the
sibling `artifacts_v0_3_multiletter_tensorization` directory and are not
evidence in the source commit.

## Freeze procedure

Run the source-only manifest validator and mutation/control tests from the README.
Review the disjoint directory and commit exactly the atomic source set. Do not
include the sibling artifact directory in that commit. Record the full source commit without
editing any source file afterward:

```powershell
$SOURCE_COMMIT = git rev-parse HEAD
git diff --exit-code $SOURCE_COMMIT -- ultra-experiments/millennium/asmp6_semantic_collusion_frontier/v0_3_multiletter_tensorization
```

Only then may a later task run the registered grid. `run.py` opens its output
with exclusive creation, embeds the source commit and source hashes, and emits
only a pre-verification conclusion. `verify_independent.py` independently
rechecks the manifest, current-versus-committed source bytes, result hash,
finite theorem, witnesses, controls, and five conclusion layers. It also opens
its output exclusively.

If either artifact path already exists, preserve it. Supply a new explicit
`--output` path for an authorized retry; never delete or overwrite evidence.
