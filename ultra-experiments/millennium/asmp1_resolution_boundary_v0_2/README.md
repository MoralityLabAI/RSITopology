# ASMP-1 representation-sensitive resolution boundary

This directory replaces the failed structural Cut-Separation Conjecture with:

- a universal observation-fiber factorization criterion;
- a decidable rational semialgebraic lane;
- a uniform undecidability theorem for arbitrary computable-real analytic
  encodings without a certified gap; and
- a complete rank/recovery/stability/lower-bound theorem for linear analytic
  mechanisms with a declared translation gauge.

Read in this order:

1. [THEOREM_v0_2.md](THEOREM_v0_2.md)
2. [RESULT_v0_2.md](RESULT_v0_2.md)
3. [RESOLUTION_AUDIT_v0_2.md](RESOLUTION_AUDIT_v0_2.md)
4. [PRIOR_ART_v0_2.md](PRIOR_ART_v0_2.md)

Run:

```powershell
$env:PYTHONPATH = "ultra-experiments\millennium\asmp1_resolution_boundary_v0_2"
python -m pytest `
  ultra-experiments/millennium/asmp1_resolution_boundary_v0_2/test_identifiability_boundary.py `
  -q
python ultra-experiments/millennium/asmp1_resolution_boundary_v0_2/identifiability_boundary.py `
  --max-quotient-dimension 3 `
  --max-rows 3 `
  --output ultra-experiments/millennium/asmp1_resolution_boundary_v0_2/artifacts/result_v0_2.json
python ultra-experiments/millennium/asmp1_resolution_boundary_v0_2/verify_result.py `
  --output ultra-experiments/millennium/asmp1_resolution_boundary_v0_2/artifacts/verify_v0_2.json
```

The exact census contains 21,300 design matrices. It constructs a rational
left inverse for every identifying design and a rational nullspace collision
for every non-identifying design.
