# ASMP-7 boundary degradation v0.2.1

This version repairs only v0.2's exact-integer decimal serialization stop.

After registration:

```powershell
python -m pytest ultra-experiments/millennium/asmp7_attestability_frontier/test_boundary_frontier.py ultra-experiments/millennium/asmp7_attestability_frontier/test_boundary_serialization_v0_2_1.py -q
python ultra-experiments/millennium/asmp7_attestability_frontier/run_boundary_frontier_v0_2_1.py --registration ultra-experiments/millennium/asmp7_attestability_frontier/registration_v0_2_1.json --output-dir ultra-experiments/millennium/asmp7_attestability_frontier/artifacts_v0_2_1
```

