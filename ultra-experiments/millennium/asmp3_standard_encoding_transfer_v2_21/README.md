# ASMP-3 standard-encoding and quantifier transfer v2.21

This package lifts the v2.20 `NONHALT` construction to the full membership set
under every adequate standard effective encoding. It also proves that the
inactive zero-gap coupling survives arbitrary semantic-respecting interface
selection, covering both `FIX` and `ADM` modes.

Read:

- `ASMP3_RESEARCH_REPORT_v2_21.md` for the consolidated status;
- `STANDARD_ENCODING_AND_QUANTIFIER_TRANSFER_THEOREM_v2_21.md` for the proof;
- `CANONICAL_ADMISSIBILITY_AUDIT_v2_21.md` for the source-field map; and
- `PARENT_RESOLUTION_DISPOSITION_v2_21.md` for the exact claim and stop rule.

Reproduce:

```powershell
python run_standard_encoding_transfer.py
python verify_standard_encoding_transfer.py
python -m pytest . -q
python build_release_manifest.py
```
