# Simulated ultra review: probability, noise, and lower bound

```text
review_kind = model_generated_internal_stress_test
qualifies_as_external_expert_receipt = false
verdict_on_probability_core = accept_with_nonmaterial_corrections
verdict_on_full_release = defer_to_complexity_major_revision
```

The probability/information-theory core is sound conditional on the frozen
message projection.

For `E_i` independent `Bernoulli(1/5)` variables, persistent across every
replication of atom `i`, write `rho=1-2/5=3/5`. If the ideal vector is uniform
on parity class `h`, then

```text
P_h(y) = 2^(-d) [1 + (-1)^(h+parity(y)) rho^d].
```

Consequently

```text
TV(P_0,P_1) = rho^d = (3/5)^d,
parity_error = (1-(3/5)^d)/2.
```

Returning the first response gives `a_H(k)<=1/5` for every `k>=1`. Repeated or
adaptive queries are a Markov kernel of the full persistent noisy vector, so
data processing cannot increase total variation. Uniform-prior averaging
correctly turns any pointwise constant completeness/soundness gap into a
contradiction as `d` grows.

## Corrections incorporated after the simulation

- The counterfamily now starts at `d>=2`; for `d=1`, one atom equals its parity.
- Advocate identities are fixed by claimed parity across both hypothesis
  classes, while the honest role switches with the true parity.
- The all-indices set has a canonical sorted encoding.
- Its cost is stated as `O(d)` word operations or `O(d log d)` bit time.

## Remaining boundary

The supplied enumerative and Fourier checkers certify the channel identity, not
the complete interactive game, oracle-access model, malformed behavior, or
absence of transcript side channels. Those are complexity/game-semantics proof
obligations.
