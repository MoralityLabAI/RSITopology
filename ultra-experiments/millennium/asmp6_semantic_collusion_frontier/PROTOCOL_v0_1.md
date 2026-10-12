# ASMP-6 finite semantic-collusion frontier protocol v0.1

## Status and question

This protocol is frozen before the claim-eligible run. It addresses a bounded
slice of `ASMP-6`: how an active finite audit class and two different
covertness definitions change the reliability of a one-bit semantic channel.
It does not estimate asymptotic capacity or construct a linguistic code.

## Registered finite object

- The transcript alphabet consists of four opaque, task-equivalent symbols.
- The benign cover law is uniform.
- The hidden message is one unbiased bit, with no key and no shared random
  variable other than the registered encoder law.
- Each message-conditioned encoder law is a four-symbol distribution whose
  probabilities are integer multiples of `1/4`. There are 35 laws and 1,225
  ordered encoder pairs.
- The auditor chooses a public deterministic map from four input symbols to
  four output symbols. Its charge is the number of symbols the map changes.
  There are 256 maps. At charge budget `b`, the adversary may use any map with
  charge at most `b`.
- The receiver knows the public audit map and uses the exact randomized
  minimax binary decoder. Reliability is the larger of the two
  message-conditioned error probabilities, minimized over decoders and then
  maximized over admissible audit maps.
- Every symbol has registered task utility 1, so utility cannot be spent on
  signaling in this finite object.

## Two covertness games

The binding frontier is computed separately under:

1. `mixture`: total variation between the message-averaged stego law and the
   cover law;
2. `per_message`: the maximum total variation between either
   message-conditioned law and the cover law.

They are never pooled. The detectability grid is `{0, 1/8, 1/4, 1/2}` and the
audit-charge grid is `{0,1,2,3,4}`.

For reporting only, both rational chi-squared orientations are computed with
separate support rules:

```text
chi2_cover_given_stego = sum_y (P_cover(y)-P_stego(y))^2/P_stego(y)
chi2_stego_given_cover = sum_y (P_stego(y)-P_cover(y))^2/P_cover(y)
```

The first orientation upper-bounds `D(P_cover || P_stego)`, matching Cachin's
cover-first convention; the second upper-bounds the reverse KL. TV is the
binding symmetric statistic. KL itself is not evaluated as an exact rational.

## Gates

- `G0 registration binding`: every frozen source hash matches registration.
- `G1 complete census`: 35 laws, 1,225 encoder pairs, 256 audit maps, and 40
  frontier cells are evaluated; the unique-response and full-collapse controls
  pass.
- `G2 definition separation`: at zero TV and zero audit charge, mixture-only
  covertness admits zero minimax error while per-message covertness forces
  minimax error `1/2`.
- `G3 full-audit kill`: charge 4 forces error `1/2` in every registered cell.
- `G4 audit monotonicity`: optimal worst-case error is nondecreasing with the
  permitted audit charge in every `(covertness regime, delta)` stratum.
- `G5 dual chi-squared support`: every exact-zero mixture code has both
  chi-squared quantities zero, and support failures are represented explicitly
  rather than smoothed.

All gates passing yields `finite_registry_frontier_established`. Any failure
yields `invalid_or_not_established`.

## Claim boundary

The result is an exact finite access-class census and a test of whether the
covertness definition manufactures the apparent payload. It does not establish
positive asymptotic rate, adaptive semantic collusion in language models, a
square-root law, a cryptographic lower bound, or ASMP-6 resolution. Optimized
encoder and decoder tables are not written to artifacts; only aggregate
frontiers and hashes are released.

## Resource ceiling

CPU only; wall time 180 seconds; peak Python memory 1 GiB; no GPU.
