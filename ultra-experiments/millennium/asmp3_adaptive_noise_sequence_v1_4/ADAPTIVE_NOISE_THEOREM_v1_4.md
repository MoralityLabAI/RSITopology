# ASMP-3 adaptive joint-noise sequence theorem v1.4

## Status and scope

```text
result_status = exact joint-noise budget phase
parent_result = ASMP-3-SEQUENCE-FORM-BRIDGE-v1.3
interface_mode = WV-FIX
noise_model = truth-aware history-adaptive zero-sum controller
noise_constraint = one global Hamming flip budget b across d responses
changes_parent_problem = false
```

The v1.3 theorem compiles a fixed rational perfect-recall game.  This successor
uses that compiler for a semantic-noise controller whose legal next response
depends on the complete response history and remaining global budget.

The theorem is about this registered adversarial budget class.  It is not a
statement about independent flips, persistent latent flips, or a noise process
that is ignorant of truth.

## 1. Repeated-response game

Chance samples hidden truth `T in {0,1}` uniformly.  The minimizing noise role
knows `T` and emits a binary response word

```text
Y=(Y_1,...,Y_d).
```

At every step it observes its previous responses and may choose either bit as
long as the final number of positions with `Y_i!=T` is at most `b`.

After all responses, the maximizing verifier sees only `Y` and guesses `T`.
Its terminal payoff is

```text
+1 for a correct guess,
-1 for an incorrect guess.
```

Verifier nodes with the same response word share one information set even when
they arise from different truths.  Noise information sets retain truth and
complete response history.  The game has perfect recall and is zero-sum.

## 2. Complete response languages

For truth zero, legal words form the Hamming ball

```text
R_0(d,b)={y : weight(y)<=b}.
```

For truth one,

```text
R_1(d,b)={y : number_of_zeros(y)<=b}
         ={y : weight(y)>=d-b}.
```

Both have size

```text
sum_(i=0)^b binom(d,i).
```

Their intersection has size

```text
sum_(w=d-b)^b binom(d,w),
```

with an empty sum interpreted as zero.

## 3. Exact phase theorem

### Theorem 1 (joint budget boundary)

The zero-sum verifier value is

```text
1  when 2b<d,
0  when 2b>=d.
```

### Separable phase: `2b<d`

Every word in `R_0` has fewer than `d/2` ones, while every word in `R_1` has
more than `d/2` ones.  Majority therefore identifies truth for every legal
adaptive noise strategy and guarantees payoff one.

No payoff exceeds one, so any legal noise strategy supplies a matching upper
bound.  The registered sequence certificate uses the no-flip strategy.

### Overlap phase: `2b>=d`

Choose any word with weight between `d-b` and `b`; the release uses weight
`d-b`.  Noise can emit this same word under either truth while respecting the
budget.  Conditional on that common transcript, the uniform truth prior remains
indistinguishable.  Every verifier guess rule has expected payoff at most zero.

Conversely, guessing zero/one uniformly gives expected payoff zero after every
truth and transcript.  These two strategies form a saddle of value zero.  QED.

The release compiles and certifies every `(d,b)` with `1<=d<=6` and `0<=b<=d`.

## 4. Sequence-form realization

Each noise history is a minimizing information set with actions equal to the
still-legal emitted bits.  Each full response word is a maximizing information
set merging the truth-zero and truth-one histories when both are reachable.

The v1.3 compiler produces:

```text
E_max x=e_max,
E_min y=e_min,
A,
```

and the v1.4 harness constructs exact majority/common-transcript realization
plans and dual potentials.  Matching lower and upper values certify each game
without enumerating complete pure noise policies.

The clean-room checker independently reconstructs:

- both Hamming languages;
- their overlap;
- every binomial count;
- the majority/common-transcript strategies;
- information-set, sequence, terminal, and node counts; and
- every recorded saddle value.

## 5. Why a marginal profile is insufficient

The boundary depends on whether the complete response languages intersect.
It is not determined by a separate accuracy number for each response.

A global budget couples all positions.  The controller may concentrate flips
on a transcript selected to erase the truth distinction.  Once `2b>=d`, one
joint word is legal under both truths and the minimax value collapses to zero,
even though many individual positions may remain unflipped.

Conversely, when `2b<d`, arbitrary history-adaptive placement of all `b` flips
cannot defeat the joint majority predicate.

Thus the relevant object is a transcript-conditional joint response class,
matching the typed `J_(E,G,Pi)` requirement from the v0.2 successor.

## 6. Noise-class boundary

Changing any of the following changes the game:

- whether noise knows truth;
- whether it sees earlier responses;
- whether the constraint is almost sure, expected, or probabilistic;
- whether flips are independent, persistent, exchangeable, or adversarial;
- whether the advocate and noise controller share information/randomness;
- whether query choice is adaptive; and
- whether the verifier sees timing or auxiliary state.

The theorem cannot be transferred to another noise class by reusing only its
single-response error rate.

## 7. Complexity boundary

The release builds the explicit history tree.  At depth `d`, this can be
exponential even though the budget controller has a compact state `(round,
flips_used, truth)`.  A further bridge would compile the finite-state controller
into a compact dynamic/occupancy formulation without enumerating response
histories, while retaining the verifier's observation information sets.

That compression is not claimed here.

## 8. Claim and novelty boundary

Hamming-ball separation and adversarial error correction are standard.  The
contribution here is the typed ASMP-3 game, exact perfect-recall compilation,
joint-noise saddle receipts, full small registry, and explicit separation from
marginal-noise claims.  This is a closed robust-noise lane, not a complete
weak-verifier characterization.
