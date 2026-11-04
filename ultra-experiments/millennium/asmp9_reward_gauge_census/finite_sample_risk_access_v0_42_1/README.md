# ASMP-9 finite-sample risk access v0.42.1

This additive repair preserves the complete v0.42 scientific protocol and
changes only the failed executor boundary:

- exact rational margin strings are parsed through `Fraction`;
- the regression test uses the literal registered value `1/1000`; and
- sampling derives a fresh seed from the new v0.42.1 registration bytes.

The failed v0.42 registration, traceback, and failure receipt remain unchanged
in the parent directory. No v0.42 scientific result exists.
