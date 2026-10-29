# ASMP-9 v0.42.1 finite-sample risk-access result

## Verdict

`finite_sample_sequential_risk_access_confirmation_established`

All nine registered gates passed. Simultaneous uncertainty in finitely sampled
query channels can be propagated uniformly through every policy tree of a
frozen finite horizon and into a strict pass/fail/inconclusive directed-access
decision.

The mathematical result is a finite Lipschitz certificate:

```text
|Delta_P(A,B) - Delta_Phat(A,B)|
  <= max_theta [b_A(theta) + b_B(theta)],

b_A(theta)
  = loss_span(theta)
    min(1, h max_(q in A) TV(P_q(.|theta), P_hat_q(.|theta))).
```

The proof is a maximal-coupling simulation argument composed with upper
risk-polytope containment. Multinomial concentration, coupling/simulation
bounds, and comparison of finite experiments are classical. The contribution
is their ASMP-9-specific composition into a total access certificate.

## Registered sample

The run retained the v0.41 population fixture and changed only channel access:

- four targets;
- three symmetric binary query channels;
- 48,000 iid flip indicators per target/query;
- 192,000 pooled indicators per shared query parameter;
- horizon two;
- `alpha = 0.05`; and
- simultaneous query-TV radius
  `0.0035309243001648894`.

The seed was derived from the exact prereveal registration bytes after
registration commit `d522c44`. The stored seed hash is:

```text
957145b1d59e1f5a806e90d9129f365f803e1d569160cd6fb4c389d7e54decd7
```

### Sampled query channels

| Query | Population error | Empirical error | Absolute error |
|---|---:|---:|---:|
| `root_q` | `1/5` | `3833/19200` | `7/19200` |
| `left_q` | `1/4` | `3997/16000` | `3/16000` |
| `right_q` | `1/3` | `7999/24000` | `1/24000` |

Every error was below the simultaneous radius, so `H0` passed.

## Exact empirical polytopes and decisions

The sampled rational channels were compiled with the unchanged v0.41 exact
Bellman/LP implementation.

| Decision problem | Mode | Exact empirical deficiency | 95% simultaneous interval | Frozen decision |
|---|---|---:|---:|---|
| four-class identification | adaptive | `35942193143471/79594905600000` | `[0.44450214, 0.45862584]` | pass |
| four-class identification | open-loop | `532511844633/1024563200000` | `[0.51268339, 0.52680709]` | fail |
| asymmetric root group | adaptive | `3833/43200` | `[0.08401895, 0.09343475]` | pass |
| asymmetric root group | open-loop | `3833/43200` | `[0.08401895, 0.09343475]` | pass |

All four intervals contain their exact population deficiencies:

```text
classification/adaptive = 61/135
classification/open_loop = 13/25
root_group/either mode = 4/45.
```

Classification used tolerance `1/2`; root-group loss used tolerance `1/10`.
Every decision also cleared the registered strict practical margin `1/1000`.
The point estimate alone could not open access.

## Gates

| Gate | Requirement | Result |
|---|---|---|
| `P0` | 26 combined preregistration tests | pass |
| `S0` | every sealed source/environment hash matches | pass |
| `U0` | exact sample, target, query, seed, and pooling universe | pass |
| `H0` | simultaneous query-channel event | pass |
| `C0` | all population deficiencies contained | pass |
| `A0` | classification adaptive pass/open-loop fail | pass |
| `D0` | both group-loss modes pass | pass |
| `R0` | exact two-problem by two-mode output | pass |
| `RESOURCE` | 900 seconds and 1.25 GiB working-set ceilings | pass |

The registered execution took `159.282717` seconds. Its recorded peak working
set was `77,377,536` bytes.

## Versioned repair record

The original v0.42 executor stopped before seed derivation or sampling because
it tried to evaluate:

```python
float("1/1000")
```

No v0.42 scientific result exists. The failure registration, normalized
traceback, and hashes remain in the parent directory. Version v0.42.1 changed
only rational parsing, added the literal regression test, generated a new
environment lock and registration, and derived a fresh version-separated
seed. No scientific threshold, sample count, gate, or resource ceiling
changed.

## Verification

- implementation commit: `9b2de93`;
- repair registration commit: `d522c44`;
- registration SHA-256:
  `0a4c40833c8fe58e8a620a7a6bb7759956c616ab9bc3bd2a0aa9eb55aa3bf6f0`;
- result file SHA-256:
  `2b4a20d7e347e54f5467bd3306202697f9638256c2d1505a1bb741f2bb7aa450`;
- stored result-content hash:
  `b686c61c830aebb8cfb416e5113758831bc56a34f6d41712a173df6bc2a6ab2c`;
- independent replay SHA-256:
  `718edcfed18ac101cc617e83d19ec12dceb25131d07b706eaa7c0d9bb317e710`.

The independent replay reproduced the entire sampled payload and all
non-resource gates exactly.

## Resolution impact

This closes one named v0.41 gap:

> confidence-valid finite-sample certification for iid unknown finite query
> channels at a fixed finite horizon and registered decision type.

It does **not** close:

- matching minimax sample-complexity rates;
- efficient policy search;
- continuous or unbounded-horizon experiment classes;
- correlated, adaptive, or strategic source misspecification;
- unknown or changing decision types;
- a calibrated physical or real-model query channel; or
- ASMP-9 itself.

The next load-bearing mathematical target is the sharp modulus of directed
deficiency under channel perturbation: either match the current
`O(h^2/g^2)` confidence upper rate with a lower witness, or replace the
union-bound horizon factor with a strictly sharper policy-uniform recursion.
