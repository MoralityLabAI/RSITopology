# ASMP-3 encoding-invariance theorem v2.0

## Status and scope

```text
result_status = exact replication-quotient invariance and macro-cost barrier
parent_result = ASMP-3-BLOCK-SELECTION-COMPOSITION-v1.9
interface_mode = WV-FIX
invariant = replication-quotiented local refutation dimension
encoding_class = transcript/class bijections with sound-complete Refute transport
macro_lower_bound = deterministic exact primitive-query complexity of parity
changes_parent_problem = false
```

This release addresses the fifth core obligation in the canonical ASMP-3
statement: benign transcript encodings must not change the proposed refutation
invariant, and a syntactically local atom must not hide uncharged global
verification.

## 1. Quotient refutation object

Let `F` be the false terminal transcripts of a frozen interface.  Let `C` be
semantic-atom equivalence classes after quotienting registered
meaning-preserving replications.  For each `tau in F`, let `W(tau)` be the
nonempty family of finite class sets that soundly and completely refute `tau`.

Define

```text
r(F,C,W)=max_(tau in F) min_(S in W(tau)) |S|.       (1)
```

This is the finite form of the typed successor's `r_(E,G)`.  It counts semantic
classes, not raw aliases or synonymous spellings.

## 2. Exact benign-transport theorem

Consider a second frozen interface `(F',C',W')`.  A benign quotient transport
consists of bijections

```text
Phi:F -> F',
psi:C -> C'
```

such that, for every false transcript and class set,

```text
S in W(tau)  iff  psi(S) in W'(Phi(tau)).            (2)
```

### Theorem 1

Under (2),

```text
r(F,C,W)=r(F',C',W').                               (3)
```

### Proof

For fixed `tau`, `S -> psi(S)` is a size-preserving bijection between the two
refuting-set families.  Their minimum cardinalities are equal.  `Phi` is a
bijection on false transcripts, so taking the maximum preserves that equality.
QED.

The release checks 27 finite hypergraph transports with different transcript
families, class rotations, transcript reversals, and nonuniform alias
multiplicities.  Every minimum and maximum agrees exactly.

## 3. Honest witness-search transport

Suppose an honest search algorithm returns `S in W(tau)`.  The encoded search
algorithm decodes `tau'` with `Phi^-1`, runs the source search, and returns
`psi(S)`.  Soundness/completeness follow from (2), and witness size is unchanged.

If encoding/decoding and class lookup have declared polylogarithmic overhead,
efficient honest search is preserved up to that overhead.  This is constructive:
the harness transports a canonical minimum witness for every registered
transcript and checks membership in the encoded family.

This theorem does not create an efficient source search algorithm; it proves
that a genuinely benign encoding cannot destroy one or manufacture one by
renaming.

## 4. Alias expansion

Give each semantic class one or more raw syntactic aliases.  A raw set refutes
exactly when its projection to semantic classes contains a quotient witness.
Changing alias multiplicities changes the raw alphabet size but not (1).

The producer exhaustively enumerates every raw subset for 14 small expanded
alphabets.  The least raw witness uses one representative from each required
class and equals the quotient minimum.  Merely adding synonyms therefore cannot
improve or worsen the quotient dimension.

An expansion that requires all synonyms, gives one synonym extra semantic
power, or changes which quotient sets refute is not the transport (2).

## 5. The one-macro trap

An interface designer might replace `N` primitive semantic bits by one atom

```text
M(x)=x_1 xor ... xor x_N
```

and then claim refutation dimension one.  This is not a benign encoding:

- `N` old semantic classes do not biject to one new class;
- the refutation hypergraph changes from an `N`-class witness to a singleton;
  and
- exact evaluation of `M` has global primitive-query cost `N`.

The last point is an exact decision-tree lower bound.  Every partial assignment
leaving at least one input unknown has two completions with opposite parity.
Therefore no exact deterministic evaluation leaf can occur before all `N` bits
are queried, and the worst-case query complexity is exactly `N`.

The harness enumerates all `3^N-2^N` nonterminal partial assignments for every
`N=4,...,12`, totaling 788,945 assignments.  It also checks that every bit is
pivotal.  Under the registered local-atom evaluation budget
`ceil(log2(N+1))`, each parity macro costs too much and is rejected.

Short description length alone is therefore insufficient: “parity of the
whole input” is syntactically concise but semantically global to evaluate.

## 6. Resource-preserving encoding rule

A usable ASMP-3 encoding theorem must transport all of the following together:

- terminal transcripts, roles, rounds, stopping, and payoff;
- semantic equivalence classes and registered replications;
- `Refute` soundly and completely;
- atom description, locality, and evaluation resources;
- transcript, query, and verifier computation costs; and
- honest witness-search algorithms.

The quotient equality (3) handles the combinatorial invariant.  Declared
resource distortion handles efficiency.  A transformation failing either part
changes the interface rather than benignly encoding it.

## 7. Computational receipts

The producer supplies ten gates covering:

- 27 complete quotient-hypergraph transports;
- constructive canonical-witness transport;
- nonuniform alias alphabet growth;
- 14 exhaustive raw-alias subset searches;
- nine complete parity partial-assignment registries; and
- parent contracts requiring registered meaning-preserving replication.

The clean-room checker independently reconstructs every hypergraph, map,
minimum, alias subset, partial assignment, pivotal bit, and resource comparison
without importing the producer.

## 8. Claim and remaining boundary

Theorem 1 is an exact finite quotient theorem.  An asymptotic application must
also prove uniform computability and the declared resource overheads of
`Phi`, `Phi^-1`, `psi`, and `psi^-1`.

The parity barrier concerns deterministic exact evaluation on unrestricted
inputs.  Randomized approximation, promises, cached preprocessing, or a
stronger primitive oracle can change query complexity—but those are explicit
interface changes that must be charged.

This release does not yet characterize all `WV-FIX`/`WV-ADM` interfaces, prove
efficient honest refutation search for arbitrary tasks, or establish matching
communication and honest-prover lower bounds.

## 9. Novelty boundary

Invariant transport under isomorphism and parity decision-tree complexity are
standard.  The contribution is their precise typed integration with ASMP-3's
replication quotient, executable refutation-hypergraph receipts, honest-search
transport, alias firewall, and explicit semantic/resource diagnosis of the
one-local-query trap.
