# ASMP-9 physical dynamic-bridge prior-art gate v0.67

## Verdict

```text
register_as_measurement_bridge
```

The protocol is eligible for prospective registration because it tests a
physical response system on held-out scenarios. It is not eligible for a new
preference-elicitation, automata, or choice-theory novelty claim.

## State-identification ancestry

The construction transducer is an empirical specialization of classical
sequential-machine state identification:

- Edward F. Moore, “Gedanken-Experiments on Sequential Machines,” in
  *Automata Studies* (1956), 129–153:
  <https://doi.org/10.1515/9781400882618-006>.
- Arthur Gill, “State-Identification Experiments in Finite Automata,”
  *Information and Control* 4 (1961), 132–154:
  <https://doi.org/10.1016/S0019-9958(61)80003-X>.
- David Lee and Mihalis Yannakakis, “Principles and Methods of Testing Finite
  State Machines—A Survey,” *Proceedings of the IEEE* 84(8), 1996:
  <https://doi.org/10.1109/5.533956>.

Version v0.67 does not claim that its three-state discretization, deterministic
map fit, or held-out replay criterion is a new automata construction.

## Constructed and transient preference motivation

The decision to measure elicitation-induced change rather than assume a fixed
latent preference is motivated by:

- Eric J. Johnson, Gerald Häubl, and Anat Keinan, “Aspects of Endowment: A
  Query Theory of Value Construction,” *Journal of Experimental Psychology:
  Learning, Memory, and Cognition* 33(3), 2007:
  <https://doi.org/10.1037/0278-7393.33.3.461>.
- Dan Simon, Daniel C. Krawczyk, Alison Bleicher, and Keith J. Holyoak, “The
  Transience of Constructed Preferences,” *Journal of Behavioral Decision
  Making* 21 (2008), 1–14:
  <https://doi.org/10.1002/bdm.575>.

Those human experiments do not validate a language model as a model of human
preference. They justify keeping “measurement discovers a state” separate
from “measurement constructs a response.”

## Registered residual question

The residual contribution is an instrumented falsification:

```text
known deterministic transducer
  -> classical exact v0.66 state-identification result;

Qwen response under frozen token histories
  -> construction map plus untouched scenario replay;

replay conflict or unseen key
  -> latent_state_model_not_established;

context movement and washout
  -> reported independently of transducer validity.
```

The paired display orders, content-free label control, balanced-washout
control, byte-identical reset, and two-stage threshold freeze are experimental
controls. They are not mathematical novelty claims.

## Claim boundary

The run may establish a deterministic context effect, a registered terminal
response classification, or replay of the declared coarse transducer for one
model and scenario universe. It may not establish a persistent internal value,
human preference, moral truth, general preference identifiability, recursive
self-improvement, or an ASMP-9 resolution.
