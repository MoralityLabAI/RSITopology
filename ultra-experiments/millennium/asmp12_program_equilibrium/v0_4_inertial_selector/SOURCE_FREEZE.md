# ASMP-12 v0.4 source freeze

Status: `source_candidate_not_executed_requires_commit_before_run`.

Exactly these eight regular non-reparse files form the atomic source set:

1. `PROTOCOL_v0_4.md`
2. `README.md`
3. `SOURCE_FREEZE.md`
4. `inertial_selector.py`
5. `manifest_v0_4.json`
6. `run.py`
7. `test_inertial_selector.py`
8. `verify_independent.py`

No registered graph cell, complete 24-trajectory grid, robustness census,
primary artifact, or verification artifact may be executed before this source
set is reviewed and committed. Source-only tests may exercise individual
traces, one-cell graph fixtures, path rejection, and deliberate mutations.

Freeze sequence:

1. Run only the source checks in `README.md`.
2. Review the selector, complete-graph semantics, exact predictions, controls,
   predecessor hashes, independent implementation, and claim boundary.
3. Commit exactly these eight files together.
4. Record the full source commit and change no source byte.
5. Rerun the source suite; the real-repository source-binding test must pass.
6. Only then may a separately authorized task create the primary write-once
   result, preserve it, and run the independent verifier.

The live source directory must contain exactly these eight files, with no cache,
symlink, junction, or other reparse entry. Both scientific entrypoints require
`python -I`. The 64-MiB figure measures only peak traced Python allocation, not
process RSS or native allocation.
