# ASMP-3 independent-noise amplification completion audit v1.8

## Newly closed

```text
registered iid Bernoulli replication class p in [0,eta] = typed
likelihood-ratio majority/tie rule = proved optimal
worst adversarial iid rate p=eta = proved/certified
exact binomial Bayes error e_d(eta) = certified
single-atom amplification profile a_H(d)=e_d(eta) = exact
value 1-2e_d(eta) = exact
even/odd recurrence and strict odd-step gain = exact
rational Bhattacharyya exponential bound = certified
seven eta values and depths 1..64 = certified (448 rows)
word-level total variation = exhaustively checked (30 cases)
rate monotonicity grid = checked (1008 triples)
persistent-correlation separation = exact
v1.7 expectation-only baseline comparison = exact
clean-room binomial/TV/rate/recurrence checker = passed
```

## Still open

```text
transcript-conditional independence under adaptive refutation selection = open
block-independent composition across several semantic atoms = open
query-replication encoding and cost invariance = open
adaptive verifier query selection and stopping = open
truth-aware, exchangeable, and partially correlated noise frontiers = open
honest-prover computation characterization = open
matching communication and honest-prover lower bounds = open
WV-ADM interface optimization = open
v0.1 scope adjudication = open/normative
external mathematical review = absent
```

## Positive-lane boundary

For one registered atom, the independent-noise amplification profile is no
longer an open quantity: it is the exact binomial tail in the theorem.  The next
nontrivial obstruction is compositional—whether this independence and query
budget survive adversarial transcript/refutation selection—not additional
single-atom majority simulation.

## Non-overclaim rule

Marginal error `eta` does not imply the i.i.d. profile.  The persistent law in
the release has the same marginals and no amplification, so every use of the
positive theorem must carry its complete correlation-class assumption.
