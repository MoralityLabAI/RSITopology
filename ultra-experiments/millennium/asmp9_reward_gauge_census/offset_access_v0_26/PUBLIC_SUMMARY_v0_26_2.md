# ASMP-9 offset-access boundary v0.26.2

## Verdict

**Established for the registered access model by additive runner repair.**

The result characterizes one strong way to overcome an unknown monotone
response link. It does not establish that ordinary preference data have this
access, and it does not resolve ASMP-9.

## Mathematical statement

Fix an anchor item and utility gaps

```text
d_i = u_i - u_0 in [-B,B],  i=1,...,d.
```

Let the unknown response link be any strictly increasing symmetric function

```text
F(-x) = 1-F(x),  F(0) = 1/2.
```

The registered interface can add a known cardinal offset `c` to one item and
return the population comparison with one half:

```text
Q(i,c) = sign(F(d_i+c)-1/2).
```

Strict monotonicity makes this query independent of the unknown link:

```text
Q(i,c) = sign(d_i+c).
```

If the offset range covers `[-B,B]`, coordinate bisection identifies the
anchored utility vector to max-norm error `eta` using

```text
d ceil(log2(B/eta))
```

queries. A volume argument gives the matching worst-case lower bound

```text
ceil(log2((B/eta)^d)).
```

The bounds coincide on dyadic cells.

If offsets are restricted to `|c|<=C<B`, the gaps

```text
(B+C)/2  and  B
```

produce the same complete query transcript. Every estimator therefore has
worst-case error at least

```text
(B-C)/4.
```

Known cardinal threshold coverage is thus sufficient, and missing coverage
has a sharp indistinguishability consequence in this access grammar.

## Finite-sample boundary

For repeated Bernoulli responses, a uniform finite-sample guarantee requires
a quantitative link margin. Under

```text
|F(x)-1/2| >= kappa |x|^alpha,
```

Hoeffding concentration gives the registered sufficient repeat count

```text
m >= 2 log(2Q/delta) / (kappa^2 eta^(2 alpha))
```

per population query. This is a conservative sufficient bound, not a minimax
rate.

Without a margin condition, scaled logistic links can be made uniformly
arbitrarily close to one half on the compact query range. A Le Cam two-point
argument then rules out any uniform finite-sample rate over the full link
class.

## Prospective checks

The v0.26 scientific run used fresh registered cells and checked:

- 3,718 population utility gaps;
- exact bisection errors and query bounds in two non-dyadic cells;
- exact upper/lower equality `70=70` and `81=81` in two dyadic cells;
- two restricted-range indistinguishability witnesses, with minimax error
  lower bounds `2` and `5/4`;
- 10,800 deterministic bounded-error bisection paths;
- two finite-sample certificates, requiring `722,879` and `590,221` repeats
  per population query under their deliberately conservative margins;
- convergence of an admissible flat-link family to within `1/1000` of one
  half; and
- the v0.8 three-item no-offset non-affine obstruction.

All mathematical and resource gates passed. The run used no GPU, completed in
1.45 seconds, and peaked at about 21.5 MB resident memory.

## Why the verdict required v0.26.2

The original v0.26 verdict remains
`offset_access_boundary_not_established_v0_26`. Its sole failed gate was a
brittle case-sensitive prose check in the prior-art gate; the mathematical
checks passed and the independent verifier isolated exactly that failure.

The registered v0.26.1 structural re-adjudication then stopped before writing
an output because its Windows resource helper narrowed a 64-bit process
handle. Its status remains unavailable.

Version v0.26.2 was registered before execution. It imports the v0.26.1
adjudication logic byte-for-byte and changes only the native argument
declaration in that resource helper. It binds both prior failures and all
original scientific artifacts. All eight repair gates and all fifteen
independent verification checks passed.

This history is part of the result:

```text
v0.26    scientific checks pass; prose gate fails
v0.26.1  structural repair registered; runner crashes before adjudication
v0.26.2  resource-only repair registered; adjudication and verification pass
```

## Prior-art and novelty boundary

Bisection, choice-indifference elicitation, willingness-to-pay procedures,
active utility learning, probabilistic bisection, stochastic root finding,
and unknown-link single-index identifiability are classical. No novelty is
claimed for those ingredients.

The contribution is an ASMP-9 access ledger: it states exactly which
registered intervention supplies the cardinal scale, proves a matching
population-query boundary in that grammar, and separates the population
theorem from the additional finite-sample margin assumption.

## Claim boundary

This result does not show that:

- ordinary human comparisons expose cardinal reward offsets;
- arbitrary environment interventions implement an additive offset in latent
  reward units;
- context-dependent, item-dependent, nonmonotone, or shifted-midpoint links
  are covered;
- the finite-sample bound is minimax;
- general MDP rewards are identified from policy behavior; or
- ASMP-9 is resolved.

