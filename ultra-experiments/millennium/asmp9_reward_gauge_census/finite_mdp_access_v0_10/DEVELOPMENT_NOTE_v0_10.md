# ASMP-9 v0.10 development note

## Burned exact checks

Development enumerated every deterministic two-action kernel for:

```text
S=2: 16 kernels;
S=3: 729 kernels.
```

Relative to the self-loop reference environment, the exact shaping-subspace
intersection dimension agreed in every case with both:

```text
S-rank(action-difference matrix)
```

and the number of successor-difference graph components.

The component distributions were:

| states | ambiguity 1 | ambiguity 2 | ambiguity 3 |
|---:|---:|---:|---:|
| 2 | 12 | 4 | — |
| 3 | 408 | 294 | 27 |

The cyclic two-action family was also checked at
`S in {2,3,4,8,16}`:

- one environment left ambiguity dimension `S`;
- self-loop plus cyclic transition kernels left dimension `1`; and
- the cyclic kernel at discounts `1/2` and `3/4` left dimension `1`.

The registered deterministic-policy witness retained the same strict
action-zero policy under both environments while changing one action-one
reward by `1/2`. The perturbation was not a common global constant.

Finally, all 64 one-step trajectory-query graphs on four reward coordinates
matched the component-count law. Their ambiguity-dimension distribution was:

```text
dimension 1: 38 graphs
dimension 2: 19 graphs
dimension 3:  6 graphs
dimension 4:  1 graph
```

These cells are burned. A prospective run must use a larger deterministic
kernel universe, fresh stochastic kernels, and a larger trajectory-query
registry.

## Prior-art consequence

The two-environment and two-discount recovery-up-to-constant claims are not
novel: Cao, Cohen, and Szpruch (2021) already prove the general
entropy-regularized identifiability result. The viable contribution is the
explicit access grammar, component-count specialization, exact finite
instrument, and matched deterministic-policy obstruction.
