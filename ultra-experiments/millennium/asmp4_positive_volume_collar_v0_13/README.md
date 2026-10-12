# ASMP-4 positive-volume collar v0.13

This package removes two degeneracy objections at once. It gives the registered ASMP-4 fork a positive-dimensional circle NHIM inside a positive-volume safe collar, and it proves exact finite-horizon corrections for every fixed positive initial margin.

The plant is

`theta_next=theta+1/4 mod 1; n_next=2n+u-q(z); z_next=w`,

where `z` is one of `-3,-1,1,3`, `q(z)` is `0,0,8,8`, and `u` lies in `[-2,10]`. The full safe set is `S^1 x [-1,1] x modes`, of normalized volume 2. Its feedback-cancelled invariant circle is `S^1 x {0}`.

For the full collar, the exact computed/read-write region is `[2,infinity) x [2,infinity)` bits per step, while the forced raw registry gives `[3,infinity) x [2,infinity)`. For `0<rho<=1`, the exact normal spanning count is `ceil(rho*2^T)`.

Run:

```powershell
python run_verification.py
python verify_positive_volume_collar.py
python -m pytest -q test_positive_volume_collar.py
```

The claim is deliberately local to this registered example. It does not prove perturbation/noise robustness, choose the canonical registry intended by ASMP-4, or complete the global variational classification.

Successor: the [v0.14 stop certificate](../asmp4_positive_volume_stop_certificate_v0_14/HARNESS_STOP_CERTIFICATE_v0_14.md)
uses this nondegenerate fork to close the repository-local construction loop.
The frozen v0.13 claim is unchanged.
