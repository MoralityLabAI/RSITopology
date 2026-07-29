# ASMP-9 v0.32 development note

## The missing access step

Versions v0.30-v0.31 assume a scalar comparison table and deterministic source
widths. The next question is not another propagation formula. It is whether a
declared behavioral interface can produce that table, test its additive
structure, and expose the uncertainty correlations needed by v0.31.

## Candidate access grammar

Let the finite semantic rectangle be `X=I x J`. The demonstrator has
preferences over a mixture space containing:

- every deterministic cell `x in X`;
- one global worst anchor `x_minus`;
- one global best anchor `x_plus`; and
- every registered objective lottery
  `L(p)=p x_plus+(1-p)x_minus`.

The positive theorem assumes the mixture-space axioms needed for a common
affine utility representation and normalizes:

```text
U(x_minus)=0,
U(x_plus)=1.
```

Population comparisons use a common strictly increasing response link with
midpoint one half. The registered oracle returns the one-bit indicator that
the choice probability is strictly above one half, assigning equality to the
non-positive branch. Therefore:

```text
1{Pr[x preferred to L(p)]>1/2} = 1{U(x)>p}.
```

This is the standard-gamble ruler. The link shape need not be known at
population level.

## Registered model-falsification checks

Acquiring one certainty equivalent per cell does not by itself validate
mixture affinity. A finite instrument must give the assumed representation an
opportunity to fail.

For registered cells `x,y` and weight `w`, acquire the compound lottery

```text
z = w x + (1-w)y
```

with the same global standard-gamble ruler. Mixture affinity predicts:

```text
U(z)=wU(x)+(1-w)U(y).
```

If the three acquired values have interval radii
`eta_z,eta_x,eta_y`, the residual support is exactly:

```text
eta_z + w eta_x + (1-w) eta_y.
```

The protocol must include both a consistent mixture and a planted
probability-weighting violation. Passing finitely many checks establishes
only registered-cell consistency, not the global mixture-space axioms.

## Why the global anchors are load-bearing

Two exact no-go witnesses prevent the access assumption from disappearing
into prose.

### Ordinal-only witness

```text
additive table       [[0,1/3],[2/3,1]]
same-order table     [[0,1/9],[4/9,1]]
```

The second table is obtained by a strictly increasing square transform. Every
deterministic ranking is preserved, but its rectangle cross-difference is
`4/9`, not `0`. Deterministic ordinal access cannot decide additive cardinal
structure.

### Row-local-ruler witness

```text
additive table       [[0,1/4,1/2],[1/3,7/12,5/6]]
interacting table    [[0,1/4,1/2],[1/2,2/3,5/6]]
```

Normalizing each row by its own endpoints produces `(0,1/2,1)` in both rows
for both tables. Row-local standard gambles therefore agree, while only the
first table has a common additive consequence scale. A global ruler or an
independently justified scale-gluing condition is necessary.

## Candidate finite theorem

For unrestricted values on a centered dyadic grid with `2^d` levels, `d`
binary standard-gamble answers identify one cell exactly. A rectangle with `N=|I||J|`
unknown cells therefore needs and admits `Nd` binary queries in this grammar.
The lower bound is the transcript-counting bound over `2^(Nd)` tables.

For continuous values, depth `d` gives a cell interval of width `2^-d` and
midpoint radius `2^(-d-1)`.

Let `D_rect` be the anchored cross-difference matrix:

```text
(D_rect U)_(ij) = U_ij-U_i0-U_0j+U_00.
```

Then:

```text
D_rect U=0
```

if and only if `U_ij=a_i+c_j+K`. If the acquired cell centers are `U_hat`
and the cellwise localization radii are `eta`, then:

```text
D_rect U in D_rect U_hat + D_rect Box(eta).
```

For any residual direction `q`, the exact support is:

```text
h(q) = sum_x eta_x |(D_rect^T q)_x|.
```

This is the behavioral source geometry that can be passed to v0.31. It is
strictly better than treating every residual as an independent four-cell
error because the same acquired cell appears in multiple cross-differences.

## Finite-sample gate

If every registered standard-gamble response has correct-sign probability at
least `p_min>1/2`, an odd majority of `r` repeated responses has exact error

```text
sum_{k=0}^{(r-1)/2}
  binom(r,k) p_min^k (1-p_min)^(r-k).
```

The smallest odd `r` whose error times the total query count is at most
`delta` gives a simultaneous union-bound certificate. In the development
cell:

```text
rectangle cells             12
bisection depth              4
population queries           48
p_min                        3/4
family error                 1/100
minimum odd repeats          43
```

At `p_min=1/2`, no finite repeat count can certify the sign. This preserves
the flat-link boundary already isolated in v0.26.

## Proposed three-state output

For a declared interaction tolerance `epsilon`, each cross-difference has an
interval determined by its center and exact box support:

- `approximately_additive_certified` if the upper absolute bound is at most
  `epsilon`;
- `interaction_certified` if the lower absolute bound is strictly greater
  than `epsilon`; and
- `inconclusive` otherwise.

Equality is accepted only on the conservative upper-bound side and never on
the rejection side.

## Claim boundary

The positive theorem is conditional on mixture-affine preferences, common
global anchors, objective lotteries, a shared response midpoint, and a
declared finite-sample margin. The finite compound-lottery audit can reject
the model on registered cells but cannot prove the axioms globally. These
assumptions are substantive and empirically fragile.

The candidate does not show that humans or models satisfy expected utility,
that arbitrary outcomes can be mixed, that anchors are context-invariant,
that stated and revealed preferences agree, or that a scalar latent value
exists outside the registered interface.
