# ASMP-11 v0.2 covering-frontier prior art

The combinatorial object in this successor is classical. An `(n,s,k)` covering
design is a family of `s`-subsets whose blocks contain every `k`-subset, and
`C(n,s,k)` denotes the minimum family size. Gordon, Kuperberg, and Patashnik's
covering-design work and the La Jolla Covering Repository provide the direct
design-theory baseline. The elementary ratio bound and the recursive
Schoenheim bound are classical; solver recovery of their small instances is
not a novelty claim.

The access interpretation remains below several established literatures:

- Angluin et al.'s value-injection query model formalizes interventions on
  circuit wires and provides topology-dependent learning algorithms and lower
  bounds.
- Statistical-query and noisy-parity/LPN work explains why sampled parity is a
  nontrivial observation problem, but supplies no automatic efficiency result
  for the parent-fixing grammar used here.
- Classical adaptive group testing studies stronger intersection feedback and
  typically aims to identify the hidden set. This experiment asks only for
  worst-case clean-versus-planted detection under a containment response.
- Existing cryptographic and statistical white-box-undetectability results are
  much stronger negative baselines than this transparent finite mechanism.

The bounded contribution is the access-class translation: along the clean
all-negative transcript, every uniformly sound detector's intervention blocks
must cover every planted support. Therefore the worst-case population query
cost equals a covering number. The finite census and sample-cost crossover are
specializations of that lemma, not new covering-design theory.
