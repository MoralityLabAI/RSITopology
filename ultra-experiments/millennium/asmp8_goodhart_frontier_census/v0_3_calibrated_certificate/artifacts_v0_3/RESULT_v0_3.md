# ASMP-8 v0.3a registered calibrated-certificate result

**Verdict:** `calibrated_certificate_valid_but_vacuous`

## Result

The run evaluated 20 proxy-only policies from 4 optimizer families against three hidden reward-error populations. Each of the nine calibration conditions used 4,096 target-blind audit replicates.

- Maximum one-sided 95% binomial upper bound on simultaneous radius failure: 0.000731.
- False-safe registered certificates conditional on valid radii: 0.
- Diffuse-error, m=512 registered non-vacuity: 44.767%.
- Corresponding Pinsker non-vacuity: 0.000%.
- Proxy-only rare-tail false-safe cells: 73,728.
- RMSE-only rare-tail false-safe cells: 22,847.

## Calibration conditions

| error family | m | radius failures | CP upper | registered coverage |
|---|---:|---:|---:|---:|
| diffuse_low_error | 32 | 0/4096 | 0.000731 | 0.000% |
| diffuse_low_error | 128 | 0/4096 | 0.000731 | 15.048% |
| diffuse_low_error | 512 | 0/4096 | 0.000731 | 44.767% |
| heteroskedastic_proxy_coupled | 32 | 0/4096 | 0.000731 | 0.000% |
| heteroskedastic_proxy_coupled | 128 | 0/4096 | 0.000731 | 0.000% |
| heteroskedastic_proxy_coupled | 512 | 0/4096 | 0.000731 | 24.426% |
| rare_top_tail | 32 | 0/4096 | 0.000731 | 0.000% |
| rare_top_tail | 128 | 0/4096 | 0.000731 | 13.854% |
| rare_top_tail | 512 | 0/4096 | 0.000731 | 33.010% |

## Interpretation

The v0.2 dual bound remains mechanically sound after replacing a known error radius with target-blind audit bounds. The primary operational question is non-vacuity: a valid certificate is useful only where its lower bound clears zero. The rare-tail arm tests the complementary failure mode in which scalar proxy accuracy looks adequate while optimization concentrates on the bad tail.

## Claim boundary

Synthetic finite-population calibration of a classical robust lower bound; no learned reward model, no real human-preference uncertainty set, no RL trajectory, and no ASMP-8 resolution.
