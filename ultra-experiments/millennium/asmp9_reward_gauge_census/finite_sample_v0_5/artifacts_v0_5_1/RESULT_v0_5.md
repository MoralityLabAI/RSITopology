# ASMP-9 finite-sample verification v0.5

**Verdict:** `finite_sample_width_and_adaptivity_theorem_implementation_verified`

## Gates

- **G0_registration_binding:** PASS
- **G1_exact_constructor:** PASS
- **G2_width_liveness:** PASS
- **G3_high_dimensional_constructor:** PASS
- **G4_noisy_calibration:** PASS
- **G5_information_phase:** PASS
- **G6_farey_adjacency:** PASS
- **G7_bound_sanity:** PASS

## Fresh exact cells

| d | B | rays | failures | max queries / bound | max width / theorem | collision below |
|---:|---:|---:|---:|---:|---:|:---:|
| 2 | 7 | 144 | 0 | 7 / 8 | 6 / 6 | True |
| 2 | 8 | 176 | 0 | 8 / 9 | 7 / 7 | True |
| 2 | 9 | 224 | 0 | 8 / 9 | 8 / 8 | True |
| 2 | 10 | 256 | 0 | 8 / 9 | 9 / 9 | True |
| 2 | 11 | 336 | 0 | 9 / 10 | 10 / 10 | True |
| 2 | 12 | 368 | 0 | 9 / 10 | 11 / 11 | True |
| 3 | 5 | 1154 | 0 | 11 / 13 | 4 / 4 | True |

## Seeded noisy calibration

| d | B | eta | trials | errors | error rate | max responses / bound |
|---:|---:|---:|---:|---:|---:|---:|
| 2 | 7 | 0.10 | 512 | 0 | 0.000000 | 651 / 744 |
| 3 | 5 | 0.25 | 512 | 0 | 0.000000 | 2772 / 3276 |
| 4 | 8 | 0.40 | 256 | 0 | 0.000000 | 37488 / 42600 |

## Interpretation

The run verifies the implementation consequences of a finite-sample
access theorem: below the exact coefficient width the stochastic
laws remain indistinguishable; at the width, adaptive Farey search
recovers the bounded primitive ray. The fresh adjacency cells also
verify the combinatorial certificate behind the nonadaptive
quadratic penalty.

The noisy cells are seeded calibration only. The written proof,
not their observed error, carries the probability guarantee.

## Claim boundary

Known independent sign-and-tie channel after shaping quotient;
not Bradley-Terry learning, behavioral IRL, discounted shaping,
human-consistency evidence, or a full ASMP-9 resolution.
