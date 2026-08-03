# Result v0.35

The robust public reset-atlas theorem converts registered pointwise nonlinear
connector words into uniform two-port safe closing.  The exact perturbation
recurrence

```text
E_(t+1) = A E_t + D omega
```

is checked against its closed form on 3,888 rational rows.  Strict nominal
safety and terminal reset margins make a connector valid on an open source
basin.  Compactness selects finitely many basins; their sensor labels cost
`ceil(log2 N_read)` bits, while the distinct actuator words separately cost
`ceil(log2 N_words)` bits.  Their maximum duration and both transcript costs
are constant, so the atlas supplies v0.33 safe closing.

The sharp nonlinear fixture

```text
x_next = 2*x + u + x^2/4 + w
```

uses the safe core `[-1,1]`, reset cell `[-1/8,1/8]`, disturbance radius
`1/128`, 33 source cells, and 33 distinct one-step actions.  The exact
Lipschitz error is `11/128 < 1/8`, giving six read bits and six write bits per
closing event.  Central and independent implementations check 3,171 exact
state/error/disturbance rows, including truncated endpoint cells.

Eight hostile mutations establish the boundaries: omitting the nonlinear
derivative, replacing worst-case disturbance by its mean, hiding an
observation collision, treating the actuator dictionary or sensor label as
free, dropping the reset margin, keeping fixed quantization for an arbitrary
unstable horizon, and claiming full canonical scope.

A scope defect found during construction is now explicit: the fixed-reset
atlas proves safe closing directly but does not satisfy v0.34's stronger
all-pairs local premise.  Only a separately registered all-pairs public atlas
may be used for that premise.

The predecessor inventory is frozen at 35 packages and 384 tests.  V0.35 adds
ten focused tests and an import-independent verifier.  The explicit 36-package
chain passes all 394 tests in 258.23 seconds with Python bytecode and pytest
caching disabled.  This is not a full
resolution of ASMP-4: the canonical normally hyperbolic wording still does not
entail robust pointwise public connector words, a sensor grammar, belief-cell
semantics, or a finite actuator dictionary.

V0.36 subsequently seals this residual registration gap together with the
earlier material forks and issues a single-root operational stop. It preserves
the v0.35 theorem and its scope boundary without treating conditional closure
as canonical resolution.
