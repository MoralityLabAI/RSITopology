# ASMP-3 independent-noise amplification v1.8

This package computes the exact amplification profile for one registered
semantic atom replicated through conditionally i.i.d. Bernoulli errors with an
adversarial rate `p<=eta`.

Majority with uniform tie breaking is minimax, and

```text
a_H(d) = upper Binomial(d,eta) tail + half the even-depth tie mass,
value  = 1-2a_H(d).
```

The release contrasts this exponential amplification with persistent and
expectation-only noise classes having the same marginal error.

Run:

```powershell
python run_independent_noise_amplification.py
python verify_independent_noise_amplification.py
python build_release_manifest.py
python -m pytest . -q
```

Marginal accuracy alone does not authorize the i.i.d. conclusion.
