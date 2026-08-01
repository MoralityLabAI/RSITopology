# ASMP-4 serial-collapse theorem v0.2

## Successor

The
[asmp4 metric-robust v0.3 successor](../asmp4_metric_robust_collapse_v0_3/RESULT.md)
distinguishes whole-language growth from causal prefix branching and
strengthens the proof with upstream and downstream normal forms. Use it for the
current metric-robust claim.

This package develops a negative resolution of the canonical two-independent-
entropy conjecture and a positive characterization of the architecture that is
actually written down.

The core observation is a relay normal form. In a deterministic serial

```text
sensor -> controller -> actuator
```

architecture, the sensor can simulate the controller on the read transcript it
generates, send the resulting write symbol as its read symbol, and let the
controller relay it. The transformed code has identical plant trajectories and
bijective realized read/write transcript languages (or equal cardinalities
after a fixed plant-independent delay prefix). Consequently the closure of the
two-port region is a diagonal quadrant governed by one operational invariance
entropy. Port-specific peak alphabets or symbol costs are additional resource
coordinates and are outside this two-rate theorem.

Run:

```powershell
python -m pytest test_serial_capacity.py -q
python run_verification.py
python verify_theorem.py
```

The finite harness exhausts 648 budget cells across every two-action,
two-safe-state one-step plant and both full and collapsed observation maps. It
also checks exact unstable, stable, nonhyperbolic, partial-observation,
uncertainty-timing, actuator-side-information, and fixed-FIFO-delay relay
fixtures.

`resolution_claim_v0_2.json` maps the proof to the exact positive and negative
ASMP-4 obligations in `problem_set_v0_1.json`; the independent verifier rejects
missing or extra obligation keys.
