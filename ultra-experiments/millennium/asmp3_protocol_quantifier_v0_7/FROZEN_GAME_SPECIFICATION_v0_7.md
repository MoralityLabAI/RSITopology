# ASMP-3 complete witness-game specification v0.7

## 1. Purpose and scope

This document closes the missing game definition for the ASMP-3 parity
countermodel. It specifies one oracle-relative two-advocate family under two
message-encoding classes:

- `G_fix`, where admissible transcript encodings are frozen game data; and
- `G_admit`, where protocol admission may choose a richer semantic encoding.

The two games share the same task relation, semantic worlds, noise law,
resources, and parties. They differ only in the legal semantic message
alphabet. This isolates the protocol-quantifier ambiguity identified by the
simulated complexity review.

The result is a formal scope fork, not a claim that every ASMP-3 completion must
use this oracle model.

## 2. Parameters and public instance

For every scale parameter `n>=4`, define

```text
d(n) = floor(log2 n),
L(n) = 2^d(n).
```

The public instance is

```text
x = (n, u, s_0, ..., s_(d-1)),
```

where `u in {0,1}^n` is a random-access formal bit string and the `s_i` are
fixed opaque identifiers, independent of the semantic world, for distinct
radius-one semantic atoms. Only the first `L(n)` formal bits enter the relation;
the remaining bits are padding.

With canonical `O(log d)`-bit atom identifiers, the total encoded input length
is

```text
N(n) = n + O(d log d) = Theta(n).
```

This defines the family at every sufficiently large input length scale, not
only powers of two.

The prover computation budget is

```text
T(N) = Theta(N).
```

Because `L(n)>=n/2`, parity of the relevant formal leaves has worst-case query
complexity `Theta(n)`. Also,

```text
d(n) = Theta(log T(N)).
```

## 3. Semantic worlds and party information

A semantic world is `z in {0,1}^d`. The ideal semantic oracle is

```text
H_z(s_i) = z_i.
```

Both advocates receive `(x,z)`. The verifier receives `x`, public randomness,
and query access only to the noisy oracle defined below. Giving both advocates
the same semantic state makes the lower bound stronger than one based on an
ignorant adversary: the dishonest advocate knows the truth and may optimize its
lie.

The correct task output is

```text
a*(x,z)
  = parity(u_0, ..., u_(L-1))
    XOR parity(z_0, ..., z_(d-1)).
```

Equivalently, the oracle-relative decision relation contains exactly
`(x,z,a*(x,z))`.

## 4. Noise and registered replications

Before interaction, independently sample

```text
E_i ~ Bernoulli(1/5),  i=0,...,d-1.
```

Every registered replication of `s_i` returns

```text
H_tilde_z(s_i) = z_i XOR E_i.
```

The same `E_i` is reused on every repeated or adaptive query to atom `i`.
Different atoms have independent latent errors. There are no other adaptive
noise choices. This singleton law is the complete registered
correlation/adaptivity class.

For every positive replication count `k`, returning the first response has
error `1/5`. Hence

```text
a_H(k) <= 1/5 = 1/2 - 3/10.
```

## 5. Common syntax and canonical serialization

Advocates occupy fixed slots `P_0` and `P_1`, labelled by their semantic parity
claims. Initial messages are canonical fixed-width encodings of

```text
(claimed output y, claimed formal root f, claimed semantic parity p),
```

subject to the syntactic identity `y=f XOR p`. In a semantic dispute `P_0`
claims `p=0` and `P_1` claims `p=1`. The honest role switches with the true
semantic parity; party labels and serialized bytes do not.

Variable padding, alternate integer spellings, reordered sets, unused fields,
timing channels, and optional aliases are inadmissible. An abort, out-of-range
integer, wrong-length message, noncanonical serialization, or failure of
`y=f XOR p` makes the responsible advocate lose formally. If both advocates are
simultaneously malformed, the verifier uses a fixed public tie rule independent
of `z`.

Messages are simultaneous within a round. The verifier reveals no noisy
semantic response to either advocate. Public coins are sampled independently of
`z` and the latent errors.

The frozen resource bounds are

```text
semantic-query budget q(N) = d^2,
verifier-time budget s(N) = 64 d^2 bit/word operations,
transcript budget B(N) = 18 d^2 bits.
```

The constants only make the game total and checkable. Both legal encodings
below fit these bounds, and all three resources are `polylog(T(N))`.

## 6. Formal-disagreement branch

If the advocates' formal-root claims differ, the verifier runs deterministic
binary bisection on the complete `L`-leaf XOR tree.

At a disputed internal node, each advocate sends its two claimed child values.
A pair whose XOR differs from that advocate's parent claim loses formally.
When both pairs are locally consistent and the parent claims differ, exactly
one child claim differs; the verifier descends to that unique child. At a leaf,
the claimed value is compared with the public bit `u_j`. A false formal root
therefore ends in either a local XOR inconsistency or a public-leaf mismatch in
exactly `d` rounds.

The honest advocate computes the complete formal parity tree in `Theta(n)` time
and thereafter answers each formal round in constant time.

## 7. Frozen semantic branch `G_fix`

If formal-root claims agree and semantic-parity claims differ, the only legal
semantic refutation message is the explicit sorted list

```text
S = (0,1,...,d-1).
```

Each index uses `ceil(log2 d)` bits, with a unique length prefix. No per-atom
truth-value claim is a legal message. After receiving the canonical list, the
verifier may query atoms adaptively, repeat any atom, and stop according to any
randomized rule within the frozen `d^2` query and `64d^2` time budgets. There are no further
prover messages.

The complete non-oracle transcript is identical under the uniform even- and
odd-parity semantic-world priors:

- `P_0` always claims parity zero;
- `P_1` always claims parity one;
- both use the same formal root and canonical set encoding; and
- only the honest-role label changes, which is not shown to the verifier.

Every adaptive oracle transcript is a Markov kernel of the full persistent
answer vector

```text
Y = z XOR E
```

and independent public randomness. Data processing therefore bounds its
even/odd total variation by the total variation of `Y`.

## 8. Extended semantic branch `G_admit`

`G_admit` adds one legal semantic message: each advocate may send a canonical
vector `v in {0,1}^d`, and its claimed semantic parity must equal `parity(v)`.

The verifier compares the vectors. Opposite parity implies at least one
differing coordinate. It chooses the least differing index `j`, queries
`H_tilde_z(s_j)` once, and selects the advocate whose vector agrees with the
response. If vectors do not match their parity claims, the responsible advocate
loses formally.

An honest advocate sends `v=z`. Against every opposite-parity vector, the
verifier selects the honest advocate with probability `4/5` and the dishonest
advocate with probability `1/5`. Thus

```text
completeness - soundness = 3/5.
```

The two vectors cost `2d` bits, the verifier uses one semantic query, and both
message and verifier costs are `O(d)=O(log T(n))`.

## 9. Terminal transcripts and `Refute`

A terminal accused transcript is false if it is syntactically malformed or any
of its output, formal-root, or semantic-parity claims is false. This convention
is at least as inclusive as treating only a wrong task output as false.

For a syntactically valid XOR decomposition with false output, exactly one
component claim is false:

```text
(f != true formal root) XOR (p != true semantic parity) = 1.
```

Define

```text
Refute(tau,S,b) =
  [tau is malformed or aborted]
  OR
  [the formal branch contains a local XOR inconsistency or leaf mismatch]
  OR
  [the semantic branch is terminal,
   S=(0,...,d-1),
   and parity(b) contradicts the accused parity claim].
```

If the task output is correct while both component claims are false, the formal
clause already gives an empty-`S` refutation. The first two clauses use
`S=empty`. Every remaining false semantic claim is refuted by all `d` atoms. No
strict subset suffices: if index `j` is omitted, flipping only the unseen bit
produces a completion consistent with the queried answers and the accused
parity. Therefore every false terminal transcript has a finite refutation and

```text
r_R(N) = d(n) = Theta(log T(N)).
```

## 10. Uniform honest strategy

The honest advocate:

1. computes the formal XOR tree and `a*(x,z)` in `Theta(n)` time;
2. sends the truthful canonical initial claim;
3. answers formal bisection from the stored tree; or
4. emits the sorted all-indices semantic set.

For every realized deterministic move sequence of an adaptive or randomized
dishonest strategy:

- malformed messages or aborts lose syntactically;
- a false formal root is localized to an inconsistency or public leaf; and
- a false semantic parity is refuted by the fixed `d`-atom set.

The proof is pointwise in the dishonest strategy's coins and therefore covers
randomized strategies. The semantic list costs `O(d log d)` bits and `O(d)`
word-RAM operations. Total honest work remains `Theta(n)`.

## 11. Payoff and gap

For the semantic least-favourable experiment, hold the public instance and
formal transcript fixed. Let `A` be the probability that a verifier selects
`P_1`.

A uniform completeness/soundness gap `Delta` requires

```text
E_odd[A] >= completeness,
E_even[A] <= soundness,
Delta = completeness - soundness.
```

Uniformly averaging over even and odd semantic worlds preserves these
inequalities. In `G_fix`,

```text
Delta
 <= TV(P_even^transcript, P_odd^transcript)
 <= TV(P_even^Y, P_odd^Y)
 = (3/5)^d
 -> 0.
```

Querying all atoms and selecting by observed parity attains equality for every
semantic world, so this is the exact minimax gap.

In `G_admit`, the vector-disagreement protocol gives the constant gap `3/5`.

## 12. Resource ledger

| Object | Cost |
| --- | --- |
| Prover computation | `Theta(N)=T(N)` |
| Formal rounds | `d=Theta(log T)` |
| Frozen semantic set | `O(d log d)` bits |
| Extended vectors | `2d` bits |
| Extended semantic queries | one |
| Frozen semantic-query budget | `d^2`; querying all `d` atoms attains the minimax rule |
| Verifier time | at most `64d^2=polylog(T)` |
| Transcript budget | `18d^2` bits |
| Atom description | `O(log d)` bits |
| Atom ideal evaluation | one ideal-oracle lookup |
| Atom locality | radius one |

No atom contains the semantic parity or full task output because `d>=2`.

## 13. Claim boundary

This specification removes the incomplete-game objection for this witness and
makes the protocol-quantifier fork exact. It does not decide whether v0.1
intended `G_fix` or `G_admit`, nor does it supply a positive characterization of
all weakly verifiable tasks.
