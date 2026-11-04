# Result v0.29

Worst-path causal branching cost transfers through a causal prefix factor with
a correction equal to local successor-fiber entropy. If `F_i(T)` is the
maximum product of local successor fibers along a target port path, then

`B_i^target(T) <= B_i^source(T) + log2 F_i(T)`.

The normalized limsup gives the directed rate slack. Bidirectional
subexponential products preserve the full branching-cost region. This
criterion is sufficient, not necessary, for other transcript-tree metrics.

The boundary is sharp and distinct from v0.28. A three-step causal factor is a
bijection on four terminal words—terminal transcript fiber one—but changes
branch cost from three bits to two with local product two. Repeated blocks have
terminal fiber one and exact asymptotic gap one third bit per step. Full
`m`-ary local cloning attains gap `log2 m`.

The central implementation checks all 332,928 binary causal morphisms through
depth three, including 10,496 injective-terminal maps with nontrivial local
fibers, and finds no violation. It also checks seven disclosure block powers
through 16,384 leaves, 256 clone rows, and 8,192 sparse horizons. The independent
verifier checks 2,115 ternary-output morphisms, eight block powers, and 16,384
sparse horizons. Eight mutations are rejected twice.

This theorem alone does not transfer the sequential minimax prefix-free cost.
The v0.30 successor now supplies that separate Kraft-rounding argument. Neither
package constructs nonlinear quotients.

The complete 30-package chain passes all 334 tests in 327.19 seconds with
Python bytecode and pytest caching disabled.
