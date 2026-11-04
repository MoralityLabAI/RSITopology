# ASMP-4 approximate-bisimulation robustness v0.27

This package quantifies the v0.26 quotient bridge. Exact state and transition
safety, registered actions, alternating successor back-and-forth, and per-edge
two-port cost error at most `epsilon` imply finite-horizon budget slack at most
`T epsilon` and asymptotic rate-region Hausdorff slack at most `epsilon`.

Metric closeness alone cannot preserve zero-error feasibility. The package
constructs arbitrarily close safe/unsafe self-loop games whose regions are
nonempty and empty, and proves that a strict `L delta` signed safety margin is
sufficient and sharp.

Run the central harness:

```powershell
python run_verification.py
```

Run the import-independent verifier:

```powershell
python verify_approximate_bisimulation_robustness.py
```

Run focused tests:

```powershell
python -m pytest -q test_approximate_bisimulation_robustness.py
```

The exact registration and frozen claim are
`approximate_bisimulation_contract_v0_27.json` and
`approximate_bisimulation_claim_v0_27.json`. The classical boundary is recorded
in `PRIOR_ART_BOUNDARY_v0_27.md`.

V0.28 handles a distinct nonadditive cost: log-cardinality of the entire
realized port language. Its correction is not the edgewise `epsilon` here but
the normalized logarithm of the maximum causal transcript fiber.
