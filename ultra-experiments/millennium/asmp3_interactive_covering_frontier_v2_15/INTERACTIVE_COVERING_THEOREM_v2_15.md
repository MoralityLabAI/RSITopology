# ASMP-3 interactive covering frontier theorem v2.15

## Scope

This theorem extends the v2.2 unique-marker communication/query frontier from a
single message followed by nonadaptive queries to arbitrary-round public-coin
interaction with adaptive semantic queries and bounded completeness.

It is an exact resource theorem for one registered family.  It is not a
universal lower bound for every ASMP-3 task.

## Interface

There are `N` semantic atoms.  The ideal semantic vector is promised to be
either the all-zero vector or to contain one marker at index `j`.

Freeze a public-coin interactive verifier with:

- an arbitrary finite number of prover/verifier rounds;
- at most `K` possible complete prover transcripts for each public seed;
- at most `q` adaptively selected ideal semantic queries; and
- pointwise perfect soundness on the zero-marker world against every prover.

A complete prover transcript is the concatenation of all prover-controlled
symbols along one interaction.  For a fixed-length `b`-bit prover budget,
`K <= 2^b`, regardless of how those bits are split among rounds.  Verifier
messages are unrestricted in this counting statement, but before a semantic
hit they reveal no hidden marker information that was not already present in
the public seed and transcript history.

Completeness may be randomized through the public seed and prover private
coins.  Its value is the minimum, over marker indices, of the best honest
acceptance probability.

## Transcript-compression lemma

Fix a public seed `r` and a complete prover transcript `t`.  Run the verifier
counterfactually with every semantic answer equal to zero.  Let `Q(r,t)` be the
set of distinct atoms queried on this all-zero-answer path.  Then

```text
|Q(r,t)| <= q.
```

If a one-marker execution with marker `j` follows transcript `t`, accepts, and
never queries `j`, every semantic answer and verifier state is identical to the
zero world.  A malicious zero-world prover can reproduce the same transcript,
contradicting pointwise perfect soundness.  Therefore every accepting marker
for `(r,t)` lies in `Q(r,t)`.

The union over all complete prover transcripts has size at most

```text
|union_t Q(r,t)| <= Kq.                              (1)
```

This proof permits arbitrary interaction and arbitrary adaptive query trees.
Only their all-zero paths matter before the first marker hit.

## Exact public-coin maximin theorem

### Theorem

For the interface above, the maximum worst-marker completeness is exactly

```text
V(N,K,q) = min(1, Kq/N).                             (2)
```

Consequently perfect completeness is possible if and only if

```text
Kq >= N.                                             (3)
```

### Upper bound

For each public seed, (1) says that at most `min(N,Kq)` markers can possibly
lead to acceptance.  Average the marker success probability first over a
uniform marker and then over the public seed and any prover randomness:

```text
(1/N) sum_j Pr[accept | marker j] <= min(N,Kq)/N.
```

At least one marker has success no larger than that average, proving the upper
bound in (2).

### Attainment

Let `m=min(N,Kq)` and draw a public seed `r` uniformly from the `N` cyclic
offsets.  Form the cyclic window

```text
W_r = {r, r+1, ..., r+m-1} mod N.
```

Partition `W_r` into at most `K` blocks of size at most `q`.  If marker `j` is
in the window, the prover sends its block identifier and the verifier queries
that block.  Otherwise the prover may send any identifier and the verifier
fails to find a marker.  The zero world always rejects.

Every marker belongs to exactly `m` of the `N` cyclic windows, so every marker
succeeds with probability `m/N`.  This matches (2).

## Fixed-length bit frontier

With `b` prover-controlled bits, set `K=2^b` to obtain

```text
V(N,b,q) = min(1, 2^b q/N).                          (4)
```

For `N=2^n` and `q=2^a`, the exact value is

```text
V = 2^min(0,b+a-n),
```

and perfect completeness is equivalent to `b+a>=n`.  Splitting the `b` bits
over any number of rounds leaves the complete-transcript capacity equal to
the product of the per-round alphabet sizes, namely `2^b`.

## Honest-work separation

The attaining protocol assumes that the honest prover knows the marker it must
name.  Under the v2.1 black-box access model, locating that marker exactly still
costs `N` semantic probes, and a `q_find`-probe randomized search has exact
worst-marker success `q_find/N`.

Thus the family retains three distinct resources even after allowing
interaction:

```text
honest Find cost:        N black-box semantic probes
prover transcript count: K (or b fixed-length bits)
verifier Check cost:     q adaptive ideal semantic queries
```

Interaction does not erase the pre-transcript honest search barrier.

## Exhaustive evidence

The machine artifact contains:

- 13,413 exact `(N,K,q)` frontier points;
- every one of 97,062 binary adaptive query trees for `N=2,...,5` and depths
  `1,...,3`, comprising 464,010 marker runs;
- 49 exhaustive small compressed-codebook frontiers;
- 738 exact cyclic public-coin attainment checks;
- 78 distributions of fixed prover bits over up to six rounds; and
- 3,310 power-of-two bit/query frontier points through `N=2^20`.

Every adaptive tree hits exactly the marker set on its all-zero-answer path;
there are zero violations.  The clean-room checker reconstructs every row and
the canonical tree digest without importing the producer.

## Boundary

The theorem assumes pointwise perfect zero-world soundness.  A positive
soundness allowance can permit some no-hit acceptance and needs a separately
frozen tradeoff.  Stronger side information, structured atom geometry,
variable transcript codebooks not charged by `K`, quantum semantic queries, or
different task families can also change the result.

Within the declared unstructured marker family, however, round count, public
coins, prover private randomness, and semantic-query adaptivity do not improve
the exact frontier.
