# ASMP-9 unknown response-link verification protocol v0.8

## Status

Prospective CPU-only verification protocol. The explicit `(0,1,3)` versus
`(0,1,4)` witness, all primitive utility rays through coordinate bound 64,
and all current unit-test fixtures are burned development data.

## Frozen claims

For:

```text
P(j preferred to i)=F(beta(u_j-u_i)),
```

with `F` known, injective, and symmetric and `beta>0` unknown, exact complete
pairwise probabilities identify `beta(u-u_root)`. Unknown inverse temperature
is therefore the registered positive-scale gauge, not an additional
population-level ambiguity.

If `F` instead ranges over every strictly increasing symmetric link on a
finite comparison design, utilities with the same labelled weak order of
pairwise differences can induce identical complete probability laws under
separate links. This equivalence is strictly larger than positive affine
reward gauge for three or more items.

The registered exact witness uses:

```text
u=(0,1,3), u'=(0,1,4)
```

and rational links giving the shared complete law:

```text
P(1>0)=3/4, P(2>1)=5/6, P(2>0)=7/8.
```

Two distinct items are the minimal negative control: every nonzero two-item
gap is positive-affine equivalent to every other.

## Fresh cells

### Known-link cells

Seed `98081`: 32,768 item sets with 2 through 16 rational utilities and a
positive rational inverse temperature. Exact inversion must recover
`beta(u-u_0)` and every complete-law edge.

### Primitive three-item shell

Enumerate every primitive strictly increasing integer utility ray:

```text
(0,a,b), 65<=b<=128, gcd(a,b)=1.
```

The shell must split into the two strict labelled difference-order classes
`a<b-a` and `a>b-a`; every class must contain more than one non-affine ray.
The equality class is absent because its sole primitive ray `(0,1,2)` is in
burned development data.

### Unknown-link ambiguity cells

Seed `98082`: 16,384 fresh pairs of three-item integer utilities. The two
members must:

- share a strict labelled difference order;
- not be positive-affine equivalent;
- have identical complete laws under the constructed matching link; and
- have different complete laws if forced to share the same known link.

Every constructed link is checked for exact symmetry and strict monotonicity
on its knots, interval probes, and tail probes.

### Controls

- seed `98083`: 8,192 distinct two-item pairs must all be positive-affine
  equivalent;
- seed `98084`: 8,192 opposite difference-order pairs must be rejected by the
  matching-link constructor.

## Gates

- **G0:** registration commit, implementation ancestry, clean tracked tree,
  and every sealed hash agree;
- **G1:** all known-link unknown-temperature recoveries are exact;
- **G2:** the registered rational three-item witness has equal laws and is
  non-affine;
- **G3:** the primitive fresh shell has exactly two strict classes and both are
  nontrivially ambiguous;
- **G4:** every fresh same-order non-affine pair has equal laws under its
  matching link;
- **G5:** the same known link separates every fresh non-affine pair;
- **G6:** every constructed link passes exact monotonicity and symmetry
  probes;
- **G7:** every two-item minimality control is positive-affine equivalent;
- **G8:** every opposite-order control is rejected.

All gates passing yields:

```text
unknown_link_finite_design_nonidentifiability_verified.
```

## Claim boundary

This is a population-law finite-design obstruction. It is not finite-sample
estimation, a characterization of sufficiently rich interventions, a general
semiparametric single-index theorem, or a complete ASMP-9 resolution. The
underlying nonidentifiability is classical; novelty is not claimed.

## Resources

CPU only; 2 GiB RAM; 5 minutes; no GPU.
