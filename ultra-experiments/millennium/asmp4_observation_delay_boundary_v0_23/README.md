# ASMP-4 observation-delay boundary v0.23

This package locates the sharp timing boundary left open by v0.22. For the
registered collar plant, same-step sensing is feasible, every positive integer
observation delay is impossible under arbitrary current disturbances, a
charged current-mode preview restores the same-step region, and a charged seed
for a constant mode gives a lower-rate predictable regime.

Run the central harness:

```powershell
python run_verification.py
```

Run the import-independent verifier:

```powershell
python verify_observation_delay_boundary.py
```

Run focused tests:

```powershell
python -m pytest -q test_observation_delay_boundary.py
```

The exact timing registration and frozen claim are
`observation_delay_contract_v0_23.json` and
`observation_delay_boundary_claim_v0_23.json`.

`GLOBAL_STOPPING_DISPOSITION_v0_23.md` maps the complete local evidence chain
to the five canonical resolution requirements and states the exact conditions
under which global ASMP-4 work should resume.

The v0.24 successor takes one permitted resume route: it freezes a parameterized
architecture grammar and proves a support-functional variational theorem for
reset-concatenable registrations. Its periodic block-completeness condition
keeps the remaining nonresetting global boundary explicit.
