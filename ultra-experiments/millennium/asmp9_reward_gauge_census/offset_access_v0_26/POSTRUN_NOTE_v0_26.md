# ASMP-9 v0.26 post-run note

## Frozen verdict

```text
offset_access_boundary_not_established_v0_26
```

The verdict is binding.

Ten of eleven registered gates passed. Every mathematical and resource gate
passed:

- 3,718 fresh exact population gaps met the registered error and query bounds;
- both dyadic upper bounds equalled their metric-entropy lower bounds
  (`70=70` and `81=81`);
- both restricted-offset cells produced exact indistinguishable transcripts
  with positive minimax-error lower bounds;
- all 10,800 deterministic bounded-probability-error paths were
  `eta`-accurate;
- the flat-link sequence decreased below its frozen endpoint;
- the inherited no-offset non-affine control reproduced; and
- both Hoeffding certificates cleared their declared failure probabilities.

Gate `G9_prior_art_and_claim_boundary` failed for a mechanical exact-substring
reason:

```text
runner expected: "choice-indifference"
sealed audit had: "Choice indifference"

runner expected: "no novelty claim"
sealed audit had: "not a novelty claim"
```

The structured allowed and forbidden claim lists matched exactly, the
known-reward-unit access phrase was present, and the prior-art audit contained
the intended substantive statements. Nevertheless the frozen Boolean gate was
false, so v0.26 cannot be reported as established.

The independent verifier reproduced every mathematical row and hash. It also
correctly returned failure because the registered all-gates verdict did not
hold.

## Artifact hashes

```text
result_v0_26.json
  e21ee3222858f31356ba2c3c0676f3afaea97f3aea607d51895c4039a418c15a

run_receipt_v0_26.json
  d18645a03628327dc460023e5e5b285408b14d9a64edda2c4a325a3367a23d3f

independent_verification_v0_26.json
  9e2f8589d020052e1de2a57e4ab760ec03c05272d1d715b91bd8e143a9d05d8d
```

## Repair policy

The sealed v0.26 files and verdict will not be edited.

A versioned v0.26.1 repair may consume the immutable v0.26 result and receipt,
replace only the brittle prose-substring test with a structural prior-art and
claim-boundary check, and independently verify the derived adjudication. It
must state that it is a mechanical re-adjudication over prospectively generated
v0.26 scientific data, not a new fresh scientific run.
