# ASMP-1 finite cut-response theorem and two obstructions

## 1. Registered finite-chain object

Let `X`, `H`, and `Y` be finite sets. A deterministic mechanism is

```text
h : X -> H,
g : H -> Y.
```

Every `x in X` is a registered environment and every `do(H=a)`, `a in H`, is a
registered intervention. Only `Y` is observed. Hidden names are gauge:
`Sym(H)` acts by

```text
(h,g) -> (pi composed with h, g composed with pi inverse),
```

and relabels the hidden intervention interface by the same `pi`. The exact
observation is therefore the natural output map `g composed with h` together
with the hidden-intervention table `g`, modulo one global hidden relabeling.

For `y in Y`, define

```text
X_y = {x in X : g(h(x))=y},  n_y = |X_y|,
H_y = {a in H : g(a)=y},     k_y = |H_y|.
```

## 2. Observation-fiber partition theorem

**Theorem 1.** Fix a realizable observation signature. Gauge orbits of
compatible mechanisms are in bijection with an independent set partition of
each labelled set `X_y` into at most `k_y` nonempty blocks. Consequently their
number is

```text
N = product_(y in Y) sum_(j=0)^k_y S(n_y,j),
```

where `S(n,j)` is a Stirling number of the second kind and `S(0,0)=1`.

If `h` is required to be surjective, every hidden state must be used and the
count becomes

```text
N_surj = product_(y in Y) S(n_y,k_y).
```

**Proof.** After choosing one representative of the observed intervention table
`g`, a compatible `h` must send every `x in X_y` into `H_y`. Two such maps are
gauge-equivalent precisely when a permutation within each fiber `H_y` converts
one to the other. The orbit invariant of a map `X_y -> H_y` is exactly the
partition of `X_y` into its nonempty inverse images. With unused hidden states
allowed, this partition may have any `j<=k_y` blocks; with surjective `h`, it
must have exactly `k_y`. Fibers for distinct `y` are independent, so their
counts multiply. QED.

**Corollary 1 (pointwise identifiability).** Without hidden-surjectivity, a
particular observation signature has one compatible orbit exactly when, for
every `y`, either `n_y<=1` or `k_y<=1`.

**Corollary 2 (surjective pointwise identifiability).** For a realizable
surjective signature, it has one compatible orbit exactly when every nonempty
fiber satisfies `k_y=1` or `k_y=n_y`.

**Corollary 3 (uniform cut-response injectivity).** Fix `g:H->Y`, let
`|X|>=2`, and range over the unrestricted class of all maps `h:X->H` (unused
hidden states are allowed). Full hidden interventions identify every such
upstream map `h` modulo the declared gauge if and only if `g` is injective.
Thus hitting a cut is not enough: registered downstream responses must separate
its states. This statement is not the corresponding uniform theorem for the
smaller class of surjective `h` maps.

**Proof.** If `g` is injective then every `k_y<=1`, so Corollary 1 gives one
orbit for every `h`. If `g` is not injective, choose distinct `a,b in H` with
`g(a)=g(b)` and distinct `x_1,x_2 in X`. One upstream map sends both inputs to
`a`; another sends `x_1` to `a` and `x_2` to `b` (and may agree elsewhere).
They have the same registered response but induce one versus two blocks in that
output fiber, so Theorem 1 places them in distinct gauge orbits. QED.

## 3. Downstream-aliasing counterexample

Take

```text
X = {0,1,2,3}, H = {a,b,c}, Y = {0,1},
g(a)=g(b)=0, g(c)=1,
h_left  = (a,a,b,c),
h_right = (a,b,b,c).
```

Both hidden maps and `g` are surjective. Both natural output vectors are
`(0,0,0,1)`, and every hidden intervention returns the same registered `g`
table. The residual gauge can only swap `a` and `b`; it cannot turn the input
partition `{0,1}|{2}` into `{0}|{1,2}`. The theorem gives
`S(3,2)S(1,1)=3` compatible surjective orbits.

This is a finite counterexample to bare node/cut coverage. It is not a
counterexample to the current generic analytic ASMP-1 conjecture, whose exact
meaning of "separates a cut" remains to be frozen.

## 4. Singleton-intervention design-rank theorem

Now let `f:{0,1}^n->{0,1}` be an observed Boolean output mechanism under the
uniform parent environment. Let `A_n` report the passive count of ones and the
counts under every singleton intervention `do(X_i=b)`. Regard a truth table as a
vector in `R^(2^n)`.

**Theorem 2.** The exact linear measurement design `A_n` has rank `n+1`.

**Proof.** Its rows are the constant function and the indicators
`1[X_i=0]`, `1[X_i=1]`. Since `1[X_i=0]+1[X_i=1]=1`, their span is contained in
the constant-plus-first-order coordinate functions. Conversely, the constant
and the `n` coordinate indicators are linearly independent on the Boolean cube,
so the rank is `n+1`. QED.

Thus singleton interventions leave a nullspace of dimension

```text
2^n - (n+1),
```

containing all unmeasured higher-order interaction directions.

For `n=3`, define truth-table one-sets (binary indices are `X1X2X3`)

```text
f^-1(1) = {011,100,111},
q^-1(1) = {011,101,110}.
```

They have identical passive and singleton-intervention measurements. Every
parent is essential. The observed output labels `0` and `1` are frozen semantic
labels, while parent-coordinate permutations and parent-bit flips are gauge.
Their sorted coordinate-influence multisets are `{1,3,3}` and `{3,3,3}`,
invariant under that gauge, so the tables are not gauge-equivalent. Their
difference lies exactly in `ker(A_3)`.

## 5. Replacement invariant suggested by the seed

Cut coverage is a support condition. Identifiability instead requires the
registered observation/intervention design to be injective on the permitted
mechanism quotient. Let a gauge group `G` act properly and isometrically on a
normed mechanism class `F`, with closed orbits, and let the registered design
`A` either be `G`-invariant or have a registered compatible isometric action
`G_A` on its observation space. After freezing the mechanism and observation
norms and their normalization, a representative-independent restricted
separation modulus is

```text
kappa_(F/G)(A)
  = inf_([f]_G != [q]_G)
      dist_(O/G_A)([A(f)]_[G_A], [A(q)]_[G_A])
      / dist_(F/G)([f]_G, [q]_G).
```

When `A` is itself gauge-invariant, the numerator reduces to the frozen norm
`||A(f)-A(q)||`. Exact identifiability is quotient injectivity (a trivial
quotient kernel). A positive separation modulus is the stronger stable-inverse
condition; stable noisy recovery additionally needs a registered sampling
bound. The ASMP-1 frontier is therefore better phrased as
**intervention-design tomography modulo functional symmetry**, with graph cuts
supplying necessary routing structure but not the complete invariant.

## Claim boundary

These are elementary finite theorems and exact counterexamples. They calibrate
ASMP-1 and sharpen its conjectured invariant. They do not prove transformer
mechanisms belong to this class, identify a real model circuit, or resolve the
analytic/noisy/sample-complexity problem. The abstraction here is a deterministic
local mechanism; equality of interventional marginals would not identify an
unregistered latent counterfactual/noise coupling.
