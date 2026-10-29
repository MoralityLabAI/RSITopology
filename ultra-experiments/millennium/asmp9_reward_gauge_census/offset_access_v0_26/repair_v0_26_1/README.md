# ASMP-9 v0.26.1 mechanical repair

This repair consumes the immutable failed v0.26 result. It does not rerun fresh
scientific cells.

V0.26 passed every mathematical gate but failed its frozen all-gates verdict
because an explanatory prior-art document used spaces where the runner
expected a hyphen and used `not a novelty claim` where the runner expected
`no novelty claim`.

V0.26.1 replaces that prose-substring check with structural checks over:

- immutable source hashes;
- the protocol's registered prior-art identifiers;
- exact allowed and forbidden claim lists;
- the original scientific gate vector; and
- the independent verifier's component checks.

The original v0.26 verdict remains failed.

## Sequence

Commit the repair implementation, then:

```powershell
python ultra-experiments/millennium/asmp9_reward_gauge_census/offset_access_v0_26/repair_v0_26_1/register_v0_26_1.py `
  --output ultra-experiments/millennium/asmp9_reward_gauge_census/offset_access_v0_26/repair_v0_26_1/registration_v0_26_1.json
```

Commit the registration before adjudication. Then:

```powershell
python ultra-experiments/millennium/asmp9_reward_gauge_census/offset_access_v0_26/repair_v0_26_1/adjudicate_v0_26_1.py `
  --registration ultra-experiments/millennium/asmp9_reward_gauge_census/offset_access_v0_26/repair_v0_26_1/registration_v0_26_1.json `
  --output-dir ultra-experiments/millennium/asmp9_reward_gauge_census/offset_access_v0_26/repair_v0_26_1/artifacts_v0_26_1
```
