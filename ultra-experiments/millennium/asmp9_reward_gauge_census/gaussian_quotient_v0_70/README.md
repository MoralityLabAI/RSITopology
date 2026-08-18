# ASMP-9 Gaussian quotient v0.70

This development package gives the exact stochastic-complexity specialization
of v0.69 for independent Gaussian scalar queries.

```powershell
python -m pytest -q test_gaussian_quotient.py
python verify_development.py
```

The central formulas are:

```text
M(n) = sum_i (n_i/sigma_i^2) b_i b_i^T

minimax quotient MSE = trace(M(n)^-1)
policy-margin MSE    = c^T M(n)^-1 c.
```

Singular `M` is an exact nonidentification result. The package is
development-only, uses classical Gaussian linear-model and optimal-design
theory, and does not resolve ASMP-9.
