# Resettable support-functional variational theorem

## 1. Registered reset blocks

Fix every architecture field in `architecture_schema_v0_24.json`. For horizon
`T`, let `A_T` contain the count pair `(R,W)` of every safe finite block code
that begins in the registered reset set and returns to it. Counts refer to the
realized complete read and write transcript languages and are at least one.

The registration is reset-concatenable when a safe `T` block with pair `(R,W)`
and a safe `S` block with pair `(R',W')` can be concatenated into a safe
`T+S` block with pair at most `(RR',WW')`. Exact independent block composition
gives equality; the theorem only needs the upper bound. Thus multiplication of
transcript counts becomes addition of their logarithms.

Define the normalized block-rate set

`P = union_T {(log2 R/T, log2 W/T):(R,W) in A_T}`.

The reset-block-generated region is

`R_blk = closure(upward-convex-hull(P))`.

Concatenation makes every rational time sharing between finite block points
achievable: repeat the two blocks suitable numbers of times, concatenate, and
let the repetition counts grow. This is an operational convexification, not an
assumption that an arbitrary nonresetting safety problem is convex.

## 2. Weighted evaluator-transversal entropy

For `0 <= lambda <= 1`, define

`h(lambda) = inf_(T,(R,W) in A_T)
             [lambda log2 R + (1-lambda) log2 W]/T`.

If no safe reset block exists, the infimum is infinity. For fixed `lambda`, let
`a_T(lambda)` be the unnormalized infimum at horizon `T`. Reset concatenation
gives `a_(T+S) <= a_T+a_S`; whenever the relevant horizons form a concatenable
semigroup, Fekete's lemma gives

`h(lambda) = inf_T a_T(lambda)/T = lim a_T(lambda)/T`.

Because `h` is an infimum of affine functions of `lambda`, it is concave.

## 3. Exact variational formula

**Theorem.** The full reset-block-generated region is

`R_blk = intersection_(0<=lambda<=1)
         {(r,w):lambda r+(1-lambda)w >= h(lambda)}`.

**Proof.** Every point of `P` satisfies every displayed lower supporting
inequality by the definition of `h`. Convexification, upward closure, and
topological closure preserve them, so `R_blk` is contained in the right-hand
side.

Conversely, `R_blk` is a closed convex upward subset of the nonnegative plane.
If a finite point is outside it, the separating-hyperplane theorem gives a
strict separating normal. Upward closure forces both components of that normal
to be nonnegative; otherwise moving an in-region point upward in the negative
coordinate would violate separation. Normalize the two components to
`(lambda,1-lambda)`. Its lower intercept is exactly `h(lambda)`, so the outside
point violates one displayed inequality. Hence the right-hand side is
contained in `R_blk`.

This family is the nonrectangular replacement for two scalar thresholds. The
endpoint values `h(1)` and `h(0)` are the separate read and write infima; an
interior weight is load-bearing exactly when the coordinatewise corner is not
achievable. Equivalently, the region is reconstructed from its lower
supporting half-spaces rather than from the two coordinate half-spaces alone.

## 4. Coordinate invariance

A depth-preserving relabeling of either transcript alphabet leaves `(R,W)` for
every block unchanged. A bijective state-coordinate conjugacy that transports
the plant, evaluator, safe/reset sets, disturbances, sensor registration, and
block codes induces a bijection between all `A_T`. Therefore it preserves
`P`, `h`, and `R_blk`. A sensor quotient is covered only when the architecture
declares it; quotienting is not silently treated as a coordinate change.

## 5. Exact prior-region recoveries

- One rate point `(1,1)` has `h(lambda)=1` and reconstructs the diagonal
  quadrant `[1,infinity) x [1,infinity)`.
- One point `(3,2)` has `h(lambda)=2+lambda` and reconstructs the unequal
  rectangle `[3,infinity) x [2,infinity)`.
- The v0.7 reset grammar has local count pairs `(3,3)` and `(4,2)`. Its rate
  endpoints are `(log2 3,log2 3)` and `(2,1)`, hence
  `h(lambda)=min(log2 3,1+lambda)`. At
  `theta=log2(3/2)`, both branches equal `log2 3`; the resulting three
  irredundant inequalities are

  `r >= log2 3`, `w >= 1`, and
  `theta r+(1-theta)w >= log2 3`.

- The v0.20 raw-clone corner `(2+log2 m,2)` has
  `h_m(lambda)=2+lambda log2 m`, exposing representation dependence unless a
  sensor experiment or quotient is registered.
- The v0.23 positive-delay/no-preview architecture has no safe block, so
  `h(lambda)=infinity` and the finite-rate region is empty.

## 6. Boundary of the theorem

Every repeated reset block is an admissible infinite safe code, so
`R_blk` is contained in the canonical full region for the same registration.
Equality requires **periodic block completeness**: every Pareto-relevant
infinite safe-code rate must be approximable by reset blocks. That property is
automatic for the full-reset fixtures above and may fail for nonresetting
plants, path-dependent safety margins, private channel state, or architectures
whose internal memory cannot be reset without charge.

The theorem therefore advances the global variational form without claiming a
formula for an unspecified nonlinear class. Proving reset/periodic block
completeness—or replacing it by a genuinely nonstationary variational
principle—is the next mathematical obligation.
