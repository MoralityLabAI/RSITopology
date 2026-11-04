# ASMP-9 v0.50 reference-law robustness development result

## Status

**Finite theorem instrument derived and tested; not prospectively
registered.**

Version v0.49 decided whether two evidence-ordering objectives share an
optimum at one frozen reference law. Version v0.50 makes the reference law
part of the certificate. For any rational polytope of strictly positive
reference laws, it returns:

1. the exact halfspace region where a declared ordering remains jointly
   optimal;
2. the exact count of orderings optimal for every objective and every
   reference law in the polytope;
3. a labelled tight-DAG cut when no such ordering exists; and
4. the exact minimum worst-case regret for small outcome sets.

## Exact theorem

For objective `d`, ordering `pi`, and reference law `w`,

```text
C_d(pi;w) = <w,b_d^pi>
```

is linear in `w`. Therefore the region where `pi` is jointly optimal is the
rational polytope

```text
R_pi(D)
  = {
      w :
      <w,b_d^pi-b_d^sigma> <= 0
      for every d and sigma
    }.
```

If the registered family is

```text
W = conv{v_1,...,v_k},
```

joint optimality throughout `W` is equivalent to joint optimality at every
generator `v_i`. Intersecting the tight-predecessor DAGs over all
`(objective,vertex)` scenarios therefore gives a necessary-and-sufficient
robust-chain certificate.

Worst-case regret also reduces exactly to those generators:

```text
Reg(pi;D,W)
  = max_(d,i,sigma)
      <v_i,b_d^pi-b_d^sigma>.
```

This is classical finite robust shortest-path mathematics.

## Minimal sensitivity witness

One objective with two outcomes has subset table

```text
B(empty,x,y,X) = (0,0,0,1).
```

At reference vertices

```text
(3/4,1/4) and (1/4,3/4),
```

the two orderings have costs

```text
(1/4,3/4) and (3/4,1/4).
```

There is no robust ordering and the exact minimax regret is `1/2`. The table
is a valid Buehler table for one risk-one parameter with outcome law
`(1/2,1/2)` at `alpha=3/5`.

The witness is minimal for reference-law sensitivity: one outcome has no
ordering choice, one objective is already sufficient, and one reference law
always has an optimum.

## Recovery and tests

A singleton reference family containing the v0.48 uniform law exactly
recovers:

```text
robust/common optimizers: 1,451,520.
```

The development suite covers:

- robust tight-DAG counts against exhaustive scenario intersection;
- the vertex theorem on registered convex combinations;
- the minimal statistical switch and its `1/2` regret;
- exact weight-region splitting at the simplex midpoint;
- zero minimax regret exactly when a robust chain exists on a planted
  positive fixture;
- v0.48 recovery at its frozen reference law; and
- rejection of zero or unnormalized reference weights.

```text
8 tests passed
```

## Next verification step

The theorem should be verified prospectively over the complete
three-outcome Buehler-admissible monotone universe:

```text
Dedekind M3:             20
exclude B(empty)=1:       1
admissible tables:       19
ordered objective pairs: 361.
```

For a frozen two-vertex positive reference polytope, the verifier should
compare robust tight-DAG counts with exhaustive intersection of all six
outcome orderings for every table pair. It should separately audit the
halfspace inequalities, minimal witness, minimax-regret identity, and v0.48
recovery.

## Claim boundary

This development is a finite specialization of linear, parametric,
multiobjective, and robust shortest-path optimization. The minimal witness is
a candidate-new elementary control, not established novelty. Nothing here
handles randomized confidence procedures, continuous experiments, strategic
response, physical preference access, or resolves ASMP-9.
