# ASMP-3 encoding invariance v2.0

This package proves that replication-quotiented local refutation dimension is
exactly invariant under bijections of false transcripts and semantic classes
that transport `Refute` soundly and completely.

It also certifies the one-macro resource trap: replacing `N` primitive parity
bits with one syntactic atom changes semantic content and still costs `N`
primitive queries to evaluate exactly.

Run:

```powershell
python run_encoding_invariance.py
python verify_encoding_invariance.py
python build_release_manifest.py
python -m pytest . -q
```

The parity barrier is for deterministic exact evaluation; approximate, promised,
cached, or stronger-oracle interfaces require separate accounting.
