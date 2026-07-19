# ASMP-1 interaction-order tomography

This seed turns the singleton-intervention obstruction into a constructive
design theorem. For Boolean mechanisms under uniform parent environments,
interventions fixing at most `r` parents recover exactly Walsh interactions of
degree at most `r`.

It also tests a symmetry effect that plain rank misses: on the complete Boolean
class, labelled recovery needs `r=n`, while recovery modulo signed parent
permutations needs only `r=n-1`.

The exact minimum-cost design fixes one all-positive assignment for every parent
subset through the target degree. It reaches full rank with the smallest total
number of fixed coordinates, while the redundant all-assignments design is
reported as a better-conditioned comparator.

The formal statements are in [`THEOREM_v0_1.md`](THEOREM_v0_1.md).

## Intended commands

Before the claim-eligible enumeration:

```powershell
python -m unittest -v test_interaction_tomography.py
```

After the protocol, theorem, source, and tests are committed:

```powershell
python interaction_tomography.py `
  --protocol protocol_v0_1.json `
  --output artifacts/result_v0_1.json
```

The experiment is CPU-only. It is a finite calibration for coordinated
interventions, not evidence that transformer features are Boolean Fourier
coordinates.
