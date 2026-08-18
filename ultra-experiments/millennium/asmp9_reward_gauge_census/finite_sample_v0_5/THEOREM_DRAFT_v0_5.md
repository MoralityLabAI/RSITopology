# Finite-sample identification through a noisy sign-and-tie channel

## Status

Unregistered theorem draft. This file may guide tests, but no result may be
called prospective until a later protocol and registration are committed.

## Model

Let `P(d,B)` be the primitive nonzero integer vectors in `[-B,B]^d`, with
positive scale quotiented and negative scale retained. A query is a primitive
integer vector `q` of coefficient width at most `W`.

The latent answer is:

```text
S(q,z) = sign(q dot z) in {-1,0,+1}.
```

For a known error rate `0 <= eta < 1/2`, one human response is binary:

```text
P(Y=1 | S=+1) = 1-eta,
P(Y=1 | S= 0) = 1/2,
P(Y=1 | S=-1) = eta.
```

Responses are conditionally independent given the reward ray and the adaptive
query sequence. The fair response at a tie is a modeling decision, not a claim
about human psychology. Because only `S` enters the channel, the law is
invariant under positive reward scaling.

## Candidate theorem

Define:

```text
W*(B) = 1       for B in {1,2},
        B-1     for B>=3.
```

Let `0 < alpha < 1/2`.

### 1. Sharp width liveness

If `W < W*(B)`, there are two distinct rays whose complete response laws agree
under every adaptive experiment of every sample size. Consequently no
estimator has worst-case error below `1/2`.

If `W >= W*(B)`, every ray is identifiable with finite worst-case sample
complexity.

### 2. Constructive finite-sample upper bound

Let `F_N` be the Farey sequence of order `N=max(1,B-1)` and let:

```text
L_B = |F_N|,
K(d,B) = d + (d-1) * (2 + ceil(log2 L_B)).
```

There is an adaptive coordinate-and-ratio search using at most `K(d,B)`
logical comparisons, all of width at most `W*(B)`.

Repeat each logical comparison:

```text
n = ceil(
      8 / (1-2eta)^2
      * ln(2 K(d,B) / alpha)
    )
```

times and classify its latent ternary sign by the two midpoints between
`eta`, `1/2`, and `1-eta`. The resulting estimator uses at most:

```text
T_upper = K(d,B) * n
```

binary responses and returns the correct ray with probability at least
`1-alpha`, uniformly over `P(d,B)`.

Since `|F_N| = Theta(B^2)`, this gives:

```text
T_upper =
O(
  d log(B)
  * log(d log(B) / alpha)
  / (1-2eta)^2
).
```

### 3. Information lower bound

Let:

```text
M(d,B) = |P(d,B)|,
C_eta = 1 - h2(eta),
```

where `h2` is binary entropy in bits. Any fixed-budget adaptive estimator with
worst-case error at most `alpha` satisfies:

```text
T >=
((1-alpha) log2 M(d,B) - h2(alpha))
/ C_eta.
```

The tie input cannot increase channel capacity: its output law is the equal
mixture of the two strict-sign output laws and has conditional entropy one.
The three-input channel therefore has the same capacity as the binary
symmetric channel, `1-h2(eta)`.

For fixed `alpha`, the lower bound scales as:

```text
Omega(d log(B) / (1-h2(eta))).
```

Near `eta=1/2`, `1-h2(eta)=Theta((1-2eta)^2)`, so the constructive upper and
information lower bounds agree in their dependence on dimension, reward
resolution, and channel degradation up to logarithmic factors.

### 4. Nonadaptive critical-width penalty

Restrict to the two-dimensional nonnegative rays:

```text
z_t = primitive representative of (1,t),  t in F_B.
```

At the critical width `W=B-1`, consecutive ratios in `F_B` have no admissible
threshold strictly between them. They can be separated only by querying an
endpoint that already lies in `F_{B-1}`. One threshold is incident to at most
two adjacent pairs.

For any fixed nonadaptive allocation of `T` queries, some one of the
`|F_B|-1` adjacent pairs therefore receives at most:

```text
2T / (|F_B|-1)
```

informative samples. Let:

```text
D_tie(eta) =
max(
  KL(Bernoulli(1/2) || Bernoulli(eta)),
  KL(Bernoulli(eta) || Bernoulli(1/2))
).
```

For `0<eta<1/2` and `0<alpha<1/4`, the Bretagnolle-Huber inequality gives the
nonadaptive lower bound:

```text
T_nonadaptive >=
(|F_B|-1) / (2 D_tie(eta))
* ln(1/(4 alpha)).
```

Since `|F_B|=Theta(B^2)`, nonadaptive identification at the minimum width costs
`Omega(B^2)` samples for fixed channel and confidence. The constructive
adaptive search has only `O(log B)` logical depth per recovered ratio and
`O(log B log log B)` binary responses under the simple repeated-query rule for
fixed channel and confidence. The separation is an access/adaptivity result,
not a claim that interventions are universally cheaper.

## Proof sketch

The impossibility below `W*(B)` is inherited exactly from the v0.4 lower
witness: equal ternary signatures imply equal stochastic response laws, so
adaptivity and repeated samples cannot help.

For the upper bound:

1. query each coordinate to recover its sign and zero status;
2. select one nonzero reference coordinate;
3. compare every other nonzero coordinate to the reference to choose a ratio
   orientation in `[0,1]`;
4. binary-search thresholds in `F_{B-1}`;
5. use the Farey-cell lemma to recover the unique bounded reduced ratio; and
6. reconstruct the unique primitive signed vector.

For one repeated logical query, the nearest classification threshold is
`(1-2eta)/4` from its mean. Hoeffding's inequality bounds a sign-classification
error by:

```text
2 exp(-n (1-2eta)^2 / 8).
```

A union bound over `K(d,B)` comparisons proves the stated upper bound.

For the lower bound, place the uniform prior on `P(d,B)`. Conditional on the
past, an adaptive query passes the hypothesis through the same three-input,
binary-output memoryless channel. Each sample contributes at most `C_eta`
bits. Chain-rule mutual information plus Fano's inequality gives the result.

For the nonadaptive penalty, sum the number of samples allocated to the
admissible endpoint thresholds over all adjacent pairs in the Farey path.
Every sample is counted at most twice, so one edge receives at most the stated
fraction. Its two transcript laws differ only on those samples. A
two-hypothesis testing lower bound then supplies the required confidence
factor.

## What would refute or amend this draft

1. a bounded primitive ratio not located uniquely by the registered Farey
   search;
2. a query emitted by the constructor above `W*(B)`;
3. a three-input channel distribution with mutual information above
   `1-h2(eta)`;
4. a counterexample to the reconstruction of the primitive vector from signed
   coordinate ratios; or
5. prior art already stating this exact width-liveness theorem and bound.

## Claim boundary

This is a finite hypothesis-identification theorem for a known independent
sign-and-tie channel. It is not Bradley-Terry reward recovery, policy
observation, discounted IRL, a theorem about human inconsistency, or a complete
ASMP-9 resolution.
