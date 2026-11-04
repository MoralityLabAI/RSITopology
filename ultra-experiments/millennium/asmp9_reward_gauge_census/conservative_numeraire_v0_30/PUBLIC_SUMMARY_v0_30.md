# When an intervention is actually a calibrated consequence

## Result

Version v0.30 resolves a hidden assumption in the v0.28 calibrated-offset
theorem: calling an intervention a numeraire does not make it one.

The registered certificate separates two questions.

### 1. Did the intervention leave the original decision problem unchanged?

The identity-level mechanical certificate requires identical state/action
sets, initial distribution, transition kernel, horizon, and target-feature
map at every consequence level. Under these conditions, every registered
policy has the same trajectory law and feature occupancy.

The fresh run verified all four deterministic stationary policies over four
consequence levels: 16 exact occupancy checks. Four matched controls changed
the horizon, policy feasibility, transition law, or feature map; each was
rejected with the altered field identified.

This is a conservative sufficient rule, not a maximal equivalence theorem.
Changed MDPs might still be equivalent under a separately declared
homomorphism.

### 2. Did the consequence add the declared scalar value?

For base object `i`, consequence level `j`, and scalar comparison argument
`V_ij`, exact calibration requires:

```text
V_ij - V_i,reference
  = c_j - c_reference.
```

The fresh five-by-four calibrated rectangle passed all 15 anchored
constraints. Matched controls separated:

```text
calibrated additive          coefficient 1
separable unknown scale      coefficient 9/7
context interaction          one 5/19 mixed residual
incomplete table             unavailable
```

The complete constraint family has rank `m(n-1)`. A separate five-by-six
cell had rank 25, and all 25 one-constraint omission witnesses passed. Thus
coverage is not a decorative requirement.

### 3. Mechanics cannot certify meaning

The calibrated, unknown-scale, and context-interacting semantic tables all
shared one mechanics hash. A mechanics-only auditor therefore cannot
distinguish them.

The unknown `9/7` coefficient also remained exactly observationally coupled
under both registered positive rescalings over the complete population grid.
This is the v0.28 scale obstruction in a mechanically conservative product
extension.

The semantic unit must be supplied by external calibration or stronger
behavioral measurement. It cannot be manufactured by adding an MDP field
named `money`, `tokens`, or `reward`.

### 4. Approximate calibration has an explicit cost

If every anchored scalar residual is at most `epsilon`, any two-sided
consequence offset has bias at most `2 epsilon`. The registered cell used:

```text
epsilon                         3/17
maximum two-sided bias          6/17
registered bound                6/17
```

The bound was attained, so the factor two cannot be improved without more
structure.

## Access ledger

```text
mechanical identity
  -> original policy laws and target occupancies preserved;

complete scalar rectangle
  -> additive semantic calibration tested;

both certificates
  -> v0.28 calibrated-offset operation eligible;

mechanics alone
  -> semantic coefficient unidentifiable;

epsilon semantic residual
  -> at most 2 epsilon two-sided offset bias.
```

## Registered verification

All eleven gates passed. The import-independent verifier reimplemented the
finite arithmetic and passed all twenty-three checks.

```text
implementation commit      b510b38a28fc30c6bd7b48f2c254122220f3b1ed
registration commit        6669fcdc95d828bdf12f27d48dce77c7c8840023
registration SHA-256       a925e338a0a4545daa83489afba259698c991b44293cb1459b409fd077c58d14
runtime                     0.121 seconds
peak resident memory        20,537,344 bytes
GPU                         none
```

## Prior-art and claim boundary

Exogenous/endogenous MDP decomposition, additive conjoint measurement,
reward invariance, environment design, and rectangular factorization are
classical. Version v0.30 is a scoped access ledger and executable gate; no
novelty is claimed for those ingredients.

The scalar value rectangle is stronger access than ordinal preferences. The
result does not establish a real consequence's cardinal utility, infer the
rectangle from human or model choices, validate a response model, prove that
all changed MDPs are nonconservative, or resolve ASMP-9.
