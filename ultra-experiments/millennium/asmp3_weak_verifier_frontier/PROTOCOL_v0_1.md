# ASMP-3 exact correlated-noise weak-verifier protocol v0.1

## Question

After an honest challenger has located a semantic atom whose truth decides a
formal refutation, when does repeated weak verification make the atom reliable
enough to support a decision, and when does correlation defeat amplification?

This is a semantic-adjudication subgame. It assumes the refuting atom and its
formal dependency path have already been located. It does not test adversarial
refutation search or transcript obfuscation.

## Registered finite model

The correct semantic answer is one bit. Each query returns that bit XOR an
error bit. The marginal error is fixed at `mu=1/5`. The verifier makes an odd
number of queries `q in {1,3,5,7,9}` and uses strict majority.

Queries are divided as evenly as possible among `g` independent verifier
families, where `g` is one, `min(3,q)`, or `q`. Within a family, error bits are
exchangeable under a beta-binomial law with intraclass correlation
`rho in {0,1/100,1/50,1/20,1/10,1/5,1/3,1/2}`. Distinct families are
independent. `rho=0` is the exact independent-binomial limit.

For each cell compute exactly, using rational arithmetic:

```text
FN(q,g,rho) = P(majority reports valid | the atom is invalid)
FP(q,g,rho) = P(majority reports invalid | the atom is valid)
Gap(q,g,rho) = 1 - FN - FP.
```

The symmetric flip model implies `FN=FP`, but both fields must be emitted and
gated separately. A cell is operationally admissible only when both are at most
`1/20`.

## Counterexample laws

1. **Global flip:** with probability `1/5`, all queries flip. Replication must
   leave both errors at `1/5` for every odd `q`.
2. **Atom-targeted average-error law:** on a universe of `N` semantic atoms, one
   registered atom is always answered incorrectly and every other atom
   correctly. For `N in {16,64,256,1024}`, atom-averaged error is at most
   `1/16 < 1/5`, yet a false transcript whose canonical refutation uses that
   atom is accepted with probability one. This law is outside the per-atom
   beta-binomial positive model and proves why an unconditional atom-average
   bound cannot support the positive claim.

## Frozen gates

- **E0 exactness:** every rational probability vector sums exactly to one;
  emitted `FP` and `FN` agree exactly in the symmetric model.
- **I0 independent liveness:** at `q=9`, independent majority error is strictly
  below `1/20`.
- **C0 correlation boundary:** at `q=9,g=1`, `rho=1/20` is admissible and
  `rho=1/10` is not.
- **D0 diversity recovery:** at `q=9,rho=1/5`, one family is inadmissible while
  three and nine independent families are admissible.
- **G0 global-correlation kill:** the global-flip law has `FP=FN=1/5` at
  `q=1,3,5,7,9`.
- **M0 marginal-bound kill:** every registered targeted law respects the
  atom-average `1/5` ceiling but has worst-case false acceptance one.
- **S0 separate-error rule:** no cell may be labelled admissible from the
  derived gap unless both individual error gates pass.

Any failed implementation gate yields `invalid_instrument`. If exactness and
controls pass but a scientific directional gate fails, report the failed gate
without threshold amendment.

## Evidence and claim boundary

The evidence is exact for this finite rational model. It does not establish
that human or model-judge errors are beta-binomial, that verifier families are
independent, that an honest challenger can locate a refutation, or that a weak
verifier can judge superhuman work. No real-model outcome or semantic content
is used.

