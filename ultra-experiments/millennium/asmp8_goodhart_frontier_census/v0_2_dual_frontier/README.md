# ASMP-8 v0.2 dual-norm robust frontier

This CPU-exact successor asks what replaces scalar KL after v0.1 rejected it
as an optimizer-independent Goodhart-pressure coordinate. It tests the sharp
robust pair:

```text
(proxy gain, dual-norm policy movement).
```

The mathematical identity is classical norm duality. The experiment's role is
instrumental: exhaustive finite validation, attaining witnesses, coordinate
minimality, a sharp near-tie control, and a rare-tail control.

The run is not evidence about learned reward models or RL training.

## Workflow

```powershell
python -m pytest -q ultra-experiments/millennium/asmp8_goodhart_frontier_census/v0_2_dual_frontier
python ultra-experiments/millennium/asmp8_goodhart_frontier_census/v0_2_dual_frontier/run.py
python ultra-experiments/millennium/asmp8_goodhart_frontier_census/v0_2_dual_frontier/verify_result.py
```

The runner refuses to execute before a committed `registration_v0_2.json`
matches every sealed source.

