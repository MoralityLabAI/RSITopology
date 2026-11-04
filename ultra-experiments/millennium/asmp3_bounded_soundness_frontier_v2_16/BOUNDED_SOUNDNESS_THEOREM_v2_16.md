# ASMP-3 bounded-soundness interactive frontier theorem v2.16

## Scope

This theorem extends the v2.15 arbitrary-round unique-marker frontier from
perfect zero-world soundness to a public-coin zero-world soundness bound
`s<1`.  It gives the exact completeness and completeness-soundness gap, not
only an upper bound.

The task and transcript/query interface remain those of v2.15.  The theorem is
not a cross-task ASMP-3 lower bound.

## Interface

There are `N` ideal semantic atoms with the promise that the semantic vector is
either all zero or has one marker.  The verifier uses public randomness visible
to the prover, allows arbitrary-round interaction, has at most `K` complete
prover transcripts for each public seed, and makes at most `q` adaptive ideal
semantic queries.

Against every zero-world prover strategy,

```text
Pr[verifier accepts the all-zero vector] <= s,       0 <= s < 1.
```

All verifier randomness is included in the public seed.  This public-coin
condition is used in the bad-seed lemma below.

## Bad-public-seed lemma

For a public seed `r`, call the seed bad if some prover transcript makes the
verifier accept the all-zero semantic vector without a marker hit.

Because `r` is public, a malicious prover can choose, for every bad seed, a
corresponding accepting transcript.  One adversarial strategy can make those
choices seed by seed.  Therefore soundness implies

```text
Pr[r is bad] <= s.                                  (1)
```

On a nonbad seed, the v2.15 transcript-compression lemma applies: every
accepting one-marker execution must query its marker, and the union of the
`K` all-zero-answer transcript paths contains at most

```text
m = min(N,Kq)                                       (2)
```

markers.

## Exact theorem

### Theorem

The maximum worst-marker completeness is

```text
C*(N,K,q,s) = s + (1-s) min(1,Kq/N).                (3)
```

The exact completeness-soundness gap is

```text
C* - s = (1-s) min(1,Kq/N).                         (4)
```

For every `s<1`, perfect completeness is possible if and only if `Kq>=N`.

### Upper bound

On a bad seed, upper-bound the number of potentially successful markers by
`N`.  On every good seed, (2) upper-bounds it by `m`.  Averaging uniformly over
markers and then over public seeds gives

```text
(1/N) sum_j Pr[accept | marker j]
    <= s + (1-s)m/N.
```

At least one marker is no better than this average.  This proves the maximin
upper bound in (3).

### Attainment

Mix two public modes:

1. with probability `s`, accept unconditionally; and
2. with probability `1-s`, run the v2.15 cyclic window protocol covering `m`
   markers per public rotation.

The all-zero world accepts exactly in the first mode, so soundness is `s`.
Every marker succeeds in the first mode and in exactly an `m/N` fraction of the
second mode.  Its completeness is therefore exactly (3).

For rational `s=a/d`, a finite uniform public seed space with `dN` atoms gives
an exact receipt: `aN` unconditional-accept atoms and `(d-a)N` cyclic-cover
atoms.  Arbitrary real `s` can be represented by a nonuniform public mode of
mass `s`, or approached by rational finite seed spaces.

## Finite uniform public seeds

Suppose there are exactly `R` equally likely public seeds, of which `B` are bad.
Let each of the `G=R-B` good seeds cover at most `m` markers.  Total good-seed
incidences are at most `Gm`, so some marker has good-seed degree at most

```text
floor(Gm/N).
```

Consecutive length-`m` chunks of the repeated cyclic marker sequence distribute
those incidences with degrees differing by at most one and attain the floor.
The exact discrete worst-marker value is

```text
(B + floor(Gm/N))/R.                                (5)
```

The harness exhaustively checks 25,523 small coverage families and finds zero
violations of this optimum.

## Target-gap resource threshold

For a desired gap `gamma<=1-s`, (4) gives the exact transcript threshold

```text
K >= ceil(gamma N / ((1-s)q)).                      (6)
```

Each of 3,103 registered rows checks that this integer threshold attains the
target and that one fewer transcript fails it.  With fixed-length prover bits
`b`, substitute `K=2^b`.

## Honest work and semantic noise

The v2.1 honest pre-transcript marker search cost remains `N` black-box probes.
Equations (3)-(6) concern the subsequent interactive transcript/check phase.

The theorem uses an ideal semantic oracle.  Under a noisy oracle, soundness and
completeness must be composed with a declared selected-path risk as in v2.13;
this release does not silently identify ideal soundness `s` with noisy-oracle
soundness.

## Evidence

The producer and independent checker reconstruct:

- 17,784 exact rational `(N,K,q,s)` rows;
- 12,150 finite uniform-seed balancing rows;
- 25,523 exhaustively enumerated small coverage families;
- 3,103 exact target-gap transcript thresholds; and
- the v2.15 and v2.13 parent contracts.

All arithmetic is exact.  The clean-room checker does not import the producer.

## Boundary

The public-coin condition is essential to the proof of (1): the prover must be
able to choose its zero-world strategy as a function of the visible seed.
Private verifier coins require a different analysis.  Structured side
information, quantum queries, uncharged transcript alphabets, noisy-oracle
composition without a path-risk contract, and other ASMP-3 task families also
remain outside this theorem.
