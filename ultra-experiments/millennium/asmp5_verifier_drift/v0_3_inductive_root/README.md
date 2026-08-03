# ASMP-5 inductive rooted-verifier certificate v0.3

This package closes one explicitly bounded seam in the v0.2 verifier-drift
instrument.  The v0.2 census checked the rooted positive control through depth
eight.  Version 0.3 proves, for the same checker grammar, that the rooted rule
is safe at every finite depth and admits an arbitrarily long safe execution.

It also gives a width- and horizon-independent two-step unsafe witness for the
matched unrooted rules whenever checker drift of Hamming radius at least one is
allowed.  The result is about this transparent four-bit checker model; it is
not a reflective-safety theorem for learned or open-ended verifiers.

Run:

```powershell
python -m pytest -q ultra-experiments/millennium/asmp5_verifier_drift/v0_3_inductive_root/test_inductive_root.py
python ultra-experiments/millennium/asmp5_verifier_drift/v0_3_inductive_root/run.py
python ultra-experiments/millennium/asmp5_verifier_drift/v0_3_inductive_root/verify_independent.py
```

The runner is a deterministic theorem compiler.  The independent verifier
does not import it and replays the registered finite grid by explicit graph
search.
