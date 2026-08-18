# ASMP-12 v0.2 equilibrium survival surface

This directory contains the preregistered exact CPU experiment crossing nested
program budget with a temptation-payoff parameter. See `RESULT_v0_2.md` for the
completed phase surface and claim boundary.

`PUBLIC_SUMMARY_v0_2.md` is the circulation-facing narrative.
`RESULT_CLARIFICATION_v0_2_1.md` records the exact death partition, margin
complement, and gate/test distinction without changing the canonical result.
`SUBSTACK_DRAFT_v0_1.md` is a general-audience treatment of the same finite
result; the sealed technical artifacts remain authoritative.

Replay:

```powershell
python ultra-experiments/millennium/asmp12_program_equilibrium/v0_2_survival/run_survival.py --registration ultra-experiments/millennium/asmp12_program_equilibrium/v0_2_survival/registration_v0_2.json --output-dir ultra-experiments/millennium/asmp12_program_equilibrium/v0_2_survival/artifacts_v0_2_replay
```

Tests:

```powershell
python -m pytest ultra-experiments/millennium/asmp12_program_equilibrium/v0_2_survival/test_survival.py -q
```
