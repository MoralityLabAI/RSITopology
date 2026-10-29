# ASMP-3 online noisy-trace extractor v2.10

This package extracts a valid local refutation from one actual noisy protocol
execution.  It re-evaluates the logged candidate under `H`, fails closed when
noise forged the candidate, and therefore needs neither ideal replay nor
strategy restart.

Run:

```powershell
python run_online_noisy_trace_extractor.py
python verify_online_noisy_trace_extractor.py
python build_release_manifest.py
python -m pytest . -q
```

The result covers one-shot stateful strategies under public trace-complete noisy
rejection binding and v2.7's adaptive path-error bound.  It does not infer those
contracts from the current typed successor.
