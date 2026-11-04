# ASMP-8 Qwen0.8B stratified completion measurement — Prime result v0.1

Status: `measurement_instrument_pass`

## Result

The frozen target-blind measurement completed on a separate Prime A100 40 GB
spot surface:

- 3,456 / 3,456 records;
- 576 unique prompts;
- 18 application-by-half strata;
- exactly four planned server sessions;
- zero thermal pauses;
- maximum observed temperature 29 C;
- maximum observed GPU memory 1,046 MB.

All registered gates passed:

| Gate | Result | Margin-bearing statistic |
|---|---|---:|
| P0 plan and session integrity | pass | zero binding/session failures |
| C0 census and cache-order invariance | pass | maximum probability range 0 |
| R0 restart and repeat stability | pass | maximum probability range 0 |
| L0 proxy liveness | pass | every stratum variance exceeded 1e-8 |

The nine application means ranged from 0.484515 (`prisoner_dilemma`) to
0.658407 (`memetic_treaty`). This variation makes the completion-probability
proxy live across the frozen prompt census while exact repeat and restart
agreement establish runtime stability on this surface.

## Operational finding

Two pre-outcome attempts produced zero records because the initial llama.cpp
build embedded virtual `compute_80` code. With the frozen half-core quota, its
first-request CUDA preparation exceeded the 120-second request timeout. The
same pinned source was rebuilt prospectively for native `sm_80`, hashed, and
committed before the successful attempt. The final native binary completed the
measurement in 406 seconds. Both failed zero-record attempts are retained in
the sealed archive.

This distinction matters: the failures were runtime-image preparation failures,
not measurement failures, and no scientific threshold, model byte, prompt,
runner, analyzer, or outcome was changed.

## Integrity and recovery

- Prime pod: `6808a1ec8cde4c1d8e09e34180e95f74`
- Pod status after recovery: `TERMINATED`
- Active Prime pods after closeout: `0`
- Local archive:
  `D:\Research_Engine\runs\asmp8_qwen08_stratified_completion_measurement_prime_spot_v0_1\asmp8_qwen08_stratified_prime_spot_v0_1_20260725.tar.gz`
- Archive SHA-256:
  `99f937107b34722ecbf734371308b29c2ef9919c05a43e7d18508c39693370da`
- Internal manifest: 3,512 / 3,512 files verified, zero failures.
- Upper-bound cost estimate: USD 0.355.

## Claim boundary

This result establishes measurement coverage, liveness, and invariance on the
Prime execution surface. The manifest contains no outcome labels. It does not
measure correctness, calibration, scalable-oversight sufficiency, Goodhart
pressure, recursive improvement, or resolve ASMP-8.
