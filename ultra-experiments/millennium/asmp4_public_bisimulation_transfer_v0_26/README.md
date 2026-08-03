# ASMP-4 public-bisimulation transfer v0.26

This package gives a checkable bridge from possibly infinite public-history
safety games to finite scheduler theorems. An exact costed alternating
bisimulation preserves safety, enabled action types, vector costs, and successor
classes, and therefore preserves the whole worst-path budget region. A
deterministic finite quotient can then use v0.25.

Run the central harness:

```powershell
python run_verification.py
```

Run the import-independent verifier:

```powershell
python verify_public_bisimulation_transfer.py
```

Run focused tests:

```powershell
python -m pytest -q test_public_bisimulation_transfer.py
```

The exact registration and frozen claim are `public_bisimulation_contract_v0_26.json`
and `public_bisimulation_claim_v0_26.json`.
