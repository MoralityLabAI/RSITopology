# ASMP-9 out-of-family transport v0.82

This preregistered branch tested whether the nuisance-quotiented Qwen0.8B
content-versus-label response contrast calibrated in v0.68 transports without
refitting to twelve behavior-family labels absent from the v0.68 registry.

The test is deliberately small: one existing model, 528 singleton next-token
scores, no training, and no sampled generation.  `protocol_v0_82.json` is the
machine-readable authority; `PROTOCOL_v0_82.md` explains it.

## Prereveal workflow

```powershell
C:\Python311\python.exe -m pytest test_v082.py -q
C:\Python311\python.exe validate_prereveal_v082.py
C:\Python311\python.exe register_v082.py
```

The exact `registration_v0_82.json` and `authorization_v0_82.json` were
committed and pushed before the hard-cap wrapper is invoked.  Results are then
written outside the repository under
`D:\Research_Engine\runs\asmp9_out_of_family_transport_v0_82_20260801` and
imported only after the frozen analysis completes.

## Result

The registered verdict is
`out_of_family_response_transport_not_established`: local liveness passed on
12/12 new families and the coarse prediction envelope passed on 11/12, but
only 21/24 target cells intersected the frozen construction coefficient band.
See [RESULT_v0_82.md](RESULT_v0_82.md) and [AUDIT_v0_82.md](AUDIT_v0_82.md).

## Scientific boundary

This is an expressed-response transport test.  It does not identify a reward
function, preference ordering, human value, or shaping-equivalence class, and
cannot resolve ASMP-9.
