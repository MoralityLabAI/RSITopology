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

The completed census and its conservative interpretation are in
`RESULT_v0_1.md`.

Post-result corrections and successors are additive:

- `FRAMEUP_CORRECTION_v0_1.md` identifies the monotone-threshold assumption the
  census rejected;
- `PRIOR_ART_ADDENDUM_v0_2.md` adds the classical strategy-expansion context;
- `PERSISTENCE_SUCCESSOR_SCOPE_v0_2.md` distinguishes a deviation-graph
  construction from an automatic bifiltration claim; and
- `THEY_SING_HYPOTHESIS_AMENDMENT_v0_1.md` replaces the downstream
  threshold-only behavioral hypothesis before any run.

The first successor has now been executed under
`v0_2_survival/RESULT_v0_2.md`: it crosses program budget with temptation and
locates the exact cooperative-survival phase boundary in the registered finite
class.
