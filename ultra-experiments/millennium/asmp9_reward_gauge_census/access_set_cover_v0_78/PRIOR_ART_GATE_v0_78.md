# Prior-art gate for ASMP-9 access Set Cover reduction v0.78

Status: **classical Set Cover/test-separation specialization**.

## Subsumption

The complexity ingredient is classical:

- Set Cover is NP-hard;
- finite test selection can be formulated as covering unresolved pairs; and
- minimum test-cover/separating-system problems are established
  combinatorial-optimization objects.

No new complexity class, approximation lower bound, or Set Cover theorem is
claimed.

## Residual ASMP-9 role

The contribution is an explicit reduction into the program's exact
target-access grammar:

```text
one mandatory anchor query
+ one binary split query per candidate set
-> access optimum = cover optimum + 1.
```

It converts the general warning “minimum access is set cover” from v0.74 into
a complete polynomial hardness witness with exact executable controls.

## Prior-art requirements before circulation

A circulation version should pin primary citations for:

1. Set Cover NP-completeness;
2. Minimum Test Cover and test-set problems;
3. separating systems and distinguishing families; and
4. approximation or parameterized algorithms relevant to structured access.

## Hostile-review questions

1. Is the multi-valued anchor query allowed by the declared access grammar?
2. Does hardness survive binary-only outputs?
3. Are adaptive queries allowed, and can they change the objective?
4. Does a natural reward-learning channel realize the arbitrary lookup table?
5. Is worst-case exact hardness being misreported as empirical difficulty?

All remain outside the finite reduction claim.
