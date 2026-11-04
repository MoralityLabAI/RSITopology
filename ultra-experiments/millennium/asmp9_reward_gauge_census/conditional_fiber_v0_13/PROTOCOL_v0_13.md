# ASMP-9 conditional-fiber quotient protocol v0.13

## Status

Prospective CPU-only protocol. Every graph, odds ratio, and cycle length in
the development census is burned. The registered cells below are disjoint.

## Frozen statements

1. Conditioning comparison counts on vertex win balance removes the scalar
   Bradley-Terry nuisance exactly.
2. The conditional law exposes exactly the span of count differences inside
   the observed fiber.
3. The full cycle quotient is identifiable on a fiber if and only if its
   affine rank equals graph cycle rank.
4. Singleton and rank-deficient fibers cannot support a full quotient claim.
5. On a single cycle's zero-balance fiber, the conditional law is a
   one-parameter exponential family in the cycle circulation and admits an
   exact randomized one-sided test.

The proof is frozen in `THEOREM_v0_13.md`.

## Fresh liveness registry

The registered graphs are:

- a five-cycle;
- a seven-cycle;
- a three-path theta graph with six edges;
- a square with one diagonal; and
- two triangles sharing one vertex.

Each is exhaustively enumerated at one, two, and three trials per edge.
Every fiber must be assigned its exact affine rank. Flat-null probability mass
is reported by visible rank.

No minimum full-rank probability is imposed. The structural liveness
requirement is that every fresh graph contain both a full-rank fiber and a
rank-deficient fiber. This makes both authorization and abstention paths live
without converting registry prevalence into a population claim.

## Fresh conditional-power calibration

The burned development census suggested:

```text
n / k * log(R)^2 approximately 25
```

at exact conditional size `0.05` and power `0.8`.

Fresh cells use:

```text
k in {10,13,18}
R in {7/5,7/4,8/3}
n = the integer frozen in protocol_v0_13.json
```

where each integer is the nearest-integer evaluation of:

```text
25 k / log(R)^2
```

performed before registration.

The exact rational power must fall in `[0.78,0.82]`. This is a prospective
calibration gate on new cells, not a minimax theorem. It deliberately avoids
calling the first power crossing a critical sample size: the burned census
showed exact-size conditional power can decrease between adjacent sample
counts.

## Gates

- **G0 registration binding:** registration commit is HEAD, tracked files are
  clean, implementation commit is an ancestor, and every sealed hash matches.
- **G1 graph arithmetic:** every fresh graph has its frozen cycle rank and
  every flat-null rank-mass distribution sums exactly to one.
- **G2 scalar nuisance cancellation:** every exact gauge-factor and selected
  normalized-law comparison agrees on every fresh cell.
- **G3 visible quotient:** no fiber rank exceeds graph cycle rank, and every
  graph has both full-rank and deficient fibers.
- **G4 non-vacuous statuses:** full-quotient and unavailable/partial mass are
  both strictly positive in every graph family.
- **G5 one-cycle formula:** generic fiber enumeration and the closed-form
  conditional law agree exactly for every fresh `(k,R)` pair.
- **G6 exact conditional test:** every test has size exactly `1/20`, a
  monotone likelihood ratio of exactly `R`, and power above size.
- **G7 fresh power calibration:** all nine exact powers lie in
  `[39/50,41/50]`.
- **G8 claim-boundary telemetry:** every result records conditional scope,
  full-versus-deficient fiber mass, and the nonmonotonicity warning.
- **G9 resource envelope:** CPU only, at most 180 seconds and 2 GiB peak
  resident memory.

All gates passing yields:

```text
conditional_fiber_cycle_quotient_verified_v0_13
```

## Claim boundary

This validates a finite exact conditional experiment and a fresh calibration
of its one-cycle power scaling. It is not an unconditional goodness-of-fit
test, a positive certificate of scalarity, a new toric-statistics theorem, a
human-response model, a general IRL theorem, or an ASMP-9 resolution.
