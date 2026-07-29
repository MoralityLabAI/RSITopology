# ASMP-9 decision-relative access v0.38

## Current status

`development_instrument_and_theorem_ready_for_disjoint_registration`

Version v0.37 separated zero-error nuisance components, quantitative target
risk, and full expanded-parameter deficiency. This successor implements the
missing middle object: exact deficiency relative to a frozen target-only
policy-decision type after a declared nuisance marginalization.

Start with:

- [`DEFINITION_AUDIT_v0_38.md`](DEFINITION_AUDIT_v0_38.md) for the exact
  classical instrument and nuisance semantics;
- [`THEOREM_DRAFT_v0_38.md`](THEOREM_DRAFT_v0_38.md) for the proved
  symmetric-family access threshold;
- [`DEVELOPMENT_RESULT_v0_38.md`](DEVELOPMENT_RESULT_v0_38.md) for the burned
  reward/policy fixture;
- [`PRIOR_ART_GATE_v0_38.md`](PRIOR_ART_GATE_v0_38.md) for the subsumption
  boundary; and
- [`FORMULATION_DRAFT_v0_38.md`](FORMULATION_DRAFT_v0_38.md) for the
  resolution-directed role.

Run the bounded tests from the repository root:

```powershell
python -m pytest -q `
  ultra-experiments/millennium/asmp9_reward_gauge_census/decision_relative_access_v0_38
```

The reward fixture contains a larger exact census and currently takes about
one minute on the local CPU. The floating optimizer proposes active
constraints only; every accepted optimum is reconstructed and certified over
exact rational arithmetic.

No confirmation grid is registered or run in this directory yet. All current
numerical cases are explicitly burned development evidence.

