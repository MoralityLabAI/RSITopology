# ASMP-11 intermediate-width crossover v0.2.1.2 source hardening

This package implements the previously drafted bounds-aware successor to the
sealed v0.2 high-width census. It is CPU-only and deterministic. It never
changes or imports code from the hash-bound v0.2 package.

The claim grid contains every previously unmeasured intermediate width for
`n in {13,15,17}` and `k in {3,4}`. A deterministic covering construction
emits a valid incumbent and exact counting/Schoenheim lower bounds. If the
construction hits its frozen resource stop, the result remains a valid bounds
interval and may remain scientifically unresolved.

## Current status

The working sources are a v0.2.1.2 hardening checkpoint. Do not execute the
claim grid yet. First commit the source checkpoint, then create and separately
commit `registration_v0_2_1_2.json`. Only that committed registration may
authorize a new run in `artifacts_v0_2_1_2/`. The v0.2.1.1 evidence bundle is
immutable and must not be overwritten or relabeled.

## Pre-registration checks

```powershell
python -m pytest -q ultra-experiments/millennium/asmp11_access_ladder/covering_frontier_v0_2_1/test_crossover_frontier.py
python C:/Users/patri/.codex/skills/alife-knowledge-experiments/scripts/validate_manifest.py ultra-experiments/millennium/asmp11_access_ladder/covering_frontier_v0_2_1/experiment_v0_2_1.json --check-paths
```

After committing the source freeze, build and inspect the prospective
registration:

```powershell
python ultra-experiments/millennium/asmp11_access_ladder/covering_frontier_v0_2_1/build_registration.py --source-commit HEAD
```

Commit that registration before running the claim grid.

## Registered execution and independent verification

```powershell
python ultra-experiments/millennium/asmp11_access_ladder/covering_frontier_v0_2_1/run.py `
  --registration ultra-experiments/millennium/asmp11_access_ladder/covering_frontier_v0_2_1/registration_v0_2_1_2.json `
  --output-dir ultra-experiments/millennium/asmp11_access_ladder/covering_frontier_v0_2_1/artifacts_v0_2_1_2

python ultra-experiments/millennium/asmp11_access_ladder/covering_frontier_v0_2_1/verify_result.py `
  --registration ultra-experiments/millennium/asmp11_access_ladder/covering_frontier_v0_2_1/registration_v0_2_1_2.json `
  --artifacts ultra-experiments/millennium/asmp11_access_ladder/covering_frontier_v0_2_1/artifacts_v0_2_1_2

python ultra-experiments/millennium/asmp11_access_ladder/covering_frontier_v0_2_1/synthesize_receipt.py `
  --registration ultra-experiments/millennium/asmp11_access_ladder/covering_frontier_v0_2_1/registration_v0_2_1_2.json `
  --artifacts ultra-experiments/millennium/asmp11_access_ladder/covering_frontier_v0_2_1/artifacts_v0_2_1_2
```

The runner writes separate result, reliability, claim, and operation layers,
raw per-cell JSONL, checkpoints, and a hash receipt. The verifier does not
import the primary covering or probability implementation. It replays exact
Cartesian grids, complete probe records and summaries, operation consistency,
and every receipt link. The synthesis receipt is the authoritative final
five-layer conclusion: it fresh-replays and exact-compares the independent
verification before binding it. Alternative-metric disagreement remains a
non-binding sensitivity result. The receipt reports RAM compliance as
unestablished because peak RAM is not measured.

## Claim boundary

This is a finite covering-design and exact-probability instrument for a
transparent parity oracle. It is not a general group-testing theorem, an
observational minimax result, evidence about neural backdoors, or proof that a
sample crossover dominates after intervention width and harm are priced.
