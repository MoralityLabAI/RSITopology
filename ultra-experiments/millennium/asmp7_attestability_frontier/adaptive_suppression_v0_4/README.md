# ASMP-7 causal adaptive suppression v0.4

This source-only package prospectively registers an exact finite theorem and
verification suite for nonanticipating history-dependent coverage masks. It
binds the complete committed v0.3 selective-suppression evidence and the v0.1
parent instrument, but it contains no new scientific result.

The suppressor knows the fixed execution and may use past challenges, reports,
masks, and private randomness. It must choose the exact-size current mask
before the iid-uniform current challenge, which remains conditionally
independent of the complete frozen filtration and all suppressor-private
coins. The monitor receives only report
bits. The primary theorem covers arbitrary rational coordinatewise-monotone
terminal functions on full report histories for deterministic finite horizons
through 8192; registered exact sample minima are the count-upper-tail
corollary.

Read `PROTOCOL_v0_4.md` and `SOURCE_FREEZE.md` before any execution.

Source-only validation does not execute the registered 48-row scientific grid
or the 11,520-comparison generic-terminal action grid:

```powershell
python C:\Users\patri\.codex\skills\alife-knowledge-experiments\scripts\validate_manifest.py ultra-experiments\millennium\asmp7_attestability_frontier\adaptive_suppression_v0_4\manifest_v0_4.json --check-paths
$env:PYTHONDONTWRITEBYTECODE = '1'
python -m pytest -q -p no:cacheprovider ultra-experiments\millennium\asmp7_attestability_frontier\adaptive_suppression_v0_4\test_adaptive_suppression.py
python -m ruff check --no-cache ultra-experiments\millennium\asmp7_attestability_frontier\adaptive_suppression_v0_4
```

After the exact eight-file source set is committed, rerun the source tests so
the real-Git binding test passes instead of skipping. Only a later authorized
task may execute the two write-once scientific stages:

```powershell
$SOURCE_COMMIT = git rev-parse HEAD
python -I ultra-experiments\millennium\asmp7_attestability_frontier\adaptive_suppression_v0_4\run.py --source-commit $SOURCE_COMMIT
python -I ultra-experiments\millennium\asmp7_attestability_frontier\adaptive_suppression_v0_4\verify_independent.py
```

Omitting `-I` fails before local imports. Existing artifacts are preserved;
neither entrypoint overwrites evidence.
