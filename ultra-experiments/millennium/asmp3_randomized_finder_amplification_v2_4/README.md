# ASMP-3 randomized finder amplification v2.4

This package broadens the v2.3 constructive protocol from an always-successful
finder to an independently retryable Las Vegas-with-FAIL finder. It certifies
the exact finder/noise gap, charges every retry, confirms an inverse-logarithmic
success scaling lane, and shows that retries do not bypass the v2.1
unique-marker search obstruction.

Run from this directory:

```powershell
python run_randomized_finder_amplification.py
python verify_randomized_finder_amplification.py
python build_release_manifest.py
python -m pytest . -q
```

The result remains conditional on the randomized finder and fresh-noise
contracts. It is progress toward, not a substitute for, the universal ASMP-3
normal-form/converse characterization.
