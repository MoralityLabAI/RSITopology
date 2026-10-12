# ASMP-8 v0.4 prior-art boundary

The mathematical ingredients remain classical.

- Hoeffding (1963), *Probability Inequalities for Sums of Bounded Random
  Variables*, <https://doi.org/10.1080/01621459.1963.10500830>, supplies the
  fixed-checkpoint bounded-variable bounds.
- A finite union bound allocates the registered familywise error across norm
  and checkpoint pairs. This is not claimed to be an optimal time-uniform
  confidence sequence.
- The dual lower margin is the classical support-function result validated in
  ASMP-8 v0.2.

The experiment-specific contribution is the non-reverting hitting-time
instrument: a monotone envelope over prospectively fixed audit checkpoints,
paired with an exact oracle-limit classification and optimizer-path census.
No novelty is claimed for the constituent inequalities.
