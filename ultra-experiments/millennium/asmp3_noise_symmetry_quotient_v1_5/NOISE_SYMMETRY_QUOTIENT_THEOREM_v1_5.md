# ASMP-3 noise-symmetry quotient theorem v1.5

## Status and scope

```text
result_status = exact permutation-quotient phase
parent_result = ASMP-3-ADAPTIVE-NOISE-SEQUENCE-v1.4
interface_mode = WV-FIX
noise_model = truth-aware history-adaptive zero-sum controller
noise_constraint = one global Hamming flip budget b across d responses
symmetry_group = all coordinate permutations S_d
changes_parent_problem = false
```

This release closes the compact finite-state formulation left open by v1.4.
For the registered game, complete response histories can be quotiented by
coordinate permutations without changing the minimax value.  The quotient has
one terminal observation per Hamming weight and controller state
`(truth, round, flips_used)`.

## 1. Parent game and payoff

Chance samples `T in {0,1}` uniformly.  A minimizing controller that knows `T`
emits `Y in {0,1}^d` subject to at most `b` coordinates satisfying `Y_i != T`.
The maximizing verifier observes `Y`, guesses `T`, and receives `+1` for a
correct guess and `-1` otherwise.

Write `g(y)` for the verifier's probability of guessing one.  Its guaranteed
payoff is

```text
V(g) = 1/2 min_(y in R_0) [1-2g(y)]
     + 1/2 min_(y in R_1) [2g(y)-1],

R_0 = {y : weight(y)<=b},
R_1 = {y : weight(y)>=d-b}.
```

The controller is adaptive, but its complete legal response language is exactly
`R_T`, so the displayed expression already includes all legal controllers.

## 2. Symmetrization theorem

The group `S_d` acts by permuting response coordinates.  Both `R_0` and `R_1`
are invariant under this action.  For any verifier rule define

```text
g_bar(y) = (1/|S_d|) sum_(pi in S_d) g(pi y).
```

For either truth, let `h_t(y)` be its corresponding payoff expression.  Since
`R_t` is invariant,

```text
min_(y in R_t) (1/|S_d|) sum_pi h_t(pi y)
  >= (1/|S_d|) sum_pi min_(y in R_t) h_t(pi y)
   = min_(y in R_t) h_t(y).
```

Thus replacing `g` by `g_bar` cannot decrease either truth-conditioned
worst-case payoff and cannot decrease `V(g)`.  A maximizing verifier therefore
has an optimal permutation-invariant rule.

The orbits of binary words under `S_d` are exactly their Hamming-weight classes.
Consequently the verifier needs only the terminal weight, not the full word.
This proves that the weight quotient is value preserving.

## 3. Finite-state controller quotient

At the beginning of round `r`, histories with the same truth and number `f` of
flips have identical legal continuations in the quotient.  The state is

```text
(T,r,f),  0<=r<d,  0<=f<=min(b,r).
```

The controller can emit the truth bit without changing `f`, or—when `f<b`—the
opposite bit and increment `f`.  Under truth zero the terminal weight is `f`;
under truth one it is `d-f`.  Therefore the two terminal weight ranges are

```text
W_0={0,...,b},       W_1={d-b,...,d}.
```

For each truth, the number of nonterminal quotient controller states is

```text
sum_(r=0)^(d-1) (min(b,r)+1)
  = (b+1)(d-b) + b(b+1)/2.
```

There are only `b+1` quotient terminal states per truth.  In comparison, the
explicit parent language has

```text
sum_(i=0)^b binom(d,i)
```

terminal words per truth and the analogous binomial prefix-tree count.  For
`d=b=32`, the exact quotient replaces `2^32` terminal words by 33 terminal
weights (and uses 528 nonterminal controller states per truth).

## 4. Exact value on the quotient

If `2b<d`, then `W_0` and `W_1` are disjoint.  Guessing by weight distinguishes
truth on every legal path and guarantees payoff one.  Since no payoff exceeds
one, the value is one.

If `2b>=d`, choose any common weight in `[d-b,b]`.  The controller can produce a
word of that weight under either truth.  The same terminal quotient state is
therefore compatible with both uniformly likely truths, giving an upper bound
of zero.  A verifier that guesses uniformly at every weight guarantees zero,
so the value is zero.

Hence the compact quotient has the same exact phase as the explicit parent:

```text
value = 1 when 2b<d,
value = 0 when 2b>=d.
```

## 5. Computational certificates

The producer reconstructs all 560 cases with `1<=d<=32` and `0<=b<=d`, checks
the closed-form state counts, and cross-checks all 27 v1.4 parent cases.  It also
enumerates every deterministic verifier rule for `d<=3` and verifies directly
that orbit averaging never lowers the worst-case value.

The clean-room checker does not import the producer.  It independently rebuilds
all formulas, strategies, the complete registry, the parent receipts, and the
small-rule symmetrization audit.

## 6. Invariance firewall

The proof requires coordinate-permutation invariance of all four ingredients:

- the truth prior;
- the hard Hamming-budget response languages;
- terminal payoff; and
- verifier observation costs.

Position-dependent queries, weighted flip costs, timing leakage, per-coordinate
reliabilities, or asymmetric payoff can split a weight orbit into inequivalent
histories.  The present quotient does not apply to such games without a new
group/action proof.

The quotient is a succinct representation of this explicit finite game; it is
not a claim that every implicitly represented weak-verifier game is tractable.
Honest-prover computation, `WV-ADM`, probabilistic noise classes, and the full
v0.1 scope remain outside this theorem.

## 7. Novelty boundary

Group averaging, Hamming-weight orbits, and adversarial error correction are
standard mathematics.  The contribution here is their exact typed integration
with the ASMP-3 v1.4 game, a value-preserving controller/observation quotient,
all-parameter formulas, executable receipts, and an explicit invariance
firewall.  This closes one compact-noise lane, not ASMP-3 as a whole.
