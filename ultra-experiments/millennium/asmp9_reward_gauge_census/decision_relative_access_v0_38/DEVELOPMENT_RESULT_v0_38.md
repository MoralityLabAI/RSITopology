# ASMP-9 v0.38 burned development result

## Status

`instrument_discriminating_confirmation_not_registered`

The result below was used to validate and shape the instrument. It is burned
development evidence and cannot become an unseen confirmation result.

## Reward and policy grammar

There are three deterministic policies with occupancy rows

```text
pi_0 = (1,0,0)
pi_1 = (0,1,0)
pi_2 = (0,0,1).
```

The three decision classes have representatives

```text
r_0 = (1,0,0)
r_1 = (0,1,0)
r_2 = (0,0,1).
```

Each also has the representative `r_theta + (1,1,1)`. The nuisance bit
selects the representative. Constant shifts are the licensed gauge and leave
the frozen policy-regret matrix unchanged:

```text
L = [[0,1,1],
     [1,0,1],
     [1,1,0]].
```

The nuisance law is uniform and independent of the target.

## Query grammar

- `q_target_0` returns one with probability `3/4` under `theta=0` and
  `1/4` otherwise.
- `q_target_1` returns one with probability `3/4` under `theta=1` and
  `1/4` otherwise.
- `q_gauge_shift` reveals the nuisance representative exactly.
- Registered query outputs are conditionally independent.
- Full access contains all three queries.

For target-relative comparison the gauge-only ancillary is removed after
the declared nuisance marginalization. Expanded comparison retains it.

## Exact census

| Access family | `G_D` | `delta_D` | Expanded deficiency |
| --- | ---: | ---: | ---: |
| none | `4/15` | `7/24` | `13/24` |
| `q_target_0` | `6/35` | `1/4` | `1/2` |
| `q_target_1` | `6/35` | `1/4` | `1/2` |
| `q_gauge_shift` | `4/15` | `7/24` | `7/24` |
| both target queries | `0` | `0` | `1/2` |
| `q_target_0` + gauge | `6/35` | `1/4` | `1/4` |
| `q_target_1` + gauge | `6/35` | `1/4` | `1/4` |
| all three | `0` | `0` | `0` |

All values are exact fractions backed by checked primal-dual LP
certificates.

## What the fixture establishes

1. At tolerance `epsilon=0`, the unique inclusion-minimal target-relative
   access family is the pair of target queries. Adding the gauge query cannot
   improve `delta_D`.
2. Removing either target query raises `delta_D` exactly to `1/4`.
3. At tolerance `epsilon=1/4` with a weak-inequality pass rule, either one
   target query is sufficient.
4. The two target queries have zero target-relative deficiency even though
   they cannot reconstruct the raw reward representative. Expanded
   deficiency charges the missing nuisance bit by `1/2`.
5. The gauge-only query improves expanded reconstruction while leaving the
   target-relative result exactly equal to having no query.

Thus the instrument distinguishes:

- optimized value;
- uniform risk-vector transfer for the registered policy decision type; and
- full target-by-nuisance experiment simulation.

## What it does not establish

This fixture was designed to contain one licensed constant-shift gauge and
two target-relevant queries. It is not confirmation evidence, a general
reward-learning theorem, evidence about human inconsistency, or a real-model
measurement. It only establishes that the proposed v0.38 instrument and
access question are non-vacuous enough to preregister a disjoint successor.

