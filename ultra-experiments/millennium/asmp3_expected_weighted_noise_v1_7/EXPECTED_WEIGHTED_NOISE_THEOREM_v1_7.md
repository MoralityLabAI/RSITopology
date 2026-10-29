# ASMP-3 expected weighted-noise theorem v1.7

## Status and scope

```text
result_status = exact expected-budget total-variation phase
parent_result = ASMP-3-WEIGHTED-NOISE-SUBSET-SUM-v1.6
interface_mode = WV-FIX
noise_model = truth-aware randomized controller
coordinate_costs = positive integers c_1,...,c_d
constraint = expected flip cost at most B separately under each truth
verifier_observation = complete terminal response word
changes_parent_problem = false
```

The hard weighted budget in v1.6 produces a subset-sum boundary.  This release
changes only the declared noise class, replacing almost-sure support constraints
with separate expected-cost constraints.  Convexification eliminates the
integrality boundary and yields a closed-form minimax value.

## 1. Distributional game

Let `C=sum_i c_i` and `s(y)=sum_i c_i y_i`.  Chance samples truth uniformly.
The minimizing controller chooses response distributions `P_0,P_1` satisfying

```text
E_(P_0)[s(Y)] <= B,
E_(P_1)[C-s(Y)] <= B.                              (1)
```

The maximizing verifier observes `Y`, guesses truth, and receives `+1` when
correct and `-1` otherwise.  For fixed `P_0,P_1`, its optimal payoff is

```text
TV(P_0,P_1) = 1/2 sum_y |P_0(y)-P_1(y)|.
```

Thus the game asks for the minimum total variation between the two moment
classes in (1).

## 2. Exact theorem

### Theorem

For `0<=B<=C`, the minimax verifier value is

```text
v(C,B)=max(0,1-2B/C).                              (2)
```

The value depends on the coordinate costs only through their total `C`.

### Lower certificate

The normalized score `f(y)=s(y)/C` lies in `[0,1]`.  Every feasible pair obeys

```text
E_(P_1) f - E_(P_0) f
  >= (C-B)/C - B/C
   = 1-2B/C.
```

For any `[0,1]`-valued function,

```text
|E_(P_1)f-E_(P_0)f| <= TV(P_0,P_1).
```

Therefore total variation is at least `1-2B/C` when this is positive, and is
always at least zero.  Operationally, when `2B<C`, the verifier implements this
dual witness by guessing one with probability `s(y)/C`.  Its payoff conditional
on either truth is at least `1-2B/C`.  When `2B>=C`, uniform guessing guarantees
zero.

### Matching upper certificate

Let `0` and `1` denote the all-zero and all-one words.  If `2B<=C`, put
`a=B/C` and choose

```text
P_0=(1-a) delta_0 + a delta_1,
P_1= a delta_0 + (1-a) delta_1.
```

Each expected flip cost is exactly `aC=B`, while

```text
TV(P_0,P_1)=1-2a=1-2B/C.
```

If `2B>=C`, choose `P_0=P_1=(delta_0+delta_1)/2`.  Each cost is `C/2<=B`, and
the total variation is zero.  These distributions meet the verifier lower
certificate, proving (2).  QED.

## 3. Why subset-sum hardness disappears

Under the v1.6 hard constraint, a single response word must have cost at most
`B` under either truth; overlap therefore asks whether a subset sum lies in
`[C-B,B]`.  Under (1), the controller may mix distant endpoint words.  Only the
mean cost matters, so no intermediate subset sum is required.

For example, both cost vectors below have `C=10` and expected budget `B=5`:

```text
(2,2,2,4): expected value 0; hard-budget value 1,
(1,1,4,4): expected value 0; hard-budget value 0.
```

The first strict separation is possible because a half/half endpoint mixture
has expected cost five under each truth even though no word has weighted score
five.  More generally, the expected-noise strategy class contains every
hard-budget strategy, so expected-budget value can never exceed hard-budget
value.  The registry finds 1,139 strict cases among the 2,729 parent rows.

## 4. Succinctness

Computing (2) requires only summing the binary-encoded costs and rational
arithmetic on `B/C`.  It does not enumerate response words or subset sums.

For `c=(1,2,4,...,2^31)`, the v1.6 weighted-score enumeration has `2^32`
distinct scores.  With expected budget `B=C/3`, the present certificate returns
value `1/3` using the two endpoint distributions and the normalized-score dual
witness, without enumerating any of those words.

This is an exact consequence of convexification, not an approximation to the
hard-budget game.

## 5. Computational receipts

The producer evaluates (2) on all 2,729 integer-budget v1.6 rows.  Every
endpoint strategy is feasible, every total-variation upper certificate matches
the verifier lower certificate, and expected value never exceeds parent hard
value.

As a separate finite sanity audit, it enumerates all probability vectors with
denominator `C` for sorted cost vectors of depths one and two with coordinate
costs one through three.  Across 39 cost/budget cases and 35,808 distribution
pairs, the minimum grid total variation matches (2).  This grid is not used to
prove the continuum theorem; the exact primal/dual argument above is.

The clean-room checker independently reconstructs all parent rows, endpoint
probabilities, rational bounds, strict separations, finite-grid optima, and the
large succinct witness without importing the producer.

## 6. Noise-class firewall

“Expected budget” must not be conflated with an almost-sure hard budget.  The
result requires:

- a separate expectation bound under each truth;
- complementary truth-zero/truth-one flip costs;
- a uniform truth prior;
- randomized truth-aware noise; and
- no verifier action before the complete terminal response.

A joint expectation averaged over a nonuniform prior, high-probability or tail
constraint, variance bound, pathwise observation, restricted controller
randomness, or truth-ignorant noise changes the feasible distributions and can
change the value.

## 7. Remaining ASMP-3 boundary

This theorem closes the expected positive-integer cost lane.  It does not
characterize the complete `WV-FIX` or `WV-ADM` class, prove efficient honest
refutation search, establish matching communication/honest-prover lower bounds,
settle adaptive semantic-query selection, or replace external end-to-end review
of the negative-resolution candidate.

## 8. Novelty boundary

Bayes testing by total variation, bounded-test duality, and moment-class endpoint
mixtures are standard.  The contribution is their typed ASMP-3 integration,
matching executable rational certificates, complete comparison with the v1.6
hard-budget registry, and a precise demonstration that changing the noise
quantifier removes the subset-sum obstruction.
