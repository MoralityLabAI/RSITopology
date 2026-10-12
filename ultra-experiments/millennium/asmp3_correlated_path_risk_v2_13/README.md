# ASMP-3 correlated path risk v2.13

This package resolves the correlated-noise block in the repaired online ASMP-3
theorem.  The extractor needs a bound on total error probability along the
actually selected adaptive path; it does not need independent errors.

It certifies persistent common-mode, per-matching-prefix conditional, and
exchangeable latent-rate controllers.  It also gives an exact counterfamily
showing why fixed-class marginals alone are insufficient when noise may
correlate with the verifier's public selection seed.

Run:

```powershell
python run_correlated_path_risk.py
python verify_correlated_path_risk.py
python build_release_manifest.py
python -m pytest . -q
```

See `CORRELATED_PATH_RISK_THEOREM_v2_13.md` for the proof and
`COMPLETION_AUDIT_v2_13.md` for the evidence boundary.
