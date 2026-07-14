# Edit sectioning

Edit sectioning replaces one globally signed VPD coordinate with one transported coordinate per certified flat patch. It consumes the existing lineage and holonomy receipts; it does not add an invariant level.

## Outputs

`section_edits()` admits a plaquette only when it is measured, orientation-preserving, within the requested holonomy budget, and every boundary edge passes the frozen lineage thresholds. Admitted plaquettes are partitioned into maximal four-neighbor components. Each patch records its deterministic spanning-tree paths, transported coordinate at every node, edge margins, worst registered elementary-loop identity-loss bound, and required `holonomy_clean` authorization.

`persistence_curve()` sweeps the budget and emits edit count plus component birth, merge, and death receipts. `rank_audit_placements()` ranks unmeasured loops using their interval-implied classification uncertainty and the number of current patch boundaries they could resolve.

The worst-case patch bound covers registered elementary plaquettes only. It does not certify arbitrary composite or unmeasured loops.

## Consumers

- `vpd_edit_program` executes the returned per-patch plan instead of assuming one global signed coordinate.
- `hrmmmm_control_harness` uses the audit ranking and calls `authorize_patch()`, which delegates every patch node to the existing `AnchorRegistry.certify(..., requested_use="disparate_weight_edit")` gate.

## Commands

```powershell
python scripts/run_edit_sectioning_control.py --protocol protocols/edit_sectioning_synthetic_v0_2.json --output artifacts/edit_sectioning_v0_2
python scripts/edit_sectioning.py --input artifacts/edit_sectioning_v0_2/mixed_curvature_input.json --budget 0.05 --persistence-budgets 0 0.005 0.012 0.02 0.05 0.1 0.202 0.25 --output run/edit_sectioning
```

The canonical CPU fixture passes the matched-rank/norm utility gates, refuses the uniformly curved negative control, and is stable inside the registered estimation-noise patch-count band. These are instrument tests, not transformer evidence.
