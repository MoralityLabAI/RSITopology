# ASMP-9 v0.27 development theorem: heterogeneous links and midpoint gauge

Status: development-only. The ingredients are classical threshold search,
Rasch/two-way additive identification, graph incidence algebra, and Hodge
residuals. Novelty is not claimed.

## 1. Cell-specific response links

Let `i` index anchored utility coordinates, `c` index contexts, and let
`H=(I disjoint-union C,E)` be the registered item-context access graph. Each
observed cell `e=(i,c)` has its own strictly increasing response link
`F_e`. A known offset `a` produces the population query

```text
Q_e(a) = sign(F_e(d_i+a)-1/2).
```

### Common-midpoint theorem

If every link has midpoint zero,

```text
F_e(0)=1/2,
```

then

```text
Q_e(a)=sign(d_i+a)
```

for every cell. Link shapes, slopes, and higher derivatives may vary
arbitrarily. One full-range cell per item is enough to recover every `d_i` by
the v0.26 threshold search.

The common response *shape* in v0.26 was therefore stronger than necessary;
the common midpoint was the operative invariant.

## 2. Arbitrary midpoint drift

Let cell `e` instead have unknown midpoint `b_e`:

```text
F_e(b_e)=1/2.
```

Full offset access identifies only

```text
z_e=d_i-b_e.
```

For any alternative item vector `d'`, define

```text
b'_e=b_e+d'_i-d_i.
```

Then `d'_i-b'_e=d_i-b_e` on every cell. Hence arbitrary cell-specific
midpoint drift makes the item utilities completely nonidentifiable, even with
unlimited population offset queries.

This is an exact access obstruction, not a finite-sample failure.

## 3. Context-only midpoint drift

Suppose the midpoint factors through context:

```text
b_e=b_c,
z_(i,c)=d_i-b_c.
```

Let `A_H` be the oriented incidence matrix of the bipartite graph, with `+1`
on item vertices and `-1` on context vertices. Then:

```text
z=A_H theta,
theta=(d,b).
```

The complete parameter gauge is

```text
ker(A_H),
```

which has one constant-shift direction per connected component. Therefore:

- parameters are identified modulo one common shift on each component;
- one global gauge remains exactly when `H` is connected; and
- disconnected components admit independent, observationally invisible
  shifts.

The incidence rank is

```text
rank(A_H)=|I|+|C|-components(H).
```

A spanning forest contains exactly that many edges and is sufficient to
reconstruct the quotient parameters when context-only drift is assumed.

## 4. Liveness of the context-only assumption

The factorization `z=A_H theta` is testable only through cycles. Its exact
obstruction dimension is

```text
beta_1(H)=|E|-|I|-|C|+components(H).
```

Equivalently, context-only midpoint drift holds if and only if every
independent cycle circulation of `z` vanishes.

- If `beta_1=0`, every edge assignment factorizes. The assumption is forced by
  design and a passing check is unavailable, not evidence.
- If `beta_1>0`, a spanning forest reconstructs the quotient parameters and
  the `beta_1` chords furnish independent compatibility checks.
- Fewer than `beta_1` independent exact linear checks leave a nonzero
  inconsistency direction in their kernel.

The smallest live design is the four-cell item-context square.

## 5. Robust reconstruction

For approximate localized thresholds

```text
z_hat=A_H theta+e,
```

least squares gives the minimum-norm quotient estimate. On the orthogonal
complement of the component gauges,

```text
||theta_hat-theta||_2
  <= ||e||_2 / sigma_min^+(A_H)
  = ||e||_2 / sqrt(lambda_min^+(L_H)).
```

The constant is the exact operator norm of the pseudoinverse. Thus
connectivity is only the exact identifiability boundary; the positive
Laplacian spectral floor is the robust boundary.

The residual

```text
rho=||(I-A_H A_H^+)z_hat||_2
```

is the exact Euclidean distance to the context-only midpoint model. Under an
edge-error budget `||e||_2<=epsilon`:

- `rho>epsilon` refutes the model;
- `rho<=epsilon` means compatible/inconclusive, not exact certification.

## 6. Claim boundary

The theorem does not establish that real demonstrators have shared or
context-only midpoints, that known reward-unit offsets are practically
available, that finite bisection certifies exact factorization, or that the
Euclidean norm is application-independent.

It is not a new Rasch, fixed-effects, graph-Hodge, synchronization, or
spectral-stability theorem. It is an ASMP-9 access and liveness ledger.

