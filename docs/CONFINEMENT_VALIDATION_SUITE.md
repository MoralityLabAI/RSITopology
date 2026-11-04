# Confinement-width validation suite

The six CPU-only entry points implement the registered plan in
[`IMPLEMENTATION_PLAN.md`](../IMPLEMENTATION_PLAN.md). They use finite symbols,
immutable work-unit receipts, deterministic `SeedSequence` derivation, and
one BLAS thread per process.

Run tests and smoke configurations from the repository root:

```powershell
python -m pytest -q
powershell -ExecutionPolicy Bypass -File scripts/run_confinement_smoke.ps1
```

Run one bounded pilot explicitly:

```powershell
python experiments/01_split_rate.py --config configs/pilot/01_split_rate.yaml --workers 4
```

Full configurations are specifications only. In particular, the dense
three-spin configuration through `N=400` is CPU-cluster work and must not be
launched as part of tests, smoke runs, or packaging.

Every run writes:

```text
artifacts/confinement/<experiment>/<run_id>/
  config.json
  environment.json
  work_units/*.json
  aggregate.csv
  aggregate.json
  metrics.json
  figure.png
  REPORT.md
  checksums.json
  run_receipt.json
```

Work-unit filenames are implementation-specific so receipts from changed code
cannot be reused. Their NumPy seeds are derived separately from the frozen
experiment, mathematical cell, and root seed; non-scientific renderer or
serialization changes therefore cannot resample an experiment.

The three linear evidence labels must not be collapsed:

- `universal_volume_lower_bound` is a certified obstruction under the frozen
  channel and geometry assumptions;
- `aligned_box_cover` is an explicit constructive controller;
- `lower_construction_gap` is unresolved, not a failure or success.

The transversal experiment is a PBH/observability estimator, the sufficiency
experiment is Monte Carlo with an analytic random-probe baseline, and the
spin-glass experiment remains basin-weighted finite-`N` evidence.
