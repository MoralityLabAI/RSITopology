# ASMP-3 oracle-parametric replay v2.9

This package compiles a total restartable protocol runtime into its exact ideal
semantic execution by dependency-injecting `H`.  It proves that fresh
nonsemantic seeds preserve the required ideal marginal law and demonstrates why
a recorded noisy transcript cannot reconstruct an unvisited ideal branch.

Run:

```powershell
python run_oracle_parametric_replay.py
python verify_oracle_parametric_replay.py
python build_release_manifest.py
python -m pytest . -q
```

The result composes v2.7 adaptive coupling with v2.8 trace extraction for the
declared restartable oracle-parametric subclass.  It does not infer that runtime
contract from the current typed successor or from protocol admission alone.
