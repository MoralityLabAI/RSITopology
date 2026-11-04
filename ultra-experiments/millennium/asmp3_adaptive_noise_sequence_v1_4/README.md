# ASMP-3 adaptive joint-noise sequence v1.4

This package compiles a truth-aware history-adaptive noise controller with a
global `b`-flip budget across `d` responses.

It proves and certifies the exact phase:

```text
2b<d  -> majority value 1,
2b>=d -> common-transcript value 0.
```

Run:

```powershell
python run_adaptive_noise_sequence.py
python verify_adaptive_noise_sequence.py
python build_release_manifest.py
python -m pytest . -q
```

The result concerns complete joint response histories, not independent
single-response error rates.
