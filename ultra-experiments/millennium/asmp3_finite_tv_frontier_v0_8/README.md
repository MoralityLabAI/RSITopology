# ASMP-3 finite TV frontier v0.8

This package proves and certifies the exact finite post-transcript frontier for
the typed fixed-interface class:

```text
optimal uniform verifier gap
  = distance_TV(conv(H), conv(F)).
```

It includes exact rational primal/dual certificates, an exhaustive small-LP
vertex solver, parity BSC certificates through depth eight, a convex-hull
collision, a joint-versus-marginal example, benign alias refinements, and a
clean-room checker.

Run:

```powershell
python run_finite_tv_frontier.py
python verify_finite_tv_frontier.py
python build_release_manifest.py
python -m pytest . -q
```

The result is a closed finite `WV-FIX` subtheorem.  It neither changes ASMP-3
v0.1 nor resolves the existential-interface class `WV-ADM`.
