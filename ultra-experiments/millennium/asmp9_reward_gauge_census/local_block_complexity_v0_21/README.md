# ASMP-9 local-block complexity v0.21

Development target: classify exact value computation inside the irreducible
biconnected block left open by v0.20.

The candidate boundary theorem is:

```text
epsilon = 1/2, N = |E|, n_e >= 1

exact ASMP availability on one biconnected block
  = T_G(0,2) / 2^|E|.
```

The current files are development-only.  No claim becomes eligible until a
versioned protocol and registration are frozen before fresh graph outcomes
are computed.

Development test:

```powershell
python -m pytest -q `
  ultra-experiments/millennium/asmp9_reward_gauge_census/local_block_complexity_v0_21
```

