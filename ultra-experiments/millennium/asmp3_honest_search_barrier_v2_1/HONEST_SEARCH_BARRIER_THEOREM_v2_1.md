# ASMP-3 honest-search barrier theorem v2.1

## Status and scope

```text
result_status = exact dimension-one unique-marker search separation
parent_result = ASMP-3-ENCODING-INVARIANCE-v2.0
interface_mode = WV-FIX
semantic_access = classical black-box queries
promise = zero or one true atom among N=2^n atoms
false_worlds = exactly one true atom, with transcript claiming none
changes_parent_problem = false
```

This release isolates the second condition in the canonical Weak-Verifier
Characterization Conjecture: small combinatorial refutation dimension does not
by itself imply that an honest prover can efficiently locate a refutation.

## 1. Unique-marker family

For parameter `n`, the frozen semantic alphabet contains

```text
A_n={a_0,...,a_(N-1)},  N=2^n.
```

The ideal oracle vector is promised to have Hamming weight zero or one.  The
task is to decide whether a marker exists.  In every one-marker world, admit the
false transcript

```text
tau = "no semantic atom is true".
```

If the unique marker is `j`, the singleton set `{a_j}` with answer one refutes
`tau`.  Consequently

```text
r_(E,G)(n)=1.                                        (1)
```

Once `j` is supplied, the verifier receives an `n`-bit index and needs one ideal
semantic query to check it.  The combinatorial witness and post-witness
verification costs are therefore tiny.

The zero-marker world remains legal, so the answer is not known from the
promise.  A global OR macro must distinguish the zero vector from every
one-marker vector and is charged the search cost below.

## 2. Deterministic exact lower bound

Against a deterministic search strategy, answer zero to each queried atom and
place the marker last in its query order.  Until that final query, the answers
are consistent with both the zero-marker world and an unqueried one-marker
world.  Hence exact worst-case search requires

```text
N=2^n
```

semantic queries.  The exhaustive zero-versus-one ambiguity is the OR analogue
of the parity macro accounting in v2.0.

## 3. Exact randomized maximin theorem

### Theorem 1

For any randomized classical strategy using at most `q<=N` semantic queries,
the maximum worst-marker success probability is exactly

```text
q/N.                                                 (2)
```

### Upper bound

Fix the algorithm's internal randomness.  Before finding the marker, every
answer is zero, so this random seed determines an ordered list containing at
most `q` distinct candidate indices.  Averaged over a uniformly random marker,
success is at most `q/N`.  Therefore some marker has success at most `q/N`, and
no randomized strategy has larger worst-marker success.

### Matching strategy

Choose a uniformly random `q`-subset (or the first `q` entries of a uniformly
random permutation) and query it.  Every fixed marker is included with
probability

```text
binom(N-1,q-1)/binom(N,q)=q/N.
```

This meets the upper bound.  QED.

The producer exhaustively checks the binomial identity for all `N=2,...,10`
and every `q=0,...,N`, covering 63 finite strategy spaces.

## 4. Honest-search separation

To succeed with probability at least `2/3` on every one-marker world, (2)
requires

```text
q >= ceil(2N/3)=ceil(2^(n+1)/3).                    (3)
```

Now declare an honest-search budget of `n^3` semantic probes.  The exact success
is

```text
min(2^n,n^3)/2^n,
```

which tends to zero.  At `n=40` it is below one in a million.  Yet throughout
the family:

- quotient refutation dimension is one;
- witness communication is `n` bits; and
- post-witness verification is one semantic query.

Thus small local refutations can be computationally inaccessible to an honest
prover.  The efficient-search clause is logically independent of the
combinatorial dimension clause.

## 5. Robust witness checking does not solve search

After a candidate marker is supplied, v1.8 independent replication can reduce
the semantic checking error exponentially with the number of registered
copies.  This makes verification robust but does not locate `j`.

The search lower bound already holds with a perfect ideal oracle.  Replacing it
by a noisy oracle cannot invalidate that lower bound unless the new interface
also supplies structured side information or a stronger primitive.

This separates two costs that a characterization must track:

```text
Find(tau): locate a refuting semantic class,
Check(tau,S): verify a supplied refuting class set.
```

The present family has hard `Find` and cheap `Check`.

## 6. Encoding invariance and macro firewall

Permuting atom identifiers preserves dimension one, deterministic search cost
`N`, and randomized value `q/N`.  The release checks 30 explicit cyclic
permutations.

Adding a new atom “some marker exists” is not a benign v2.0 encoding: it changes
`N` semantic classes into a stronger global primitive.  Exact black-box
evaluation of that OR macro still costs `N` queries because the legal zero input
must be distinguished from every marker location.

## 7. Relation to the characterization target

This family does not contradict the typed successor, which explicitly requires
efficient honest refutation search in addition to small quotient dimension and
noise robustness.  It proves that omitting or weakening that condition makes
the proposed sufficiency direction false even in a very simple oracle-relative
family.

A positive characterization must specify:

- what information the honest prover receives;
- its time/query budget relative to task parameter and prover computation;
- whether search is worst-case, average-case, or distributional;
- whether advice, preprocessing, or witness-bearing transcripts are allowed;
- and how semantic noise interacts with search versus checking.

## 8. Computational receipts

The producer certifies 40 exact resource rows through `n=40`, 63 exhaustive
query-subset identities, and 30 encoding permutations.  The clean-room checker
reconstructs every power of two, budget, success/failure fraction, threshold,
subset count, permutation, and parent contract without importing the producer.

## 9. Claim and novelty boundary

The lower bound is classical black-box query complexity under a zero-or-one
promise.  Structure, advice, witness-bearing transcripts, quantum queries, or a
stronger semantic primitive can change it and must be part of the frozen
interface.

Unstructured search lower bounds are standard.  The contribution is the typed
ASMP-3 separation between quotient dimension, honest `Find`, verifier `Check`,
noise amplification, and benign encoding, with exact executable resource
receipts.
