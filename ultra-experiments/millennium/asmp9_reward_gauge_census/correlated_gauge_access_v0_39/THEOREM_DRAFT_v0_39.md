# ASMP-9 v0.39 theorem draft: gauge semantics do not imply ancillarity

## Frozen decision grammar

Let the target be `theta in {0,1,2}` and the decision be one of the three
matching policies. Loss is normalized policy regret:

```text
L(theta,a) = 0 if a=theta, and 1 otherwise.
```

For each target, two reward representatives are licensed:

```text
r(theta,xi) = e_theta + xi * (1,1,1),  xi in {0,1}.
```

The two representatives are decision-equivalent under constant-shift reward
gauge. The random variable `xi` chooses the representative.

## Theorem 1: exact observational gauge-leakage radius

Write

```text
p_theta = P(xi=1 | theta),
diam(p) = max_theta p_theta - min_theta p_theta.
```

Let `E_p` reveal `xi`, and let `E_0` return a constant observation. For the
registered three-policy decision type,

```text
delta_D(E_0,E_p) = diam(p)/2.
```

The ordinary total-variation deficiency has the same value:

```text
delta(E_0,E_p) = diam(p)/2.
```

In the reverse direction both deficiencies are zero. Consequently `E_p` is
Blackwell-equivalent to the constant experiment exactly when all `p_theta`
are equal.

### Proof

A simulator from the constant experiment can emit a Bernoulli bit with
probability

```text
m = (max_theta p_theta + min_theta p_theta)/2.
```

Its worst total-variation error is `diam(p)/2`, proving both upper bounds.

For the decision-relative lower bound choose targets `i,j` attaining the
maximum and minimum. In the reference rule, output `1` selects policy `i`
and output `0` selects policy `j`. If a source rule uses policy probabilities
`s_i,s_j`, target-wise risk domination with slack `epsilon` requires

```text
s_i >= p_i - epsilon,
s_j >= 1 - p_j - epsilon.
```

Since `s_i+s_j <= 1`, `epsilon >= (p_i-p_j)/2`. This matches the upper bound.
The observed experiment can ignore its bit, proving both reverse
deficiencies zero.

## Corollary 1: intervention erases the leakage

Under a stochastic intervention

```text
do(xi ~ Bernoulli(lambda))
```

with the same registered `lambda` for every target, `p_theta=lambda` and both
deficiencies vanish. Thus a reward transformation may be decision-preserving
without its observational selection mechanism being ancillary; ancillarity
is a property of the target-indexed assignment law.

## Theorem 2: access value depends on alignment, not leakage radius alone

For `high+low=1`, define three one-vs-rest binary queries:

```text
q0 = (high,low,low)
q1 = (low,high,low)
q2 = (low,low,high).
```

The reference access is `(q0,q1)`. The source retains `q1` and observes one
gauge-selection bit. All of `q0`, `q1`, and `q2` have the same leakage radius
`(high-low)/2`, but:

1. if the gauge assignment is `q0` or its output complement, source and
   reference are exactly equivalent;
2. if the gauge assignment is `q1`, its duplicate does not distinguish
   targets `0` and `2`, and the relative deficiency remains
   `(high-low)/2`;
3. if the gauge assignment is target-independent, intervention returns the
   same missing-query threshold `(high-low)/2`; and
4. on the burned rational strengths, the transverse `q2` assignment has
   exact relative and ordinary deficiency
   `high*low*(high-low)`.

Items 1--3 are analytic consequences of channel equality, output reframing,
and target indistinguishability. Item 4 is currently an exact finite
primal-dual computation, not yet asserted as a general theorem.

## Claim boundary

Theorem 1 is an elementary finite specialization of classical Blackwell,
Le Cam, and Torgersen experiment comparison. The intervention corollary uses
the standard distinction between observational assignment and randomized
intervention. This draft does not establish a new general comparison theorem,
that real reward-model gauge choices follow this grammar, or that ASMP-9 is
resolved.
