# ASMP-4 causal branch-fiber transfer v0.29

This package gives the quotient distortion law for the v0.3 worst-path causal
branching metric. Under a length-preserving causal prefix morphism, multiply
the maximum local successor fibers along each target path. The target branch
cost exceeds the source by at most the logarithm of the largest such product.
Its normalized limsup is the directional branch-rate slack.

Terminal language fibers are insufficient. A three-step causal map is
bijective on complete transcripts but has branch costs three and two with
local successor-fiber product two. Repeating the block gives an exact one-third
bit-per-step gap despite terminal fiber one.

Run the central harness:

```powershell
python run_verification.py
```

Run the import-independent verifier:

```powershell
python verify_causal_branch_fiber.py
```

Run focused tests:

```powershell
python -m pytest -q test_causal_branch_fiber.py
```

The frozen registration and claim are `causal_branch_fiber_contract_v0_29.json`
and `causal_branch_fiber_claim_v0_29.json`.
