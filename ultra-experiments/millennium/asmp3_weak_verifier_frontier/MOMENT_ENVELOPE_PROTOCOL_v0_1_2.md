# Exchangeable two-moment classification protocol v0.1.2

## Status

This is a post-result exact characterization prompted by review of v0.1.1. It
is not a preregistered empirical outcome. The v0.1 protocol and result remain
unchanged.

## Frozen object

Let `X_1,...,X_9` be an exchangeable Bernoulli error vector and
`S=sum_i X_i`. Retain only the quantities frozen in v0.1:

```text
E[X_i] = 1/5
Corr(X_i,X_j) = rho for i != j
rho in [0,1]
majority failure = P(S >= 5)
admissible failure <= 1/20.
```

Exchangeability reduces the joint law to ten probabilities
`p_s=P(S=s)`, `s=0,...,9`. The moment constraints are

```text
sum_s p_s = 1
sum_s s p_s = 9/5
sum_s s(s-1) p_s = (72+288 rho)/25
p_s >= 0.
```

Conversely, every feasible count law defines an exchangeable nine-bit law by
assigning probability `p_s / C(9,s)` to every error vector of Hamming weight
`s`. The ten-variable LP therefore loses no exchangeable laws.

The objective `sum_{s>=5} p_s` is linear.

## Required certificates

1. Verify the analytic lower envelope

```text
L(rho) = 0                              for 0 <= rho <= 7/32
L(rho) = (32 rho - 7)/125              for 7/32 <= rho <= 1.
```

2. For the positive lower branch, verify the dual inequality

```text
1{s>=5} >= [s(s-1)-3s]/45
```

on every `s in {0,...,9}`, and verify equality in expectation for a primal law
supported on `{0,4,9}`.
3. At `rho=0`, verify the upper certificate

```text
1{s>=5} <= 1/6 - s/6 + s(s-1)/12,
```

with equality for a primal law supported on `{1,2,5}` and tail `8/75`.
4. Verify a failing law for every `rho`: mix the certified `rho=0` upper
   witness with the common-shock `rho=1` law on `{0,9}`. Its tail must equal
   `8/75 + 7 rho/75 > 1/20`.
5. Verify the classification boundary `rho=53/128`, where `L(rho)=1/20`.
6. Independently enumerate all support-size-at-most-three LP vertices on a
   frozen rational audit grid. Exact agreement is an implementation check, not
   the continuum proof. Three support points suffice at an LP vertex because
   the feasible simplex has three equality constraints, including
   normalization.

## Registered interpretation

- **universally_pass:** impossible for every `rho in [0,1]` because a failing
  exchangeable law exists everywhere;
- **underdetermined:** `0 <= rho <= 53/128`, because both an admissible and an
  inadmissible law exist; and
- **universally_fail:** `53/128 < rho <= 1`, because the sharp lower envelope
  exceeds `1/20`.

Equality is admissible under the unchanged `<=1/20` rule.

## Claim boundary

The result is exact for finite exchangeable nine-bit laws with the first two
binomial moments fixed. It does not characterize nonexchangeable judge errors,
estimate any real verifier, or claim novelty over the discrete moment-problem
literature.
