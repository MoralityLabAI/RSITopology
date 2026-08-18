# ASMP-3 typed successor draft v0.2

## Status

```text
document_status = nonnormative_successor_draft
parent = ASMP-CANDIDATE-SET-v0.1 / ASMP-3
changes_parent_problem = false
motivation = exact protocol-quantifier fork v0.7
```

This draft does not amend v0.1. It supplies the missing type signatures needed
for a future problem version and separates two inequivalent questions that
v0.1 currently compresses into the phrase “admits a protocol.”

## 1. Typed semantic task environment

For each input length `n`, a semantic task environment is

```text
E_n = (
  X_n, W_n, Y_n, R_n,
  A_n, Rep_n,
  H_n, Noise_n,
  InfoP_n, InfoV_n,
  T_n
).
```

The fields mean:

- `X_n`: public instances;
- `W_n`: semantic worlds or hidden specifications;
- `Y_n`: task outputs;
- `R_n subseteq X_n x W_n x Y_n`: the frozen decision relation;
- `A_n(x)`: legal semantic atoms for an instance;
- `Rep_n`: registered meaning-preserving replications;
- `H_n(w,a)`: the ideal semantic answer;
- `Noise_n`: the complete legal response-process class, including correlation
  and adaptivity;
- `InfoP_n`: information given to each prover role;
- `InfoV_n`: information and oracle access given to the verifier; and
- `T_n`: prover computation budget.

Atom description length, locality radius, ideal evaluation cost, and
replication equivalence are properties of `E_n`. They are not inferred from a
protocol's spelling.

## 2. Typed fixed game interface

A fixed game interface is

```text
G_n = (
  M_n, Enc_n,
  Order_n, Stop_n,
  Coins_n,
  Budget_n,
  Malformed_n,
  Payoff_n,
  Refute_n
).
```

Here:

- `M_n` is the legal message alphabet by role and round;
- `Enc_n` is a canonical serialization with no optional padding or aliases;
- `Order_n` and `Stop_n` define the public-coin round machine;
- `Coins_n` declares all public and private randomness;
- `Budget_n=(s_n,q_n,B_n)` gives verifier time, semantic queries, and transcript
  bits;
- `Malformed_n` gives total behavior for aborts and invalid messages;
- `Payoff_n` defines completeness and soundness; and
- `Refute_n` is a decidable terminal-transcript relation.

`Refute_n` must satisfy declared adequacy axioms:

1. **soundness:** a recognized refutation cannot refute a truthful terminal
   claim under ideal answers;
2. **coverage:** every false terminal claim has a finite recognized refutation;
3. **binding:** any semantic rejection or advocate selection attributed to a
   local refutation must use the declared relation; and
4. **replication quotient:** meaning-preserving registered copies do not change
   dimension merely by being duplicated.

The exact quotient rule is part of the future version and must be decidable on
registered atom equivalence classes.

## 3. Typed protocol

For fixed `(E_n,G_n)`, a protocol is a tuple of algorithms

```text
Pi_n = (P_honest,n, P_adversarial,n, V_n)
```

that operate only inside `G_n`. The algorithms may choose messages and
randomized strategies; they may not enlarge `M_n`, change `Enc_n`, add rounds,
replace `Refute_n`, or alter budgets.

For an environment without a fixed interface, an admissible protocol package is

```text
Q_n = (G_n, Pi_n),
```

where `G_n` is selected from a prospectively declared interface class
`Interfaces(E_n)`.

This distinction creates two separate complexity classes.

## 4. Fixed-interface weak verification

Define

```text
WV-FIX(E,G)
```

to hold when a uniform family of verifier/honest-prover algorithms inside the
fixed game interface has:

- prover computation at most `T_n`;
- verifier, semantic-query, and transcript costs `polylog(T_n)`;
- a constant completeness/soundness gap against every legal efficient
  adversarial strategy; and
- the declared noise robustness uniformly over `Noise_n`.

For this class, the local refutation dimension is well typed:

```text
r_(E,G)(n)
  = max_(false terminal tau in G_n)
    min{|[S]_Rep| :
        Refute_n(tau,S,H_n restricted to S)}.
```

The size counts replication-equivalence classes, not raw synonymous spellings.

The v0.7 frozen parity witness is a candidate counterexample to any theorem
claiming that the three v0.1 displayed conditions suffice for `WV-FIX`.

## 5. Protocol-existential weak verification

Define

```text
WV-ADM(E,Interfaces)
```

to hold when there exists a uniform admissible package

```text
Q_n=(G_n,Pi_n),  G_n in Interfaces(E_n),
```

with the same constant-gap and resource requirements.

An arbitrary `Refute` relation attached outside the existential protocol cannot
be a necessary invariant of this class. Any characterization must instead use
one of:

```text
protocol-relative dimension:
  r_(E,G)(n);

best-interface dimension:
  r*_E(n) = inf_(G in Interfaces(E_n), adequate Refute_G) r_(E,G)(n);

or an operational invariant proved equivalent to protocol admission.
```

The future problem version must select one and specify whether the infimum is
effective and attained. It may not mix `WV-ADM` on the left side with a
syntactic dimension from an unrelated interface on the right.

The v0.7 vector-disagreement protocol proves that the parity witness belongs to
`WV-ADM` when vector messages are in `Interfaces(E_n)`.

## 6. Joint semantic-noise profile

The v0.1 single-atom profile `a_H(k)` is retained as a marginal diagnostic but
is not sufficient for a growing refutation predicate.

For a fixed `(E,G,Pi)`, define a transcript-conditional joint risk

```text
J_(E,G,Pi)(n)
  = sup_(legal adversarial strategy D)
    sup_(legal noise process nu in Noise_n)
    Pr[the verifier selects a false output
       on the refutation selected by the interaction].
```

The probability includes:

- adversarial selection of the transcript and refuting set;
- conditional noise after the selected history;
- all registered replications;
- adaptive query order and stopping; and
- the full joint Boolean decision rule used by `Refute`.

A positive characterization must control this joint risk, or an equivalent
selection-conditional advantage, by a constant below `1/2`. A bound on each
atom separately is insufficient.

For compositional theorems, a more local functional version may be registered:

```text
Risk_Noise(F,tau,S,q)
  = inf_(q-query decision rules A)
    sup_(nu legal after tau)
    Pr[A != F(H_n restricted to S)].
```

The theorem must state how this quantity composes over adaptively selected
terminal transcripts.

## 7. Revised characterization targets

The successor should pose two explicit targets rather than one ambiguous iff.

### Target FIX

Characterize exactly the pairs `(E,G)` in `WV-FIX`, using:

- adequate replication-quotiented `Refute`;
- efficient honest refutation search;
- a joint transcript-conditional noise invariant; and
- matching communication, query, honest-prover, and noise lower bounds.

### Target ADM

Characterize exactly the environments `E` in `WV-ADM(E,Interfaces)`, including:

- the declared admissible interface class;
- the cost of choosing/serializing an interface;
- a protocol-relative or optimized refutation invariant;
- a constructive interface and protocol; and
- lower bounds uniform over all admissible interfaces.

Neither target may infer a positive result from single-atom accuracy alone.

## 8. Encoding invariance

A benign encoding transformation is a polynomial-time bijection between
canonical transcripts that:

- preserves roles, rounds, stopping, and payoff;
- preserves semantic atom equivalence classes;
- changes every resource by at most a declared polylogarithmic factor; and
- transports `Refute` soundly and completely.

A characterization invariant must be unchanged up to the declared resource
equivalence under such transformations. Adding `m` synonymous raw atoms does
not multiply dimension after quotienting.

Changing the legal semantic content—such as adding a per-atom truth vector to a
parity-only alphabet—is not a benign encoding. It changes `G` and is exactly the
difference between the v0.7 FIX and ADM branches.

## 9. Resolution obligations

A complete successor resolution must:

1. identify whether it resolves FIX, ADM, or both;
2. state every uniformity and asymptotic quantifier;
3. give a constructive protocol for every positive direction;
4. prove soundness against adaptive and obfuscating provers;
5. prove matching resource and honest-prover lower bounds;
6. prove a robust joint-noise theorem;
7. prove replication and benign-encoding invariance;
8. retain nontrivial honest work and nonzero legal noise; and
9. satisfy the existing public-proof, certified-arithmetic, independent-checker,
   and two-team reproduction rules.

## 10. Disposition of the v0.1 fork

This draft does not decide v0.1 authorial intent:

- if v0.1 meant FIX, the frozen v0.7 branch is a negative-resolution candidate
  for the displayed sufficiency criterion;
- if v0.1 meant ADM, the vector protocol defeats that candidate; and
- if no interpretation is authoritative, v0.1 remains definitionally unclosed
  and this typed split is the appropriate successor repair.

## 11. Claim boundary

This is a nonnormative problem-definition draft. It closes no prize gate,
changes no parent quantifier, and does not claim a complete characterization.
Its purpose is to ensure the next mathematical claim has one typed truth
condition.
