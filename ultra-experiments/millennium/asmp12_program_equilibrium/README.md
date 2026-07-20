# ASMP-12 finite program-frontier census

This CPU-exact seed enumerates pure program equilibria in a three-program,
total source-table language. It asks whether nested program budgets have
monotone cooperative payoff frontiers and whether any failures are caused by
source-label sensitivity to extensionally equivalent programs.

The mathematical and novelty boundary is recorded in `PRIOR_ART_v0_1.md`
before the experiment protocol was frozen.

Run unit tests with:

```powershell
python -m pytest ultra-experiments/millennium/asmp12_program_equilibrium/test_frontier.py -q
```

The claim-eligible census requires a source-bound `registration_v0_1.json`.

