# ASMP-9 stochastic-experiment object v0.37

## Status

Unregistered development note. No experiment is authorized and no novelty is
claimed.

Version 0.36 separates raw nuisance confusability from its connected-component
decision quotient. The next resolution-directed step is to make the response
law stochastic and to distinguish zero-error identification from bounded-risk
decision sufficiency.

## One data source, four different objects

Freeze:

- target parameters `theta in Theta`;
- nuisance states `xi in Xi`;
- an access design `A`;
- a finite transcript alphabet `Z_A`; and
- response laws `P^A_(theta,xi)` on `Z_A`.

For each target, the compound statistical experiment exposes the set

```text
P_A(theta) = {P^A_(theta,xi) : xi in Xi}.
```

Four objects must not be conflated.

### 1. Exact observational fiber

```text
theta ==_A theta'
iff P_A(theta) = P_A(theta').
```

This is an equivalence relation. It records equality of complete set-valued
response laws, not whether a finite observation distinguishes the targets.

### 2. Zero-error confusability

The relevant observation set depends on the oracle.

- With an exact population-law oracle, two targets are confusable when their
  sets `P_A(theta)` intersect.
- With one sampled transcript, replace each set of laws by the union of their
  supports and test support intersection.

Either relation can be reflexive and symmetric without being transitive. Its
graph retains pairwise access information. A deterministic decision map is
uniformly zero-error decodable exactly when it is constant on every connected
component.

### 3. Component decision quotient

The connected components form the finest equivalence relation containing all
zero-error confusability edges. This quotient exactly records which fixed
decision maps can be decoded with zero error. It discards the internal edge
geometry needed to ask which additional query breaks which ambiguity.

Any finite partition can be realized abstractly as the orbit partition of
some permutation group. Such an existence statement is mathematically
vacuous for reward learning. A reward gauge is scientifically meaningful only
when its transformations are declared independently and preserve the relevant
environment/decision semantics.

### 4. Bounded-risk statistical experiment

For positive error, a component quotient is generally insufficient. Given a
decision target `d`, loss `ell in [0,1]`, and decoder `delta`, define

```text
R_A(delta; d, ell)
  = sup_(theta,xi)
      E_(Z ~ P^A_(theta,xi))
        ell(delta(Z), d(theta)).
```

The minimax risk is the infimum over decoders. Access designs should be
compared by attainable risk or by statistical-experiment simulation, not by a
binary invariance partition alone.

## Candidate robust-deficiency lemma

For two finite access designs `A` and `B`, define the directional robust
deficiency

```text
delta_rob(A -> B)
  = inf_K sup_(theta,xi)
      TV(K P^A_(theta,xi), P^B_(theta,xi)),
```

where `K` ranges over Markov kernels from `Z_A` to `Z_B`, and the same frozen
nuisance index is used on both sides.

For every decoder on `B` and every loss in `[0,1]`, composing that decoder with
`K` gives an `A`-decoder whose worst-case risk exceeds the `B` risk by at most
the displayed total-variation error. Taking the infimum yields the
corresponding minimax-risk transfer bound.

This is the finite robust analogue to the classical Blackwell/Le Cam
simulation idea. The inequality is elementary; whether the exact formulation
and its converses are already standard for compound experiments must be
settled before registration.

## Proposed exact finite experiment

Use rational kernels with:

- three targets;
- two nuisance states;
- binary outputs;
- one- and two-query access designs; and
- every binary decision map plus the identity decision.

Compute directional deficiency by rational linear programming. Keep
population-law and sampled-transcript oracles in separate strata.

### Candidate gates

1. **B0 — Blackwell anchor:** with one nuisance state, the LP agrees with
   classical finite garbling/simulation checks.
2. **R0 — risk transfer:** every enumerated decoder/loss cell respects the
   registered deficiency upper bound.
3. **S0 — quotient insufficiency:** exhibit two channels with the same
   zero-error component quotient but different exact bounded-risk frontiers.
4. **Q0 — access monotonicity:** appending a query with compatible shared
   nuisance cannot worsen the optimal risk or deficiency to the full
   experiment.
5. **H0 — deterministic embedding:** point-mass kernels reproduce every v0.36
   headline count.

S0 is the load-bearing liveness gate. If it fails on the registered universe,
the experiment reports that the chosen finite class did not separate
zero-error quotient from bounded-risk geometry; it does not widen the class
after outcomes.

## Resolution value

This branch can sharpen obligation 1 and provide the language for obligation
4:

- exact fibers describe observational equality;
- confusability graphs describe zero-error access;
- components describe fixed zero-error decision feasibility;
- robust deficiency describes approximate decision sufficiency under a frozen
  misspecification/nuisance class.

It still would not supply the adaptive query theorem or matching complexity
bounds required by obligations 2 and 3.

