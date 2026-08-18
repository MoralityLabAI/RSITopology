# ASMP-6 balanced-cover parity theorem v0.2.1 verification repair

The v0.1 four-symbol census showed that exact message-averaged covertness can
hide a perfectly reliable bit while exact per-message covertness cannot.  This
CPU-exact successor determines when that separation persists as the size of a
uniform opaque-symbol alphabet changes.

For two equiprobable messages and an `m`-symbol uniform benign cover, perfect
one-shot decoding under exact message-averaged covertness is possible exactly
when `m` is even.  For odd `m`, the sharp Bayes error is `1/(2m)`.  Under exact
per-message covertness the error is always `1/2`.

The package contains no language, codebook, learned encoder, shared key, or
adaptive history.  It is a transparent extremal probability calculation, not
an operational collusion policy.

The primary artifact is intentionally pre-verification: even when all primary
gates pass, its measurement status and operation remain
`awaiting_independent_verification`.  The import-independent verifier
recomputes all cells `m=2..31` and alone advances the verified conclusion.  A
final receipt then binds that conclusion to an exact source commit and hashes
of the protocol, primary result, and verification artifact.  During synthesis,
the independent verifier is rerun and its fresh canonical output must exactly
match the stored verification artifact.

Run the focused tests, then checkpoint the listed source and documentation
files before producing artifacts.  The receipt generator rejects an
uncommitted or mismatched source tree:

```powershell
python -m pytest -q ultra-experiments/millennium/asmp6_semantic_collusion_frontier/v0_2_balanced_cover/test_balanced_cover.py
$SOURCE_COMMIT = git rev-parse HEAD
python ultra-experiments/millennium/asmp6_semantic_collusion_frontier/v0_2_balanced_cover/run.py
python ultra-experiments/millennium/asmp6_semantic_collusion_frontier/v0_2_balanced_cover/verify_independent.py
python ultra-experiments/millennium/asmp6_semantic_collusion_frontier/v0_2_balanced_cover/synthesize_receipt.py --source-commit $SOURCE_COMMIT
```

`$SOURCE_COMMIT` must be the 40-character commit containing the exact current
bytes of `balanced_cover.py`, `run.py`, `verify_independent.py`,
`synthesize_receipt.py`, `test_balanced_cover.py`, `protocol_v0_2.json`,
`PROTOCOL_v0_2.md`, and this README.  Commit the generated artifacts only after
the final receipt passes.
