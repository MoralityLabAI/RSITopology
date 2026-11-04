# ASMP-9 v0.19.2: exact finite-budget design on cactus cyclic cores

## Result

Version 0.19.2 establishes, inside the frozen independent-binomial
conditional-access model inherited from ASMP-9 v0.16-v0.18:

> If the cyclic core of the comparison graph is a cactus, exact finite-budget
> maximin access design factorizes over its edge-disjoint cycle blocks. Every
> bridge receives the mandatory minimum count, every cycle is internally
> balanced, and an exact Bellman recursion allocates the remaining integer
> budget among cycles.

The registered verdict is:

```text
finite_budget_cactus_dp_established_in_frozen_model_v0_19_2
```

All ten preregistered gates passed. A separately sealed verifier passed all
eleven checks.

## Mathematical statement

Let the cactus cyclic core have cycle blocks

```text
C_1,...,C_c
```

with lengths `k_1,...,k_c`. For a fixed positive edge-count allocation `n`,
let `F_G(n)` be the worst-case probability that the conditional comparison
fiber spans the complete reward-gauge quotient. Under the frozen independent
response model:

```text
F_G(n) = product_j F_Cj(n restricted to C_j).
```

The cycle events use disjoint edge sets, and the endpoint-label adversary also
separates across those sets. Original bridges enter neither the residual-cycle
liveness event nor its probability.

Let `f_k(N)` denote the exact one-cycle maximin availability with `N` trials.
The v0.16 theorem shows that its optimizer assigns counts differing by at most
one within the cycle. Consequently the complete finite problem becomes:

```text
maximize  product_j f_(k_j)(N_j)

subject to

  N_j >= k_j,
  sum_j N_j = N - number_of_bridges.
```

With `D_j(b)` denoting the best product for the first `j` cycles using exactly
`b` trials:

```text
D_0(0) = 1,

D_j(b)
  = max_(k_j <= t <= b)
      D_(j-1)(b-t) f_(k_j)(t).
```

This returns the exact value and every optimal cycle-total vector in
pseudo-polynomial time in the integer budget. It is a classical separable
integer resource-allocation dynamic program. The ASMP-9 contribution is the
reduction from conditional reward-gauge access to that classical object, not
the invention of dynamic programming or redundancy allocation.

## Why simpler allocation rules are insufficient

Two exact counterexamples remain part of the result:

1. For two triangle blocks, `epsilon=1/4`, and total cyclic budget `10`, every
   maximum-one-step-gain greedy branch ends at `(4,6)` or `(6,4)`, while the
   exact optimum is `(5,5)`. The exact gap is:

   ```text
   45/262144.
   ```

   Thus the one-cycle objective is not discretely log-concave in general.

2. For cycle lengths `(3,4)`, `epsilon=1/10`, and total cyclic budget `12`,
   the best globally balanced edge allocation induces `(4,8)`, while the
   exact finite optimum is `(3,9)`. The exact gap is:

   ```text
   26235981/125000000000.
   ```

   Therefore the v0.18 asymptotically uniform cactus design is not an exact
   every-budget rule.

## Registered evidence

Versions 0.19 and 0.19.1 passed their mathematical gates but exceeded the
frozen `180`-second resource cap. Their negative verdicts and verifier
limitations remain visible.

A post-outcome profile of v0.19.1 showed that `387.565` of `430.209` seconds
were spent recomputing identical one-cycle endpoint-label minima across
different total-vector compositions. Version 0.19.2 prospectively froze an
exact memoized checker that still:

- exhausts every feasible cycle-total vector;
- exhausts all endpoint-label assignments once per distinct
  `(cycle length, cycle total)` pair;
- uses exact rational arithmetic; and
- remains implementation-independent of the compact Bellman cycle factor.

The fresh primary cell `(5,8,10,12)` has greater total cycle length and a
longer largest cycle than the failed v0.19.1 primary cell, so the passing run
did not narrow the workload merely to satisfy the cap.

The fresh run checked:

- every endpoint-label vector on a `(4,5)` cactus;
- bridge irrelevance on a `(3,7)` cactus with one bridge;
- three exact Bellman-versus-independent exhaustive allocations, including
  the four-cycle `(5,8,10,12)` cell;
- a 330-allocation positive all-edge census;
- both frozen counterexamples; and
- three outcome-neutral greedy/global-balance comparator cells.

All ten gates passed in `50.568574` seconds, using `24,293,376` peak resident
bytes and no GPU. Independent replay passed `11/11` checks.

## Evidence chain

- implementation freeze:
  `da0734da7d5a8c6f89f98b64cd7f0fed9df0ba42`;
- registration commit:
  `4667857250855cf0e11254846e997c07e8e12826`;
- result commit:
  `c4754e2363ebac4834505985ade67f7f36431ab8`;
- registration SHA-256:
  `7328118a2b76aa0cb8f79c369f5deaaf61bd0663ab9ab35877f4b0ff94089298`;
- protocol SHA-256:
  `9c1d2789f1413e05200056dd36a03f73fed5edc714c30b7eda23721ddd921791`;
- result SHA-256:
  `b7db6efdde7f8453b255f0e93162b368ce1baeef6c26909c7e825667e5e1615d`.

## What this advances

Version 0.18 identified cyclic-core bonds as the asymptotic failure supports.
Version 0.19.2 now closes exact finite-budget allocation for cactus cyclic
cores in the same frozen model. Together they separate:

- asymptotic graph structure: max-min cyclic-core cut design; and
- exact finite cactus design: a series product solved by integer Bellman
  allocation.

The general cyclic-core finite-budget objective remains a network-reliability
design problem and is not solved here.

## Claim boundary

Exact finite-budget maximin allocation on cactus cyclic cores inside the
frozen independent-binomial, known symmetric-interior, positive-count
conditional-access model. Not an exact arbitrary-graph every-budget theorem,
adaptive allocation theorem, dependent-response theorem, unknown-link
theorem, downstream policy-estimation theorem, behavioral
reward-identification theorem, general inverse-reinforcement-learning theorem,
or resolution of ASMP-9.
