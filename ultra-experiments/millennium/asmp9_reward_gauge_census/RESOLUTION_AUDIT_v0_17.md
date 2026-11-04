# ASMP-9 resolution audit after v0.17

## Verdict

ASMP-9 remains unresolved.

Version v0.17 closes the multi-cycle transfer question named by the v0.16
audit inside one declared independent Bernoulli comparison model. It does
not close the full value-identifiability problem over reward classes,
response models, query interfaces, and environment interventions.

## Milestone closed by v0.17

The v0.16 audit asked for a graph-wide objective that:

1. reduces to the one-cycle availability object;
2. supplies certified allocation conditions;
3. contains a counterexample to naive uniform allocation;
4. distinguishes finite from asymptotic claims; and
5. exposes the remaining adaptive and misspecified-response questions.

Version v0.17 supplies:

```text
dim(S_t)=beta_1(H_y)
```

for the conditional-fiber span and residual-live subgraph; an exact
three-status reliability polynomial; endpoint reduction on the registered
probability box; and the asymptotic allocation game

```text
tau_G* = max_w min_(B in B_G) sum_(e in B) w_e
       = min_mu max_e P_(B~mu)[e in B].
```

The matching primal/dual certificates solve that exponent problem for the
fresh controls. The registered theta `(1,3,3)` census then proves that uniform
finite allocation is strictly suboptimal at `N=14` and `epsilon=2/7`.

This refutes the naive extension of the v0.16 balancing theorem. The graph
object replacing raw balance is the hypergraph of minimal bad boundary
supports.

## Status against the ASMP-9 obligations

### 1. Maximal invariance groups

**Partially addressed in declared finite models; not closed generally.**

Versions v0.1-v0.13 characterize additive, affine, potential-shaping,
discounted gain-graph, context-gluing, scalar-gradient, and conditional
finite-sample quotients. Version v0.17 assumes the conditional scalar-gradient
quotient and adds no maximal invariance theorem for broader reward or behavior
classes.

### 2. Necessary and sufficient query/environment interventions

**Sharp for conditional full-rank liveness on a known finite comparison
graph; open for general interfaces.**

The residual-rank theorem gives a necessary and sufficient realized-data
condition:

```text
full quotient available
iff every original nonbridge edge lies on a directed residual cycle.
```

It does not characterize arbitrary preference queries, adaptive policies,
transition interventions, history-dependent interfaces, or unknown
environments.

### 3. Sharp query, sample, and intervention-order bounds

**The asymptotic nonadaptive graph-allocation exponent is characterized.
Exact finite design remains open generally.**

The minimal-bad-support game is a sharp asymptotic exponent result for every
finite graph in the frozen response model. Exact finite optimality is proved
only for one registered theta cell; unlike v0.16, there is no theorem
characterizing every finite total budget on every graph.

No minimax downstream test-power theorem, adaptive allocation bound,
dependent-sample bound, or general policy-query rate is established.

### 4. Robustness to behavioral misspecification

**Open and now more clearly isolated.**

The status compression and endpoint theorem require independent Bernoulli
edge trials with fixed counts and a known symmetric probability interior.
Dependence can change the reliability law without changing the graph.
Unknown links, asymmetric interiors, strategic demonstrators,
nonstationarity, and non-expected-utility behavior remain outside the result.

### 5. No-go theorem when no coherent latent value object exists

**Only finite special cases exist.**

The contextual-gluing, unknown-link, deterministic-policy, and
conditional-fiber results provide explicit obstructions and unavailable
states. They do not classify all demonstrator laws for which no stable scalar
or quotient value object exists.

## Evidence audit

The scientific run was prospectively registered before the fresh
theta `(1,3,3)` allocation census:

- implementation freeze:
  `f6bb525ff62aea1c9d2c3c1674090063c819a65b`;
- registration commit:
  `0297fcddbe34ea028597fe60b0d3cb849deabfaf`;
- registration SHA-256:
  `fc0931d34707dad22481e34c3fb50b686978e444828adbd1fd9686b599813b1b`.

All ten gates passed. The registered run checked 3,852 count
representatives, 1,900 conditional fibers, 48,924 endpoint-monotonicity
comparisons, 36 minimal bad supports, three primal/dual certificate pairs,
and all 1,716 positive allocations in the finite theta cell.

A separate verifier used transitive closure instead of the implementation's
SCC routine and independently reconstructed the fibers, probabilities,
supports, certificates, and full allocation digest. All 41 checks passed.
A clean detached replay ran 11 focused tests and reproduced every scientific
payload field.

## What is now theorem versus finite evidence

Analytic:

- residual-cycle fiber-rank identity;
- lossless `Z/I/F` compression;
- coordinatewise endpoint reduction;
- minimal-bad-support large-deviation exponent;
- primal/dual allocation game.

Prospectively verified finite evidence:

- six fresh capacity cells and three fresh probability cells;
- exact registered support certificates on three graphs;
- one theta `(1,3,3)` finite counterexample to uniform allocation.

The finite census verifies the implementation and supplies the registered
counterexample. It is not the proof of the general analytic statements.

## Next load-bearing sequence

### A. Exact finite-budget graph design

Determine whether exact maximin allocation on a general graph admits a
combinatorial characterization, certified approximation, or hardness result.
The large-deviation hypergraph game need not determine the finite optimum.

### B. Adaptive allocation

Freeze a sequential policy class that can choose the next comparison edge
from observed counts. Compare its worst-case stopping time or budget with the
best nonadaptive design. A positive adaptive result must charge all selection
information and cannot reuse the latent probabilities.

### C. Response misspecification

Replace independent edges by a registered dependence class or a
contamination neighborhood. Determine which parts of residual-rank liveness
remain deterministic and which probability/allocation conclusions fail.

### D. Behavioral bridge

Only after A-C should the program attempt a preference or policy-learning
bridge. Such a bridge must first test whether a coherent quotient value object
exists; conditional availability cannot certify the response model whose
nuisance it removes.

## Epistemic boundary

Version v0.17 materially advances the access-design component of ASMP-9 and
refutes uniform edge balance as a general rule. It does not show that human or
model preferences are coherent, that Bradley-Terry is a valid behavioral
model, that the selected comparisons improve downstream decisions, or that
ASMP-9 is resolved.
