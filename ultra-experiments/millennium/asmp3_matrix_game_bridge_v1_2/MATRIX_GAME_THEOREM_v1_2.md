# ASMP-3 simultaneous hidden-action matrix theorem v1.2

## Status and scope

```text
result_status = exact simultaneous hidden-action bridge
parent_result = ASMP-3-TWO-ROLE-BACKWARD-BRIDGE-v1.1
interface_mode = WV-FIX
interaction_model = finite rational zero-sum normal-form matrix
changes_parent_problem = false
```

The v1.1 theorem solves public turn-based perfect-information games.  Its
matching-pennies audit proves that revealing a hidden action and imposing a
sequential order can change the game value.  This theorem closes the finite
simultaneous normal-form lane without revealing either role's randomized
action.

## 1. Frozen matrix game

Let `A in Q^(m x n)` be the maximizing verifier role's payoff matrix.  The
maximizer privately samples row `i`; the minimizing challenge role privately
samples column `j`; their actions are simultaneous; and the expected zero-sum
payoff is `A_(i,j)`.

The action registries, information structure, timing, randomness, matrix, and
payoff interpretation are frozen interface data.  In an ASMP-3 application,
the matrix entries must already represent the declared
completeness-versus-soundness gap.

## 2. Primal and dual games

The maximizing role solves

```text
maximize    v
subject to  x_i >= 0,
            sum_i x_i = 1,
            sum_i x_i A_(i,j) >= v  for every column j.
```

The minimizing role solves

```text
minimize    w
subject to  y_j >= 0,
            sum_j y_j = 1,
            sum_j A_(i,j)y_j <= w  for every row i.
```

### Theorem 1 (finite simultaneous saddle)

The two rational LPs have the same optimum.  If feasible rational strategies
`x,y` satisfy the displayed inequalities with a common value `gamma`, then

```text
min_j (x^T A)_j >= gamma,
max_i (A y)_i <= gamma,
```

so `(x,y)` is an exact mixed saddle and the game value is `gamma`.

### Proof

For any maximizing mixture `x` and minimizing mixture `y`,

```text
min_j (x^T A)_j <= x^T A y <= max_i (A y)_i.
```

Thus every primal lower bound is at most every dual upper bound.  The two
programs are the standard finite zero-sum primal/dual pair; finite LP strong
duality gives equal optima and rational optimal basic solutions.  When supplied
lower and upper certificates meet at `gamma`, weak duality alone verifies
optimality.  QED.

The release checker trusts no floating-point solve.  It recomputes every row
and column expectation using exact fractions.

## 3. Registered exact saddles

### Matching pennies

```text
A = [[ 1,-1],
     [-1, 1]].
```

Uniform mixtures give every row and column expectation zero.  The value is
zero, while the pure maximin is `-1`.  This closes the information-boundary
fixture from v1.1 without converting it to revealed sequential play.

### Rock-paper-scissors

The standard antisymmetric three-action matrix has value zero under uniform
mixtures.  Every pure action is exploitable; all three actions are required by
the registered certificate.

### Biased oversight matrix

```text
A = [[4/5,1/5],
     [2/5,3/5]].
```

The maximizer mixes `(1/4,3/4)` and the minimizer mixes `(1/2,1/2)`.  Every
opposing pure action then gives payoff `1/2`, certifying exact value `1/2`.
This fixture checks a nonuniform saddle rather than only symmetry.

## 4. Growing hidden-attack family

Let `A=I_k`, with payoff one when the verifier row matches the hidden attack
column and zero otherwise.  Uniform mixtures satisfy

```text
A^T x = (1/k)1,
A y   = (1/k)1.
```

Hence the exact value is `1/k`.  For every `k>=2`, the pure maximin is zero.
The release certifies `k=1,...,12`.

This is a simple asymptotic warning: perfect performance against a matched
hidden case and a finite exact saddle do not imply a constant gap as the hidden
attack registry grows.  Uniform coverage must remain bounded away from zero.

## 5. Action-alias invariance

Duplicating every row and column of the biased matrix `r` times adds only
synonymous actions.  Splitting the original saddle mass uniformly among the
copies preserves every expected payoff and the value `1/2`.  Exact certificates
cover `r=1,...,6`.

This is benign registry refinement.  Adding a genuinely new row or column with
different payoffs changes the game and is not an alias.

## 6. Normal-form representation boundary

The LP is polynomial-size in the explicit `m x n` matrix.  This does not make
it polynomial-size in an arbitrary extensive-form protocol.  A compact game
tree with many information sets can have exponentially many complete pure
strategies, so constructing `A` may dominate the computation.

Normal form also erases the causal structure needed to charge transcript,
semantic-query, and per-round verifier costs.  Those resources must remain
typed in the extensive interface.

## 7. Next bridge: perfect-recall sequence form

For a finite two-player zero-sum extensive game with perfect recall, realization
plans satisfy one flow equality per information set.  The sequence-form payoff
is bilinear in the two realization plans, yielding a compact saddle LP.

A valid ASMP-3 successor must:

1. register histories, information sets, actions, chance probabilities, and
   terminal payoffs;
2. prove perfect recall for both roles;
3. construct the realization matrices and payoff matrix without normal-form
   enumeration;
4. map sequence strategies back to behavioral strategies at zero-reach
   information sets; and
5. reproduce normal-form values on small hidden-action and sequential fixtures.

## 8. Claim and novelty boundary

Finite zero-sum minimax and its primal/dual LP are standard.  The contribution
here is the exact ASMP-3 hidden-action bridge, rational certificate registry,
growing-attack and alias audits, and the explicit normal-form stopping boundary.
This is not yet a compact characterization of general debate protocols.
