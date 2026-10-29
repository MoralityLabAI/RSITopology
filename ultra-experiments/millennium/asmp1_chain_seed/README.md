# ASMP-1 finite-chain seed

This directory isolates a closed seed of ASMP-1. It studies deterministic
finite mechanisms

```text
X --h--> H --g--> Y
```

when every input environment and every perfect hidden-state intervention is
available, but the names of hidden states are a global `Sym(H)` gauge.

The formal statements and proofs are in [`THEOREM_v0_1.md`](THEOREM_v0_1.md).

The theorem is that the remaining compatible mechanism orbits are
exactly the set partitions hidden inside each output fiber. If
`n_y = |{x:g(h(x))=y}|` and `k_y = |g^-1(y)|`, the number of compatible orbits is

```text
product_y sum_(j=0)^k_y S(n_y,j)
```

for arbitrary `h`, and

```text
product_y S(n_y,k_y)
```

when `h` is surjective. Here `S(n,k)` is a Stirling number of the second kind.

The protocol registers a counterexample to "cut coverage is sufficient" in
this finite setting: full input coverage and `do(H=a)` for every hidden state do
not reveal how labelled inputs partition among hidden states that the downstream
map aliases.

It also registers a second obstruction on a Boolean three-parent star. Passive
and every singleton-`do` output count span only a rank-4 subspace of the
8-dimensional truth-table space. Two explicit functions have identical
registered measurements and make every parent essential, but differ in
higher-order interaction structure and are not related by parent-coordinate
permutations or parent-bit flips. This turns the proposed repair into a
linear-algebraic one: the registered intervention design must be injective on
the mechanism class, with a positive quotient separation modulus in the noisy
setting.

## Commands

Run planted and small exhaustive tests:

```powershell
Set-Location ultra-experiments/millennium/asmp1_chain_seed
python -m unittest -v test_chain_identifiability.py
```

The full registered enumeration is intentionally run only after the protocol,
source, and tests are committed. Its command is:

```powershell
python chain_identifiability.py `
  --protocol protocol_v0_1.json `
  --output artifacts/result_v0_1.json `
  --max-input-size 5 `
  --max-hidden-size 4 `
  --max-output-size 3
```

This is an exact finite theorem seed and counterexample, not transformer
evidence and not a resolution of the generic analytic ASMP-1 statement.
