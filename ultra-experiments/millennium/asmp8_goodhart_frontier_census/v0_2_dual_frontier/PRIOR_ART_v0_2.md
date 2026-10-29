# ASMP-8 v0.2 prior-art audit

## Verdict before registration

The central identity in this seed is classical convex duality, not a novel
Goodhart theorem. For a finite reference law `p0`, policy `pi`, proxy reward
`y`, and true-reward error `e = r - y`, the error contribution to policy gain
is a linear functional of `e`. Its minimum over a norm ball is the negative
support function of that ball, hence the corresponding dual norm.

The candidate contribution is an exact, registered specialization of this
classical fact to the finite Goodhart registry that already rejected scalar KL
pressure, plus sharpness and coordinate-minimality witnesses. It is an
instrument result, not new convex analysis.

## Primary anchors

- Ben-Tal and Nemirovski, **Robust Solutions of Uncertain Linear Programs**
  (1999), develops robust counterparts for linear optimization under declared
  uncertainty sets: <https://doi.org/10.1016/S0167-6377(99)00016-4>.
- Iyengar, **Robust Dynamic Programming** (2005), and Nilim and El Ghaoui,
  **Robust Control of Markov Decision Processes with Uncertain Transition
  Matrices** (2005), place uncertainty-set duality in sequential decision
  problems: <https://doi.org/10.1287/moor.1040.0129> and
  <https://people.eecs.berkeley.edu/~elghaoui/pubs_rob_mdp.html>.
- Skalse et al., **Defining and Characterizing Reward Hacking** (NeurIPS 2022),
  formalizes unhackability and shows how restrictive it is over stochastic
  policies: <https://arxiv.org/abs/2209.13085>.
- Gao, Schulman, and Hilton, **Scaling Laws for Reward Model
  Overoptimization** (ICML 2023), empirically finds optimizer-dependent
  overoptimization curves for RL and best-of-n, directly motivating the v0.1
  test of optimizer-independent scalar pressure:
  <https://proceedings.mlr.press/v202/gao23h.html>.

## Precise placement

This seed does not contradict unhackability impossibility results. It assumes a
declared norm-bounded uncertainty set for proxy error and asks for a worst-case
certificate within that set. It does not derive the uncertainty radius from
data.

It also does not claim that dual-norm movement is the unique empirical notion
of optimization pressure. The two coordinates have operational meaning only
relative to a frozen error norm:

- proxy gain states what the optimizer appears to gain;
- dual movement states how strongly policy reweighting can couple to admissible
  proxy error.

The v0.2 result may establish exact sufficiency and sharpness for that robust
finite problem. It cannot establish an RL training law, heavy-tail scaling,
reward-model calibration, or a universal Goodhart frontier.

