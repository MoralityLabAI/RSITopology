# Reviewer packet v0.29

## Claim under review

For a length-preserving causal port-tree morphism, the target worst-path
branching cost is at most the source cost plus the logarithm of the maximum
product of local successor fibers. Its normalized limsup is the directional
rate correction.

## Fast audit path

1. Read `causal_branch_fiber_contract_v0_29.json`.
2. Check the degree-grouping proof and disclosure map in `THEOREM.md`.
3. Run `python run_verification.py`.
4. Run `python verify_causal_branch_fiber.py`.
5. Run `python -m pytest -q test_causal_branch_fiber.py`.
6. Inspect `PRIOR_ART_BOUNDARY_v0_29.md` before assessing novelty.

## Load-bearing falsifications

- Replace local fibers with terminal fibers: the disclosure block fails.
- Use state-class size: repeated histories fail.
- Replace maximum local fiber by minimum: the concentrated map fails.
- Require bounded rather than subexponential products: sparse merging fails.
- Replace limsup by liminf: the burst schedule fails.
- Infer equality from one direction or share one profile across ports: the
  asymmetric repeated blocks fail.

No transfer theorem for sequential prefix-free rounding is claimed.
