# ASMP-9 context gluing v0.11

Development theorem and exact rational instrument for distinguishing:

- a scalar utility in every context separately; from
- one shared context-independent scalar utility.

The candidate obstruction dimension is the mixed-context cycle rank

```text
beta_1(context-labelled union) - sum_context beta_1(context graph).
```

Run the development tests with:

```powershell
python -m pytest `
  ultra-experiments/millennium/asmp9_reward_gauge_census/context_gluing_v0_11 `
  -q
```

The prospective files are:

- `PROTOCOL_v0_11.md`;
- `protocol_v0_11.json`;
- `environment_v0_11.json`;
- `run_verification.py`; and
- `verify_result.py`.

They must be hash-sealed in a registration commit before fresh execution.
