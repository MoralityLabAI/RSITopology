# Sequential risk access v0.41

This additive ASMP-9 development extends the v0.40 finite risk-polytope object
from static query subsets to adaptive finite-horizon query policies.

The exact recursion generates the upper risk polytope of all policy trees.
The burned control uses four targets and three deterministic queries. Its
pre-run development prediction assigned the two-query nonadaptive arm
deficiency `1/2`. Exact execution corrected that value because the open-loop
class permits randomization across fixed query sequences:

```text
adaptive horizon 2      -> exact identification
nonadaptive horizon 2   -> deficiency 1/4
nonadaptive horizon 3   -> exact identification
```

No deterministic two-query sequence identifies all targets. The lower
`1/4` risk is achieved only by convexifying those imperfect open-loop plans.
The failed `1/2` development prediction remains in
`DEVELOPMENT_PROTOCOL_v0_41.json`; it is not rewritten as a preregistered
success.

This directory is currently `burned_development_not_registered`. Its output
may shape a disjoint confirmation protocol but is not claim-eligible evidence.

Run:

```powershell
python -m pytest -q ultra-experiments/millennium/asmp9_reward_gauge_census/sequential_risk_access_v0_41
python ultra-experiments/millennium/asmp9_reward_gauge_census/sequential_risk_access_v0_41/run_burned_development.py
```
