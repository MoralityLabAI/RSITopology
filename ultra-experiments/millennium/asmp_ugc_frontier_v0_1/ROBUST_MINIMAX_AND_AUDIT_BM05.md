# BM-05: robust parity monitoring, costed probes, and restoration evidence

**Date:** 2026-11-09. **Status:** finite model theorems and exact CPU controls. This extends [BM-03 finite-sample inference](FINITE_SAMPLE_MONITOR_BM03.md) and [BM-04 adaptive intervention design](ADAPTIVE_MONITOR_BM04.md). The goal is a falsifiable mathematical baseline for provisional **ASMP-14**, whose full adaptive correlation-robust, physically costed and independently attested frontier remains open.

This packet studies **two explicitly different experiment classes**: a minimax binary cycle under adversarial correlated readout masks, and a Bayesian four-label holonomy-search policy with charged, assumed-sound restoration audits. Their individual guarantees must not be silently combined into a single minimax policy theorem.

## A. Sharp conditional correlation-budget minimax theorem (BM-05/T1)

### Frozen class

Let G be a single cycle of length L>=1 with K=F₂ and fixed unknown holonomy h in {0,1}. In each episode a fresh uniform vertex labeling produces a clean full edge-satisfaction vector X in {0,1}^L. Its parity identifies h exactly. Readout reports Y=X XOR M, where the adversary chooses the distribution of a bit-error mask M. The mask is independent of the **current** clean labeling. The monitor sees Y and knows L and the error budget eta.

The adversary may correlate errors *within* an episode and select a new error distribution after observing previous transcripts and h. Crucially, each per-bit conditional error rate after any history and for either h is bounded:

    Pr[M_i=1 | history, h] <= eta,    i=1..L.             (1)

No independence among bits is assumed. This conditional budget is stronger than a marginal error rate averaged over episodes. The monitor receives N full-cycle observations and must decide h with equal-prior Bayes loss. The minimax game allows randomized monitors and arbitrary adversarial strategies satisfying (1).

### Theorem: exact least favorable channel and risk

The XOR parity of M is odd only if at least one bit flips. By the union bound,

    Pr[odd(M) | history,h] <= L*eta.

Set p_star=min(L*eta,1/2), t_star=1-2*p_star. The lower parity signal is t_star. It is attained by the following legal least-favorable distribution, independently at every episode:

    Pr[M=all-zero]=1-p_star,
    Pr[M=one hot at position i]=p_star/L, i=1..L.       (2)

Every marginal is p_star/L<=eta. Conditioned on parity, Y is uniformly distributed within its parity coset. Therefore even the full L-bit pattern contains no additional information beyond parity under (2). The resulting binary hypothesis test is a BSC(p_star) between opposite parity signs.

For arbitrary conditional adversaries, the parity-flip indicators have conditional probability at most p_star. A monotone coupling of successive flips to iid Bernoulli(p_star) variables implies that a parity-majority test has worst-case risk at most the iid BSC(p_star) majority risk. The stationary least-favorable law (2) attains that risk. Hence

    minimax_R_N(L,eta)
      = Pr[K<N/2] + (1/2) Pr[K=N/2],                    (3)
    K ~ Bin(N,(1+t_star)/2).

This is an **exact minimax theorem for this specifically declared class**. For p_star=1/2 it yields risk 1/2 for every N. For 0<t_star<1, the fixed-confidence sample scale in the low-signal regime is Theta(t_star^(-2)) by standard Hellinger and Hoeffding inequalities. At t_star=1 one sample identifies h.

### Concrete difference from iid bit noise

For L=4 and eta=1/8, the least-favorable correlated distribution has p_star=1/2, hence complete parity erasure and minimax risk 1/2 for all N. Independent bit flips with the *same per-bit rate* retain parity signal (1-2eta)^L=(3/4)^4=81/256, which supports consistent testing as N grows.

At L=4 and eta=1/16, the conditional minimax parity bias is t_star=1/2. Three episodes yield exact minimax error 5/32; the iid independent-bit model would give a different, more informative channel.

### Marginal-only across-episode noise changes the conclusion

If the cap Pr[M_i=1]<=eta is imposed only over the **entire trajectory**, choose one shared M from distribution (2) and reuse it for every episode. Each clean X is freshly sampled, so all observed parities share the same unknown flip. No number of repeated full-cycle observations removes that latent ambiguity; the optimal equal-prior error against this one legal noise process remains p_star.

Thus the marginal-only class has minimax error **at least p_star for all N**, even though conditional-budget risk in (3) may tend to zero. This is a sharp *negative control*, not a complete characterization of all marginal-only adversaries.

## B. Unknown restoration drift makes holonomy nonidentifiable (BM-05/T2)

When an externally applied known cycle shift is x in K=F₂^s, suppose the actual baseline includes an unknown, persistent restoration drift d in K. Each response law depends on the *effective holonomy*

    h_eff(x) = h + d + x.                                  (4)

For any a in K, worlds (h,d) and (h+a,d+a) yield identical effective holonomies for **every** x. By induction on the policy history, any adaptive monitor whose only data are these cycle-response laws receives identical transcript distributions in the two worlds. For example, (h=1,d=2) and (h=3,d=0) over F₂² are indistinguishable even under unlimited chosen shifts.

Hence the allowed intervention set is insufficient to identify the original h without a trusted external root-state anchor or independent restoration certificate. A symmetric prior over the two indistinguishable worlds gives optimal original-state classification error 1/2.

A composable *conditional audit* statement is elementary: if at intervention i an independently justified root attestor has false-restoration-acceptance probability bounded by rho_i, conditional on the registered history, then

    Pr[some false restoration accepted in B rounds)
       <= min(1, sum_{i=1}^B rho_i).                      (5)

The event of *authorizing while an accepted restoration was false* is bounded by the same quantity. Equation (5) is a union bound with externally verified premises. A monitor's own circular report cannot supply those premises.

## C. Costed exact Bayes design with hard budget (BM-05/T3)

### Different model from part A

Freeze q in {2,4}, a cycle length 1<=L<=4, known iid bit-flip readout eta, and a **uniform prior** on numerical h in F₂^s. At each episode the monitor chooses x in K, receives the full failure-count k and returns the graph shift to baseline using an assumed-sound independent restoration audit when x!=0. Each action has *integer resource cost*

    c(x) = observation_units
         + shift_bit_units * HammingWeight(x)
         + restoration_audit_units * 1[x!=0].            (6)

The model enforces positive observation and restoration audit costs. It caps the total cost along **every trajectory** by R, limits the number of episodes to N, allows early stopping, and maximizes

    Pr[h_hat=h] - lambda * E[total resource units].       (7)

This utility is a mathematical tradeoff with declared rational price lambda. It does not assign real dollar value to safety or empirically validate any audit.

### Exact Bellman recursion

Let w_h be unnormalized weights, V(w,n,r) optimal *unnormalized* utility from a state with n possible episodes and r resource units left. Writing p_flat(k) for x=h and p_nonflat(k) otherwise,

    V(w,0,r) = max_h w_h,

    V(w,n,r) = max{
       max_h w_h,
       max_(x:c(x)<=r) [
         sum_k V((w_h*p_(h,x)(k))_h,n-1,r-c(x))
         - lambda*c(x)*sum_h w_h
       ]
    }.                                                    (8)

Here p_(h,x)=p_flat if h=x and p_nonflat otherwise. The proof is backwards induction on the finite decision tree. Exact posterior arithmetic gives optimal identification probability, expected resource units, expected episode count and the first shift. Randomizing actions cannot improve the maximized expected linear utility.

### Exact audit-budget witness

For q=4, L=3, eta=0, at most two episodes, observation cost 1, per-set shift-bit cost 1, restoration audit cost 1, and price lambda=1/100:

| Worst-case pathwise budget R | Optimal net utility | Correct identification | Expected units |
|---:|---:|---:|---:|
| 0 | 1/4 | 1/4 | 0 |
| 1 | 121/400 | 5/16 | 1 |
| 2 | 0.32921875 | 89/256 | 59/32 |
| 4 | 0.338046875 | 189/512 | 199/64 |

The optimal first shift is x=0 for positive budgets in this witness, since a passive first measurement is inexpensive and preserves the choice to make a later active intervention. Under budget two, the monitor can afford two passive measurements but no active shift. Under budget four, it can afford one passive observation followed by one audited nonzero shift on selected branches. The gain in identification probability must be weighed against the added expected resource charge.

An **independent exhaustive enumerator** checks all first actions and every mapping from the first observed failure count to a second action or early stop. It agrees with the dynamic program across budgets zero through five. A separate test confirms that sufficiently expensive restoration audits change the optimal policy, and at price lambda=1 early stopping is optimal.

### Claim boundary

The costed Bayes model assumes that every paid restoration audit is sound. Its value is not a minimax bound against hostile false attestations; that requires a joint strategic model with calibrated external rho_i. The robust correlation class in part A concerns binary parity, and is not automatically a valid noise law for the q=4 failure-count sufficient statistic.

## D. Verification and next mathematical frontier

New independent Python controls:
- [correlated_minimax.py](correlated_minimax.py) and [test_correlated_minimax.py](test_correlated_minimax.py): least-favorable mask construction, exact full-pattern total variation, enumeration of admissible small joint-error distributions, independent likelihood products for multi-episode minimax, restoration gauge aliasing, and conditional union bound.
- [audit_budget_design.py](audit_budget_design.py) and [test_audit_budget_design.py](test_audit_budget_design.py): exact rational cost-aware Bellman recursion, early stopping, posterior expected charges, worst-case resource cap and independent exhaustive two-step policies.

The focused Linux workflow executes the entire ASMP seed suite under five minutes, including all prior BM-01..04 controls. This package uses the standard library and launches no GPU or live model actions.

**Open ASMP-14 extension:** derive a single minimax theorem with an adversary allowed to choose a family of correlated and partially observed error channels, the controller choosing adaptive interventions under certified perturbation budgets, and an independently authenticated restoration process that itself has adversarially controlled error. A credible theorem needs a sharp non-inert positive class, exact error/utility quantifiers, matching information lower bounds, and a novelty audit against robust sequential design, partially observed stochastic games, and interactive-proof soundness. BM-05 supplies exact baselines and negative controls, not that general result.


## E. A two-sided non-inert certification gate (BM-05/T4)

The [executable gate](robust_certification_gate.py) turns the binary minimax parity risk and externally supplied restoration error budgets into **sufficient** authorization conditions. Consider N full-cycle episodes, of which at most B involve a known nonzero shift followed by a mandatory independent root attestation. The per-bit conditional noise law from part A is assumed on all correctly restored episodes. For each potential shifted step i, let rho_i bound the conditional probability of falsely accepting an unrecovered state, and let kappa_i bound the conditional false rejection of a genuinely restored state.

Write R_N^* for the exact worst-case binary parity-majority error from (3). If the output is released only after all required audit passes, then

    Pr[authorize wrong original-h verdict] <= R_N^* + sum_i rho_i,
    Pr[authorize correct verdict | genuine restoration]
        >= 1 - R_N^* - sum_i kappa_i.                        (9)

These statements follow by event decomposition: if each required restoration is sound, parity-majority has error at most R_N^*; accepting a failed restoration contributes at most sum rho_i. In the all-genuine-restoration reference system, abstention due to false audit rejection costs at most sum kappa_i, while the parity error costs at most R_N^*. The bounds remain valid with adaptive timing because the audit coverage assumptions are conditional on the preceding history. False-accept **and** false-reject calibrations are mandatory for a usable certificate.

For a declared maximum wrong-authorization alpha and minimum correct-authorization u0, approve only if the corresponding right-hand bounds in (9) meet alpha and u0, and the worst-case total **integer units** fit the hard cap:

    units = N*observation_units
          + B*(shift_bit_units + restoration_audit_units).

This freezes B as a maximum permitted number of nonzero F₂ shifts. The utility floor excludes an always-abstain solution.

**Exact positive control:** L=4, per-edge conditional noise eta=1/16, N=3, B=3. The minimax parity error is 5/32. If each accepted-failure audit bound rho_i=1/1000 and each genuine-restoration rejection bound kappa_i=1/100, the gate yields

    wrong-authorization <= 5/32 + 3/1000 = 0.15925,
    correct-authorization >= 1 - 5/32 - 3/100 = 0.81375.

With observation cost 1, shift cost 1 and audit cost 1, worst-case resources are 9 units. This meets the sample targets alpha=1/5 and u0=4/5 if the resource cap is at least 9. The targeted tests reject the same noisy experiment at a tighter eight-unit cap, an inadequate attestation error budget, and a correlated-error allowance eta=1/8.

The audit error rates are **premises** that must come from a genuinely independent attestation instrument; the finite code cannot establish that a real model edit restored its state. The probability bounds are conservative Bonferroni certificates, and the general joint adaptive minimax frontier remains an open research problem.
