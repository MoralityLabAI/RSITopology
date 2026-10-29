# ASMP-3 honest-search barrier v2.1

This package constructs a zero-or-one-marker semantic family with
replication-quotiented refutation dimension one and one-query verification after
a witness is supplied.

Locating that witness among `N=2^n` black-box atoms is different:

```text
deterministic exact search = N queries,
randomized q-query maximin success = q/N.
```

It therefore separates combinatorial dimension, honest refutation search, and
post-witness checking exactly.

Run:

```powershell
python run_honest_search_barrier.py
python verify_honest_search_barrier.py
python build_release_manifest.py
python -m pytest . -q
```

Structured, advised, preprocessed, quantum, or witness-bearing interfaces are
outside this black-box theorem.
