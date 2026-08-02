# ASMP-4 registered sensor classification v0.16

This package answers the formalization route opened by v0.15. It makes the sensor experiment explicit theorem data: a fixed partition `P` of the four disturbance modes, with the current `P` symbol injectively recoverable from the charged read transcript.

All 15 partitions are classified on the positive-volume v0.13 collar. Exactly four refine the two `q` fibers and are feasible; the other eleven fail at the first control step. If a feasible partition has `k` blocks, its exact full-collar region is `[1+log2(k),infinity) x [2,infinity)`. Thus `k=2,3,4` yields read corners `2`, `log2(6)`, and `3`, while the write corner stays `2`.

For initial radius `0<rho<=1`, exact transcript counts are `k^T ceil(rho*2^T)` reads and `2^T ceil(rho*2^T)` writes.

Run:

```powershell
python run_verification.py
python verify_registered_sensor_classification.py
python -m pytest -q test_registered_sensor_classification.py
```

This is a complete classification for one registered finite sensor grammar on one nondegenerate plant, not the universal nonlinear ASMP-4 theorem.

Successor: [v0.17](../asmp4_zero_error_sensor_kernels_v0_17/RESULT.md)
extends the grammar to finite stochastic memoryless kernels under
support-zero-error safety. The frozen v0.16 claim remains unchanged.
