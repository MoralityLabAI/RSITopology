# Prior-art boundary v0.27

Approximate simulation and bisimulation are classical. Girard and Pappas,
[Approximation Metrics for Discrete and Continuous Systems](https://doi.org/10.1109/TAC.2007.895849),
develop approximate language inclusion, simulation, and bisimulation metrics.
Pola and Tabuada,
[Symbolic Models for Nonlinear Control Systems: Alternating Approximate Bisimulations](https://arxiv.org/abs/0707.4205),
give the alternating notion appropriate to controller/adversary systems.
Girard,
[Controller Synthesis for Safety and Reachability via Approximate Bisimulation](https://arxiv.org/abs/1010.4672),
studies safety-controller concretization and safety-set approximation.

No novelty is claimed for approximate bisimulation, alternating simulation,
symbolic abstraction, safety-set erosion, or representative-history controller
concretization as general ideas.

The repository contribution is deliberately narrower:

1. it registers the ASMP-4 two-port objective as coordinatewise worst-path
   limsup additive read/write costs;
2. it proves the exact `T epsilon` finite-horizon and `epsilon` asymptotic
   budget shifts for that vector objective while retaining unrestricted causal
   strategy memory;
3. it isolates exact Boolean safety as a separate load-bearing clause;
4. it gives an arbitrarily-close nonempty/empty zero-error region witness and
   a sharp strict Lipschitz-margin repair; and
5. it supplies central vector-frontier and import-independent scalar-game
   harnesses plus mutation tests for the registered statement.
