# Repository hygiene pass — 2026-10-12

Non-destructive additions only. Nothing was moved, untracked, re-sealed or
merged; the decisions that would change history or published artifacts are
listed at the end for the owner.

## What was added

| item | purpose |
|---|---|
| `scripts/audit_receipts.py` | recomputes every SHA-256 file binding in the repository's JSON receipts and classifies it (see below); writes `reports/receipt_audit_<date>.md/.json` |
| `scripts/run_package_tests.py` | runs each ASMP package directory's own tests in a separate pytest process (the tree reuses module names, so one collection cannot work); `--filter`, `--jobs`, `--list` |
| `scripts/list_registered_not_run.py` | one page of every protocol or run whose status says registered but not executed; writes `docs/REGISTERED_NOT_RUN_<date>.md` |
| `.github/workflows/tests.yml` | CI: core `tests/` on every push and pull request; the problem-set validator and the receipt audit as non-gating reports; the per-package suites on manual dispatch |
| `pyproject.toml` | optional dependency groups: `test` (pytest, hypothesis, matplotlib, sympy, networkx) and `model` (torch, transformers, bitsandbytes, safetensors), which were used but undeclared |

## Receipt audit

`scripts/audit_receipts.py` scanned 1,126 JSON files and found 3,421
bindings of a hash to a named file (content hashes of prompts and rows are
not bindings and were skipped).

| status | bindings | meaning |
|---|---:|---|
| `match_raw` | 2,798 | sealed hash equals the file as checked out |
| `external_absolute` | 489 | absolute path outside the repository: `C:\projects\…` 243, `D:\Research_Engine\…` 117, `/workspace/…` 61, `/home/…` 40, `C:\Users\…` 22; unverifiable from a checkout |
| `mismatch` | 76 | the named file no longer has the sealed hash |
| `match_crlf_only` | 36 | the sealed hash is that of the file with CRLF line endings; `.gitattributes` mandates LF, so every compliant checkout fails these seals (19 receipts: ASMP-9 24 bindings, ASMP-11 7, ASMP-10 3, ASMP-6 2) |
| `missing` | 22 | untracked artifacts, model files, archives |

The 76 mismatches split by what was sealed:

- 44 are *living summary documents*: the ASMP-9 README (sealed by 18
  registrations, changed by every later version), the v0.2 progress note
  (10), the fellowship link pages (10). Sealing a document that is meant to
  change guarantees a stale seal; a registration should pin a git blob id or
  a dated copy instead.
- 32 are *package-level*: the two ASMP-11 v0.2.1 registrations seal eight
  source, protocol and test files that have since changed
  (`PROTOCOL_v0_2_1.md`, `run.py`, `verify_result.py`,
  `crossover_frontier.py`, `build_registration.py`, `experiment_v0_2_1.json`,
  `test_crossover_frontier.py`, `README.md`); the ASMP-9 v0.34 burned-pilot
  registrations seal ten scripts and tests that have since changed; the
  ASMP-2 v0.2 result seals a theorem file that changed; the ASMP-9 v0.20
  census seals its own source file that changed. The audit does not
  adjudicate whether the later edits were legitimate repairs that should have
  produced a new registration, or edits to sealed inputs; either way the
  current files are not the ones the registrations describe, and a reader
  who checks the hashes will find that out.

Seals also live hard-coded in Python verifiers, which the audit does not
scan. The per-package test run found one worked case: the ASMP-4 v0.15
verifier (`asmp4_semantic_selector_audit_v0_15/verify_semantic_selector_audit.py`)
holds eight artifact seals, five of which are hashes of the CRLF rendering of
the artifact (`preflight.json`, `stage.json`, `robustness.json`,
`semantic_clause_rows_v0_15.jsonl`, `robustness_observations_v0_15.jsonl`),
so three of its ten tests fail on every LF checkout. The package's
mathematics is unaffected; its "independent artifact integrity" gate is what
fails. There are likely more such cases among the 19 packages that fail
below.

Recommendations that need no history rewrite: seal LF-normalised bytes (or
refuse to seal a file containing CR); never seal a living document; emit
repository-relative paths; keep the audit running in CI, as it now does.

## Test baseline

Core suite on this machine: 251 passed; three tests deselected in CI because
they read files outside the repository or need torch (listed in
`docs/CRITIQUE_NOTES_20261012.md` §7). The problem-set validator fails on the
stale README receipt and is reported, not gated.

The first CI run (Ubuntu, 2026-10-13) failed on two tests that had only ever
run on Windows; both were test-side assumptions, not defects in the code
under test, and both are fixed:

- `tests/test_qwen_geometry_analysis.py::test_bound_paths_and_hashes_have_canonical_shape`
  checked `Path(p).is_absolute()` on the registration's `D:\Research_Engine\…`
  capture paths; a POSIX `Path` calls a Windows drive path relative. The test
  now accepts either flavour of absolute path.
- `tests/test_zk_conformance.py::test_replay_all_golden_vectors` compared the
  float replay of the gate bit-for-bit with values recorded on Windows. The
  float path calls the platform libm, and glibc and the MSVC runtime round 15
  of the 200+ recorded sines differently in the last bit (both results are
  within one ulp of the true value, for example `2·sin(0.9075764461263718)`:
  glibc is 0.45 ulp low, MSVC 0.55 ulp high). The float replay is now compared
  to `1e-14` relative; the fixed-point path, its decision and its canonical
  SHA-256 remain bit-exact, which is the contract the ZK guest depends on.

After the fixes the core suite passes on both platforms: 255 passed, 5
deselected (Windows 55 s, WSL Ubuntu 50 s).

Per-package suites (`scripts/run_package_tests.py --jobs 3`, about ten
minutes): 200 package directories, 3,038 tests, 196 directories pass. The
four that fail, and why:

| package | failure | cause |
|---|---|---|
| `asmp10_capability_transition` | 3 collection errors | `torch` not installed (training pilots; `model` extra) |
| `asmp9_reward_gauge_census/out_of_family_transport_v0_82` | 1 of 4 | manifest test reads `torch` package metadata (`model` extra) |
| `asmp11_access_ladder/covering_frontier_v0_2_1` | 1 of 27 | `prior_anchor_v0_2.json` seals the CRLF rendering of `frontier.csv` |
| `asmp4_semantic_selector_audit_v0_15` | 3 of 10 | five of the eight seals hard-coded in its verifier are CRLF seals |

Before `psutil` was installed, 19 directories failed; fifteen of those were
collection errors on that one undeclared import, now in the `test` extra.

## Registered but not run

`docs/REGISTERED_NOT_RUN_20261012.md` lists 24 entries, among them 13
protocol files under `protocols/` (the Qwen capture, precision, holonomy and
controller-task protocols) and the ASMP-9 physical-acquisition registrations.

## Owner decisions not taken here

- Merge or close PR #1; the feature branch is 678+ commits ahead of `main`
  and `main` no longer describes the repository.
- Move the 17 root zip bundles (4.1 MB) to GitHub releases.
- Decide whether `artifacts/` should stay partly tracked against its own
  ignore rule, and whether 76 MB of regenerable JSON receipts belong in git.
- Re-seal or re-register the 32 package-level stale bindings and the 36
  CRLF-sealed ones; the audit report names each pair.
