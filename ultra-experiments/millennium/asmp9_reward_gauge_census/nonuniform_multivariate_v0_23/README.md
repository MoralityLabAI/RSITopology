# ASMP-9 nonuniform multivariate design v0.23

This additive successor addresses the exact nonuniform local-value gap left
open by v0.22.1.

It freezes two claims:

1. arbitrary positive integer counts at `epsilon=1/2` have an exact
   edge-multivariate `q=-1` Tutte representation; and
2. an infinite K4 family consists of strict suboptimal one-exchange local
   maxima and explicitly violates M-concavity.

The graph polynomial and weighted orientation machinery are classical.  The
candidate contribution is the ASMP specialization and exact exchange-trap
family.  Optimizer hardness and global maximin design remain open.

## Development tests

```powershell
python -m pytest -q `
  ultra-experiments/millennium/asmp9_reward_gauge_census/nonuniform_multivariate_v0_23
```

## Claim-eligible workflow

The registration, run, independent verification, and release commands will be
recorded only after the prereveal files are committed.
