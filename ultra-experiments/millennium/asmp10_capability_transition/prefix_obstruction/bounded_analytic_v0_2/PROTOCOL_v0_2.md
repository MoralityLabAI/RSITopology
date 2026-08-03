# ASMP-10 norm-bounded codimension-one continuation protocol v0.2

## Question

How much future-score disagreement can an exact finite prefix hide once the
continuation class has both a degree ceiling and a declared coefficient-norm
budget?

This protocol takes the first CPU-exact slice proposed in
`../SUCCESSOR_SCOPE_v0_2.md`. It does not execute the separate neural-training
branch.

## Frozen class and basis

For `n >= 1` and jet order `k >= 0`, observe every derivative through order
`k` at the physical nodes `0,...,n-1`. Set

`J = n(k+1)`.

The primary class has degree at most `D=J`. Coefficients are frozen in the
ascending physical-coordinate monomial basis

`(1,x,x^2,...,x^J)`.

For `p(x)=sum_j a_j x^j`, the declared norm is

`||p||_(1,mono) = sum_j |a_j|`.

Each member of a compared pair has norm at most the rational budget `B >= 0`.
The pair must have exactly equal observed jets, so this phase freezes
observation error to `delta=0`. The envelope is global over all shared exact
prefixes; it is not conditional on one fixed nonzero jet vector.

## First-kernel theorem and exact envelope

Let `H` be the confluent-Vandermonde jet map. At `D=J-1`, `H` is square and
invertible. At `D=J`, its kernel is one-dimensional and is spanned by the monic
polynomial

`q(x) = product_(i=0)^(n-1) (x-i)^(k+1)`.

Let `phi` be any frozen linear future-score probe. If `p_plus` and `p_minus`
have equal jets, their difference is `t q`. The two norm budgets imply

`|t| ||q||_(1,mono) <= ||p_plus-p_minus||_(1,mono) <= 2B`.

Therefore

`|phi(p_plus)-phi(p_minus)| <= 2B |phi(q)| / ||q||_(1,mono)`.

The bound is attained exactly by

`p_plus = B q / ||q||_(1,mono)` and
`p_minus = -B q / ||q||_(1,mono)`.

The registered output is thus

`Delta*(n,k,B,phi) = 2B |phi(q)| / ||q||_(1,mono)`.

For the primary future-gradient probe, `phi(p)=p'(n)`, the independent
closed-form control is

`q'(n) = (k+1) (n!)^(k+1) H_n`,

where `H_n=sum_(r=1)^n 1/r`.

## Exact census

- geometries `(n,k)`:
  `(1,1), (2,1), (3,1), (2,2), (3,2)`;
- rational budgets: `0, 1/3, 1, 5/2`;
- five future-score pseudometric probes:
  `p'(n)`, `p(n)`, `p(n+1)`, `p'(n+1)`, and `p(n+1)-p(n)`;
- exact `fractions.Fraction` arithmetic only;
- CPU only, with no network or GPU operation.

The primary solver obtains the kernel by exact row reduction. The independent
verifier does not import the solver. It reconstructs the product polynomial,
checks the determinant of the `D=J-1` square Hermite matrix, evaluates the
metric symbolically, and uses `sign(coeff(q))` as the L-infinity dual witness
that saturates the coefficient L1 norm.

## Conjunctive gates

- **Z0 zero-nullity:** every `D=J-1` identified control has nullity zero.
- **H0 homogeneity:** every envelope is exactly linear in `B` on the registered
  rational budgets.
- **M0 monotonicity:** increasing `B` never decreases the envelope.
- **B0 basis binding:** row-reduced and product coefficients agree in the
  frozen basis, the reported norm is their monomial L1 norm, and a shifted-basis
  control demonstrates that the norm is not being treated as basis invariant.
- **W0 witness feasibility:** every Fraction witness matches all prefix jets,
  respects both budgets, and attains the reported envelope.
- **O0 independent optimality:** product, determinant, metric, L1 norm, dual
  saturation, and optimum agree with the independent verifier.
- **R0 metric robustness:** all five registered future-score probes pass every
  applicable feasibility and independent-optimality check.

Any failed gate yields `instrument_failed`. Otherwise the task result is
`exact_codimension_one_norm_bounded_envelope_established`.

## Output separation

The deterministic report has four deliberately separate records:

1. `task_result`: exact envelopes and kernel witnesses;
2. `reliability`: gates and independent-verifier evidence;
3. `claim_support`: supported and unsupported inference scopes; and
4. `operation`: CPU/network/GPU/write facts.

Passing reliability gates is not itself represented as broader claim support.

