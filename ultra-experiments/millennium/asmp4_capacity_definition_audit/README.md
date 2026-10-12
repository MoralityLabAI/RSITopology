# ASMP-4 capacity-definition audit

This development harness asks whether the exact finite
`asmp4_two_port_game` result can be interpreted as a finite instance of the
canonical achieved-transcript capacity region `R_K`.

It does not dispute the internal exactness of the frozen v0.1 solver. It checks
three properties forced by the canonical definition:

1. `R_K` is upward closed because its rates are upper budgets.
2. For a deterministic controller that receives only the read transcript, the
   write transcript is its causal image, so `|M_w(T)| <= |M_r(T)|`.
3. At a finite horizon, either a singleton read-transcript set or a singleton
   write-transcript set leaves only plant-independent open-loop control, when
   actuator authority and decoder memory are held fixed.

Run the tests and print the full audit:

```powershell
python -m pytest test_capacity_definition_audit.py -q
python audit.py
```

The audit is intentionally separate from the preregistered v0.1 result. Its
status is a definition-repair stop, not a retrospective invalidation of the
finite memoryless phase map.
