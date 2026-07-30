# ASMP-9 fiber-group correction v0.74

This CPU-only development package corrects the “maximal invariance group”
language in the ASMP-9 draft.

```powershell
python -m pytest -q test_fiber_group.py
python verify_development.py
```

The central rule is:

```text
observations determine a fiber partition;
the decision problem independently licenses a gauge orbit partition;
exact quotient identification means those partitions are equal.
```

The full permutation group inside observation fibers always exists and is
usually scientifically meaningless. Minimum exact access in a finite
deterministic registry is the corresponding non-gauge-pair set-cover problem.

This is unregistered classical development, not behavioral validation or an
ASMP-9 resolution.
