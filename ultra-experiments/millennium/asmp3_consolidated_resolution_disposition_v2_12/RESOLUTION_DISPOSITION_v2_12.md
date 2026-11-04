# ASMP-3 consolidated resolution disposition v2.12

## Executive disposition

Five layers must remain separate:

```text
literal v0.1 Weak-Verifier Characterization Conjecture
  = refuted internally, exactly, in both directions

nonnormative registry negative-route mathematical conditions
  = satisfied internally

repaired six-clause online-contract subclass
  = constructively characterized and black-box minimal

unrestricted ASMP-3 classification
  = not established

community or prize-style acceptance
  = not established; external gate remains 0/2
```

This supersedes the v2.6 disposition.  The literal refutation is unchanged, but
the repaired result is now substantially broader: v2.10 extracts from one
actual noisy execution even for one-shot stateful strategies, and v2.11 proves
the remaining six-clause online contract minimal for the registered black-box
Las Vegas model.

## 1. Literal named conjecture

The displayed v0.1 iff fails in both directions.

1. **Frozen sufficiency fails.**  The v0.7 complete parity game satisfies the
   three displayed criteria while its exact optimal gap is `(3/5)^d`, which
   vanishes.  Honest work remains `Theta(T)` and semantic error remains `1/5`.
2. **Literal necessity fails.**  The v2.5 one-query, gap-`3/5` protocol is
   unchanged when its nonbinding decidable `Refute` relation is singleton,
   padded to dimension `T`, or empty with infinite dimension.

Therefore the literal universal characterization is internally refuted under
both principal readings.  A successor that replaces its objects or quantifiers
is a different statement.

## 2. Updated repaired normal form

The constructive chain now has the following shape:

```text
v2.3  deterministic finder -> fresh-noise protocol
v2.4  randomized Las Vegas-with-FAIL finder amplification
v2.5  witness-transparent protocol-to-finder extraction
v2.7  adaptive fresh-path coupling and exact noise loss
v2.8  witness transparency from trace-complete Refute binding
v2.9  ideal replay for restartable oracle-parametric runtimes
v2.10 online extraction from one actual noisy trace, no restart required
v2.11 black-box minimality of the six-clause online contract
```

The strongest current converse is v2.10, not v2.5 or v2.9.  On an actual noisy
rejection it extracts the logged candidate, evaluates `H` only on that
candidate, reruns `Refute`, and otherwise returns `FAIL`.  It is Las
Vegas-valid, works for one-shot stateful strategies, has dimension `r<=q`, and
succeeds with

```text
alpha >= 1-s-delta_q.
```

V2.11 proves that public bound trace access, candidate-only `H`, mandatory ideal
rechecking, adaptive path-error control, queried quotient scope, and complete
resource accounting each have a registered failure mode when removed.

The correct repaired label is therefore:

```text
constructively characterized and black-box minimal for the declared
six-clause online-contract subclass.
```

## 3. Complete-resolution requirement status

The stronger normal form does not convert the entire research frontier into a
closed class equality.

- **Formal class/invariant:** closed for the declared online subclass and
  black-box observation model; unrestricted task-specific/non-black-box scope
  remains open.
- **Constructive adaptive protocol:** satisfied for the declared subclass.
- **Matching resource lower bounds:** exact for unique-marker, one-message, and
  black-box observation families; not universal across arbitrary interaction.
- **Correlated/noisy theorem:** exact for fresh conditional post-history blocks;
  persistent or adversarial correlation without a path bound remains outside.
- **Encoding invariance:** benign quotient transport and the macro-query
  firewall are satisfied components.

The machine artifact contains 18 evidence-backed requirement rows and forbids
promoting partial rows to universal claims.

## 4. Evidence and reproduction status

Twelve decisive packages are release-sealed and independently checked inside
the repository.  Their manifests bind 275 members totaling more than 16 MB.
The v2.12 clean-room checker independently rehashes those members and
reconstructs the status map.

This is strong internal reproducibility, but it is not external acceptance.
The expert gate remains:

```text
qualifying independent expert teams = 0/2
independently implemented team checker = 0/1
completion gate = false
```

Repository-generated simulated reviews cannot satisfy identity or independence.

## 5. Remaining blockers

Five blockers remain:

1. authoritative choice of `WV-FIX` versus `WV-ADM` and the operational online
   contract;
2. a task-specific non-black-box theory beyond the v2.11 observation model;
3. interface-uniform interactive communication/query/honest-work lower bounds;
4. a broader correlated-noise theorem or sharp impossibility; and
5. attributable external expert reproduction.

The v2.11 harness proves that none is an unresolved marker count or probability
denominator.  Extending the current grid is therefore stopped.

## 6. Safe public label

Use:

```text
ASMP-3 v0.1 named iff: internally refuted exactly.
ASMP-3 repaired online subclass: constructively characterized and
black-box minimal.
ASMP-3 unrestricted classification and external acceptance: not established.
```

Do not use “ASMP-3 fully solved” or “community accepted.”  Do not regress to the
obsolete v2.6 description that ideal simulation or restartability is still the
main converse blocker.
