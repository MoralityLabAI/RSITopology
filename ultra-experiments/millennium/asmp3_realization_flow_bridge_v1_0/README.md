# ASMP-3 realization-flow bridge v1.0

This package derives the rational terminal-law polytope required by v0.9 from a
frozen finite acyclic controlled stochastic graph.

It proves exact policy/occupancy-flow equivalence, keeps terminal laws as a
compact extended formulation, certifies a `2^k` pure-policy family with `2k`
flow variables, and checks an adaptive multi-stage graph.

Run:

```powershell
python run_realization_flow_bridge.py
python verify_realization_flow_bridge.py
python build_release_manifest.py
python -m pytest . -q
```

Scope is limited to one fully observed strategic controller.  Multi-role games
remain a separate sequence-form target.
