# ASMP-1 cut-separation audit result v0.1

## Verdict

The exact harness passes all registered internal gates and gives a convincing
reason to stop attempting a theorem for ASMP-1 v0.1 as written:

> The Cut-Separation Conjecture is not a closed mathematical iff. Under its
> literal full-mechanism excitation reading, necessity fails. Under three
> strong structural hypergraph readings of cut separation, sufficiency fails.
> Under a global quotient-separation reading, the condition assumes the desired
> identifiability and becomes circular.

This result does **not** resolve the broader ASMP-1 classification program. It
locates the definition choices that must be frozen before that program has a
single truth value.

## Exact necessity obstruction

Let a three-parent analytic Bernoulli SCM have conditional response

```text
p_theta(x) = sum_(T subseteq {1,2,3}) theta_T chi_T(x)
```

on an interior parameter neighborhood. Let the environment observe only
`x=(-1,-1,-1)`, let the declared gauge be the identity, and freeze the
nonconstant abstraction

```text
Q(theta) = p_theta(-1,-1,-1).
```

The observation design has rank one on the eight-dimensional local mechanism
class, while the full set of parent configurations has rank eight. Nevertheless
`Q` is exactly the observed scalar, so it is identifiable for every admissible
model.

Therefore the condition that environments excite every parent configuration
needed to distinguish the registered **local mechanism class** is not necessary
for identification of an independently frozen, coarser `Q`. A repaired
necessity condition must be `Q`-relative.

## Exact full-cut replacement obstruction

The first sufficiency pressure test does not hide which input environment was
used and does not limit the intervention to a few hidden values. Let

```text
X={0,1} -> H=R^2 -> Y=R,
g(u,v)=u+2v.
```

Observe the natural output at both labelled inputs and register replacement of
the entire typed cut state `do(H=(a,b))`. Freeze `Q` as the full labelled
upstream map `h:X->H` and use the identity gauge. The two upstream maps

```text
h_left(0)  = (0,0),    h_left(1)  = ( 1,0)
h_right(0) = (0,0),    h_right(1) = (-1,1)
```

have the same natural outputs `(0,1)`. Every cut replacement also has the same
law in both models because it returns the shared analytic function `a+2b`.
Nevertheless the upstream maps differ, and each input retains the continuous
blind direction

```text
ker([1,2]) = span{(-2,1)}.
```

The exact upstream observation design has rank two and nullity two. Both hidden
coordinates have nonzero downstream causal effect, and `[1,2]` is a surjective
submersion. More generally every nonzero linear map `R^2 -> R` has a
one-dimensional kernel, so this obstruction persists on an open coefficient
set. Full access to a cut is therefore not enough unless “separates” requires
state/quotient separation in addition to structural access.

## Exact structural-sufficiency obstruction

Use the same analytic response class, now with the uniform full-support parent
environment and passive plus every singleton activation replacement. Freeze
`Q` as the full conditional response table and quotient only by parent
permutations and parent sign flips.

The singleton intervention hypergraph passes all three structural gates:

- every parent site is covered;
- every pair of parent sites has different intervention incidence; and
- the site-incidence matrix is the `3 x 3` identity.

Both witness mechanisms are uniformly interior Bernoulli kernels, and every
parent has a positive average causal effect. They differ only in the
three-parent Walsh coefficient:

```text
theta_123(left)  = -1/100
theta_123(right) =  1/100.
```

All lower-order coefficients are equal and asymmetric. Exact enumeration of
the 48 parent permutation/sign-flip transformations confirms that the two
tables lie in different gauge orbits.

The passive and singleton-do observation matrix has rank four and nullity four.
In particular, `theta_123` lies in its exact kernel, so the two mechanisms have
identical registered Bernoulli laws. The blind coefficient can vary over an
open interval without changing any registered law, support gate, structural
cut gate, or singleton effect margin. This is a positive-dimensional analytic
ambiguity, not an isolated Boolean collision.

Thus purely structural cut separation is insufficient. The observation design
must separate the mechanism quotient, not merely the graph.

## Why the obvious repair is circular

One could define “the intervention hypergraph separates a cut” to mean that
every distinct admissible `Q/G` pair has positively separated registered
observations, or interpret `kappa>0` as a global lower bound on exactly that
quotient separation. The harness computes that margin as zero on the witness,
so such an assumption excludes it.

But this repair is the desired conclusion:

```text
positive global quotient separation
    implies exact quotient injectivity
    equals stable identifiability after normalization.
```

It does not provide an independently checkable graph/intervention criterion.
The missing theorem is precisely a noncircular characterization of when the
separation modulus is positive.

## Stopping argument

Further attempts to prove or refute the v0.1 iff would choose meanings not fixed
by the statement. A v0.2 problem must first specify:

1. a `Q`-relative excitation condition rather than full-class recovery when
   `Q` is coarse;
2. a formal, noncircular cut-separation predicate connected to the observation
   operator;
3. whether `kappa` is local numerical conditioning or the global quotient
   separation modulus;
4. the exact algebraic or measure-theoretic parameter space behind “generic”;
   and
5. which activation, path, and parameter-local interventions are mandatory.

After those choices, the current harness becomes a regression test: a proposed
criterion must accept the coarse-`Q` positive instance and reject the
higher-order blind fiber without defining acceptance as identifiability itself.

## Reproduction and claim boundary

The machine-readable receipt is
`artifacts/result.json`. All scientific comparisons use exact rational
arithmetic. The exhaustive group check contains 48 transformations. The
cut-replacement identity is symbolic and is additionally exercised on 25 exact
rational probe states; the finite probes are a regression check, not the
proof. No simulation or failure-to-find inference is used.

The result refutes the literal full-class necessity reading and the structural
hypergraph sufficiency reading. Because ASMP-1 v0.1 leaves the contested terms
parametric or undefined, it does not claim a resolution of every possible
repaired statement or of the broader four-part classification program.
