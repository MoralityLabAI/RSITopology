# Behavioral acquisition of an additive semantic rectangle

Status: development-only. Not registered and not claim-eligible.

## Setting

Let `X=I x J` be a finite rectangle of base objects and consequence levels.
Assume preferences are defined on a mixture space containing `X`, a common
worst anchor `x_minus`, a common best anchor `x_plus`, and all objective
lotteries:

```text
L(p)=p x_plus+(1-p)x_minus,  p in [0,1].
```

Assume the Herstein-Milnor mixture-space conditions needed for an affine
utility representation and normalize:

```text
U(x_minus)=0,
U(x_plus)=1.
```

Suppose the population response to comparing `x` with `L(p)` has form

```text
Pr[x preferred to L(p)] = F(U(x)-p),
```

where `F` is strictly increasing and `F(0)=1/2`.

The registered population oracle returns one bit:

```text
Q(x,p)=1{Pr[x preferred to L(p)]>1/2},
```

with equality assigned to `0`.

## Theorem A: population acquisition

Strict monotonicity gives `Q(x,p)=1{U(x)>p}`.

Consequently, depth-`d` bisection localizes every `U(x)` to an interval of
width at most `2^-d`.

If every cell value belongs to the centered grid:

```text
G_d = {(2k+1)/2^(d+1): k=0,...,2^d-1},
```

then exactly `d` queries per cell recover the complete table. None of the
registered bisection thresholds is a centered grid point. This `N d` total is
sharp for the unrestricted `N`-cell grid class under the registered binary
interface:
there are `2^(Nd)` possible tables and at most `2^q` length-`q` transcripts.

## Theorem B: additive rectangle test and uncertainty geometry

Let `D` have one row for each `i>0,j>0`, with:

```text
(D U)_ij = U_ij-U_i0-U_0j+U_00.
```

Then:

```text
D U=0
```

if and only if there exist row effects `a_i`, consequence effects `c_j`, and
a constant `K` such that:

```text
U_ij=a_i+c_j+K.
```

If cellwise acquisition returns:

```text
U in U_hat + Box(eta),
```

then the complete interaction vector obeys:

```text
D U in D U_hat + D Box(eta).
```

For any interaction-space direction `q`, the outer set has exact support:

```text
h(q)=sum_x eta_x |(D^T q)_x|.
```

Therefore a declared maximum interaction tolerance can be accepted, rejected,
or left inconclusive without replacing shared cell errors by independent
residual errors.

### Proof

Theorem A follows from affine mixture utility:

```text
U(L(p))=pU(x_plus)+(1-p)U(x_minus)=p,
```

and strict monotonicity of `F`. Ordinary bisection gives the interval bound.
Centered grid points lie at the centers of the depth-`d` leaves, so they are
recovered exactly. The transcript count proves the lower bound.

For Theorem B, an additive table has zero cross-differences. Conversely, if
all cross-differences vanish, set:

```text
K=U_00,
a_i=U_i0-U_00,
c_j=U_0j-U_00.
```

The cross-difference equation gives `U_ij=a_i+c_j+K`. Linear propagation of
the cell box gives the residual zonotope. The support formula is the standard
support of a linear image of a box.

## Theorem C: exact finite-sample majority certificate

Assume every registered comparison has an independent correct-sign
probability at least `p_min>1/2`. For odd repeat count `r`, majority-vote
error is at most:

```text
B(r,p_min) =
sum_{k=0}^{(r-1)/2}
  binom(r,k) p_min^k (1-p_min)^(r-k).
```

If `Q B(r,p_min)<=delta`, then with probability at least `1-delta`, all `Q`
bisection signs are correct simultaneously and every resulting cell interval
and interaction zonotope covers its target.

No finite uniform repeat certificate exists over a response class allowing
`p_min=1/2`.

## Proposition D: finite mixture-affinity audit

For registered cells `x,y`, acquire the compound lottery
`z=w x+(1-w)y` with the same standard-gamble ruler. Under mixture affinity:

```text
U(z)-wU(x)-(1-w)U(y)=0.
```

If the three acquired values have radii `eta_z,eta_x,eta_y`, the exact
absolute support of this residual is:

```text
eta_z+w eta_x+(1-w)eta_y.
```

This gives conservative certify/reject/inconclusive decisions for each
registered mixture. Passing finitely many cells does not prove the global
mixture-space axioms.

## Proposition E: liveness and no-go controls

1. **Ordinal access is insufficient.** The tables
   `[[0,1/3],[2/3,1]]` and `[[0,1/9],[4/9,1]]` have the same deterministic
   order. The first is additive and the second has cross-difference `4/9`.

2. **Row-local standard-gamble rulers are insufficient.** The tables
   `[[0,1/4,1/2],[1/3,7/12,5/6]]` and
   `[[0,1/4,1/2],[1/2,2/3,5/6]]` have identical row-normalized coordinates
   `(0,1/2,1)`. Only the first is additive on one global scale.

3. **Complete coverage is necessary for a full-table certificate.** If any
   one cell is unmeasured, perturbing only that cell leaves every observed
   cell fixed and creates a nonzero cross-difference.

## Scope

The mixture-space representation, standard-gamble method, additive conjoint
representation, binary search, binomial tails, and support-function
calculus are classical. The proposed result is an ASMP-9 access ledger and
executable composition, not a novelty claim.

It assumes the behavioral model whose scalar object it recovers. It does not
validate expected utility, identify utility from deterministic rankings,
handle context-varying anchors, cover dependent responses, prove minimax
finite-sample constants, or resolve ASMP-9.
