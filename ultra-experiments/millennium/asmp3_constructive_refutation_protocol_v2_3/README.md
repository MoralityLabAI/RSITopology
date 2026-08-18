# ASMP-3 constructive refutation protocol v2.3

This package gives a constructive positive weak-verification theorem under four
typed contracts: small quotient witnesses, a uniform efficient honest finder,
sound-complete `Refute`, and fresh independent replication blocks after the
transcript/witness is selected.

```text
completeness >= 1-delta,
soundness    <= delta,
gap          >= 1-2delta,
queries       = r*d.
```

Run:

```powershell
python run_constructive_refutation_protocol.py
python verify_constructive_refutation_protocol.py
python build_release_manifest.py
python -m pytest . -q
```

The theorem is conditional and sufficient; it is not a converse or a complete
`WV-FIX`/`WV-ADM` characterization.
