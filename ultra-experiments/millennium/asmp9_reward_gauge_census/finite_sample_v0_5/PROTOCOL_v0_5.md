# ASMP-9 finite-sample sign-and-tie verification protocol v0.5

## Status

Prospective verification protocol. The development cells `d=2,B=1..6`,
`d=3,B=3..4`, and Farey adjacency bounds `B=3..32` are burned and excluded
from the confirmatory grid.

## Frozen response model

For a primitive bounded reward ray `z` and an integer comparison `q`, let:

```text
S = sign(q dot z).
```

At known `0<=eta<1/2`, one response is conditionally independent with:

```text
P(Y=1 | S=+1) = 1-eta,
P(Y=1 | S= 0) = 1/2,
P(Y=1 | S=-1) = eta.
```

The exact tie law is a model assumption. It is not a model of human
incomparability.

## Frozen theorem claims

1. **Width liveness.** Finite-sample identification is possible exactly at:

   ```text
   W*(B)=1 for B<=2, and B-1 for B>=3.
   ```

   Below this width, an indistinguishable witness pair has identical complete
   response laws.

2. **Constructive upper bound.** Adaptive coordinate/Farey search uses at most:

   ```text
   K(d,B)=d+(d-1)(2+ceil(log2 |F_max(1,B-1)|))
   ```

   logical comparisons. Repeating each:

   ```text
   n=ceil(8 ln(2K/alpha)/(1-2eta)^2)
   ```

   times gives worst-case error at most `alpha`.

3. **Capacity lower bound.** A fixed-budget adaptive estimator needs at least:

   ```text
   ((1-alpha)log2 |P(d,B)| - h2(alpha))
   /(1-h2(eta))
   ```

   samples.

4. **Nonadaptive critical-width penalty.** In the two-dimensional Farey
   subfamily, every nonadaptive design at width `B-1` needs:

   ```text
   (|F_B|-1) ln(1/(4alpha))
   /(2 D_tie(eta))
   ```

   responses for `0<eta<1/2` and `0<alpha<1/4`.

The written proof carries these claims. The run checks the constructor,
finite-registry consequences, and extremal combinatorics.

## Fresh grid

### Exact every-ray constructor

- `d=2`, `B=7..12`;
- `d=3`, `B=5`.

Every ray must be reconstructed at width `W*(B)`. The registered lower witness
must remain indistinguishable at width `W*(B)-1`.

### Seeded high-dimensional constructor

- `(d=4,B=8,n=2048,seed=95041)`;
- `(d=8,B=16,n=2048,seed=95042)`;
- `(d=16,B=32,n=2048,seed=95043)`.

### Seeded noisy calibration

- `(d=2,B=7,eta=0.10,alpha=0.01,n=512,seed=95101)`;
- `(d=3,B=5,eta=0.25,alpha=0.01,n=512,seed=95102)`;
- `(d=4,B=8,eta=0.40,alpha=0.01,n=256,seed=95103)`.

Observed error must not exceed the registered `alpha`, response counts must not
exceed the constructive upper bound, and no query may exceed `W*(B)`. This is a
seeded implementation calibration, not a proof of coverage.

### Information-design phase check

At `d=2`, `B in {7,8}`, and `eta in {0.10,0.25}`, the minimum pairwise
Bhattacharyya information must be zero at `W*(B)-1` and strictly positive at
`W*(B)`.

### Fresh nonadaptive certificate

For every `B=33..64`, exact enumeration must verify that each adjacent
`F_B` pair is separated only by admissible endpoint thresholds and that every
threshold is incident to at most two adjacent pairs.

## Gates

- **G0:** registration, implementation commit, clean tree, and all sealed
  hashes agree;
- **G1:** every fresh exact ray is reconstructed;
- **G2:** all exact queries obey `W*(B)` and every lower witness collides below
  it;
- **G3:** every seeded high-dimensional ray is reconstructed within width;
- **G4:** every noisy calibration cell respects its frozen error and resource
  bounds;
- **G5:** every information-design cell changes from zero to positive at the
  theorem width;
- **G6:** every fresh Farey adjacency certificate is valid;
- **G7:** capacity, Fano, and nonadaptive bounds are finite and ordered on all
  applicable cells.

All gates passing yields:

```text
finite_sample_width_and_adaptivity_theorem_implementation_verified.
```

## Pre-registration tests

```powershell
python -m pytest -q `
  ultra-experiments/millennium/asmp9_reward_gauge_census/finite_sample_v0_5
```

Expected at freeze: `82 passed`.

## Claim boundary

This is a finite, known, conditionally independent response model after
potential shaping is already quotiented. It does not establish Bradley-Terry
reward recovery, infer reward from policies, handle discounted shaping,
validate a model of human judgment, or resolve ASMP-9.

## Resources

CPU only; 4 GiB RAM; 10 minutes; no GPU.
