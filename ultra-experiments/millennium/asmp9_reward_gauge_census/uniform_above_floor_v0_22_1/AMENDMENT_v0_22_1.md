# ASMP-9 v0.22.1 mechanical amendment

Version v0.22 failed only its registered complexity-attribution gate.  The
frozen evaluator searched case-sensitively for a lowercase substring inside a
capitalized forbidden sentence.  Nine other gates passed, and the independent
verifier reproduced every numerical cell while correctly preserving the
failed composite verdict.

Version v0.22.1 makes exactly one evaluator repair:

```text
old: substring proxy over one forbidden sentence
new: exact equality of both complete structured claim lists
```

It changes no mathematical statement, trial count, threshold, resource cap,
or claim boundary.  The v0.22 record remains sealed and failed.

The successor uses three new graphs whose outcomes were unread at
registration: `K5`, a seven-vertex chorded cycle, and an eight-vertex chorded
cycle.  The burned registry includes the v0.22 wheel, octahedral, and Wagner
cells.

No claim is eligible until the amendment source is committed, the registration
is generated and committed, and the new cells are executed afterward.
