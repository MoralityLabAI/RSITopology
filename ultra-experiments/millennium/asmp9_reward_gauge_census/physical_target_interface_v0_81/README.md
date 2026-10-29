# ASMP-9 structured physical target interface v0.81

Status: **prereveal successor; no v0.81 outcomes read**.

Version v0.80 showed that an armwise average-of-inverse-logits decoder could
recover every target sign but missed its frozen cardinal-error threshold at
512 samples per query. Version v0.81 keeps the model, target semantics,
contexts, arms, sample count, and all scientific thresholds fixed. It changes
only the prospectively declared decoder:

- the three target-decoder arms have known offsets `{-2, 0, +2}` from one
  context-local base margin;
- one joint likelihood estimates that base margin;
- shaping representatives are reserved for the leakage gate and cannot add
  information to the target decoder; and
- the misspecification penalty counts every sample actually consumed by the
  joint decoder.

The experiment is CPU-only and uses fresh deterministic seeds. It is a
controlled acquisition test, not evidence about human or model values.

Prereveal sequence:

```powershell
python -m pytest -q test_structured_target.py
python register_v0_81.py
git add .
git commit -m "Register ASMP-9 structured target decoder v0.81"
git push
```

Only after the registration commit is public may `execute_registered.py` be
run against a fresh output directory.

