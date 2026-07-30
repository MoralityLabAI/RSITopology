# ASMP-9 history replacement v0.71

This development package gives a total exact decision for a bounded finite
path valuation:

```text
Markov edge reward exists
  iff path values lie in the path-incidence column space.
```

Failure emits an exact left-kernel witness and constructs the minimal
endpoint/time-respecting future-increment history quotient that replays the
valuation as an augmented reward machine.

```powershell
python -m pytest -q test_history_replacement.py
python verify_development.py
```

The result is classical finite linear algebra and weighted-automata machinery
specialized to the ASMP-9 replacement-object ledger. It does not validate a
human/model value object or resolve ASMP-9.
