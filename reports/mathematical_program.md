# A Spectral-Bundle Mathematics for Bounded Self-Improvement

## Scientific state

The JSpace controls deflate topology as an independent explanation: two graphs
with the same harmonic/global-section projector receive the same static score.
The surviving object is operator geometry. For each prompt or context `p`, the
reliability-weighted normalized sheaf Laplacian is

\[
\widetilde L_p = \frac{\delta_p^\top W_p\delta_p}
{\lambda_{\max}(\delta_p^\top W_p\delta_p)}.
\]

For a frozen spectral interval `I_b`, define the prompt-specific band

\[
E_b(p)=\operatorname{im}\mathbf 1_{I_b}(\widetilde L_p),\qquad
P_b(p)=\mathbf 1_{I_b}(\widetilde L_p).
\]

The proposal is to treat `p -> E_b(p)` as an empirical spectral bundle. Its
cross-prompt consensus is not a coordinate intersection, which is brittle, but
the high-occupancy eigenspace of the mean projector

\[
\bar P_b=\frac1{|P|}\sum_pP_b(p),\qquad
U_b=\operatorname{im}\mathbf 1_{[\rho,1]}(\bar P_b).
\]

An eigenvalue of `bar P_b` is the fraction-like occupancy of a direction across
prompt subspaces. The inferred dimension `rank(U_b)` replaces the guessed
“512-dimensional tuple.” If no band has sufficient occupancy and rank, the
high-dimensional-structure claim stops.

The present implementation assumes every prompt operator acts on one registered
edit space. Different sites or layers require registered Jacobian transports
into a common reference stalk, followed by the same projector construction.
If those transports fail JSpace naturality/secant gates, no cross-site bundle is
defined.

## Reinforcement-learning policy branch

For candidate update `x`, the target-blind bundle-energy feature is

\[
e_b(x)=\frac{\|U_b^\top x\|^2}{\|x\|^2}.
\]

Grouped training folds estimate whether this feature adds causal utility beyond
norm, rank, support, site/layer, family, uncertainty, and Jacobian visibility.
It does not replace the reward model. If it passes, it controls allocation:

\[
\pi_\eta(i\mid s)\propto
\pi_0(i\mid s)\exp\{\eta\widehat{\Delta u}_i\},
\]

where `eta` is the largest value whose measured `KL(pi_eta || pi_0)` is at most
the frozen budget. This is a training-data or candidate-sampling policy, not an
unbounded reward-maximizing controller. Its gate requires grouped held-out
prediction gain, standardized positive realized return uplift, and the KL
bound. Protocol v0.2 standardizes each held-out fold's weighted-minus-uniform
uplift by that fold's outcome standard deviation. The earlier absolute `0.03`
gate is preserved in v0.1 and failed the rank-32/dimension-384 synthetic run;
it is not retroactively reinterpreted.

Protocol v0.2.1 additionally reports
`IC = standardized_uplift / sqrt(2 * realized_KL)` as a descriptive
linear-response diagnostic. It does not replace the primary standardized
uplift gate because equivalence fails when folds do not bind at the same KL
cap. Geometry also reports its occupancy margin above the frozen threshold;
small margins warn that downstream utility may already be fragile without
changing the necessary-but-not-sufficient geometry gate.

## Coordinated-edit branch

Bundle energy discards sign, so direct proposals use coordinates
`z=U_b^T x`. Training folds fit residual causal outcomes after the same nuisance
baseline. A normalized proposal is

\[
x_* = \frac{U_b\hat a}{\|U_b\hat a\|},
\]

and remains proposal-only until a separately registered trust radius, damage
suite, and reveal join exist. The primary gate is grouped held-out prediction;
the structure must also beat a matched-rank Haar subspace. The June VPD receipts
cannot test this because the actual edit matrices and exact candidate pairing
were not preserved.

## What the synthetic control establishes

The planted fixture contains a stable rank-12 low-frequency bundle. Geometry is
sealed before outcomes. On the signal fixture, the bundle improves held-out
policy-outcome MSE and supports a KL-bounded positive allocation uplift; signed
coordinates also beat a matched-rank Haar subspace. With the identical geometry
but the outcome signal removed, both downstream gates fail. This validates the
instrument’s polarity, not a transformer claim.

The next real milestone is a one-prompt operator benchmark that serializes the
actual common-space edit vectors and matrix-free Laplacian actions. Only after
that benchmark passes N0/R0/A0 should multiple prompt operators be sealed and
outcomes collected. A real self-improvement claim additionally requires an
external task improvement, no collateral regression, independent run
replicates, and comparison with ordinary RL/data selection and interp-blind
low-rank edit baselines.
