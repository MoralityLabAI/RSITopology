# ASMP-5A finite bounded-tiling seed

This CPU-exact theorem-generator enumerates full binary certificate trees over
up to twelve independent safety obligations. It separates total proof work,
critical-path depth, and Horton-Strahler evaluation memory.

Before registration run only:

```powershell
python -m pytest -q ultra-experiments/millennium/asmp5a_bounded_tiling/test_bounded_tiling.py
```

The claim census must not run until `registration_v0_1.json` is committed.

After registration:

```powershell
python ultra-experiments/millennium/asmp5a_bounded_tiling/run.py
python ultra-experiments/millennium/asmp5a_bounded_tiling/verify_result.py `
  --result ultra-experiments/millennium/asmp5a_bounded_tiling/artifacts_v0_1/result_v0_1.json `
  --receipt ultra-experiments/millennium/asmp5a_bounded_tiling/artifacts_v0_1/receipt_v0_1.json `
  --output ultra-experiments/millennium/asmp5a_bounded_tiling/artifacts_v0_1/verification_v0_1.json
```
