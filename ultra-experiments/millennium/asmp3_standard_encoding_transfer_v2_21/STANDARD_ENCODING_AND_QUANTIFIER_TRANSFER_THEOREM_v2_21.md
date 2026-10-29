# ASMP-3 standard-encoding and quantifier-transfer theorem v2.21

## Status

```text
result = representation-robust full-set undecidability theorem
decision modes = strict FIX and semantic-respecting ADM
parent = ASMP-3 v0.1 through v2.20
external reproductions = 0/2
```

V2.20 proved a `NONHALT` reduction for one registered strict-FIX program
representation. This theorem proves two missing transfer statements:

1. the reduction targets the full membership set under every adequate standard
   effective encoding, not merely a separately named subclass; and
2. the same reduction works under both the `FIX` and `ADM` protocol quantifiers
   so long as verifier information remains the public input, transcript, coins,
   and declared semantic oracle.

## 1. Full standard-encoded decision set

Fix an effective description system `D`. Let `ASMP3-FIX-STD[D]` contain every
valid `D`-description of a uniform canonical strict-FIX family for which there
exist uniform in-interface algorithms and constants `c>0,N` such that every
depth `d>=N` has completeness/soundness gap at least `c`. Invalid codes are
outside the set.

Call `D` adequate when:

1. canonical syntax is decidable;
2. a total computable compiler `C_D(e)` emits the v2.20 bounded-simulation
   parity family for every machine index `e`;
3. decoding `C_D(e)` preserves that family's exact game semantics;
4. membership is extensional under semantics-preserving encodings; and
5. the full decision domain includes every valid compiler output.

These are representation conditions, not membership or decidability
assumptions. Ordinary JSON AST, register-machine IR, and circuit IR descriptions
all satisfy them; the harness supplies canonical compilers and independent
decoders for those three examples.

## 2. Full-set reduction theorem

### Theorem 1

For every adequate `D`, `ASMP3-FIX-STD[D]` is undecidable and its positive index
set is not recursively enumerable.

### Proof

Given machine index `e`, compute `C_D(e)`. Adequacy makes this a valid element
of the full decision domain. By semantic preservation and the v2.20 theorem,

```text
C_D(e) in ASMP3-FIX-STD[D]  iff  e in NONHALT.
```

If the full set had a decider, composition with `C_D` would decide `NONHALT`.
If its positive set were recursively enumerable, enumerating or recognizing
positive compiler outputs would recursively enumerate `NONHALT`. Both are
impossible. QED.

The compiler image is the many-one reduction witness inside the full set. It is
not being substituted for the full set as the theorem's domain. This is the
same reason an undecidability proof for arbitrary programs may use a very simple
syntactic family of programs.

## 3. Encoding invariance

The proof applies separately in every adequate representation; it does not
require a literal byte-for-byte translator between arbitrary encodings. An
encoding change can evade the theorem only by doing at least one of the
following:

- exclude the compiler image from the domain;
- change the decoded game semantics;
- use a non-effective representation of computation; or
- make membership depend on spelling rather than the decoded game.

The first produces a narrower restricted task domain. The second changes a
frozen game. The third is not a standard effective encoding. The fourth
violates benign-encoding invariance. Thus ordinary effective representation
choice cannot restore decidability.

## 4. Universal inactive-interface coupling

The old `FIX`/`ADM` fork does not change the reduction's truth value.

Let `e` halt at time `t`, fix `d>=t`, and choose the uniform opposite-parity
worlds

```text
z_0 = 0^d,
z_1 = 10^(d-1).
```

The ideal semantic oracle is now world-independent zero. Consider any legal
interactive interface and any proposed honest algorithms `P_0^h,P_1^h`.
Construct the following efficient adversarial strategies:

- in world `z_0`, false `P_1` emulates `P_1^h` on `z_1`;
- in world `z_1`, false `P_0` emulates `P_0^h` on `z_0`.

Couple all algorithms' random coins by label. At the beginning, the public
inputs agree. Inductively, if labelled histories agree, the verifier sends the
same labelled challenges, and each labelled prover runs the same algorithm on
the same emulated world and history, producing the same message distribution.
Every adaptive semantic query receives the same ideal zero and can be coupled
to the same `BSC(1/5)` response. Therefore every transcript prefix and the
terminal verifier-output law are identical in the two worlds.

The correct claim label is zero in `z_0` and one in `z_1`. Hence any claimed
positive completeness/soundness gap would require the same output probability
to differ from itself. The optimal gap is zero.

This proof permits arbitrary finite rounds, message alphabets, public/private
coins, stopping decisions, and adaptive query selection. It uses only the
declared verifier-information boundary. Adding a trusted world-dependent
verifier channel would change the semantic environment, not merely select or
re-encode an interface.

## 5. Transfer to FIX and ADM

### Theorem 2

The v2.20 reduction satisfies

```text
membership iff NONHALT
```

in each of the following modes:

- `FIX`, with the vector interface frozen;
- `ADM-singleton`, with `Interfaces(E)={G_vec}`; and
- `ADM-broad`, whenever `Interfaces(E)` contains `G_vec` and every selected
  interface respects the declared verifier-information boundary.

Formally, an adequate ADM encoding has an effective tuple constructor for
declared interface classes. The total wrapper compiler emits either

```text
(E_e, Interfaces(E_e)={G_vec})
```

or a broader effective class containing `G_vec`. These outputs are valid
members of the full `ASMP3-ADM-STD[D]` input domain, not a promise problem
external to it.

### Proof

If `e` never halts, `G_vec` has uniform exact gap `3/5`, so it supplies the
positive protocol in all three modes. If `e` halts, the universal coupling
above makes every sufficiently large depth zero-gap under every legal selected
interface. Thus no `ADM` choice repairs the tail. QED.

## 6. Source-level consequence

V0.1 explicitly:

- asks for standard encodings of computation;
- requires invariance under equivalent encodings;
- says a narrower-subclass theorem is only partial;
- permits undecidability of the associated full uniform decision family as a
  resolution; and
- says changed assumptions require a new version or a reduction.

Under the ordinary standard-effective-encoding and declared-semantic-access
reading, Theorems 1 and 2 therefore satisfy the source's mathematical negative
resolution route for both natural protocol quantifiers.

## 7. Claim boundary

V0.1 also labels itself a definition draft and admits that not every candidate
has a closed formal core. It never supplies literal parser code or a complete
typed information structure. An authority could publish a narrower successor
domain that excludes this compiler image or adds a different trusted input;
that would be a different restricted problem and would need new analysis.

Accordingly, the safe claim is:

> The full standard-encoded ASMP-3 membership problem is internally proved
> undecidable across FIX and semantic-respecting ADM closures. This is a
> parent-level negative-resolution candidate under the source's ordinary
> encoding convention, not prize-grade external acceptance.

The required two independent expert reproductions remain absent.
