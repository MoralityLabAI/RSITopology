# ASMP-8 finite Goodhart-frontier census — Result

**Verdict:** `scalar_kl_pressure_rejected_on_registered_class`

This is an exhaustive result for the registered six-outcome labelled reward class and two
optimizer paths. It is not a universal Goodhart theorem.

## Gates

- **G0_registration_binding:** PASS
- **G1_numerical_calibration:** PASS
- **G2_supnorm_positive_control:** PASS
- **G3_reference_l2_negative_control:** PASS
- **G4_optimizer_independence_falsification:** PASS
- **G5_alignment_descriptor_stress:** PASS
- **G6_complete_census:** PASS

## Primary estimand

The exhaustive census contained 15,620 normalized labelled true-reward vectors.
It found 5,300 matched-KL cells with registered sign disagreement.

The strongest witness used the same proxy, reference policy, and KL pressure for both optimizers:

- KL pressure: 0.627115814 nats
- Gibbs true-reward gain: 0.055264597
- top-spike true-reward gain: -0.482093509
- absolute difference: 0.537358107
- raw true-reward vector: `[-2.0, -2.0, -1.0, 0.0, 2.0, -2.0]`

## Controls

The pointwise-error census attained maximum regret 0.000000 against the registered 2ε bound 0.500000.
The rare-state control had reference L2 error 0.002000000 while optimized true regret was 1.000000.

## Interpretation

A scalar KL distance from the reference policy is not, by itself, an optimizer-independent state variable for true-reward change on this class. It remains a useful coordinate when paired with the reachable-set or optimizer-path geometry. Uniform pointwise proxy error supplies a positive bound; average reference-distribution error does not.

## Prohibited extrapolations

- a universal Goodhart frontier
- a theorem for reinforcement learning trajectories
- a distribution-free best-of-n KL identity
- a characterization of heavy-tail asymptotics
- ASMP-8 resolution
