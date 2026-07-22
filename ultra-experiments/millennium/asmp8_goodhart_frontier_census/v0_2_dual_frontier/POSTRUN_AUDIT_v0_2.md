# ASMP-8 v0.2 post-run audit

## Integrity

- Source commit before registration: `9410dbd071692825f0d54d26c1c88426eab65018`.
- Registration commit: `36ef46ce43aa6c62fcd64fd91dc7ea062ab7df2d`.
- The independent verifier replayed the entire policy census, reproduced the
  frontier CSV byte-for-byte, reproduced the witness JSON structurally, and
  passed all eleven verification checks.
- Runtime was 5.21 seconds with 28,909,568 bytes peak RSS, below the registered
  ceilings.

## Result

All eight gates passed. The registry contained 3,876 labelled rational
policies, of which 1,863 strictly improved proxy reward. Across three error
geometries, 5,589 policy/norm cells were checked independently for the robust
formula and for an attaining witness.

At error radius `epsilon = 1/4`, the robust classifications were:

| Proxy-error norm | Robust positive | Boundary | Robust negative |
|---|---:|---:|---:|
| weighted L-infinity | 1,534 | 76 | 253 |
| weighted L2 | 1,505 | 2 | 356 |
| weighted L1 | 1,218 | 32 | 613 |

These rows are different uncertainty models, not competing estimates of one
unknown empirical truth.

## Exact coordinate separation

The strongest same-gain witness under the sup-norm error model holds proxy gain
fixed at `2/15` while dual movement changes from `2/15` to `22/15`. The same
declared proxy improvement can therefore have an eleven-fold difference in
worst-case error coupling.

Conversely, movement `22/15` occurs with proxy gains `1/15` and `29/15` in the
registered policy grid. Movement alone also cannot determine the frontier.

Analogous pairs exist for weighted L2 and weighted L1 error balls. The exact
witness policies are recorded in `artifacts_v0_2/witnesses_v0_2.json`.

## Controls

- The near-tie example attains deterministic regret `1/2 = 2 epsilon` under
  the frozen adverse tie rule, repairing the loose v0.1 positive control.
- The rare-tail example has reference-weighted L2 error squared `1/250000`
  while proxy gain is `+999999/1000000` and true gain is
  `-999999/1000000`. Small average error remains compatible with nearly
  maximal harm when policy movement concentrates on the rare state.

## What was and was not learned

The identity is a direct robust-optimization/support-function result and is
not novel. The experiment validates an exact instrument and shows how to
replace the scalar-KL coordinate that v0.1 rejected:

```text
robust margin = proxy gain - error radius * dual policy movement.
```

The certificate is conditional on both the selected error norm and its radius.
This run does not estimate either from reward-model data. A real-model follow-up
must freeze a calibration procedure on construction data and evaluate coverage
on disjoint outcomes before the robust margin can be interpreted operationally.

