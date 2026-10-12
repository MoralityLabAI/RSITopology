# ASMP-3 noise-symmetry quotient v1.5

This package compresses the v1.4 truth-aware adaptive Hamming-budget game by
all coordinate permutations.  Orbit averaging proves that an optimal verifier
depends only on terminal Hamming weight, while the noise controller needs only
`(truth, round, flips_used)`.

It certifies all 560 pairs with `1<=d<=32`, proves the same exact value phase,
and witnesses the replacement of `2^32` response words by 33 terminal weights
when `d=b=32`.

Run:

```powershell
python run_noise_symmetry_quotient.py
python verify_noise_symmetry_quotient.py
python build_release_manifest.py
python -m pytest . -q
```

The quotient requires coordinate-permutation invariance.  It does not cover
position-dependent observations, costs, payoffs, or noise constraints.
