# ASMP-2 external review packet

## Requested adjudication

Reviewers should independently answer four questions.

1. **Correctness:** Is the safety-deficiency reduction exactly equivalent to
   the canonical ASMP-2 certification event, including policy randomization,
   global safety, and utility?
2. **Boundary:** Do the source-fiber primal/dual theorem, approximate
   total-variation lower bound, and smooth opposite-action witness establish a
   sharp no-free-lunch boundary?
3. **Local clause:** Does the deterministic-policy QMD example validly refute
   factorization-only local sufficiency, or was robust feasibility/policy
   mixing already implicit in v0.1?
4. **Resolution status:** Should the classical Blackwell/Le Cam
   decision-specific deficiency reduction count as ASMP-2's requested
   coordinate-invariant characterization, or is the candidate statement
   under-specified because it requires an unstated structural closed form?

## Reading order

1. [`CANDIDATE_RESOLUTION_v0_6.md`](CANDIDATE_RESOLUTION_v0_6.md)
2. [`THEOREM_v0_2.md`](THEOREM_v0_2.md)
3. [`DECISION_DEFICIENCY_REDUCTION_v0_3.md`](DECISION_DEFICIENCY_REDUCTION_v0_3.md)
4. [`FINITE_DEFICIENCY_LP_v0_7.md`](FINITE_DEFICIENCY_LP_v0_7.md)
5. [`APPROXIMATE_DEFICIENCY_v0_8.md`](APPROXIMATE_DEFICIENCY_v0_8.md)
6. [`LOCAL_SUFFICIENCY_COUNTEREXAMPLE_v0_5.md`](LOCAL_SUFFICIENCY_COUNTEREXAMPLE_v0_5.md)
7. [`LIPSCHITZ_CONTINUATION_v0_4.md`](LIPSCHITZ_CONTINUATION_v0_4.md)
8. [`PRIOR_ART_v0_2.md`](PRIOR_ART_v0_2.md)
9. [`EVIDENCE_LEDGER_v0_6.md`](EVIDENCE_LEDGER_v0_6.md)

## Independent reproduction

Run each historical suite in its own directory because the older harnesses use
colliding top-level module names.

```powershell
cd ultra-experiments/millennium/asmp2_crossed_shift
python -m pytest test_crossed_shift.py -q

cd ../asmp2_active_design_census
python -m pytest test_active_design.py test_active_design_v0_2_1.py `
  test_active_design_v0_2_2.py -q

cd ../asmp2_source_fiber_boundary_v0_2
python -m pytest test_source_fiber.py test_decision_deficiency.py `
  test_fiber_lp.py test_finite_deficiency_lp.py `
  test_lipschitz_continuation.py test_local_counterexample.py -q

python run.py --output artifacts/result_v0_2.json
python verify_result.py --result artifacts/result_v0_2.json `
  --output artifacts/verification_v0_2.json

python run_deficiency.py --output artifacts/deficiency_result_v0_3.json
python verify_deficiency.py --result artifacts/deficiency_result_v0_3.json `
  --output artifacts/deficiency_verification_v0_3.json
```

Expected results:

- historical crossed-shift suite: `7 passed`;
- historical active-design suite: `14 passed`;
- new theorem suite: `30 passed`;
- source-fiber verifier: `13/13`;
- finite-sample deficiency verifier: `6/6`.

## Required independence

At least one team should avoid the supplied vertex-enumeration implementation
and instead use an independent LP package or hand duality proof. At least one
team should independently reconstruct the QMD scores, Fisher information,
curvature bound, and globally good action sets.

Reviewers should not treat matching JSON hashes as mathematical replication.
They should record:

- theorem/counterexample verdict;
- prior-art/subsumption verdict;
- whether the v0.1 resolution rule is met;
- implementation and environment;
- independent artifact hashes; and
- any changed assumption they believe is necessary.

## Acceptance outcomes

- **`resolved_negative_subsumed_or_false`**: the local iff is false as written
  and/or the complete certification boundary is already decision-specific
  deficiency, so ASMP-2 v0.1 should be retired.
- **`unresolved_refreeze_required`**: deficiency is deemed tautological and
  v0.1 must freeze a structural class and acceptance form before a solution can
  be judged.
- **`candidate_refuted`**: a reviewer supplies a concrete mathematical error
  in the theorem, witness, or reduction.

No other outcome should silently redefine the target after reviewing the
results.
