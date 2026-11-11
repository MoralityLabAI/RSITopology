# BM-02: controlled cycle perturbations repair the Boolean-monitor blind spot

**2026-11-09.** This is a conditional constructive complement to [BM-01](BOOLEAN_MONITOR_QUOTIENT_BM01.md). The intervention is an externally registered operation on a hidden edge translation, rather than a passive observation or an agent's self-reported state. All results below are elementary finite identities; the physical admissibility of the intervention requires separate verification.

## Mathematical interface

Fix a simple directed cycle C of length ell, K=F₂^s, q=2^s, and unknown holonomy h in K. A control action chooses an edge e in C and a *known* shift x in K and applies c_e <- c_e+x, leaving all other shifts fixed. The monitor then receives independent uniform-label Boolean satisfaction patterns as in BM-01, including the indicators for all edges of C.

Under this intervention,

    Hol(C; c+x 1_e) = h+x.

Therefore the resulting cycle is balanced exactly when x=h. The induced binary monitor becomes a **K-valued equality tester** for the unknown cycle holonomy, provided it has a reliable way to decide balancedness.

### Ideal information theorem

If an ideal balance oracle returns the exact bit 1[h=x] for a user-selected candidate x in K, then q-1 worst-case queries identify h:

- try q-1 distinct values;
- a positive reply yields h immediately;
- q-1 negative replies determine the sole remaining candidate.

This is worst-case optimal for deterministic equality-only queries, since each negative reply eliminates exactly one member of a q-element candidate set. The construction applies independently to each fundamental cycle (whose intervened edge must have known orientation). The count of q-ary holonomy queries is distinct from the number of **physical binary measurement episodes** required to implement each ideal balance test.

### Finite-sample constructive bound

For the modified cycle C, let A be the event that all ell satisfaction bits are true in one fresh uniform-label episode. Exact counting gives

    Pr(A | x=h)=q^(1-ell),
    Pr(A | x!=h)=0.

Thus observing A is a one-sided perfect witness that x=h. Across N independent episodes, the false-negative probability in the matching case is

    (1-q^(1-ell))^N.

The smallest N making this at most beta satisfies

    N >= ceil(log(beta)/log(1-q^(1-ell)))              (ell>=2),

and when ell=1, one episode suffices. For q-1 sequential candidate tests with target total error alpha, taking beta=alpha/(q-1) on each test and using a union bound gives a sufficient worst-case budget

    (q-1)*ceil(log(alpha/(q-1))/log(1-q^(1-ell)))

independent sampling episodes, with the usual ell=1 convention. This is a conservative constructive bound. A full-pattern likelihood-ratio test can exploit more information, as in the existing exact cycle-TV result in [ASMP-14 sharp bounds](SHARP_VISIBILITY_AND_DECODING_BOUNDS.md).

## Smallest cactus intervention witness

The 6-vertex, 7-edge connected BM-01 pair has second-triangle holonomy h2=1 (aligned world) or h2=2 (independent world) in K=F₂². Before intervention, their complete passive Boolean laws have TV=0.

Apply x=1 to the closing edge of triangle two. Its new holonomy is zero in the aligned world and 3 in the independent world. The resulting complete Boolean laws have exact TV

    (2/4)^(3-1)=1/4.

The optimal equal-prior single-episode classification success rises from 1/2 to 5/8 under this declared intervention. In particular, the all-satisfied event on triangle two has probability 1/16 in the aligned case and zero in the independent case. Repetition gives a one-sided arbitrarily confident test.

**The change in access class is the result.** A passive Boolean satisfaction channel identifies only the biased-graph balance structure; an authenticated, controllable group translation lets the monitor test hidden cycle gains against known values. Any AI application must account for the ability to apply, observe, and restore controlled perturbations, including their effects on the system and downstream policy.

## Verification

- [Intervention oracle and exact episode-count code](active_cycle_probe.py).
- [Tests](test_active_cycle_probe.py) exhaustively recover all four-cycle F₂² holonomies from ideal equality probes, compare the independent cactus law before/after intervention, verify loops and parallel edges, reproduce the exact all-satisfied event probabilities, and test invalid interface requests.
- Independent direct-label enumeration from [finite_seed.py](finite_seed.py) checks the balancedness probability. All tests are CPU-only.

### ASMP novelty boundary

Controlled system identification and active experiment design already use interventions to expose invariants lost in passive observations. This is a precise ASMP-14 observation-grammar baseline. A new top-level theorem needs to optimize **intervention damage, restored-state verification, noisy or missing observations, sample budget, and adaptivity** under realistic capabilities and a declared policy predicate. An exact equality-query reconstruction by itself is classical.
