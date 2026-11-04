# ASMP-9 physical dynamic bridge v0.67

Status: **construction completed; instrument gates failed; confirmation
closed**.

This additive lane carries the exact v0.66 dynamic-response distinction into a
small real-model experiment. It keeps four questions separate:

1. does substantive context move an expressed forced choice beyond a bare
   recommendation-label control;
2. does a frozen washout instruction return that choice inside a
   construction-derived envelope;
3. can repeated context create a strict choice reversal; and
4. does a coarse construction response transducer replay exactly on untouched
   scenario families?

The model-facing runner and pure analysis contract can be checked now:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m pytest `
  ultra-experiments/millennium/asmp9_reward_gauge_census/physical_dynamic_bridge_v0_67/test_bridge_core.py `
  -q -p no:cacheprovider
```

See:

- [registered protocol narrative](PROTOCOL_v0_67.md);
- [machine-readable protocol](protocol_v0_67.json);
- [paired scenario manifest](scenario_manifest_v0_67.json);
- [pure prompt/analysis implementation](bridge_core.py);
- [prior-art gate](PRIOR_ART_GATE_v0_67.md);
- [registration decision](REGISTRATION_DECISION_v0_67.md);
- [resource plan](RESOURCE_PLAN_v0_67.md);
- [resource-only amendment v0.67.1](RESOURCE_AMENDMENT_v0_67_1.md);
- [construction result v0.67.1](CONSTRUCTION_RESULT_v0_67_1.md); and
- [compact construction receipts](artifacts/construction_v0_67_1).

The source freeze is not an environment registration. The construction
registration was created inside the execution environment and bound its exact
model, packages, wrapper, and paths before inference. The construction
instrument preconditions failed, so the second confirmation freeze was not
opened.
