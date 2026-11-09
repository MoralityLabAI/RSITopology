# BM-04: exact adaptive intervention design under a finite holonomy prior

**2026-11-09.** Status: exact finite Bayes decision calculation with independent exhaustive policy checks. This is a new *bounded example for the ASMP-14 research packet*, using established sequential-experimental-design mathematics. The original [BM-02 active cycle probe](ACTIVE_PROBE_RECOVERY_BM02.md) supplies the intervention model and [BM-03 iid monitor likelihood](FINITE_SAMPLE_MONITOR_BM03.md) supplies the observation law.

## 1. Fixed registered inference game

Choose an alphabet K=F2^s, q=|K|, a known simple cycle of length L, and an unknown holonomy h in K with a **uniform prior** on its q values. In each of N independent episodes, an external monitor chooses one known shift x in K to apply to a selected cycle edge, then observes the complete Boolean satisfaction pattern under a fresh uniform vertex labeling and independently flipped readout bits with a known rate eta. After each episode the edge perturbation is precisely restored to baseline. The frozen target is to identify the exact h, with zero-one loss and maximum N observations.

For the failure count k in 0..L let

    p0(k) = Pr(k observed failures | x=h),
    p1(k) = Pr(k observed failures | x!=h).

These are the exact count distributions from BM-03. They are insensitive to the *particular* nonzero difference h+x, so every intervention x asks whether h equals x through a binary statistical experiment. The count k is sufficient for that episode's likelihood; no information is gained by retaining the individual Boolean edge pattern after its count is known.

The finite policy chooses x_t adaptively from earlier counts, with final estimator h_hat. The primary statistic is the maximum uniform-prior probability Pr(h_hat=h). This is a Bayes criterion for the specified prior, and is not automatically a uniform worst-case guarantee over h or over adversarially correlated observation laws.

## 2. Exact dynamic-programming theorem

Let w_h be *unnormalized posterior weights* on h. Initially w=(1,...,1). Define V_N(w) as the maximum total winning mass after N remaining observations, with

    V_0(w)=max_h w_h,

    V_N(w)=max_{x in K} sum_{k=0}^L
             V_{N-1}((w_h*p0(k) if h=x
                             else w_h*p1(k))_{h in K}).        (1)

The Bayes-optimal identification success is V_N(1,...,1)/q. The proof is finite backwards induction over the experimental decision tree: conditional on action x and observation k, the unnormalized posterior becomes the vector shown in (1), and the final zero-one Bayes decision selects the largest component. Randomized actions cannot improve a maximum of linear conditional payoffs.

Since all x are available and hypotheses are symmetric, V_N(w) is invariant under permutations of the entries of w. Sorting successor weight vectors creates an **exact**, finite state-space reduction. The code enumerates q<=4, L<=4, N<=6; these are deliberately small computation limits.

### Matched fixed-schedule baseline

A nonadaptive schedule commits before seeing outcomes to all N shifts x_1,...,x_N. Because episodes are conditionally independent, its order is irrelevant, and its exact likelihood depends only on the per-shift visit-count allocation (n_0,...,n_(q-1)). The optimal nonadaptive success is computed by enumerating all nonincreasing q-partitions of N and evaluating the same exact likelihood tree **without** observation-contingent action selection.

## 3. Strict finite adaptive advantage: q=4, L=3

The clean cycle failure-count laws are

    p0 = (1/16, 0, 9/16, 3/8),
    p1 = (0, 3/16, 3/8, 7/16).

For N=2, a first query at x=0 gives a count k. An optimal second action is:

| First observation k | Best second shift |
|---:|---|
| 0 | Any shift; h is already identified |
| 1 | Any x!=0 |
| 2 | Repeat x=0 |
| 3 | Any x!=0 |

This yields **exact Bayes success**

    best adaptive (N=2) = 189/512 = 36.9140625%,
    best fixed    (N=2) = 183/512 = 35.7421875%,
    strict gain          =   3/256 =  1.171875 percentage points.

The optimal fixed two-shot allocation tests two distinct shifts. An **independent brute-force oracle enumerates all 4^4=256 maps** from the first failure-count observation to the second shift and agrees with the recursive dynamic program. A separate brute force checks all 4^2 fixed schedules.

At N=3, the optimal adaptive success is 3467/8192 = 42.32177734375%, versus 1617/4096 = 39.4775390625% for the best fixed schedule (allocation (2,1,0,0)). The absolute improvement is 233/8192, approximately 2.844 percentage points. This is a valid strict finite example of the value of feedback within the registered monitor grammar.

When q=2 and eta=0, one full-cycle query distinguishes the two possible numerical holonomies exactly, so further adaptivity cannot help. If eta=1/2, the iid readout destroys all information and success remains exactly 1/q under both monitoring policies for every N.

## 4. ASMP-14 research obligation

This bounded result gives ASMP-14 an **experimental-selection** dimension. A complete mathematical frontier would characterize joint budgets for:

- external shift/restore intervention cost, amplitude and perturbation damage;
- sample acquisition and correlated or adversarial readout noise;
- prior-sensitive Bayes versus worst-case false-authorization guarantees;
- ability to query several cycles jointly or reuse a persistent labeling;
- proof and attestation of the intervention-to-observation linkage.

A sharp scalable theorem should supply matching minimax information lower bounds and a constructive near-optimal policy for a specified class of gain graphs. The tiny dynamic program is an exact reference oracle, not an algorithm for large q, and is subject to a resource cap.

**Novelty boundary:** Classical active hypothesis testing already demonstrates strict benefits for causal control in multihypothesis sensing. Relevant work includes [Chernoff, Sequential Design of Experiments (1958/1959)](https://statistics.stanford.edu/technical-reports/sequential-design-experiments), [Naghshvar and Javidi, Active Sequential Hypothesis Testing (2012)](https://arxiv.org/abs/1203.4626), and [Nitinawarat, Atia and Veeravalli, Controlled Sensing for Multihypothesis Testing (2013)](https://doi.org/10.1109/TAC.2013.2261188). Any new ASMP-14 theorem would need a substantive gain-graph/holonomy constraint, admissible intervention proof, or distributionally robust complexity frontier beyond that existing theory.

## 5. Reproducibility

- [adaptive_monitor_design.py](adaptive_monitor_design.py): exact memoized dynamic program, fixed-schedule allocation search and optimal second-step action table.
- [test_adaptive_monitor_design.py](test_adaptive_monitor_design.py): exact two-step independent brute-force policy enumeration, comparison to optimal fixed schedules, strict advantage witnesses, BSC(1/2) null, binary positive control, and input/resource gates.
- All outputs are rational arithmetic. No GPU, API, real model, or randomness used.
- Reproduce with: python -m unittest discover -s ultra-experiments/millennium/asmp_ugc_frontier_v0_1 -p 'test_*.py' -v

The research packet remains **provisional**, with ASMP-14 classified as a top-level contender requiring prior-art and independent hostile review.
