# Sublinear safe-closing theorem

## 1. Registered nonfinite protocol components

Fix the plant, evaluator, sensor, timing, randomness, controller, actuator,
cost functional, and safety semantics.  The public protocol state may be
finite, countable, or continuous.

Let `q` index a registered recurrent safe component.  An infinite safe code
`C` in component `q` has prefix log-cost vector

`a(C,T) = (a_r(C,T),a_w(C,T))`

and coordinatewise rate

`rho(C) = limsup_T a(C,T)/T`.

A reset block `B` in `q` starts and ends at the component's registered reset
condition, remains evaluator-safe, has physical length `|B|`, and has log-cost
vector `c(B)`.  Define

`P_q = {c(B)/|B| : B is a safe reset block in q}`.

Transcript cardinalities are one admissible cost: if `M_i(B)` is the realized
block language, then `c_i(B)=log2 |M_i(B)|`.  Prefix-free or branch costs are
admissible only after their registered concatenation law is supplied; v0.28-
v0.30 explain why one quotient-size surrogate cannot replace that law.

## 2. Safe-closing hypotheses

The component has the **sublinear safe-closing property** when:

1. safe reset blocks concatenate inside `q`, and concatenation has componentwise
   submultiplicative transcript counts, hence subadditive log costs;
2. every infinite safe code `C` in `q` has cofinally many prefix horizons
   `T_j -> infinity` that admit safe closing blocks `B_j` with

   `|B_j| = T_j + ell_j`,

   `c(B_j) <= a(C,T_j) + b_j` componentwise,

   `ell_j/T_j -> 0`, and `b_j/T_j -> (0,0)`; and
3. every admissible infinite safe code is assigned to a registered component,
   up to a transient whose time and vector cost are asymptotically negligible.

The cost condition is load-bearing.  A linear closing charge can shift either
port's boundary.  Sublinear closing time ensures that closing preserves, rather
than dilates, the original physical-time normalization.

## 3. Exact component and global regions

Let `R_q` denote the closed upward budget region of all infinite safe codes in
component `q`.

**Theorem 1 (nonfinite periodic completeness).** Under the safe-closing
hypotheses,

`R_q = closure(upward(conv(P_q)))`.

Consequently, with

`h_q(lambda) = inf_B [lambda c_r(B)+(1-lambda)c_w(B)]/|B|`,

the exact component formula is

`R_q = intersection_(0<=lambda<=1)`

`      {(r,w): lambda r+(1-lambda)w >= h_q(lambda)}`.

If several irreversible components are reachable, the full closed region is

`closure(R) = closure(union_q R_q)`.

The component index cannot in general be minimized away before taking support
half-spaces: that operation convexifies mutually irreversible choices.

**Proof.** Repeating one reset block gives an infinite safe code with its block
rate.  Concatenating reset blocks in rational proportions realizes rational
convex combinations, and arbitrary combinations follow by closure.  This proves
`closure(upward(conv(P_q))) subset R_q`.

For the reverse inclusion, take an infinite safe code with rate `rho`.  For
every `epsilon>0`, coordinatewise limsup gives, at all sufficiently large
closing horizons,

`a_i(C,T_j)/T_j <= rho_i+epsilon`.

The corresponding block satisfies

`c_i(B_j)/|B_j| <= [a_i(C,T_j)+b_(j,i)]/[T_j+ell_j]`

`                   <= a_i(C,T_j)/T_j + b_(j,i)/T_j`.

The last term is at most `rho_i+2 epsilon` for large `j`.  Thus normalized
reset-block points approach a vector componentwise no larger than `rho`, so the
upward closed block region contains every infinite-code budget.  This proves
the reverse inclusion.  The support formula follows from separation of the
closed convex upward component region, exactly as in v0.24.  Taking the union
over the registered exhaustive component decomposition proves the global
formula.  No finiteness, stationarity, or additive state quotient is used.

### Coordinate invariance

A cost-preserving causal conjugacy transports plant states, disturbances,
safe/reset sets, protocol components, codes, and closing blocks bijectively.
Transcript-alphabet relabelings preserve every realized count.  Therefore the
conjugacy preserves `a(C,T)`, `P_q`, `h_q`, each component region, and their
global union.  The theorem's quantities are invariants of the registered
two-port experiment, not of a chosen state chart or symbol naming.

## 4. Exact finite-horizon correction

For a closable prefix of length `T`, closing time `ell`, overhead
`b=(b_r,b_w)`, and `0<=lambda<=1`, the construction gives

`h_q(lambda) <=`

`[lambda(a_r+b_r)+(1-lambda)(a_w+b_w)]/(T+ell)`

`<= [lambda a_r+(1-lambda)a_w]/T`

`   +[lambda b_r+(1-lambda)b_w]/T`.

This is an exact finite-horizon correction, not only an asymptotic statement.
It separately exposes read and write closing charges.  Constant closing cost
gives an `O(1/T)` correction; a linear charge does not disappear.

## 5. Metric shadow-closing lift

Suppose a state-space closing or shadowing lemma produces a closed candidate
trajectory at uniform distance at most `epsilon_T` from the safe reference
prefix.  Let

`delta_T = min_t dist(x_t, X \ K)`

be the registered safety margin.  If `epsilon_T < delta_T`, the closed
trajectory stays in `K` by the triangle inequality, so its protocol block is
eligible for Theorem 1.  The strict inequality is the coordinate-free safe
version when no closure convention for `K` is silently imposed.  Under a
bi-Lipschitz state-coordinate change, both quantities rescale by the declared
constants and the safety conclusion is unchanged.

This lemma identifies exactly what a hyperbolic shadowing or local-control
argument must provide: safe component return, sublinear two-port cost overhead,
and shadow error below the evaluator margin.

## 6. Aperiodic infinite-state sharp witness

Let `t_n` be the Thue-Morse sequence,

`t_(2n)=t_n`, `t_(2n+1)=1-t_n`.

At step `n`, charge `(t_n,1-t_n)`.  After any prefix of length `T`, one safe
connector returns the public state to zero with cost `(1,1)`.  Pair cancellation
gives

`|2 sum_(n<T)t_n - T| <= 1`.

Every closed block therefore has both rates at least `1/2`, and the blocks of
length `2^k+1` converge to `(1/2,1/2)`.  The exact component region is the
quadrant above that corner.

These integer bit costs are literal transcript costs: at a step of cost `k`,
the corresponding port has `2^k` independent realized continuations.  Products
of those continuation counts give exactly `2` raised to the displayed additive
block cost.

There is no finite exact stationary quotient preserving the step costs.  A
finite deterministic quotient would make the cost sequence eventually
periodic.  To see that Thue-Morse is not, assume an eventual period `p`.  If
`p=2q`, the two recurrence identities make `q` an eventual period, so repeated
division reduces to odd `p=2q+1`.  Eventual `p`-periodicity then gives, for all
large `n`, both

`t_(n+q)=1-t_n` and `t_(n+q+1)=1-t_n`.

Hence the sequence would be eventually constant, contradicting
`t_(2n+1)=1-t_(2n)` at arbitrarily large indices.  The theorem therefore
strictly exceeds the finite-quotient lane of v0.25-v0.31.

For two irreversible aperiodic components, use step costs `(t_n,2-t_n)` and
`(2-t_n,t_n)`, with connector costs `(1,2)` and `(2,1)`.  Their exact corners
are `(1/2,3/2)` and `(3/2,1/2)`.  The point `(1,1)` satisfies every half-space
obtained by first minimizing the support value across components, but belongs
to neither component region.  Thus the component disjunction remains
load-bearing even without finite state.

## 7. Scope

The theorem supplies a genuine nonfinite replacement for periodic block
completeness and a concrete target for shadowing/local-controllability proofs.
It does not prove that every normally hyperbolic, locally controllable
registration in the canonical prose has the safe-closing property.  Hidden
belief state, unsafe component connectors, linear transcript overhead,
nonresettable actuator memory, and missing evaluator margin can all defeat the
hypotheses.  Establishing safe closing for a formal global nonlinear class is
the next remaining step toward full ASMP-4 resolution.

V0.34 discharges that implication for compact connected recurrent components
whose charged public information state has safe local connector certificates.
Compactness and the connected safe overlap nerve turn those local certificates
into constant vector closing overhead. The unresolved implication is now from
the canonical plant-level hyperbolicity/controllability prose to those public
finite-cost certificates.
