# Prior-art boundary for v0.30

## Classical coding results

Claude Shannon's 1948 communication theory develops instantaneous coding and
the binary code-length inequalities underlying the Kraft calculation used
here: [A Mathematical Theory of Communication](https://doi.org/10.1002/j.1538-7305.1948.tb00917.x).

Brockway McMillan's converse for uniquely decipherable codes establishes the
corresponding length inequality beyond instantaneous codes:
[Two inequalities implied by unique decipherability](https://doi.org/10.1109/TIT.1956.1056818).

No novelty is claimed for prefix-free coding, the Kraft/McMillan inequality,
or the elementary minimax recurrence obtained from it.

## Relation to earlier packages

- v0.3 registers the sequential binary prefix-cost recurrence used here.
- v0.28 controls terminal port-language log-cardinality by full-word fibers.
- v0.29 controls worst-path unrounded branching cost by products of local
  successor fibers and explicitly leaves sequential Kraft rounding open.
- v0.30 proves that missing transfer law and identifies the required
  per-prefix ceiling.

The package's contribution is the precise internal ASMP-4 specialization:
under a causal transcript factor, the sequential minimax prefix cost changes
by at most the worst-path sum of local `ceil(log2 fiber)` terms. The ternary
clone and terminal-bijective disclosure examples delimit two tempting but
false substitutes. This is a registered theorem inside the repository's cost
model, not a claim of priority over classical coding theory.

## Deliberate nonclaims

The package does not address expected code length, probabilistic sources,
arithmetic coding, nonbinary code alphabets, noisy-channel capacity, or a
general symbolic/public quotient construction for nonlinear control systems.
Those would require hypotheses and comparisons beyond the present harness.
