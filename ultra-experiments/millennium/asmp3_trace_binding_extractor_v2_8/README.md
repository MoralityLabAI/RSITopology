# ASMP-3 trace-binding extractor v2.8

This package turns operational `Refute` binding into an explicit finder. Every
ideal rejection must log a successful canonical call over previously queried
classes; the extractor scans that trace, returns the witness, and charges all
replay, ideal-evaluation, scan, canonicalization, message, and query resources.

Run from this directory:

```powershell
python run_trace_binding_extractor.py
python verify_trace_binding_extractor.py
python build_release_manifest.py
python -m pytest . -q
```

The theorem does not derive trace-complete binding from a decision label or
remove the remaining efficient ideal-replay premise.
