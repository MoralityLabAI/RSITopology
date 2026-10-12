# ASMP-3 correlated-noise weak-verifier frontier

This exact CPU experiment repairs the strongest objection in the ASMP-3
round-robin review. It gates false acceptance and false rejection separately,
uses a closed rational correlation class, includes a failing cell inside the
main grid, and supplies a constructive counterexample to atom-averaged semantic
accuracy.

The experiment assumes that an honest challenger has already located a
refuting semantic atom. It therefore tests semantic adjudication after
localization, not the full weak-verifier problem.

Run tests:

```powershell
python -m pytest ultra-experiments/millennium/asmp3_weak_verifier_frontier/test_frontier.py -q
```

After `registration_v0_1.json` is sealed, execute:

```powershell
python ultra-experiments/millennium/asmp3_weak_verifier_frontier/run_frontier.py
```

No NumPy, solver, GPU, or stochastic sampling is used.

