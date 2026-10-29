# ASMP-9 discounted shaping quotient v0.6

Unregistered theorem development for the discounted-shaping obligation.

The ordinary graph cycle space is replaced by the left nullspace of:

```text
(D_gamma Phi)(u->v)=gamma Phi(v)-Phi(u).
```

The quotient dimension depends on balanced components of the resulting gain
graph, and finite trajectory comparisons are invariant only when their
discounted boundary signatures match.

Run:

```powershell
python -m pytest -q `
  ultra-experiments/millennium/asmp9_reward_gauge_census/discounted_shaping_v0_6
```

No claim is prospective until a later protocol is frozen and registered.
