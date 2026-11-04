# ASMP-12 inertial selector v0.4

Source-only successor to the committed ASMP-12 v0.3.1 constructible-survival
evidence. It freezes one deterministic alternating inertial best-response rule,
complete augmented-state graphs, and an exact fair-two-schedule distribution.

Before the source commit, run only:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m pytest -q -p no:cacheprovider test_inertial_selector.py
python -m ruff check --no-cache .
python C:\Users\patri\.codex\skills\alife-knowledge-experiments\scripts\validate_manifest.py manifest_v0_4.json --check-paths
```

The tests deliberately avoid `compile_result` and the complete registered
24-trajectory grid. After the exact eight files are committed and the
postcommit source-binding test passes, a separately authorized task may run:

```powershell
python -I run.py --source-commit <40-hex-source-commit>
python -I verify_independent.py
```

Artifacts are write-once in sibling `artifacts_v0_4_inertial_selector/`.
Existing evidence is never overwritten. See `PROTOCOL_v0_4.md` for the dynamic
and `SOURCE_FREEZE.md` for the non-aliasing sequence.
