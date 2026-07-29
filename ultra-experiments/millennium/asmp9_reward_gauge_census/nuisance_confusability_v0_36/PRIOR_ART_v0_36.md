# Prior-art boundary for nuisance confusability v0.36

## Classical ingredients

The experiment does not claim novelty for confusability graphs or zero-error
decoding.

- Claude Shannon, **The Zero Error Capacity of a Noisy Channel** (1956),
  introduced the channel confusability graph and its zero-error interpretation:
  <https://doi.org/10.1109/TIT.1956.1056798>.
- Compound and arbitrarily varying channels already formalize communication
  under unknown or changing channel state. One modern general treatment is
  Loyka and Charalambous, **A General Formula for Compound Channel Capacity**:
  <https://arxiv.org/abs/1604.01434>.
- Skalse et al., **Invariance in Policy Optimisation and Partial
  Identifiability in Reward Learning**, characterize reward-learning data
  sources through invariances and downstream tasks:
  <https://arxiv.org/abs/2203.07475>.
- Skalse and Abate, **Partial Identifiability and Misspecification in Inverse
  Reinforcement Learning**, explicitly join partial identification with
  behavioral-model misspecification:
  <https://arxiv.org/abs/2411.15951>.
- Cao, Cohen, and Szpruch, **Identifiability in Inverse Reinforcement
  Learning**, give necessary and sufficient reward-reconstruction results for
  important entropy-regularized and multi-environment settings:
  <https://arxiv.org/abs/2106.03498>.

The statement that transformations preserving an interval scale are positive
affine belongs to classical representational measurement theory; see Krantz,
Luce, Suppes, and Tversky, *Foundations of Measurement*. It is not a new
ASMP-9 theorem.

## Narrow contribution

The bounded contribution is an access-ledger specialization:

1. distinguish a fixed-data-source orbit quotient from nuisance-projected
   pairwise confusability;
2. prove by a minimal monotone-threshold witness that the latter can be
   nontransitive and therefore cannot be a group-orbit relation;
3. state the exact decision-relative decoder criterion; and
4. isolate shared nuisance across interventions as a possible calibration
   resource, with nuisance reset as the matched negative control.

These facts are elementary consequences of zero-error information theory and
set-valued identification. The result is useful to ASMP-9 because it corrects
the type of object demanded by the problem statement; it is not presented as
new graph theory, coding theory, or a complete reward-identifiability result.
