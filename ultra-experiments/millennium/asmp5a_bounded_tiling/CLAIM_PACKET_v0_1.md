# ASMP-5A bounded-tiling finite claim packet v0.1

## Frozen object

Each successor introduces one semantically independent safety obligation. A
root-verifiable certificate is a full binary tree whose leaves name every
obligation exactly once and whose internal nodes apply one fixed sound
conjunction rule. The trusted checker never changes.

Three resources are measured separately:

- total work: number of proof-tree nodes;
- critical path: proof-tree depth;
- peak evaluation memory: Horton-Strahler register number.

## Hypothesis

Through twelve obligations:

1. every valid explicit certificate has exactly `2k-1` nodes, so balancing
   cannot improve total proof work;
2. balanced tiling reaches minimum depth `ceil(log2(k))`;
3. chain and balanced architectures reverse their ranking between the frozen
   shallow-parallel and memory-tight-serial budgets; and
4. any constant-size summary that omits explicit obligation leaves fails the
   unchanged semantic coverage gate.

## Interpretation

The seed tests whether a scalar "proof-strength degradation" measure is
well-posed even in the smallest exact grammar. A ranking reversal means that a
tiling scheme can improve one registered resource while worsening another;
the proof budget must therefore be a declared vector or scalarization.

## Boundary

The result is classical binary-tree combinatorics packaged as a certificate
instrument. It does not model arithmetic reflection, prove bounded Lob, or
establish safe open-ended self-modification.
