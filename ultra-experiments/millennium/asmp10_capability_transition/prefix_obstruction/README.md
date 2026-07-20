# ASMP-10 finite-prefix obstruction seed

This CPU-exact experiment tests the negative branch of ASMP-10. It treats the
allowed training observables as finite local jets of a one-dimensional
polynomial loss along a frozen gradient-descent prefix.

The experiment is a consolidation of classical Hermite interpolation into an
ASMP instrument. It is not a novelty claim and does not address neural-network
training without the registered polynomial-degree restriction.

Run tests with:

```powershell
python -m pytest ultra-experiments/millennium/asmp10_capability_transition/prefix_obstruction/test_prefix_obstruction.py -q
```

The claim-eligible runner must not execute until `registration_v0_1.json`
exists and binds the committed runner and protocol hashes.

