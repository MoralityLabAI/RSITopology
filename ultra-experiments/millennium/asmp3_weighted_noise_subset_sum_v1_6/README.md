# ASMP-3 weighted-noise subset-sum boundary v1.6

This package extends the v1.5 adaptive noise game to positive integer
coordinate flip costs.  It proves that the exact value is controlled by whether
a subset sum lies in `[C-B,B]`, builds the pseudo-polynomial controller state
`(truth, round, spent_cost)`, and exposes PARTITION as the general exact
complexity boundary.

The release certifies 2,729 cost/budget cases, 18,436 deterministic verifier
instances, a unit-cost reduction to v1.5, and an exponential distinct-score
noncompression witness.

Run:

```powershell
python run_weighted_noise_subset_sum.py
python verify_weighted_noise_subset_sum.py
python build_release_manifest.py
python -m pytest . -q
```

The result covers hard positive-integer budgets with terminal-only verification,
not stochastic costs, path observations, or the full ASMP-3 characterization.
