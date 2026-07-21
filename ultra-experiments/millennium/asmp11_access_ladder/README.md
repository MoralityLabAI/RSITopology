# ASMP-11 Boolean access ladder

CPU-only exact access-lattice seed for the v0.2 conditional-defection
detectability candidate.

```powershell
python -m pytest -q ultra-experiments/millennium/asmp11_access_ladder/test_access_ladder.py
python ultra-experiments/millennium/asmp11_access_ladder/run.py
python ultra-experiments/millennium/asmp11_access_ladder/verify_result.py
```

The claim-eligible run is permitted only after `registration_v0_1.json` and
its source files are committed.

For review, read `RESULT_v0_1.md`, `PRIOR_ART_v0_1.md`, and
`PRIOR_ART_ADDENDUM_v0_1.md` together. The v0.1 cost column is explicitly a
nonadaptive exhaustive upper bound, not an adaptive query lower bound.
