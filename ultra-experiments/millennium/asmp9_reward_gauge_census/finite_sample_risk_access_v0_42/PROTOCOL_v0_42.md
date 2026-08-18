# ASMP-9 v0.42 finite-sample risk-access protocol

## Question

Can uncertainty in finitely sampled query channels be propagated through every
adaptive policy tree and into a non-discretionary access decision?

The population fixture is the already sealed v0.41 three-query, four-target
experiment. Reusing that population is deliberate: v0.42 changes only the
access condition from known rational channels to iid channel samples. It is
not a claim of fixture generalization.

## Estimand and theorem

The estimand is directed deficiency from the sampled source library to exact
perfect revelation, separately for:

- four-target zero-one classification; and
- the asymmetric root-group loss.

For each target `theta`, terminal loss span `s(theta)`, horizon `h`, and a
simultaneous channel event

```text
TV(P_q(.|theta), P_hat_q(.|theta)) <= eta(theta,q),
```

the registered policy-uniform radius is

```text
b(theta)
  = s(theta) min(1, h max_q eta(theta,q)).
```

The directed-deficiency interval has half-width

```text
max_theta [b_source(theta) + b_reference(theta)].
```

Perfect revelation is exact here, so `b_reference = 0`. See
`THEOREM_DRAFT_v0_42.md` for the coupling and upper-set proof.

## Sampling and seed

Each query retains the v0.41 symmetric binary flip probability shared across
four targets. The run draws 48,000 flip indicators per target/query and pools
the four counts to estimate one error probability per query.

Sampling uses keyed BLAKE2b streams with rejection sampling into the exact
rational denominator. The 32-byte key is:

```text
SHA256(
  exact_registration_bytes
  || NUL
  || "asmp9-v0.42-sampled-confirmation"
).
```

The seed therefore cannot be evaluated until the write-once registration
exists. Every target/query count is emitted.

## Confidence construction

For `Q=3` shared binary query parameters, `Theta=4` targets, `n=48000`
samples per target/query, and `alpha=0.05`, the frozen radius is:

```text
eta
  = sqrt(log(2Q/alpha)/(2 Theta n))
  = 0.0035309243001648894... .
```

Logarithms and square roots are evaluated at 80 decimal digits and converted
outward to binary float. The shared-query radius is simultaneous over all
three parameters. The generic implementation also supports Bonferroni
Weissman radii over a frozen multinomial cell universe.

## Decisions and pre-run arithmetic

All comparisons are strict. Equality is inconclusive.

| Decision type | Tolerance | Practical margin |
|---|---:|---:|
| four-class identification | `1/2` | `1/1000` |
| root-group asymmetric loss | `1/10` | `1/1000` |

The population deficiencies are already known from v0.41. Accounting both for
movement of the empirical point away from the population value and for the
confidence interval around that empirical point gives:

| Arm | Adverse event-bound value | Required comparison |
|---|---:|---|
| classification, adaptive | `0.46597555` | `< 0.499` |
| classification, open-loop | `0.50587630` | `> 0.501` |
| root-group, either mode | `0.09830469` | `< 0.099` |

Consequently, the four decisions are forced on the simultaneous channel event:

```text
classification/adaptive -> pass
classification/open_loop -> fail
root_group/adaptive -> pass
root_group/open_loop -> pass
```

## Gates and total status

- `P0`: exact preregistration test count passes.
- `S0`: every sealed source and environment hash matches.
- `U0`: the exact sample universe, pooling rule, and registration-derived seed
  are preserved.
- `H0`: the visible synthetic population lies in the simultaneous channel
  event.
- `C0`: all four exact population deficiencies lie inside their intervals.
- `A0`: classification returns pass/fail as frozen.
- `D0`: both group-loss modes pass as frozen.
- `R0`: exactly four arm rows are emitted.
- `RESOURCE`: one process remains within 900 seconds and 1.25 GiB peak working
  set.

If `H0` fails, the outcome is
`not_established_by_registered_channel_event`; it is not a theorem
refutation. If `H0` passes but `C0` fails, the outcome is
`theorem_or_implementation_failure`. Only all gates passing returns
`finite_sample_sequential_risk_access_confirmation_established`.

## Claim boundary

This is a confidence-valid finite-sample specialization of classical
multinomial concentration, coupling/simulation bounds, and comparison of
finite experiments. It does not establish optimal confidence regions,
matching minimax lower bounds, strategic-source robustness, continuous
channels, real-model access, or ASMP-9 resolution.
