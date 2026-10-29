# ASMP-4 v0.6 adaptive-grammar proof audit

## Scope

This audit covers Theorem 6 only: finite and infinite read/write regions for a
finite nonblocking mode graph, a unique safe-action partition, a prescribed
nonempty initial belief, and a finite registered grammar of sensor partitions.

## Timing ledger

At each stage:

1. the complete public transcript determines the pre-read belief `B`;
2. the sensor chooses a registered partition using that public history;
3. the actual mode selects one nonempty cell `C` of the partition on `B`;
4. safety requires the unique action map `g` to be constant on `C`;
5. the controller emits that action; and
6. the disturbance chooses the next mode from the union of graph successors of
   modes in `C`, producing the next pre-read belief `Succ(C)`.

The partition is selected before the current cell is known. This is why the
minimum is outside the sum in the Bellman recurrence.

## Finite Bellman obligation

Set `V_0(B)=1`. For a safe partition, distinct realized cells are distinct
children of the current read-tree node. Their continuation languages have
different one-symbol prefixes, so their cardinalities add. The future depends
on a cell only through `Succ(C)`. Therefore

~~~text
V_(t+1)(B) = min_P sum_C V_t(Succ(C)).
~~~

Induction gives both the lower bound and a causal tree attaining it. The sensor
history fixes the current action, so transmitting that action gives exactly
the required-action language on the write port. Distinct required action words
cannot share one deterministic write word. Hence the finite rectangle is
jointly exact.

## Infinite viability obligation

Let `K_0` be all nonempty beliefs and

~~~text
K_(r+1) = {B in K_r : some safe P at B has every Succ(C) in K_r}.
~~~

The sequence stabilizes at the greatest fixed point `K_infinity` after at most
`N` strict deletions, where `N` is the number of nonempty beliefs. Membership in
`K_r` is equivalent to existence of an `r`-step safe continuation. Thus an
infinite safe policy exists from `I` exactly when `I in K_infinity`.

Let `W_T` be the finite Bellman value restricted to actions that remain in
`K_infinity`. Any unrestricted length-`T` safe tree must remain in
`K_infinity` during its first `T-N` levels; otherwise People can choose a
successor with fewer than `N` safe stages remaining and terminate the tree
before horizon `T`. Truncating at depth `T-N` gives a viable read tree, and
every truncated prefix has a complete descendant. Conversely every viable
tree is an unrestricted finite tree. Therefore

~~~text
W_(T-N)(I) <= V_T(I) <= W_T(I).
~~~

The bounded tail cannot change an exponential language-growth rate.

## Entropy-game reduction obligation

On `K_infinity`, use:

| Sensor problem | Extended entropy game |
| --- | --- |
| pre-read belief | prescribed game state |
| safe registered partition | minimizing action |
| nonempty current cell | People’s nondeterministic branch |
| `Succ(C)` | next game state |
| number of cells with the same successor | integer transition weight |

For a stationary belief policy `pi`, the weighted adjacency matrix is exactly

~~~text
A_pi[B,B'] = #{C : Succ(C)=B'}.
~~~

Its length-`T` read count from `I` is `e_I^transpose A_pi^T 1`. The prescribed-
initial-state operator theorem cited in `PRIOR_ART_AUDIT_v0_6.md` supplies an
optimal positional policy and identifies its value with
`lim_T W_T(I)^(1/T)`. The bounded-tail sandwich transfers the result to the
unrestricted finite values `V_T`.

## Two-port conclusion

Let `rho_I` be the optimal stationary read growth factor and `h_g` the required-
action language entropy. Every infinite safe code has read rate at least
`log2 rho_I` and write rate at least `h_g`. The optimal stationary sensor
policy and direct action emission attain both simultaneously, yielding

~~~text
[log2 rho_I,infinity) x [h_g,infinity).
~~~

## Harness findings

- The strongly connected, aperiodic fixture has viable beliefs with masks
  `1,2,3,4,5`, initial mask `5`, stationary reachable matrix
  `[[0,1],[1,1]]`, and exact Fibonacci growth.
- Central and import-independent implementations agree on all 120,050 bounded
  three-mode cases.
- All 99,524 horizon-four feasible cases are also infinitely viable; there are
  no finite-only cases in that universe.
- No case violates the required-action lower bound or the dominance of an
  adaptive grammar over its fixed members.
- Central and independent canonical-source audits agree on eight explicit
  architecture clauses, zero sensor-closure selection clauses, and disposition
  `registration_class_underdetermined`.
- Both audit paths reject all 13 decision-reversing source and witness
  mutations.
- Central and independent registry-model builders verify 13 of 13 canonical
  obligations for both code domains and derive distinct exact regions without
  asserted compliance flags.
- A whole-document audit finds 31 uses of `registered`, zero definitions of
  the causal-code domain, and no normative repair in the non-normative machine
  index.
- The complete 32,767-registry lattice has the exact histogram
  `2047/16384/12288/2048`; all 245,760 cover edges are monotone and 26,624 are
  strict in two independent implementations.
- The general Stirling/Bell registry formula agrees with direct safe-partition
  enumeration for all 18 action shapes and 75 action partitions through five
  modes, including the analytically counted `2^52` five-mode lattices.
- The full constrained adaptive lattice checks 372,155 nonempty grammars and
  960,400 covers with no monotonicity reversal. Its 12 singleton finite-only
  cases all first fail at horizon five, so the earlier zero-transient statement
  remains explicitly limited to two-partition grammars.
- An independent observer-layer census gives first-failure histogram
  `10642,8406,3110,534,12` over all 60,134 fixed-transducer cases and verifies
  the explicit four-safe/fifth-failing witness.

## Nonclaims

This proof does not turn the registration-dependent result into one canonical
region across incompatible sensor grammars. It does not cover noisy channels,
randomized observation kernels, continuous belief spaces, or every normally
hyperbolic nonlinear plant.
It also does not claim the entropy-game positional theorem as new.

The v0.7 relational-action successor closes the nonunique-safe-action seam for
one exact full-reset grammar. Its concave-moment converse permits arbitrary
public read-history adaptation and yields a genuinely nonrectangular region;
its support-derandomization theorem also closes randomized observation kernels
under zero-error support-cardinality accounting. That successor is separate
from the unique-action Theorems 4-6 audited here.
