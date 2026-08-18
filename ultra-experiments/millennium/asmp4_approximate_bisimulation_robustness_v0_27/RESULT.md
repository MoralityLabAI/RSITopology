# Result v0.27

Exact-safety epsilon-cost alternating bisimulation preserves the ASMP-4
two-port region up to `l_infinity` Hausdorff slack at most `epsilon`. At finite
horizon `T`, the sharp cumulative budget slack is `T epsilon`. The proof
transfers unrestricted causal strategies through representative histories in
both directions and remains valid with adversarial public successors.

The guarantee separates additive rate error from zero-error safety. With a
signed `L`-Lipschitz safety guard and observation error `delta`, strict margin
greater than `L delta` transfers exact safety. Equality is sharp. For every
positive `delta`, two `delta`-close zero-cost loop games can have safe margins
`delta` and `0`, making their achievable regions jump from nonempty to empty.

Central vector-frontier checks cover 256 factor/horizon pairs through 64 raw
states and eight nondeterministic horizons. An independent minimax dynamic
program checks 2,400 factor/weight/horizon comparisons through 96 states. The
cost constant is attained at 32 central and 64 independent horizons; 128 and
256 metric scales independently verify the safety discontinuity. Seven
definition mutations are rejected twice.

An approximate finite quotient is sufficient, not necessary, and this package
does not construct one for arbitrary nonlinear plants. Nonadditive tree costs
and multidimensional adversarial mean-payoff computation remain open.

The complete 28-package chain passes all 314 tests in 294.89 seconds with
Python bytecode and pytest caching disabled.

The v0.28 successor proves that nonadditive port-language cardinality transfers
with a relative history-fiber-entropy correction. Its finite one-class clone
shows why exact state bisimulation does not by itself preserve that tree cost.
