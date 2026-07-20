# ASMP-12 v0.2 equilibrium survival surface

This directory contains the preregistered exact CPU experiment crossing nested
program budget with a temptation-payoff parameter. See `RESULT_v0_2.md` for the
completed phase surface and claim boundary.

Replay:

```powershell
python ultra-experiments/millennium/asmp12_program_equilibrium/v0_2_survival/run_survival.py --registration ultra-experiments/millennium/asmp12_program_equilibrium/v0_2_survival/registration_v0_2.json --output-dir ultra-experiments/millennium/asmp12_program_equilibrium/v0_2_survival/artifacts_v0_2_replay
```

Tests:

```powershell
python -m pytest ultra-experiments/millennium/asmp12_program_equilibrium/v0_2_survival/test_survival.py -q
```
