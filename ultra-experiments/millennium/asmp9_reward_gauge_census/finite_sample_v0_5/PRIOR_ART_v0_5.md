# Finite-sample reward-ray access: prior-art boundary

## Disposition

The proposed v0.5 theorem is an elementary specialization of established
noisy-search and information-theoretic results to the bounded reward-ray access
grammar developed in ASMP-9. Novelty is not claimed.

## Primary adjacent results

- Shannon's channel-coding theorem supplies the binary-symmetric-channel
  capacity `1-h2(eta)` and the fact that noiseless feedback does not increase
  memoryless-channel capacity.
- Horstein's sequential transmission scheme and later posterior-matching work
  connect adaptive noisy binary search with feedback communication.
- Nowak, *The Geometry of Generalized Binary Search* (2009), develops
  noise-tolerant generalized binary search and conditions for logarithmic
  hypothesis identification.
- Dereniowski, Lukaszewicz, and Uznanski, *Noisy searching: simple, fast and
  correct* (2021), give near-capacity query bounds for noisy search.
- Chen et al., *Human-in-the-loop: Provably Efficient Preference-based
  Reinforcement Learning with General Function Approximation* (ICML 2022),
  establish preference-based RL guarantees with trajectory feedback.
- Saha, Pacchiano, and Lee, *Dueling RL: Reinforcement Learning with Trajectory
  Preferences* (AISTATS 2023), study trajectory-preference RL under generalized
  linear preference models.
- Schlaginhaufen, Ouhamma, and Kamgarpour, *Efficient Preference-Based
  Reinforcement Learning: Randomized Exploration Meets Experimental Design*
  (2025), explicitly connects trajectory-query selection with experimental
  design.
- Drago et al., *Generalizing Preference-based Reinforcement Learning: a
  Rationality Model for Incomparability* (2026), model a third semantic
  response category. Their incomparability label is not the fair binary
  response at exact equality used here.

Primary links:

- <https://doi.org/10.1109/TIT.1963.1057832>
- <https://arxiv.org/abs/0910.4397>
- <https://arxiv.org/abs/2107.05753>
- <https://proceedings.mlr.press/v162/chen22ag.html>
- <https://proceedings.mlr.press/v206/saha23a.html>
- <https://arxiv.org/abs/2506.09508>
- <https://arxiv.org/abs/2607.11432>

## Residual contribution

The only proposed contribution is the composition:

1. the exact ASMP-9 coefficient-width threshold;
2. a scale-invariant stochastic sign-and-tie response channel;
3. a constructive Farey ratio search at that same sharp width; and
4. matching-order finite-sample upper and information lower bounds.

The access threshold is the relevant distinction. Below it, no number of noisy
responses helps because the response laws are identical. At it, finite
identification becomes possible and has the expected noisy-search scaling.

## Deliberate omissions

- The response model is known and correctly specified.
- Ties are latent reward equalities, not human incomparability judgments.
- Samples are conditionally independent.
- Potential shaping has already been quotiented in cycle coordinates.
- Positive scale is removed by the sign-only channel.
- No policy or demonstration distribution is observed.
- No discounted shaping operator is present.

Those omissions are remaining ASMP-9 obligations, not details to be silently
folded into this theorem.
