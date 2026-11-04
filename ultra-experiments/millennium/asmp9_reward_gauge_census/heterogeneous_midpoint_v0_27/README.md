# ASMP-9 heterogeneous-midpoint boundary v0.27

This development branch asks which response-link heterogeneity survives the
v0.26 additive-offset access channel.

The candidate theorem separates three cases:

```text
arbitrary link shape + shared zero midpoint
  -> utility threshold remains identifiable;

arbitrary cell-specific midpoint
  -> utility is completely confounded;

context-only midpoint
  -> bipartite synchronization, one gauge per component,
     and cycle-rank liveness.
```

The implementation is CPU-only. It is development evidence until a later
registration seals fresh graph and threshold cells.

```powershell
python -m pytest `
  ultra-experiments/millennium/asmp9_reward_gauge_census/heterogeneous_midpoint_v0_27 `
  -q
```

