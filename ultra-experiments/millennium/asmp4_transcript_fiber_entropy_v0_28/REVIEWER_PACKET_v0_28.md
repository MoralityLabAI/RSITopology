# Reviewer packet v0.28

## Claim under review

For realized safe port languages connected by a port-compatible causal factor,
the target log-cardinality exceeds the source by at most the logarithm of the
maximum transcript fiber. The normalized limsup is the directional rate slack;
subexponential fibers in both directions preserve the complete region.

## Fast audit path

1. Read `transcript_fiber_contract_v0_28.json`.
2. Check the fiber partition proof in `THEOREM.md`.
3. Run `python run_verification.py`.
4. Run `python verify_transcript_fiber_entropy.py`.
5. Run `python -m pytest -q test_transcript_fiber_entropy.py`.
6. Inspect `PRIOR_ART_BOUNDARY_v0_28.md` before assessing novelty.

## Load-bearing falsifications

- Replace history-fiber growth by state-class size: the finite clone fails.
- Infer equal tree entropy from exact path bisimulation: the clone fails.
- Require uniformly bounded fibers: sparse dyadic branching refutes necessity.
- Replace maximum fiber by minimum fiber: the concentrated fixture fails.
- Replace limsup by liminf: the burst schedule fails.
- Use one directional factor for equality: the section/factor pair fails.
- Use one scalar modulus for both ports: the asymmetric clone fails.

No claim is made for tree costs lacking a registered causal-factor distortion
law.
