# ASMP-6 balanced-cover parity theorem v0.2

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

Run:

```powershell
python -m pytest -q ultra-experiments/millennium/asmp6_semantic_collusion_frontier/v0_2_balanced_cover/test_balanced_cover.py
python ultra-experiments/millennium/asmp6_semantic_collusion_frontier/v0_2_balanced_cover/run.py
python ultra-experiments/millennium/asmp6_semantic_collusion_frontier/v0_2_balanced_cover/verify_independent.py
```
