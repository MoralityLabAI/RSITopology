# ASMP-3 constructive refutation protocol theorem v2.3

## Status and scope

```text
result_status = constructive positive protocol under typed finder/noise contracts
parent_result = ASMP-3-RESOURCE-TRADEOFF-v2.2
interface_mode = WV-FIX
protocol = advocate transcript, critic quotient witness, fresh replicated checks
changes_parent_problem = false
```

This release connects the previously separate dimension, honest-search,
semantic-noise, encoding, and resource results into a positive weak-verification
theorem for a restricted but nontrivial class of frozen interfaces.

It is a sufficient theorem under explicit operational contracts, not a complete
`WV-FIX` or `WV-ADM` characterization.

## 1. Positive-class contracts

Fix a uniform family `(E_n,G_n)` with:

1. **Sound-complete quotient refutation.** `Refute_n(tau,S,b)` is decidable,
   sound on true admissible transcripts, and every false admissible transcript
   has a quotient witness `S` of at most `r_n` semantic classes.
2. **Uniform honest finder.** For every false transcript—including transcripts
   chosen adaptively or obfuscated by a legal advocate—`Find_n(tau)` returns such
   a witness and its ideal answer vector within declared time `H_n`.
3. **Registered atom encoding.** Atom IDs, answer bits, witness serialization,
   and benign replication classes obey the v2.0 resource/encoding contract.
4. **Fresh block-independent noise.** Only after `(tau,S)` is fixed, each class
   in `S` receives a fresh disjoint block of `d` meaning-preserving replicas.
   Within and across blocks, errors are conditionally iid with adversarial rate
   `p<=eta<1/2`.

Malformed critic messages are ignored, so they cannot make a true advocate lose.

## 2. Protocol

1. The advocate submits its candidate output and admissible transcript `tau`.
2. The critic either declines or submits `(S,b)=Find_n(tau)` in canonical
   quotient serialization.
3. For every class in `S`, the verifier asks `d` fresh replicas and decodes by
   majority with uniform tie breaking.
4. The verifier rejects the advocate exactly when `Refute_n` accepts the decoded
   witness; otherwise it accepts.

The message order, malformed behavior, noise timing, and payoff are fixed before
the strategic roles act.

## 3. Exact noise event

Let `e_d(eta)` be the v1.8 worst-rate majority error for one block.  With at most
`r` disjoint independent blocks, the probability that any decoded atom is wrong
is at most

```text
delta_(r,d,eta)=1-(1-e_d(eta))^r.                  (1)
```

This is the exact v1.9 block-union probability when the witness has size `r`.
For smaller witnesses it is a valid monotone upper bound.

Sampling only after `(tau,S)` is finalized is essential.  It prevents the
selection inflation demonstrated by v1.9; an adaptive advocate can choose a
difficult transcript, but cannot inspect and select among already realized
replication errors.

## 4. Completeness and soundness theorem

### Theorem 1

Under the four contracts, the protocol has

```text
completeness >= 1-delta_(r,d,eta),
soundness    <= delta_(r,d,eta),
gap          >= 1-2delta_(r,d,eta).                (2)
```

### Completeness

Suppose the advocate transcript is true.  By soundness of `Refute`, no critic
witness with the correct ideal atom answers can refute it.  Therefore the
advocate is accepted whenever every queried block decodes correctly.  A false
rejection is contained in the event (1), proving the completeness bound against
every critic strategy.

### Soundness

Suppose the advocate transcript is false.  The uniform finder returns a valid
witness despite the advocate's legal obfuscation.  By completeness of `Refute`,
the verifier rejects whenever every block decodes correctly.  False acceptance
is contained in (1), proving the soundness bound for the honest critic against
every legal advocate transcript.  QED.

This is the standard two-role completeness/soundness quantifier: one honest role
must possess the declared efficient strategy in each direction; it does not
assume both strategic roles cooperate.

## 5. Exact replication choice

For target protocol error `epsilon<1/2`, choose the least odd `d` satisfying

```text
1-(1-e_d(eta))^r <= epsilon.                        (3)
```

The release independently minimizes `d` for 42 combinations:

- `eta in {1/5,1/3,2/5}`;
- `r in {1,2,4,8,16,32,64}`; and
- `epsilon in {1/10,1/100}`.

Each receipt records the previous odd depth and checks that it fails (3).  The
resulting gap is at least `1-2epsilon`, hence at least `4/5` or `49/50` in the
two target lanes.

## 6. Charged resources

For `L`-bit atom identifiers, the registered implementation charges:

```text
semantic queries = r*d,
critic message   = ceil(log2(r+1)) + r(L+1) bits,
finder time      = H <= rL in the direct-index registered lane,
verifier work    = decoding r blocks plus the declared Refute computation.
```

The `r(L+1)` term serializes each atom ID and its claimed ideal answer.  The
length prefix prevents ambiguous parsing.  Other interfaces may use different
encodings, but v2.0 requires them to transport resources explicitly.

The scaling audit sets `log2(T)=L=r`, `eta=1/5`, and target error `1/L`.  For
`L=10,20,...,100`, the independently minimized query count, critic message, and
registered finder time all fit within `L^3=polylog(T)` while the gap tends to
one.  These finite receipts illustrate the uniform asymptotic formula; they do
not replace proof that a concrete task family satisfies the finder contract.

## 7. Why every contract is material

The preceding releases supply explicit kill cases:

- v2.0: an uncharged macro can fake dimension one unless semantic classes and
  evaluation cost are transported;
- v2.1: dimension one and cheap checking do not imply efficient honest search;
- v2.2: communication and verifier queries obey an independent sharp frontier;
- v1.8/v1.9: marginal accuracy does not imply block independence, and selection
  can amplify error unless fresh conditional blocks are specified.

Thus Theorem 1 does not merely list convenient assumptions.  Removing each one
invalidates a step of the construction on a certified family.

## 8. Relation to adaptive and obfuscating provers

The advocate may adaptively produce any transcript allowed by `G_n`.  Uniformity
of `Find_n` over every false admissible transcript is exactly what supplies
soundness against obfuscation.  If `Find_n` is only average-case, only works on
canonical traces, or receives uncharged side information, Theorem 1 does not
apply.

Likewise, fresh noise is conditional on the completed history and selected
witness.  If the advocate or critic can inspect candidate noise blocks before
selection, the v1.9 selection bound—not the one-witness bound—must be charged.

## 9. Completion boundary

This theorem establishes a constructive positive direction for one typed
refutation-protocol class.  It does not prove:

- that every `(E,G) in WV-FIX` has such a finder/refutation normal form;
- a converse showing these contracts are necessary for all protocols;
- an optimizer or attained infimum over `WV-ADM` interfaces;
- universal communication/honest-prover lower bounds; or
- the normative FIX-versus-ADM interpretation of v0.1.

Those are the remaining steps toward a complete characterization.

## 10. Novelty boundary

Witness checking, majority amplification, and union bounds are standard.  The
contribution is the fully typed ASMP-3 protocol composition: uniform honest
search, quotient encoding, post-selection noise, strategic quantifiers, exact
rational gap receipts, and end-to-end resource accounting tied to independently
certified obstruction families.
