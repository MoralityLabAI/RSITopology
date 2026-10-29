# Reviewer packet v0.27

## Claim under review

For public-history safety games related by exact-safety epsilon-cost
alternating bisimulation, every horizon-`T` achievable budget transfers with
coordinate slack `T epsilon`, and every asymptotic worst-path limsup budget
transfers with slack `epsilon`. A strict Lipschitz safety margin is sufficient
for the exact Boolean premise; metric closeness without it is insufficient.

## Fast audit path

1. Read `approximate_bisimulation_contract_v0_27.json`.
2. Check both representative-history directions in `THEOREM.md`.
3. Run `python run_verification.py`.
4. Run `python verify_approximate_bisimulation_robustness.py`.
5. Run `python -m pytest -q test_approximate_bisimulation_robustness.py`.
6. Inspect `PRIOR_ART_BOUNDARY_v0_27.md` before assessing novelty.

## Load-bearing checks

- Delete one backward successor match: the relation must fail.
- Change state or transition safety: the relation must fail.
- Exceed the registered per-edge epsilon: the relation must fail.
- Drop one registered action type: the relation must fail.
- Claim vanishing asymptotic error: the sharp loop must refute it.
- Claim metric-only zero-error transfer: the safe/boundary loops must refute it.

The package does not promote the theorem to nonadditive costs or assert that a
finite approximate quotient exists for the canonical nonlinear problem.
