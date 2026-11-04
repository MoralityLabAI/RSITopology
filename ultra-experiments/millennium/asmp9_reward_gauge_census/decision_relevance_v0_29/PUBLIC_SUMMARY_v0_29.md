# When a reward quotient is sufficient for a policy decision

## Result

Version v0.29 closes the decision-relevance handoff left open by the calibrated
occupancy result v0.28.

### 1. A reward gauge must be null on policy differences

Suppose a finite policy family has feature occupancies `mu_pi` and reward is
known only modulo a declared linear subspace `G`. Quotient-level policy claims
are well-posed exactly when:

```text
g^T(mu_pi-mu_pi') = 0
```

for every `g in G` and every registered policy pair. If this fails, changing
only the declared gauge representative can change the policy ranking. The
registered invalid-gauge control therefore returned unavailable rather than a
misleading numeric certificate.

### 2. Quotient error gives an exact regret bound

Let:

```text
delta = inf_(g in G) ||r_hat-r-g||_2.
```

For the policy selected by `r_hat`:

```text
Regret
  <= delta ||mu_opt-mu_selected||_2
  <= delta D,
```

where `D` is the largest occupancy distance in the registered policy family.
The fresh nonzero-regret cell had:

```text
observed regret                 8
quotient error squared          25/8
selected occupancy distance^2   32
bound squared                 100
```

The separate sharpness cell attained equality:

```text
regret                         22/13
regret squared                484/169
bound squared                 484/169
```

### 3. A strict margin can certify the selected policy

An estimated policy is also uniquely optimal under the true reward if every
estimated margin is strictly larger than quotient uncertainty in that policy
difference direction.

The strict-margin cell passed. A matched equality case was correctly
inconclusive. This makes the strict inequality operational rather than a
post-hoc convention.

### 4. Measurement geometry composes with decision geometry

Version v0.28 bounded quotient reward error by:

```text
||e||_2 / sigma_min(XU).
```

Version v0.29 composes it with the policy result:

```text
Regret
  <= D ||e||_2 / sigma_min(XU).
```

The registered composition cell had nonzero regret `8` and a valid predicted
squared bound of `100`. The three factors have different meanings:

```text
localized error       -> measurement quality
sigma_min(XU)         -> access conditioning
D                      -> downstream policy sensitivity
```

### 5. Positive scale depends on the target

Both registered positive rescalings selected the same optimal policy. Yet a
fixed policy's regret changed from `6/5` to `14`, crossing the registered
fixed-unit threshold `4`.

Positive scale can therefore be quotientable for fixed-MDP policy identity
while remaining essential for a cardinal regret statement.

## Registered verification

The exact-rational CPU run passed all ten gates. The import-independent
verifier reimplemented the finite arithmetic and passed all nineteen checks.

```text
implementation commit      c54dde192b432b32feb41625a2db16f073e392b7
registration commit        283c3420d940dcd1f8cf39df75a664d51555ce2c
registration SHA-256       a2fe94f2be38ce9e4681de7a8466511172b5845dd408560db798b1901dc244f7
runtime                     0.048 seconds
peak resident memory        20,234,240 bytes
GPU                         none
```

## Prior-art and novelty boundary

The mathematical ingredients belong to apprenticeship learning,
downstream-task reward invariance, inverse-reward identifiability, robust
optimization, and finite-sample IRL. Version v0.29 is a scoped consolidation
and executable decision ledger; no novelty is claimed for those ingredients.

The result does not establish that the learned reward is correct, that a safe
policy exists in the finite family, that reward regret is a complete safety
metric, that real demonstrators obey the v0.28 access model, or that ASMP-9 is
resolved.
