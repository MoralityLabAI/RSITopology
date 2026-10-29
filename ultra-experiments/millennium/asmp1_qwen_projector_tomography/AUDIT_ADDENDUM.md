# Reproducibility addendum for v0.1

This addendum does not alter the frozen protocol, registration, gates, analysis, or result receipt. It records two clarifications surfaced by independent review after result commit `b712b75`.

## Exact test invocation

The previously reported “14 relevant tests” came from this literal command:

```powershell
python -m pytest tests/test_projector_tomography.py tests/test_v03_lineage_bifiltration.py tests/test_attestation.py -q
```

Observed result on 2026-07-19: `14 passed in 4.16s`, exit code 0. The dedicated projector-tomography file itself contains three tests. The other eleven are lineage/bifiltration and attestation regression tests selected because the experiment consumes those contracts. Future machine-readable receipts must store the literal invocation and collection result rather than only a count.

## S0 interpretation limit

The frozen S0 gate validly failed, but its degree-two-or-higher *fraction* is scale-confounded: the selected and random arms had materially different total causal response scales. Therefore v0.1 supports “the preregistered specificity gate failed,” but does not by itself establish that nonlinear energy is intrinsically less geometry-specific than random.

The v0.2 draft fixes this prospectively with a calibration/confirmation split, a magnitude-matched random alpha, absolute higher-order energy, and an 8-of-9 fold-sign gate. No v0.1 threshold or verdict is changed.
