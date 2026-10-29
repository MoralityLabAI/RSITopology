# ASMP-3 interactive covering frontier v2.15

This package extends the v2.2 unique-marker `Kq>=N` frontier to arbitrary-round
public-coin interaction with adaptive ideal semantic queries and bounded
completeness.  Under pointwise perfect zero-world soundness, the exact
worst-marker value is `min(1,Kq/N)`.

Run:

```powershell
python run_interactive_covering_frontier.py
python verify_interactive_covering_frontier.py
python build_release_manifest.py
python -m pytest . -q
```

See `INTERACTIVE_COVERING_THEOREM_v2_15.md` for the proof and
`COMPLETION_AUDIT_v2_15.md` for the evidence boundary.
