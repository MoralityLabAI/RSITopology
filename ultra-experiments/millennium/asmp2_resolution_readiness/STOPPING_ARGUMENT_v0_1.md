# ASMP-2 v0.1 resolution-readiness stopping argument

## Decision

**Stop the full-resolution attempt for `ASMP-CANDIDATE-SET-v0.1` as
currently written. ASMP-2 is not resolved.**

This is a definition-readiness stop, not a claim that the research program is
hopeless. The repository's own authoritative status, a formal-slot audit, and
an exact smooth countermodel agree on the same conclusion: v0.1 does not bind
one closed theorem whose five obligations can be proved or refuted.

## 1. The problem's own resolution policy blocks a full-resolution claim

The authoritative registry says:

- the set status is `proposed_candidate_definition_draft`;
- `graduation_standard_satisfied` is `false`;
- the machine-readable registry is not normative;
- an exact problem version is required;
- a narrow subclass does not count as a full resolution; and
- empirical resolution is forbidden for ASMP-2.

The hostile referee audit is more specific: ASMP-2's “global class [is] still
conditional,” and external review must still decide whether its quotient and
conditioning modulus are the right ones. The main statement asks the reader to
start with “a registered class” and “registered source sample sizes,” but v0.1
contains no registration object or schema binding them.

The harness records fifteen load-bearing unbound slots:

1. model-class registration;
2. common parameterization and tangent transport;
3. nuisance spaces and trajectories;
4. support/overlap constants;
5. curvature and remainder constants;
6. deployment set and metric;
7. source environments and sample allocation;
8. policy or monitor class;
9. regular local-certificate definition;
10. minimax radius and loss;
11. conditioning norm and margin;
12. simultaneous-confidence regime;
13. active-design action space;
14. active-design cost and budget; and
15. active-design objective and tie rule.

These are not cosmetic omissions. Changing any of them changes the theorem,
the minimax rate, or the optimal design. The v0.1 acceptance policy itself says
that changing such assumptions creates a new problem version.

## 2. Exact countermodel to a qualitative local-to-global reading

Let `theta` range over the compact connected interval `[-1,1]`, with source
environments

```text
F = {-1/2, 0, 1/2}.
```

For worlds `s in {-1,+1}`, observe independent Bernoulli variables `Z,Y` with

```text
P(Z=1) = 1/2 + theta/8,

g(theta) = (16/9) theta^2 (theta^2 - 1/4)^2,

P_s(Y=1) = 1/2 + theta/16 + s g(theta)/8.
```

Use safety loss `L_s(theta)=P_s(Y=1)`, constant acting utility `U=1`, utility
floor `u_0=4/5`, safety threshold `epsilon=9/16`, and the singleton admissible
policy class `{act}`.

This family satisfies all of the following exactly:

- `g=g'=0` at every source, so the worlds have identical source laws and
  identical first derivatives;
- the `Z` channel identifies the one-dimensional deployment tangent;
- at the reference point `theta=0`, total Fisher information is `5/64>0`;
- the nonzero risk derivative `1/16` factors through the `Z` score with factor
  `1/2`;
- all observation probabilities are bounded away from zero and one, so these
  polynomial finite-alphabet families are dominated and QMD with common full
  support;
- `0<=g<=1` on the compact domain;
- both worlds obey the common finite risk-curvature bound `193/36`; and
- utility is non-inert and exceeds the frozen floor.

Nevertheless, at the unsampled deployment point `theta=1`,

```text
L_-(1) = 7/16 < 9/16 < 11/16 = L_+(1).
```

The exact global ambiguity is `1/4`. Thus compactness, connected topology,
common support, smooth QMD regularity, finite curvature, full local shift
information, first-order functional factorization, and a positive utility
floor do not by themselves imply global certification.

Because the source laws are identical, this conclusion is independent of the
finite source sample sizes. Because the only admissible policy is unsafe in
the `+` world at `theta=1`, the infimum over the two registered worlds in the
v0.1 certification goal is exactly zero for every source-only procedure.

### General finite-source bump lemma

The example is not an accident of the three selected points. Let `F` be any
finite subset of a nondegenerate compact interval and define

```text
q(theta) = product over x in F of (theta-x)^2.
```

The continuous nonnegative polynomial `q` has a positive maximum on the
interval. Normalize by that maximum to obtain `g`. Then `0<=g<=1`, while
`g(x)=g'(x)=0` for every `x in F`, and `g(theta*)=1` at some unsampled
maximizer. Adding a small common linear Bernoulli channel supplies positive
Fisher information for the entire one-dimensional tangent. Adding
`+/- a g(theta)` to a second Bernoulli risk channel leaves every finite source
law and source score unchanged but separates the two risks at `theta*`.
Choosing the linear and bump amplitudes small enough keeps all probabilities
uniformly inside `(0,1)`; polynomiality supplies QMD and a finite common
curvature bound. A singleton acting policy supplies any fixed utility floor
below one.

Therefore no number of samples at a fixed finite source set can uniformly
certify an unrestricted smooth QMD continuation class. A positive theorem must
restrict the continuation class or bind a quantitative covering/margin rule;
the current v0.1 prose does neither.

This is stronger than the existing crossed-shift fixture in one useful sense:
the hidden term and its derivative vanish at three sources in a connected
one-dimensional family while an independent channel keeps the entire local
shift tangent identifiable. It still does not refute a quantitatively frozen
continuation theorem; rather, it proves why such a theorem must bind coverage,
margin, curvature/remainder, and model-class structure jointly.

## 3. Why more finite census work is not the next rational step

The existing repository evidence already supplies:

- one exact forced counterexample showing local tangent span need not continue
  globally; and
- an exhaustive census over 65,536 source subsets showing that one registered
  myopic active selector fails its support gate in all three deployment
  families.

The new harness closes the remaining meta-question: neither result can be
promoted to a resolution because there is no frozen universal active-design
objective or global continuation class to which it could generalize. Another
finite selector, grid, or polynomial degree would add a restricted example
without discharging the definition debt.

## 4. Exact condition for resuming

Resume a full-resolution attempt only after a successor ASMP-2 version binds
the fifteen slots above and replaces “asks for necessary and sufficient
conditions” with a typed proposition or classification over a declared class.
At minimum, the successor must make the following mechanically decidable from
its statement:

- what counts as a regular local certificate and its radius;
- which norms define the quotient conditioning margin;
- which quantitative hypotheses permit continuation;
- what sample-complexity variables are optimized;
- what actions, costs, budgets, and loss define active-design optimality; and
- what precise universal sentence a negative witness must refute.

Until then, the correct evidence-backed outcome is
`stop_full_resolution_attempt_pending_successor_definition`, with
`problem_resolved=false`.
