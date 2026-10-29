# ASMP-9 sharp atom modulus v0.47

Successor to the v0.46 coupled shared-channel audit.

The core instrument converts uniform confidence coverage at one observed
sample atom into a mandatory parameter region, then propagates that region
through the exact downstream decision risk.  On a finite parameter grid, a
spike confidence construction attains the same region, so the reported
modulus is simultaneously a lower and upper bound.

Run the dedicated tests:

```powershell
python -m pytest -q `
  ultra-experiments/millennium/asmp9_reward_gauge_census/sharp_atom_modulus_v0_47/test_sharp_atom_modulus.py
```

The coarse and targeted development runs are permanently disclosed as burned
work. The prospective confirmation uses a disjoint `N=72` budget and fixed
designs under `PROTOCOL_v0_47.md`.

Run the burned six-level development census:

```powershell
python `
  ultra-experiments/millennium/asmp9_reward_gauge_census/sharp_atom_modulus_v0_47/run_development_v0_47.py `
  --workers 4 --total-budget 66
```

`DEVELOPMENT_RESULT_v0_47.json`, when present, is explicitly
non-claim-eligible and may only inform a disjoint registration.

After the coarse-grid stop, run the targeted boundary-resolution check:

```powershell
python `
  ultra-experiments/millennium/asmp9_reward_gauge_census/sharp_atom_modulus_v0_47/run_targeted_development_v0_47.py `
  --workers 4
```

After the registration exists, execute and independently replay the
confirmation:

```powershell
python `
  ultra-experiments/millennium/asmp9_reward_gauge_census/sharp_atom_modulus_v0_47/run_confirmation_v0_47.py

python `
  ultra-experiments/millennium/asmp9_reward_gauge_census/sharp_atom_modulus_v0_47/verify_result_v0_47.py
```
