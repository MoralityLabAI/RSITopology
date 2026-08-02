# ASMP-4 support-zero-error sensor kernels v0.17

This package extends the deterministic partition theorem to finite memoryless stochastic sensor kernels. A registered kernel gives each mode a nonempty output support, assigns arbitrary rational probabilities strictly positive on that support, and charges the realized raw output symbol injectively.

Under universal/support-zero-error safety, feasibility holds exactly when outputs supported by the `q=0` modes are disjoint from outputs supported by the `q=8` modes. If `a` output symbols are active, the exact full-collar region is `[1+log2(a),infinity) x [2,infinity)`. Probabilities do not otherwise enter.

The harness exhausts all 53,108 nonempty support relations through four declared output symbols: 724 are feasible and 52,384 are infeasible. V0.16 is recovered as the deterministic special case.

Run:

```powershell
python run_verification.py
python verify_zero_error_sensor_kernels.py
python -m pytest -q test_zero_error_sensor_kernels.py
```

Block error, expected-length coding, channel memory, hidden state, and vanishing failure probability remain outside this registered contract.
