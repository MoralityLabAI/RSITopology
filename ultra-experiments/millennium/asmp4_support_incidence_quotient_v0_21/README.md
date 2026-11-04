# ASMP-4 support-incidence quotient v0.21

This package implements the quotient-first resume route from v0.20. It removes
duplicate raw labels with identical finite event-support incidence, proves the
exact invariances and semantic rate formula, and reclassifies the complete
memoryless census.

Run the central harness:

```powershell
python run_verification.py
```

Run the import-independent verifier:

```powershell
python verify_support_incidence_quotient.py
```

Run focused tests:

```powershell
python -m pytest -q test_support_incidence_quotient.py
```

The exact contract and frozen claim are
`support_incidence_quotient_contract_v0_21.json` and
`support_incidence_quotient_claim_v0_21.json`.

The v0.22 successor allows causal belief-aware encoding rather than preserving
exact support incidence. It proves the stronger optimized local collapse while
leaving this exact-support quotient unchanged for its declared semantics.
