# ASMP-9 hidden-consideration boundary v0.64

Status: **unregistered development lane; not claim eligible**.

This lane addresses the first post-v0.63 resolution obligation without
pretending the limited-consideration literature is empty.

It records an exact finite access theorem:

1. With unrestricted menu-dependent hidden consideration, every stochastic
   choice kernel is compatible with every latent strict preference.  Random
   assignment of recorded menus or attention prompts does not repair this if
   actual compliance remains unrestricted and unobserved.
2. For an arbitrary finite hidden-compliance correspondence, exact
   identification is equivalent to covering every pair of latent rankings by
   an intervention whose attainable-choice sets are disjoint.
3. If an intervention can force the actual considered set to equal an exact
   pair and the latent preference is deterministic and stable, nonadaptive
   identification over all strict rankings is possible exactly when every
   pair is queried.  The sharp query count is `C(n,2)`.

The negative construction uses singleton consideration.  The middle theorem
is a finite simplex-intersection/separation-cover reduction.  The positive
endpoint is classical comparison-query logic.  The contribution is a
claim-disciplined ASMP-9 access ledger, not new limited-attention theory.

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m pytest `
  ultra-experiments/millennium/asmp9_reward_gauge_census/hidden_consideration_boundary_v0_64/test_hidden_consideration_boundary.py `
  -q -p no:cacheprovider

python `
  ultra-experiments/millennium/asmp9_reward_gauge_census/hidden_consideration_boundary_v0_64/verify_development.py
```

The exact counts and source hashes are recorded in
[`DEVELOPMENT_VERIFICATION_v0_64.json`](DEVELOPMENT_VERIFICATION_v0_64.json).
That receipt is explicitly non-registered and non-claim-eligible.
