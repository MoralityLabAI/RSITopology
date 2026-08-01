# ASMP-3 witness-transparent normal form v2.5

This package proves a protocol-to-finder extraction theorem for
witness-transparent, ideal-simulable protocols. It exhaustively audits the
coupling loss, composes the extracted randomized finder with v2.4, and certifies
that a nonbinding `Refute` breaks the literal v0.1 characterization's necessity
direction while v0.7 already breaks sufficiency.

Run from this directory:

```powershell
python run_witness_transparent_normal_form.py
python verify_witness_transparent_normal_form.py
python build_release_manifest.py
python -m pytest . -q
```

The package closes a normal form for a declared operational subclass and a
two-sided separation of the literal displayed iff. It does not claim a complete
characterization of unrestricted `WV-FIX` or `WV-ADM`.
