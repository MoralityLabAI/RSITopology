# ASMP-4 adaptive-history collapse v0.5

**Successor scope note.** The v0.6 registration-fork theorem preserves every
v0.5 adaptive-prefix result but shows that the canonical v0.3 diagonal theorem
cannot be promoted across sensor grammars that forbid upstream computation.
The current canonical status is a partial structural classification, not an
unconditional candidate resolution.

This package closes the scheduling gap left intentionally open by the v0.4
heterogeneous-cost fixture. It permits public deterministic codebook choice
from common decoded history, computes the exact finite Bellman frontiers, and
proves that `O(log n)` worst-write slack restores the expected-read/worst-write
lower corner in asymptotic rate. The martingale proof also covers every
positive sorted four-plan law, including the full skew/boundary/balanced phase
identified in v0.4. The final theorem covers arbitrary finite i.i.d. plan
alphabets: optimal expected prefix length and minimum worst prefix length are
jointly attainable in closed asymptotic rate. A uniform conditional-MGF guard
also covers correlated exogenous sources, demonstrated by an exact rotating
Huffman Markov fixture. A further vanishing-maximum theorem removes the
uniform-MGF premise whenever bounded code-length surplus has a negative
almost-sure rate. Exact time-varying and observable stationary-ergodic renewal
sources separate the two hypotheses. The final public-predictor theorem gives
the full rectangle for every stationary ergodic finite full-support plan source
whose sufficient predictive state is common causal information. For finite
public predictors with state-dependent support, a positional prefix-code
mean-payoff game replaces the fixed worst-length threshold; a competing-cycle
fixture verifies the case where read- and write-optimal codes differ. Its
two-sided Bellman potential certifies the write value against arbitrary
history-dependent coders and explains the exact finite transient bound.

Run the central harness:

~~~powershell
python run_verification.py
~~~

Run the independent verifier:

~~~powershell
python verify_adaptive_theorem.py
~~~

Run the tests from this directory or by explicit path:

~~~powershell
python -m pytest -q test_adaptive_frontier.py
~~~

The main artifacts are:

- `THEOREM.md`: exact finite recurrence and adaptive asymptotic theorem;
- `RESULT.md`: result summary and interpretation;
- `adaptive_frontier.py`: exhaustive action census, Bellman DP, witness replay,
  and martingale-bound calculator;
- `verify_adaptive_theorem.py`: independent implementation with no import from
  the central harness;
- `COMPLETION_AUDIT_v0_5.md`: claim-by-claim evidence and remaining scope;
- `CANONICAL_SCOPE_AUDIT_v0_5.md`: line-by-line audit of the v0.2/v0.3
  normal-form claim against the original ASMP-4 quantifiers;
- `STOPPING_ARGUMENT_v0_5.md`: evidence-backed boundary for ending this finite
  harness lane; and
- `PRIOR_ART_AUDIT_v0_5.md`: primary-source novelty firewall for the classical
  buffer-overflow and exponential-length ingredients.

The integrated verification run passes 62 tests across all six ASMP-4
generations, all current theorem verifiers, and the frozen v0.1 receipt replay.
