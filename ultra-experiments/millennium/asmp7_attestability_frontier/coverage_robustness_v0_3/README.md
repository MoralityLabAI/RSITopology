# ASMP-7 meter-coverage robustness v0.3

This additive successor tests the trusted-meter coverage assumption left open
by the ASMP-7 v0.1 and v0.2.1 instruments. It compares an execution-independent
fresh per-challenge coverage events with an exact-size coverage mask chosen to
suppress evidence and then held fixed across challenges.

An execution-fixed *random* independent mask is a distinct, out-of-scope
counterfactual because repeated reports then follow a mixture of binomials. See
the protocol for the recorded fixed-mask sensitivity.

The implementation is CPU-only and uses exact integer binomial masses plus
`fractions.Fraction`. The independent verifier repeats the model and test from
scratch and does not import `coverage_robustness.py`.

Run the focused suite:

```powershell
python -m pytest ultra-experiments/millennium/asmp7_attestability_frontier/coverage_robustness_v0_3/test_coverage_robustness.py -q
```

After a source checkpoint, write a result into a new output directory:

```powershell
python ultra-experiments/millennium/asmp7_attestability_frontier/coverage_robustness_v0_3/run.py `
  --output-dir ultra-experiments/millennium/asmp7_attestability_frontier/coverage_robustness_v0_3/artifacts_v0_3

python ultra-experiments/millennium/asmp7_attestability_frontier/coverage_robustness_v0_3/verify_result.py `
  --artifact-dir ultra-experiments/millennium/asmp7_attestability_frontier/coverage_robustness_v0_3/artifacts_v0_3
```

The run receipt hashes the executable registration, result, and exact source
set. Verification reconstructs the complete payload and writes both
`verification.json` and `bundle_receipt.json`; the latter additionally binds
the verification bytes.

Result, reliability, claim support, and operational decision are separate
fields. Even a passing finite claim authorizes no deployment threshold.
