"""Orientation-reversal liveness for rank-r holonomy under a lineage floor.

For a cycle of r-dimensional subspaces U_0, ..., U_m = U_0 with polar
(shortest-geodesic) transports, the holonomy H lies in O(r) and det(H) is the
holonomy of the induced line bundle Lambda^r U.  The angle between the lines
Lambda^r U and Lambda^r V is arccos |det(U^T V)| = arccos prod_i cos(alpha_i),
where alpha_i are the principal angles.  Lifting the cycle to the unit sphere of
Lambda^r R^n, det(H) = -1 forces the lifted path to join a vector to its
antipode, so

    sum_edges arccos( prod_i cos(alpha_i^(e)) ) >= pi.

With a lineage floor tau on worst-direction retention, every principal angle
satisfies cos(alpha_i) >= sqrt(tau), hence each edge contributes at most
theta_r(tau) = arccos(tau^(r/2)) and a cycle of length L can show orientation
reversal only if L * theta_r(tau) >= pi.  This script tabulates the bound.
Rank 1 recovers Theorem 1 of reports/QWEN08_PRECISION_GEOMETRY_PAPER_V0_1.md.
"""
from __future__ import annotations

import math
import sys


def theta_deg(tau: float, r: int) -> float:
    return math.degrees(math.acos(tau ** (r / 2.0)))


def min_live_length(tau: float, r: int) -> int:
    th = math.radians(theta_deg(tau, r))
    return int(math.ceil(math.pi / th)) if th > 0 else 10**9


def main() -> int:
    taus = [float(x) for x in sys.argv[1:]] or [0.9, 0.95, 0.5]
    ranks = range(1, 9)
    for tau in taus:
        print(f"lineage floor tau = {tau}")
        print("  rank | max line angle per edge | minimal live cycle length | 4-edge rectangle | 8-edge cycle")
        for r in ranks:
            th = theta_deg(tau, r)
            L = min_live_length(tau, r)
            rect = "live" if 4 * th >= 180.0 else "forced +1"
            cyc8 = "live" if 8 * th >= 180.0 else "forced +1"
            print(f"  {r:4d} | {th:8.2f} deg               | {L:5d}                     | {rect:9s}        | {cyc8}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
