# ASMP-4 single-root stop v0.36

This package audits the full ASMP-4 chain after the v0.35 robust atlas.  It
finds one remaining root—formal normative registration or attributable
semantic adjudication—and issues a harness-backed stop on further autonomous
work.

Run:

```powershell
python run_verification.py
python verify_single_root_stop.py
python -m pytest -q test_single_root_stop.py
python -m ruff check .
```

Read `STOP_CERTIFICATE_v0_36.md` for the argument and four reopening
conditions.  This is an operational stop, not a resolution or a universal
impossibility theorem. The complete 37-package chain passes all 404 tests.
