# ASMP-9 finite-sample tier boundary development v0.58

This unregistered successor asks what finite samples can certify after v0.57
has supplied a structural completion class and a constructive full-kernel
reconstruction map.

The candidate result has two parts:

1. **No uniform exact-tier theorem.** Even with every menu available, a Luce
   kernel can be arbitrarily close in experiment law to a non-Luce RUM kernel.
   A second explicit family puts non-Luce RUM and non-RUM kernels arbitrarily
   close. No finite sampling budget uniformly classifies the exact three tiers.
2. **Margin-promised positive theorem.** If the true kernel is separated by a
   declared distance `gamma` from the tier boundaries, then empirical
   low-menu probabilities, v0.57 Mobius reconstruction, and distances to the
   Luce closure and RUM polytope yield an explicit finite-sample certificate.
3. **Matching margin exponent on one slice.** An explicit margin-promised
   RUM/non-RUM pair requires `Omega(gamma^-2)` adaptive queries, matching the
   positive theorem's separation-margin exponent at `n=3,r=1`.

The upper bound exposes the v0.57 interpolation condition number rather than
hiding it inside big-O notation.

See `DEVELOPMENT_RESULT_v0_58.md` for the current verdict, exact paths,
verification counts, and representative sample costs.

Development commands:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
python -m pytest -p no:cacheprovider `
  ultra-experiments/millennium/asmp9_reward_gauge_census/finite_sample_tiers_v0_58/test_finite_sample_tiers.py `
  -q

python ultra-experiments/millennium/asmp9_reward_gauge_census/finite_sample_tiers_v0_58/verify_development.py
```

Nothing in this directory is registered or claim eligible.
