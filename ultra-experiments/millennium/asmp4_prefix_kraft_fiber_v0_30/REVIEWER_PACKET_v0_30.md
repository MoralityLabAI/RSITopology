# Reviewer packet v0.30

## Claim under review

For the registered sequential minimax binary prefix cost and any
length-preserving causal tree factor,

`P_target(T) <= P_source(T) + max_path sum_t ceil(log2 m(p_t))`.

Bidirectional sublinear rounded profiles preserve the complete prefix-cost
region, conditional on the corresponding safe strategy transfers.

## Fast audit path

1. Read `THEOREM.md`, especially the backward Kraft induction in section 3.
2. Check the ternary boundary carefully: a final ceiling first becomes strict
   at `T >= 3`, not at `T=2`.
3. Run `python run_verification.py` for the central ten-gate report.
4. Run `python verify_prefix_kraft_fiber.py` for the import-independent
   implementation.
5. Run `python -m pytest -q` and `python -m ruff check .`.

## Strongest falsification targets

- Find a causal morphism violating the rounded bound. The central census
  exhausts 332,928 binary cases through depth three; the independent census
  checks all 4,096 binary labelings of a full depth-two ternary tree.
- Replace the per-prefix ceilings by `log2` or one final ceiling. The explicit
  ternary trees reject both replacements from depth three.
- Replace the local maximum by a minimum, terminal fiber, or state-class
  count. Concentrated and disclosure examples reject these substitutions.
- Replace asymptotic `limsup` by `liminf`, or require bounded corrections.
  Burst/rest and dyadic-sparse profiles reject these substitutions.

## Integrity anchors

The harness seals the problem statement, the v0.3 registered cost claim, and
the v0.29 local branch-fiber claim. The contract and claim JSON files are
compared to literal expected payloads by the central implementation. The
independent verifier parses its own imports to reject dependency on the
central module.

## Scope warning

This packet verifies a deterministic causal cost-transfer theorem. It does not
verify safe quotient existence for arbitrary nonlinear plants, stochastic or
average-length coding, or multidimensional adversarial mean-payoff synthesis.
