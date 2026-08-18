# ASMP-9 finite cactus design v0.19

This additive successor targets the exact finite-budget subclass left open by
the v0.18 cyclic-core bond theorem.

Current status: development-only. No v0.19 scientific cell has been
registered or run.

The candidate theorem is:

```text
cactus residual liveness
  = series product of edge-disjoint cycle events
  = exact integer allocation over per-cycle totals.
```

Counts balance inside each cycle, but the cycle-total response is not
discretely concave. The exact optimizer is therefore a Bellman dynamic
program, not the usual marginal-gain greedy rule.

Development tests:

```powershell
python -m pytest -q `
  ultra-experiments/millennium/asmp9_reward_gauge_census/finite_cactus_design_v0_19/test_finite_cactus_design.py
```

The claim boundary is in `THEORY_DRAFT_v0_19.md`. Burned parameter cells are
listed in `DEVELOPMENT_NOTE_v0_19.md`.
