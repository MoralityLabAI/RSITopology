# ASMP-8 v0.3a calibrated certificate

This is the CPU-only calibration successor to the exact v0.2 dual frontier.
It tests whether target-blind reward-error audits can turn the sharp bound into
a sound and non-vacuous prereveal certificate across several proxy-only
optimizer paths.

The source, protocol, and registration are committed before the claim run.
The runner refuses dirty or hash-mismatched registered sources and refuses to
overwrite outputs.

After registration:

```powershell
python ultra-experiments/millennium/asmp8_goodhart_frontier_census/v0_3_calibrated_certificate/run.py
python ultra-experiments/millennium/asmp8_goodhart_frontier_census/v0_3_calibrated_certificate/verify_result.py
python -m pytest ultra-experiments/millennium/asmp8_goodhart_frontier_census/v0_3_calibrated_certificate -q
```

No GPU is used. A pass remains a finite synthetic calibration result, not
evidence about a learned reward model.
