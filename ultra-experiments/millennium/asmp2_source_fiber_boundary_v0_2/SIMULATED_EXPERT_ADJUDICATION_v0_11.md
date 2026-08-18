# ASMP-2 simulated Ultra adjudication

## Non-external status

Two Ultra-reasoning agents were assigned disjoint adversarial mandates. Team A
reconstructed the decision-theoretic reduction and finite LPs; Team B
reconstructed the smooth QMD, continuation, active-design, and local
counterexample arguments.

These are simulations, not independent human teams. They increase internal
confidence and expose defects, but they do **not** satisfy the external-review
gate in `external_review_checklist_v0_9.json`:

```text
minimum_independent_teams = 2
current_team_receipts = []
completion_gate_satisfied = false
```

## Convergent findings

Both reviews support the core no-free-lunch mathematics:

- Team A independently reformulated the programs in SciPy/HiGHS and reproduced
  primal-dual equality across 438 finite source-fiber cases and 81 finite noisy
  experiments, with maximum numerical gaps near machine precision.
- Team B independently recovered equality of the source laws and scores,
  Fisher information `3/32`, curvature bound `193/36`, opposite singleton good
  sets, and the exact all-sample minimax value `1/2`.
- Both accepted the deterministic local example as a refutation of a literal
  factorization-only sufficiency clause, while emphasizing that randomized
  deployment policies change that example.
- Both judged the Lipschitz envelope theorem to be a valid positive result for
  its frozen product class.

## Defects found by the simulations

The reviews found three concrete mathematical statement repairs and one scope
fork:

1. The arbitrary-space deficiency “iff” needs attainment (or a strict
   inequality/closure convention). Team A supplied a countable standard-Borel
   example where the infimum failure is `1/2` but no rule attains it.
2. Dense-source sufficiency requires every admissible continuation to be
   continuous; saying that the class merely *contains* all continuous families
   is insufficient.
3. The randomized finite-query packing corollary needs a domain with
   arbitrarily large finite packings of disjoint bump regions.
4. The canonical statement does not settle whether an exact variational
   deficiency value counts as its requested structural characterization, and
   it leaves action randomization, robust margin, sample allocation, and
   adaptive-design costs under-bound.

The first three statement-level repairs were applied to the packet after the
simulated reviews and before commit. The scope fork cannot be repaired without
an authoritative successor statement.

## Joint verdict

The strongest defensible conclusion is:

```text
unresolved_refreeze_required
```

The exact finite theorems and QMD counterexample are credible after independent
simulated reconstruction. They establish a sharp obstruction cell and a
convincing reason to stop pursuing a blanket resolution under the present
wording. They do not justify marking ASMP-2 resolved: the candidate needs the
specified theorem-statement repairs, an authoritative scope refreeze, and—if
the frozen prize-style acceptance rule remains in force—two genuine external
expert-team receipts.

## Repository evidence at adjudication

- scoped readiness and source-fiber suites: `35 passed`;
- historical crossed-shift suite: `7 passed`;
- historical active-design suite: `14 passed`;
- readiness verifier: `12/12`;
- source-fiber verifier: `13/13`; and
- finite-sample deficiency verifier: `6/6`.

The detailed simulated reports are
`SIMULATED_EXPERT_REVIEW_A_v0_11.md` and
`SIMULATED_EXPERT_REVIEW_B_v0_11.md`.
