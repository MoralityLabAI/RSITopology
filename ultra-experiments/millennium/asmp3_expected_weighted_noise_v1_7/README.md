# ASMP-3 expected weighted-noise v1.7

This package replaces the v1.6 hard weighted flip budget with a separate
expected-cost bound under each truth.  It proves the exact total-variation
saddle

```text
value = max(0, 1-2B/C),  C=sum_i c_i,
```

using a normalized-score verifier and matching all-zero/all-one noise mixtures.
The result shows exactly how expectation convexification removes the parent
subset-sum obstruction.

Run:

```powershell
python run_expected_weighted_noise.py
python verify_expected_weighted_noise.py
python build_release_manifest.py
python -m pytest . -q
```

The theorem does not apply to hard, tail-risk, coupled-prior, path-dependent,
or truth-ignorant noise constraints.
