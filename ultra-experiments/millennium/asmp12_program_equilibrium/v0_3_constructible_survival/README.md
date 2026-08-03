# ASMP-12 constructible cooperative-survival correspondence v0.3

This additive successor turns v0.2's finite survival surface into an explicitly
typed graph correspondence. It builds all 24,576 profitable-deviation cell
graphs, verifies budget inclusions, uses adjacent graph unions for temptation
zigzags, and records cooperative sink events separately with exact margins and
profitable-edge witnesses.

Run the scoped tests:

```powershell
python -m pytest ultra-experiments/millennium/asmp12_program_equilibrium/v0_3_constructible_survival/test_constructible_survival.py -q
```

Build the deterministic four-layer report without writing an artifact:

```powershell
python ultra-experiments/millennium/asmp12_program_equilibrium/v0_3_constructible_survival/run_constructible_survival.py
```

See `PROTOCOL_v0_3.md` for the finite object and gates and
`CLAIM_BOUNDARY_v0_3.md` for the inference limits. In particular, this work
does not treat equilibrium sets as an ordinary bifiltration.
