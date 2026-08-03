# Reviewer packet v0.18

## Claim to attack

For the stated finite known-initial-state transducer contract, universal
support safety is feasible exactly when every reachable subset-observer
transition has a singleton current `q` class. In the feasible case the exact
region is `[1+log2(rho(A)),infinity) x [2,infinity)`.

## Highest-value falsification attempts

1. Exhibit two supported executions at the earliest mixed transition for
   which the prior raw history cannot be synchronized with the same normal
   transcript, contradicting the necessity proof.
2. Find a reachable transducer whose output-language exponential rate differs
   from the spectral radius of its multiplicity observer matrix.
3. Find a feasible member of the 256-transducer census outside the stated 80,
   or an infeasible member inside it.
4. Give a legal code under the frozen separate-charging contract with fewer
   than `L_T ceil(rho*2^T)` read transcripts or fewer than
   `2^T ceil(rho*2^T)` write transcripts.
5. Show that the history-toggle example uses an uncharged sensor-state or
   normal-state side channel.

## Load-bearing registrations

- the sensor transducer and its initial state are fixed and registered;
- the controller receives raw outputs but not hidden sensor state;
- the normal symbol depends only on the normal coordinate;
- raw words and normal cells are separately and injectively charged;
- every disturbance and supported event word is adversarially quantified; and
- current sensing precedes current writing.

Relaxing any of these assumptions defines a successor problem rather than a
counterexample to this theorem.
