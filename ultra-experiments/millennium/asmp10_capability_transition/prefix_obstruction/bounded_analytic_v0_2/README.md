# ASMP-10 bounded analytic continuation slice v0.2

This additive successor quantifies the first invisible Hermite direction after
v0.1. It freezes the physical-coordinate monomial basis, an exact coefficient
L1 budget, exact shared prefix jets, and five linear future-score probes.

The primary solver discovers the codimension-one kernel by exact row
reduction. The independent verifier reconstructs the product witness, checks a
square Hermite determinant, and supplies an L-infinity dual certificate. Both
paths use rational arithmetic.

Run the scoped tests from this directory or the repository root:

```powershell
python -m pytest ultra-experiments/millennium/asmp10_capability_transition/prefix_obstruction/bounded_analytic_v0_2/test_bounded_analytic.py -q
```

Build the deterministic report without writing an artifact:

```powershell
python ultra-experiments/millennium/asmp10_capability_transition/prefix_obstruction/bounded_analytic_v0_2/run_bounded_analytic.py
```

See `PROTOCOL_v0_2.md` for the frozen theorem, census, and gates, and
`CLAIM_BOUNDARY_v0_2.md` for the deliberately narrow inference scope. This
directory does not authorize or modify the separate GPU training branch.
