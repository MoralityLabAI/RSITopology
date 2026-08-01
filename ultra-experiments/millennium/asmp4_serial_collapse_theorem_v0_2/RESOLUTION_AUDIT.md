# ASMP-4 resolution-obligation audit

## Candidate verdict

**Mathematical obligations satisfied for the canonical deterministic
noiseless, achieved-transcript, no-side-channel architecture.**

This is a candidate negative resolution of the premise that two independent
transversal entropies or a nonrectangular rate tradeoff can arise in that
architecture. It is simultaneously a positive characterization of the region
that remains:

```text
closure(R_K) =
    [h_perp(K_0,K),infinity) x [h_perp(K_0,K),infinity).
```

The result should be independently reviewed before the repository advertises
external consensus. The proof is self-contained; passing code is supporting
evidence only.

## Normative positive-resolution requirements

| Requirement | Evidence | Status |
| --- | --- | --- |
| Coordinate-invariant entropies | `THEOREM.md`, Section 6 proves conjugacy invariance and states the exact control-congruence condition for evaluator quotients. | Satisfied |
| Full capacity region | Theorems 2 and 3 give the entire finite and closed asymptotic regions. | Satisfied |
| Converse | Lemma 1, the definition of `nu_T`, and Theorems 2-3 give finite and asymptotic converses. | Satisfied |
| Constructive coder-controller | Theorem 1 constructs the relay normal form; Sections 4-5 construct a serial code from every safe control tree; Theorem 4 constructs exact scalar codes. | Satisfied |
| Finite-horizon correction | Theorem 4 gives `ceil(a^T delta/L)` exactly and the diagonal-box corollary recovers the Lyapunov sum. | Satisfied |
| Boundary counterexamples | Section 8 covers partial observation, uncertainty timing, actuator authority, nonhyperbolicity, side information, decoder memory, and tangent coupling; Section 1 isolates deadline-incompatible timing. | Satisfied |

## Normative negative-resolution requirements

The registry permits a negative resolution when:

1. the counterexample or impossibility uses the registered no-side-channel
   architecture; and
2. read/write rates and control authority remain frozen.

The relay theorem uses the strict serial no-side-channel architecture itself.
It does not change the plant, safe set, observation relation, actuator
authority, decoder, or transcript metric. It replaces a safe code by a
behaviorally identical code with the controller computation moved into the
sensor and an identity relay. Both requirements are therefore satisfied.

## Empirical firewall

The exhaustive finite harness does not establish the theorem. It checks:

- all 648 one-step budget cells from all 162 registered
  plant/observation pairs;
- exact mode-switching growth through horizon four;
- partial-observation and uncertainty-timing kill cases;
- side-information collapse;
- full-versus-restricted actuator authority;
- deadline-shifted relay equivalence for fixed FIFO delays;
- terminal-language versus causal-branching separation in the exact comb game; and
- scalar coasting, stable zero-rate, diagonal positive-exponent, and
  nonhyperbolic polynomial-growth formulas.

The resolution remains valid or invalid with the proof, not with the test
count.

## Assumption audit

| Assumption | Why load-bearing | Failure mode |
| --- | --- | --- |
| Realized transcript cardinality | Makes rate operational and invariant to unused-symbol padding. | Nominal non-nested dictionaries can violate upward closure. |
| Controller gets only read transcript | Lets the sensor simulate its deterministic output. | Private controller channel state adds a second input. |
| Actuator gets only write transcript | Makes write words determine control words. | Local mode/state sensing can reduce write rate to zero. |
| Timing-compatible fixed public delivery | Lets the sensor compute the controller output by the relayed read symbol's deadline; constant FIFO delay satisfies this. | Private, varying, or deadline-incompatible timing needs a larger timing/reliability model. |
| Uniform zero-error randomness semantics | Lets an independent seed be fixed without weakening the universal guarantee. | Pointwise almost-sure safety over an uncountable path family needs a reliability definition. |
| Relabelable port alphabets | Lets the read port carry the finite write symbol without adding an unreported peak-rate coordinate. | Fixed peak alphabets or burst caps require a larger capacity region. |
| Fixed control authority | Isolates information from actuation. | Changing action values with bit budget measures a different plant interface. |
| Arbitrary registered sensor computation | Permits upstream composition. | Computational restrictions create a computation/communication frontier not present in `R_K`. |
| Regenerative augmented invariance state (finite-block corollary only) | Makes `nu_T^reg` submultiplicative and repeatable, including public clock, queue, and decoder state. | The general asymptotic theorem instead uses the direct infinite-policy formula and allows arbitrary `K_0` contained in `K`. |

## Claim boundary

This package resolves the mathematical object actually defined by ASMP-4 v0.1
under deterministic noiseless, timing-compatible delivery. It does not resolve
a future noisy-channel, reliability-constrained, computationally bounded,
private-channel-state, deadline-incompatible, or fixed peak-alphabet variant.
Such a variant needs new rates and a new registry entry rather than being read
into the current formulas.
