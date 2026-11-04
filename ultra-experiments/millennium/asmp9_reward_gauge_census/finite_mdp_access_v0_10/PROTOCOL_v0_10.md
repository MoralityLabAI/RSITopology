# ASMP-9 finite-MDP access protocol v0.10

## Status

Prospective CPU-only exact verification protocol. The `S=2` and `S=3`
deterministic-kernel censuses, state counts through 16, four-coordinate
trajectory census, and all unit-test fixtures are burned.

## Frozen statements

For a known-temperature full-support entropy-regularized policy in a finite
MDP, one exact policy leaves the shaping ambiguity

```text
im G_(P,gamma),
G_(P,gamma)V(s,a)=V(s)-gamma E[V(s')|s,a].
```

Across a registered environment family, the common ambiguity is the
intersection of those shaping images.

Relative to a self-loop reference environment, a second kernel `P` leaves

```text
S-rank(A_P)
```

dimensions, where `A_P` contains within-state action differences of transition
rows. For deterministic `P`, this equals the component count of the
successor-difference graph.

The structured cyclic kernel has sharp access threshold two:

- one environment or one discount leaves `S` dimensions;
- self-loop plus cyclic transitions leaves one global constant; and
- the cyclic kernel under two distinct discounts leaves one global constant.

The matched deterministic-policy arm must remain nonidentifying: two
non-gauge rewards retain the same strict action identities in both
environments.

A direct one-step trajectory-comparison graph on `D=SA` reward coordinates
has ambiguity dimension equal to its component count and requires at least
`D-1` comparisons for constant-only ambiguity.

## Fresh cells

### Exact deterministic census

Enumerate all

```text
4^(4*2)=65,536
```

deterministic transition kernels for four states and two actions at discount
`2/3`. For every kernel, independently compute:

- successor-difference component count;
- `4-rank(A_P)`; and
- the exact block-system intersection dimension.

### Rational stochastic cells

Seed `1001001`: 4,096 strictly positive rational transition kernels with:

```text
states in 2..8;
actions in 2..3;
integer row weights in 1..17;
gamma in {1/5,1/3,1/2,2/3,4/5}.
```

Every shaping operator must have rank `S`, and every reference-pair
intersection must equal `S-rank(A_P)`.

### Structured access cells

Fresh state counts `17..32`, transition discount `2/3`, and discount pair
`(1/3,3/4)`. Each cell checks:

- single-environment ambiguity `S`;
- transition-pair ambiguity `1`;
- same-discount duplicate ambiguity `S`;
- distinct-discount ambiguity `1`; and
- the matched deterministic-policy non-gauge witness.

### Direct trajectory comparator

Enumerate all `2^15=32,768` undirected query graphs on six reward
coordinates. Compute both exact incidence rank and graph component count.

## Gates

- **G0 registration binding:** registration commit, implementation ancestry,
  clean tracked tree, and every sealed hash agree.
- **G1 stochastic coverage and shaping injectivity:** exactly 4,096 fresh
  cells execute; every registered state count, action count, and discount
  occurs at least once; and every shaping matrix has rank `S`.
- **G2 stochastic intersection formula:** every stochastic reference pair
  has intersection dimension `S-rank(A_P)`.
- **G3 deterministic component theorem:** all 65,536 deterministic kernels
  satisfy both exact dimension identities.
- **G4 deterministic liveness:** the census contains both connected and
  disconnected successor-difference graphs and all ambiguity dimensions
  `1..4`.
- **G5 transition/discount threshold:** every structured state count has
  ambiguity sequence `S -> 1`, while duplicating a discount stays at `S`.
- **G6 deterministic-policy obstruction:** every structured witness keeps a
  strict policy in both environments, has common soft-policy gauge dimension
  one, and differs by a nonconstant reward perturbation.
- **G7 trajectory component theorem:** all 32,768 query graphs have ambiguity
  equal to component count.
- **G8 trajectory sharpness:** no connected graph uses fewer than five
  queries, and at least one five-query connected graph exists.
- **G9 access separation:** every structured cell simultaneously exhibits
  constant-only soft-policy ambiguity and non-gauge deterministic-policy
  ambiguity.
- **G10 resource envelope:** the registered run uses no GPU, finishes within
  240 seconds, and its process peak resident set remains at or below 2 GiB.

All gates passing yields:

```text
finite_mdp_environment_access_geometry_verified
```

## Claim boundary

This is an exact finite access specialization of established
entropy-regularized IRL identifiability theory. It assumes population policies,
known entropy temperature, known finite transitions and discounts, and
registered state-action rewards. It is not finite-sample policy estimation,
unknown-temperature IRL, passive-trajectory identification, a general
environment-design optimum, or an ASMP-9 resolution.

## Resources

CPU only; 2 GiB process peak resident memory; 240 seconds; no GPU. The runner
records the operating-system peak working set and refuses a successful verdict
when either measured bound is exceeded.
