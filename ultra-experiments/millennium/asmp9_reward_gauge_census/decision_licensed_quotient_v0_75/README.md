# ASMP-9 decision-licensed quotient v0.75

This CPU-only development package derives the maximal additive reward gauge
for a finite all-policy-margin target and composes it with physical measurement
nuisance.

```powershell
python -m pytest -q test_decision_licensed_quotient.py
python verify_development.py
```

For policy-occupancy difference matrix `D`:

```text
licensed additive gauge = ker(D);
exact physical access   = A^-1(N + A(ker D)) = ker(D).
```

Failure emits a reward direction that changes a registered policy margin but
is erased by the representative-independent observation.

This closes one finite linear class. It does not validate the policy family,
features, response channel, or moral meaning of cardinal margins, and it does
not resolve ASMP-9.
