# ASMP-2 resolution-readiness harness

This harness asks whether `ASMP-CANDIDATE-SET-v0.1` supplies a closed
mathematical statement that can currently be resolved, and it checks the
strongest qualitative local-to-global reading with an exact countermodel.

It does **not** claim to resolve ASMP-2. Its admissible conclusion is narrower:
stop attempting a full resolution of v0.1 until the missing formal inputs are
bound in a successor problem version.

The harness has two independent parts:

1. A closure audit reads the authoritative v0.1 registry, normative statement,
   and hostile referee audit. It checks the problem's own status and whether
   the formal slots needed by its five resolution obligations are bound.
2. An exact-rational witness constructs two smooth, dominated Bernoulli
   environment families on a compact connected deployment interval. They have
   common full support, identical source laws and first derivatives, positive
   local Fisher information, a nonzero utility floor, and a shared finite
   curvature bound, but they lie on opposite sides of the global safety
   threshold at an unsampled deployment point.

Run:

```powershell
python -m pytest test_resolution_harness.py -q
python run_harness.py --output artifacts/result_v0_1.json
python verify_result.py --result artifacts/result_v0_1.json `
  --output artifacts/verification_v0_1.json
```

The stopping argument is in
[`STOPPING_ARGUMENT_v0_1.md`](STOPPING_ARGUMENT_v0_1.md).
