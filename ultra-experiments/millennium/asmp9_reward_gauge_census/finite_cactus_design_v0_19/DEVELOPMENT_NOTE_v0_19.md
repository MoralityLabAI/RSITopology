# ASMP-9 v0.19 development note

Status: burned development evidence; never claim-eligible.

## Question

Does the v0.16 balanced-cycle optimum

```text
f_k(N)=F_star(k,N,epsilon)
```

have diminishing multiplicative returns in `N`, so that the finite-budget
cactus problem can be solved by one-step marginal greedy allocation?

## Exact sweep

An in-memory exact-rational sweep checked

```text
f_k(N)^2 >= f_k(N-1) f_k(N+1)
```

over:

- `k=3,...,12`;
- `N=k+1,...,119`; and
- `epsilon` in
  `{1/100,1/20,1/10,1/5,1/4,1/3,2/5,49/100,1/2}`.

There were `10,035` comparisons, `3,927` strict failures, and `55`
equalities. The conjectured log-concavity is false.

The follow-up burned search covered two-cycle length pairs through ten,
forty surplus-budget units, and the preceding epsilon grid plus `1/50`.
It found `3,176` cells in which every maximum-one-step-gain tie branch was
strictly suboptimal.

## Small exact witness

For two triangles, `epsilon=1/4`, total budget `10`:

```text
all marginal-greedy endpoints: (4,6), (6,4)
exact optimum:                (5,5)
greedy value:                 34551/262144
optimal value:                8649/65536
exact gap:                    45/262144
```

The first log-concavity failure is visible in

```text
f_3(4)^2 - f_3(3) f_3(5) = -27/16384.
```

## Finite/asymptotic separation

The burned search also found cells where the best globally balanced
cyclic-edge allocation is not finite-optimal. One compact witness is cycle
lengths `(3,4)`, `epsilon=1/10`, and cyclic budget `12`:

```text
best globally balanced cycle totals: (4,8)
exact cycle totals:                  (3,9)
```

This does not contradict the v0.18 asymptotic exponent theorem.

## Consequence

Version v0.19 should register:

1. cactus probability factorization;
2. within-cycle balancing from v0.16;
3. an exact Bellman recurrence over cycle totals;
4. tie-independent greedy and finite-uniform counterexamples; and
5. a claim boundary restricted to the frozen independent cactus model.

No parameter cell listed in this note may be used as fresh v0.19 evidence.

