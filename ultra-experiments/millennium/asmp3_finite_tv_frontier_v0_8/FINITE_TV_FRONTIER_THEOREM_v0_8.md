# ASMP-3 finite transcript-separation theorem v0.8

## Status and scope

```text
result_status = exact finite typed subtheorem
parent = ASMP-3 / typed successor draft v0.2
interface_mode = WV-FIX
protocol_stage = fixed transcript laws followed by a randomized terminal decision
changes_parent_problem = false
```

This theorem closes the finite post-transcript decision lane of `WV-FIX`.  It
does not decide what ASMP-3 v0.1 meant by “admits a protocol,” and it does not
claim a characterization of arbitrary efficient interactive protocols.

## 1. Frozen finite lane

Fix an input length and a typed game interface `(E,G)`.  Let `Omega` be its
finite canonical terminal-observation alphabet after all interaction, semantic
queries, legal noise, and stopping behavior have occurred.

Let

```text
H = {p_1,...,p_h}
F = {q_1,...,q_f}
```

be nonempty finite classes of probability laws on `Omega`:

- `H` contains every truthful terminal law over which completeness must hold;
- `F` contains every false/adversarial terminal law over which soundness must
  hold.

A randomized terminal verifier is a function

```text
a : Omega -> [0,1],
```

where `a(omega)` is the probability of selecting the truthful output after
observing `omega`.  Its uniform gap is

```text
gap(a;H,F)
  = min_(p in H) E_p[a] - max_(q in F) E_q[a]
  = min_(p in H,q in F) <p-q,a>.
```

Define `gamma*(H,F)=max_a gap(a;H,F)`.

## 2. Exact characterization

### Theorem 1 (finite transcript-separation frontier)

For every finite `Omega`, `H`, and `F` above,

```text
gamma*(H,F)
  = min_(p in conv(H), q in conv(F)) TV(p,q).
```

Consequently:

1. a positive uniform terminal-verification gap exists exactly when
   `conv(H)` and `conv(F)` are disjoint;
2. for a sequence of finite typed games, a uniform constant gap exists exactly
   when

   ```text
   inf_n distance_TV(conv(H_n),conv(F_n)) > 0;
   ```

3. pairwise separation of the named laws is insufficient—separation must
   survive convexification; and
4. a necessary-and-sufficient finite invariant is a joint transcript-law
   invariant, not a list of single-atom marginal accuracies.

### Proof

Write `d_(i,j)=p_i-q_j`.  Since minimization of a linear functional over a
simplex occurs at an extreme point,

```text
gamma*
  = max_(a in [0,1]^Omega)
      min_(lambda in Delta(H x F))
        <sum_(i,j) lambda_(i,j)d_(i,j), a>.
```

The cube and simplex are compact convex sets and the displayed payoff is
bilinear.  Finite minimax therefore exchanges `max` and `min`:

```text
gamma*
  = min_lambda max_a <p_lambda-q_lambda,a>,
```

where

```text
p_lambda = sum_(i,j) lambda_(i,j)p_i,
q_lambda = sum_(i,j) lambda_(i,j)q_j.
```

Every joint `lambda` yields one point in `conv(H) x conv(F)`.  Conversely, any
pair of convex mixtures is realized by the product coupling of its two mixture
weights.  Thus the possible `(p_lambda,q_lambda)` are exactly
`conv(H) x conv(F)`.

For any two probability laws, `sum_omega(p-q)=0`, so

```text
max_(0<=a<=1) <p-q,a>
  = sum_omega max(p(omega)-q(omega),0)
  = (1/2)||p-q||_1
  = TV(p,q).
```

Substitution proves the identity.  The two convex hulls are compact; therefore
their TV distance is positive exactly when they are disjoint.  Applying the
identity at every length proves the asymptotic statement.  QED.

## 3. Exact certificate form

The harness uses matching rational certificates.

### Lower certificate

Provide `a in [0,1]^Omega` and `gamma` such that

```text
<p_i-q_j,a> >= gamma  for every (i,j).
```

### Upper certificate

Provide rational weights `lambda_(i,j)>=0` summing to one and values
`t_omega>=0` such that

```text
t_omega >= sum_(i,j) lambda_(i,j)
                    (p_i(omega)-q_j(omega)).
```

Then

```text
gamma* <= sum_omega t_omega.
```

Matching `gamma=sum t_omega` proves the optimum exactly.  This format avoids a
floating-point optimizer and is independently checkable with integer/rational
arithmetic.

## 4. Parity-channel corollary

Let hidden words have length `d`.  Truthful worlds have even parity, false
worlds have odd parity, and every bit passes through an independent BSC with
error `1/5`.  Accept when the observed word has even parity.

With `lambda=1-2/5=3/5`, every even input is accepted with probability

```text
(1+lambda^d)/2,
```

and every odd input is accepted with probability

```text
(1-lambda^d)/2.
```

The lower gap is `lambda^d`.  For the upper certificate, mix uniformly over
the even worlds and uniformly over the odd worlds.  Their signed observation
law difference is

```text
+lambda^d / 2^(d-1)  on every even observation,
-lambda^d / 2^(d-1)  on every odd observation.
```

Its positive mass is exactly `lambda^d`.  Hence

```text
gamma* = (3/5)^d.
```

This recovers the v0.7 frozen parity obstruction as an instance of the finite
convex-hull distance theorem, rather than as an isolated Fourier calculation.

## 5. Why the joint object is necessary

The certified fixtures expose both failures of marginal reasoning:

- **decaying global signal:** every BSC coordinate has constant single-bit
  advantage `3/5`, while parity's optimal joint gap is `(3/5)^d -> 0`;
- **invisible marginal signal:** the law uniform on `{00,11}` and the law
  uniform on `{01,10}` have identical one-coordinate marginals but TV distance
  one, so a joint parity decision separates them perfectly.

The convex-hull collision fixture adds a separate warning.  Honest laws
`delta_0` and `delta_1` are each separated from the false uniform law, but the
uniform law is their midpoint.  No single terminal decision has positive
uniform gap.

## 6. Replication and benign encoding

Splitting every observation into `r` equiprobable ancillary aliases changes
the raw alphabet from two outcomes to `2r` outcomes but leaves the TV gap at
`3/5`.  The exact certificates cover `r=1,...,8`.

This is a representation-refinement check, not a license to treat independent
new semantic measurements as aliases.  A transformation that changes the
conditional transcript law or supplies new semantic content changes `G` and
is outside benign encoding invariance.

## 7. Relation to the full problem

For a fixed protocol and fixed adaptive interaction tree, legal strategies and
noise processes induce transcript laws.  The theorem says that terminal
selection succeeds exactly when the resulting truthful and false law hulls
remain uniformly separated.

Three larger obligations remain outside this theorem:

1. constructing an efficient interactive protocol whose induced law hulls are
   separated;
2. representing exponentially or infinitely many adaptive strategies and
   noise processes efficiently; and
3. characterizing `WV-ADM`, where the protocol may select a different
   interface and therefore a different pair of law classes.

Those are genuine next problems.  They are no longer conflated with the exact
finite terminal-decision criterion.

## 8. Claim boundary

The minimax/TV identity is a classical finite decision-theoretic fact.  The
contribution here is its typed placement inside ASMP-3, the exact rational
certificate format, the parity/convex-hull/joint-noise audit, and the explicit
boundary between terminal separation and protocol construction.  No novelty
claim is made for finite minimax or binary hypothesis testing itself.
