# ASMP-3 correlated path-risk theorem v2.13

## Scope

This result refines the noise boundary of the v2.10 one-shot online extractor.
It keeps the six-clause trace and revalidation contract of v2.10 unchanged.  The
new observation is that its proof does not require independent semantic-oracle
errors.  It requires only a bound on the probability that at least one error
occurs along the adaptive path actually selected by the verifier.

This is a theorem for the repaired online ASMP-3 subclass.  It is not a
classification of every protocol permitted by the literal v0.1 wording.

## General path-risk law

Let:

- `s` be the soundness upper bound of the claimed noisy-oracle strategy;
- `E_path` be the event that a semantic-oracle error occurs on at least one
  query on the verifier's actually selected adaptive path; and
- `delta_path = Pr(E_path)` under the joint law of the instance, public coins,
  private coins, and noise.

The v2.10 extractor runs the claimed strategy once, reads the bound trace,
selects its candidate, and revalidates that candidate against `H`.  It neither
restarts nor replays the strategy.  On the event that the claimed strategy
succeeds and `E_path` does not occur, the six-clause contract makes the selected
candidate a valid witness.  Hence the union bound gives

```text
Pr[valid extracted witness] >= max(0, 1 - s - delta_path).
```

No independence assumption is used in this implication.  Dependence matters
only when one tries to derive a usable upper bound on `delta_path`.

## Three admissible dependent-noise controllers

### Persistent truth-independent common-mode flip

Let one bit `Z ~ Bernoulli(eta)`, independent of the semantic truth and of path
selection, flip every semantic answer on the run.  For every nonempty path,

```text
delta_path = eta.
```

Repeated copies do not reduce this error; that preserves the v1.8
non-amplification result.  But non-amplification is not non-extractability.  The
online finder still has lower bound `max(0, 1 - s - eta)`, which is positive
whenever `s + eta < 1`.  Useless replication can be removed, so a `q`-query
verifier uses `q` raw semantic queries in this controller.

### Per-matching-prefix conditional control

For an adaptive path of length `q`, suppose that after every error-free matching
prefix the next selected answer is wrong with conditional probability at most
`e_i`.  The chain rule, without independence, gives

```text
Pr[no selected-path error] >= product_i (1 - e_i),
delta_path <= 1 - product_i (1 - e_i).
```

The condition is explicitly on the selected query after the realized matching
prefix; fixed-query marginal bounds are not a substitute for it.

### Exchangeable latent-rate mixture

Let a latent error rate `P` be drawn once and make the selected answers
conditionally iid given `P`.  For a path of length `q`,

```text
delta_path = 1 - E[(1 - P)^q]
           <= 1 - (1 - E[P])^q.
```

The inequality is Jensen's inequality because `p -> (1-p)^q` is convex on
`[0,1]` for integer `q >= 1`.  The harness checks 18,012 rational mixture/query
cases, including 10,296 held-out denominator-9 and denominator-10 cases, with
zero violations.

## Marginal firewall

Fixed-class marginal error bounds alone do not control the selected path.  For
`N >= 2`, draw a public seed `J` uniformly from `N` semantic classes, make class
`J` the unique bad class, and let the verifier query class `J`.  Then every
fixed class has marginal error `1/N`, while the actually selected one-query path
errs with probability one.

This counterexample deliberately permits the noise state to correlate with the
public verifier seed.  It therefore does not contradict noise models that
declare independence from public coins.  It proves that the joint law—or an
equivalent selected-path condition—must be stated; fixed marginals do not state
enough.

## Corrected boundary

The repaired online theorem covers arbitrary dependence structures for which
`delta_path` is controlled.  Registered examples now include the persistent
common-mode, matching-prefix conditional, and exchangeable-mixture controllers
above.  The theorem does not cover a marginal-only model with adversarial
selection, and it does not claim that repetition amplifies common-mode noise.

Thus v2.12's practical boundary should be read as **controlled selected-path
risk**, not as **fresh conditional noise only**.  The stronger reading resolves
the correlated-noise block while preserving the explicit firewall where no
path-risk bound follows.

## Machine-checked evidence

The producer and clean-room checker independently reconstruct:

- 24 common-mode rows over four error rates and six query depths;
- 20 matching-prefix conditional-chain rows;
- 18,012 exact rational exchangeable-mixture/query cases;
- 20 same-marginal controller comparisons;
- 31 public-seed selection counterexamples for `N = 2,...,32`;
- all 12 v2.10 online composition rows under persistent common-mode noise; and
- the v1.8 persistent-error samples at depths `1, 3, 9, 17, 33, 64`.

Every calculation uses exact rational arithmetic.  The independent checker does
not import the producer.
