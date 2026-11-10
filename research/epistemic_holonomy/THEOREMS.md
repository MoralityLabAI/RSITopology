# EH-01: Epistemic holonomy of provenance-marked evidence

**Status: 2026-11-10.** The finite results here are elementary theorems with proofs. The numerical results concern a synthetic binary experiment. Relevance to recurrent neural networks and AI control is an untested hypothesis. Local candidate labels EH-T1/2/3 avoid colliding with the broader ASMP numbering.

## Object and observation contract

Let G=(V,E) be a finite directed **multigraph whose vertices mark authenticated independent-information states**. A source-preserving echo gives the observer no new information, so it is identified with the original information state and induces a self-loop. Each edge e carries the log-odds increment w_e claimed by the updating policy. The mark is essential: reclassifying a copy as an independent source changes the graph and may erase the relevant cycle.

Define the incidence matrix B with B[u,e]=-1 and B[v,e]=+1 for an edge from u to v; self-loop columns vanish. A finite edge cochain w has the unique orthogonal decomposition

    w = B^T phi + h,  B h = 0,  h perpendicular to im(B^T).

The vertex potential phi is unique only up to a constant on each connected component. In matrix notation,

    h = [I - B^T (B B^T)^+ B] w.

For every oriented fundamental cycle c, its **epistemic holonomy** is the additive log-odds integral c^T w. It is an abelian additive quantity defined by this particular graph. It is distinct from the O(r) matrix-valued loop transport used elsewhere in RSI-Topology.

## EH-T1: exactness and gauge-invariant cycle obstructions

For any finite directed multigraph, the following are equivalent:

1. There exists a vertex potential phi satisfying w=B^T phi.
2. All directed, signed cycle integrals c^T w vanish.
3. The Hodge residual h is zero.
4. Every fundamental cycle integral relative to any spanning forest is zero.

**Proof.** The identity (ker B) perp = im B^T proves the equivalence of the first three statements. Every non-tree edge defines one fundamental cycle, and its coefficient at that edge is one while the other fundamental cycles have zero there. These cycles span ker B. Their number equals |E|-|V|+number_of_components by rank-nullity. Hence the fourth statement is equivalent. A gauge change w -> w+B^T psi leaves cycle integrals unchanged because Bc=0 and leaves h unchanged by orthogonal projection. QED.

**Boundary:** this proves path independence conditional on the information-state marking. It is silent about whether any interpretation is true. Every tree has zero cycle rank, including trees whose belief updates are badly mistaken.

## EH-T2: recursive certainty inflation from informational copies

Assume H is a uniform random binary truth, X is one authentic observation with Pr(X=H)=r, and 1/2<r<1. The subsequent messages Y_1,...,Y_(N-1) depend on H only through X. Equivalently, H -> X -> (Y_1,...,Y_(N-1)) is a Markov chain.

The chain rule yields

    I(H;X,Y_1,...,Y_(N-1)) = I(H;X) = 1-h_2(r).

Suppose the updater mistakes N copies of the observed bit for independent conditionally reliable observations. Define ell=ln[r/(1-r)]. The reported confidence in the observed bit becomes

    q_N = sigmoid(N ell),

whereas actual classification accuracy stays r. The calibration gap is q_N-r. Expected negative log likelihood is

    L_N = r log(1+exp(-N ell)) + (1-r) log(1+exp(N ell)).

Differentiating for real N gives

    dL_N/dN = ell [sigmoid(N ell)-r].

Since sigmoid(ell)=r, the expected loss rises strictly for N>1. Its asymptotic slope is (1-r)ell>0 even though the information about H remains fixed. On the correctly provenance-quotiented graph, the extra N-1 messages are self-loops. Naively assigning ell to each loop gives nonzero cycle holonomy; assigning zero to the duplicates makes the same graph flat.

**Proof.** Conditional mutual information I(H;Y|X)=0 under the Markov hypothesis. Bayes likelihood odds are multiplied by r/(1-r) once per falsely treated independent copy. The accuracy, log-loss formula, derivative, and cycle result follow directly. QED.

**Boundary:** if a retransmission supplies new independently informative material or changes the underlying truth, the Markov assumption fails. For an observed X=0 the sign of every log increment reverses; the magnitude of loop defects is unchanged.

## EH-T3: the flat-but-false impossibility boundary

Let two equally likely worlds W0 and W1 have externally marked, opposite correct binary responses. Suppose their observable transcript distributions are identical under every adaptive auditing policy, including their stopping choices. Any decision rule, deterministic or randomized, has equal-prior accuracy exactly 1/2.

**Proof.** Fix an auditing policy and couple the worlds using the same transcript law. Given any transcript and auditor random seed, its guess is the same in both worlds, while the correct answers are opposite. The two correctness indicators sum to one. Averaging proves the result. QED.

The belief cochain can be a perfectly exact gradient in each world. Vanishing holonomy does not distinguish the correct world. Independent semantic markings and outcomes are indispensable. This is analogous to QD-03's demonstration that an unmarked operator spectrum forgets the chosen macroscopic observation partition.

## Matched synthetic controls and interpretation

The naive echo and provenance-corrected echo use the same graph, edges, and evidence IDs, with N-1 self-loops. The corrected updater assigns zero weight to those loops. The independently generated N-signal condition instead has N authenticated source IDs and a chain of N observations; its true posterior follows a binomial mixture. A gauge test adds B^T psi, demonstrating that both cycle integrals and the Hodge residual are invariant. A two-world impossibility test gives a flat system with unidentifiable correctness.

With r=0.6 and N=10: naive confidence 0.982954; actual accuracy 0.6; naive expected log loss 1.63905 nats; fresh-data expected log loss 0.52213 nats; mutual information of the echoed condition 0.0290494 bits.

The existing signed-coordinate authorization policy remains governed by the established Grassmann-bundle identity system. These finite mathematical results confer no holonomy_clean certification and imply no general recursive self-improvement risk guarantee.

For a future real-model study, freeze evidence origin and source groupings before outcomes, pair graph-cycle metrics with externally assessed calibration, and compare against count/entropy/logit and nuisance baselines on held-out independent sources. The link between these cochain quantities and neural representation holonomy remains open.
