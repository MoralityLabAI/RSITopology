# ASMP-11 covering-mediated finite-sample frontier

This successor converts parent-fixing detection into a classical covering-
design problem and attaches exact rational finite-sample power.

Before registration, only run the tests or smoke cells outside the claim grid:

```powershell
python -m pytest -q ultra-experiments/millennium/asmp11_access_ladder/covering_frontier_v0_2/test_covering_frontier.py
```

After the prospective registration commit, run:

```powershell
python ultra-experiments/millennium/asmp11_access_ladder/covering_frontier_v0_2/run.py
python ultra-experiments/millennium/asmp11_access_ladder/covering_frontier_v0_2/verify_result.py
```

Outputs are write-once under `artifacts_v0_2/`.
