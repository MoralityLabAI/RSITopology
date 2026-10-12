# ASMP-11 Boolean access-ladder protocol v0.1

## Status

This protocol is frozen before execution. It is a finite theorem/instrument
seed for the proposed `ASMP-11` access frontier, not a claim about
cryptographic or learned backdoors.

## Paired mechanisms

There are six Boolean parent variables in the `{-1,+1}` convention. For each
degree `k in {2,3,4,5,6}`, each `k`-element support, and each sign, construct a
paired mechanism:

- clean: the parity feature is present in a dormant output channel;
- conditional-defection seed: the same feature is routed to the action channel
  when a deployment flag is one;
- when the deployment flag is zero, both action outputs are zero;
- after forgetting output-channel labels, their coefficient-magnitude spectra
  are identical.

This gives 114 planted mechanisms. It is an algebraic negative control, not a
linguistic trigger.

## Access lattice

Access class `A_(r,s)` returns every Walsh coefficient through order `r` after
every intervention fixing at most `s` parent coordinates. The grid is
`r,s in {0,...,6}`. Classes are ordered coordinatewise and the implementation
must verify that each stronger class contains the complete observation
signature of every weaker class.

For a degree-`k` parity, fixing `s` support coordinates leaves degree `k-s`.
The registered prediction is therefore:

```text
distinguishing advantage(A_(r,s)) = 0  when r+s < k
distinguishing advantage(A_(r,s)) = 1  when r+s >= k.
```

Advantage is total variation between the clean and uniformly planted
observation laws. The exhaustive query-count upper bound is reported for every
cell; resource coordinates are never collapsed to query count in the gate.

## Gates

- `G0`: source hashes match the prospective registration.
- `G1`: all 114 mechanisms and 245 degree/access cells are enumerated.
- `G2`: every paired model matches on benign action and unlabelled coefficient
  spectrum.
- `G3`: every cell below `r+s=k` has exact advantage zero.
- `G4`: every cell on or above the boundary has exact advantage one.
- `G5`: the coordinatewise simulator/containment test passes for every model
  and nested access pair.
- `G6`: the same threshold holds independently on lexicographically interleaved
  construction and held-out support/sign sets.
- `G7`: the minimum total resource `r+s` is exactly `k` for every registered
  degree.

All passing yields `finite_access_ladder_established`; otherwise the result is
`invalid_or_not_established`.

## Claim boundary

The parity threshold is a direct Boolean-Fourier restriction fact. The useful
artifact is the two-resource access lattice, its simulation audit, and a sharp
planted negative control for future detectors. This run does not prove sample
complexity for arbitrary white-box algorithms, cryptographic undetectability,
semantic conditional defection, or ASMP-11 resolution. Raw full-weight access
is not modeled.

## Resources

CPU only; 120 seconds; 512 MiB Python memory; no GPU.
