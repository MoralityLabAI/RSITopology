# ASMP-3 strict-FIX uniform-membership undecidability theorem v2.20

## Status and scope

```text
result_status = exact computability theorem for a registered strict-FIX class
class = WV-FIX-UCOMP
parent = ASMP-3 v0.1, interpreted through the conservative fixed-interface lane
unconditional_parent_resolution = false
```

This theorem closes a previously missing uniform-computability lane. It does
not retroactively repair the v2.18 semantic argument and does not claim that
ASMP-3 itself is impossible. Its parent-level force depends on whether the
unspecified task-family representation in v0.1 includes arbitrary computable
uniform generators.

## 1. Registered uniform decision class

`WV-FIX-UCOMP` instances are indices of total programs that generate, uniformly
in depth `d >= 2`, a semantic task environment and a strict fixed game
interface. A protocol consists of uniform randomized advocate and verifier
algorithms operating only inside that interface. It cannot add messages,
rounds, queries, or encodings.

An indexed family is in `WV-FIX-UCOMP` when there are such algorithms and
constants `c > 0` and `N` for which every `d >= N` has
completeness/soundness gap at least `c`, uniformly over legal adversaries and
the registered noise law. Finite prefixes are ignored, as in ordinary
asymptotic complexity classes.

This is a conservative successor formalization of strict `FIX`. V0.1 asks for
a formal class and permits undecidability of the associated frozen uniform
decision family as a negative resolution, but it does not state an encoding
grammar for inputs to that decision problem.

## 2. The reduction family

Fix a Turing-machine index `e`. At depth `d`:

- the hidden semantic world is `z in {0,1}^d`;
- the required output is `parity(z)`;
- both claim-labelled advocates observe `z`, while the verifier does not;
- advocate `P_b` must send one `d`-bit vector of parity `b`;
- the simultaneous labelled vectors are the entire prover-message interface;
- the verifier may make one coordinate query `a_i`;
- the ideal oracle is

  ```text
  H_(e,d)(z,i) = z_i,  if e has not halted within d steps;
                 0,    otherwise;
  ```

- the response passes through a completely specified `BSC(1/5)`; and
- the verifier must choose one of the two claim labels.

The `e,d` halting test is bounded, so this is a total computable game
generator. The interface is fixed before protocol algorithms are chosen.

The exhibited verifier queries the first coordinate at which the two vectors
differ and chooses the claimant whose vector agrees with the noisy response.
The honest claimant sends `z`. Malformed messages lose.

Set `T(d)=2^(d+4)`. Each advocate sends `d` bits, the complete terminal record
uses

```text
2d + ceil(log2 d) + 1
```

bits, the verifier uses one semantic query and `O(d)` time, and the honest
strategy uses `O(d)` time. All are `polylog(T(d))`, and honest work is nonzero.

Each registered atom reveals only one coordinate. For every `d >= 2`, every
coordinate `i`, and each bit value, there are worlds of both parities having
that coordinate value. Thus no atom is a disguised full-answer query.

## 3. Exact value while the machine is active

Suppose `e` has not halted within `d` steps. Let the labelled messages be
`z_0` of even parity and `z_1` of odd parity, and let `i` be their first
difference. Their bits at `i` are opposite.

If `z_b` is the true world, its claim-labelled advocate can send `z_b`. The
first-difference verifier selects it with probability `4/5`; it selects the
opposite claimant with probability `1/5`. Hence the protocol has gap `3/5`
against every opposite-parity vector.

This gap is optimal over every legal protocol in the fixed interface. Consider
arbitrary honest algorithms `h_0,h_1` and any even/odd world pair `z_0,z_1`.
In world `z_0`, let the false `P_1` sample the message distribution
`h_1(z_1)`; in world `z_1`, let the false `P_0` sample `h_0(z_0)`. Coupling
coins gives the same labelled message distribution
`(h_0(z_0),h_1(z_1))` in both worlds. These are efficient legal adversarial
strategies because the paired worlds can be fixed in their code.

Condition on any messages and verifier coins. Whatever coordinate the
verifier queries, the two ideal answers are either equal or opposite. The two
noisy response laws therefore have total-variation distance either zero or
exactly `3/5`. Mixture convexity and data processing bound the difference of
any verifier's selection probabilities by `3/5`.

Therefore the exact depth-`d` fixed-interface value is

```text
gamma_d = 3/5.
```

## 4. Exact value after the machine halts

Suppose `e` halts at time `t` and `d >= t`. Then the ideal answer is zero for
every world and coordinate. For an arbitrary protocol, pair any even world
`z_0` with any odd world `z_1` and use the same honest-message coupling as in
the active upper bound.

The complete verifier observation law is now identical: same public input,
same labelled messages, same query policy as a function of the observed
history, and the same world-independent noisy response process. Correctness
requires opposite labels in the paired worlds. Thus the probability of
selecting label zero is equal in the true-zero and false-zero cases, so no
legal verifier can have positive uniform gap. A world-independent randomized
choice attains gap zero.

Therefore

```text
gamma_d = 0  for every d >= t.
```

This is a universal coupling bound over legal protocols, not an evaluation of
only the exhibited first-difference verifier.

## 5. NONHALT reduction

Let `G_e` denote the uniform family generated from `e`.

- If `e` never halts, every depth is active and the exhibited uniform protocol
  has exact gap `3/5`.
- If `e` halts at time `t`, every depth `d >= t` has exact value zero, so no
  constants `c > 0,N` can witness membership.

Consequently,

```text
G_e is in WV-FIX-UCOMP  iff  e is in NONHALT.
```

The mapping `e -> G_e` is total and computable. A total membership decider for
`WV-FIX-UCOMP` would therefore decide `NONHALT` (and, by complementation,
`HALT`), which is impossible.

Because `NONHALT` is not recursively enumerable, the positive index set of
`WV-FIX-UCOMP` is not recursively enumerable either. In particular there
cannot be sound-and-complete finite positive certificates with a computable
checker. There also cannot be a computable complete invariant whose membership
predicate is decidable.

## 6. Sharp finite/uniform boundary

No individual finite game is made mysterious by the reduction. Given `e,d`,
simulate `e` for `d` steps. The exact value is then either `3/5` or zero, with
the total-variation certificates above. More generally, the v0.8--v1.3 chain
decides supplied finite rational terminal games through convex-hull TV and
sequence form.

The obstruction is the asymptotic quantifier over an arbitrary program-coded
family:

```text
exists c>0,N  forall d>=N: gamma_d >= c.
```

Finite exact solvability and uniform membership undecidability therefore
coexist without contradiction.

## 7. Claim boundary

The theorem establishes an undecidable index set for the registered
`WV-FIX-UCOMP` representation while retaining:

- a strict interface fixed before the protocol;
- efficient honest strategies in the positive cases;
- one local semantic atom per query;
- nonzero, fully specified noise;
- polylogarithmic verifier, query, and transcript resources; and
- exact per-depth upper and lower bounds.

It is a candidate negative resolution of ASMP-3 only if v0.1's “associated
frozen uniform decision family” ranges over arbitrary computable task-family
generators of this kind. V0.1 never freezes that representation grammar. The
theorem also does not exclude a noncomputable mathematical characterization,
does not satisfy the five positive-resolution deliverables for the unrestricted
class, and has not received the required external reproductions.
