# Identity attestation integration

This layer gives three existing consumers one identity contract. It introduces no invariant above engineering evidence, lineage, or holonomy.

## Named consumers

- `hrmmmm_control_harness`: attach `AnchorRecord.site_id` to each monitor and reward feature. Before applying a reward or action, call `registry.certify(site_id, requested_use=...)`. Signed monitor outputs and signed interventions are denied unless `authorized` is true at `holonomy_clean`; bundle-energy rewards require `lineage_certified`. A lower certificate can still be logged as engineering evidence.
- `vpd_edit_program`: attach the registered site to every intervention and matched-random candidate. Seal identity strata with `seal_vpd_identity_strata.py` before generating or reading outcomes. Protocol v0.2 keeps two estimands separate: attribution direction versus random direction at one site, and attribution-selected site versus a matched random site under a fixed direction policy. The analysis refuses cross-estimand and cross-stratum pooling.
- `blue_beam`: load `bluebeam_proposals.jsonl` as risky proposals. After the run, produce one detection row per `tamper_id`. The scorer calls every missing or negative result a `demonstrated_blind_spot`.

Every anchor carries a reference-basis hash, current-basis hash, selected band, the unique spanning-tree path from reference to site, receipts for its edges, a holonomy budget, loop receipts, and an aggregate `det_h_flag`. Path hashes must form a continuous chain. Band failover breaks lineage certification. Any orientation-reversing loop or exceeded holonomy margin blocks signed use.

## Commands

```powershell
python scripts/identity_attestation.py build --records anchors/site_a.json anchors/site_b.json --output run/anchor_registry.json
python scripts/identity_attestation.py certify --registry run/anchor_registry.json --site layer.12.mlp --use disparate_weight_edit
python scripts/generate_bluebeam_tampers.py --output run/bluebeam_tampers
python scripts/score_bluebeam_tampers.py --detections run/bluebeam_detections.jsonl --output run/bluebeam_score.json
python scripts/seal_vpd_identity_strata.py --features run/vpd_features_v02.jsonl --registry run/anchor_registry.json --protocol protocols/vpd_identity_stratification_v0_2.json --output run/vpd_sealed
python scripts/analyze_vpd_identity_strata.py --sealed run/vpd_sealed/sealed_identity_strata.jsonl --registration run/vpd_sealed/stratification_registration.json --outcomes run/vpd_outcomes.jsonl --output run/vpd_analysis.json
```

The registry and prereveal outputs use compare-or-fail writes. Preserve them with the run. Outcome tables are never part of the sealed feature artifact.
