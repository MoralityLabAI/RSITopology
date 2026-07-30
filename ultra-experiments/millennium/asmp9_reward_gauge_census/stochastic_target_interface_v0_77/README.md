# ASMP-9 finite stochastic target interface v0.77

This CPU-only package extends v0.76 from deterministic observation labels to
known finite iid laws.

```powershell
python -m pytest -q test_stochastic_target.py
python verify_development.py
```

It provides:

- exact population target/leakage classification;
- a Hellinger-affinity maximum-likelihood union bound;
- an exact rational binary Bayes calibration; and
- a per-sample TV misspecification stress bound.

On the frozen `(0.9,0.1)` versus `(0.1,0.9)` fixture, the generic 5% bound
needs six samples while exact Bayes error needs three. A 0.1% per-sample TV
stress removes the generic six-sample certificate under the worst-case bound.

This is classical finite hypothesis testing, not behavioral validation or an
ASMP-9 resolution.
