# ASMP-3 resource tradeoff v2.2

This package proves the exact communication/query frontier for one-message
verification of the v2.1 unique-marker family:

```text
minimum messages = ceil(N/q),
minimum bits     = ceil(log2 ceil(N/q)),
capacity         = 2^b q >= N.
```

A partition protocol attains every point.  The release also keeps the `N`-query
honest search cost separate and composes robust v1.9 replication costs.

Run:

```powershell
python run_resource_tradeoff.py
python verify_resource_tradeoff.py
python build_release_manifest.py
python -m pytest . -q
```

The frontier is for a deterministic one-message, nonadaptive-query,
perfect-completeness/perfect-soundness interface.
