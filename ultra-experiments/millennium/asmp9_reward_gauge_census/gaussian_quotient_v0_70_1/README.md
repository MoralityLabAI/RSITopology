# ASMP-9 Gaussian quotient v0.70.1

This additive amendment preserves v0.70 and makes its quotient-loss metric
explicitly coordinate-covariant.

```powershell
python -m pytest -q test_coordinate_metric.py
python verify_development.py
```

The invariant risk is `trace(W M^-1)` with both information `M` and loss
metric `W` transported under coordinate changes. A policy functional is
transported as a covector. Silently resetting either object changes the
scientific question.

This is a scope correction, not a new optimal-design theorem or ASMP-9
resolution.
