# ASMP-9 uniform above-floor evaluation v0.22

Development target: extend the v0.21 count-floor classification to a declared
uniform trial count `r>=2` on every edge of one biconnected block.

The candidate theorem is a direct specialization of Backman's weighted
partial-orientation formula:

```text
F_G(r)
  = (1-z)^(|V|-1) z^(|E|-|V|+1)
    T_G((1-2z)/(1-z),1/z),

z = 2^(-r).
```

Every fixed `r` lies on the Jaeger-Vertigan-Welsh hard curve `H_-1`.

Development tests:

```powershell
python -m pytest -q `
  ultra-experiments/millennium/asmp9_reward_gauge_census/uniform_above_floor_v0_22
```

No claim becomes eligible until a versioned protocol is frozen and registered
before fresh graph outcomes are computed.

