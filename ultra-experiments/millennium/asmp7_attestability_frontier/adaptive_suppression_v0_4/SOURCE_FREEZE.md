# ASMP-7 v0.4 source-freeze note

## Candidate state

`source_candidate_not_executed_requires_commit_before_run`

This directory is reviewable source only. No v0.4 registry row, oracle grid,
11,520-comparison generic-terminal proof census, result, or verification
artifact has been executed. Source-only unit tests may exercise isolated
analytic fixtures, enumeration-only terminal counts, and deliberate
scope-breaking controls; they must not call `compile_result`, `run.py`, the
full 48-row registry, or the registered generic-terminal action grid.

## Atomic source set

Exactly these eight regular non-reparse files must be reviewed and committed
together:

1. `PROTOCOL_v0_4.md`
2. `README.md`
3. `SOURCE_FREEZE.md`
4. `adaptive_suppression.py`
5. `manifest_v0_4.json`
6. `run.py`
7. `test_adaptive_suppression.py`
8. `verify_independent.py`

The manifest, primary module, runner, verifier, and tests freeze the same
sorted set. Scientific entrypoints reject any additional live entry, including
`__pycache__`, test caches, symlinks, junctions, or other reparse points. They
also require CPython isolated safe-path mode before local import.

V0.4 result and verification artifacts live in the sibling
`artifacts_v0_4_adaptive_suppression` directory. They are not source files and
must not be created in the source-freeze commit.

## Freeze procedure

Run only the source checks documented in `README.md`. Review the theorem,
filtration, upstream bindings, negative controls, exact key universes, resource
stops, and mutation tests. Commit exactly the eight files. Then record the full
source commit without changing a source byte:

```powershell
$SOURCE_COMMIT = git rev-parse HEAD
git diff --exit-code $SOURCE_COMMIT -- ultra-experiments/millennium/asmp7_attestability_frontier/adaptive_suppression_v0_4
```

Rerun the source suite. Its real-repository source-binding regression must now
pass. Only afterward may a separately authorized task invoke `run.py` and then
`verify_independent.py` with `python -I`.

Both artifact paths use exclusive creation. If either already exists, preserve
it and use a new explicit output path for an authorized retry. Never delete or
overwrite evidence.

The 64-MiB limit is a peak traced-Python-allocation ceiling, not a process-RSS
or native-allocation claim. Any future change to hard-cap process memory would
be a new source version and registration.
