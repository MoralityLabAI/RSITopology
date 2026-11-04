# ASMP-9 path factorization test v0.72

This development package adds a known-variance Gaussian liveness and sample
test to the exact v0.71 path-factorization theorem.

```powershell
python -m pytest -q test_path_factorization_test.py
python verify_development.py
```

On the frozen reconvergent fixture:

```text
rank(X)=3, residual df=1,
distance^2=1/4,
minimum repeats/path at alpha=.05 and power=.80 = 32.
```

Deleting one path leaves reward identification intact but reduces residual
degrees of freedom to zero, making factorization empirically untestable.

The result is classical Gaussian lack-of-fit theory, not physical value
validation or ASMP-9 resolution.
