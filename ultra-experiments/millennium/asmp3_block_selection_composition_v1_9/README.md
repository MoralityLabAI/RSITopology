# ASMP-3 block-selection composition v1.9

This package composes `M` v1.8 independently amplified semantic atoms and
charges the risk of an OR predicate or a selector that returns a failed decoded
block whenever one exists.

```text
independent-block risk = 1-(1-e_d(eta))^M,
marginal-only maximum = min(1,M e_d(eta)),
semantic query cost   = M*d.
```

It includes exact minimal-depth tables for target joint risks and a correlation
firewall for adaptive selection.

Run:

```powershell
python run_block_selection_composition.py
python verify_block_selection_composition.py
python build_release_manifest.py
python -m pytest . -q
```

The result covers fixed majority blocks and declared OR/selector interfaces,
not every globally optimized adaptive protocol.
