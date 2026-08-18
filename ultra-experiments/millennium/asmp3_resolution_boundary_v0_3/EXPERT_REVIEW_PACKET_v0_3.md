# ASMP-3 v0.3 independent expert-review packet

## Requested reviews

The repository policy requires two independent expert checks before this
candidate can be treated as accepted. Reviewers should work from
`RELEASE_MANIFEST_v0_3.json` and record the exact manifest SHA-256 they
reviewed.

The two reviews should be independent: reviewers should submit their initial
verdicts before seeing the other review.

**Pre-review hold:** the simulated ultra review recorded in
`SIMULATED_ULTRA_REVIEW_SYNTHESIS_v0_6.md` found a material quantifier and
complete-game-specification gap. Do not solicit qualifying receipts until that
gap is repaired, this hold is removed, and the manifest is resealed.

Both teams must reproduce the end-to-end decisive argument. The declared track
records the team's primary specialty; it does not excuse that team from
answering the other section.

## Questions 1-6: complexity and game semantics

Please adjudicate:

1. Does the canonical v0.1 text actually permit the frozen message grammar used
   in the binding countermodel?
2. Does the displayed `Refute` relation have
   `r_R(T)=log2(T)` under the canonical max-min definition?
3. Is the honest advocate efficient against every legal dishonest strategy,
   including malformed formal or semantic messages?
4. Could any verifier in the frozen grammar obtain information not represented
   in the total-variation experiment?
5. Does the nonbinding synonym construction genuinely violate necessity or
   encoding invariance under the v0.1 wording?
6. Does one countermodel suffice for the registry's negative-resolution route,
   or does the top-level “broader classification program” warning require a
   replacement theorem?

The key hostile check is item 4. A valid objection must identify an allowed
message, query, random variable, or side channel omitted from the two
least-favourable transcript distributions.

## Questions 7-12: probability, noise, and lower bound

Please adjudicate:

7. Is the persistent per-atom law a complete legal correlated-noise class with
   marginal error below one half?
8. Does the first-answer aggregator establish the conjecture's displayed
   single-atom condition without assuming independence?
9. Are repeated queries informationally redundant under the frozen law?
10. Is the total variation between uniform even- and odd-parity channel outputs
   exactly `(3/5)^d`?
11. Does the variational inequality correctly convert that average-prior result
   into a worst-case impossibility for a uniform constant
   completeness-soundness gap?
12. Are atom description length, locality, and evaluation cost small enough to
   avoid hiding the full answer in one query?

The key hostile check is item 11. A valid objection should exhibit a decision
rule whose pointwise gap evades the least-favourable-prior bound or identify a
world-dependent message omitted from the distributions.

## Required response fields

Use `expert_review.schema.json`. Each review must include:

- reviewer identity and relevant expertise;
- conflict-of-interest declaration;
- reviewed release-manifest SHA-256;
- answers to all twelve questions;
- one of `accept`, `accept_with_nonmaterial_corrections`, `major_revision`, or
  `reject`;
- any counterexample or proof gap with exact file/line references;
- permission status for storing the review in this repository; and
- an `independent_checker` record. At least one of the two teams must implement
  and pass a checker independently of the supplied producer and verifiers,
  store that artifact below `reviews/checkers/`, and bind its SHA-256 in the
  receipt. A team not supplying the checker records `implemented_by_review_team`
  as false and `result` as `not_run`.

Two `accept` or `accept_with_nonmaterial_corrections` verdicts on the same
manifest are required, and all twelve questions must be answered `yes` by each
team.
Corrections that change the message grammar, `Refute` relation, noise law,
asymptotic quantifiers, or theorem conclusion are material and require a new
release manifest plus fresh reviews.

The completion validator additionally requires at least one qualifying review
team's independently implemented checker to pass. Merely rerunning
`verify_result.py` or `verify_fourier_certificate.py` does not satisfy that
condition.
