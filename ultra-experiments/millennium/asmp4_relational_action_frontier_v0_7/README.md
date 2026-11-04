# ASMP-4 relational-action frontier v0.7

This package closes the nonunique-safe-action seam left by the v0.6
registration fork.  It proves an exact nonrectangular two-port rate region for
a four-mode relational controller, even when the registered sensor partition
is selected from arbitrary public read history.  It also proves that zero-error
randomized observation kernels derandomize without increasing either support
language.

The mathematical result is in [THEOREM.md](THEOREM.md), the compact conclusion
is in [RESULT.md](RESULT.md), and the canonical disposition is in
[STOPPING_ARGUMENT_v0_7.md](STOPPING_ARGUMENT_v0_7.md).

Run the central verifier:

~~~powershell
python run_verification.py
~~~

Run the import-independent verifier:

~~~powershell
python verify_relational_frontier.py
~~~

Run focused tests:

~~~powershell
python -m pytest -q test_relational_frontier.py
~~~

The frozen claim is [relational_claim_v0_7.json](relational_claim_v0_7.json).
No generated output is required for verification.

The integrated predecessor-to-v0.7 chain contains 98 tests. This package
passes ten central and ten import-independent verification gates.

The [v0.8 stochastic-quantifier successor](../asmp4_randomness_quantifier_boundary_v0_8/RESULT.md)
separates per-disturbance almost-sure safety from this package's
support-zero-error convention on an uncountable disturbance domain.
