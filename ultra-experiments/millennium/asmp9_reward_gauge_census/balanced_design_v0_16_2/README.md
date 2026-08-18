# ASMP-9 balanced maximin design v0.16.2

This successor preserves the balanced maximin theorem, ten-gate universe, and
120-second cap after two registered resource aborts.

Its threshold search is exact but logarithmic: exponential bracketing followed
by binary search and exact predecessor/current verification.

The scientific registry is disjoint from development, v0.16, and v0.16.1.
Both earlier aborts remain sealed dependencies.
