# ASMP-4 causal encoder collapse v0.22

This package executes the encoder-optimized route from the v0.20 stop. It
proves feasibility equivalence, exact finite and asymptotic rates, a strict
static-versus-causal separation, and inheritance across the complete small and
memoryless censuses.

Run the central harness:

```powershell
python run_verification.py
```

Run the import-independent verifier:

```powershell
python verify_causal_encoder_collapse.py
```

Run focused tests:

```powershell
python -m pytest -q test_causal_encoder_collapse.py
```

The exact registration and frozen claim are `causal_encoder_contract_v0_22.json`
and `causal_encoder_collapse_claim_v0_22.json`.

The v0.23 successor freezes the timing omitted here. It proves a sharp jump
from the same-step region to an empty region at every positive integer delay
under arbitrary current modes, then gives charged-preview and predictable-mode
restoration theorems.
