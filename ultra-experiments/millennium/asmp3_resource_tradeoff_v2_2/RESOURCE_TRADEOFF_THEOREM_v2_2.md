# ASMP-3 resource-tradeoff theorem v2.2

## Status and scope

```text
result_status = exact unique-marker communication/query frontier
parent_result = ASMP-3-HONEST-SEARCH-BARRIER-v2.1
interface_mode = WV-FIX
protocol = one prover message, then a message-indexed nonadaptive ideal-query set
completeness = perfect on every one-marker input
soundness = perfect on the zero-marker input
changes_parent_problem = false
```

This release gives matching communication and semantic-query lower/upper bounds
for the v2.1 unique-marker family.  It separates the cost of finding the marker,
describing enough information to the verifier, and checking the resulting
candidate set.

## 1. Frozen one-message interface

There are `N` semantic atoms with the zero-or-one-marker promise.  On a
one-marker input, the honest prover sends one message from an alphabet of size
`K`.  Each message determines a nonadaptive set of at most `q` atom indices.
The verifier queries that set and accepts exactly when it finds the marker.

On the legal zero input all queried answers are zero, so this protocol has
perfect soundness.  Perfect completeness requires every possible marker index
to belong to at least one message's query set.

## 2. Sharp covering theorem

### Theorem 1

The minimum message-alphabet size is

```text
K_min(N,q)=ceil(N/q).                                (1)
```

Consequently the minimum fixed-length communication is

```text
b_min(N,q)=ceil(log2 ceil(N/q)).                     (2)
```

### Lower bound

The union of `K` query sets, each of size at most `q`, contains at most `Kq`
indices.  Perfect completeness for all `N` markers requires

```text
Kq>=N.
```

Thus `K>=ceil(N/q)` and (2) follows from binary message capacity.

### Attainment

Partition the `N` marker indices into consecutive blocks of size at most `q`.
The number of blocks is `ceil(N/q)`.  The prover sends the block containing the
marker, and the verifier queries that entire block.  This has perfect
completeness and zero-input soundness, meeting both lower bounds.  QED.

The release represents even the largest partitions by a quotient/remainder
block-size histogram, so the constructive certificate is constant-space rather
than an explicit list of millions of singleton blocks.

## 3. Capacity form and endpoints

Equivalently, `b` communication bits and `q` ideal semantic queries can cover at
most

```text
2^b q
```

marker locations.  The exact admissibility condition is

```text
2^b q >= N.                                         (3)
```

At one verifier query, `b=ceil(log2 N)` bits are necessary and sufficient: send
the marker index.  At `q=N`, no message is needed: the verifier recomputes the
global OR by querying every atom.  Intermediate frontier points continuously
trade communication against verifier work.

For `N=2^n` and power-of-two `q=2^s`, the frontier simplifies to

```text
b+log2(q)=n.
```

## 4. Honest search remains separate

The protocol begins after the prover knows which marker/block to name.  By v2.1,
finding that marker from black-box access has deterministic exact cost `N` and
randomized `q_search`-query maximin success `q_search/N`.

Thus the same family has three independently sharp resources:

```text
honest Find cost:          N queries,
prover-verifier message:   ceil(log2 ceil(N/q)) bits,
verifier Check cost:       q ideal semantic queries.
```

A small post-search message or verifier budget does not make honest search
cheap, and a cheap witness search would not erase the covering lower bound for
this one-message interface.

## 5. Robust noisy-query composition

Replace each of the verifier's `q` ideal candidate queries by a v1.9 majority
block with independent error rate bound `eta`.  If each decoded candidate has
error `e_d(eta)`, the union-safe joint error is at most `q e_d(eta)`.  The
semantic-query charge becomes

```text
q*d.                                                 (4)
```

The release composes four exact operating points for `N=2^20`,
`q in {1,4,16,64}`, `eta=1/5`, and target joint noise risk `1/100`.  It retains
the communication frontier (2) and imports the independently minimized v1.9
replication depth for each `q`.

Noise amplification therefore adds a multiplicative query cost; it does not
alter the ideal covering lower bound or the honest search cost.

## 6. Exhaustive finite audit

For every `N=2,...,8` and every `q=1,...,N`, the producer enumerates all exact
`q`-query subsets.  It verifies that no family of `ceil(N/q)-1` subsets covers
the universe and finds a cover with `ceil(N/q)` subsets.  These 35 cases audit
both sides of (1) without relying on the formula implementation.

The all-parameter registry contains 433 frontier points for `N=2^n`,
`n=1,...,24`, using every power-of-two query budget and several nonpower
budgets.  The clean-room checker independently rebuilds all rows, small covers,
partition histograms, capacities, noisy operating points, and parent contracts.

## 7. Interface firewall

The theorem is exact for the declared one-message, message-indexed,
nonadaptive-query, perfect-completeness/perfect-soundness interface.  Shared
randomness, interaction, bounded error, adaptive semantic queries, variable
length coding, advice, or structured atom geometry can change the achievable
tradeoff and require new lower bounds.

The result is a matching resource theorem for one nontrivial family, not the
universal communication/query/honest-prover lower bound required for a complete
`WV-FIX`/`WV-ADM` characterization.

## 8. Novelty boundary

Set-cover counting and block partitioning are standard.  The contribution is
the exact typed ASMP-3 protocol frontier, joint separation of Find/message/Check
resources, constant-space constructive receipts, exhaustive small-cover audit,
and composition with independently certified semantic-noise replication costs.
