# ASMP-5 verifier-drift census v0.2 repair

This additive successor preserves the v0.1 scientific universe while removing
the implementation bottleneck that caused `unavailable_resource_cap`.

Before registration, only run:

```powershell
python -m pytest -q ultra-experiments/millennium/asmp5_verifier_drift/v0_2_repair/test_verifier_drift_v0_2.py
```

Do not run the registered census until `registration_v0_2.json` exists in a
committed tree. Outputs are write-once under `artifacts_v0_2/`.

After registration:

```powershell
python ultra-experiments/millennium/asmp5_verifier_drift/v0_2_repair/run_v0_2.py
python ultra-experiments/millennium/asmp5_verifier_drift/v0_2_repair/verify_v0_2.py `
  --result ultra-experiments/millennium/asmp5_verifier_drift/v0_2_repair/artifacts_v0_2/result_v0_2.json `
  --receipt ultra-experiments/millennium/asmp5_verifier_drift/v0_2_repair/artifacts_v0_2/receipt_v0_2.json `
  --output ultra-experiments/millennium/asmp5_verifier_drift/v0_2_repair/artifacts_v0_2/verification_v0_2.json
```
