# Result v0.28

Nonadditive port-language entropy transfers through a public quotient with a
sharp correction equal to relative fiber entropy. At horizon `T`, a
port-compatible causal factor with maximum fiber `M_i(T)` gives

`log2 |L_i^target(T)| <= log2 |L_i^source(T)| + log2 M_i(T)`.

The asymptotic directed rate slack is
`limsup log2 M_i(T)/T`, separately for read and write and separately in each
transfer direction. Bidirectional subexponential fibers preserve the complete
capacity region. Uniformly bounded fibers are sufficient, not necessary.

The bound is sharp. A finite raw game with `r*w` states and one quotient class
has exact safety, actions, successor-class sets, and zero additive costs, yet
its read/write transcript fibers are `r^T,w^T` and its corner shifts by
`(log2 r,log2 w)`. Thus finite state-class size does not control public history
multiplicity. Sparse dyadic branching gives an unbounded but zero-entropy
counterboundary.

The central harness checks 2,048 asymmetric clone rows, 30 explicitly
enumerated languages, 4,096 sparse horizons, concentrated maximum-fiber
fixtures, and a limsup/liminf burst schedule. The independent verifier builds
35 tries through 78,125 leaves, exhausts 6,561 multiplicity schedules, and
checks 8,192 sparse horizons. Eight mutations are rejected twice.

This criterion is sufficient, not necessary, for arbitrary transcript-tree
functionals: those require a registered distortion modulus beyond language
cardinality. Quotient construction for general nonlinear plants remains open.

The complete 29-package chain passes all 324 tests in 292.85 seconds with
Python bytecode and pytest caching disabled.

The v0.29 successor handles worst-path causal branching with a local
successor-fiber path product. Its repeated disclosure block has terminal fiber
one but a positive branching-rate gap, separating the two factor invariants.
