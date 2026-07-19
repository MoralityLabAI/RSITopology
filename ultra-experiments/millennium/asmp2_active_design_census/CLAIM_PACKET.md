# ASMP-2 active-design claim packet

## Object

For `x in {-1,+1}^4`, let `phi(x)` contain the intercept, four linear monomials, and six pairwise monomials. An unknown risk function is `f_a(x)=a^T phi(x)` with `||a||_2 <= 1`. Exact source evaluations at a design `S` constrain `a` through the feature matrix `A_S`.

The registered squared ambiguity radius on deployment set `T` is

```text
R^2(S,T) = max_{x in T} phi(x)^T P_ker(A_S) phi(x).
```

This is coordinate invariant and exactly characterizes the worst residual evaluation magnitude under the frozen Euclidean coefficient ball.

## Non-forced estimand

For budgets 1 through 10, enumerate every source subset and compute the globally minimal `R^2` under the registered ten-decimal numerical ordering contract. Compare:

1. one-step minimax greedy, which selects the next environment minimizing the next registered radius;
2. a geometry-only farthest-Hamming selector; and
3. 256 seeded random sequences without replacement.

The greedy first-step comparison is mechanically favored and is excluded from scientific classification. The registered evidence question uses the entire budgets 2--10 curve: normalized AUC, maximum regret relative to the globally minimal registered subset at the same budget, and improvements over both control selectors. Exact-rational checks certify the reported radii of deterministic selected designs, but do not establish ordering among designs inside one rounded tie bin.

## Deployment families

- `full_cube`: all 16 corners;
- `nonnegative_sum`: corners with coordinate sum at least zero;
- `even_parity`: corners with coordinate product `+1`.

## Scientific classification

For a deployment family to support the active selector, over budgets 2--10:

- relative AUC improvement over median random must be at least 5%;
- relative AUC improvement over space filling must be at least 5%; and
- maximum regret relative to the exhaustive global optimum, normalized by the empty-design radius, must be at most 5%.

All three families passing yields `active_design_supported_in_registered_finite_class`; one or two yields `active_design_mixed`; zero yields `active_design_not_supported`. These are outcomes, not instrument-validity gates.

## Claim boundary

This finite census can validate or reject one selector in one polynomial shift class under the frozen numerical contract. It does not establish a semiparametric necessity/sufficiency theorem, exact ordering within numerical tie bins, minimax sample complexity, noisy confidence bounds, local-to-global continuation conditions, or an optimal active design for unrestricted shifts. The construction is adjacent to classical G-optimal design and polynomial interpolation; no novelty is claimed.
