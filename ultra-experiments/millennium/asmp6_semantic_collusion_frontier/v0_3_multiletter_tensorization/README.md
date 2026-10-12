# ASMP-6 finite multiletter tensorization v0.3

This source-only package prospectively registers a twelve-cell exact comparison
between arbitrary multiletter couplings and a coordinatewise product code under
uniform globally averaged transcript cover.

For block length `n`, the payload has `K=2^n` equiprobable words and the
transcript alphabet has `M=m^n` words. The unrestricted calculation is an exact
finite transportation problem. The product comparator sends one independent
payload bit per coordinate using the v0.2 one-shot law. All probability and
optimization calculations use `fractions.Fraction`; there is no RNG or floating
point.

The directory currently contains no scientific result. Read
`PROTOCOL_v0_3.md` for the frozen semantics and `SOURCE_FREEZE.md` before any
execution.

Source-only validation, which does not execute the registered grid:

```powershell
python C:\Users\patri\.codex\skills\alife-knowledge-experiments\scripts\validate_manifest.py ultra-experiments\millennium\asmp6_semantic_collusion_frontier\v0_3_multiletter_tensorization\manifest_v0_3.json --check-paths
$env:PYTHONDONTWRITEBYTECODE = '1'
python -m pytest -q -p no:cacheprovider ultra-experiments\millennium\asmp6_semantic_collusion_frontier\v0_3_multiletter_tensorization\test_multiletter_tensorization.py
```

Re-run the same source suite after all eight source files are committed; its
real-repository source-binding regression must then pass rather than skip.
After that source commit exists, the later scientific run
is intentionally two-stage and write-once:

```powershell
$SOURCE_COMMIT = git rev-parse HEAD
python -I ultra-experiments\millennium\asmp6_semantic_collusion_frontier\v0_3_multiletter_tensorization\run.py --source-commit $SOURCE_COMMIT
python -I ultra-experiments\millennium\asmp6_semantic_collusion_frontier\v0_3_multiletter_tensorization\verify_independent.py
```

Those two scientific commands are documentation only at source-freeze time.
They must not be run until the source commit exists. Omitting `-I` fails before
argument parsing or any scientific import. Both refuse to overwrite an existing
artifact.
