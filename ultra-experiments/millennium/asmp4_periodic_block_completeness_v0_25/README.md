# ASMP-4 periodic block completeness v0.25

This package proves the exact finite-public-scheduler boundary left by v0.24.
Within each reachable cyclic strongly connected component, the rate region is
the upward cycle-mean polytope and periodic closed walks are complete. Across
irreversible recurrent components, the full region is a union of such
polytopes and one global support family can add false convex combinations.

Run the central harness:

```powershell
python run_verification.py
```

Run the import-independent verifier:

```powershell
python verify_periodic_block_completeness.py
```

Run focused tests:

```powershell
python -m pytest -q test_periodic_block_completeness.py
```

The exact registration and frozen claim are `finite_scheduler_contract_v0_25.json`
and `periodic_block_claim_v0_25.json`.

`PRIOR_ART_BOUNDARY_v0_25.md` credits the classical minimum-cycle-mean and
finite-type rotation-set results and limits the repository contribution to the
two-port mapping and SCC-disjunction diagnosis.

V0.26 supplies a sufficient bridge into this theorem: an exact costed
alternating bisimulation preserves the full safety-budget region, so a
deterministic finite quotient may use the component-indexed cycle formula.
