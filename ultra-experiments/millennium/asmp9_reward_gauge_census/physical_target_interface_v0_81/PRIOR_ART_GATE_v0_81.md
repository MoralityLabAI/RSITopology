# Prior-art gate for ASMP-9 v0.81

## Existing mathematics

This successor does not claim novelty for:

- binomial logistic likelihood or Bradley-Terry estimation;
- joint maximum-likelihood estimation with known experimental offsets;
- additivity of Fisher information across independent designed observations;
- potential-based reward shaping; or
- Hellinger-affinity and total-variation error bounds.

Those are standard generalized-linear-model, paired-comparison,
optimal-design, reward-shaping, and statistical-decision ingredients.

## Residual experimental question

The registered question is narrower: in the already frozen v0.80 controlled
finite-MDP channel, does respecting the known intervention algebra repair the
finite-sample cardinal-recovery failure without violating the already frozen
leakage or misspecification limits?

The contribution, if the gates pass, is an executable access-ledger result:
intervention metadata changes which observations can be pooled and therefore
changes the finite-sample feasibility boundary. It is not a new logistic MLE
theorem and cannot establish that the response model is natural.

