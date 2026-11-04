# ASMP-3 weighted-noise subset-sum theorem v1.6

## Status and scope

```text
result_status = exact weighted-budget phase and complexity boundary
parent_result = ASMP-3-NOISE-SYMMETRY-QUOTIENT-v1.5
interface_mode = WV-FIX
noise_model = truth-aware adaptive controller
coordinate_costs = positive integers c_1,...,c_d encoded in binary
constraint = hard total flip-cost budget B
verifier_observation = complete terminal response word
changes_parent_problem = false
```

This release resolves the position-dependent positive-integer cost boundary
identified by v1.5.  It gives an exact terminal sufficient statistic and a
pseudo-polynomial controller, then proves why the same enumerated-score
compression cannot be guaranteed polynomial in `d` for arbitrary
binary-encoded costs.

## 1. Weighted response game

Let `C=sum_i c_i`.  Chance chooses truth `T in {0,1}` uniformly.  The minimizing
controller knows `T` and emits `Y in {0,1}^d`, paying `c_i` whenever `Y_i != T`.
The sum of paid costs may not exceed `B`.  The maximizing verifier sees `Y`,
guesses `T`, and receives `+1` for a correct guess and `-1` otherwise.

Define the terminal weighted score

```text
s(y)=sum_i c_i y_i.
```

The two complete legal languages are

```text
R_0={y : s(y)<=B},
R_1={y : C-s(y)<=B}.
```

## 2. Weighted-score sufficiency

For a verifier rule `g(y)=Pr[guess one]`, its guaranteed payoff is

```text
V(g) = 1/2 min_(y in R_0) [1-2g(y)]
     + 1/2 min_(y in R_1) [2g(y)-1].
```

Partition all words into level sets with equal `s(y)`.  Each `R_t` is a union of
whole level sets.  Average `g` independently inside every level set.  For each
truth, the minimum of the averaged payoffs is at least the average of the
original minimum payoffs, exactly as in the v1.5 group-averaging inequality.
Thus score averaging cannot lower `V(g)`, and an optimal verifier depends only
on `s(y)`.

This is a terminal-language symmetry.  It does not assert that unequal-cost
coordinates can be permuted at intermediate histories.

## 3. Exact subset-sum phase

Let

```text
S(c)={sum_(i in I) c_i : I subseteq {1,...,d}}
```

be the reachable subset sums.  Truth zero can produce precisely the terminal
scores in `S(c) intersect [0,B]`; truth one can produce precisely
`C-(S(c) intersect [0,B])`.

These score sets overlap exactly when

```text
S(c) intersect [C-B,B] is nonempty.                 (1)
```

Indeed, a common word has score `w<=B` under truth zero and flip cost
`C-w<=B` under truth one.  Conversely, any subset realizing a score in the
interval supplies the same legal word under both truths.

Therefore:

```text
value = 1  iff no subset sum lies in [C-B,B],
value = 0  iff a subset sum lies in [C-B,B].
```

In the first phase, the two weighted-score sets are disjoint, so score-based
classification is always correct.  In the second, the controller emits one
common word under either truth, giving an upper bound zero, while uniform
guessing gives the matching lower bound zero.

For unit costs, `S(c)={0,...,d}` and (1) reduces to `2B>=d`, exactly recovering
v1.5.

## 4. Exact finite-state controller

After round `r`, the controller retains only

```text
(T,r,a),
```

where `a` is the accumulated flip cost.  At coordinate `r+1`, emitting truth
leaves `a` unchanged; flipping adds `c_(r+1)` when the result is at most `B`.

For a fixed coordinate order, the exact nonterminal states per truth are

```text
sum_(r=0)^(d-1) |S(c_1,...,c_r) intersect [0,B]| <= d(B+1).
```

The terminal weighted-score count per truth is at most `B+1`.  A standard
subset-sum dynamic program constructs all states in pseudo-polynomial time and
space.  The bound is polynomial in the numeric budget but not necessarily in
the bit length of `B`.

## 5. PARTITION boundary

Consider the decision problem “do the two legal response languages overlap?”
It is in NP: a response word is a certificate, and its two weighted costs can
be checked in polynomial time.

Given an instance of PARTITION with positive integer weights `c_i` and even
total `C`, set `B=C/2`.  Criterion (1) becomes

```text
S(c) intersect {C/2} is nonempty,
```

which is exactly the PARTITION question.  For an odd total, choosing
`B=floor(C/2)` makes the interval empty and preserves the no answer.  Hence
weighted-language overlap is NP-complete, weakly so in the standard sense
because the dynamic program is pseudo-polynomial.

This does not say that every individual weighted game is hard or that no other
symbolic quotient can be small.  It says that a uniform exact phase algorithm
polynomial in `d` and the binary input length would solve PARTITION.

## 6. Two explicit obstructions

Hamming depth, total cost, and budget do not determine the phase.  Both examples
below have depth four, total cost ten, and budget five:

```text
c=(2,2,2,4): no subset sums to 5, so value=1;
c=(1,1,4,4): 1+4=5, so value=0.
```

Nor must weighted-score quotienting compress the terminal language.  With

```text
c=(1,2,4,...,2^31),  B=2^32-1,
```

binary expansion gives every one of the `2^32` subsets a distinct score.  The
explicit weighted-score quotient therefore also has `2^32` states and
compression factor one.  This statement is about enumerating score states, not
about the nonexistence of a different symbolic representation for this
particular easy-budget instance.

## 7. Computational evidence

The producer certifies all 2,729 combinations formed by nondecreasing cost
vectors of depths one through six, coordinate costs one through four, and every
budget from zero to total cost.  It checks explicit response languages against
subset-sum dynamic programming, reconstructs controller-state counts, and
cross-checks all 27 unit-cost v1.5 cases.

It also averages all deterministic verifier rules across equal-score level sets
for depths at most three, covering 18,436 rule/cost/budget instances.  A
clean-room checker independently rebuilds the registry and all of these tests
without importing the producer.

## 8. Claim firewall and remaining ASMP-3 work

The theorem assumes finite positive integer costs, one hard total budget,
truth-aware noise, and no verifier action before the terminal word.  Signed or
real-valued costs, stochastic/expected budgets, timing or path observations,
adaptive query selection, and other information patterns require new models.

The result closes a robust-noise representation lane.  It does not supply the
general `WV-FIX`/`WV-ADM` characterization, honest-refutation search theorem,
matching communication and honest-prover lower bounds, or external resolution
review required by the ASMP-3 successor.

## 9. Novelty boundary

Subset-sum dynamic programming and PARTITION hardness are standard.  The
contribution is the exact ASMP-3 weighted-language reduction, score-sufficiency
proof, matching saddle strategies, finite-state receipt, exhaustive typed
registry, unit-cost reduction, and explicit exponential noncompression witness.
