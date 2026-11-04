# ASMP-5 v0.4 source freeze

Status: `source_candidate_not_executed_requires_commit_before_run`.

Exactly these eight regular, non-reparse files form the atomic source set:

1. `PROTOCOL_v0_4.md`
2. `README.md`
3. `SOURCE_FREEZE.md`
4. `manifest_v0_4.json`
5. `noisy_anchor.py`
6. `run.py`
7. `test_noisy_anchor.py`
8. `verify_independent.py`

No registered 54-row grid or scientific artifact may be produced before this
exact set is reviewed and committed. Source-only tests may exercise off-grid
formula, enumerator, recurrence, binding-mutation, write-once, and isolated
entrypoint-help fixtures, but must not call `compile_result`, execute either
entrypoint past argument help, or invoke the full registry iterator.

The predecessor is commit
`61a2f802adb4c4b5f06272d97d9de888413d5352`; its three evidence artifacts,
protocol, and three executable sources are bound by the SHA-256 values in the
manifest. A future source commit must contain byte-identical copies of exactly
these eight files and descend from that predecessor.

Authorized artifacts belong only in sibling directory
`artifacts_v0_4_dynamic_noisy_anchor`. The runner exclusively creates
`result_v0_4.json`; the verifier exclusively creates `verification_v0_4.json`.
Existing evidence is preserved. Both entrypoints require `python -I`, reject
extra live entries including caches and links, and bind the committed snapshot
before scientific work.
