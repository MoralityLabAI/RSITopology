# ASMP-11 v0.2 covering-frontier review addendum

This is an additive post-result clarification. It does not modify any source
file bound by `registration_v0_2.json`.

## Classical placement

The all-negative-path argument belongs beside adaptive combinatorial search
and group testing: an adaptive strategy restricted to that transcript emits a
fixed sequence of queries, so worst-case detection requires that sequence to
cover every admissible hidden support. A standard broad reference is:

- Ding-Zhu Du and Frank K. Hwang, *Combinatorial Group Testing and Its
  Applications*, second edition, World Scientific, 2000.

The finite extremal object is the classical covering number `C(v,k,t)`:

- Daniel M. Gordon, Greg Kuperberg, and Oren Patashnik, "New constructions for
  covering designs," *Journal of Combinatorial Designs* 3(4):269-284, 1995,
  DOI `10.1002/jcd.3180030404`.
- La Jolla Covering Repository, <https://ljcr.dmgordon.org/cover.html>.

The repository supplies best-known constructions and upper bounds; a listed
cover is not, by itself, a proof that the covering number is optimal. The v0.2
run did **not** query or import La Jolla data.

## What "solver-certified" means here

Each registered covering cell was formulated as a binary set-cover ILP and
solved locally by `scipy.optimize.milp` under SciPy 1.16.2 with bundled HiGHS
1.8.0. The receipt records an optimal solver status, zero reported MIP gap,
and equality of the integer objective and dual bound. A separate verifier
checks every emitted block family against the complete support universe.

Accordingly:

- the witness and upper bound are independently replayable from the artifact;
- the matching lower bound relies on the floating-point MILP solver's optimal
  termination record;
- no independently checkable branch-and-bound or cutting-plane proof object
  was emitted.

"Solver-backed optimum with an independently checked witness" is therefore
the most precise description.

## Cost-comparison boundary

The observational baseline enumerates all degree-`k` Walsh supports and gives
each query the exact registered binomial sample size needed for familywise
error at most `1/20` and signal power at least `9/10`. It is a frozen,
nonadaptive estimator, not a minimax lower bound over observational methods.
The reported `0.0975%` ratio at `(n,k)=(17,4)` compares this estimator with the
registered covering estimator.

The matched-random control holds family size equal to the extremal covering
number. Its low completion frequency demonstrates the value of designed block
placement at that exact budget. Random placement with a larger budget can
also cover; v0.2 did not estimate the extra coupon-collector-like overhead.

## Successor question

The high-width endpoints establish that a cost crossover exists, but not its
shape. The successor should locate the minimum intervention width at which a
crossover is certified in each `(n,k,flip-rate)` stratum, while reporting an
interval when exact covering-number optimization times out.
