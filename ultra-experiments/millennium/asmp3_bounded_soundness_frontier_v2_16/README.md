# ASMP-3 bounded-soundness frontier v2.16

This package extends the v2.15 arbitrary-round public-coin unique-marker
frontier to zero-world soundness `s<1`.  The exact worst-marker completeness is
`s+(1-s)min(1,Kq/N)`, with exact gap `(1-s)min(1,Kq/N)`.

Run:

```powershell
python run_bounded_soundness_frontier.py
python verify_bounded_soundness_frontier.py
python build_release_manifest.py
python -m pytest . -q
```

See `BOUNDED_SOUNDNESS_THEOREM_v2_16.md` for the proof and
`COMPLETION_AUDIT_v2_16.md` for the evidence boundary.
