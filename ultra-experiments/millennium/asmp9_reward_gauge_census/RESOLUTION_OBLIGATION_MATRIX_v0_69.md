# ASMP-9 resolution-obligation matrix after v0.69 development

## Verdict

**ASMP-9 remains unresolved.**

Version v0.69 closes one finite linear compositional gap left explicit after
v0.68.1: it combines licensed reward-gauge directions, physical measurement
nuisance, and a linear query/intervention channel in one exact quotient.
The result is classical quotient linear algebra packaged as an ASMP-9
admission theorem; it is development-only and not claim-eligible.

## Status against the five obligations

| Obligation | Strongest evidence after v0.69 | Status | Missing resolution evidence |
|---|---|---|---|
| 1. Maximal invariance or identifiability object | For finite linear channels, `K=A^(-1)(N+A(G))` exactly characterizes the maximal reward object `R/K`; the intended quotient `R/G` is identified exactly when `K=G` | **Exact in the joint finite linear grammar; open broadly** | Nonlinear, stochastic, context-varying, history-sensitive, strategic, relational, and non-scalar joint quotients |
| 2. Necessary and sufficient access | Exact kernel/rank/row-span criterion for any declared linear query/intervention dictionary | **Exact in the joint finite linear grammar** | Physical validation, adaptive nonlinear access, unknown channel classes, and access that changes the target |
| 3. Sharp query, sample, and intervention bounds | Effective output dimension at least `dim(R/G)` is necessary and sharp; `1/sigma_min` is the sharp deterministic inverse constant | **Noiseless dimension and deterministic conditioning closed locally; stochastic complexity open** | Joint minimax sampling, adaptive allocation, dependence, computation, and lower bounds for the physical stochastic channel |
| 4. Robustness to misspecification | Residual nuisance enters through its projection onto the admitted quotient and is amplified by exactly `1/sigma_min` | **Deterministic norm bound only** | A physically justified misspecification radius, nonlinear remainder, drift, correlated/adaptive corruption, and held-out confirmation |
| 5. No-go without a coherent latent value object | Every `h in K\\G` is an exact non-gauge indistinguishability witness; representative leakage is separated from reward-orbit information | **Exact linear no-go; general replacement classification open** | A class-level theorem selecting relation-, kernel-, set-, or path-valued targets for incoherent demonstrators |

## What v0.69 adds

### One joint object

```text
reward space R
licensed gauge G
measurement A
physical nuisance N

J = N + A(G)
K = A^(-1)(J).
```

The admitted measurement identifies exactly `R/K`. It identifies the intended
reward quotient exactly when `K=G`.

### Two distinct failure modes

1. **Extra blindness:** `K` strictly contains `G`, so the verifier emits an
   exact non-gauge witness.
2. **Gauge leakage:** `A(G)` is not contained in `N`, so raw measurements
   reveal the selected representative. The representative-insensitive
   analysis must quotient this image rather than count it as value evidence.

### Sharp deterministic stability

After orthogonal gauge fixing and nuisance projection, the smallest singular
value of the effective map gives the exact inverse Lipschitz constant.
Zero singular value is not merely poor conditioning; it is the non-gauge
kernel obstruction.

## Remaining load-bearing sequence

### A. Bind the theorem to a physical stochastic channel

The v0.68.1 construction passed on one finite response registry. A successor
must prospectively define the reward-gauge directions `G`, measurement map
or local linearization `A`, and nuisance class `N`, then test whether the
empirical kernel contains directions beyond `G` on untouched data.

### B. Joint stochastic policy complexity

Replace the deterministic norm ball by a declared response law and derive
matching query/sample lower and upper bounds that include quotient dimension,
conditioning, context frequency, dependence, and policy margin.

### C. General replacement-object classification

When scalar reward quotient identification fails for reasons not representable
as a linear kernel, classify when the identifiable target should instead be a
preference relation, stochastic choice kernel, admissible set, or path-valued
process.

## Claim boundary

Version v0.69 does not show that any physical reward transformation is
licensed, that the model response score is a reward, that the linearization is
valid outside its registered radius, that humans or models possess a scalar
value object, or that ASMP-9 is resolved.
