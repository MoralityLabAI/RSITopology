# ASMP-9 general incomplete-menu development result v0.56

## Verdict

**`candidate_general_incomplete_menu_theorem_supported`**

The finite checks support the proof architecture in
[THEOREM_DRAFT_v0_56.md](THEOREM_DRAFT_v0_56.md).  They do not prove the
arbitrary-`n` theorem and were not prospectively registered.

## Exact affine-rank checks

The deterministic-ranking choice signatures affinely span the complete
stochastic-choice ambient space in every checked universe:

| alternatives | ambient dimension | ranking affine rank |
|---:|---:|---:|
| 3 | 5 | 5 |
| 4 | 17 | 17 |
| 5 | 49 | 49 |

This is the finite implementation check for the classical full-dimensionality
ingredient.

## Complete small-domain checks

Every proper nontrivial-menu domain was enumerated for `n=3` and `n=4`,
including the empty observed domain:

| alternatives | proper domains | minimum dimension gap | maximum gap | non-RUM witness failures | preservation failures |
|---:|---:|---:|---:|---:|---:|
| 3 | 15 | 1 | 3 | 0 | 0 |
| 4 | 2,047 | 1 | 14 | 0 | 0 |

The dimension gap is:

```text
dimension(RUM completion fiber)
  - dimension(Luce completion fiber).
```

Its strict positivity is the mechanism that prevents a proper-domain
Luce-compatible dataset from identifying the complete kernel as Luce.

The constructive completion check separately confirms that every proper
domain permits a positive completion violating random-utility regularity while
leaving every observed probability unchanged.

## Interpretation

The denominator-six trichotomy in v0.55 appears to be the smallest instance of
a general access theorem:

```text
partial data may refute RUM;
unrestricted missing-menu completion prevents it from certifying RUM.
```

The useful threshold is complete nontrivial-menu access, not three-alternative
grid resolution.

## Remaining proof debt

- establish the full-dimensionality lemma for arbitrary finite `n` by a
  precise classical citation or self-contained proof;
- formalize the semialgebraic-dimension exclusion step;
- search for exact subsumption by incomplete stochastic-choice results; and
- review positivity, singleton-menu, and exceptional-domain conventions
  before registration.

## Claim boundary

This is an unregistered development result.  It is not an arbitrary-`n`
machine proof, a finite-sample result, evidence about human or model values,
or a resolution of ASMP-9.

