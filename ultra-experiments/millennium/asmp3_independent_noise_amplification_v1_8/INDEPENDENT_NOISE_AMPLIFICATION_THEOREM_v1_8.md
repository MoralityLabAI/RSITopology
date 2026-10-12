# ASMP-3 independent-noise amplification theorem v1.8

## Status and scope

```text
result_status = exact iid replication-amplification profile
parent_result = ASMP-3-EXPECTED-WEIGHTED-NOISE-v1.7
interface_mode = WV-FIX
semantic_object = one frozen binary atom with registered meaning-preserving copies
noise_class = iid Bernoulli error rate p chosen adversarially in [0,eta]
truth_prior = uniform
eta_range = 0<=eta<1/2
changes_parent_problem = false
```

This release instantiates the canonical block-independent positive noise example
from ASMP-3.  It computes the exact semantic-noise amplification profile for one
replicated atom and proves why the same marginal error bound gives no
amplification under persistent correlation.

## 1. Registered replication game

Chance chooses `T in {0,1}` uniformly.  A registered replication family asks
the same semantic atom `d` times.  The legal noise class chooses one rate
`p in [0,eta]`; conditional on `T`, the errors `E_i` are independent and
identically distributed `Bernoulli(p)`, independent of truth, and

```text
Y_i=T xor E_i.
```

The verifier observes all `d` responses and guesses `T`, receiving `+1` for a
correct guess and `-1` otherwise.

The theorem assumes the copies are genuinely meaning preserving and charges all
`d` semantic queries.  It does not create new semantic content by replication.

## 2. Likelihood-ratio and majority theorem

Let `w` be the number of ones in a response word.  At a fixed `p<1/2`,

```text
P_1(y)/P_0(y)=((1-p)/p)^(2w-d).
```

The likelihood-ratio test therefore guesses one when `w>d/2`, zero when
`w<d/2`, and breaks an even-depth tie uniformly.  The same rule is optimal for
every `p<1/2`.

Its conditional error is

```text
e_d(p)
 = sum_(k>d/2) binom(d,k) p^k(1-p)^(d-k)
   + (1/2) 1_(d even) binom(d,d/2) p^(d/2)(1-p)^(d/2).       (1)
```

Couple errors at all rates using shared uniforms, `E_i(p)=1[U_i<=p]`.  The
majority-with-random-tie loss is nondecreasing in the error count, so `e_d(p)`
is nondecreasing on `[0,1/2]`.  The adversarial legal rate is therefore
`p=eta`.

For equal priors, optimal signed payoff is total variation, or one minus twice
Bayes error.  Hence the exact robust value and single-atom amplification profile
are

```text
v_d(eta)=1-2e_d(eta),
a_H(d)=e_d(eta).                                      (2)
```

## 3. Exact parity recurrence

Uniform tie breaking makes an even sample supply no improvement over the
preceding odd sample:

```text
e_(2m)(eta)=e_(2m-1)(eta).
```

The next odd sample gives the exact improvement

```text
e_(2m)(eta)-e_(2m+1)(eta)
 = (1/2) binom(2m,m) [eta(1-eta)]^m (1-2eta).          (3)
```

This is strictly positive for `0<eta<1/2`.  Thus replication value is unchanged
from depth `2m-1` to `2m`, then strictly improves at depth `2m+1`.  In
particular, depths one and two retain value `1-2eta`, while every depth at least
three has strictly larger value.

## 4. Exponential certificate

For the two response distributions `P_0,P_1`, equal-prior Bayes error is

```text
e_d=(1/2) sum_y min(P_0(y),P_1(y)).
```

Using `min(a,b)<=sqrt(ab)` and product factorization,

```text
e_d
 <= (1/2) sum_y sqrt(P_0(y)P_1(y))
  = (1/2) [2 sqrt(eta(1-eta))]^d.
```

The release avoids irrational arithmetic by certifying the squared form

```text
e_d^2 <= (1/4) [4eta(1-eta)]^d.                       (4)
```

Since `4eta(1-eta)<1` for `eta<1/2`, the error tends exponentially to zero and
the verifier value tends to one.  A target error `epsilon` is obtained with a
number of queries logarithmic in `1/epsilon`, with the constant determined by
the registered `eta`.

## 5. Correlation-class separation

Now retain the same marginal error `eta` but draw one latent
`Z~Bernoulli(eta)` and copy it to every response:

```text
Y_i=T xor Z  for every i.
```

Every repetition is identical, so the Bayes error remains `eta` and value
remains `1-2eta` at every depth.  The v1.7 expectation-only adversarial class
with unit costs and budget `B=d eta` has exactly the same worst-case value.

At `eta=1/5` and `d=9`, the exact contrast is

```text
iid error       = 7649/390625,
iid value       = 375327/390625  (about 0.96084),
persistent value= 3/5,
expected-budget adversarial value = 3/5.
```

All three classes have the same per-response marginal error allowance.  Their
joint laws, and therefore their amplification profiles, differ sharply.  This
is an executable instance of the v0.1 warning that independence may not be
assumed from marginals.

## 6. Computational receipts

The producer certifies 448 exact rational rows: seven positive error bounds and
every depth from one through 64.  It additionally checks:

- total variation by enumerating every response word for 30 small cases;
- monotonicity over 1,008 sampled `(d,eta,p)` rate triples;
- all 217 parity-recurrence instances through depth 63;
- the rational squared exponential bound on every registry row; and
- exact comparison with the v1.7 expectation-budget formula.

The clean-room checker independently rebuilds every binomial probability,
word-level distribution, rate grid, recurrence, correlation witness, and parent
comparison without importing the producer.

## 7. Query-cost and compositional boundary

Equation (2) is the exact amplification profile for one frozen atom.  Using it
inside a larger verifier still requires proof that:

- the query language registers `d` meaning-preserving copies;
- their conditional independence survives adaptive transcript selection;
- query and aggregation cost fit the verifier budget; and
- the amplified atoms compose through the full `Refute` predicate.

This release does not establish those transcript-conditional composition steps,
efficient honest refutation search, or matching communication/honest-prover
lower bounds.

## 8. Claim firewall and novelty

The result applies only to the complete i.i.d. class declared above.  Exchangeable,
block-correlated, persistent, adaptive, truth-aware, or merely marginally
bounded errors are different noise classes.

Binomial majority amplification, likelihood-ratio testing, and Bhattacharyya
bounds are standard.  The contribution is the typed ASMP-3 minimax class,
adversarial-rate quantifier, exact rational profile and parity receipts, and a
side-by-side executable separation from two equally accurate correlated laws.
