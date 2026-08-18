# ASMP-7 finite transformation-closed attestation frontier

This directory contains a CPU-only, exact-rational instrument seed for
ASMP-7. It compares a trace-only telemetry experiment with an explicitly
charged randomized-response challenge channel over a finite Boolean execution
and representation registry.

The statistical results are classical. See `PRIOR_ART_v0_1.md` and the frozen
claim boundary in `PROTOCOL_v0_1.md`.

After `registration_v0_1.json` exists, run:

```powershell
python -m pytest ultra-experiments/millennium/asmp7_attestability_frontier/test_attestability.py -q
python ultra-experiments/millennium/asmp7_attestability_frontier/run_frontier.py
```

Outputs are written to `artifacts_v0_1/`. The runner validates every sealed
source hash before computing outcomes and refuses to overwrite an existing
result unless `--force` is supplied for an explicit replay.

