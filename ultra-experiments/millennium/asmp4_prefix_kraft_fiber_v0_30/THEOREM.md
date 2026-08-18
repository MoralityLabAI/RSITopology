# ASMP-4 rounded local-fiber Kraft transfer v0.30

## 1. Sequential minimax prefix cost

Fix a finite realized port language `L(T)` and its prefix tree. At a leaf set

`P_L(p)=0`.

At a nonterminal prefix `p`, set

`P_L(p)=ceil(log2 sum_a 2^P_L(pa))`,

where `a` ranges over the realized successors of `p`. The horizon cost is
`P_T(L)=P_L(empty)`.

This recurrence is exactly the minimum worst-case cumulative length of a
sequential binary prefix-free description. If the future cost after successor
`a` is `P_L(pa)`, a root code with integer lengths `l_a` has worst-case total
at most `K` precisely when `l_a <= K-P_L(pa)` and

`sum_a 2^(-(K-P_L(pa))) <= 1`.

The least integer `K` satisfying that Kraft inequality is the displayed
recurrence.

## 2. Causal factor and rounded local fiber

Let `phi` be a length-preserving, extension-consistent map from a target tree
`A` to a source tree `S=phi(A)`. Thus, if `pa` extends target prefix `p` by one
symbol, then

`phi(pa)=phi(p)b`

for one source successor `b`. Define the maximum local successor fiber

`m(p)=max_b |{a : phi(pa)=phi(p)b}|`.

Define the remaining rounded correction recursively by

- `C_phi(p)=0` at a leaf;
- `C_phi(p)=ceil(log2 m(p)) + max_a C_phi(pa)` otherwise.

Equivalently, at horizon `T`,

`C_phi(T)=max_(ell in A(T)) sum_(t<T) ceil(log2 m(ell[:t])).`

This is neither a terminal-word fiber nor the logarithm of the unrounded
worst-path fiber product.

## 3. Finite-horizon transfer theorem

Every such causal tree factor obeys

`P_T(A) <= P_T(S) + C_phi(T).`

### Proof

Prove the prefixwise statement

`P_A(p) <= P_S(phi(p)) + C_phi(p)`

by backward induction. It is immediate at leaves. Let `q=phi(p)` and let
`D=max_a C_phi(pa)`. By induction, group target successors according to their
source successor `b`:

`sum_a 2^P_A(pa)`

`<= sum_b sum_(a:phi(pa)=qb) 2^(P_S(qb)+C_phi(pa))`

`<= m(p) 2^D sum_b 2^P_S(qb)`.

The sum over `b` may be enlarged to all realized source successors at `q`.
By the source recurrence,

`sum_b 2^P_S(qb) <= 2^P_S(q)`,

and `m(p) <= 2^ceil(log2 m(p))`. Hence the target Kraft sum is at most

`2^(P_S(q)+D+ceil(log2 m(p)))`.

Taking the ceiling of its base-two logarithm gives the induction claim because
`D+ceil(log2 m(p))=C_phi(p)`. QED.

The proof is uniform over histories: when several target prefixes share one
source prefix, using the complete source subtree only enlarges the source
Kraft sum.

## 4. Asymptotic transfer

For a uniform horizon profile define the directional rounded local-fiber
entropy

`chi_phi = limsup_(T -> infinity) C_phi(T)/T`.

The normalized target prefix cost is at most the normalized source cost plus
`chi_phi`. Read and write ports require separate profiles, and reverse
strategy transfer requires a separate reverse causal factor. Conditional on
the corresponding safe strategy transfers, bidirectional profiles with
`C_phi(T)=o(T)` preserve the complete prefix-cost region.

Let `F_phi(T)` be the unrounded local-fiber product from v0.29. Since each
`m(p)` is a positive integer,

`log2 m(p) <= ceil(log2 m(p)) <= 2 log2 m(p)`

when `m(p)>1`, with both sides zero for `m(p)=1`. Therefore

`log2 F_phi(T) <= C_phi(T) <= 2 log2 F_phi(T)`.

Subexponential `F_phi` and sublinear `C_phi` have the same zero/nonzero phase
boundary, although their positive finite-horizon corrections need not agree.

## 5. Sequential rounding is load-bearing

Map a full ternary target tree to a deterministic source tree. At every
prefix, `m(p)=3`, so the recurrence adds two bits per step:

`P_T(A)=C_phi(T)=2T`, while `log2 F_phi(T)=T log2 3`.

One final ceiling does not repair the difference. It equals `2T` at `T=1,2`,
but

`ceil(T log2 3) < 2T` for every `T >= 3`.

Indeed, `3 log2(4/3)>1`, so from `T=3` onward the unrounded value is more than
one bit below `2T`. Thus neither `log2 F_phi(T)` nor
`ceil(log2 F_phi(T))` can replace the sum of per-prefix ceilings.

## 6. Terminal-bijective disclosure obstruction

Use the target and source languages

`A={000,001,010,100}` and `S={000,001,010,011}`

with the causal disclosure map registered in v0.29. The full-word map is a
bijection, so the terminal fiber is one. Direct Kraft evaluation gives

`P_3(A)=3,   P_3(S)=2,   C_phi(3)=1`.

The theorem is tight. Repeating the block `k` times yields costs `3k` and `2k`,
terminal fiber one, and rounded correction `k`: an exact one-third bit per-step
distortion hidden by terminal fibers.

## 7. Other sharp boundaries

- The maximum local fiber is necessary. A source node with two successors can
  receive target successor groups of sizes `M` and one; the minimum group is
  one while the target prefix cost grows with `M`.
- Bounded corrections are sufficient but not necessary for exact rates.
  Ternary merging only at dyadic times gives unbounded
  `C(T)=2 bit_length(T)=o(T)`.
- `limsup` is necessary. Alternating increasingly long zero-correction rests
  and positive-density bursts makes the normalized correction approach zero
  on one subsequence and one half on another.

## 8. Scope

This is a deterministic, worst-case, binary prefix-free cost theorem for
finite realized causal port trees. It is a cost-layer result: it does not by
itself construct a safe strategy transfer. It does not claim an average-length
or stochastic source-coding theorem, a nonbinary coding law, a public quotient
for arbitrary nonlinear plants, or the adversarial multidimensional
mean-payoff construction still outside the current ASMP-4 harness.
