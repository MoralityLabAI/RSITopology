# ASMP-5 dynamic replicated noisy anchor v0.4

This source-only package prospectively registers a 54-row exact experiment on
replicated one-sided errors in the four-bit v0.3 anchor. It contains no v0.4
result or verification artifact. Read `PROTOCOL_v0_4.md` and
`SOURCE_FREEZE.md` before execution.

Source-only checks (which do not call the registered compiler) are:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
python -B -m pytest -q -p no:cacheprovider ultra-experiments/millennium/asmp5_verifier_drift/v0_4_dynamic_noisy_anchor/test_noisy_anchor.py
```

After exactly the eight files are committed and only under separate
authorization, the write-once stages are:

```powershell
$SOURCE_COMMIT = git rev-parse HEAD
python -I ultra-experiments/millennium/asmp5_verifier_drift/v0_4_dynamic_noisy_anchor/run.py --source-commit $SOURCE_COMMIT
python -I ultra-experiments/millennium/asmp5_verifier_drift/v0_4_dynamic_noisy_anchor/verify_independent.py
```

Both commands fail without isolated safe-path mode, reject a dirty or
non-exact source snapshot, and never overwrite evidence.
