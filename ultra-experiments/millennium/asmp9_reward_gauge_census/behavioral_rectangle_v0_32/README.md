# ASMP-9 behavioral rectangle v0.32

Status: development-only, unregistered, and not claim-eligible.

This successor targets the first open item in the v0.31 resolution audit:
behavioral acquisition of the scalar semantic rectangle and its uncertainty
geometry.

The proposed access model uses one common global worst/best lottery. Under a
mixture-affine utility representation, a standard-gamble comparison at
probability `p` reveals the sign of `U(x)-p`. Exact bisection localizes every
rectangle cell. The rectangle cross-difference operator then tests additive
separability while preserving shared cellwise uncertainty as a zonotope.

The development tests are:

```powershell
python -m pytest `
  ultra-experiments/millennium/asmp9_reward_gauge_census/behavioral_rectangle_v0_32/test_behavioral_rectangle.py `
  -q
```

The current ten tests cover:

- exact localization on centered dyadic grids;
- additive and interacting rectangles;
- redundant compound-lottery mixture-affinity checks;
- exact shared-cell support calculation;
- pass/reject/inconclusive semantics;
- ordinal-only and row-local-scale no-go witnesses;
- a missing-cell witness for every rectangle cell; and
- an exact finite majority-vote repeat bound.

Nothing in this directory is frozen. No result should be reported until the
prior-art gate, theorem statement, controls, protocol, and registration have
survived review.
