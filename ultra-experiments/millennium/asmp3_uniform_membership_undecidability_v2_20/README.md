# ASMP-3 uniform-membership undecidability v2.20

This package proves that membership in the registered strict fixed-interface
class `WV-FIX-UCOMP` is undecidable for arbitrary computable uniform task-family
generators. The reduction preserves fixed vector messages, one local query,
`BSC(1/5)` noise, efficient honest work, and `polylog(T)` verifier resources.

The result is a candidate parent-level negative resolution only if ASMP-3 v0.1
is taken to include that representation. V0.1 does not freeze the representation
grammar, so the package does not claim unconditional closure or external
acceptance.

Start with:

- `ASMP3_RESEARCH_REPORT_v2_20.md` for the consolidated research summary;
- `UNIFORM_MEMBERSHIP_UNDECIDABILITY_THEOREM_v2_20.md` for the proof;
- `REQUIREMENT_AUDIT_v2_20.md` for the five-item ledger; and
- `RESOLUTION_DISPOSITION_v2_20.md` for the exact stopping rule.

Reproduce:

```powershell
python run_uniform_membership_undecidability.py
python verify_uniform_membership_undecidability.py
python -m pytest . -q
python build_release_manifest.py
```
