# ASMP-3 consolidated path-risk disposition v2.14

## Executive disposition

The current evidence supports five distinct statements:

```text
literal v0.1 Weak-Verifier Characterization Conjecture
  = internally refuted exactly in both directions

nonnormative registry negative-route conditions
  = internally satisfied

repaired six-clause online-contract subclass
  = constructively characterized, black-box minimal, and robust to arbitrary
    dependence through controlled selected-path risk

unrestricted ASMP-3 classification
  = not established

community or prize-style acceptance
  = not established; external gate remains 0/2
```

This supersedes v2.12's noise description.  It does not change the exact
literal refutation or promote the repaired subclass into the unrestricted
classification requested by the original research program.

## 1. Literal named conjecture

The displayed v0.1 iff remains false in both directions.

1. In v0.7, the frozen complete parity game meets the three displayed criteria
   but has exact optimal gap `(3/5)^d`, which vanishes with depth.
2. In v2.5, the same one-query gap-`3/5` protocol survives singleton, padded,
   and empty choices of a nonbinding decidable `Refute` relation, so the literal
   local-refutation-dimension criterion is not necessary.

These are exact counterfamilies, not a failure to find a protocol.  They settle
the named v0.1 characterization as written, while leaving any differently
quantified successor as a new statement.

## 2. Repaired online normal form

The constructive/converse chain is:

```text
v2.3  deterministic finder -> fresh-noise protocol
v2.4  randomized Las Vegas-with-FAIL amplification
v2.5  witness-transparent protocol-to-finder extraction
v2.7  adaptive path coupling
v2.8  trace-complete Refute binding
v2.9  ideal replay for restartable oracle-parametric runtimes
v2.10 extraction from one actual noisy trace without restart
v2.11 black-box minimality of the six-clause online contract
v2.13 dependence-agnostic composition through selected-path risk
```

For the declared six-clause trace and revalidation contract, the one-shot
extractor succeeds with

```text
alpha >= max(0, 1 - s - delta_path),
```

where `delta_path` is the probability that at least one semantic error occurs
on the actually selected adaptive path.  The implication uses no independence
assumption.

## 3. Corrected correlated-noise boundary

V2.12 described the positive scope as fresh conditional post-history blocks.
That is sufficient but not necessary.  V2.13 proves:

- a persistent truth-independent common-mode flip has
  `delta_path = eta` at every nonempty depth;
- per-matching-prefix conditional bounds give
  `delta_path <= 1 - product_i(1-e_i)` without independence;
- an exchangeable latent-rate mixture gives
  `delta_path = 1-E[(1-P)^q] <= 1-(1-E[P])^q`; and
- fixed-class marginals alone do not control the chosen path when the noise
  state may correlate with public selection coins.

Thus the former v2.12 noise resume trigger has been used and cleared for the
online subclass.  Persistent non-amplification remains true: common-mode
repetition does not reduce `eta`.  It simply does not prevent positive one-shot
extraction whenever `s + eta < 1`.

The exact remaining firewall is not “correlation.”  It is failure to control
the joint selected-path event.

## 4. Complete-resolution requirement status

- **Formal class/invariant:** the declared black-box online subclass is
  characterized and premise-minimal; unrestricted task-specific scope remains
  open.
- **Constructive adaptive protocol:** satisfied for that subclass.
- **Matching resources:** exact for registered marker, covering, and black-box
  observation families; not interface-uniform across arbitrary interaction.
- **Correlated/noisy theorem:** exact for the online subclass through
  `delta_path`, for arbitrary dependence; marginal-only positive guarantees are
  ruled out by an exact selection counterfamily.
- **Encoding invariance:** benign quotient transport and the full-answer macro
  firewall are satisfied components.

The qualification “for the online subclass” is essential.  The v0.1 complete
resolution request asks for a broader class-level result.

## 5. Evidence and reproduction

Thirteen decisive packages have valid manifests and passing independent
repository checkers.  Their manifests bind 298 members totaling 17,672,457
bytes.  V2.14 reconstructs all manifests and all 18 requirement rows, rather
than trusting parent summary fields.

The correlated-risk evidence includes 24 common-mode rows, 20 conditional-chain
rows, 18,012 exact exchangeable-mixture/query cases with zero Jensen
violations, 31 selection-correlated counterexamples, and all 12 v2.10 online
composition rows.

Internal reproducibility is not external acceptance.  The expert gate remains
`0/2` qualifying teams and `0/1` independently implemented team checker.

## 6. Remaining blockers

Exactly four blockers remain:

1. authoritative adoption of a normative interface (`WV-FIX`, `WV-ADM`, or a
   successor) and its operational binding contract;
2. a non-black-box task-specific family or universal structure theorem beyond
   the v2.11 observation model;
3. interface-uniform interactive communication, semantic-query, and
   honest-work lower bounds; and
4. attributable external reproduction.

The former separate correlated-noise blocker is absent because v2.13 cleared
it at the exact scope of the repaired online theorem.

## 7. Safe label

Use:

```text
ASMP-3 v0.1 named iff: internally refuted exactly.
ASMP-3 repaired online subclass: constructively characterized, black-box
minimal, and correlated-noise robust through selected-path risk.
ASMP-3 unrestricted classification and external acceptance: not established.
```

Do not use “ASMP-3 fully solved” or “community accepted.”
