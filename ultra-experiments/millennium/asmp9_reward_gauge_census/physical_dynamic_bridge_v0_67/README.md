# ASMP-9 physical dynamic bridge v0.67

Status: **construction protocol registered prereveal; no model outcomes have
been read**.

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
- [registration decision](REGISTRATION_DECISION_v0_67.md); and
- [resource plan](RESOURCE_PLAN_v0_67.md).

The source freeze is not an environment registration. The construction
registration is created inside the eventual execution environment and binds
its exact model, packages, wrapper, and paths before inference. Confirmation
has a second freeze after construction-only calibration.
