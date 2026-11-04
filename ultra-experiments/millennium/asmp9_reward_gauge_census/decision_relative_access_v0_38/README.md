# ASMP-9 decision-relative access v0.38

## Current status

`finite_decision_relative_access_threshold_established`

Version v0.37 separated zero-error nuisance components, quantitative target
risk, and full expanded-parameter deficiency. This successor implements the
missing middle object: exact deficiency relative to a frozen target-only
policy-decision type after a declared nuisance marginalization.

Start with:

- [`RESULT_v0_38.md`](RESULT_v0_38.md) for the prospectively registered
  six-cell result and exact access frontier;
- [`DEFINITION_AUDIT_v0_38.md`](DEFINITION_AUDIT_v0_38.md) for the exact
  classical instrument and nuisance semantics;
- [`THEOREM_DRAFT_v0_38.md`](THEOREM_DRAFT_v0_38.md) for the proved
  symmetric-family access threshold;
- [`DEVELOPMENT_RESULT_v0_38.md`](DEVELOPMENT_RESULT_v0_38.md) for the burned
  reward/policy fixture;
- [`PRIOR_ART_GATE_v0_38.md`](PRIOR_ART_GATE_v0_38.md) for the subsumption
  boundary; and
- [`FORMULATION_DRAFT_v0_38.md`](FORMULATION_DRAFT_v0_38.md) for the
  resolution-directed role; and
- [`POSTRUN_EMPTY_ACCESS_THEOREM_v0_38.md`](POSTRUN_EMPTY_ACCESS_THEOREM_v0_38.md)
  for a separately labeled theorem noticed after reveal.

Run the bounded tests from the repository root:

```powershell
python -m pytest -q `
  ultra-experiments/millennium/asmp9_reward_gauge_census/decision_relative_access_v0_38
```

The registered confirmation produced six exact rows in `88.94` seconds with a
`72.01 MiB` peak working set. All gates passed, and an exact replay reproduced
every mathematical row and gate value. The floating optimizer proposes active
constraints only; every accepted optimum is reconstructed and certified over
exact rational arithmetic.

The result remains a finite classical specialization, not a general value
identifiability theorem or an ASMP-9 resolution.
