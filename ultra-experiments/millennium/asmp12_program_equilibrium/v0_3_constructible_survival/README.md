# ASMP-12 constructible cooperative-survival correspondence v0.3

This additive successor turns v0.2's finite survival surface into an explicitly
typed graph correspondence. It builds all 24,576 profitable-deviation cell
graphs, verifies budget inclusions, uses adjacent graph unions for temptation
zigzags, and records cooperative sink events separately with exact margins and
profitable-edge witnesses.

The v0.3.1 integrity repair adds an exact machine registry, independent
Cartesian and adjacency reconstruction, full event and relation replay, and a
source-bound root-of-roots receipt. The mathematical surface is unchanged; the
earlier compact v0.3 artifacts are superseded because their verifier was
cardinality-bound and signature-only.

Run the scoped tests:

```powershell
python -m pytest ultra-experiments/millennium/asmp12_program_equilibrium/v0_3_constructible_survival/test_constructible_survival.py -q
```

Build the deterministic four-layer report without writing an artifact:

```powershell
python ultra-experiments/millennium/asmp12_program_equilibrium/v0_3_constructible_survival/run_constructible_survival.py
```

After committing a source checkpoint, write a non-aliasing evidence bundle:

```powershell
python ultra-experiments/millennium/asmp12_program_equilibrium/v0_3_constructible_survival/build_artifacts.py --source-commit <full-commit-sha> --output-dir ultra-experiments/millennium/asmp12_program_equilibrium/v0_3_constructible_survival/artifacts_v0_3_1
```

See `PROTOCOL_v0_3.md` and `protocol_v0_3_1.json` for the finite object and
gates, and `CLAIM_BOUNDARY_v0_3.md` for the inference limits. In particular,
this work does not treat equilibrium sets as an ordinary bifiltration.
