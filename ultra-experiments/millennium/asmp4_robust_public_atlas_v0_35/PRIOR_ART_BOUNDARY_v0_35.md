# Prior-art boundary v0.35

The mathematical ingredients are classical and are not claimed as new in
isolation.

- Colonius, Kawan, and Nair's invariance-entropy and invariance-pressure work
  supplies the surrounding worst-case data-rate perspective for controlled
  invariant sets.
- Pola, Girard, and Tabuada's approximate symbolic-model results establish
  how metric error bounds and alternating quantifiers support finite symbolic
  abstractions of nonlinear control systems.
- Da Silva and Kawan's hyperbolic-control-set theory supplies a rigorous
  hyperbolic setting in which invariance entropy admits dynamical formulas.
- Local-to-global controllability results explain when geometric local
  accessibility hypotheses can have global consequences, but do not by
  themselves charge a separated sensor label and actuator word.

Primary references used for this boundary are:

1. Da Silva and Kawan, [Hyperbolic Control Sets](https://arxiv.org/abs/1408.2416).
2. Colonius, Cossich, and Santana,
   [Invariance Pressure for Control Systems](https://arxiv.org/abs/1706.03025).
3. Pola, Girard, and Tabuada,
   [Approximately Bisimilar Symbolic Models for Nonlinear Control Systems](https://arxiv.org/abs/0706.0246).
4. Pola and Tabuada,
   [Symbolic Models for Nonlinear Control Systems: Alternating Approximate Bisimulations](https://arxiv.org/abs/0707.4205).

The repository contribution is the ASMP-4 architecture-specific composition:

- an exact rational Lipschitz-to-reset certificate;
- separate charged read-cell and write-word cardinalities;
- an explicit fixed-reset/all-pairs logical boundary;
- transport into the v0.33 two-port support-region theorem; and
- central plus import-independent mutation-tested harnesses.

V0.35 does not claim a new general symbolic-abstraction theorem, a new
invariance entropy formula, or a proof that classical local controllability
implies the registered public architecture required by ASMP-4.
