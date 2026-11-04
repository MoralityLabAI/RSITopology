# ASMP-3 research report through v2.19

## Executive summary

ASMP-3 asks which tasks admit constant-gap, doubly efficient oversight by a
weak verifier using a polylogarithmic number of noisy semantic judgments. The
research program produced several exact counterfamilies, constructive subclass
theorems, and sharp resource frontiers. Its strongest defensible disposition is:

```text
V0.1 displayed characterization iff:
  internally refuted in both directions under strict FIX.

Repaired six-clause online subclass:
  constructively characterized, premise-minimal in its black-box model, and
  robust to arbitrary dependence through selected-path risk.

Unique-marker resource family:
  exact through arbitrary public-coin rounds, adaptive semantic queries, and
  bounded soundness.

Unrestricted ASMP-3 classification:
  not established.

Mathematical impossibility of ASMP-3:
  not proved.

External acceptance:
  not established; qualifying expert gate remains 0/2.
```

V2.18 temporarily promoted a conditional interpretation lemma into completion
of a resolve-or-impossibility goal. V2.19 withdraws that promotion. The source
order supports strict `FIX` as the conservative reading, but `ADM` clause
preservation and formal entailment of `FIX` are both unproved.

## 1. Problem and source status

The v0.1 canonical setting freezes:

- the decision relation;
- public-coin message order and stopping;
- the atomic semantic-query language and registered replications;
- ideal and noisy semantic oracles with a complete correlation/adaptivity
  class;
- verifier time, query, and transcript budgets;
- admissible transcript encodings, randomness, and adaptive access as game
  components; and
- a decidable terminal `Refute` relation.

It then conjectures that constant-gap weak verification is equivalent to three
conditions: polylogarithmic local-refutation dimension, efficient honest
refutation search, and constructively amplifiable semantic noise.

The document is explicitly a research-agenda definition draft rather than a
prize announcement. Its graduation standard requires an explicit quantifier
order and a closed formal core. Its two-sided resolution rule also states that
refuting one proposed criterion does not resolve a broader classification
program unless that criterion is the entire frozen statement.

## 2. Interpretation audit

### Strict fixed-interface reading

The source first defines and freezes the game and only afterward quantifies
protocol admission. Ordinary sequential reading therefore favors:

```text
FIX: for a frozen game G, quantify protocol algorithms Pi inside G.
```

This is the conservative reading used for the decisive v0.7 counterfamily. It
is an interpretive conclusion, not a machine-proved formal entailment, because
v0.1 has no formal semantics for the relevant English scope.

### Protocol-admissible interface reading

The typed v0.2 successor introduces:

```text
E_n, G_n, Interfaces(E_n), Q_n=(G_n,Pi_n).
```

It defines an alternative `ADM` target in which protocol admission can select
an interface from a declared class. This is mathematically coherent and useful
for a successor problem, but those objects are absent from v0.1. No proof shows
that moving game selection inside protocol admission preserves v0.1's earlier
freeze scope.

The correct interpretive status is therefore:

```text
FIX = conservative natural reading, not formally entailed
ADM = reasonable successor target, not proved clause-preserving
```

## 3. Exact refutation of the displayed iff

### 3.1 Sufficiency counterfamily: frozen parity game

V0.7 constructs a complete oracle-relative family with semantic depth
`d=floor(log2 n)` and persistent semantic error `1/5`. It proves:

```text
r_R(N) = d = Theta(log T(N));
efficient honest refutation search exists;
a_H(k) <= 1/5 for every k >= 1;
optimal completeness/soundness gap = (3/5)^d -> 0.
```

The proof identifies the verifier's observation with a noisy parity channel.
Under even- and odd-parity priors, the exact total variation is `(3/5)^d`.
Adaptive queries, public coins, and stopping rules are post-processing kernels,
so they cannot increase that advantage. All three displayed right-hand
conditions hold while constant-gap protocol admission fails in the frozen
interface. Thus displayed sufficiency is false under strict `FIX`.

If vector messages are added, a one-query protocol obtains completeness `4/5`,
soundness `1/5`, and gap `3/5`. This shows that changing the interface changes
the witness outcome; it does not prove that the added interface was already
admissible in v0.1.

### 3.2 Necessity counterfamily: nonbinding `Refute`

V2.5 holds a gap-`3/5` protocol fixed while changing a decidable `Refute`
relation that the verifier never consults. Across transparent singleton,
padded sound-complete, and empty variants, the protocol value is identical,
while local-refutation dimension becomes respectively:

```text
1, T (super-polylogarithmic), or infinity.
```

The finite audit exhaustively checks all worlds, claims, and atom subsets for
two through eight semantic classes. Six asymptotic rows establish the padded
separation. Hence the literal local-refutation criterion is not necessary
without an operational binding axiom.

Together, v0.7 and v2.5 internally refute both directions of the displayed iff.
They do not rule out a repaired invariant or characterize the unrestricted
fixed-interface class.

## 4. Repaired constructive subclass

V2.3–v2.13 develop a six-clause online trace-and-revalidation contract:

1. witness transparency;
2. ideal replay or trace access;
3. binding to the declared refutation object;
4. an online extractor;
5. controlled semantic revalidation; and
6. a positive selected-path noise margin.

The constructive direction turns an efficient finder into a noisy verification
protocol. The converse extracts a finder from one actual noisy trace. V2.11
provides a failure family for removing each premise, establishing black-box
premise minimality at the declared scope.

For arbitrary noise dependence, v2.13 proves the one-shot extraction bound

```text
alpha >= max(0, 1 - s - delta_path),
```

where `s` is false-acceptance probability and `delta_path` is the probability
that at least one semantic error occurs on the selected adaptive path. No
independence assumption is required. Fixed marginal error bounds alone are
insufficient because public selection may correlate with the hidden noise
state.

This is a genuine characterization of the declared online subclass, not of
all `WV-FIX` protocols.

## 5. Encoding and resource results

### Encoding invariance

V2.0 establishes benign quotient transport and a full-answer macro firewall.
Duplicated synonymous atoms do not inflate dimension after quotienting, while
adding semantic content—such as a per-atom truth vector to a parity-only
alphabet—is a change of interface rather than benign re-encoding.

### Marker-family search and checking

The unique-marker packages establish exact black-box frontiers. An honest
finder needs `N` worst-case probes to locate an unstructured marker. With at
most `K` complete prover transcripts and `q` adaptive semantic queries, the
arbitrary-round public-coin frontier is

```text
C*   = s + (1-s) min(1, Kq/N),
C*-s =     (1-s) min(1, Kq/N),
```

where `s` is bounded zero-world soundness. Interaction compresses to at most
`K` all-zero-answer paths per public seed, and cyclic public-coin constructions
attain the upper bound. These results cover arbitrary finite rounds, adaptive
queries, bounded completeness/soundness, and finite seed balancing.

They are sharp for the registered marker family. They are not universal
cross-task lower bounds because v0.1 never supplies a formal cross-task class,
reduction notion, advice model, or interface-invariance rule.

## 6. The v2.18 error and v2.19 correction

V2.18 constructed `FIX` and `ADM` rows, copied phrase-presence predicates into
both, and labeled both clause-preserving. From that assumption it correctly
derived a conditional no-singleton-selector lemma and a randomized minimax
error of `1/2`.

The construction did not formally interpret every source clause or prove that
`ADM` satisfies the original freeze order. In particular, “frozen within the
realized game” was an added qualifier that enabled `ADM`. Consequently:

- the conditional selector lemma survives;
- the unconditional semantic-underdetermination premise is not established;
- the resolve-or-impossibility completion is withdrawn; and
- the claim that all internal research should stop is replaced by a
  lane-specific stop.

V2.19 independently reconstructs source order, the four ADM-only added objects,
the v0.7 and v2.5 counterfamilies, the canonical resolution policy, and the open
normative/external gates.

## 7. What remains open

Four substantive blockers remain:

1. **Formal class:** register a strict fixed-interface class, reductions, and
   invariance rules—or authoritatively publish a different successor.
2. **Unrestricted structure:** prove a task-specific non-black-box theorem or a
   universal characterization beyond the six-clause online observation model.
3. **Uniform resources:** prove matching communication, semantic-query, and
   honest-work lower bounds across the registered class rather than only exact
   families.
4. **External acceptance:** obtain two attributable independent expert
   reproductions, including one independently implemented checker for
   machine-assisted work.

No current theorem establishes that these objectives are impossible.

## 8. Recommended next research program

The most source-faithful continuation is:

1. freeze a typed strict-`FIX` class `WV-FIX(E,G)`;
2. declare reductions and benign interface transformations;
3. replace the nonbinding v0.1 dimension with an adequate, replication-
   quotiented, operationally bound invariant;
4. state a joint selected-path noise functional;
5. test the proposed invariant against the parity, nonbinding-`Refute`, marker,
   macro-query, selection-correlated-noise, and premise-removal counterfamilies;
6. prove constructive and converse resource transport; and
7. seek external reproduction before making prize-grade claims.

Publishing `FIX` and `ADM` as separate problems is preferable to silently
mixing their quantifiers.

## 9. Verification record

The v2.19 correction passed:

```text
producer gates = 10/10
clean-room checks = 10/10
focused tests = 12/12
full ASMP-3 regression = 458/458 across 40 test files
standalone ASMP-3 checkers = 36/36
external expert gate = 0/2; complete=false
```

The successful external checker result verifies that the acceptance gate is
still open; it does not count missing review as completion.

## Conclusion

The ASMP-3 work has decisively falsified its original displayed iff under the
conservative strict-game reading and has produced exact positive and negative
theorems for meaningful subclasses. It has not supplied an unrestricted class
characterization and has not proved that such a characterization is
impossible. The correct research posture is neither “solved” nor “impossible,”
but “original criterion refuted; substantial repaired theory established;
formal unrestricted target and external validation still open.”
