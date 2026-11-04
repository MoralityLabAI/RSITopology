# ASMP-1 representation boundary and linear-gauge theorem v0.2

## 1. Registered object

Let `X` be a mechanism class, let

```text
O : X -> Y
```

be the complete registered observation/intervention map, and let

```text
T : X -> Z/G
```

be the declared abstraction `Q` after quotienting the frozen functional
symmetry `G`. Equality in `Z/G` means equality of declared mechanism orbits,
not equality of parameter names.

Define

```text
x ~O x'  iff  O(x)=O(x'),
x ~T x'  iff  T(x)=T(x').
```

The encoding language for `X`, `O`, `T`, and `G` is part of the problem
instance. This is load-bearing: a rational-polynomial description and a
program that names an arbitrary computable real do not have the same decision
theory.

## 2. Universal fiber-factorization theorem

**Theorem 1 (maximal identifiable information).** The following are
equivalent:

1. `T` is identifiable from the registered experiment;
2. `~O` refines `~T`;
3. every observation fiber lies inside one target orbit;
4. there is a unique map

   ```text
   T_bar : O(X) -> Z/G
   ```

   such that `T = T_bar composed_with O`.

The observational quotient `X/~O`, equivalently the image experiment `O(X)`,
is universal among identifiable abstractions: every identifiable target
factors uniquely through it. It therefore retains the maximum information
that this experiment can justify. A proposed graph-cut condition is valid only
if it implies this factorization without defining cut separation to mean the
factorization itself.

**Proof.** If `T` is identifiable, define `T_bar(O(x))=T(x)`. This is
well-defined exactly because equal observations imply equal targets, and it is
unique because every point of `O(X)` has the form `O(x)`. Conversely, a
factorization gives `O(x)=O(x') => T(x)=T(x')`. The equivalence with refinement
and fiber containment is the same implication written as relations or sets.
QED.

Suppose `Y` and `Z/G` have registered metrics. Define the normalized quotient
separation modulus

```text
kappa_T(O)
  = inf_(T(x) != T(x'))
      d_Y(O(x),O(x')) / d_(Z/G)(T(x),T(x')).
```

**Theorem 2 (stable factorization).** `kappa_T(O)>0` if and only if the
factor map `T_bar` is globally `1/kappa_T(O)`-Lipschitz on `O(X)`.

**Proof.** Substitute `y=O(x)` and `y'=O(x')` in the Lipschitz inequality and
rearrange. Pairs with equal target do not constrain the ratio. QED.

Thus exact identifiability is fiber refinement; stable identifiability is a
quantitative inverse condition. The latter is stronger. Calling a promised
positive `kappa` an assumption is legitimate only if its value has an
independent certificate; otherwise the promise contains the hard part of the
problem.

## 3. Effective representation boundary

### 3.1 Rational semialgebraic lane

Assume:

- `X=Theta` is a compact rational semialgebraic set;
- `O` and `Q` are rational polynomial maps; and
- `G` is a finite explicitly listed group of rational polynomial actions.

Failure of exact identifiability is the sentence

```text
exists theta,theta' in Theta:
    O(theta)=O(theta')
    and
    for every g in G, Q(theta') != g.Q(theta).
```

All membership, equality, and finite-orbit clauses expand into a first-order
formula over a real closed field. The same is true of failure of a fixed
rational separation margin `kappa>0`, after squaring norms and expanding the
finite minimum over `G`.

**Theorem 3 (semialgebraic decidability).** Exact quotient identifiability and
validity of any fixed rational global separation margin are decidable in this
lane by quantifier elimination. Existence of some positive semialgebraic
margin is also first-order decidable by quantifying `kappa`.

This is a decidability theorem, not a polynomial-time theorem. General
real-closed-field quantifier elimination can be prohibitively expensive.

### 3.2 Computable-real analytic lane

A computable real is supplied by a program that, on input `n`, returns a
rational within `2^-n` of the named real. This is a finite exact encoding with
a registered modulus.

For a Turing machine `e`, define

```text
c_e = 0       if e never halts,
c_e = 2^-t    if e first halts at step t.
```

There is a uniform Cauchy-name program for `c_e`: on precision input `n`,
simulate `e` for `n` steps; return `2^-t` if it has halted by step `n`, and
return zero otherwise. If it first halts later, the error is
`2^-t < 2^-n`.

Now use the entire analytic mechanism

```text
Y_e(X,A)=(1+c_e)X+A,  (X,A) in [0,1]^2.
```

Compare it with the base mechanism `Y_0(X,A)=X+A`. Register environment
`(X,A)=(0,0)` and intervention `do(A=1)` at `X=0`, freeze
`T(Y)=Y(1,0)`, and use the identity gauge. The two models always have the same
registered laws, namely zero and one. Every local derivative is at least one,
and the registered intervention has effect one, so the construction has
uniform local conditioning and intervention-strength margins
`kappa_local=gamma=1`. Their targets agree exactly when `e` never halts.

This is a finite two-model class with three typed scalar nodes, two active
edges, in-degree two, deterministic noise, covering number at most two,
infinite analytic radius, and norm bound `B=5/2` on `[0,1]^2`. The target is a
single bounded-complexity evaluation functional.

**Theorem 4 (uniform undecidability).** No total algorithm decides exact
ASMP-1 target identifiability for all program-encoded computable-real analytic
instances, even for two degree-one entire mechanisms with two scalar parents,
one output, norm at most `5/2`, uniform local conditioning and intervention
strength at least one, and identity gauge.

**Proof.** If a total identifiability decider existed, apply it to
`{Y_0,Y_e}`. It returns identifiable exactly when `c_e=0`, hence exactly when
`e` does not halt. Negating its answer decides whether `e` halts, contradicting
undecidability of the halting problem. QED.

The same reduction does not require a Cauchy program to appear as one opaque
coefficient. Define the rational Taylor coefficients

```text
a_(e,n) = 1  if e first halts at step n,
a_(e,n) = 0  otherwise,
h_e(X) = sum_(n>=1) a_(e,n) X^n.
```

Every coefficient is a one-bit rational computable by simulating exactly `n`
steps, and at most one coefficient is nonzero. Hence `h_e` is either zero or
one monomial and is entire. On `0<=X<=1/2`, simulating through step `n` gives
uniform error at most `2^-n`: any still-undiscovered monomial has degree
greater than `n`. Moreover,

```text
h_e(1/2)=c_e.
```

Replacing the mechanism above by

```text
Y_e(X,A)=X+A+h_e(X)
```

therefore gives the same reduction with a finite program that generates only
rational Taylor coefficients and has an explicit evaluation modulus. Its
local derivatives and registered `do(A=1)` effect remain at least one.

For this rational-Taylor form, restrict `X in [0,1/2]` and `A in [0,1]`.
Then a canonical parameter binding is

```text
n=3 typed scalar nodes, s=2, d=2, p=1,
F={Y_0,Y_e}, covering number <=2,
analytic radius=infinity, B=2, deterministic noise,
kappa_local=1, gamma=1,
E={(X,A)=(0,0)}, I={do(A=1) at X=0},
Q(Y)=Y(1/2,0), G={identity}.
```

Every coefficient of the generated Taylor series has bit complexity one; the
finite program and the machine index supply the remaining encoding length.
Evaluating to error `2^-n` uses at most `n` simulated machine steps plus
rational arithmetic at precision `n`.

The reduction does not hide an exceptional parameter inside a positive-
dimensional family. For each machine index, `F` is a finite zero-dimensional
semantic class and the identifiability statement holds or fails on the entire
class. Under counting measure there is no null exceptional set; under the
zero-dimensional algebraic reading each distinct semantic mechanism is its own
component. Declaring the coincident nonhalting representation “nongeneric”
would require deciding the same semantic equality used in the reduction.

The obstruction disappears under a valid certified gap promise: if the input
also proves `c_e=0` or `|c_e|>=kappa` for a supplied rational `kappa>0`, finite
precision separates the two cases. The certificate, not analyticity alone,
crosses the computability boundary.

**Corollary 4.1 (the `kappa` fork).** If the canonical `kappa>0` is a global
lower bound on

```text
d_Y(O(x),O(x')) / d_(Z/G)(T(x),T(x'))
```

over every distinct target pair, Theorem 2 shows that target identifiability is
already assumed and the proposed characterization is circular. If `kappa`
instead means local mechanism conditioning, Theorem 4 respects
`kappa_local=gamma=1` and the uniform exact classification problem remains
undecidable. No third interpretation is supplied by v0.1.

## 4. Sharp tractable theorem for linear analytic mechanisms

Let `V=R^d` be a linear parameter realization and let `N` be the full declared
redundant-encoding subspace. Translation by `N` is the registered gauge, so the
mechanistic target is

```text
z = P_(N_perp) theta in N_perp,
q = dim(N_perp).
```

The registered scalar environment/intervention rows form

```text
A : V -> R^m,
```

and gauge compatibility requires `N subseteq ker(A)`. Let

```text
A_bar = A restricted_to N_perp.
```

Assume the mechanism class contains a neighborhood in the quotient coordinates
so every sufficiently small non-gauge kernel direction is admissible. Linear
maps are analytic, and the rows may be arbitrary registered linear response
functionals induced by environments or interventions.

**Theorem 5 (exact linear-gauge boundary).** The following are equivalent:

1. the quotient target `z` is uniformly identifiable;
2. `ker(A)=N`;
3. `A_bar` has column rank `q`;
4. the registered rows span the dual quotient `(N_perp)^*`.

When they hold, the constructive recovery map is

```text
z_hat = A_bar^dagger y.
```

The minimum number of scalar query types is at least `q`; exactly `q` suffice
whenever the admissible row family contains a quotient basis.

**Proof.** Because `N subseteq ker(A)`, observations depend only on `z`.
Two quotient points collide precisely when their difference lies in
`ker(A_bar)`. Hence uniform identification is equivalent to
`ker(A_bar)={0}`, column rank `q`, and row-span equality. A full-column-rank
matrix has `A_bar^dagger A_bar=I_q`. Rank is at most `m`, proving `m>=q`;
a quotient basis attains equality. QED.

This quotient is justified rather than post hoc: `N` is frozen as the complete
kernel of the parameter-to-mechanism realization, not chosen after seeing
which directions the experiment misses.

**Theorem 6 (stability and finite samples).** Let

```text
kappa = sigma_min(A_bar)>0.
```

With `N_rep` independent observations per row,

```text
Y_(j,l) = (A theta)_j + xi_(j,l),
xi_(j,l) iid Normal(0,sigma^2),
```

apply the pseudoinverse to the row means. With probability at least `1-delta`,

```text
||z_hat-z||_2
  <= sigma/(kappa sqrt(N_rep))
     [sqrt(q)+sqrt(2 log(1/delta))].
```

Therefore it suffices that

```text
N_rep
  >= sigma^2 [sqrt(q)+sqrt(2 log(1/delta))]^2
     / (kappa^2 epsilon^2).
```

**Proof.** Only the projection of the isotropic row-mean noise onto the
`q`-dimensional column space affects the pseudoinverse. Its norm is bounded by
the standard Gaussian norm concentration inequality, and the pseudoinverse
operator norm is `1/kappa`. QED.

The same proof works for registered sub-Gaussian noise with the corresponding
vector concentration constant.

**Theorem 7 (matching negative branch).**

1. If `rank(A_bar)<q`, a nonzero quotient vector `v` lies in the exact kernel.
   Two sufficiently close admissible mechanisms separated by `v` induce
   identical laws for every sample count. No estimator can uniformly recover
   both.
2. If `m<q`, rank deficiency is unavoidable, giving the matching scalar-query
   lower bound `q`.
3. If `kappa>0` is attained in direction `v` and the quotient class contains
   `+/-2 epsilon v`, then any estimator with error at most `epsilon` and
   failure probability at most `delta<1/4` at both points requires

   ```text
   N_rep
     >= sigma^2 log(1/(4 delta))
        / (8 kappa^2 epsilon^2).
   ```

**Proof.** Parts 1 and 2 are the kernel and rank arguments above. For part 3,
the two Gaussian experiments have mean separation `4 epsilon kappa` and
Kullback-Leibler divergence

```text
8 N_rep epsilon^2 kappa^2 / sigma^2.
```

An `epsilon`-accurate estimator distinguishes the two points. The
Bretagnolle-Huber two-point bound then gives the displayed necessary
condition. QED.

The upper and lower bounds match in `kappa^-2`, `epsilon^-2`, and
`log(1/delta)`; the upper bound additionally pays the quotient dimension
needed for simultaneous Euclidean recovery.

## 5. Consequence for ASMP-1

There is no representation-independent polynomial recovery theorem for the
v0.1 schema:

- the exact criterion is fiber factorization;
- its effective decidability depends on the registered encoding;
- rational semialgebraic instances are decidable but not uniformly promised
  polynomial-time;
- arbitrary computable-real analytic instances are uniformly undecidable
  without a certified separation promise; and
- a linear-gauge subclass has the complete four-part constructive boundary.

Accordingly, a repaired ASMP-1 must choose an effective representation lane.
“Analytic with bit complexity” is not sufficient unless it states whether
coefficients are rational/algebraic, semialgebraic, oracle-computable with a
gap certificate, or arbitrary computable reals.

## 6. Claim boundary

Theorems 1, 2, and 5-7 are elementary factorization, linear inverse-problem,
and Gaussian testing facts assembled into the ASMP-1 obligations. Theorem 3 is
an application of real-closed-field quantifier elimination. Theorem 4 is a
self-contained halting reduction closely related to the classical
undecidability of equality for computable reals.

This result does not give a polynomial algorithm for arbitrary nonlinear
semialgebraic SCMs, certify that a learned transformer abstraction belongs to
the linear class, or prove that a declared `Q` captures all safety-relevant
mechanism content.
